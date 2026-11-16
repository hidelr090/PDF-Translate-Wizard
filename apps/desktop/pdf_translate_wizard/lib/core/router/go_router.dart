import 'package:go_router/go_router.dart';
import 'package:flutter/material.dart';

/// Global router for the PDF Translate Wizard application.
/// Uses go_router for navigation management.
final goRouter = GoRouter(
  initialLocation: '/dashboard',
  routes: [
    GoRoute(
      path: '/dashboard',
      builder: (context, state) => const Text('Dashboard Screen'),
    ),
  ],
);
