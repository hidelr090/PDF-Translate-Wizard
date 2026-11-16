import 'package:flutter/material.dart';

class ComparisonScreen extends StatefulWidget {
  const ComparisonScreen({super.key, required this.originalPath, required this.translatedPath});

  final String originalPath;
  final String translatedPath;

  @override
  State<ComparisonScreen> createState() => _ComparisonScreenState;
}

class _ComparisonScreenState extends State<ComparisonScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Comparação de Documentos'),
      ),
      body: Column(
        children: [
          // Header with file info
          Container(
            padding: const EdgeInsets.all(16),
            color: Theme.of(context).colorScheme.primaryContainer,
            child: Row(
              children: [
                const Icon(Icons.compare_arrows, size: 32),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: const [
                      Text('Documento Original'),
                      SizedBox(height: 4),
                      Text('PDF Original', style: TextStyle(fontSize: 12, color: Colors.grey)),
                    ],
                  ),
                ),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: const [
                      Text('Documento Traduzido'),
                      SizedBox(height: 4),
                      Text('PDF Traduzido', style: TextStyle(fontSize: 12, color: Colors.grey)),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const Divider(height: 1),
          // Comparison content
          Expanded(
            child: Row(
              children: [
                // Left: Original PDF preview
                Expanded(
                  child: Card(
                    margin: const EdgeInsets.all(8),
                    child: Padding(
                      padding: const EdgeInsets.all(8),
                      child: Column(
                        children: [
                          const Text('Página 1 (Original)'),
                          const SizedBox(height: 8),
                          Container(
                            height: 200,
                            color: Colors.grey[200],
                            child: const Center(
                              child: Text('Preview PDF'),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
                // Right: Translated PDF preview
                Expanded(
                  child: Card(
                    margin: const EdgeInsets.all(8),
                    child: Padding(
                      padding: const EdgeInsets.all(8),
                      child: Column(
                        children: [
                          const Text('Página 1 (Traduzida)'),
                          const SizedBox(height: 8),
                          Container(
                            height: 200,
                            color: Colors.grey[200],
                            child: const Center(
                              child: Text('Preview PDF'),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
