from contextlib import asynccontextmanager
from decimal import Decimal
from pathlib import Path
import shutil
import uuid

from fastapi import (
    Body,
    Depends,
    FastAPI,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pwdlib import PasswordHash
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from database import Base, SessionLocal, engine, obtener_sesion

from models import (
    Blog,
    BlogImagen,
    Carrito,
    CarritoDetalle,
    Comentario,
    ComentarioReaccion,
    HistorialPuntos,
    Pedido,
    PedidoDetalle,
    Producto,
    ReaccionBlog,
    Usuario,
)

from schemas import (
    BlogActualizar,
    BlogCrear,
    BlogGestionarEstado,
    BlogImagenRespuesta,
    BlogRestaurar,
    BlogRespuesta,
    ComentarioActualizar,
    ComentarioCrear,
    ComentarioEliminar,
    ComentarioReaccionCrear,
    ComentarioRestaurar,
    ComentarioRespuesta,
    CarritoDetalleActualizar,
    CarritoDetalleCrear,
    CarritoDetalleRespuesta,
    CarritoResumenRespuesta,
    CompraConfirmar,
    CompraConfirmarRespuesta,
    HistorialPuntosCrear,
    HistorialPuntosRespuesta,
    LoginRequest,
    PedidoRespuesta,
    ProductoActualizar,
    ProductoAjustarStock,
    ProductoCrear,
    ProductoGestionarEstado,
    ProductoRespuesta,
    ReaccionBlogCrear,
    ReaccionBlogRespuesta,
    ReaccionEmojiRespuesta,
    UsuarioActualizar,
    UsuarioCrear,
    UsuarioRespuesta,
)


password_hash = PasswordHash.recommended()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

EXTENSIONES_PERMITIDAS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}

TIPOS_IMAGEN_PERMITIDOS = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
    "application/octet-stream",
}

ADMIN_NOMBRE = "Administrador"
ADMIN_CORREO = "admin@gmail.com"
ADMIN_PASSWORD = "123456789"

EMOJIS_COMENTARIO = {
    "👍",
    "❤️",
    "😂",
    "🌿",
    "🐍",
}


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def texto_opcional(
    valor: str | None,
) -> str | None:
    if valor is None:
        return None

    texto = valor.strip()

    return texto if texto else None


def validar_categoria(
    categoria: str,
) -> str:
    categoria_limpia = categoria.strip().lower()

    if categoria_limpia not in {
        "flora",
        "fauna",
    }:
        raise HTTPException(
            status_code=422,
            detail=(
                "La categoría debe ser "
                "'flora' o 'fauna'"
            ),
        )

    return categoria_limpia


def validar_reaccion(
    tipo: str,
) -> str:
    tipo_limpio = tipo.strip().lower()

    if tipo_limpio not in {
        "like",
        "dislike",
    }:
        raise HTTPException(
            status_code=422,
            detail=(
                "La reacción debe ser "
                "'like' o 'dislike'"
            ),
        )

    return tipo_limpio


def obtener_usuario_o_error(
    db: Session,
    usuario_id: int,
) -> Usuario:
    usuario = db.get(
        Usuario,
        usuario_id,
    )

    if usuario is None:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado",
        )

    return usuario


def obtener_blog_o_error(
    db: Session,
    blog_id: int,
) -> Blog:
    publicacion = db.get(
        Blog,
        blog_id,
    )

    if publicacion is None:
        raise HTTPException(
            status_code=404,
            detail="Publicación no encontrada",
        )

    return publicacion


def obtener_blog_completo_o_error(
    db: Session,
    blog_id: int,
) -> Blog:
    publicacion = db.scalar(
        select(Blog)
        .options(
            selectinload(Blog.usuario),
            selectinload(Blog.imagenes),
        )
        .where(Blog.id_blog == blog_id)
    )

    if publicacion is None:
        raise HTTPException(
            status_code=404,
            detail="Publicación no encontrada",
        )

    return publicacion


def puede_gestionar_publicacion(
    usuario: Usuario,
    publicacion: Blog,
) -> bool:
    return (
        usuario.id_usr == publicacion.usr_id
        or usuario.tip_usu == 1
    )


def validar_gestion_publicacion(
    db: Session,
    usuario_id: int,
    publicacion: Blog,
) -> Usuario:
    usuario = obtener_usuario_o_error(db, usuario_id)

    if usuario.estatus != 1:
        raise HTTPException(
            status_code=403,
            detail="La cuenta del usuario está inactiva",
        )

    if not puede_gestionar_publicacion(usuario, publicacion):
        raise HTTPException(
            status_code=403,
            detail="No puedes gestionar esta publicación",
        )

    return usuario


def validar_autor_publicacion(db: Session, usuario_id: int, publicacion: Blog) -> Usuario:
    usuario = obtener_usuario_o_error(db, usuario_id)
    if usuario.estatus != 1:
        raise HTTPException(status_code=403, detail="La cuenta del usuario está inactiva")
    if usuario.id_usr != publicacion.usr_id:
        raise HTTPException(status_code=403, detail="Solo el autor puede editar esta publicación")
    return usuario


def validar_autor_comentario(db: Session, usuario_id: int, comentario: Comentario) -> Usuario:
    usuario = obtener_usuario_o_error(db, usuario_id)
    if usuario.estatus != 1:
        raise HTTPException(status_code=403, detail="La cuenta del usuario está inactiva")
    if usuario.id_usr != comentario.usr_id:
        raise HTTPException(status_code=403, detail="Solo el autor puede editar este comentario")
    return usuario


def ruta_local_upload(ruta_publica: str | None) -> Path | None:
    if not ruta_publica or not ruta_publica.startswith("/uploads/"):
        return None

    nombre = Path(ruta_publica).name
    if not nombre:
        return None

    return UPLOAD_DIR / nombre


def eliminar_archivo_local(ruta_publica: str | None) -> None:
    ruta = ruta_local_upload(ruta_publica)
    if ruta is None:
        return

    try:
        if ruta.exists() and ruta.is_file():
            ruta.unlink()
    except OSError:
        pass


def serializar_blog(
    db: Session,
    publicacion: Blog,
) -> dict:
    autor = publicacion.usuario
    if autor is None:
        autor = obtener_usuario_o_error(db, publicacion.usr_id)

    cantidad_comentarios = db.scalar(
        select(func.count(Comentario.id_con)).where(
            Comentario.blog_id == publicacion.id_blog,
            Comentario.estatus == 1,
        )
    ) or 0

    return {
        "id_blog": publicacion.id_blog,
        "titulo": publicacion.titulo,
        "descripcion": publicacion.descripcion,
        "img": publicacion.img,
        "tags": publicacion.tags,
        "categoria": publicacion.categoria,
        "latitud": (
            float(publicacion.latitud)
            if publicacion.latitud is not None
            else None
        ),
        "longitud": (
            float(publicacion.longitud)
            if publicacion.longitud is not None
            else None
        ),
        "likes": publicacion.likes or 0,
        "dislikes": publicacion.dislikes or 0,
        "visualizaciones": publicacion.visualizaciones or 0,
        "estatus": publicacion.estatus,
        "fecha_publicacion": publicacion.fecha_publicacion,
        "usr_id": publicacion.usr_id,
        "autor": {
            "id_usr": autor.id_usr,
            "nom_usr": autor.nom_usr,
            "foto_perfil": autor.foto_perfil,
        },
        "imagenes": [
            {
                "id_img": imagen.id_img,
                "blog_id": imagen.blog_id,
                "ruta_imagen": imagen.ruta_imagen,
            }
            for imagen in publicacion.imagenes
        ],
        "cantidad_comentarios": int(cantidad_comentarios),
    }


def obtener_comentario_o_error(
    db: Session,
    comentario_id: int,
) -> Comentario:
    comentario = db.scalar(
        select(Comentario)
        .options(
            selectinload(
                Comentario.usuario,
            ),
        )
        .where(
            Comentario.id_con == comentario_id,
        )
    )

    if comentario is None:
        raise HTTPException(
            status_code=404,
            detail="Comentario no encontrado",
        )

    return comentario


def validar_administrador(
    db: Session,
    usuario_id: int,
) -> Usuario:
    usuario = obtener_usuario_o_error(
        db,
        usuario_id,
    )

    if usuario.tip_usu != 1:
        raise HTTPException(
            status_code=403,
            detail=(
                "Solo un administrador puede "
                "realizar esta operación"
            ),
        )

    if usuario.estatus != 1:
        raise HTTPException(
            status_code=403,
            detail=(
                "La cuenta del administrador "
                "está inactiva"
            ),
        )

    return usuario


def validar_emoji_comentario(
    emoji: str,
) -> str:
    emoji_limpio = emoji.strip()

    if emoji_limpio not in EMOJIS_COMENTARIO:
        raise HTTPException(
            status_code=422,
            detail=(
                "El emoji seleccionado "
                "no está permitido"
            ),
        )

    return emoji_limpio


def puede_gestionar_comentario(
    usuario: Usuario,
    comentario: Comentario,
) -> bool:
    return (
        usuario.id_usr == comentario.usr_id
        or usuario.tip_usu == 1
    )


