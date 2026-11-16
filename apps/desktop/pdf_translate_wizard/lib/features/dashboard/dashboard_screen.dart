import 'package:flutter/material.dart';
import 'package:pdf_translate_wizard/core/router/go_router.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState;
}

class _DashboardScreenState extends State<DashboardScreen> {
  // Simple dashboard with quick access to main features
  int _selectedIndex = 0;

  final _pages = [
    // Home/dashboard view
    const Center(
      child: Text(
        'Dashboard',
        style: TextStyle(fontSize: 24),
      ),
    ),
    // Translation screen
    const TranslationScreen(),
    // Provider selection
    const ProviderSelectionScreen(),
    // History screen
    const HistoryScreen(),
    // Glossary screen
    const GlossaryScreen(),
    // Visual fidelity screen
    const VisualFidelityScreen(),
    // Comparison screen
    const ComparisonScreen(),
    // Settings screen
    const SettingsScreen(),
  ];

  void _onItemTapped(int index) {
    setState(() => _selectedIndex = index);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _pages[_selectedIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: _onItemTapped,
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.dashboard),
            label: 'Início',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.insert_drive_file),
            label: 'Nova Tradução',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.psychology),
            label: 'Provedor IA',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.history),
            label: 'Histórico',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.edit),
            label: 'Glossário',
          ),
          BottomNavigationBarItem(
            icon: Icon(
              // Icon for fidelity visual
              Icons.settings_suggest,
            ),
            label: 'Fidelidade',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.insert_comparison),
            label: 'Comparar',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.settings),
            label: 'Configurações',
          ),
        ],
      ),
    );
  }
}
