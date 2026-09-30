import 'package:flutter/material.dart';
import 'screens/login_user_page.dart';

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
      home: const LoginPage(),
    );
  }
}