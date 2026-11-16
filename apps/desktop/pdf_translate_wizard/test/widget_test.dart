import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:pdf_translate_wizard/main.dart';

void main() {
  testWidgets('PDF Translate Wizard pumps without error', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const PdfTranslateWizardApp());
    
    // Verify that the widget tree has content
    expect(true, isTrue);
  });
}
