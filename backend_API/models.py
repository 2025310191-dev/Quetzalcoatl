from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    DECIMAL,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from database import Base


# ============================================================
# USUARIOS
# ============================================================

class Usuario(Base):
    __tablename__ = "usuario"
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8mb4",
    }

    id_usr = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    nom_usr = Column(
        String(100),
        nullable=False,
    )

    mail = Column(
        String(150),
        nullable=False,
        unique=True,
        index=True,
    )

    pass_hash = Column(
        "pass",
        String(255),
        nullable=False,
    )

    foto_perfil = Column(
        String(500),
        nullable=True,
    )

    dir_usr = Column(
        String(200),
        nullable=True,
    )

    telefono = Column(
        String(20),
        nullable=True,
    )

    puntos = Column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    tip_usu = Column(
        Integer,
        nullable=False,
        default=2,
        server_default="2",
    )

    estatus = Column(
        Integer,
        nullable=False,
        default=1,
        server_default="1",
    )

    fecha_registro = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    blogs = relationship(
        "Blog",
        back_populates="usuario",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    comentarios = relationship(
        "Comentario",
        back_populates="usuario",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    reacciones_blog = relationship(
        "ReaccionBlog",
        back_populates="usuario",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    reacciones_comentarios = relationship(
        "ComentarioReaccion",
        back_populates="usuario",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    carritos = relationship(
        "Carrito",
        back_populates="usuario",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    pedidos = relationship(
        "Pedido",
        back_populates="usuario",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    historial_puntos = relationship(
        "HistorialPuntos",
        back_populates="usuario",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


# ============================================================
# BLOG
# ============================================================

class Blog(Base):
    __tablename__ = "blog"
    __table_args__ = (
        Index(
            "ix_blog_categoria",
            "categoria",
        ),
        Index(
            "ix_blog_estatus",
            "estatus",
        ),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
        },
    )

    id_blog = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    titulo = Column(
        String(200),
        nullable=False,
    )

    descripcion = Column(
        Text,
        nullable=False,
    )

    img = Column(
        String(500),
        nullable=True,
    )

    tags = Column(
        String(255),
        nullable=True,
    )

    categoria = Column(
        Enum(
            "flora",
            "fauna",
            name="categoria_blog",
        ),
        nullable=False,
        default="flora",
        server_default="flora",
    )

    latitud = Column(
        DECIMAL(10, 8),
        nullable=True,
    )

    longitud = Column(
        DECIMAL(11, 8),
        nullable=True,
    )

    likes = Column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    dislikes = Column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    visualizaciones = Column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    estatus = Column(
        Integer,
        nullable=False,
        default=1,
        server_default="1",
    )

    fecha_publicacion = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    usr_id = Column(
        Integer,
        ForeignKey(
            "usuario.id_usr",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    usuario = relationship(
        "Usuario",
        back_populates="blogs",
    )

    comentarios = relationship(
        "Comentario",
        back_populates="blog",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    imagenes = relationship(
        "BlogImagen",
        back_populates="blog",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    reacciones = relationship(
        "ReaccionBlog",
        back_populates="blog",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


# ============================================================
# IMÁGENES ADICIONALES DEL BLOG
# ============================================================

class BlogImagen(Base):
    __tablename__ = "blog_imagenes"
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8mb4",
    }

    id_img = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    blog_id = Column(
        Integer,
        ForeignKey(
            "blog.id_blog",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    ruta_imagen = Column(
        String(500),
        nullable=False,
    )

    blog = relationship(
        "Blog",
        back_populates="imagenes",
    )


# ============================================================
# COMENTARIOS
# ============================================================

class Comentario(Base):
    __tablename__ = "comentarios"
    __table_args__ = (
        Index(
            "ix_comentarios_blog_estatus",
            "blog_id",
            "estatus",
        ),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
        },
    )

    id_con = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    comentario = Column(
        Text,
        nullable=False,
    )

    fecha = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    estatus = Column(
        Integer,
        nullable=False,
        default=1,
        server_default="1",
    )

    usr_id = Column(
        Integer,
        ForeignKey(
            "usuario.id_usr",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    blog_id = Column(
        Integer,
        ForeignKey(
            "blog.id_blog",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    usuario = relationship(
        "Usuario",
        back_populates="comentarios",
    )

    blog = relationship(
        "Blog",
        back_populates="comentarios",
    )

    reacciones = relationship(
        "ComentarioReaccion",
        back_populates="comentario_ref",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


# ============================================================
# REACCIONES DE COMENTARIOS
# ============================================================

class ComentarioReaccion(Base):
    __tablename__ = "comentario_reacciones"
    __table_args__ = (
        UniqueConstraint(
            "comentario_id",
            "usuario_id",
            name="uq_comentario_reaccion_usuario",
        ),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
        },
    )

    id_reaccion = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    comentario_id = Column(
        Integer,
        ForeignKey(
            "comentarios.id_con",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    usuario_id = Column(
        Integer,
        ForeignKey(
            "usuario.id_usr",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    emoji = Column(
        String(30),
        nullable=False,
    )

    fecha = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    comentario_ref = relationship(
        "Comentario",
        back_populates="reacciones",
    )

    usuario = relationship(
        "Usuario",
        back_populates="reacciones_comentarios",
    )


# ============================================================
# LIKE Y DISLIKE DEL BLOG
# ============================================================

class ReaccionBlog(Base):
    __tablename__ = "reacciones_blog"
    __table_args__ = (
        UniqueConstraint(
            "usuario_id",
            "blog_id",
            name="uq_reaccion_blog_usuario",
        ),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
        },
    )

    id_reaccion = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    usuario_id = Column(
        Integer,
        ForeignKey(
            "usuario.id_usr",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    blog_id = Column(
        Integer,
        ForeignKey(
            "blog.id_blog",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    tipo = Column(
        Enum(
            "like",
            "dislike",
            name="tipo_reaccion",
        ),
        nullable=False,
    )

    fecha = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    usuario = relationship(
        "Usuario",
        back_populates="reacciones_blog",
    )

    blog = relationship(
        "Blog",
        back_populates="reacciones",
    )


# ============================================================
# PRODUCTOS
# ============================================================

class Producto(Base):
    __tablename__ = "producto"
    __table_args__ = (
        CheckConstraint(
            "precio > 0",
            name="chk_producto_precio",
        ),
        CheckConstraint(
            "stock >= 0",
            name="chk_producto_stock",
        ),
        CheckConstraint(
            "estatus IN (0, 1)",
            name="chk_producto_estatus",
        ),
        Index(
            "idx_producto_categoria",
            "categoria",
        ),
        Index(
            "ix_producto_estatus",
            "estatus",
        ),
        Index(
            "ix_producto_stock",
            "stock",
        ),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
        },
    )

    id_producto = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    nombre = Column(
        String(150),
        nullable=False,
    )
    descripcion = Column(
        Text,
        nullable=True,
    )
    precio = Column(
        DECIMAL(10, 2),
        nullable=False,
    )
    stock = Column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )
    imagen = Column(
        String(500),
        nullable=True,
    )
    categoria = Column(
        String(100),
        nullable=False,
    )
    estatus = Column(
        Integer,
        nullable=False,
        default=1,
        server_default="1",
    )
    fecha_creacion = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    detalles_carrito = relationship(
        "CarritoDetalle",
        back_populates="producto",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    detalles_pedido = relationship(
        "PedidoDetalle",
        back_populates="producto",
        passive_deletes=True,
    )

    @property
    def disponible(self) -> bool:
        return self.estatus == 1 and self.stock > 0

    @property
    def agotado(self) -> bool:
        return self.stock <= 0

    @property
    def stock_bajo(self) -> bool:
        return 0 < self.stock <= 5


# ============================================================
# CARRITO
# ============================================================

class Carrito(Base):
    __tablename__ = "carrito"
    __table_args__ = (
        UniqueConstraint(
            "usuario_id",
            name="uq_carrito_usuario",
        ),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
        },
    )

    id_carrito = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    usuario_id = Column(
        Integer,
        ForeignKey(
            "usuario.id_usr",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    fecha_creacion = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    usuario = relationship(
        "Usuario",
        back_populates="carritos",
    )

    detalles = relationship(
        "CarritoDetalle",
        back_populates="carrito",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


# ============================================================
# DETALLE DEL CARRITO
# ============================================================

class CarritoDetalle(Base):
    __tablename__ = "carrito_detalle"
    __table_args__ = (
        UniqueConstraint(
            "carrito_id",
            "producto_id",
            name="uq_carrito_producto",
        ),
        CheckConstraint(
            "cantidad > 0",
            name="chk_carrito_cantidad",
        ),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
        },
    )

    id_detalle = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    carrito_id = Column(
        Integer,
        ForeignKey(
            "carrito.id_carrito",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    producto_id = Column(
        Integer,
        ForeignKey(
            "producto.id_producto",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    cantidad = Column(
        Integer,
        nullable=False,
        default=1,
        server_default="1",
    )

    carrito = relationship(
        "Carrito",
        back_populates="detalles",
    )

    producto = relationship(
        "Producto",
        back_populates="detalles_carrito",
    )


# ============================================================
# PEDIDOS
# ============================================================

class Pedido(Base):
    __tablename__ = "pedido"
    __table_args__ = (
        CheckConstraint(
            "total >= 0",
            name="chk_pedido_total",
        ),
        Index(
            "idx_pedido_usuario",
            "usuario_id",
        ),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
        },
    )

    id_pedido = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    usuario_id = Column(
        Integer,
        ForeignKey(
            "usuario.id_usr",
        ),
        nullable=False,
    )

    total = Column(
        DECIMAL(10, 2),
        nullable=False,
        default=0,
        server_default="0.00",
    )

    estado = Column(
        Enum(
            "pendiente",
            "pagado",
            "enviado",
            "entregado",
            "cancelado",
            name="estado_pedido",
        ),
        nullable=False,
        default="pendiente",
        server_default="pendiente",
    )

    fecha = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    usuario = relationship(
        "Usuario",
        back_populates="pedidos",
    )

    detalles = relationship(
        "PedidoDetalle",
        back_populates="pedido",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


# ============================================================
# DETALLE DE PEDIDOS
# ============================================================

class PedidoDetalle(Base):
    __tablename__ = "pedido_detalle"
    __table_args__ = (
        UniqueConstraint(
            "pedido_id",
            "producto_id",
            name="uq_pedido_producto",
        ),
        CheckConstraint(
            "cantidad > 0",
            name="chk_pedido_detalle_cantidad",
        ),
        CheckConstraint(
            "precio_unitario > 0",
            name="chk_pedido_detalle_precio",
        ),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
        },
    )

    id_detalle = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    pedido_id = Column(
        Integer,
        ForeignKey(
            "pedido.id_pedido",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    producto_id = Column(
        Integer,
        ForeignKey(
            "producto.id_producto",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    cantidad = Column(
        Integer,
        nullable=False,
    )

    precio_unitario = Column(
        DECIMAL(10, 2),
        nullable=False,
    )

    pedido = relationship(
        "Pedido",
        back_populates="detalles",
    )

    producto = relationship(
        "Producto",
        back_populates="detalles_pedido",
    )


# ============================================================
# HISTORIAL DE PUNTOS
# ============================================================

class HistorialPuntos(Base):
    __tablename__ = "historial_puntos"
    __table_args__ = (
        Index(
            "ix_historial_usuario_fecha",
            "usuario_id",
            "fecha",
        ),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
        },
    )

    id_historial = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    usuario_id = Column(
        Integer,
        ForeignKey(
            "usuario.id_usr",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    puntos = Column(
        Integer,
        nullable=False,
    )

    accion = Column(
        String(255),
        nullable=False,
    )

    fecha = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    usuario = relationship(
        "Usuario",
        back_populates="historial_puntos",
    )