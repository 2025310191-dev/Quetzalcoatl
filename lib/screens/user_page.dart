import 'package:flutter/material.dart';
import '../services/user_service.dart';
import '../models/user_model.dart';

class UsersPage extends StatefulWidget {
  const UsersPage({super.key});

  @override
  State<UsersPage> createState() => _UsersPageState();
}

class _UsersPageState extends State<UsersPage> {
  final UserService userService = UserService();
  final TextEditingController nombreController = TextEditingController();
  final TextEditingController correoController = TextEditingController();
  final TextEditingController passwordController = TextEditingController();

  void mostrarFormulario() {
    nombreController.clear();
    correoController.clear();
    passwordController.clear();

    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('Nuevo usuario'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: nombreController,
                decoration: const InputDecoration(labelText: 'Nombre'),
              ),
              TextField(
                controller: correoController,
                decoration: const InputDecoration(labelText: 'Correo'),
              ),
              TextField(
                controller: passwordController,
                obscureText: true,
                decoration: const InputDecoration(labelText: 'Contraseña'),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancelar'),
            ),
            ElevatedButton(
              onPressed: () {
                crearUsuario();
                Navigator.pop(context);
              },
              child: const Text('Guardar'),
            ),
          ],
        );
      },
    );
  }

  void mostrarFormularioEditar(UserModel usuario) {
    nombreController.text = usuario.nombre;
    correoController.text = usuario.correo;
    passwordController.text = usuario.password;

    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('Editar usuario'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: nombreController,
                decoration: const InputDecoration(labelText: 'Nombre'),
              ),
              TextField(
                controller: correoController,
                decoration: const InputDecoration(labelText: 'Correo'),
              ),
              TextField(
                controller: passwordController,
                obscureText: true,
                decoration: const InputDecoration(labelText: 'Contraseña'),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancelar'),
            ),
            ElevatedButton(
              onPressed: () {
                usuario.nombre = nombreController.text;
                usuario.correo = correoController.text;
                usuario.password = passwordController.text;
                setState(() {});
                Navigator.pop(context);
              },
              child: const Text('Guardar cambios'),
            ),
          ],
        );
      },
    );
  }

  void crearUsuario() {
    final nuevoUsuario = UserModel(
      id: DateTime.now().millisecondsSinceEpoch,
      nombre: nombreController.text,
      correo: correoController.text,
      password: passwordController.text,
    );

    userService.agregarUsuario(nuevoUsuario);
    setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      floatingActionButton: FloatingActionButton(
        onPressed: () => mostrarFormulario(),
        child: const Icon(Icons.add),
      ),
      appBar: AppBar(
        title: const Text('Gestion de Usuarios'),
      ),
      body: ListView.builder(
        itemCount: userService.obtenerUsuarios().length,
        itemBuilder: (context, index) {
          final usuario = userService.obtenerUsuarios()[index];
          return ListTile(
            leading: const CircleAvatar(child: Icon(Icons.person)),
            title: Text(usuario.nombre),
            subtitle: Text(usuario.correo),
            trailing: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                IconButton(
                  icon: const Icon(Icons.edit),
                  onPressed: () {
                    mostrarFormularioEditar(usuario);
                  },
                ),
                IconButton(
                  icon: const Icon(Icons.delete),
                  onPressed: () {
                    userService.eliminarUsuario(index);
                    setState(() {});
                  },
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}