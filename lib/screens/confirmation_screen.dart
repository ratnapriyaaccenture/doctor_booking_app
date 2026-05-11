import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/booking.dart';
import '../theme/app_theme.dart';
import '../data/booking_store.dart';

class ConfirmationScreen extends StatefulWidget {
  final Booking booking;

  const ConfirmationScreen({super.key, required this.booking});

  @override
  State<ConfirmationScreen> createState() => _ConfirmationScreenState();
}

class _ConfirmationScreenState extends State<ConfirmationScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnim;
  late Animation<double> _fadeAnim;

  @override
  void initState() {
    super.initState();
    BookingStore.add(widget.booking);
    _controller = AnimationController(vsync: this, duration: const Duration(milliseconds: 600));
    _scaleAnim = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _controller, curve: Curves.elasticOut),
    );
    _fadeAnim = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeIn),
    );
    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            children: [
              const SizedBox(height: 32),
              _buildSuccessIcon(),
              const SizedBox(height: 24),
              FadeTransition(
                opacity: _fadeAnim,
                child: Column(
                  children: [
                    const Text(
                      'Booking Confirmed!',
                      style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: AppTheme.textPrimary),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Your appointment has been successfully booked.\nA confirmation will be sent to your email.',
                      textAlign: TextAlign.center,
                      style: TextStyle(fontSize: 14, color: AppTheme.textSecondary, height: 1.5),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 32),
              FadeTransition(opacity: _fadeAnim, child: _buildBookingCard()),
              const SizedBox(height: 20),
              FadeTransition(opacity: _fadeAnim, child: _buildPaymentDetails()),
              const SizedBox(height: 32),
              FadeTransition(opacity: _fadeAnim, child: _buildActions(context)),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSuccessIcon() {
    return ScaleTransition(
      scale: _scaleAnim,
      child: Container(
        width: 90,
        height: 90,
        decoration: const BoxDecoration(
          color: AppTheme.secondary,
          shape: BoxShape.circle,
        ),
        child: const Icon(Icons.check_rounded, color: Colors.white, size: 50),
      ),
    );
  }

  Widget _buildBookingCard() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppTheme.surface,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppTheme.divider),
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 12)],
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('Booking ID', style: TextStyle(color: AppTheme.textSecondary, fontSize: 13)),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                decoration: BoxDecoration(
                  color: AppTheme.primary.withOpacity(0.08),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  '#${widget.booking.id}',
                  style: const TextStyle(color: AppTheme.primary, fontWeight: FontWeight.bold, fontSize: 13),
                ),
              ),
            ],
          ),
          const Divider(height: 24),
          _detailRow(Icons.person_outline, 'Doctor', widget.booking.doctorName),
          _detailRow(Icons.medical_services_outlined, 'Specialty', widget.booking.doctorSpecialty),
          _detailRow(Icons.location_on_outlined, 'Hospital', widget.booking.hospital),
          _detailRow(Icons.calendar_today_outlined, 'Date',
              DateFormat('EEEE, MMMM d, y').format(widget.booking.appointmentDate)),
          _detailRow(Icons.access_time_outlined, 'Time', widget.booking.timeSlot),
          _detailRow(Icons.video_call_outlined, 'Type', widget.booking.consultationTypeLabel),
          const Divider(height: 20),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('Amount Paid', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
              Text(
                '₹${widget.booking.fee.toStringAsFixed(0)}',
                style: const TextStyle(color: AppTheme.secondary, fontWeight: FontWeight.bold, fontSize: 18),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildPaymentDetails() {
    String methodLabel;
    IconData methodIcon;
    switch (widget.booking.paymentMethod) {
      case PaymentMethod.upi:
        methodLabel = 'UPI Payment';
        methodIcon = Icons.currency_rupee;
        break;
      case PaymentMethod.card:
        methodLabel = 'Card Payment';
        methodIcon = Icons.credit_card;
        break;
      case PaymentMethod.wallet:
        methodLabel = 'Wallet Payment';
        methodIcon = Icons.account_balance_wallet_outlined;
        break;
      case PaymentMethod.netBanking:
        methodLabel = 'Net Banking';
        methodIcon = Icons.account_balance_outlined;
        break;
    }

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.secondary.withOpacity(0.05),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: AppTheme.secondary.withOpacity(0.2)),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: AppTheme.secondary.withOpacity(0.1),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(methodIcon, color: AppTheme.secondary, size: 20),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(methodLabel,
                    style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14, color: AppTheme.textPrimary)),
                Text('Txn ID: ${widget.booking.transactionId}',
                    style: const TextStyle(fontSize: 11, color: AppTheme.textSecondary)),
              ],
            ),
          ),
          const Icon(Icons.check_circle, color: AppTheme.secondary, size: 22),
        ],
      ),
    );
  }

  Widget _detailRow(IconData icon, String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 7),
      child: Row(
        children: [
          Icon(icon, size: 16, color: AppTheme.textSecondary),
          const SizedBox(width: 10),
          SizedBox(
            width: 80,
            child: Text(label, style: const TextStyle(fontSize: 13, color: AppTheme.textSecondary)),
          ),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: AppTheme.textPrimary),
              textAlign: TextAlign.right,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildActions(BuildContext context) {
    return Column(
      children: [
        SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed: () => Navigator.pushNamedAndRemoveUntil(context, '/', (_) => false),
            icon: const Icon(Icons.home_outlined),
            label: const Text('Back to Home'),
          ),
        ),
        const SizedBox(height: 12),
        SizedBox(
          width: double.infinity,
          child: OutlinedButton.icon(
            onPressed: () {
              Navigator.pushNamedAndRemoveUntil(context, '/', (_) => false);
              Navigator.pushNamed(context, '/bookings');
            },
            icon: const Icon(Icons.calendar_month_outlined),
            label: const Text('View My Bookings'),
            style: OutlinedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 14),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            ),
          ),
        ),
      ],
    );
  }
}
