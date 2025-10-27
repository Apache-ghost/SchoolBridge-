import 'package:flutter/material.dart';

class AppTheme {
  static const Color primaryBlue = Color(0xFF2563EB);
  static const Color darkBlue = Color(0xFF1E3A8A);
  static const Color slate900 = Color(0xFF0F172A);
  static const Color slate800 = Color(0xFF1E293B);
  static const Color slate700 = Color(0xFF334155);
  static const Color slate600 = Color(0xFF475569);

  static ThemeData get darkTheme {
    return ThemeData(
      brightness: Brightness.dark,
      primarySwatch: Colors.blue,
      primaryColor: primaryBlue,
      scaffoldBackgroundColor: slate900,
      cardColor: slate800,
      
      colorScheme: const ColorScheme.dark(
        primary: primaryBlue,
        secondary: primaryBlue,
        surface: slate800,
        background: slate900,
        error: Colors.red,
      ),
      
      appBarTheme: const AppBarTheme(
        backgroundColor: slate800,
        elevation: 0,
        titleTextStyle: TextStyle(
          color: Colors.white,
          fontSize: 20,
          fontWeight: FontWeight.bold,
        ),
      ),
      
      cardTheme: CardTheme(
        color: slate800,
        elevation: 4,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),
      
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primaryBlue,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
        ),
      ),
      
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: slate700,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: BorderSide.none,
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: primaryBlue, width: 2),
        ),
        labelStyle: const TextStyle(color: Colors.white70),
        hintStyle: const TextStyle(color: Colors.white54),
      ),
      
      textTheme: const TextTheme(
        headlineLarge: TextStyle(
          color: Colors.white,
          fontSize: 28,
          fontWeight: FontWeight.bold,
        ),
        headlineMedium: TextStyle(
          color: Colors.white,
          fontSize: 24,
          fontWeight: FontWeight.bold,
        ),
        bodyLarge: TextStyle(
          color: Colors.white,
          fontSize: 16,
        ),
        bodyMedium: TextStyle(
          color: Colors.white70,
          fontSize: 14,
        ),
      ),
    );
  }
}