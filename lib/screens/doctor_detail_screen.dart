import 'package:flutter/material.dart';
import 'package:flutter_rating_bar/flutter_rating_bar.dart';
import '../models/doctor.dart';
import '../theme/app_theme.dart';
import 'booking_screen.dart';

class DoctorDetailScreen extends StatelessWidget {
  final Doctor doctor;

  const DoctorDetailScreen({super.key, required this.doctor});

  @override
  Widget build(BuildContext context) {
    final color = Color(int.parse('FF${doctor.avatarColor}', radix: 16));

    return Scaffold(
      backgroundColor: AppTheme.background,
      body: CustomScrollView(
        slivers: [
          _buildSliverAppBar(context, color),
          SliverToBoxAdapter(
            child: Column(
              children: [
                _buildProfileCard(color),
                _buildStatsRow(),
                _buildAboutSection(),
                _buildAvailabilitySection(),
                _buildTimeSlotsPreview(),
                _buildConsultationTypes(),
                const SizedBox(height: 100),
              ],
            ),
          ),
        ],
      ),
      bottomNavigationBar: _buildBookButton(context),
    );
  }

  Widget _buildSliverAppBar(BuildContext context, Color color) {
    return SliverAppBar(
      expandedHeight: 160,
      pinned: true,
      backgroundColor: color,
      leading: IconButton(
        icon: const Icon(Icons.arrow_back, color: Colors.white),
        onPressed: () => Navigator.pop(context),
      ),
      flexibleSpace: FlexibleSpaceBar(
        background: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [color, color.withOpacity(0.7)],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildProfileCard(Color color) {
    final initials = doctor.name
        .split(' ')
        .where((p) => p.isNotEmpty && p != 'Dr.')
        .take(2)
        .map((p) => p[0])
        .join();

    return Transform.translate(
      offset: const Offset(0, -40),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16),
        child: Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: AppTheme.surface,
            borderRadius: BorderRadius.circular(20),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.08),
                blurRadius: 16,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Column(
            children: [
              Container(
                width: 80,
                height: 80,
                decoration: BoxDecoration(
                  color: color.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Center(
                  child: Text(
                    initials,
                    style: TextStyle(color: color, fontSize: 28, fontWeight: FontWeight.bold),
                  ),
                ),
              ),
              const SizedBox(height: 12),
              Text(
                doctor.name,
                style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: AppTheme.textPrimary),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 4),
              Text(
                doctor.specialty,
                style: const TextStyle(fontSize: 14, color: AppTheme.primary, fontWeight: FontWeight.w600),
              ),
              const SizedBox(height: 4),
              Text(
                doctor.qualification,
                style: const TextStyle(fontSize: 12, color: AppTheme.textSecondary),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 12),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  RatingBarIndicator(
                    rating: doctor.rating,
                    itemBuilder: (_, __) => const Icon(Icons.star, color: AppTheme.star),
                    itemCount: 5,
                    itemSize: 18,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    '${doctor.rating} · ${doctor.reviewCount} reviews',
                    style: const TextStyle(fontSize: 13, color: AppTheme.textSecondary),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                decoration: BoxDecoration(
                  color: AppTheme.background,
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.location_on, size: 14, color: AppTheme.textSecondary),
                    const SizedBox(width: 4),
                    Flexible(
                      child: Text(
                        doctor.hospital,
                        style: const TextStyle(fontSize: 12, color: AppTheme.textSecondary),
                        textAlign: TextAlign.center,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatsRow() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
      child: Row(
        children: [
          _statCard('${doctor.experienceYears}+', 'Years Exp.', Icons.workspace_premium_outlined),
          const SizedBox(width: 12),
          _statCard('${doctor.reviewCount}+', 'Patients', Icons.people_outline),
          const SizedBox(width: 12),
          _statCard('₹${doctor.consultationFee.toInt()}', 'Consult Fee', Icons.currency_rupee),
        ],
      ),
    );
  }

  Widget _statCard(String value, String label, IconData icon) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 10),
        decoration: BoxDecoration(
          color: AppTheme.surface,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: AppTheme.divider),
        ),
        child: Column(
          children: [
            Icon(icon, color: AppTheme.primary, size: 22),
            const SizedBox(height: 6),
            Text(value, style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: AppTheme.textPrimary)),
            Text(label, style: const TextStyle(fontSize: 11, color: AppTheme.textSecondary)),
          ],
        ),
      ),
    );
  }

  Widget _buildAboutSection() {
    return _sectionCard(
      'About Doctor',
      Text(doctor.about, style: const TextStyle(fontSize: 14, color: AppTheme.textSecondary, height: 1.6)),
    );
  }

  Widget _buildAvailabilitySection() {
    return _sectionCard(
      'Available Days',
      Wrap(
        spacing: 8,
        children: doctor.availableDays.map((day) => Container(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
          decoration: BoxDecoration(
            color: AppTheme.primary.withOpacity(0.08),
            borderRadius: BorderRadius.circular(20),
          ),
          child: Text(day, style: const TextStyle(color: AppTheme.primary, fontSize: 13, fontWeight: FontWeight.w500)),
        )).toList(),
      ),
    );
  }

  Widget _buildTimeSlotsPreview() {
    return _sectionCard(
      'Available Time Slots',
      Wrap(
        spacing: 8,
        runSpacing: 8,
        children: doctor.timeSlots.map((slot) => Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            color: AppTheme.background,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: AppTheme.divider),
          ),
          child: Text(slot, style: const TextStyle(fontSize: 12, color: AppTheme.textPrimary, fontWeight: FontWeight.w500)),
        )).toList(),
      ),
    );
  }

  Widget _buildConsultationTypes() {
    return _sectionCard(
      'Consultation Types',
      Row(
        children: [
          _consultTypeChip(Icons.local_hospital_outlined, 'In-Person'),
          const SizedBox(width: 10),
          _consultTypeChip(Icons.videocam_outlined, 'Video Call'),
          const SizedBox(width: 10),
          _consultTypeChip(Icons.phone_outlined, 'Phone Call'),
        ],
      ),
    );
  }

  Widget _consultTypeChip(IconData icon, String label) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: AppTheme.secondary.withOpacity(0.08),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 16, color: AppTheme.secondary),
          const SizedBox(width: 6),
          Text(label, style: const TextStyle(fontSize: 12, color: AppTheme.secondary, fontWeight: FontWeight.w500)),
        ],
      ),
    );
  }

  Widget _sectionCard(String title, Widget content) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 0, 16, 12),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppTheme.surface,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: AppTheme.divider),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: AppTheme.textPrimary)),
            const SizedBox(height: 12),
            content,
          ],
        ),
      ),
    );
  }

  Widget _buildBookButton(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
      decoration: const BoxDecoration(
        color: AppTheme.surface,
        boxShadow: [BoxShadow(color: Colors.black12, blurRadius: 10, offset: Offset(0, -2))],
      ),
      child: SizedBox(
        width: double.infinity,
        child: ElevatedButton.icon(
          onPressed: () => Navigator.push(
            context,
            MaterialPageRoute(builder: (_) => BookingScreen(doctor: doctor)),
          ),
          icon: const Icon(Icons.calendar_today),
          label: const Text('Book Appointment'),
          style: ElevatedButton.styleFrom(
            backgroundColor: AppTheme.primary,
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(vertical: 16),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
          ),
        ),
      ),
    );
  }
}
