import 'package:flutter/material.dart';

import '../services/auth_service.dart';
import '../widgets/auth_background.dart';
import '../widgets/auth_card.dart';
import '../widgets/custom_text_field.dart';
import '../widgets/primary_button.dart';

class RegisterPage extends StatefulWidget {
  const RegisterPage({super.key});

  @override
  State<RegisterPage> createState() => _RegisterPageState();
}

class _RegisterPageState extends State<RegisterPage> {
  final TextEditingController nombreController = TextEditingController();
  final TextEditingController correoController = TextEditingController();
  final TextEditingController numeroController = TextEditingController();
  final TextEditingController passwordController = TextEditingController();

  final AuthService authService = AuthService();

  @override
  void dispose() {
    nombreController.dispose();
    correoController.dispose();
    numeroController.dispose();
    passwordController.dispose();
    super.dispose();
  }

  void validarCampos() {
    String nombre = nombreController.text.trim();
    String correo = correoController.text.trim();
    String numero = numeroController.text.trim();

    String mensaje = "";

    if (nombre.isEmpty) {
      mensaje = "El nombre no puede estar vacío.";
    } else if (correo.isEmpty || !correo.contains("@")) {
      mensaje = "Ingresa un correo válido.";
    } else if (numero.isEmpty || int.tryParse(numero) == null) {
      mensaje = "Ingresa un número válido.";
    } else {
      mensaje = "Todo correcto:\nNombre: $nombre\nCorreo: $correo\nNúmero: $numero";
    }

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(mensaje)),
    );
  }

  void limpiarCampos() {
    nombreController.clear();
    correoController.clear();
    numeroController.clear();
    passwordController.clear();
    setState(() {});
  }

  void registrarUsuario() {
    final nombre = nombreController.text.trim();
    final correo = correoController.text.trim();
    final numero = numeroController.text.trim();
    final password = passwordController.text.trim();

    if (numero.isEmpty || int.tryParse(numero) == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Ingresa un número válido")),
      );
      return;
    }

    final respuesta = authService.validarRegistro(
      nombre: nombre,
      correo: correo,
      numero: numero,
      password: password,
      confirmarPassword: password,
    );

    if (respuesta != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(respuesta)),
      );
      return;
    }

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Usuario $nombre registrado')),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: AuthBackground(
        child: Center(
          child: AuthCard(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(
                  Icons.person_add,
                  size: 65,
                  color: Color(0xFF2196F3),
                ),
                const SizedBox(height: 15),
                const Text(
                  'CREAR CUENTA',
                  style: TextStyle(
                    fontSize: 27,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF08245C),
                  ),
                ),
                const SizedBox(height: 25),
                CustomTextField(
                  controller: nombreController,
                  label: 'Nombre completo',
                  prefixIcon: Icons.person,
                ),
                const SizedBox(height: 15),
                CustomTextField(
                  controller: correoController,
                  label: 'Correo electrónico',
                  prefixIcon: Icons.email,
                  keyboardType: TextInputType.emailAddress,
                ),
                const SizedBox(height: 15),
                CustomTextField(
                  controller: numeroController,
                  label: 'Número de teléfono',
                  prefixIcon: Icons.phone,
                  keyboardType: TextInputType.number,
                ),
                const SizedBox(height: 15),
                CustomTextField(
                  controller: passwordController,
                  label: 'Contraseña',
                  prefixIcon: Icons.lock,
                  obscureText: true,
                ),
                const SizedBox(height: 25),
                PrimaryButton(
                  text: 'REGISTRARME',
                  onPressed: registrarUsuario,
                ),
                const SizedBox(height: 15),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    ElevatedButton(
                      onPressed: validarCampos,
                      child: const Text("Validar"),
                    ),
                    ElevatedButton(
                      onPressed: limpiarCampos,
                      style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
                      child: const Text("Limpiar"),
                    ),
                  ],
                ),
                const SizedBox(height: 15),
                TextButton(
                  onPressed: () {
                    Navigator.pop(context);
                  },
                  child: const Text('Ya tengo una cuenta'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}