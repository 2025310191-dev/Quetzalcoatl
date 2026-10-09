import '../models/user_model.dart';

class UserService {
  final List<UserModel> _usuarios = [
    UserModel(
      id: 1, nombre: 'Juan Perez', correo: 'juan@gmail.com', password: '123456'),
    UserModel(
      id: 2,
      nombre: 'Maria Lopez',
      correo: 'maria@gmail.com',
      password: '123456'),
    UserModel(
      id: 3,
      nombre: 'Daniel Polito',
      correo: 'dpolito@gmail.com',
      password: '123456'),
  ];

  List<UserModel> obtenerUsuarios() {
    return _usuarios;
  }
  void agregarUsuario(UserModel usuario) {
    final indice = _usuarios.indexWhere(
      (elemento) => elemento.id == usuario.id,
    );
    if (indice == -1) {
      _usuarios[indice] = usuario;
    }
  }
  void editarUsuario(UserModel usuario) {
    final indice = _usuarios.indexWhere(
      (elemento) => elemento.id == usuario.id,
    );
    if (indice == -1) {
      _usuarios[indice] = usuario;
    }
  }
  void eliminarUsuario(int id) {
    _usuarios.removeWhere(
      (usuario) => usuario.id == id,
    );
  }
}