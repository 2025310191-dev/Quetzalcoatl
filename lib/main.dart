import 'package:flutter/material.dart';
import 'screens/login_user_page.dart';
import 'screens/register_user_page.dart';
import 'screens/olvide_contra_user_page.dart';
import 'screens/user_page.dart';

void main(){
  runApp(const LoginApp());
}

class LoginApp extends StatelessWidget {
  const LoginApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Mi aplicacion',
      initialRoute: '/login',
      routes: {
        '/login': (context) => const LoginPage(),
        '/register': (context) => const RegisterPage(),
        '/recuperar': (context) => const RecuperarPage(),
        '/userspage': (context) => const UsersPage(),
      },
    );
  }
}