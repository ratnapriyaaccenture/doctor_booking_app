import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:uuid/uuid.dart';
import '../models/doctor.dart';
import '../models/booking.dart';
import '../theme/app_theme.dart';
import 'confirmation_screen.dart';

class PaymentScreen extends StatefulWidget {
  final Doctor doctor;
  final DateTime date;
  final String timeSlot;
  final ConsultationType consultationType;
  final double fee;

  const PaymentScreen({
    super.key,
    required this.doctor,
    required this.date,
    required this.timeSlot,
    required this.consultationType,
    required this.fee,
  });

  @override
  State<PaymentScreen> createState() => _PaymentScreenState();
}

class _PaymentScreenState extends State<PaymentScreen> {
  PaymentMethod _selectedMethod = PaymentMethod.upi;
  bool _isProcessing = false;
  String _upiId = '';
  int _selectedCard = -1;
  int _selectedWallet = 0;
  String _cardNumber = '';
  String _cardHolder = '';
  String _expiry = '';
  String _cvv = '';

  double get _total => widget.fee * 1.18;

  final List<Map<String, dynamic>> _savedCards = [
    {'last4': '4242', 'brand': 'Visa', 'holder': 'Ratna D Priya'},
    {'last4': '8888', 'brand': 'Mastercard', 'holder': 'Ratna D Priya'},
  ];