def obtener_reacciones_comentario(
    db: Session,
    comentario_id: int,
    usuario_id: int | None = None,
) -> list[dict]:
    filas = db.execute(
        select(
            ComentarioReaccion.emoji,
            func.count(
                ComentarioReaccion.id_reaccion,
            ).label("cantidad"),
        )
        .where(
            ComentarioReaccion.comentario_id
            == comentario_id,
        )
        .group_by(
            ComentarioReaccion.emoji,
        )
    ).all()

    emoji_seleccionado: str | None = None

    if usuario_id is not None:
        reaccion_usuario = db.scalar(
            select(ComentarioReaccion).where(
                ComentarioReaccion.comentario_id
                == comentario_id,
                ComentarioReaccion.usuario_id
                == usuario_id,
            )
        )

        if reaccion_usuario is not None:
            emoji_seleccionado = reaccion_usuario.emoji

    conteos = {
        emoji: int(cantidad)
        for emoji, cantidad in filas
    }

    resultado: list[dict] = []

    for emoji in [
        "👍",
        "❤️",
        "😂",
        "🌿",
        "🐍",
    ]:
        cantidad = conteos.get(
            emoji,
            0,
        )

        if cantidad > 0 or emoji == emoji_seleccionado:
            resultado.append(
                {
                    "emoji": emoji,
                    "cantidad": cantidad,
                    "seleccionada": (
                        emoji == emoji_seleccionado
                    ),
                }
            )

    return resultado


def serializar_comentario(
    db: Session,
    comentario: Comentario,
    usuario_id: int | None = None,
) -> dict:
    autor = comentario.usuario

    if autor is None:
        autor = obtener_usuario_o_error(
            db,
            comentario.usr_id,
        )

    return {
        "id_con": comentario.id_con,
        "comentario": comentario.comentario,
        "fecha": comentario.fecha,
        "estatus": comentario.estatus,
        "usr_id": comentario.usr_id,
        "blog_id": comentario.blog_id,
        "autor": {
            "id_usr": autor.id_usr,
            "nom_usr": autor.nom_usr,
            "foto_perfil": autor.foto_perfil,
        },
        "reacciones": obtener_reacciones_comentario(
            db,
            comentario.id_con,
            usuario_id,
        ),
    }


def serializar_producto(
    producto: Producto,
) -> dict:
    stock = producto.stock or 0
    estatus = producto.estatus or 0

    return {
        "id_producto": producto.id_producto,
        "nombre": producto.nombre,
        "descripcion": producto.descripcion,
        "precio": float(producto.precio),
        "stock": stock,
        "imagen": producto.imagen,
        "categoria": producto.categoria,
        "estatus": estatus,
        "fecha_creacion": producto.fecha_creacion,
        "disponible": estatus == 1 and stock > 0,
        "agotado": stock <= 0,
        "stock_bajo": 0 < stock <= 5,
    }


def validar_datos_producto(
    nombre: str,
    precio: float,
    stock: int,
    categoria: str,
) -> tuple[str, Decimal, str]:
    nombre_limpio = nombre.strip()
    categoria_limpia = categoria.strip()

    if len(nombre_limpio) < 2:
        raise HTTPException(
            status_code=422,
            detail="El nombre debe tener al menos 2 caracteres",
        )

    if precio <= 0:
        raise HTTPException(
            status_code=422,
            detail="El precio debe ser mayor que cero",
        )

    if stock < 0:
        raise HTTPException(
            status_code=422,
            detail="El stock no puede ser negativo",
        )

    if not categoria_limpia:
        raise HTTPException(
            status_code=422,
            detail="La categoría es obligatoria",
        )

    return (
        nombre_limpio,
        Decimal(str(precio)),
        categoria_limpia,
    )


def obtener_producto_o_error(
    db: Session,
    producto_id: int,
) -> Producto:
    producto = db.get(
        Producto,
        producto_id,
    )

    if producto is None:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado",
        )

    return producto


def obtener_pedido_o_error(
    db: Session,
    pedido_id: int,
) -> Pedido:
    pedido = db.get(
        Pedido,
        pedido_id,
    )

    if pedido is None:
        raise HTTPException(
            status_code=404,
            detail="Pedido no encontrado",
        )

    return pedido


def registrar_puntos(
    db: Session,
    usuario: Usuario,
    puntos: int,
    accion: str,
) -> HistorialPuntos:
    usuario.puntos = (
        usuario.puntos or 0
    ) + puntos

    historial = HistorialPuntos(
        usuario_id=usuario.id_usr,
        puntos=puntos,
        accion=accion,
    )

    db.add(historial)

    return historial


def guardar_imagen(
    imagen: UploadFile,
) -> tuple[Path, str]:
    extension = Path(
        imagen.filename or "",
    ).suffix.lower()

    if extension not in EXTENSIONES_PERMITIDAS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Formato no permitido. "
                "Utiliza JPG, JPEG, PNG o WEBP"
            ),
        )

    tipo = (
        imagen.content_type or ""
    ).lower()

    if tipo not in TIPOS_IMAGEN_PERMITIDOS:
        raise HTTPException(
            status_code=400,
            detail="El archivo no es una imagen válida",
        )

    nombre = f"{uuid.uuid4().hex}{extension}"
    ruta = UPLOAD_DIR / nombre

    try:
        with ruta.open("wb") as destino:
            shutil.copyfileobj(
                imagen.file,
                destino,
            )
    except OSError as error:
        raise HTTPException(
            status_code=500,
            detail="No se pudo guardar la imagen",
        ) from error
    finally:
        imagen.file.close()

    return ruta, f"/uploads/{nombre}"


def obtener_o_crear_carrito(
    db: Session,
    usuario_id: int,
) -> Carrito:
    carrito = db.scalar(
        select(Carrito).where(
            Carrito.usuario_id == usuario_id,
        )
    )

    if carrito is not None:
        return carrito

    carrito = Carrito(
        usuario_id=usuario_id,
    )

    db.add(carrito)
    db.flush()

    return carrito


def validar_usuario_activo(
    db: Session,
    usuario_id: int,
) -> Usuario:
    usuario = obtener_usuario_o_error(db, usuario_id)
    if usuario.estatus != 1:
        raise HTTPException(
            status_code=403,
            detail="La cuenta del usuario está inactiva",
        )
    return usuario


def obtener_carrito_usuario(
    db: Session,
    usuario_id: int,
    crear: bool = False,
) -> Carrito | None:
    carrito = db.scalar(
        select(Carrito)
        .options(
            selectinload(Carrito.detalles)
            .selectinload(CarritoDetalle.producto),
        )
        .where(Carrito.usuario_id == usuario_id)
    )
    if carrito is None and crear:
        carrito = Carrito(usuario_id=usuario_id)
        db.add(carrito)
        db.flush()
    return carrito


def serializar_detalle_carrito(
    detalle: CarritoDetalle,
) -> dict:
    producto = detalle.producto
    if producto is None:
        raise HTTPException(
            status_code=409,
            detail="El carrito contiene un producto inexistente",
        )

    precio = Decimal(producto.precio)
    cantidad = detalle.cantidad or 0
    stock = producto.stock or 0
    activo = producto.estatus == 1
    cantidad_valida = cantidad > 0 and cantidad <= stock
    disponible = activo and stock > 0

    return {
        "id_detalle": detalle.id_detalle,
        "carrito_id": detalle.carrito_id,
        "producto_id": detalle.producto_id,
        "cantidad": cantidad,
        "producto": {
            "id_producto": producto.id_producto,
            "nombre": producto.nombre,
            "descripcion": producto.descripcion,
            "precio": float(precio),
            "stock": stock,
            "imagen": producto.imagen,
            "categoria": producto.categoria,
            "estatus": producto.estatus,
            "disponible": disponible,
            "agotado": stock <= 0,
            "stock_bajo": 0 < stock <= 5,
        },
        "precio_unitario": float(precio),
        "subtotal": float(precio * cantidad),
        "cantidad_valida": cantidad_valida,
        "disponible": disponible,
    }


def serializar_resumen_carrito(carrito: Carrito) -> dict:
    detalles = [
        serializar_detalle_carrito(detalle)
        for detalle in carrito.detalles
    ]
    total = sum(
        Decimal(str(detalle["subtotal"]))
        for detalle in detalles
    )
    mensajes: list[str] = []

    for detalle in detalles:
        producto = detalle["producto"]
        if not detalle["disponible"]:
            mensajes.append(
                f"{producto['nombre']} no está disponible"
            )
        elif not detalle["cantidad_valida"]:
            mensajes.append(
                f"La cantidad de {producto['nombre']} supera el stock"
            )

    return {
        "id_carrito": carrito.id_carrito,
        "usuario_id": carrito.usuario_id,
        "fecha_creacion": carrito.fecha_creacion,
        "detalles": detalles,
        "cantidad_productos": len(detalles),
        "cantidad_articulos": sum(
            detalle["cantidad"] for detalle in detalles
        ),
        "subtotal": float(total),
        "total": float(total),
        "carrito_valido": not mensajes and bool(detalles),
        "mensajes": mensajes,
    }


def serializar_pedido(pedido: Pedido) -> dict:
    detalles = []
    for detalle in pedido.detalles:
        precio = Decimal(detalle.precio_unitario)
        producto = detalle.producto
        detalles.append(
            {
                "id_detalle": detalle.id_detalle,
                "pedido_id": detalle.pedido_id,
                "producto_id": detalle.producto_id,
                "cantidad": detalle.cantidad,
                "precio_unitario": float(precio),
                "subtotal": float(precio * detalle.cantidad),
                "producto": (
                    {
                        "id_producto": producto.id_producto,
                        "nombre": producto.nombre,
                        "imagen": producto.imagen,
                        "categoria": producto.categoria,
                    }
                    if producto is not None
                    else None
                ),
            }
        )

    return {
        "id_pedido": pedido.id_pedido,
        "usuario_id": pedido.usuario_id,
        "total": float(pedido.total),
        "estado": pedido.estado,
        "fecha": pedido.fecha,
        "detalles": detalles,
        "cantidad_productos": len(detalles),
        "cantidad_articulos": sum(
            detalle["cantidad"] for detalle in detalles
        ),
    }


