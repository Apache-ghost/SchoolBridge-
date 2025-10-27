import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:schoolbridge_mobile/providers/auth_provider.dart';
import 'package:schoolbridge_mobile/providers/socket_provider.dart';
import 'package:schoolbridge_mobile/screens/auth_screen.dart';
import 'package:schoolbridge_mobile/screens/dashboard_screen.dart';
import 'package:schoolbridge_mobile/config/app_theme.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProxyProvider<AuthProvider, SocketProvider>(
          create: (_) => SocketProvider(),
          update: (_, auth, socket) => socket!..updateAuth(auth),
        ),
      ],
      child: MaterialApp(
        title: 'SchoolBridge',
        theme: AppTheme.darkTheme,
        home: const AuthWrapper(),
        debugShowCheckedModeBanner: false,
      ),
    );
  }
}

class AuthWrapper extends StatelessWidget {
  const AuthWrapper({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<AuthProvider>(
      builder: (context, authProvider, child) {
        if (authProvider.isLoading) {
          return const Scaffold(
            body: Center(
              child: CircularProgressIndicator(),
            ),
          );
        }
        
        return authProvider.isAuthenticated 
            ? const DashboardScreen() 
            : const AuthScreen();
      },
    );
  }
}