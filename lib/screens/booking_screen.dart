import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/doctor.dart';
import '../models/booking.dart';
import '../theme/app_theme.dart';
import 'payment_screen.dart';

class BookingScreen extends StatefulWidget {
  final Doctor doctor;

  const BookingScreen({super.key, required this.doctor});

  @override
  State<BookingScreen> createState() => _BookingScreenState();
}

class _BookingScreenState extends State<BookingScreen> {
  DateTime? _selectedDate;
  String? _selectedSlot;
  ConsultationType _consultationType = ConsultationType.inPerson;

  List<DateTime> get _availableDates {
    final now = DateTime.now();
    final dates = <DateTime>[];
    final dayMap = {
      'Mon': DateTime.monday,
      'Tue': DateTime.tuesday,
      'Wed': DateTime.wednesday,
      'Thu': DateTime.thursday,
      'Fri': DateTime.friday,
      'Sat': DateTime.saturday,
      'Sun': DateTime.sunday,
    };
    for (int i = 1; i <= 30; i++) {
      final date = now.add(Duration(days: i));
      final dayName = DateFormat('E').format(date).substring(0, 3);
      if (widget.doctor.availableDays.contains(dayName)) {
        dates.add(date);
        if (dates.length >= 14) break;
      }
    }
    return dates;
  }

