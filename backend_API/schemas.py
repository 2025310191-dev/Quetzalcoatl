from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


# ==================================================
# LOGIN
# ==================================================

class LoginRequest(BaseModel):
    mail: str = Field(
        min_length=5,
        max_length=150,
    )

    password: str = Field(
        min_length=1,
        max_length=128,
    )


# ==================================================
# USUARIOS
# ==================================================

class UsuarioCrear(BaseModel):
    nom_usr: str = Field(
        min_length=2,
        max_length=100,
    )

    mail: str = Field(
        min_length=5,
        max_length=150,
    )

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    foto_perfil: str | None = Field(
        default=None,
        max_length=500,
    )

    dir_usr: str | None = Field(
        default=None,
        max_length=200,
    )

    telefono: str | None = Field(
        default=None,
        max_length=20,
    )

    tip_usu: int = Field(
        default=2,
        ge=1,
        le=2,
    )


class UsuarioActualizar(BaseModel):
    nom_usr: str = Field(
        min_length=2,
        max_length=100,
    )

    mail: str = Field(
        min_length=5,
        max_length=150,
    )

    foto_perfil: str | None = Field(
        default=None,
        max_length=500,
    )

    dir_usr: str | None = Field(
        default=None,
        max_length=200,
    )

    telefono: str | None = Field(
        default=None,
        max_length=20,
    )

    tip_usu: int = Field(
        default=2,
        ge=1,
        le=2,
    )

    estatus: int = Field(
        default=1,
        ge=0,
        le=1,
    )


class UsuarioRespuesta(BaseModel):
    id_usr: int

    nom_usr: str

    mail: str

    foto_perfil: str | None = None

    dir_usr: str | None = None

    telefono: str | None = None

    puntos: int

    tip_usu: int

    estatus: int

    fecha_registro: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


# ==================================================
# BLOG
# ==================================================

class AutorBlogRespuesta(BaseModel):
    id_usr: int
    nom_usr: str
    foto_perfil: str | None = None

    model_config = ConfigDict(
        from_attributes=True,
    )


class BlogCrear(BaseModel):
    titulo: str = Field(
        min_length=2,
        max_length=200,
    )
    descripcion: str = Field(
        min_length=1,
    )
    categoria: str = Field(
        min_length=1,
        max_length=20,
    )
    img: str | None = Field(
        default=None,
        max_length=500,
    )
    tags: str | None = Field(
        default=None,
        max_length=255,
    )
    usr_id: int = Field(
        gt=0,
    )
    latitud: float | None = Field(
        default=None,
        ge=-90,
        le=90,
    )
    longitud: float | None = Field(
        default=None,
        ge=-180,
        le=180,
    )


class BlogActualizar(BaseModel):
    titulo: str = Field(
        min_length=2,
        max_length=200,
    )
    descripcion: str = Field(
        min_length=1,
    )
    categoria: str = Field(
        min_length=1,
        max_length=20,
    )
    img: str | None = Field(
        default=None,
        max_length=500,
    )
    tags: str | None = Field(
        default=None,
        max_length=255,
    )
    latitud: float | None = Field(
        default=None,
        ge=-90,
        le=90,
    )
    longitud: float | None = Field(
        default=None,
        ge=-180,
        le=180,
    )
    usuario_id: int = Field(
        gt=0,
    )


class BlogGestionarEstado(BaseModel):
    usuario_id: int = Field(
        gt=0,
    )


class BlogRestaurar(BaseModel):
    administrador_id: int = Field(
        gt=0,
    )


class BlogImagenCrear(BaseModel):
    blog_id: int = Field(
        gt=0,
    )
    ruta_imagen: str = Field(
        min_length=1,
        max_length=500,
    )


class BlogImagenRespuesta(BaseModel):
    id_img: int
    blog_id: int
    ruta_imagen: str

    model_config = ConfigDict(
        from_attributes=True,
    )


class BlogRespuesta(BaseModel):
    id_blog: int
    titulo: str
    descripcion: str
    img: str | None = None
    tags: str | None = None
    categoria: str
    latitud: float | None = None
    longitud: float | None = None
    likes: int
    dislikes: int
    visualizaciones: int
    estatus: int
    fecha_publicacion: datetime
    usr_id: int
    autor: AutorBlogRespuesta | None = None
    imagenes: list[BlogImagenRespuesta] = Field(
        default_factory=list,
    )
    cantidad_comentarios: int = Field(
        default=0,
        ge=0,
    )

    model_config = ConfigDict(
        from_attributes=True,
    )