  final List<Map<String, dynamic>> _wallets = [
    {'name': 'Paytm', 'color': 0xFF00BAF2, 'icon': Icons.account_balance_wallet},
    {'name': 'PhonePe', 'color': 0xFF5F259F, 'icon': Icons.phone_android},
    {'name': 'Google Pay', 'color': 0xFF4285F4, 'icon': Icons.g_mobiledata},
    {'name': 'Amazon Pay', 'color': 0xFFFF9900, 'icon': Icons.shopping_bag_outlined},
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('Payment'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 16),
            child: Row(
              children: [
                const Icon(Icons.lock, size: 16, color: AppTheme.secondary),
                const SizedBox(width: 4),
                Text('Secure', style: TextStyle(color: AppTheme.secondary, fontSize: 12, fontWeight: FontWeight.w600)),
              ],
            ),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            _buildOrderSummary(),
            const SizedBox(height: 16),
            _buildPaymentMethodSelector(),
            const SizedBox(height: 16),
            _buildPaymentForm(),
            const SizedBox(height: 100),
          ],
        ),
      ),
      bottomNavigationBar: _buildPayButton(context),
    );
  }

  Widget _buildOrderSummary() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [AppTheme.primary, AppTheme.primaryDark],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Order Summary', style: TextStyle(color: Colors.white70, fontSize: 12, fontWeight: FontWeight.w500)),
          const SizedBox(height: 8),
          Text(
            widget.doctor.name,
            style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold),
          ),
          Text(
            '${widget.consultationType == ConsultationType.inPerson ? "In-Person" : widget.consultationType == ConsultationType.video ? "Video Call" : "Phone Call"} Consultation',
            style: const TextStyle(color: Colors.white70, fontSize: 13),
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              const Icon(Icons.calendar_today, color: Colors.white70, size: 14),
              const SizedBox(width: 4),
              Text(
                '${DateFormat('EEE, MMM d').format(widget.date)} · ${widget.timeSlot}',
                style: const TextStyle(color: Colors.white70, fontSize: 13),
              ),
            ],
          ),
          const SizedBox(height: 12),
          const Divider(color: Colors.white24),
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('Total Amount', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w600, fontSize: 14)),
              Text(
                '₹${_total.toStringAsFixed(0)}',
                style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 22),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildPaymentMethodSelector() {
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
          const Text('Payment Method', style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          Row(
            children: [
              _methodTab(PaymentMethod.upi, 'UPI', Icons.currency_rupee),
              _methodTab(PaymentMethod.card, 'Card', Icons.credit_card),
              _methodTab(PaymentMethod.wallet, 'Wallet', Icons.account_balance_wallet_outlined),
              _methodTab(PaymentMethod.netBanking, 'Net Bank', Icons.account_balance_outlined),
            ],
          ),
        ],
      ),
    );
  }

  Widget _methodTab(PaymentMethod method, String label, IconData icon) {
    final isSelected = _selectedMethod == method;
    return Expanded(
      child: GestureDetector(
        onTap: () => setState(() => _selectedMethod = method),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          margin: const EdgeInsets.symmetric(horizontal: 3),
          padding: const EdgeInsets.symmetric(vertical: 10),
          decoration: BoxDecoration(
            color: isSelected ? AppTheme.primary : AppTheme.background,
            borderRadius: BorderRadius.circular(10),
          ),
          child: Column(
            children: [
              Icon(icon, size: 20, color: isSelected ? Colors.white : AppTheme.textSecondary),
              const SizedBox(height: 4),
              Text(
                label,
                style: TextStyle(
                  fontSize: 11,
                  color: isSelected ? Colors.white : AppTheme.textSecondary,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPaymentForm() {
    switch (_selectedMethod) {
      case PaymentMethod.upi:
        return _buildUPIForm();
      case PaymentMethod.card:
        return _buildCardForm();
      case PaymentMethod.wallet:
        return _buildWalletForm();
      case PaymentMethod.netBanking:
        return _buildNetBankingForm();
    }
  }

  Widget _buildUPIForm() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: _formDecoration(),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Pay via UPI', style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold)),
          const SizedBox(height: 16),
          _buildQRSection(),
          const SizedBox(height: 16),
          const Row(
            children: [
              Expanded(child: Divider()),
              Padding(
                padding: EdgeInsets.symmetric(horizontal: 12),
                child: Text('OR', style: TextStyle(color: AppTheme.textSecondary, fontSize: 12)),
              ),
              Expanded(child: Divider()),
            ],
          ),
          const SizedBox(height: 16),
          TextField(
            onChanged: (v) => setState(() => _upiId = v),
            keyboardType: TextInputType.emailAddress,
            decoration: const InputDecoration(
              labelText: 'Enter UPI ID',
              hintText: 'yourname@upi',
              prefixIcon: Icon(Icons.currency_rupee, size: 18),
            ),
          ),
          const SizedBox(height: 12),
          const Text(
            'Accepted: Google Pay, PhonePe, Paytm, BHIM UPI',
            style: TextStyle(fontSize: 11, color: AppTheme.textSecondary),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildQRSection() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppTheme.background,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppTheme.divider),
      ),
      child: Column(
        children: [
          Container(
            width: 120,
            height: 120,
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(8),
              boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.08), blurRadius: 8)],
            ),
            child: CustomPaint(
              painter: _QRPainter(),
            ),
          ),
          const SizedBox(height: 8),
          const Text('Scan to Pay', style: TextStyle(fontSize: 12, color: AppTheme.textSecondary)),
          const Text('docbook@ybl', style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: AppTheme.primary)),
        ],
      ),
    );
  }

  Widget _buildCardForm() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: _formDecoration(),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Pay via Card', style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold)),
          const SizedBox(height: 16),
          if (_savedCards.isNotEmpty) ...[
            const Text('Saved Cards', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: AppTheme.textSecondary)),
            const SizedBox(height: 10),
            ..._savedCards.asMap().entries.map((e) => _savedCardTile(e.key, e.value)),
            const SizedBox(height: 12),
            const Row(
              children: [
                Expanded(child: Divider()),
                Padding(
                  padding: EdgeInsets.symmetric(horizontal: 12),
                  child: Text('Add New Card', style: TextStyle(color: AppTheme.textSecondary, fontSize: 12)),
                ),
                Expanded(child: Divider()),
              ],
            ),
            const SizedBox(height: 12),
          ],
          _buildCardPreview(),
          const SizedBox(height: 16),
          TextField(
            onChanged: (v) => setState(() => _cardNumber = v),
            keyboardType: TextInputType.number,
            maxLength: 19,
            decoration: const InputDecoration(
              labelText: 'Card Number',
              hintText: '1234 5678 9012 3456',
              prefixIcon: Icon(Icons.credit_card, size: 18),
              counterText: '',
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            onChanged: (v) => setState(() => _cardHolder = v),
            decoration: const InputDecoration(
              labelText: 'Cardholder Name',
              hintText: 'Name on card',
              prefixIcon: Icon(Icons.person_outline, size: 18),
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: TextField(
                  onChanged: (v) => setState(() => _expiry = v),
                  keyboardType: TextInputType.number,
                  maxLength: 5,
                  decoration: const InputDecoration(
                    labelText: 'Expiry',
                    hintText: 'MM/YY',
                    counterText: '',
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: TextField(
                  onChanged: (v) => setState(() => _cvv = v),
                  keyboardType: TextInputType.number,
                  maxLength: 3,
                  obscureText: true,
                  decoration: const InputDecoration(
                    labelText: 'CVV',
                    hintText: '• • •',
                    counterText: '',
                    suffixIcon: Icon(Icons.help_outline, size: 18),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _savedCardTile(int index, Map<String, dynamic> card) {
    final isSelected = _selectedCard == index;
    return GestureDetector(
      onTap: () => setState(() => _selectedCard = index),
      child: Container(
        margin: const EdgeInsets.only(bottom: 8),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
        decoration: BoxDecoration(
          color: isSelected ? AppTheme.primary.withOpacity(0.05) : AppTheme.background,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: isSelected ? AppTheme.primary : AppTheme.divider),
        ),
        child: Row(
          children: [
            Icon(Icons.credit_card, color: isSelected ? AppTheme.primary : AppTheme.textSecondary),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('${card['brand']} •••• ${card['last4']}',
                    style: TextStyle(fontWeight: FontWeight.w600, color: isSelected ? AppTheme.primary : AppTheme.textPrimary)),
                  Text(card['holder'], style: const TextStyle(fontSize: 12, color: AppTheme.textSecondary)),
                ],
              ),
            ),
            if (isSelected) const Icon(Icons.check_circle, color: AppTheme.primary),
          ],
        ),
      ),
    );
  }

  Widget _buildCardPreview() {
    return Container(
      height: 140,
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF1A73E8), Color(0xFF6C5CE7)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [BoxShadow(color: AppTheme.primary.withOpacity(0.3), blurRadius: 12, offset: const Offset(0, 6))],
      ),
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('DocBook Pay', style: TextStyle(color: Colors.white70, fontSize: 12)),
              const Icon(Icons.credit_card, color: Colors.white, size: 28),
            ],
          ),
          const Spacer(),
          Text(
            _cardNumber.isEmpty ? '•••• •••• •••• ••••' : _cardNumber,
            style: const TextStyle(color: Colors.white, fontSize: 16, letterSpacing: 2, fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(_cardHolder.isEmpty ? 'CARD HOLDER' : _cardHolder.toUpperCase(),
                style: const TextStyle(color: Colors.white70, fontSize: 12)),
              Text(_expiry.isEmpty ? 'MM/YY' : _expiry,
                style: const TextStyle(color: Colors.white70, fontSize: 12)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildWalletForm() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: _formDecoration(),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Select Wallet', style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold)),
          const SizedBox(height: 16),
          GridView.count(
            crossAxisCount: 2,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            crossAxisSpacing: 10,
            mainAxisSpacing: 10,
            childAspectRatio: 2.5,
            children: _wallets.asMap().entries.map((e) {
              final isSelected = _selectedWallet == e.key;
              return GestureDetector(
                onTap: () => setState(() => _selectedWallet = e.key),
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 200),
                  decoration: BoxDecoration(
                    color: isSelected
                        ? Color(e.value['color']).withOpacity(0.1)
                        : AppTheme.background,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: isSelected ? Color(e.value['color']) : AppTheme.divider,
                      width: isSelected ? 2 : 1,
                    ),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(e.value['icon'], color: Color(e.value['color']), size: 20),
                      const SizedBox(width: 8),
                      Text(
                        e.value['name'],
                        style: TextStyle(
                          fontWeight: FontWeight.w600,
                          fontSize: 13,
                          color: isSelected ? Color(e.value['color']) : AppTheme.textPrimary,
                        ),
                      ),
                    ],
                  ),
                ),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }

  Widget _buildNetBankingForm() {
    final banks = [
      {'name': 'SBI', 'color': 0xFF1A237E},
      {'name': 'HDFC Bank', 'color': 0xFF004C8C},
      {'name': 'ICICI Bank', 'color': 0xFFB71C1C},
      {'name': 'Axis Bank', 'color': 0xFF880E4F},
      {'name': 'Kotak Bank', 'color': 0xFFE65100},
      {'name': 'Bank of Baroda', 'color': 0xFF1B5E20},
    ];

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: _formDecoration(),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Net Banking', style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold)),
          const SizedBox(height: 4),
          const Text('Select your bank', style: TextStyle(fontSize: 12, color: AppTheme.textSecondary)),
          const SizedBox(height: 16),
          ...banks.map((bank) => Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
              decoration: BoxDecoration(
                color: AppTheme.background,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppTheme.divider),
              ),
              child: Row(
                children: [
                  Container(
                    width: 36,
                    height: 36,
                    decoration: BoxDecoration(
                      color: Color(bank['color']!),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Center(
                      child: Text(
                        bank['name']![0],
                        style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16),
                      ),
                    ),
                  ),
                  const SizedBox(width: 14),
                  Text(bank['name']!, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
                  const Spacer(),
                  const Icon(Icons.arrow_forward_ios, size: 14, color: AppTheme.textSecondary),
                ],
              ),
            ),
          )),
        ],
      ),
    );
  }

  BoxDecoration _formDecoration() {
    return BoxDecoration(
      color: AppTheme.surface,
      borderRadius: BorderRadius.circular(16),
      border: Border.all(color: AppTheme.divider),
    );
  }

  Widget _buildPayButton(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
      decoration: const BoxDecoration(
        color: AppTheme.surface,
        boxShadow: [BoxShadow(color: Colors.black12, blurRadius: 10, offset: Offset(0, -2))],
      ),
      child: SizedBox(
        width: double.infinity,
        child: ElevatedButton(
          onPressed: _isProcessing ? null : () => _processPayment(context),
          style: ElevatedButton.styleFrom(
            backgroundColor: AppTheme.secondary,
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(vertical: 16),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
          ),
          child: _isProcessing
              ? const Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                    ),
                    SizedBox(width: 12),
                    Text('Processing Payment...', style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600)),
                  ],
                )
              : Text(
                  'Pay ₹${_total.toStringAsFixed(0)} Securely',
                  style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold),
                ),
        ),
      ),
    );
  }

  Future<void> _processPayment(BuildContext context) async {
    setState(() => _isProcessing = true);
    await Future.delayed(const Duration(seconds: 2));

    final txnId = 'TXN${DateTime.now().millisecondsSinceEpoch}';
    final bookingId = const Uuid().v4().substring(0, 8).toUpperCase();

    final booking = Booking(
      id: bookingId,
      doctorId: widget.doctor.id,
      doctorName: widget.doctor.name,
      doctorSpecialty: widget.doctor.specialty,
      hospital: widget.doctor.hospital,
      appointmentDate: widget.date,
      timeSlot: widget.timeSlot,
      consultationType: widget.consultationType,
      fee: _total,
      status: BookingStatus.confirmed,
      paymentMethod: _selectedMethod,
      transactionId: txnId,
      bookedAt: DateTime.now(),
    );

    if (!mounted) return;
    Navigator.pushAndRemoveUntil(
      context,
      MaterialPageRoute(builder: (_) => ConfirmationScreen(booking: booking)),
      (route) => route.isFirst,
    );
  }
}

class _QRPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.black
      ..style = PaintingStyle.fill;

    final cell = size.width / 11;

    final pattern = [
      [1,1,1,1,1,1,1,0,1,0,0],
      [1,0,0,0,0,0,1,0,0,1,0],
      [1,0,1,1,1,0,1,0,1,0,1],
      [1,0,1,1,1,0,1,0,0,1,1],
      [1,0,1,1,1,0,1,0,1,1,0],
      [1,0,0,0,0,0,1,0,0,0,1],
      [1,1,1,1,1,1,1,0,1,0,1],
      [0,0,0,0,0,0,0,0,0,1,0],
      [1,0,1,1,0,1,1,0,1,0,1],
      [0,1,0,0,1,0,0,1,0,1,1],
      [1,1,1,0,1,1,1,0,1,0,0],
    ];

    for (int r = 0; r < pattern.length; r++) {
      for (int c = 0; c < pattern[r].length; c++) {
        if (pattern[r][c] == 1) {
          canvas.drawRect(
            Rect.fromLTWH(c * cell + 4, r * cell + 4, cell - 1, cell - 1),
            paint,
          );
        }
      }
    }
  }

  @override
  bool shouldRepaint(_) => false;
}