  bool get _canProceed => _selectedDate != null && _selectedSlot != null;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('Book Appointment'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildDoctorSummary(),
            const SizedBox(height: 20),
            _buildConsultationTypeSelector(),
            const SizedBox(height: 20),
            _buildDateSelector(),
            const SizedBox(height: 20),
            if (_selectedDate != null) _buildTimeSlotSelector(),
            if (_selectedDate != null) const SizedBox(height: 20),
            _buildFeeBreakdown(),
            const SizedBox(height: 100),
          ],
        ),
      ),
      bottomNavigationBar: _buildProceedButton(context),
    );
  }

  Widget _buildDoctorSummary() {
    final color = Color(int.parse('FF${widget.doctor.avatarColor}', radix: 16));
    final initials = widget.doctor.name
        .split(' ')
        .where((p) => p.isNotEmpty && p != 'Dr.')
        .take(2)
        .map((p) => p[0])
        .join();

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.divider),
      ),
      child: Row(
        children: [
          Container(
            width: 56,
            height: 56,
            decoration: BoxDecoration(
              color: color.withOpacity(0.15),
              borderRadius: BorderRadius.circular(14),
            ),
            child: Center(
              child: Text(initials, style: TextStyle(color: color, fontSize: 20, fontWeight: FontWeight.bold)),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(widget.doctor.name, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
                Text(widget.doctor.specialty, style: const TextStyle(color: AppTheme.primary, fontSize: 13, fontWeight: FontWeight.w500)),
                Text(widget.doctor.hospital, style: const TextStyle(color: AppTheme.textSecondary, fontSize: 12)),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildConsultationTypeSelector() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('Consultation Type', style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: AppTheme.textPrimary)),
        const SizedBox(height: 10),
        Row(
          children: [
            _typeCard(ConsultationType.inPerson, Icons.local_hospital_outlined, 'In-Person', '₹${widget.doctor.consultationFee.toInt()}'),
            const SizedBox(width: 10),
            _typeCard(ConsultationType.video, Icons.videocam_outlined, 'Video', '₹${(widget.doctor.consultationFee * 0.8).toInt()}'),
            const SizedBox(width: 10),
            _typeCard(ConsultationType.phone, Icons.phone_outlined, 'Phone', '₹${(widget.doctor.consultationFee * 0.6).toInt()}'),
          ],
        ),
      ],
    );
  }

  Widget _typeCard(ConsultationType type, IconData icon, String label, String fee) {
    final isSelected = _consultationType == type;
    return Expanded(
      child: GestureDetector(
        onTap: () => setState(() => _consultationType = type),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 8),
          decoration: BoxDecoration(
            color: isSelected ? AppTheme.primary.withOpacity(0.08) : AppTheme.surface,
            borderRadius: BorderRadius.circular(14),
            border: Border.all(
              color: isSelected ? AppTheme.primary : AppTheme.divider,
              width: isSelected ? 2 : 1,
            ),
          ),
          child: Column(
            children: [
              Icon(icon, color: isSelected ? AppTheme.primary : AppTheme.textSecondary, size: 24),
              const SizedBox(height: 6),
              Text(label, style: TextStyle(color: isSelected ? AppTheme.primary : AppTheme.textPrimary, fontSize: 12, fontWeight: FontWeight.w600)),
              const SizedBox(height: 2),
              Text(fee, style: TextStyle(color: isSelected ? AppTheme.primary : AppTheme.textSecondary, fontSize: 11)),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDateSelector() {
    final dates = _availableDates;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('Select Date', style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: AppTheme.textPrimary)),
        const SizedBox(height: 10),
        SizedBox(
          height: 80,
          child: ListView.separated(
            scrollDirection: Axis.horizontal,
            itemCount: dates.length,
            separatorBuilder: (_, __) => const SizedBox(width: 10),
            itemBuilder: (_, i) {
              final date = dates[i];
              final isSelected = _selectedDate != null &&
                  DateFormat('yyyyMMdd').format(date) == DateFormat('yyyyMMdd').format(_selectedDate!);
              return GestureDetector(
                onTap: () {
                  setState(() {
                    _selectedDate = date;
                    _selectedSlot = null;
                  });
                },
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 200),
                  width: 60,
                  decoration: BoxDecoration(
                    color: isSelected ? AppTheme.primary : AppTheme.surface,
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(color: isSelected ? AppTheme.primary : AppTheme.divider),
                  ),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        DateFormat('E').format(date),
                        style: TextStyle(
                          fontSize: 12,
                          color: isSelected ? Colors.white.withOpacity(0.8) : AppTheme.textSecondary,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        DateFormat('d').format(date),
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: isSelected ? Colors.white : AppTheme.textPrimary,
                        ),
                      ),
                      Text(
                        DateFormat('MMM').format(date),
                        style: TextStyle(
                          fontSize: 11,
                          color: isSelected ? Colors.white.withOpacity(0.8) : AppTheme.textSecondary,
                        ),
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildTimeSlotSelector() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Select Time Slot · ${DateFormat('EEEE, MMM d').format(_selectedDate!)}',
          style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: AppTheme.textPrimary),
        ),
        const SizedBox(height: 10),
        Wrap(
          spacing: 10,
          runSpacing: 10,
          children: widget.doctor.timeSlots.map((slot) {
            final isSelected = _selectedSlot == slot;
            return GestureDetector(
              onTap: () => setState(() => _selectedSlot = slot),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 10),
                decoration: BoxDecoration(
                  color: isSelected ? AppTheme.primary : AppTheme.surface,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(
                    color: isSelected ? AppTheme.primary : AppTheme.divider,
                    width: isSelected ? 2 : 1,
                  ),
                ),
                child: Text(
                  slot,
                  style: TextStyle(
                    color: isSelected ? Colors.white : AppTheme.textPrimary,
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            );
          }).toList(),
        ),
      ],
    );
  }

  double get _fee {
    switch (_consultationType) {
      case ConsultationType.inPerson:
        return widget.doctor.consultationFee;
      case ConsultationType.video:
        return widget.doctor.consultationFee * 0.8;
      case ConsultationType.phone:
        return widget.doctor.consultationFee * 0.6;
    }
  }

  Widget _buildFeeBreakdown() {
    final fee = _fee;
    final gst = fee * 0.18;
    final total = fee + gst;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.divider),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Fee Breakdown', style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          _feeRow('Consultation Fee', '₹${fee.toInt()}'),
          _feeRow('GST (18%)', '₹${gst.toStringAsFixed(0)}'),
          const Divider(height: 20),
          _feeRow('Total Amount', '₹${total.toStringAsFixed(0)}', isTotal: true),
        ],
      ),
    );
  }

  Widget _feeRow(String label, String value, {bool isTotal = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: TextStyle(
            fontSize: isTotal ? 15 : 13,
            fontWeight: isTotal ? FontWeight.bold : FontWeight.normal,
            color: isTotal ? AppTheme.textPrimary : AppTheme.textSecondary,
          )),
          Text(value, style: TextStyle(
            fontSize: isTotal ? 15 : 13,
            fontWeight: isTotal ? FontWeight.bold : FontWeight.w600,
            color: isTotal ? AppTheme.primary : AppTheme.textPrimary,
          )),
        ],
      ),
    );
  }

  Widget _buildProceedButton(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
      decoration: const BoxDecoration(
        color: AppTheme.surface,
        boxShadow: [BoxShadow(color: Colors.black12, blurRadius: 10, offset: Offset(0, -2))],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (!_canProceed)
            const Padding(
              padding: EdgeInsets.only(bottom: 8),
              child: Text(
                'Please select date & time slot to proceed',
                style: TextStyle(fontSize: 12, color: AppTheme.textSecondary),
                textAlign: TextAlign.center,
              ),
            ),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: _canProceed
                  ? () => Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (_) => PaymentScreen(
                            doctor: widget.doctor,
                            date: _selectedDate!,
                            timeSlot: _selectedSlot!,
                            consultationType: _consultationType,
                            fee: _fee,
                          ),
                        ),
                      )
                  : null,
              icon: const Icon(Icons.payment),
              label: Text(_canProceed
                  ? 'Proceed to Pay  ₹${(_fee * 1.18).toStringAsFixed(0)}'
                  : 'Select Date & Time'),
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