# ==================================================
# COMENTARIOS
# ==================================================

class AutorComentarioRespuesta(BaseModel):
    id_usr: int

    nom_usr: str

    foto_perfil: str | None = None

    model_config = ConfigDict(
        from_attributes=True,
    )


class ComentarioCrear(BaseModel):
    comentario: str = Field(
        min_length=1,
        max_length=1000,
    )

    usr_id: int = Field(
        gt=0,
    )

    blog_id: int = Field(
        gt=0,
    )


class ComentarioActualizar(BaseModel):
    comentario: str = Field(
        min_length=1,
        max_length=1000,
    )

    usuario_id: int = Field(
        gt=0,
    )


class ComentarioEliminar(BaseModel):
    usuario_id: int = Field(
        gt=0,
    )


class ComentarioRestaurar(BaseModel):
    administrador_id: int = Field(
        gt=0,
    )


class ReaccionEmojiRespuesta(BaseModel):
    emoji: str = Field(
        min_length=1,
        max_length=30,
    )

    cantidad: int = Field(
        default=0,
        ge=0,
    )

    seleccionada: bool = False


class ComentarioRespuesta(BaseModel):
    id_con: int

    comentario: str

    fecha: datetime

    estatus: int

    usr_id: int

    blog_id: int

    autor: AutorComentarioRespuesta

    reacciones: list[
        ReaccionEmojiRespuesta
    ] = Field(
        default_factory=list,
    )


# ==================================================
# REACCIONES DE COMENTARIOS
# ==================================================

class ComentarioReaccionCrear(BaseModel):
    usuario_id: int = Field(
        gt=0,
    )

    emoji: str = Field(
        min_length=1,
        max_length=30,
    )


class ComentarioReaccionEliminar(BaseModel):
    usuario_id: int = Field(
        gt=0,
    )


class ComentarioReaccionRespuesta(BaseModel):
    id_reaccion: int

    comentario_id: int

    usuario_id: int

    emoji: str

    fecha: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class ComentarioReaccionesRespuesta(
    BaseModel
):
    comentario_id: int

    reacciones: list[
        ReaccionEmojiRespuesta
    ] = Field(
        default_factory=list,
    )


# ==================================================
# LIKE / DISLIKE DEL BLOG
# ==================================================

class ReaccionBlogCrear(BaseModel):
    usuario_id: int = Field(
        gt=0,
    )

    blog_id: int = Field(
        gt=0,
    )

    tipo: str = Field(
        min_length=1,
        max_length=20,
    )


class ReaccionBlogRespuesta(BaseModel):
    id_reaccion: int

    usuario_id: int

    blog_id: int

    tipo: str

    fecha: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


# ==================================================
# PRODUCTOS
# ==================================================

class ProductoBase(BaseModel):
    nombre: str = Field(
        min_length=2,
        max_length=150,
    )
    descripcion: str | None = Field(
        default=None,
        max_length=5000,
    )
    precio: float = Field(
        gt=0,
        le=99999999.99,
    )
    stock: int = Field(
        ge=0,
    )
    categoria: str = Field(
        min_length=1,
        max_length=100,
    )
    imagen: str | None = Field(
        default=None,
        max_length=500,
    )


class ProductoCrear(ProductoBase):
    administrador_id: int = Field(
        gt=0,
    )


class ProductoActualizar(ProductoBase):
    administrador_id: int = Field(
        gt=0,
    )


class ProductoGestionarEstado(BaseModel):
    administrador_id: int = Field(
        gt=0,
    )


class ProductoAjustarStock(BaseModel):
    administrador_id: int = Field(
        gt=0,
    )
    stock: int = Field(
        ge=0,
    )


class ProductoRespuesta(BaseModel):
    id_producto: int
    nombre: str
    descripcion: str | None = None
    precio: float
    stock: int
    imagen: str | None = None
    categoria: str
    estatus: int
    fecha_creacion: datetime
    disponible: bool = False
    agotado: bool = False
    stock_bajo: bool = False

    model_config = ConfigDict(
        from_attributes=True,
    )


