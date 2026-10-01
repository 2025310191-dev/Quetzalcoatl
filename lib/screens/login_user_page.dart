import 'package:flutter/material.dart';
import '../services/auth_service.dart';
import '../widgets/auth_background.dart';
import '../widgets/auth_card.dart';
import '../widgets/custom_text_field.dart';
import '../widgets/primary_button.dart';

class LoginPage extends StatefulWidget {

  const LoginPage({
    super.key,
  });

  @override
  State<LoginPage> createState() =>
      _LoginPageState();
}

class _LoginPageState
    extends State<LoginPage> {

  final TextEditingController usuarioController =
      TextEditingController();

  final TextEditingController passwordController =
      TextEditingController();

  final AuthService authService =
      AuthService();

  bool ocultarPassword = true;

  @override
  void dispose() {
    usuarioController.dispose();
    passwordController.dispose();

    super.dispose();
  }

  void iniciarSesion() {

    final mensaje =
        authService.validarLogin(
      usuario:
          usuarioController.text.trim(),

      password:
          passwordController.text,
    );

    if (mensaje != null) {

      ScaffoldMessenger.of(context)
          .showSnackBar(
        SnackBar(
          content: Text(mensaje),
        ),
      );

      return;
    }

    ScaffoldMessenger.of(context)
        .showSnackBar(
      SnackBar(
        content: Text(
          'Bienvenido ${usuarioController.text}',
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {

    return Scaffold(

      body: AuthBackground(

        child: Center(

          child: AuthCard(

            child: Column(

              mainAxisSize:
                  MainAxisSize.min,

              children: [
                const Icon(
                  Icons.lock_outline,
                  size: 65,
                  color:
                      Color.fromARGB(255, 112, 6, 241),
                ),

                const SizedBox(
                  height: 15,
                ),

                const Text(
                  'INICIAR SESIÓN',

                  style: TextStyle(
                    fontSize: 27,
                    fontWeight: 
                        FontWeight.w700,
                    fontStyle: 
                        FontStyle.italic,
                    color:
                    Color.fromARGB(255, 112, 6, 241),
                  ),
                ),

                const SizedBox(
                  height: 25,
                ),

                CustomTextField(
                  controller:
                      usuarioController,

                  label: 'Usuario',

                  prefixIcon:
                      Icons.person,
                ),

                const SizedBox(
                  height: 15,
                ),

                CustomTextField(
                  controller:
                      passwordController,

                  label: 'Contraseña',

                  prefixIcon:
                      Icons.lock_outline,

                  obscureText:
                      ocultarPassword,

                  suffixIcon:
                      IconButton(

                    icon: Icon(
                      ocultarPassword
                          ? Icons
                              .visibility_off_outlined
                          : Icons
                              .visibility_outlined,
                    ),

                    onPressed: () {

                      setState(() {

                        ocultarPassword =
                            !ocultarPassword;

                      });
                    },
                  ),
                ),

                Align(

                  alignment:
                      Alignment.centerRight,

                  child: TextButton(

                    onPressed: () {
                        Navigator.pushNamed(
                          context,
                          '/recuperar',
                        );
                    },

                    child: const Text(
                      '¿Olvidaste tu contraseña?',
                    ),
                  ),
                ),

                const SizedBox(
                  height: 5,
                ),

                PrimaryButton(
                  text: 'INGRESAR',
                  onPressed:
                      iniciarSesion,
                ),

                const SizedBox(
                  height: 15,
                ),

                Row(

                  mainAxisAlignment:
                      MainAxisAlignment.center,

                  children: [

                    const Text(
                      '¿No tienes cuenta?',
                    ),

                    TextButton(

                      onPressed: () {

                        Navigator.pushNamed(
                          context,
                          '/register',
                        );
                      },

                      child: const Text(
                        'Registrarse',
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}