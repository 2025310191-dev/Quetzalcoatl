import 'package:flutter/material.dart';
import '../widgets/category_chip.dart';
import '../models/post_model.dart';
import '../services/post_services.dart';
import '../widgets/post_card.dart';

class BlogPage extends StatefulWidget {
  const BlogPage({
    super.key,
  });

  @override
  State<BlogPage> createState() => _BlogPageState();
}

class _BlogPageState extends State<BlogPage> {
  final PostService postService = PostService();

  @override
  Widget build(BuildContext context) {
    final posts = postService.getPosts();

    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Mi Blog',
        ),
        centerTitle: false,
        actions: [
          IconButton(
            onPressed: () {},
            icon: const Icon(
              Icons.search,
            ),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text(
            'Bienvenido',
            style: TextStyle(
              fontSize: 28,
              fontWeight: FontWeight.bold,
              color: Color(0xFF08245C),
            ),
          ),
          const SizedBox(
            height: 5,
          ),
          const Text(
            'Descubre nuevas ideas',
            style: TextStyle(
              fontSize: 16,
              color: Colors.grey,
            ),
          ),
          SizedBox(
            height: 45,
            child: ListView(
              scrollDirection: Axis.horizontal,
              children: [
                CategoryChip(
                  text: 'Todos',
                  selected: true,
                  onTap: () {},
                ),
                const SizedBox(
                  width: 10,
                ),
                CategoryChip(
                  text: 'Flutter',
                  selected: false,
                  onTap: () {},
                ),
                const SizedBox(
                  width: 10,
                ),
                CategoryChip(
                  text: 'IA',
                  selected: false,
                  onTap: () {},
                ),
                const SizedBox(
                  width: 10,
                ),
                CategoryChip(
                  text: 'Diseño',
                  selected: false,
                  onTap: () {},
                ),
              ],
            ),
          ),
          const SizedBox(
            height: 20,
          ),
          ...posts.map(
            (post) {
              return PostCard(
                post: post,
                onTap: () {
                  print(
                    'Seleccionaste: ${post.titulo}',
                  );
                },
              );
            },
          ),
        ],
      ),
    );
  }
}