def crear_administrador_inicial() -> None:
    db = SessionLocal()

    try:
        administrador = db.scalar(
            select(Usuario).where(
                Usuario.mail == ADMIN_CORREO,
            )
        )

        if administrador is None:
            administrador = Usuario(
                nom_usr=ADMIN_NOMBRE,
                mail=ADMIN_CORREO,
                pass_hash=password_hash.hash(
                    ADMIN_PASSWORD,
                ),
                foto_perfil=None,
                dir_usr=None,
                telefono=None,
                puntos=0,
                tip_usu=1,
                estatus=1,
            )

            db.add(administrador)
            db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
    finally:
        db.close()


# ============================================================
# INICIO DE LA API
# ============================================================

@asynccontextmanager
async def lifespan(
    app: FastAPI,
):
    Base.metadata.create_all(
        bind=engine,
    )

    crear_administrador_inicial()

    yield


app = FastAPI(
    title="API Quetzalcóatl",
    description=(
        "API para blog, geolocalización, tienda, "
        "carrito, pedidos y gamificación"
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/uploads",
    StaticFiles(
        directory=str(UPLOAD_DIR),
    ),
    name="uploads",
)


@app.get("/")
def inicio():
    return {
        "mensaje": "API Quetzalcóatl funcionando",
        "version": "1.0.0",
    }


@app.get("/health")
def health():
    return {
        "estado": "ok",
    }


# ============================================================
# AUTENTICACIÓN
# ============================================================

@app.post(
    "/login",
    response_model=UsuarioRespuesta,
)
def iniciar_sesion(
    datos: LoginRequest,
    db: Session = Depends(
        obtener_sesion,
    ),
):
    correo = datos.mail.strip().lower()

    usuario = db.scalar(
        select(Usuario).where(
            Usuario.mail == correo,
        )
    )

    if usuario is None:
        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos",
        )

    if usuario.estatus != 1:
        raise HTTPException(
            status_code=403,
            detail="La cuenta se encuentra inactiva",
        )

    try:
        password_correcta = password_hash.verify(
            datos.password,
            usuario.pass_hash,
        )
    except Exception:
        password_correcta = False

    if not password_correcta:
        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos",
        )

    return usuario


@app.post("/password/solicitar")
def solicitar_recuperacion(
    correo: str = Body(
        embed=True,
    ),
):
    return {
        "mensaje": (
            "Si existe una cuenta asociada al correo, "
            "se enviarán instrucciones de recuperación"
        ),
    }


# ============================================================
# USUARIOS
# ============================================================

@app.get(
    "/usuarios",
    response_model=list[UsuarioRespuesta],
)
def listar_usuarios(
    db: Session = Depends(
        obtener_sesion,
    ),
):
    return db.scalars(
        select(Usuario).order_by(
            Usuario.id_usr,
        )
    ).all()


@app.get(
    "/usuarios/{usuario_id}",
    response_model=UsuarioRespuesta,
)
def obtener_usuario(
    usuario_id: int,
    db: Session = Depends(
        obtener_sesion,
    ),
):
    return obtener_usuario_o_error(
        db,
        usuario_id,
    )


@app.post(
    "/usuarios",
    response_model=UsuarioRespuesta,
    status_code=201,
)
def crear_usuario(
    datos: UsuarioCrear,
    db: Session = Depends(
        obtener_sesion,
    ),
):
    correo = datos.mail.strip().lower()

    existente = db.scalar(
        select(Usuario).where(
            Usuario.mail == correo,
        )
    )

    if existente is not None:
        raise HTTPException(
            status_code=409,
            detail="El correo ya está registrado",
        )

    usuario = Usuario(
        nom_usr=datos.nom_usr.strip(),
        mail=correo,
        pass_hash=password_hash.hash(
            datos.password,
        ),
        foto_perfil=texto_opcional(
            datos.foto_perfil,
        ),
        dir_usr=texto_opcional(
            datos.dir_usr,
        ),
        telefono=texto_opcional(
            datos.telefono,
        ),
        puntos=0,
        tip_usu=datos.tip_usu,
        estatus=1,
    )

    db.add(usuario)

    try:
        db.commit()
        db.refresh(usuario)
    except IntegrityError as error:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="El correo ya está registrado",
        ) from error
    except SQLAlchemyError as error:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="No se pudo registrar el usuario",
        ) from error

    return usuario


@app.put(
    "/usuarios/{usuario_id}",
    response_model=UsuarioRespuesta,
)
def actualizar_usuario(
    usuario_id: int,
    datos: UsuarioActualizar,
    solicitante_id: int = Query(..., gt=0),
    db: Session = Depends(obtener_sesion),
):
    solicitante = validar_usuario_activo(db, solicitante_id)
    if solicitante.id_usr != usuario_id:
        raise HTTPException(status_code=403, detail="Solo puedes editar tu propio perfil")
    usuario = obtener_usuario_o_error(db, usuario_id)

    correo = datos.mail.strip().lower()

    correo_existente = db.scalar(
        select(Usuario).where(
            Usuario.mail == correo,
            Usuario.id_usr != usuario_id,
        )
    )

    if correo_existente is not None:
        raise HTTPException(
            status_code=409,
            detail="El correo ya está registrado",
        )

    usuario.nom_usr = datos.nom_usr.strip()
    usuario.mail = correo
    usuario.foto_perfil = texto_opcional(
        datos.foto_perfil,
    )
    usuario.dir_usr = texto_opcional(
        datos.dir_usr,
    )
    usuario.telefono = texto_opcional(
        datos.telefono,
    )
    # El rol y el estado se conservan al editar el perfil.

    try:
        db.commit()
        db.refresh(usuario)
    except IntegrityError as error:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="El correo ya está registrado",
        ) from error
    except SQLAlchemyError as error:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="No se pudo actualizar el usuario",
        ) from error

    return usuario


@app.delete("/usuarios/{usuario_id}")
def eliminar_usuario(
    usuario_id: int,
    administrador_id: int = Query(..., gt=0),
    db: Session = Depends(obtener_sesion),
):
    administrador = validar_administrador(db, administrador_id)
    if administrador.id_usr == usuario_id:
        raise HTTPException(status_code=409, detail="No puedes desactivar tu propia cuenta administrativa")
    usuario = obtener_usuario_o_error(db, usuario_id)
    if usuario.estatus == 0:
        return {"mensaje": "El usuario ya estaba desactivado"}
    usuario.estatus = 0
    try:
        db.commit()
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(status_code=500, detail="No se pudo desactivar el usuario") from error
    return {"mensaje": "Usuario desactivado correctamente"}


@app.put("/usuarios/{usuario_id}/restaurar", response_model=UsuarioRespuesta)
def restaurar_usuario(
    usuario_id: int,
    administrador_id: int = Query(..., gt=0),
    db: Session = Depends(obtener_sesion),
):
    validar_administrador(db, administrador_id)
    usuario = obtener_usuario_o_error(db, usuario_id)
    usuario.estatus = 1
    try:
        db.commit()
        db.refresh(usuario)
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(status_code=500, detail="No se pudo restaurar el usuario") from error
    return usuario


# ============================================================
# BLOG
# ============================================================

@app.get(
    "/blog",
    response_model=list[BlogRespuesta],
)
def listar_blog(
    categoria: str | None = Query(default=None),
    usuario_id: int | None = Query(default=None),
    incluir_inactivos: bool = Query(default=False),
    administrador_id: int | None = Query(default=None),
    db: Session = Depends(obtener_sesion),
):
    if categoria is not None:
        categoria = validar_categoria(categoria)

    if usuario_id is not None:
        obtener_usuario_o_error(db, usuario_id)

    if incluir_inactivos:
        if administrador_id is None:
            raise HTTPException(
                status_code=403,
                detail="Debes indicar el administrador",
            )
        validar_administrador(db, administrador_id)

    consulta = select(Blog).options(
        selectinload(Blog.usuario),
        selectinload(Blog.imagenes),
    )

    if not incluir_inactivos:
        consulta = consulta.where(Blog.estatus == 1)

    if categoria is not None:
        consulta = consulta.where(Blog.categoria == categoria)

    if usuario_id is not None:
        consulta = consulta.where(Blog.usr_id == usuario_id)

    publicaciones = db.scalars(
        consulta.order_by(Blog.id_blog.desc())
    ).all()

    return [serializar_blog(db, publicacion) for publicacion in publicaciones]


@app.get(
    "/blog/mis-publicaciones/{usuario_id}",
    response_model=list[BlogRespuesta],
)
def listar_mis_publicaciones(
    usuario_id: int,
    incluir_inactivas: bool = Query(default=True),
    db: Session = Depends(obtener_sesion),
):
    usuario = obtener_usuario_o_error(db, usuario_id)
    if usuario.estatus != 1:
        raise HTTPException(status_code=403, detail="La cuenta está inactiva")

    consulta = (
        select(Blog)
        .options(
            selectinload(Blog.usuario),
            selectinload(Blog.imagenes),
        )
        .where(Blog.usr_id == usuario_id)
    )

    if not incluir_inactivas:
        consulta = consulta.where(Blog.estatus == 1)

    publicaciones = db.scalars(
        consulta.order_by(Blog.id_blog.desc())
    ).all()
    return [serializar_blog(db, publicacion) for publicacion in publicaciones]


