import 'package:flutter/material.dart';
import 'package:flutter_rating_bar/flutter_rating_bar.dart';
import '../models/doctor.dart';
import '../theme/app_theme.dart';

class DoctorCard extends StatelessWidget {
  final Doctor doctor;
  final VoidCallback onTap;

  const DoctorCard({super.key, required this.doctor, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
        decoration: BoxDecoration(
          color: AppTheme.surface,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: AppTheme.divider),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.04),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              _buildAvatar(),
              const SizedBox(width: 14),
              Expanded(child: _buildInfo()),
              _buildFeeChip(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAvatar() {
    final color = Color(int.parse('FF${doctor.avatarColor}', radix: 16));
    final initials = doctor.name
        .split(' ')
        .where((p) => p.isNotEmpty && p != 'Dr.')
        .take(2)
        .map((p) => p[0])
        .join();
    return Container(
      width: 64,
      height: 64,
      decoration: BoxDecoration(
        color: color.withOpacity(0.15),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Center(
        child: Text(
          initials,
          style: TextStyle(
            color: color,
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
    );
  }

  Widget _buildInfo() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          doctor.name,
          style: const TextStyle(
            fontSize: 15,
            fontWeight: FontWeight.w600,
            color: AppTheme.textPrimary,
          ),
        ),
        const SizedBox(height: 2),
        Text(
          doctor.specialty,
          style: const TextStyle(
            fontSize: 13,
            color: AppTheme.primary,
            fontWeight: FontWeight.w500,
          ),
        ),
        const SizedBox(height: 4),
        Row(
          children: [
            RatingBarIndicator(
              rating: doctor.rating,
              itemBuilder: (_, __) => const Icon(Icons.star, color: AppTheme.star),
              itemCount: 5,
              itemSize: 14,
            ),
            const SizedBox(width: 4),
            Text(
              '${doctor.rating} (${doctor.reviewCount})',
              style: const TextStyle(fontSize: 12, color: AppTheme.textSecondary),
            ),
          ],
        ),
        const SizedBox(height: 4),
        Row(
          children: [
            const Icon(Icons.location_on_outlined, size: 13, color: AppTheme.textSecondary),
            const SizedBox(width: 2),
            Expanded(
              child: Text(
                doctor.hospital,
                style: const TextStyle(fontSize: 12, color: AppTheme.textSecondary),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],
        ),
        const SizedBox(height: 4),
        Row(
          children: [
            const Icon(Icons.work_outline, size: 13, color: AppTheme.textSecondary),
            const SizedBox(width: 2),
            Text(
              '${doctor.experienceYears} yrs exp',
              style: const TextStyle(fontSize: 12, color: AppTheme.textSecondary),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildFeeChip() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
          decoration: BoxDecoration(
            color: AppTheme.primary.withOpacity(0.08),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Text(
            '₹${doctor.consultationFee.toInt()}',
            style: const TextStyle(
              color: AppTheme.primary,
              fontWeight: FontWeight.bold,
              fontSize: 14,
            ),
          ),
        ),
        const SizedBox(height: 4),
        const Text(
          'per visit',
          style: TextStyle(fontSize: 10, color: AppTheme.textSecondary),
        ),
      ],
    );
  }
}
