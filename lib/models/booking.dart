enum BookingStatus { confirmed, pending, cancelled, completed }
enum ConsultationType { inPerson, video, phone }
enum PaymentMethod { upi, card, wallet, netBanking }

class Booking {
  final String id;
  final String doctorId;
  final String doctorName;
  final String doctorSpecialty;
  final String hospital;
  final DateTime appointmentDate;
  final String timeSlot;
  final ConsultationType consultationType;
  final double fee;
  final BookingStatus status;
  final PaymentMethod paymentMethod;
  final String transactionId;
  final DateTime bookedAt;

  const Booking({
    required this.id,
    required this.doctorId,
    required this.doctorName,
    required this.doctorSpecialty,
    required this.hospital,
    required this.appointmentDate,
    required this.timeSlot,
    required this.consultationType,
    required this.fee,
    required this.status,
    required this.paymentMethod,
    required this.transactionId,
    required this.bookedAt,
  });

  String get consultationTypeLabel {
    switch (consultationType) {
      case ConsultationType.inPerson:
        return 'In-Person';
      case ConsultationType.video:
        return 'Video Call';
      case ConsultationType.phone:
        return 'Phone Call';
    }
  }

  String get statusLabel {
    switch (status) {
      case BookingStatus.confirmed:
        return 'Confirmed';
      case BookingStatus.pending:
        return 'Pending';
      case BookingStatus.cancelled:
        return 'Cancelled';
      case BookingStatus.completed:
        return 'Completed';
    }
  }
}