@app.get(
    "/blog/{blog_id}",
    response_model=BlogRespuesta,
)
def obtener_blog(
    blog_id: int,
    incrementar_vista: bool = Query(default=True),
    usuario_id: int | None = Query(default=None),
    db: Session = Depends(obtener_sesion),
):
    publicacion = obtener_blog_completo_o_error(db, blog_id)

    if publicacion.estatus != 1:
        if usuario_id is None:
            raise HTTPException(status_code=404, detail="Publicación no encontrada")
        validar_gestion_publicacion(db, usuario_id, publicacion)

    if incrementar_vista:
        publicacion.visualizaciones = (publicacion.visualizaciones or 0) + 1
        try:
            db.commit()
            db.refresh(publicacion)
        except SQLAlchemyError:
            db.rollback()

    return serializar_blog(db, publicacion)


@app.post(
    "/blog",
    response_model=BlogRespuesta,
    status_code=201,
)
def crear_blog(
    datos: BlogCrear,
    db: Session = Depends(obtener_sesion),
):
    usuario = obtener_usuario_o_error(db, datos.usr_id)
    if usuario.estatus != 1:
        raise HTTPException(status_code=403, detail="La cuenta está inactiva")

    titulo = datos.titulo.strip()
    descripcion = datos.descripcion.strip()
    if not descripcion:
        raise HTTPException(status_code=422, detail="La descripción es obligatoria")

    publicacion = Blog(
        titulo=titulo,
        descripcion=descripcion,
        img=texto_opcional(datos.img),
        tags=texto_opcional(datos.tags),
        categoria=validar_categoria(datos.categoria),
        latitud=datos.latitud,
        longitud=datos.longitud,
        likes=0,
        dislikes=0,
        visualizaciones=0,
        estatus=1,
        usr_id=usuario.id_usr,
    )
    db.add(publicacion)

    try:
        registrar_puntos(db, usuario, 10, "Publicó un avistamiento")
        if datos.latitud is not None and datos.longitud is not None:
            registrar_puntos(db, usuario, 5, "Agregó ubicación GPS")
        db.commit()
        db.refresh(publicacion)
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="No se pudo guardar la publicación",
        ) from error

    publicacion = obtener_blog_completo_o_error(db, publicacion.id_blog)
    return serializar_blog(db, publicacion)


@app.post(
    "/blog/upload",
    response_model=BlogRespuesta,
    status_code=201,
)
def crear_blog_con_imagen(
    titulo: str = Form(...),
    descripcion: str = Form(...),
    categoria: str = Form(...),
    usr_id: int = Form(...),
    tags: str | None = Form(None),
    latitud: float | None = Form(None),
    longitud: float | None = Form(None),
    imagen: UploadFile = File(...),
    db: Session = Depends(obtener_sesion),
):
    usuario = obtener_usuario_o_error(db, usr_id)
    if usuario.estatus != 1:
        raise HTTPException(status_code=403, detail="La cuenta está inactiva")

    titulo_limpio = titulo.strip()
    descripcion_limpia = descripcion.strip()
    if len(titulo_limpio) < 2:
        raise HTTPException(status_code=422, detail="El título es demasiado corto")
    if not descripcion_limpia:
        raise HTTPException(status_code=422, detail="La descripción es obligatoria")

    ruta_archivo, ruta_publica = guardar_imagen(imagen)
    publicacion = Blog(
        titulo=titulo_limpio,
        descripcion=descripcion_limpia,
        img=ruta_publica,
        tags=texto_opcional(tags),
        categoria=validar_categoria(categoria),
        latitud=latitud,
        longitud=longitud,
        likes=0,
        dislikes=0,
        visualizaciones=0,
        estatus=1,
        usr_id=usuario.id_usr,
    )
    db.add(publicacion)

    try:
        registrar_puntos(db, usuario, 10, "Publicó un avistamiento")
        if latitud is not None and longitud is not None:
            registrar_puntos(db, usuario, 5, "Agregó ubicación GPS")
        db.commit()
        db.refresh(publicacion)
    except SQLAlchemyError as error:
        db.rollback()
        if ruta_archivo.exists():
            ruta_archivo.unlink()
        raise HTTPException(
            status_code=500,
            detail="No se pudo guardar la publicación",
        ) from error

    publicacion = obtener_blog_completo_o_error(db, publicacion.id_blog)
    return serializar_blog(db, publicacion)


@app.put(
    "/blog/{blog_id}",
    response_model=BlogRespuesta,
)
def actualizar_blog(
    blog_id: int,
    datos: BlogActualizar,
    db: Session = Depends(obtener_sesion),
):
    publicacion = obtener_blog_completo_o_error(db, blog_id)
    validar_autor_publicacion(db, datos.usuario_id, publicacion)

    if publicacion.estatus != 1:
        raise HTTPException(
            status_code=409,
            detail="No se puede editar una publicación inactiva",
        )

    publicacion.titulo = datos.titulo.strip()
    publicacion.descripcion = datos.descripcion.strip()
    publicacion.img = texto_opcional(datos.img)
    publicacion.tags = texto_opcional(datos.tags)
    publicacion.categoria = validar_categoria(datos.categoria)
    publicacion.latitud = datos.latitud
    publicacion.longitud = datos.longitud

    try:
        db.commit()
        db.refresh(publicacion)
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="No se pudo actualizar la publicación",
        ) from error

    publicacion = obtener_blog_completo_o_error(db, blog_id)
    return serializar_blog(db, publicacion)


@app.put(
    "/blog/{blog_id}/upload",
    response_model=BlogRespuesta,
)
def actualizar_blog_con_imagen(
    blog_id: int,
    titulo: str = Form(...),
    descripcion: str = Form(...),
    categoria: str = Form(...),
    usuario_id: int = Form(...),
    tags: str | None = Form(None),
    latitud: float | None = Form(None),
    longitud: float | None = Form(None),
    imagen: UploadFile | None = File(None),
    db: Session = Depends(obtener_sesion),
):
    publicacion = obtener_blog_completo_o_error(db, blog_id)
    validar_autor_publicacion(db, usuario_id, publicacion)

    if publicacion.estatus != 1:
        raise HTTPException(
            status_code=409,
            detail="No se puede editar una publicación inactiva",
        )

    nueva_ruta_archivo: Path | None = None
    nueva_ruta_publica: str | None = None
    imagen_anterior = publicacion.img

    if imagen is not None and imagen.filename:
        nueva_ruta_archivo, nueva_ruta_publica = guardar_imagen(imagen)

    publicacion.titulo = titulo.strip()
    publicacion.descripcion = descripcion.strip()
    publicacion.categoria = validar_categoria(categoria)
    publicacion.tags = texto_opcional(tags)
    publicacion.latitud = latitud
    publicacion.longitud = longitud
    if nueva_ruta_publica is not None:
        publicacion.img = nueva_ruta_publica

    try:
        db.commit()
        db.refresh(publicacion)
    except SQLAlchemyError as error:
        db.rollback()
        if nueva_ruta_archivo is not None and nueva_ruta_archivo.exists():
            nueva_ruta_archivo.unlink()
        raise HTTPException(
            status_code=500,
            detail="No se pudo actualizar la publicación",
        ) from error

    if nueva_ruta_publica is not None:
        eliminar_archivo_local(imagen_anterior)

    publicacion = obtener_blog_completo_o_error(db, blog_id)
    return serializar_blog(db, publicacion)


@app.delete("/blog/{blog_id}")
def eliminar_blog(
    blog_id: int,
    datos: BlogGestionarEstado,
    db: Session = Depends(obtener_sesion),
):
    publicacion = obtener_blog_completo_o_error(db, blog_id)
    validar_gestion_publicacion(db, datos.usuario_id, publicacion)

    if publicacion.estatus == 0:
        return {"mensaje": "La publicación ya estaba desactivada"}

    publicacion.estatus = 0
    try:
        db.commit()
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="No se pudo desactivar la publicación",
        ) from error

    return {"mensaje": "Publicación desactivada correctamente"}


@app.put(
    "/blog/{blog_id}/restaurar",
    response_model=BlogRespuesta,
)
def restaurar_blog(
    blog_id: int,
    datos: BlogRestaurar,
    db: Session = Depends(obtener_sesion),
):
    validar_administrador(db, datos.administrador_id)
    publicacion = obtener_blog_completo_o_error(db, blog_id)
    publicacion.estatus = 1

    try:
        db.commit()
        db.refresh(publicacion)
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="No se pudo restaurar la publicación",
        ) from error

    publicacion = obtener_blog_completo_o_error(db, blog_id)
    return serializar_blog(db, publicacion)


@app.get(
    "/blog/{blog_id}/imagenes",
    response_model=list[BlogImagenRespuesta],
)
def listar_imagenes_blog(
    blog_id: int,
    db: Session = Depends(obtener_sesion),
):
    obtener_blog_o_error(db, blog_id)
    return db.scalars(
        select(BlogImagen)
        .where(BlogImagen.blog_id == blog_id)
        .order_by(BlogImagen.id_img.desc())
    ).all()


