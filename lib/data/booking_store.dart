import '../models/booking.dart';

class BookingStore {
  static final List<Booking> _bookings = [];

  static List<Booking> get all => List.unmodifiable(_bookings.reversed.toList());

  static void add(Booking booking) => _bookings.add(booking);
}
