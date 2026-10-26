import 'package:flutter/material.dart';
import '../models/post_model.dart';
class PostDetailPage extends StatelessWidget {
  final PostModel post;
  const PostDetailPage({
    super.key,
    required this.post,
  });
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title:
            const Text('Detalle'),
      ),

      body: SingleChildScrollView(

        child: Column(

          crossAxisAlignment:
              CrossAxisAlignment.start,

          children: [

            Image.network(

              post.imagen,

              height: 230,

              width:
                  double.infinity,

              fit: BoxFit.cover,
            ),

            Padding(

              padding:
                  const EdgeInsets.all(20),

              child: Column(

                crossAxisAlignment:
                    CrossAxisAlignment.start,

                children: [

                  Text(
                    post.categoria,

                    style:
                        const TextStyle(
                      color:
                          Color(0xFF2196F3),

                      fontWeight:
                          FontWeight.bold,
                    ),
                  ),

                  const SizedBox(
                    height: 10,
                  ),

                  Text(
                    post.titulo,

                    style:
                        const TextStyle(
                      fontSize: 28,

                      fontWeight:
                          FontWeight.bold,

                      color:
                          Color(0xFF08245C),
                    ),
                  ),

                  const SizedBox(
                    height: 15,
                  ),

                  Row(
                    children: [

                      Text(
                        post.autor,
                      ),

                      const SizedBox(
                        width: 10,
                      ),

                      Text(
                        '• ${post.fecha}',
                      ),
                    ],
                  ),

                  const SizedBox(
                    height: 25,
                  ),

                  Text(
                    post.contenido,

                    style:
                        const TextStyle(
                      fontSize: 17,

                      height: 1.6,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}