@app.post(
    "/blog/{blog_id}/imagenes",
    response_model=BlogImagenRespuesta,
    status_code=201,
)
def agregar_imagen_blog(
    blog_id: int,
    usuario_id: int = Form(...),
    imagen: UploadFile = File(...),
    db: Session = Depends(obtener_sesion),
):
    publicacion = obtener_blog_completo_o_error(db, blog_id)
    validar_autor_publicacion(db, usuario_id, publicacion)

    ruta_archivo, ruta_publica = guardar_imagen(imagen)
    registro = BlogImagen(blog_id=blog_id, ruta_imagen=ruta_publica)
    db.add(registro)

    try:
        db.commit()
        db.refresh(registro)
    except SQLAlchemyError as error:
        db.rollback()
        if ruta_archivo.exists():
            ruta_archivo.unlink()
        raise HTTPException(
            status_code=500,
            detail="No se pudo guardar la imagen adicional",
        ) from error

    return registro


@app.delete("/blog/imagenes/{imagen_id}")
def eliminar_imagen_blog(
    imagen_id: int,
    usuario_id: int = Query(...),
    db: Session = Depends(obtener_sesion),
):
    imagen = db.get(BlogImagen, imagen_id)
    if imagen is None:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")

    publicacion = obtener_blog_completo_o_error(db, imagen.blog_id)
    validar_autor_publicacion(db, usuario_id, publicacion)
    ruta_publica = imagen.ruta_imagen

    try:
        db.delete(imagen)
        db.commit()
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="No se pudo eliminar la imagen",
        ) from error

    eliminar_archivo_local(ruta_publica)
    return {"mensaje": "Imagen eliminada correctamente"}


# ============================================================
# COMENTARIOS
# ============================================================

@app.get(
    "/comentarios",
    response_model=list[ComentarioRespuesta],
)
def listar_comentarios(
    blog_id: int | None = Query(default=None),
    usuario_id: int | None = Query(default=None),
    incluir_inactivos: bool = Query(default=False),
    administrador_id: int | None = Query(default=None),
    db: Session = Depends(obtener_sesion),
):
    if usuario_id is not None:
        obtener_usuario_o_error(db, usuario_id)

    if incluir_inactivos:
        if administrador_id is None:
            raise HTTPException(
                status_code=403,
                detail="Debes indicar el administrador",
            )
        validar_administrador(db, administrador_id)

    consulta = select(Comentario).options(
        selectinload(Comentario.usuario),
    )

    if blog_id is not None:
        obtener_blog_o_error(db, blog_id)
        consulta = consulta.where(
            Comentario.blog_id == blog_id,
        )

    if not incluir_inactivos:
        consulta = consulta.where(
            Comentario.estatus == 1,
        )

    comentarios = db.scalars(
        consulta.order_by(Comentario.id_con.desc())
    ).all()

    return [
        serializar_comentario(db, comentario, usuario_id)
        for comentario in comentarios
    ]


@app.get(
    "/comentarios/{comentario_id}",
    response_model=ComentarioRespuesta,
)
def obtener_comentario(
    comentario_id: int,
    usuario_id: int | None = Query(default=None),
    db: Session = Depends(obtener_sesion),
):
    if usuario_id is not None:
        obtener_usuario_o_error(db, usuario_id)

    comentario = obtener_comentario_o_error(
        db,
        comentario_id,
    )

    if comentario.estatus != 1:
        raise HTTPException(
            status_code=404,
            detail="Comentario no encontrado",
        )

    return serializar_comentario(
        db,
        comentario,
        usuario_id,
    )


@app.post(
    "/comentarios",
    response_model=ComentarioRespuesta,
    status_code=201,
)
def crear_comentario(
    datos: ComentarioCrear,
    db: Session = Depends(obtener_sesion),
):
    usuario = obtener_usuario_o_error(
        db,
        datos.usr_id,
    )

    if usuario.estatus != 1:
        raise HTTPException(
            status_code=403,
            detail="La cuenta del usuario está inactiva",
        )

    publicacion = obtener_blog_o_error(
        db,
        datos.blog_id,
    )

    if publicacion.estatus != 1:
        raise HTTPException(
            status_code=409,
            detail=(
                "No se puede comentar una publicación inactiva"
            ),
        )

    texto = datos.comentario.strip()

    if not texto:
        raise HTTPException(
            status_code=422,
            detail="El comentario está vacío",
        )

    comentario = Comentario(
        comentario=texto,
        estatus=1,
        usr_id=usuario.id_usr,
        blog_id=publicacion.id_blog,
    )

    db.add(comentario)

    try:
        registrar_puntos(
            db,
            usuario,
            2,
            "Realizó un comentario",
        )
        db.commit()
        db.refresh(comentario)
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="No se pudo guardar el comentario",
        ) from error

    comentario = obtener_comentario_o_error(
        db,
        comentario.id_con,
    )

    return serializar_comentario(
        db,
        comentario,
        usuario.id_usr,
    )


@app.put(
    "/comentarios/{comentario_id}",
    response_model=ComentarioRespuesta,
)
def actualizar_comentario(
    comentario_id: int,
    datos: ComentarioActualizar,
    db: Session = Depends(obtener_sesion),
):
    comentario = obtener_comentario_o_error(
        db,
        comentario_id,
    )
    usuario = validar_autor_comentario(
        db,
        datos.usuario_id,
        comentario,
    )

    if comentario.estatus != 1:
        raise HTTPException(
            status_code=409,
            detail=(
                "No se puede editar un comentario inactivo"
            ),
        )

    texto = datos.comentario.strip()

    if not texto:
        raise HTTPException(
            status_code=422,
            detail="El comentario está vacío",
        )

    comentario.comentario = texto

    try:
        db.commit()
        db.refresh(comentario)
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="No se pudo actualizar el comentario",
        ) from error

    comentario = obtener_comentario_o_error(
        db,
        comentario_id,
    )

    return serializar_comentario(
        db,
        comentario,
        usuario.id_usr,
    )


@app.delete("/comentarios/{comentario_id}")
def eliminar_comentario(
    comentario_id: int,
    datos: ComentarioEliminar,
    db: Session = Depends(obtener_sesion),
):
    usuario = obtener_usuario_o_error(
        db,
        datos.usuario_id,
    )
    comentario = obtener_comentario_o_error(
        db,
        comentario_id,
    )

    if not puede_gestionar_comentario(usuario, comentario):
        raise HTTPException(
            status_code=403,
            detail="No puedes eliminar este comentario",
        )

    if comentario.estatus == 0:
        return {
            "mensaje": "El comentario ya estaba eliminado",
        }

    comentario.estatus = 0

    try:
        db.commit()
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="No se pudo eliminar el comentario",
        ) from error

    return {
        "mensaje": "Comentario eliminado correctamente",
    }


@app.put(
    "/comentarios/{comentario_id}/restaurar",
    response_model=ComentarioRespuesta,
)
def restaurar_comentario(
    comentario_id: int,
    datos: ComentarioRestaurar,
    db: Session = Depends(obtener_sesion),
):
    administrador = validar_administrador(
        db,
        datos.administrador_id,
    )
    comentario = obtener_comentario_o_error(
        db,
        comentario_id,
    )
    comentario.estatus = 1

    try:
        db.commit()
        db.refresh(comentario)
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="No se pudo restaurar el comentario",
        ) from error

    comentario = obtener_comentario_o_error(
        db,
        comentario_id,
    )

    return serializar_comentario(
        db,
        comentario,
        administrador.id_usr,
    )


# ============================================================
# REACCIONES DE COMENTARIOS
# ============================================================

@app.get(
    "/comentarios/{comentario_id}/reacciones",
    response_model=list[ReaccionEmojiRespuesta],
)
def listar_reacciones_comentario(
    comentario_id: int,
    usuario_id: int | None = Query(default=None),
    db: Session = Depends(obtener_sesion),
):
    comentario = obtener_comentario_o_error(
        db,
        comentario_id,
    )

    if comentario.estatus != 1:
        raise HTTPException(
            status_code=404,
            detail="Comentario no encontrado",
        )

    if usuario_id is not None:
        obtener_usuario_o_error(db, usuario_id)

    return obtener_reacciones_comentario(
        db,
        comentario_id,
        usuario_id,
    )


@app.post(
    "/comentarios/{comentario_id}/reacciones",
    response_model=list[ReaccionEmojiRespuesta],
)
def reaccionar_comentario(
    comentario_id: int,
    datos: ComentarioReaccionCrear,
    db: Session = Depends(obtener_sesion),
):
    usuario = obtener_usuario_o_error(
        db,
        datos.usuario_id,
    )

    if usuario.estatus != 1:
        raise HTTPException(
            status_code=403,
            detail="La cuenta del usuario está inactiva",
        )

    comentario = obtener_comentario_o_error(
        db,
        comentario_id,
    )

    if comentario.estatus != 1:
        raise HTTPException(
            status_code=404,
            detail="Comentario no encontrado",
        )

    emoji = validar_emoji_comentario(datos.emoji)

    reaccion = db.scalar(
        select(ComentarioReaccion).where(
            ComentarioReaccion.comentario_id
            == comentario_id,
            ComentarioReaccion.usuario_id
            == usuario.id_usr,
        )
    )

    if reaccion is None:
        reaccion = ComentarioReaccion(
            comentario_id=comentario_id,
            usuario_id=usuario.id_usr,
            emoji=emoji,
        )
        db.add(reaccion)
    elif reaccion.emoji == emoji:
        db.delete(reaccion)
    else:
        reaccion.emoji = emoji

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="La reacción ya está registrada",
        ) from error
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="No se pudo registrar la reacción",
        ) from error

    return obtener_reacciones_comentario(
        db,
        comentario_id,
        usuario.id_usr,
    )


