import 'package:flutter/material.dart';
import '../services/user_service.dart';

class UsersPage extends StatefulWidget {
  const UsersPage({
    super.key,
  });
  @override
  State<UsersPage> createState() => _UsersPageState();
}

class _UsersPageState extends State<UsersPage> {
  final UserService userService = UserService();
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Gestion de Usuarios',
        ),
      ),
      body: ListView.builder(
        itemCount: userService.obtenerUsuarios().length,
        itemBuilder: (context, index) {
          final usuario = userService.obtenerUsuarios()[index];
          return ListTile(
            leading: const CircleAvatar(
              child: Icon(Icons.person),
            ),
            title: Text(
              usuario.nombre,
            ),
            subtitle: Text(
              usuario.correo,
            ),
          );
        },
      ),
    );
  }
}