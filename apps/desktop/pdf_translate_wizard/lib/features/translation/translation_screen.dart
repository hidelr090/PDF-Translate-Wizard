import 'package:flutter/material.dart';
import 'package:pdf_translate_wizard/core/router/go_router.dart';

class TranslationScreen extends StatefulWidget {
  const TranslationScreen({super.key});

  @override
  State<TranslationScreen> createState() => _TranslationScreenState();
}

class _TranslationScreenState extends State<TranslationScreen> {
  // State for translation process
  String _selectedFile = 'Nenhum arquivo selecionado';
  String _targetLanguage = 'en';
  String _sourceLanguage = 'pt';
  String _selectedProvider = 'ollama';
  String _selectedModel = 'llama3.2';
  double _progress = 0.0;
  String _status = 'Pronto';
  bool _isTranslating = false;

  // Glossary state
  final _glossaryTerms = [];

  // File picker
  Future<void> _pickFile() async {
    // TODO: Implement file picker integration with Python service
    // final result = await FilePicker.platform.pickFiles(type: FileType.custom, allowedExtensions: ['pdf']);
    // if (result != null && result.files.single.path != null) {
    //   setState(() => _selectedFile = result.files.single.path!);
    // }
  }

  // Start translation
  void _startTranslation() {
    if (_selectedFile == 'Nenhum arquivo selecionado') {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Selecione um arquivo PDF primeiro')),
      );
      return;
    }
    
    setState(() {
      _isTranslating = true;
      _status = 'Em tradução...';
      _progress = 0.0;
    });
    
    // TODO: Implement translation logic with Python service JSON-RPC
    // Simulate translation progress
    // _simulateTranslationProgress();
  }
  
  // void _simulateTranslationProgress() {
  //   // Simulate progress updates
  //   for (int i = 0; i <= 10; i++) {
  //     Future.delayed(const Duration(seconds: 1), () {
  //       if (_isTranslating) {
  //         setState(() {
  //           _progress = i / 10.0;
  //           if (_progress >= 1.0) {
  //             _status = 'Concluído';
  //             _isTranslating = false;
  //           }
  //         });
  //       }
  //     });
  //   }
  // }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Nova Tradução'),
        actions: [
          IconButton(
            icon: const Icon(Icons.save),
            onPressed: () {},
            tooltip: 'Salvar projeto',
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // File selection card
            Card(
              child: Padding(
                padding: const EdgeInsets.all(12.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Arquivo PDF:',
                      style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      _selectedFile,
                      style: const TextStyle(fontFamily: 'monospace'),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 8),
                    ElevatedButton.icon(
                      onPressed: _pickFile,
                      icon: const Icon(Icons.insert_drive_file),
                      label: const Text('Selecionar PDF'),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),
            
            // Language selection
            const Text(
              'Configurações de Idioma:',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: DropdownButtonFormField<String>(
                    value: _sourceLanguage,
                    decoration: const InputDecoration(
                      labelText: 'Idioma de Origem',
                      border: OutlineInputBorder(),
                    ),
                    items: const [
                      DropdownMenuItem(value: 'pt', child: Text('Português')),
                      DropdownMenuItem(value: 'en', child: Text('English')),
                      DropdownMenuItem(value: 'es', child: Text('Español')),
                    ],
                    onChanged: (value) {
                      setState(() => _sourceLanguage = value!);
                    },
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: DropdownButtonFormField<String>(
                    value: _targetLanguage,
                    decoration: const InputDecoration(
                      labelText: 'Idioma de Destino',
                      border: OutlineInputBorder(),
                    ),
                    items: const [
                      DropdownMenuItem(value: 'en', child: Text('English')),
                      DropdownMenuItem(value: 'es', child: Text('Español')),
                      DropdownMenuItem(value: 'fr', child: Text('Français')),
                    ],
                    onChanged: (value) {
                      setState(() => _targetLanguage = value!);
                    },
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),
            
            // Provider and model selection
            const Text(
              'Provedor e Modelo:',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            DropdownButtonFormField<String>(
              value: _selectedProvider,
              decoration: const InputDecoration(
                labelText: 'Provedor',
                border: OutlineInputBorder(),
              ),
              items: const [
                DropdownMenuItem(value: 'ollama', child: Text('Ollama (Local)')),
                DropdownMenuItem(value: 'openai', child: Text('OpenAI')),
                DropdownMenuItem(value: 'anthropic', child: Text('Anthropic')),
              ],
              onChanged: (value) {
                setState(() => _selectedProvider = value!);
              },
            ),
            const SizedBox(height: 4),
            DropdownButtonFormField<String>(
              value: _selectedModel,
              decoration: const InputDecoration(
                labelText: 'Modelo',
                border: OutlineInputBorder(),
              ),
              items: const [
                DropdownMenuItem(value: 'llama3.2', child: Text('Llama 3.2')),
                DropdownMenuItem(value: 'gpt-4o-mini', child: Text('GPT-4o-mini')),
                DropdownMenuItem(value: 'claude-3-haiku', child: Text('Claude 3 Haiku')),
              ],
              onChanged: (value) {
                setState(() => _selectedModel = value!);
              },
            ),
            const SizedBox(height: 24),
            
            // Glossary
            ElevatedButton.icon(
              onPressed: () {
                // Navigator.push(context, MaterialPageRoute(builder: (_) => const GlossaryScreen()));
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Abrir glossário')),
                );
              },
              icon: const Icon(Icons.edit),
              label: const Text('Gerenciar Glossário'),
            ),
            const Text(
              'Termos especiais serão preservados durante a tradução.',
              style: TextStyle(fontSize: 12, color: Colors.grey),
            ),
            const SizedBox(height: 24),
            
            // Fidelity settings
            const Text(
              'Fidelidade Visual:',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Slider(
              value: 0.9,
              min: 0.5,
              max: 1.0,
              divisions: 10,
              label: '0.90',
              onChanged: (_) {},
            ),
            Text(
              'Score: 0.90 - Maior fidelidade = mais preservação de layout, mas pode reduzir qualidade da tradução',
              style: const TextStyle(fontSize: 12, color: Colors.grey),
            ),
            const SizedBox(height: 24),
            
            // Progress and status
            if (_isTranslating) ... [
              LinearProgressIndicator(value: _progress),
              const SizedBox(height: 8),
              Text(
                _status,
                style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold),
              ),
            ] else ... [
              ElevatedButton.icon(
                onPressed: _startTranslation,
                icon: const Icon(Icons.play_arrow),
                label: const Text('Iniciar Tradução'),
              ),
              const SizedBox(height: 8),
              ElevatedButton.icon(
                onPressed: () {},
                icon: const Icon(Icons.info_outline),
                label: const Text('Como funciona'),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