@app.delete(
    "/comentarios/{comentario_id}/reacciones/{usuario_id}",
    response_model=list[ReaccionEmojiRespuesta],
)
def eliminar_reaccion_comentario(
    comentario_id: int,
    usuario_id: int,
    db: Session = Depends(obtener_sesion),
):
    obtener_usuario_o_error(db, usuario_id)
    comentario = obtener_comentario_o_error(
        db,
        comentario_id,
    )

    reaccion = db.scalar(
        select(ComentarioReaccion).where(
            ComentarioReaccion.comentario_id
            == comentario_id,
            ComentarioReaccion.usuario_id
            == usuario_id,
        )
    )

    if reaccion is not None:
        try:
            db.delete(reaccion)
            db.commit()
        except SQLAlchemyError as error:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail="No se pudo eliminar la reacción",
            ) from error

    return obtener_reacciones_comentario(
        db,
        comentario.id_con,
        usuario_id,
    )


# ============================================================
# REACCIONES
# ============================================================

@app.get(
    "/reacciones",
    response_model=list[ReaccionBlogRespuesta],
)
def listar_reacciones(
    blog_id: int | None = Query(None),
    usuario_id: int | None = Query(None),
    db: Session = Depends(
        obtener_sesion,
    ),
):
    consulta = select(ReaccionBlog)

    if blog_id is not None:
        consulta = consulta.where(
            ReaccionBlog.blog_id == blog_id,
        )

    if usuario_id is not None:
        consulta = consulta.where(
            ReaccionBlog.usuario_id == usuario_id,
        )

    return db.scalars(
        consulta.order_by(
            ReaccionBlog.id_reaccion.desc(),
        )
    ).all()


@app.post(
    "/reacciones",
    response_model=ReaccionBlogRespuesta,
    status_code=201,
)
def registrar_reaccion(
    datos: ReaccionBlogCrear,
    db: Session = Depends(
        obtener_sesion,
    ),
):
    obtener_usuario_o_error(
        db,
        datos.usuario_id,
    )

    blog = obtener_blog_o_error(
        db,
        datos.blog_id,
    )

    tipo = validar_reaccion(
        datos.tipo,
    )

    reaccion = db.scalar(
        select(ReaccionBlog).where(
            ReaccionBlog.usuario_id == datos.usuario_id,
            ReaccionBlog.blog_id == datos.blog_id,
        )
    )

    if reaccion is None:
        reaccion = ReaccionBlog(
            usuario_id=datos.usuario_id,
            blog_id=datos.blog_id,
            tipo=tipo,
        )

        db.add(reaccion)

        if tipo == "like":
            blog.likes = (
                blog.likes or 0
            ) + 1

            autor = obtener_usuario_o_error(
                db,
                blog.usr_id,
            )

            registrar_puntos(
                db,
                autor,
                1,
                "Recibió un like",
            )
        else:
            blog.dislikes = (
                blog.dislikes or 0
            ) + 1

    elif reaccion.tipo != tipo:
        if reaccion.tipo == "like":
            blog.likes = max(
                (blog.likes or 0) - 1,
                0,
            )
            blog.dislikes = (
                blog.dislikes or 0
            ) + 1
        else:
            blog.dislikes = max(
                (blog.dislikes or 0) - 1,
                0,
            )
            blog.likes = (
                blog.likes or 0
            ) + 1

        reaccion.tipo = tipo

    try:
        db.commit()
        db.refresh(reaccion)
    except SQLAlchemyError as error:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="No se pudo registrar la reacción",
        ) from error

    return reaccion


@app.post("/blog/{blog_id}/like")
def dar_like(
    blog_id: int,
    usuario_id: int | None = Query(None),
    db: Session = Depends(
        obtener_sesion,
    ),
):
    blog = obtener_blog_o_error(
        db,
        blog_id,
    )

    if usuario_id is None:
        blog.likes = (
            blog.likes or 0
        ) + 1

        db.commit()
        db.refresh(blog)

        return {
            "likes": blog.likes,
            "dislikes": blog.dislikes,
        }

    datos = ReaccionBlogCrear(
        usuario_id=usuario_id,
        blog_id=blog_id,
        tipo="like",
    )

    reaccion = registrar_reaccion(
        datos,
        db,
    )

    return {
        "mensaje": "Like registrado",
        "id_reaccion": reaccion.id_reaccion,
        "likes": blog.likes,
        "dislikes": blog.dislikes,
    }


@app.post("/blog/{blog_id}/dislike")
def dar_dislike(
    blog_id: int,
    usuario_id: int | None = Query(None),
    db: Session = Depends(
        obtener_sesion,
    ),
):
    blog = obtener_blog_o_error(
        db,
        blog_id,
    )

    if usuario_id is None:
        blog.dislikes = (
            blog.dislikes or 0
        ) + 1

        db.commit()
        db.refresh(blog)

        return {
            "likes": blog.likes,
            "dislikes": blog.dislikes,
        }

    datos = ReaccionBlogCrear(
        usuario_id=usuario_id,
        blog_id=blog_id,
        tipo="dislike",
    )

    reaccion = registrar_reaccion(
        datos,
        db,
    )

    return {
        "mensaje": "Dislike registrado",
        "id_reaccion": reaccion.id_reaccion,
        "likes": blog.likes,
        "dislikes": blog.dislikes,
    }


# ============================================================
# PRODUCTOS
# ============================================================

@app.get(
    "/productos",
    response_model=list[ProductoRespuesta],
)
def listar_productos(
    buscar: str | None = Query(default=None),
    categoria: str | None = Query(default=None),
    disponibilidad: str | None = Query(default=None),
    stock_bajo: bool = Query(default=False),
    incluir_inactivos: bool = Query(default=False),
    administrador_id: int | None = Query(default=None),
    orden: str = Query(default="recientes"),
    db: Session = Depends(obtener_sesion),
):
    if incluir_inactivos:
        if administrador_id is None:
            raise HTTPException(
                status_code=403,
                detail="Debes indicar el administrador",
            )
        validar_administrador(db, administrador_id)

    consulta = select(Producto)

    if not incluir_inactivos:
        consulta = consulta.where(Producto.estatus == 1)

    if buscar is not None and buscar.strip():
        termino = f"%{buscar.strip()}%"
        consulta = consulta.where(
            (Producto.nombre.ilike(termino))
            | (Producto.descripcion.ilike(termino))
            | (Producto.categoria.ilike(termino))
        )

    if categoria is not None and categoria.strip():
        consulta = consulta.where(
            Producto.categoria == categoria.strip(),
        )

    if disponibilidad is not None:
        disponibilidad_limpia = disponibilidad.strip().lower()
        if disponibilidad_limpia == "disponibles":
            consulta = consulta.where(
                Producto.estatus == 1,
                Producto.stock > 0,
            )
        elif disponibilidad_limpia == "agotados":
            consulta = consulta.where(Producto.stock == 0)
        elif disponibilidad_limpia not in {"", "todos"}:
            raise HTTPException(
                status_code=422,
                detail=(
                    "La disponibilidad debe ser "
                    "'todos', 'disponibles' o 'agotados'"
                ),
            )

    if stock_bajo:
        consulta = consulta.where(
            Producto.stock > 0,
            Producto.stock <= 5,
        )

    orden_limpio = orden.strip().lower()
    ordenes = {
        "recientes": Producto.id_producto.desc(),
        "antiguos": Producto.id_producto.asc(),
        "nombre_asc": Producto.nombre.asc(),
        "nombre_desc": Producto.nombre.desc(),
        "precio_asc": Producto.precio.asc(),
        "precio_desc": Producto.precio.desc(),
        "stock_asc": Producto.stock.asc(),
        "stock_desc": Producto.stock.desc(),
    }

    if orden_limpio not in ordenes:
        raise HTTPException(
            status_code=422,
            detail="El criterio de orden no es válido",
        )

    productos = db.scalars(
        consulta.order_by(ordenes[orden_limpio])
    ).all()

    return [serializar_producto(producto) for producto in productos]


@app.get(
    "/productos/{producto_id}",
    response_model=ProductoRespuesta,
)
def obtener_producto(
    producto_id: int,
    administrador_id: int | None = Query(default=None),
    db: Session = Depends(obtener_sesion),
):
    producto = obtener_producto_o_error(db, producto_id)

    if producto.estatus != 1:
        if administrador_id is None:
            raise HTTPException(
                status_code=404,
                detail="Producto no encontrado",
            )
        validar_administrador(db, administrador_id)

    return serializar_producto(producto)


@app.post(
    "/productos",
    response_model=ProductoRespuesta,
    status_code=201,
)
def crear_producto(
    datos: ProductoCrear,
    db: Session = Depends(obtener_sesion),
):
    validar_administrador(db, datos.administrador_id)
    nombre, precio, categoria = validar_datos_producto(
        datos.nombre,
        datos.precio,
        datos.stock,
        datos.categoria,
    )

    producto = Producto(
        nombre=nombre,
        descripcion=texto_opcional(datos.descripcion),
        precio=precio,
        stock=datos.stock,
        categoria=categoria,
        imagen=texto_opcional(datos.imagen),
        estatus=1,
    )
    db.add(producto)

    try:
        db.commit()
        db.refresh(producto)
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Los datos del producto no son válidos",
        ) from error
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="No se pudo guardar el producto",
        ) from error

    return serializar_producto(producto)


