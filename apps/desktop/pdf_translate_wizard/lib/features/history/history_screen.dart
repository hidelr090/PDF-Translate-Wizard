import 'package:flutter/material.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState;
}

class _HistoryScreenState extends State<HistoryScreen> {
  // Simulated history data
  final _historyItems = [
    {
      'date': 'Hoje, 14:30',
      'file': 'documento1.pdf',
      'targetLanguage': 'Inglês',
      'status': 'Concluído',
      'progress': 1.0,
    },
    {
      'date': '13/11/2024, 10:15',
      'file': 'relatorio.pdf',
      'targetLanguage': 'Espanhol',
      'status': 'Concluído',
      'progress': 1.0,
    },
    {
      'date': '12/11/2024, 16:45',
      'file': 'apresentacao.pdf',
      'targetLanguage': 'Francês',
      'status': 'Falhou',
      'progress': 0.0,
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Histórico de Traduções'),
      ),
      body: ListView.builder(
        itemCount: _historyItems.length,
        itemBuilder: (context, index) {
          final item = _historyItems[index];
          return Card(
            margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: ListTile(
              contentPadding: const EdgeInsets.all(12),
              title: Text(item['file']),
              subtitle: Text('${item['date']} - ${item['targetLanguage']}'),
              trailing: Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: item['status'] == 'Concluído' ? Colors.green : Colors.red,
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  item['status'],
                  style: const TextStyle(color: Colors.white, fontSize: 12),
                ),
              ),
              onTap: () {
                // Navegar para detalhes
              },
            ),
          );
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          // Limpar histórico
        },
        icon: const Icon(Icons.delete),
        tooltip: 'Limpar Histórico',
      ),
    );
  }
}
