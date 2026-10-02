class AuthService {
  final RegExp emailRegExp =
      RegExp(r'^[\w\.-]+@[\w\.-]+\.\w+$');

  String? validarLogin({
    required String usuario,
    required String password,
  }) {
    if (usuario.isEmpty || password.isEmpty) {
      return 'Completa usuario y contraseña';
    }

    if (password.length < 6) {
      return 'La contraseña debe tener al menos 6 caracteres';
    }

    return null;
  }

  String? validarRegistro({
    required String nombre,
    required String correo,
    required String numero,
    required String password,
    required String confirmarPassword,
  }) {
    if (nombre.isEmpty ||
        correo.isEmpty ||
        numero.isEmpty ||
        password.isEmpty ||
        confirmarPassword.isEmpty) {
      return 'Completa todos los campos';
    }

    if (!emailRegExp.hasMatch(correo)) {
      return 'Ingresa un correo válido';
    }

    if (int.tryParse(numero) == null) {
      return 'Ingresa un número válido';
    }

    if (password.length < 6) {
      return 'La contraseña debe tener al menos 6 caracteres';
    }

    if (password != confirmarPassword) {
      return 'Las contraseñas no coinciden';
    }

    return null;
  }
}