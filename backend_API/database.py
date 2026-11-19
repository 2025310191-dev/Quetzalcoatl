import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, sessionmaker

ENV_PATH = Path(__file__).resolve().parent / ".env"

load_dotenv(
    dotenv_path=ENV_PATH,
    override=True,
)

DB_HOST = os.getenv(
    "DB_HOST",
    "127.0.0.1",
)

DB_PORT = int(
    os.getenv(
        "DB_PORT",
        "3306",
    )
)

DB_USER = os.getenv(
    "DB_USER",
    "root",
)

DB_PASSWORD = os.getenv(
    "DB_PASSWORD",
    "",
)

DB_NAME = os.getenv(
    "DB_NAME",
    "flora_fauna_blog",
)

url = URL.create(
    drivername="mysql+pymysql",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    query={
        "charset": "utf8mb4",
    },
)

engine = create_engine(
    url,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


def obtener_sesion():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def comprobar_conexion() -> None:
    print(
        f"Archivo .env cargado: {ENV_PATH}"
    )

    print(
        f"Base configurada: {DB_NAME}"
    )

    with engine.connect() as conexion:
        base_actual = conexion.execute(
            text("SELECT DATABASE()")
        ).scalar_one()

        print(
            "Base conectada por SQLAlchemy: "
            f"{base_actual}"
        )

        if base_actual != DB_NAME:
            raise RuntimeError(
                "La base conectada no coincide con "
                "la base configurada. "
                f"Configurada: {DB_NAME}. "
                f"Conectada: {base_actual}."
            )