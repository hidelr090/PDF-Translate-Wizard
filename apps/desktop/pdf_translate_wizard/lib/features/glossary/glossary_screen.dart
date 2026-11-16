import 'package:flutter/material.dart';

class GlossaryScreen extends StatefulWidget {
  const GlossaryScreen({super.key});

  @override
  State<GlossaryScreen> createState() => _GlossaryScreenState();
}

class _GlossaryScreenState extends State<GlossaryScreen> {
  final _termController = TextEditingController();
  final _translationController = TextEditingController();
  _glossaryTerms = [];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Glossário de Termos'),
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              itemCount: _glossaryTerms.length,
              itemBuilder: (context, index) {
                final term = _glossaryTerms[index];
                return ListTile(
                  title: Text(term['original']),
                  subtitle: Text(term['translated']),
                  trailing: IconButton(
                    icon: const Icon(Icons.delete),
                    onPressed: () {
                      setState(() {
                        _glossaryTerms.removeAt(index);
                      });
                    },
                  ),
                );
              },
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _termController,
                    decoration: const InputDecoration(
                      labelText: 'Termo Original',
                      border: OutlineInputBorder(),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: TextField(
                    controller: _translationController,
                    decoration: const InputDecoration(
                      labelText: 'Tradução',
                      border: OutlineInputBorder(),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                ElevatedButton.icon(
                  onPressed: () {
                    if (_termController.text.isNotEmpty && _translationController.text.isNotEmpty) {
                      setState(() {
                        _glossaryTerms.add({
                          'original': _termController.text,
                          'translated': _translationController.text,
                        });
                        _termController.clear();
                        _translationController.clear();
                      });
                    }
                  },
                  icon: const Icon(Icons.add),
                  label: const Text('Adicionar'),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
