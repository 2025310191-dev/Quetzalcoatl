class AuthService{
  String? validarLogin({
    required String usuario,
    required String password,
  }){
    if (usuario.isEmpty || password.isEmpty){
      return 'Completa usuario y contraseña';
    }
    return null;
  }
  String? validarRegistro({
    required String nombre,
    required String correo,
    required String password,
    required String confirmarPassword,
  }){
    if (nombre.isEmpty || correo.isEmpty || password.isEmpty || confirmarPassword.isEmpty){
      return 'Completa todos los campos';
    }
    if (!correo.contains('@')){
      return 'Ingresa un correo valido';
    }
    if (password.length < 6){
      return 'La contraseña debe tener almenos 6 caracteres';
    }
    if (password != confirmarPassword){
      return 'Las contraseñas no coinciden';
    }
    return null;
  }
}