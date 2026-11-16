import 'package:flutter/material.dart';

class VisualFidelityScreen extends StatefulWidget {
  const VisualFidelityScreen({super.key});

  @override
  State<VisualFidelityScreen> createState() => _VisualFidelityScreenState;
}

class _VisualFidelityScreenState extends State<VisualFidelityScreen> {
  double _fidelityLevel = 0.9;
  bool _preserveImages = true;
  bool _preserveFonts = true;
  bool _preserveColors = true;
  bool _preserveDimensions = true;
  bool _respectPageBreaks = true;
  bool _optimizeColumns = true;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Fidelidade Visual'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Nível de Fidelidade:',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            Slider(
              value: _fidelityLevel,
              min: 0.5,
              max: 1.0,
              divisions: 10,
              label: '${_fidelityLevel.toStringAsFixed(1)}',
              onChanged: (value) => setState(() => _fidelityLevel = value),
            ),
            Text(
              'Score: ${_fidelityLevel.toStringAsFixed(2)}',
              style: const TextStyle(fontSize: 14),
            ),
            const SizedBox(height: 24),
            const Text(
              'Opções de Preservação:',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            CheckboxListTile(
              title: const Text('Preservar Imagens'),
              value: _preserveImages,
              onChanged: (value) => setState(() => _preserveImages = value),
            ),
            CheckboxListTile(
              title: const Text('Preservar Fontes'),
              value: _preserveFonts,
              onChanged: (value) => setState(() => _preserveFonts = value),
            ),
            CheckboxListTile(
              title: const Text('Preservar Cores'),
              value: _preserveColors,
              onChanged: (value) => setState(() => _preserveColors = value),
            ),
            CheckboxListTile(
              title: const Text('Preservar Dimensões de Página'),
              value: _preserveDimensions,
              onChanged: (value) => setState(() => _preserveDimensions = value),
            ),
            CheckboxListTile(
              title: const Text('Respeitar Quebras de Página'),
              value: _respectPageBreaks,
              onChanged: (value) => setState(() => _respectPageBreaks = value),
            ),
            CheckboxListTile(
              title: const Text('Otimizar Colunas'),
              value: _optimizeColumns,
              onChanged: (value) => setState(() => _optimizeColumns = value),
            ),
            const Spacer(),
            ElevatedButton.onPressed(
              onPressed: () {
                // Aplicar configurações
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(text: 'Configurações de fidelidade salvas'),
                );
              },
              child: const Text('Aplicar'),
            ),
          ],
        ),
      ),
    );
  }
}
