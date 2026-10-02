import 'package:flutter/material.dart';
import 'login_user_page.dart';

class RecuperarPage extends StatefulWidget {
  const RecuperarPage({super.key});

  @override
  State<RecuperarPage> createState() => _RecuperarPageState();
}

class _RecuperarPageState extends State<RecuperarPage> {
  final TextEditingController correoController = TextEditingController();
  final TextEditingController passwordController = TextEditingController();
  final TextEditingController passwordController1 = TextEditingController();

  bool ocultarPassword = true;

  @override
  void dispose() {
    correoController.dispose();
    passwordController.dispose();
    passwordController1.dispose();
    super.dispose();
  }

  void recuperar() {
    final correo = correoController.text.trim();
    final pass1 = passwordController.text.trim();
    final pass2 = passwordController1.text.trim();

    String? mensaje;

    if (correo.isEmpty || !correo.contains("@") || !correo.contains(".")) {
      mensaje = "Ingresa un correo electrónico válido.";
    }
    else if (pass1.isEmpty || pass2.isEmpty) {
      mensaje = "Completa ambas contraseñas.";
    }
    else if (pass1.length < 6) {
      mensaje = "La contraseña debe tener al menos 6 caracteres.";
    }
    else if (pass1 != pass2) {
      mensaje = "Las contraseñas no coinciden.";
    }

    if (mensaje != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(mensaje)),
      );
      return;
    }

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text("Contraseña actualizada correctamente")),
    );

    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const LoginPage()),
    );
  }

  void cancelar() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const LoginPage()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Recuperar contraseña'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            const Icon(
              Icons.person_add,
              size: 70,
            ),
            const SizedBox(height: 20),
            const Text(
              'RECUPERAR CONTRASEÑA',
              style: TextStyle(
                fontSize: 26,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 15),
            TextField(
              controller: correoController,
              decoration: const InputDecoration(
                labelText: 'Correo electrónico',
                prefixIcon: Icon(Icons.email),
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 15),
            TextField(
              controller: passwordController,
              obscureText: true,
              decoration: const InputDecoration(
                labelText: 'Nueva Contraseña',
                prefixIcon: Icon(Icons.lock),
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 15),
            TextField(
              controller: passwordController1,
              obscureText: true,
              decoration: const InputDecoration(
                labelText: 'Confirmar contraseña',
                prefixIcon: Icon(Icons.lock),
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 15),
            TextButton(
              onPressed: recuperar,
              child: const Text('ACEPTAR'),
            ),
            TextButton(
              onPressed: cancelar,
              child: const Text('CANCELAR'),
            ),
          ],
        ),
      ),
    );
  }
}