# ==================================================
# CARRITO
# ==================================================

class CarritoCrear(BaseModel):
    usuario_id: int = Field(
        gt=0,
    )


class CarritoProductoRespuesta(BaseModel):
    id_producto: int
    nombre: str
    descripcion: str | None = None
    precio: float
    stock: int
    imagen: str | None = None
    categoria: str
    estatus: int
    disponible: bool = False
    agotado: bool = False
    stock_bajo: bool = False


class CarritoDetalleCrear(BaseModel):
    usuario_id: int = Field(
        gt=0,
    )
    producto_id: int = Field(
        gt=0,
    )
    cantidad: int = Field(
        default=1,
        gt=0,
    )


class CarritoDetalleActualizar(BaseModel):
    usuario_id: int = Field(
        gt=0,
    )
    cantidad: int = Field(
        gt=0,
    )


class CarritoDetalleRespuesta(BaseModel):
    id_detalle: int
    carrito_id: int
    producto_id: int
    cantidad: int
    producto: CarritoProductoRespuesta
    precio_unitario: float
    subtotal: float
    cantidad_valida: bool
    disponible: bool


class CarritoResumenRespuesta(BaseModel):
    id_carrito: int
    usuario_id: int
    fecha_creacion: datetime
    detalles: list[CarritoDetalleRespuesta] = Field(
        default_factory=list,
    )
    cantidad_productos: int = Field(
        default=0,
        ge=0,
    )
    cantidad_articulos: int = Field(
        default=0,
        ge=0,
    )
    subtotal: float = Field(
        default=0,
        ge=0,
    )
    total: float = Field(
        default=0,
        ge=0,
    )
    carrito_valido: bool = True
    mensajes: list[str] = Field(
        default_factory=list,
    )


class CarritoVaciar(BaseModel):
    usuario_id: int = Field(
        gt=0,
    )


# ==================================================
# COMPRA
# ==================================================

class CompraConfirmar(BaseModel):
    usuario_id: int = Field(
        gt=0,
    )


class CompraConfirmarRespuesta(BaseModel):
    mensaje: str
    pedido_id: int
    total: float = Field(
        gt=0,
    )
    estado: str
    fecha: datetime
    cantidad_productos: int = Field(
        gt=0,
    )
    cantidad_articulos: int = Field(
        gt=0,
    )


# ==================================================
# PEDIDOS
# ==================================================

class PedidoCrear(BaseModel):
    usuario_id: int = Field(
        gt=0,
    )


class PedidoEstadoActualizar(BaseModel):
    estado: str = Field(
        min_length=1,
        max_length=30,
    )


class PedidoProductoRespuesta(BaseModel):
    id_producto: int
    nombre: str
    imagen: str | None = None
    categoria: str


class PedidoDetalleCrear(BaseModel):
    pedido_id: int = Field(
        gt=0,
    )
    producto_id: int = Field(
        gt=0,
    )
    cantidad: int = Field(
        gt=0,
    )
    precio_unitario: float = Field(
        gt=0,
    )


class PedidoDetalleRespuesta(BaseModel):
    id_detalle: int
    pedido_id: int
    producto_id: int
    cantidad: int
    precio_unitario: float
    subtotal: float
    producto: PedidoProductoRespuesta | None = None


class PedidoRespuesta(BaseModel):
    id_pedido: int
    usuario_id: int
    total: float
    estado: str
    fecha: datetime
    detalles: list[PedidoDetalleRespuesta] = Field(
        default_factory=list,
    )
    cantidad_productos: int = Field(
        default=0,
        ge=0,
    )
    cantidad_articulos: int = Field(
        default=0,
        ge=0,
    )


# ==================================================
# HISTORIAL DE PUNTOS
# ==================================================

class HistorialPuntosCrear(BaseModel):
    usuario_id: int = Field(
        gt=0,
    )

    puntos: int

    accion: str = Field(
        min_length=1,
        max_length=255,
    )


class HistorialPuntosRespuesta(BaseModel):
    id_historial: int

    usuario_id: int

    puntos: int

    accion: str

    fecha: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )