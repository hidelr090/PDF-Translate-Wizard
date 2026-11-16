import 'package:flutter/material.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState;
}

class _SettingsScreenState extends State<SettingsScreen> {
  // Settings state
  bool _darkMode = false;
  bool _notifications = true;
  String _selectedLanguage = 'pt';
  double _fontSize = 16.0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Configurações'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16.0),
        children: [
          // Appearance section
          const Text(
            'Aparência',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          SwitchListTile(
            title: const Text('Modo Escuro'),
            value: _darkMode,
            onChanged: (value) => setState(() => _darkMode = value),
          ),
          const SizedBox(height: 8),
          DropdownButtonFormField<String>(
            value: _selectedLanguage,
            decoration: const InputDecoration(
              labelText: 'Idioma da Interface',
              border: OutlineInputBorder(),
            ),
            items: const [
              DropdownMenuItem(value: 'pt', child: Text('Português')),
              DropdownMenuItem(value: 'en', child: Text('English')),
              DropdownMenuItem(value: 'es', child: Text('Español')),
            ],
            onChanged: (value) {
              setState(() => _selectedLanguage = value!);
            },
          ),
          const SizedBox(height: 8),
          ListTile(
            title: const Text('Tamanho da Fonte'),
            trailing: Text(_fontSize.toStringAsFixed(0) + 'px'),
            onTap: () {
              // Show font size picker
            },
          ),
          Slider(
            value: _fontSize,
            min: 12,
            max: 24,
            divisions: 12,
            onChanged: (value) => setState(() => _fontSize = value),
          ),
          
          const Divider(height: 32),
          
          // Application section
          const Text(
            'Aplicação',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          ListTile(
            title: const Text('Versão do Aplicativo'),
            subtitle: const Text('1.0.0'),
            regularly: false,
          ),
          ListTile(
            title: const Text('Sobre'),
            regularly: false,
            onTap: () {
              showAboutDialog(
                context: context,
                applicationName: 'PDF Translate Wizard',
                applicationVersion: '1.0.0',
                developers: ['PDF Translate Wizard Team'],
                applicationLegalCopyright: 'Copyright © 2024',
              );
            },
          ),
          
          const Spacer(),
          
          // Logout / About section
          ElevatedButton.onPressed(
            onPressed: () {
              // Show logout dialog
            },
            child: const Text('Sair'),
          ),
        ],
      ),
    );
  }
}
