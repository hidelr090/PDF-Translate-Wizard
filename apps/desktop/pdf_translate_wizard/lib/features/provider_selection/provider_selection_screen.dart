import 'package:flutter/material.dart';
import 'package:pdf_translate_wizard/core/router/go_router.dart';

class ProviderSelectionScreen extends StatefulWidget {
  const ProviderSelectionScreen({super.key});

  @override
  State<ProviderSelectionScreen> createState() => _ProviderSelectionScreenState();
}

class _ProviderSelectionScreenState extends State<ProviderSelectionScreen> {
  String _selectedProvider = 'ollama';
  String _selectedModel = 'llama3.2';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Seleção de Provedor de IA'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Escolha o provedor de IA:',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            _buildProviderTile(
              context,
              'Ollama (Local)',
              'Executando modelos localmente no seu dispositivo',
              Icons.local_library,
              _selectedProvider == 'ollama',
              () => setState(() => _selectedProvider = 'ollama'),
            ),
            _buildProviderTile(
              context,
              'OpenAI',
              'Modelos GPT-4 via API',
              Icons.cloud,
              _selectedProvider == 'openai',
              () => setState(() => _selectedProvider = 'openai'),
            ),
            _buildProviderTile(
              context,
              'Anthropic',
              'Modelos Claude via API',
              Icons.psychology,
              _selectedProvider == 'anthropic',
              () => setState(() => _selectedProvider = 'anthropic'),
            ),
            const SizedBox(height: 24),
            const Text(
              'Escolha o modelo:',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            DropdownButtonFormField<String>(
              value: _selectedModel,
              decoration: const InputDecoration(
                labelText: 'Modelo',
                border: OutlineInputBorder(),
              ),
              items: const [
                DropdownMenuItem(value: 'llama3.2', child: Text('Llama 3.2 (local)')),
                DropdownMenuItem(value: 'gpt-4o-mini', child: Text('GPT-4o-mini (OpenAI)')),
                DropdownMenuItem(value: 'claude-3-haiku-20240307', child: Text('Claude 3 Haiku (Anthropic)')),
              ],
              onChanged: (value) {
                setState(() => _selectedModel = value!);
              },
            ),
            const Spacer(),
            ElevatedButton.onPressed(
              onPressed: () {
                // Salvar seleção e navegar
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('Provedor: $_selectedProvider, Modelo: $_selectedModel')),
                );
                // Navigator.of(context).pushNamed('/translation');
              },
              child: const Text('Iniciar Tradução'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildProviderTile(
    BuildContext context,
    String title,
    String subtitle,
    IconData icon,
    bool isSelected,
    VoidCallback onTap,
  ) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Container(
        margin: const EdgeInsets.only(bottom: 8),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: isSelected ? Theme.of(context).colorScheme.primaryContainer : Colors.transparent,
          border: Border.all(
            color: isSelected ? Theme.of(context).colorScheme.primary : Colors.grey.shade300,
            width: 2,
          ),
          borderRadius: BorderRadius.circular(8),
        ),
        row(
          children: [
            Icon(icon, color: isSelected ? Colors.white : Colors.grey),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children [
                  Text(
                    title,
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                      color: isSelected ? Colors.white : Colors.black,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    subtitle,
                    style: const TextStyle(fontSize: 12, color: Colors.grey),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
            const Icon(Icons.check, color: Colors.blue, size: 20),
          ],
        ),
      ),
    );
  }
}