@app.post(
    "/productos/upload",
    response_model=ProductoRespuesta,
    status_code=201,
)
def crear_producto_con_imagen(
    nombre: str = Form(...),
    precio: float = Form(...),
    stock: int = Form(...),
    categoria: str = Form(...),
    administrador_id: int = Form(...),
    descripcion: str | None = Form(None),
    imagen: UploadFile = File(...),
    db: Session = Depends(obtener_sesion),
):
    validar_administrador(db, administrador_id)
    nombre_limpio, precio_decimal, categoria_limpia = validar_datos_producto(
        nombre,
        precio,
        stock,
        categoria,
    )
    ruta_archivo, ruta_publica = guardar_imagen(imagen)

    producto = Producto(
        nombre=nombre_limpio,
        descripcion=texto_opcional(descripcion),
        precio=precio_decimal,
        stock=stock,
        categoria=categoria_limpia,
        imagen=ruta_publica,
        estatus=1,
    )
    db.add(producto)

    try:
        db.commit()
        db.refresh(producto)
    except SQLAlchemyError as error:
        db.rollback()
        if ruta_archivo.exists():
            ruta_archivo.unlink()
        raise HTTPException(
            status_code=500,
            detail="No se pudo guardar el producto",
        ) from error

    return serializar_producto(producto)


@app.put(
    "/productos/{producto_id}",
    response_model=ProductoRespuesta,
)
def actualizar_producto(
    producto_id: int,
    datos: ProductoActualizar,
    db: Session = Depends(obtener_sesion),
):
    validar_administrador(db, datos.administrador_id)
    producto = obtener_producto_o_error(db, producto_id)

    if producto.estatus != 1:
        raise HTTPException(
            status_code=409,
            detail="No se puede editar un producto inactivo",
        )

    nombre, precio, categoria = validar_datos_producto(
        datos.nombre,
        datos.precio,
        datos.stock,
        datos.categoria,
    )

    producto.nombre = nombre
    producto.descripcion = texto_opcional(datos.descripcion)
    producto.precio = precio
    producto.stock = datos.stock
    producto.categoria = categoria
    producto.imagen = texto_opcional(datos.imagen)

    try:
        db.commit()
        db.refresh(producto)
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Los datos del producto no son válidos",
        ) from error
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="No se pudo actualizar el producto",
        ) from error

    return serializar_producto(producto)


@app.put(
    "/productos/{producto_id}/upload",
    response_model=ProductoRespuesta,
)
def actualizar_producto_con_imagen(
    producto_id: int,
    nombre: str = Form(...),
    precio: float = Form(...),
    stock: int = Form(...),
    categoria: str = Form(...),
    administrador_id: int = Form(...),
    descripcion: str | None = Form(None),
    imagen: UploadFile | None = File(None),
    db: Session = Depends(obtener_sesion),
):
    validar_administrador(db, administrador_id)
    producto = obtener_producto_o_error(db, producto_id)

    if producto.estatus != 1:
        raise HTTPException(
            status_code=409,
            detail="No se puede editar un producto inactivo",
        )

    nombre_limpio, precio_decimal, categoria_limpia = validar_datos_producto(
        nombre,
        precio,
        stock,
        categoria,
    )

    nueva_ruta_archivo: Path | None = None
    nueva_ruta_publica: str | None = None
    imagen_anterior = producto.imagen

    if imagen is not None and imagen.filename:
        nueva_ruta_archivo, nueva_ruta_publica = guardar_imagen(imagen)

    producto.nombre = nombre_limpio
    producto.descripcion = texto_opcional(descripcion)
    producto.precio = precio_decimal
    producto.stock = stock
    producto.categoria = categoria_limpia
    if nueva_ruta_publica is not None:
        producto.imagen = nueva_ruta_publica

    try:
        db.commit()
        db.refresh(producto)
    except SQLAlchemyError as error:
        db.rollback()
        if nueva_ruta_archivo is not None and nueva_ruta_archivo.exists():
            nueva_ruta_archivo.unlink()
        raise HTTPException(
            status_code=500,
            detail="No se pudo actualizar el producto",
        ) from error

    if nueva_ruta_publica is not None:
        eliminar_archivo_local(imagen_anterior)

    return serializar_producto(producto)


@app.put(
    "/productos/{producto_id}/stock",
    response_model=ProductoRespuesta,
)
def ajustar_stock_producto(
    producto_id: int,
    datos: ProductoAjustarStock,
    db: Session = Depends(obtener_sesion),
):
    validar_administrador(db, datos.administrador_id)
    producto = obtener_producto_o_error(db, producto_id)
    producto.stock = datos.stock

    try:
        db.commit()
        db.refresh(producto)
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="No se pudo actualizar el stock",
        ) from error

    return serializar_producto(producto)


@app.delete("/productos/{producto_id}")
def eliminar_producto(
    producto_id: int,
    datos: ProductoGestionarEstado,
    db: Session = Depends(obtener_sesion),
):
    validar_administrador(db, datos.administrador_id)
    producto = obtener_producto_o_error(db, producto_id)

    if producto.estatus == 0:
        return {"mensaje": "El producto ya estaba desactivado"}

    producto.estatus = 0

    try:
        db.commit()
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="No se pudo desactivar el producto",
        ) from error

    return {"mensaje": "Producto desactivado correctamente"}


@app.put(
    "/productos/{producto_id}/restaurar",
    response_model=ProductoRespuesta,
)
def restaurar_producto(
    producto_id: int,
    datos: ProductoGestionarEstado,
    db: Session = Depends(obtener_sesion),
):
    validar_administrador(db, datos.administrador_id)
    producto = obtener_producto_o_error(db, producto_id)
    producto.estatus = 1

    try:
        db.commit()
        db.refresh(producto)
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="No se pudo restaurar el producto",
        ) from error

    return serializar_producto(producto)


# ============================================================
# CARRITO
# ============================================================

@app.get(
    "/carrito/{usuario_id}",
    response_model=CarritoResumenRespuesta,
)
def obtener_carrito(
    usuario_id: int,
    db: Session = Depends(obtener_sesion),
):
    validar_usuario_activo(db, usuario_id)
    carrito = obtener_carrito_usuario(db, usuario_id, crear=True)

    try:
        db.commit()
        db.refresh(carrito)
    except IntegrityError:
        db.rollback()
        carrito = obtener_carrito_usuario(db, usuario_id, crear=False)
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="No se pudo obtener el carrito",
        ) from error

    carrito = obtener_carrito_usuario(db, usuario_id, crear=False)
    return serializar_resumen_carrito(carrito)


@app.post(
    "/carrito",
    response_model=CarritoDetalleRespuesta,
    status_code=201,
)
def agregar_carrito(
    datos: CarritoDetalleCrear,
    db: Session = Depends(obtener_sesion),
):
    validar_usuario_activo(db, datos.usuario_id)
    producto = obtener_producto_o_error(db, datos.producto_id)

    if producto.estatus != 1 or producto.stock <= 0:
        raise HTTPException(
            status_code=409,
            detail="El producto no está disponible",
        )

    carrito = obtener_carrito_usuario(db, datos.usuario_id, crear=True)
    detalle = db.scalar(
        select(CarritoDetalle).where(
            CarritoDetalle.carrito_id == carrito.id_carrito,
            CarritoDetalle.producto_id == producto.id_producto,
        )
    )
    nueva_cantidad = datos.cantidad
    if detalle is not None:
        nueva_cantidad += detalle.cantidad

    if nueva_cantidad > producto.stock:
        raise HTTPException(
            status_code=409,
            detail="La cantidad supera el stock disponible",
        )

    if detalle is None:
        detalle = CarritoDetalle(
            carrito_id=carrito.id_carrito,
            producto_id=producto.id_producto,
            cantidad=nueva_cantidad,
        )
        db.add(detalle)
    else:
        detalle.cantidad = nueva_cantidad

    try:
        db.commit()
        detalle = db.scalar(
            select(CarritoDetalle)
            .options(selectinload(CarritoDetalle.producto))
            .where(CarritoDetalle.id_detalle == detalle.id_detalle)
        )
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="El producto ya está en el carrito",
        ) from error
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="No se pudo agregar el producto al carrito",
        ) from error

    return serializar_detalle_carrito(detalle)


@app.put(
    "/carrito/{detalle_id}",
    response_model=CarritoDetalleRespuesta,
)
def actualizar_cantidad(
    detalle_id: int,
    datos: CarritoDetalleActualizar,
    db: Session = Depends(obtener_sesion),
):
    validar_usuario_activo(db, datos.usuario_id)
    detalle = db.scalar(
        select(CarritoDetalle)
        .join(Carrito)
        .options(selectinload(CarritoDetalle.producto))
        .where(
            CarritoDetalle.id_detalle == detalle_id,
            Carrito.usuario_id == datos.usuario_id,
        )
    )
    if detalle is None:
        raise HTTPException(status_code=404, detail="Artículo no encontrado")

    producto = detalle.producto
    if producto.estatus != 1 or producto.stock <= 0:
        raise HTTPException(
            status_code=409,
            detail="El producto no está disponible",
        )
    if datos.cantidad > producto.stock:
        raise HTTPException(
            status_code=409,
            detail="La cantidad supera el stock disponible",
        )

    detalle.cantidad = datos.cantidad
    try:
        db.commit()
        db.refresh(detalle)
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="No se pudo actualizar la cantidad",
        ) from error

    return serializar_detalle_carrito(detalle)


