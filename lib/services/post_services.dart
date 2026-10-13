import '../models/post_model.dart';

class PostService {

  final List<PostModel> _posts = [

    PostModel(

      id: 1,
      titulo: 'Construyendo aplicaciones en flutter',
      autor: 'Adriana',
      categoria: 'Flutter',
      descripcion: 'iuhiuehiuerh',
      contenido:  'uihiuduuiwuien',
      imagen: 'https://picsum.photos/800/400?random=1&#39',
      fecha: '01 Oct 2026',

    ),

    PostModel(

      id: 2,
      titulo: 'Introduccion a la inteligencia artificial',
      autor: 'Adriana',
      categoria: 'IA',
      descripcion: 'Conceptos fundamentales de inteligencia artificial',
      contenido: 'La inteligencia artificial permite desarrollar sistemas capaces de realizar tareas que requieren razonamiento',
      imagen: 'https://picsum.photos/800/400?random=2&#39',
      fecha: '03 Oct 2026',

    ),

    PostModel(

      id: 3,
      titulo: 'Diseño de interfaces moviles',
      autor: 'Adriana',
      categoria: 'Diseño',
      descripcion: 'Principios para construir interfaces faciles de utilizar',
      contenido: 'Una buena interfaz debe considerar organizacion, jerarquia visual, accesibilidad',
      imagen: 'https://picsum.photos/800/400?random=3&#39',
      fecha: '05 Oct 2026',

    ),

  ];

  List<PostModel> getPosts() {
    return _posts;
  }

}