import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class AuthProvider extends ChangeNotifier {
  static const String _tokenKey = 'auth_token';
  static const String _usernameKey = 'username';
  
  String? _token;
  String? _username;
  bool _isLoading = false;
  
  // API URLs - in production, these would come from environment variables
  final String _authBaseUrl = 'http://10.0.2.2:4000'; // Android emulator localhost
  final String _apiBaseUrl = 'http://10.0.2.2:3000';
  
  bool get isAuthenticated => _token != null;
  bool get isLoading => _isLoading;
  String? get token => _token;
  String? get username => _username;
  
  AuthProvider() {
    _loadFromStorage();
  }
  
  Future<void> _loadFromStorage() async {
    _isLoading = true;
    notifyListeners();
    
    try {
      final prefs = await SharedPreferences.getInstance();
      _token = prefs.getString(_tokenKey);
      _username = prefs.getString(_usernameKey);
      
      if (_token != null) {
        // Verify token is still valid
        final isValid = await _verifyToken();
        if (!isValid) {
          await logout();
        }
      }
    } catch (e) {
      if (kDebugMode) {
        print('Error loading auth data: $e');
      }
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
  
  Future<bool> _verifyToken() async {
    if (_token == null) return false;
    
    try {
      final response = await http.get(
        Uri.parse('$_authBaseUrl/me'),
        headers: {'Authorization': 'Bearer $_token'},
      );
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }
  
  Future<Map<String, dynamic>> login(String username, String password) async {
    _isLoading = true;
    notifyListeners();
    
    try {
      final response = await http.post(
        Uri.parse('$_authBaseUrl/login'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'username': username,
          'password': password,
        }),
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        _token = data['token'];
        _username = username;
        
        // Save to storage
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString(_tokenKey, _token!);
        await prefs.setString(_usernameKey, username);
        
        _isLoading = false;
        notifyListeners();
        
        return {'success': true};
      } else {
        final error = json.decode(response.body);
        _isLoading = false;
        notifyListeners();
        return {'success': false, 'error': error['error'] ?? 'Login failed'};
      }
    } catch (e) {
      _isLoading = false;
      notifyListeners();
      return {'success': false, 'error': 'Network error: $e'};
    }
  }
  
  Future<Map<String, dynamic>> register(String username, String password) async {
    _isLoading = true;
    notifyListeners();
    
    try {
      final response = await http.post(
        Uri.parse('$_authBaseUrl/register'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'username': username,
          'password': password,
        }),
      );
      
      _isLoading = false;
      notifyListeners();
      
      if (response.statusCode == 200) {
        return {'success': true};
      } else {
        final error = json.decode(response.body);
        return {'success': false, 'error': error['error'] ?? 'Registration failed'};
      }
    } catch (e) {
      _isLoading = false;
      notifyListeners();
      return {'success': false, 'error': 'Network error: $e'};
    }
  }
  
  Future<void> logout() async {
    _token = null;
    _username = null;
    
    // Clear storage
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
    await prefs.remove(_usernameKey);
    
    notifyListeners();
  }
}