@app.delete("/carrito/usuario/{usuario_id}")
def vaciar_carrito(
    usuario_id: int,
    db: Session = Depends(obtener_sesion),
):
    validar_usuario_activo(db, usuario_id)
    carrito = obtener_carrito_usuario(db, usuario_id, crear=False)
    if carrito is None or not carrito.detalles:
        return {"mensaje": "El carrito ya está vacío"}

    try:
        for detalle in list(carrito.detalles):
            db.delete(detalle)
        db.commit()
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="No se pudo vaciar el carrito",
        ) from error

    return {"mensaje": "Carrito vaciado correctamente"}


@app.delete("/carrito/{detalle_id}")
def eliminar_del_carrito(
    detalle_id: int,
    usuario_id: int = Query(..., gt=0),
    db: Session = Depends(obtener_sesion),
):
    validar_usuario_activo(db, usuario_id)
    detalle = db.scalar(
        select(CarritoDetalle)
        .join(Carrito)
        .where(
            CarritoDetalle.id_detalle == detalle_id,
            Carrito.usuario_id == usuario_id,
        )
    )
    if detalle is None:
        raise HTTPException(status_code=404, detail="Artículo no encontrado")

    try:
        db.delete(detalle)
        db.commit()
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="No se pudo eliminar el producto",
        ) from error

    return {"mensaje": "Producto eliminado del carrito"}


# ============================================================
# COMPRA TRANSACCIONAL
# ============================================================

@app.post(
    "/compras/confirmar",
    response_model=CompraConfirmarRespuesta,
    status_code=201,
)
def confirmar_compra(
    datos: CompraConfirmar,
    db: Session = Depends(obtener_sesion),
):
    usuario = validar_usuario_activo(db, datos.usuario_id)
    carrito = db.scalar(
        select(Carrito)
        .where(Carrito.usuario_id == usuario.id_usr)
        .with_for_update()
    )
    if carrito is None:
        raise HTTPException(status_code=409, detail="El carrito está vacío")

    detalles = db.scalars(
        select(CarritoDetalle)
        .where(CarritoDetalle.carrito_id == carrito.id_carrito)
        .order_by(CarritoDetalle.producto_id)
        .with_for_update()
    ).all()
    if not detalles:
        raise HTTPException(status_code=409, detail="El carrito está vacío")

    productos_ids = [detalle.producto_id for detalle in detalles]
    productos = db.scalars(
        select(Producto)
        .where(Producto.id_producto.in_(productos_ids))
        .order_by(Producto.id_producto)
        .with_for_update()
    ).all()
    productos_por_id = {
        producto.id_producto: producto for producto in productos
    }

    total = Decimal("0.00")
    compra: list[tuple[CarritoDetalle, Producto]] = []
    for detalle in detalles:
        producto = productos_por_id.get(detalle.producto_id)
        if producto is None:
            raise HTTPException(
                status_code=409,
                detail="El carrito contiene un producto inexistente",
            )
        if producto.estatus != 1:
            raise HTTPException(
                status_code=409,
                detail=f"{producto.nombre} está inactivo",
            )
        if detalle.cantidad <= 0:
            raise HTTPException(
                status_code=409,
                detail=f"La cantidad de {producto.nombre} no es válida",
            )
        if producto.stock < detalle.cantidad:
            raise HTTPException(
                status_code=409,
                detail=f"Stock insuficiente para {producto.nombre}",
            )
        if producto.precio <= 0:
            raise HTTPException(
                status_code=409,
                detail=f"El precio de {producto.nombre} no es válido",
            )

        total += Decimal(producto.precio) * detalle.cantidad
        compra.append((detalle, producto))

    if total <= 0:
        raise HTTPException(
            status_code=409,
            detail="El total de la compra no es válido",
        )

    pedido = Pedido(
        usuario_id=usuario.id_usr,
        total=total,
        estado="pendiente",
    )
    db.add(pedido)

    try:
        db.flush()
        cantidad_articulos = 0
        for detalle, producto in compra:
            db.add(
                PedidoDetalle(
                    pedido_id=pedido.id_pedido,
                    producto_id=producto.id_producto,
                    cantidad=detalle.cantidad,
                    precio_unitario=producto.precio,
                )
            )
            producto.stock -= detalle.cantidad
            cantidad_articulos += detalle.cantidad
            db.delete(detalle)

        registrar_puntos(db, usuario, 8, "Realizó una compra")
        db.commit()
        db.refresh(pedido)
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="La compra ya fue procesada o contiene datos duplicados",
        ) from error
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="No se pudo confirmar la compra",
        ) from error

    return {
        "mensaje": "Compra realizada correctamente",
        "pedido_id": pedido.id_pedido,
        "total": float(pedido.total),
        "estado": pedido.estado,
        "fecha": pedido.fecha,
        "cantidad_productos": len(compra),
        "cantidad_articulos": cantidad_articulos,
    }


# Compatibilidad con la ruta anterior.
@app.post(
    "/pedidos",
    response_model=CompraConfirmarRespuesta,
    status_code=201,
)
def crear_pedido(
    datos: CompraConfirmar,
    db: Session = Depends(obtener_sesion),
):
    return confirmar_compra(datos, db)


# ============================================================
# PEDIDOS
# ============================================================

@app.get(
    "/pedidos",
    response_model=list[PedidoRespuesta],
)
def listar_pedidos(
    usuario_id: int | None = Query(None),
    db: Session = Depends(obtener_sesion),
):
    consulta = select(Pedido).options(
        selectinload(Pedido.detalles)
        .selectinload(PedidoDetalle.producto)
    )
    if usuario_id is not None:
        validar_usuario_activo(db, usuario_id)
        consulta = consulta.where(Pedido.usuario_id == usuario_id)

    pedidos = db.scalars(
        consulta.order_by(Pedido.id_pedido.desc())
    ).all()
    return [serializar_pedido(pedido) for pedido in pedidos]


@app.put(
    "/pedidos/{pedido_id}/cancelar",
    response_model=PedidoRespuesta,
)
def cancelar_pedido(
    pedido_id: int,
    usuario_id: int = Query(..., gt=0),
    db: Session = Depends(obtener_sesion),
):
    usuario = validar_usuario_activo(db, usuario_id)
    pedido = db.scalar(
        select(Pedido)
        .options(
            selectinload(Pedido.detalles)
            .selectinload(PedidoDetalle.producto)
        )
        .where(Pedido.id_pedido == pedido_id)
        .with_for_update()
    )
    if pedido is None:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if pedido.usuario_id != usuario.id_usr and usuario.tip_usu != 1:
        raise HTTPException(
            status_code=403,
            detail="No puedes cancelar este pedido",
        )
    if pedido.estado != "pendiente":
        raise HTTPException(
            status_code=409,
            detail="Solo se pueden cancelar pedidos pendientes",
        )

    productos_ids = [detalle.producto_id for detalle in pedido.detalles]
    productos = db.scalars(
        select(Producto)
        .where(Producto.id_producto.in_(productos_ids))
        .order_by(Producto.id_producto)
        .with_for_update()
    ).all()
    productos_por_id = {
        producto.id_producto: producto for producto in productos
    }

    try:
        for detalle in pedido.detalles:
            producto = productos_por_id.get(detalle.producto_id)
            if producto is not None:
                producto.stock += detalle.cantidad
        pedido.estado = "cancelado"
        db.commit()
        pedido = db.scalar(
            select(Pedido)
            .options(
                selectinload(Pedido.detalles)
                .selectinload(PedidoDetalle.producto)
            )
            .where(Pedido.id_pedido == pedido_id)
        )
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="No se pudo cancelar el pedido",
        ) from error

    return serializar_pedido(pedido)


# ============================================================
# HISTORIAL DE PUNTOS Y RANKING
# ============================================================

@app.get(
    "/historial-puntos",
    response_model=list[HistorialPuntosRespuesta],
)
def listar_historial(
    usuario_id: int | None = Query(None),
    db: Session = Depends(
        obtener_sesion,
    ),
):
    consulta = select(HistorialPuntos)

    if usuario_id is not None:
        consulta = consulta.where(
            HistorialPuntos.usuario_id
            == usuario_id,
        )

    return db.scalars(
        consulta.order_by(
            HistorialPuntos.id_historial.desc(),
        )
    ).all()


@app.post(
    "/historial-puntos",
    response_model=HistorialPuntosRespuesta,
    status_code=201,
)
def crear_historial(
    datos: HistorialPuntosCrear,
    db: Session = Depends(
        obtener_sesion,
    ),
):
    usuario = obtener_usuario_o_error(
        db,
        datos.usuario_id,
    )

    historial = registrar_puntos(
        db,
        usuario,
        datos.puntos,
        datos.accion.strip(),
    )

    try:
        db.commit()
        db.refresh(historial)
    except SQLAlchemyError as error:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="No se pudieron registrar los puntos",
        ) from error

    return historial


@app.get(
    "/ranking",
    response_model=list[UsuarioRespuesta],
)
def ranking(
    db: Session = Depends(
        obtener_sesion,
    ),
):
    return db.scalars(
        select(Usuario).where(
            Usuario.estatus == 1,
        ).order_by(
            Usuario.puntos.desc(),
            Usuario.nom_usr,
        )
    ).all()