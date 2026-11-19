# Quetzalcóatl

Quetzalcóatl es una aplicación desarrollada en Flutter para compartir información sobre flora y fauna, participar en la comunidad, consultar ubicaciones en el mapa y utilizar las funciones de tienda, carrito y pedidos.

El proyecto está formado por una aplicación Flutter, una API creada con FastAPI y una base de datos MySQL.

## Requisitos

Antes de instalar el proyecto, necesitas:

- Flutter 3.47.5
- Dart 3.13.4
- Android SDK 36
- Python 3.12.9
- MySQL

## Configurar la base de datos

Crea en MySQL una base de datos llamada:

```sql
CREATE DATABASE flora_fauna_blog;
```

Después, crea un archivo `.env` dentro de la carpeta `backend` con tus datos de conexión:

```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=tu_contraseña
DB_NAME=flora_fauna_blog
```

La API utiliza estos datos para conectarse a MySQL. Las tablas necesarias se crean al iniciar el backend.

## Instalar y ejecutar el backend

Abre una terminal en la carpeta `backend` y crea el entorno virtual:

```powershell
py -m venv .venv
```

Activa el entorno e instala las dependencias:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Inicia la API:

```powershell
python -m uvicorn main:app --reload
```

Puedes comprobar que funciona entrando en `http://127.0.0.1:8000/docs`.

## Instalar y ejecutar la aplicación

Abre otra terminal en la carpeta principal del proyecto y ejecuta:

```powershell
flutter pub get
flutter analyze
flutter test
```

Para abrir la aplicación en Windows usando el backend local:

```powershell
flutter run -d windows --dart-define=API_URL=http://127.0.0.1:8000
```

## Usar la aplicación en un teléfono

El teléfono debe poder conectarse al ordenador donde están funcionando FastAPI y MySQL. Ambos dispositivos deben estar en la misma red.

Consulta la dirección IPv4 del ordenador con:

```powershell
ipconfig
```

Después genera el APK sustituyendo `IP_DEL_ORDENADOR` por esa dirección:

```powershell
flutter build apk --release --dart-define=API_URL=http://IP_DEL_ORDENADOR:8000
```

El APK se guardará en:

```text
build/app/outputs/flutter-apk/app-release.apk
```

Mientras se utilice esta configuración local, MySQL y el backend deben permanecer activos en el ordenador.

## Notas

Credenciales de administrador:

correo: admin@gmail.com
contraseña: 123456789
