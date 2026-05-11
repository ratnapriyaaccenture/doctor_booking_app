import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../data/booking_store.dart';
import '../models/booking.dart';
import '../theme/app_theme.dart';

class MyBookingsScreen extends StatelessWidget {
  const MyBookingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final bookings = BookingStore.all;

    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(title: const Text('My Bookings')),
      body: bookings.isEmpty ? _buildEmptyState() : _buildList(bookings),
    );
  }

  Widget _buildEmptyState() {
    return const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.calendar_today_outlined, size: 72, color: AppTheme.textSecondary),
          SizedBox(height: 16),
          Text('No bookings yet', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppTheme.textPrimary)),
          SizedBox(height: 8),
          Text('Book a consultation with a doctor\nto see it here', textAlign: TextAlign.center,
              style: TextStyle(fontSize: 14, color: AppTheme.textSecondary)),
        ],
      ),
    );
  }

  Widget _buildList(List<Booking> bookings) {
    return ListView.separated(
      padding: const EdgeInsets.all(16),
      itemCount: bookings.length,
      separatorBuilder: (_, __) => const SizedBox(height: 12),
      itemBuilder: (_, i) => _BookingCard(booking: bookings[i]),
    );
  }
}

class _BookingCard extends StatelessWidget {
  final Booking booking;
  const _BookingCard({required this.booking});

  Color get _statusColor {
    switch (booking.status) {
      case BookingStatus.confirmed: return AppTheme.secondary;
      case BookingStatus.pending: return AppTheme.star;
      case BookingStatus.cancelled: return AppTheme.accent;
      case BookingStatus.completed: return AppTheme.textSecondary;
    }
  }

  IconData get _consultIcon {
    switch (booking.consultationType) {
      case ConsultationType.inPerson: return Icons.local_hospital_outlined;
      case ConsultationType.video: return Icons.videocam_outlined;
      case ConsultationType.phone: return Icons.phone_outlined;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppTheme.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.divider),
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 8, offset: const Offset(0, 2))],
      ),
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            decoration: BoxDecoration(
              color: _statusColor.withOpacity(0.08),
              borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('Booking #${booking.id}',
                    style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13, color: AppTheme.textPrimary)),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: _statusColor,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    booking.statusLabel,
                    style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold),
                  ),
                ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(booking.doctorName,
                              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
                          const SizedBox(height: 2),
                          Text(booking.doctorSpecialty,
                              style: const TextStyle(color: AppTheme.primary, fontSize: 13, fontWeight: FontWeight.w500)),
                          const SizedBox(height: 2),
                          Text(booking.hospital,
                              style: const TextStyle(color: AppTheme.textSecondary, fontSize: 12)),
                        ],
                      ),
                    ),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        Text('₹${booking.fee.toStringAsFixed(0)}',
                            style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: AppTheme.primary)),
                        const SizedBox(height: 4),
                        Row(
                          children: [
                            Icon(_consultIcon, size: 14, color: AppTheme.textSecondary),
                            const SizedBox(width: 4),
                            Text(booking.consultationTypeLabel,
                                style: const TextStyle(fontSize: 12, color: AppTheme.textSecondary)),
                          ],
                        ),
                      ],
                    ),
                  ],
                ),
                const Divider(height: 20),
                Row(
                  children: [
                    _infoChip(Icons.calendar_today_outlined,
                        DateFormat('MMM d, y').format(booking.appointmentDate)),
                    const SizedBox(width: 12),
                    _infoChip(Icons.access_time_outlined, booking.timeSlot),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _infoChip(IconData icon, String label) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 14, color: AppTheme.textSecondary),
        const SizedBox(width: 4),
        Text(label, style: const TextStyle(fontSize: 13, color: AppTheme.textPrimary, fontWeight: FontWeight.w500)),
      ],
    );
  }
}
