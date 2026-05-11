class Doctor {
  final String id;
  final String name;
  final String specialty;
  final String city;
  final double rating;
  final int reviewCount;
  final int experienceYears;
  final double consultationFee;
  final String hospital;
  final String qualification;
  final String about;
  final List<String> availableDays;
  final List<String> timeSlots;
  final String avatarColor;

  const Doctor({
    required this.id,
    required this.name,
    required this.specialty,
    required this.city,
    required this.rating,
    required this.reviewCount,
    required this.experienceYears,
    required this.consultationFee,
    required this.hospital,
    required this.qualification,
    required this.about,
    required this.availableDays,
    required this.timeSlots,
    required this.avatarColor,
  });
}
