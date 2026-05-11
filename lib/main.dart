import 'package:flutter/material.dart';
import 'screens/home_screen.dart';
import 'screens/my_bookings_screen.dart';
import 'theme/app_theme.dart';

void main() {
  runApp(const DoctorBookingApp());
}

class DoctorBookingApp extends StatelessWidget {
  const DoctorBookingApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'DocBook',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.theme,
      initialRoute: '/',
      routes: {
        '/': (_) => const HomeScreen(),
        '/bookings': (_) => const MyBookingsScreen(),
      },
    );
  }
}
