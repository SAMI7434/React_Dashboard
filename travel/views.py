from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from travel.models import (
    NavanApiConfig, SyncedUser, Booking, ImportLog
)
from travel.serializers import (
    NavanApiConfigSerializer, SyncedUserSerializer,
    BookingSerializer, BookingListSerializer, ImportLogSerializer,
    DashboardAnalyticsSerializer, MonthlyBookingTrendSerializer,
    BookingStatusDistributionSerializer, DepartmentSpendSerializer,
    RegionBookingsSerializer
)
from travel.services import (
    NavanUserService, NavanTripImportService
)


class NavanApiConfigViewSet(viewsets.ModelViewSet):
    queryset = NavanApiConfig.objects.all()
    serializer_class = NavanApiConfigSerializer
    permission_classes = [IsAuthenticated]


class SyncedUserViewSet(viewsets.ModelViewSet):
    queryset = SyncedUser.objects.all()
    serializer_class = SyncedUserSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'department', 'region', 'policy_level']
    search_fields = ['email', 'first_name', 'last_name', 'full_name', 'employee_id']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Apply filters
        department = self.request.query_params.get('department')
        region = self.request.query_params.get('region')
        policy_level = self.request.query_params.get('policy_level')
        status = self.request.query_params.get('status')
        
        if department:
            queryset = queryset.filter(department=department)
        if region:
            queryset = queryset.filter(region=region)
        if policy_level:
            queryset = queryset.filter(policy_level=policy_level)
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def sync(self, request):
        """Trigger user sync from Navan API"""
        try:
            service = NavanUserService()
            result = service.sync_users()
            
            if result.get('success'):
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def departments(self, request):
        """Get list of unique departments"""
        departments = self.queryset.values_list('department', flat=True).distinct().exclude(department__isnull=True).exclude(department='')
        return Response(list(departments))
    
    @action(detail=False, methods=['get'])
    def regions(self, request):
        """Get list of unique regions"""
        regions = self.queryset.values_list('region', flat=True).distinct().exclude(region__isnull=True).exclude(region='')
        return Response(list(regions))


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return BookingListSerializer
        return BookingSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Apply filters
        booking_type = self.request.query_params.get('booking_type')
        status = self.request.query_params.get('status')
        user_email = self.request.query_params.get('user_email')
        is_out_of_policy = self.request.query_params.get('is_out_of_policy')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        region = self.request.query_params.get('region')
        
        if booking_type:
            queryset = queryset.filter(booking_type=booking_type)
        if status:
            queryset = queryset.filter(status=status)
        if user_email:
            queryset = queryset.filter(user_email__icontains=user_email)
        if is_out_of_policy is not None:
            queryset = queryset.filter(is_out_of_policy=is_out_of_policy == 'true')
        if start_date:
            queryset = queryset.filter(booking_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(booking_date__lte=end_date)
        if region:
            queryset = queryset.filter(region=region)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def booking_types(self, request):
        """Get list of unique booking types"""
        booking_types = self.queryset.values_list('booking_type', flat=True).distinct()
        return Response(list(booking_types))
    
    @action(detail=False, methods=['get'])
    def regions(self, request):
        """Get list of unique regions"""
        regions = self.queryset.values_list('region', flat=True).distinct().exclude(region__isnull=True).exclude(region='')
        return Response(list(regions))


class ImportLogViewSet(viewsets.ModelViewSet):
    queryset = ImportLog.objects.all()
    serializer_class = ImportLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        import_type = self.request.query_params.get('import_type')
        status = self.request.query_params.get('status')
        
        if import_type:
            queryset = queryset.filter(import_type=import_type)
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset


class TravelDashboardViewSet(viewsets.ViewSet):
    """ViewSet for travel dashboard analytics"""
    permission_classes = [IsAuthenticated]
    
    def analytics(self, request):
        """Get dashboard analytics data"""
        now = timezone.now()
        current_month_start = now.replace(day=1)
        
        # User analytics
        total_synced_users = SyncedUser.objects.count()
        active_users = SyncedUser.objects.filter(status='active').count()
        
        # Booking analytics
        total_trips = Booking.objects.count()
        flights = Booking.objects.filter(booking_type='flight').count()
        hotels = Booking.objects.filter(booking_type='hotel').count()
        rental_cars = Booking.objects.filter(booking_type='car').count()
        rail_bookings = Booking.objects.filter(booking_type='rail').count()
        black_car_bookings = Booking.objects.filter(booking_type='black_car').count()
        
        # Monthly spend
        monthly_spend = Booking.objects.filter(
            booking_date__gte=current_month_start
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Out of policy trips
        out_of_policy_trips = Booking.objects.filter(is_out_of_policy=True).count()
        
        serializer = DashboardAnalyticsSerializer({
            'total_synced_users': total_synced_users,
            'active_users': active_users,
            'total_trips': total_trips,
            'flights': flights,
            'hotels': hotels,
            'rental_cars': rental_cars,
            'rail_bookings': rail_bookings,
            'black_car_bookings': black_car_bookings,
            'monthly_travel_spend': monthly_spend,
            'out_of_policy_trips': out_of_policy_trips
        })
        
        return Response(serializer.data)
    
    def monthly_trend(self, request):
        """Get monthly booking trend"""
        months = Booking.objects.annotate(
            month=TruncMonth('booking_date')
        ).values('month').annotate(
            booking_count=Count('id'),
            total_amount=Sum('amount')
        ).order_by('-month')[:12]
        
        serializer = MonthlyBookingTrendSerializer(months, many=True)
        return Response(serializer.data)
    
    def status_distribution(self, request):
        """Get booking status distribution"""
        total = Booking.objects.count()
        if total == 0:
            return Response([])
        
        status_counts = Booking.objects.values('status').annotate(
            count=Count('id')
        )
        
        result = []
        for item in status_counts:
            result.append({
                'status': item['status'],
                'count': item['count'],
                'percentage': round((item['count'] / total) * 100, 2)
            })
        
        serializer = BookingStatusDistributionSerializer(result, many=True)
        return Response(serializer.data)
    
    def department_spend(self, request):
        """Get department-wise travel spend"""
        # Get departments from synced users
        department_spend = Booking.objects.values(
            'user_email'
        ).annotate(
            total_spend=Sum('amount'),
            booking_count=Count('id')
        )
        
        # Join with user data to get department
        results = []
        for item in department_spend:
            user = SyncedUser.objects.filter(email=item['user_email']).first()
            if user and user.department:
                results.append({
                    'department': user.department,
                    'total_spend': item['total_spend'],
                    'booking_count': item['booking_count']
                })
        
        # Aggregate by department
        dept_totals = {}
        for item in results:
            dept = item['department']
            if dept not in dept_totals:
                dept_totals[dept] = {'total_spend': 0, 'booking_count': 0}
            dept_totals[dept]['total_spend'] += item['total_spend']
            dept_totals[dept]['booking_count'] += item['booking_count']
        
        serializer = DepartmentSpendSerializer([
            {'department': dept, 'total_spend': data['total_spend'], 'booking_count': data['booking_count']}
            for dept, data in dept_totals.items()
        ], many=True)
        
        return Response(serializer.data)
    
    def region_bookings(self, request):
        """Get region-wise bookings"""
        region_data = Booking.objects.values('region').annotate(
            booking_count=Count('id'),
            total_amount=Sum('amount')
        ).exclude(region__isnull=True).exclude(region='')
        
        serializer = RegionBookingsSerializer(region_data, many=True)
        return Response(serializer.data)
    
    def booking_type_comparison(self, request):
        """Get booking type comparison"""
        type_data = Booking.objects.values('booking_type', 'booking_type_display').annotate(
            count=Count('id'),
            total_amount=Sum('amount')
        )
        
        return Response(list(type_data))
    
    def recent_imports(self, request):
        """Get recent import logs"""
        recent_logs = ImportLog.objects.all()[:10]
        serializer = ImportLogSerializer(recent_logs, many=True)
        return Response(serializer.data)


class ImportViewSet(viewsets.ViewSet):
    """ViewSet for triggering imports"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def sync_users(self, request):
        """Trigger user sync"""
        try:
            service = NavanUserService()
            result = service.sync_users()
            
            if result.get('success'):
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def import_bookings(self, request):
        """Trigger booking import"""
        try:
            start_date = request.data.get('start_date')
            end_date = request.data.get('end_date')
            
            service = NavanTripImportService()
            result = service.import_trips(start_date, end_date)
            
            if result.get('success'):
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def daily_reconciliation(self, request):
        """Trigger daily reconciliation"""
        try:
            service = NavanTripImportService()
            result = service.daily_reconciliation()
            
            if result.get('success'):
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)