import 'package:flutter/material.dart';
import '../data/mock_doctors.dart';
import '../models/doctor.dart';
import '../theme/app_theme.dart';
import '../widgets/doctor_card.dart';
import 'doctor_detail_screen.dart';
import 'my_bookings_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  String? _selectedCity;
  String? _selectedSpecialty;
  double _minRating = 0;
  final TextEditingController _searchController = TextEditingController();
  String _searchQuery = '';
  List<Doctor> _doctors = mockDoctors;

  @override
  void initState() {
    super.initState();
    _searchController.addListener(() {
      setState(() {
        _searchQuery = _searchController.text;
        _applyFilters();
      });
    });
  }

  void _applyFilters() {
    setState(() {
      _doctors = filterDoctors(
        city: _selectedCity,
        specialty: _selectedSpecialty,
        minRating: _minRating > 0 ? _minRating : null,
        searchQuery: _searchQuery.isNotEmpty ? _searchQuery : null,
      );
    });
  }

  void _clearFilters() {
    setState(() {
      _selectedCity = null;
      _selectedSpecialty = null;
      _minRating = 0;
      _searchController.clear();
      _searchQuery = '';
      _doctors = mockDoctors;
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      body: CustomScrollView(
        slivers: [
          _buildAppBar(context),
          SliverToBoxAdapter(child: _buildSearchBar()),
          SliverToBoxAdapter(child: _buildFilters()),
          SliverToBoxAdapter(child: _buildResultsHeader()),
          _doctors.isEmpty
              ? SliverToBoxAdapter(child: _buildEmptyState())
              : SliverList(
                  delegate: SliverChildBuilderDelegate(
                    (context, index) => DoctorCard(
                      doctor: _doctors[index],
                      onTap: () => Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (_) => DoctorDetailScreen(doctor: _doctors[index]),
                        ),
                      ),
                    ),
                    childCount: _doctors.length,
                  ),
                ),
          const SliverToBoxAdapter(child: SizedBox(height: 24)),
        ],
      ),
    );
  }

  Widget _buildAppBar(BuildContext context) {
    return SliverAppBar(
      expandedHeight: 140,
      floating: false,
      pinned: true,
      backgroundColor: AppTheme.primary,
      flexibleSpace: FlexibleSpaceBar(
        background: Container(
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [AppTheme.primary, AppTheme.primaryDark],
            ),
          ),
          child: Padding(
            padding: const EdgeInsets.fromLTRB(20, 60, 20, 16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Find a Doctor',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 22,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          '${_doctors.length} doctors available',
                          style: TextStyle(color: Colors.white.withOpacity(0.85), fontSize: 13),
                        ),
                      ],
                    ),
                    IconButton(
                      onPressed: () => Navigator.push(
                        context,
                        MaterialPageRoute(builder: (_) => const MyBookingsScreen()),
                      ),
                      icon: const Icon(Icons.calendar_month_outlined, color: Colors.white, size: 26),
                      tooltip: 'My Bookings',
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildSearchBar() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
      child: TextField(
        controller: _searchController,
        decoration: InputDecoration(
          hintText: 'Search by name, specialty, hospital...',
          prefixIcon: const Icon(Icons.search, color: AppTheme.textSecondary),
          suffixIcon: _searchQuery.isNotEmpty
              ? IconButton(
                  icon: const Icon(Icons.clear, color: AppTheme.textSecondary),
                  onPressed: () {
                    _searchController.clear();
                    _applyFilters();
                  },
                )
              : null,
          hintStyle: const TextStyle(color: AppTheme.textSecondary, fontSize: 14),
        ),
      ),
    );
  }

  Widget _buildFilters() {
    final cities = availableCities;
    final specialties = availableSpecialties;
    final bool hasFilter = _selectedCity != null || _selectedSpecialty != null || _minRating > 0;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // City filter
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('City', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13, color: AppTheme.textPrimary)),
              const SizedBox(height: 6),
              SizedBox(
                height: 36,
                child: ListView.separated(
                  scrollDirection: Axis.horizontal,
                  itemCount: cities.length,
                  separatorBuilder: (_, __) => const SizedBox(width: 8),
                  itemBuilder: (context, i) => ChoiceChip(
                    label: Text(cities[i]),
                    selected: _selectedCity == cities[i],
                    onSelected: (v) {
                      setState(() => _selectedCity = v ? cities[i] : null);
                      _applyFilters();
                    },
                    selectedColor: AppTheme.primary,
                    labelStyle: TextStyle(
                      color: _selectedCity == cities[i] ? Colors.white : AppTheme.textPrimary,
                      fontSize: 13,
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),

        // Specialty filter
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Specialty', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13, color: AppTheme.textPrimary)),
              const SizedBox(height: 6),
              SizedBox(
                height: 36,
                child: ListView.separated(
                  scrollDirection: Axis.horizontal,
                  itemCount: specialties.length,
                  separatorBuilder: (_, __) => const SizedBox(width: 8),
                  itemBuilder: (context, i) => ChoiceChip(
                    label: Text(specialties[i]),
                    selected: _selectedSpecialty == specialties[i],
                    onSelected: (v) {
                      setState(() => _selectedSpecialty = v ? specialties[i] : null);
                      _applyFilters();
                    },
                    selectedColor: AppTheme.primary,
                    labelStyle: TextStyle(
                      color: _selectedSpecialty == specialties[i] ? Colors.white : AppTheme.textPrimary,
                      fontSize: 13,
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),

        // Rating filter
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
          child: Row(
            children: [
              const Text('Min Rating:', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13, color: AppTheme.textPrimary)),
              const SizedBox(width: 12),
              ...[0, 3, 3.5, 4, 4.5].map((r) {
                final rating = r.toDouble();
                final isSelected = _minRating == rating;
                return Padding(
                  padding: const EdgeInsets.only(right: 6),
                  child: GestureDetector(
                    onTap: () {
                      setState(() => _minRating = rating);
                      _applyFilters();
                    },
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                      decoration: BoxDecoration(
                        color: isSelected ? AppTheme.primary : AppTheme.surface,
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(
                          color: isSelected ? AppTheme.primary : AppTheme.divider,
                        ),
                      ),
                      child: Text(
                        rating == 0 ? 'All' : '${rating}+⭐',
                        style: TextStyle(
                          color: isSelected ? Colors.white : AppTheme.textPrimary,
                          fontSize: 12,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ),
                  ),
                );
              }),
              if (hasFilter) ...[
                const Spacer(),
                TextButton(
                  onPressed: _clearFilters,
                  child: const Text('Clear all', style: TextStyle(fontSize: 12, color: AppTheme.accent)),
                ),
              ],
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildResultsHeader() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Text(
        '${_doctors.length} doctors found',
        style: const TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.w600,
          color: AppTheme.textSecondary,
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return SizedBox(
      height: 300,
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.search_off, size: 64, color: AppTheme.textSecondary),
            const SizedBox(height: 16),
            const Text(
              'No doctors found',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppTheme.textPrimary),
            ),
            const SizedBox(height: 8),
            const Text(
              'Try adjusting your filters',
              style: TextStyle(fontSize: 14, color: AppTheme.textSecondary),
            ),
            const SizedBox(height: 24),
            TextButton.icon(
              onPressed: _clearFilters,
              icon: const Icon(Icons.refresh),
              label: const Text('Clear Filters'),
            ),
          ],
        ),
      ),
    );
  }
}
