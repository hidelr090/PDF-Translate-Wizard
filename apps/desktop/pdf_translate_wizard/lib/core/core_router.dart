import 'package:go_router/go_router.dart';
import 'features/dashboard/dashboard_screen.dart';
import 'features/translation/translation_screen.dart';
import 'features/settings/settings_screen.dart';
import 'features/file_selection/file_selection_screen.dart';

final goRouter = GoRouter(
  initialLocation: '/dashboard',
  routes: [
    GoRoute(
      path: '/dashboard',
      builder: (context, state) => const DashboardScreen(),
    ),
    GoRoute(
      path: '/translation',
      builder: (context, state) => const TranslationScreen(),
    ),
    GoRoute(
      path: '/file-selection',
      builder: (context, state) => const FileSelectionScreen(),
    ),
    GoRoute(
      path: '/settings',
      builder: (context, state) => const SettingsScreen(),
    ),
  ],
);
