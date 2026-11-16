import 'core/themes/app_theme.dart';
import 'core/router/go_router.dart';
import 'package:flutter/material.dart';

void main() {
  runApp(const PdfTranslateWizardApp());
}

class PdfTranslateWizardApp extends StatelessWidget {
  const PdfTranslateWizardApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'PDF Translate Wizard',
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      routerDelegate: goRouter.routerDelegate,
      routeInformationParser: goRouter.routeInformationParser,
      routeInformationProvider: goRouter.routeInformationProvider,
    );
  }
}
