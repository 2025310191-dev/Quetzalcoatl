import 'package:flutter/material.dart';
import '../widgets/category_chip.dart';
import '../services/post_services.dart';
import '../widgets/post_card.dart';

class BlogPage extends StatefulWidget {
  const BlogPage({super.key});

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
        title: const Text('Mi Blog'),
        centerTitle: false,
        actions: [
          IconButton(
            onPressed: () {},
            icon: const Icon(Icons.search),
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
              fontStyle: FontStyle.italic,
              color: Color(0xFF08245C),
            ),
          ),
          const SizedBox(height: 5),
          const Text(
            'Descubre nuevas ideas',
            style: TextStyle(
              fontSize: 20,
              color: Color.fromARGB(255, 34, 1, 255),
            ),
          ),
          SizedBox(
            height: 45,
            child: ListView(
              scrollDirection: Axis.horizontal,
              children: [
                CategoryChip(
                  text: 'Todos',
                  icon: Icons.apps,
                  selected: true,
                  onTap: () {},
                ),
                const SizedBox(width: 10),
                CategoryChip(
                  text: 'Flutter',
                  icon: Icons.flutter_dash,
                  selected: false,
                  onTap: () {},
                ),
                const SizedBox(width: 10),
                CategoryChip(
                  text: 'IA',
                  icon: Icons.smart_toy,
                  selected: false,
                  onTap: () {},
                ),
                const SizedBox(width: 10),
                CategoryChip(
                  text: 'Diseño',
                  icon: Icons.brush,
                  selected: false,
                  onTap: () {},
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),
          ...posts.map(
            (post) {
              return PostCard(
                post: post,
                onTap: () {},
              );
            },
          ),
        ],
      ),
    );
  }
}