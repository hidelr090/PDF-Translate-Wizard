import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:pdf_translate_wizard/core/router/go_router.dart';

class FileSelectionScreen extends StatefulWidget {
  const FileSelectionScreen({super.key});

  @override
  State<FileSelectionScreen> createState() => _FileSelectionScreenState();
}

class _FileSelectionScreenState extends State<FileSelectionScreen> {
  String? _selectedFilePath;
  bool _isLoading = false;

  Future<void> _pickFile() async {
    setState(() => _isLoading = true);
    try {
      final result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['pdf'],
      );
      if (result != null && result.files.single.path != null) {
        setState(() => _selectedFilePath = result.files.single.path!);
        // TODO: Send file path to Python service via JSON-RPC
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Arquivo selecionado: ${_selectedFilePath}')),
        );
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Seleção de Arquivo'),
      ),
      body: Center(
        child: _isLoading
            ? const CircularProgressIndicator()
            : _selectedFilePath == null
                ? const Text('Nenhum arquivo selecionado')
                : Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        'Arquivo: $_selectedFilePath',
                        style: const TextStyle(fontSize: 16),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 16),
                      ElevatedButton(
                        onPressed: _pickFile,
                        child: const Text('Selecionar PDF'),
                      ),
                    ],
                  ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _pickFile,
        tooltip: 'Selecionar PDF',
        child: const Icon(Icons.insert_drive_file),
      ),
    );
  }
}
