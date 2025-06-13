from datetime import datetime, time, timedelta
from django.contrib.auth.models import Group
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from appointments.serializers import AppointmentSerializer, FieldAvailabilitySerializer
from appointments.models import Appointment
from football.models import FootballField
from appointments.permissions import IsAppointmentOwner


class AppointmentViewSet(ModelViewSet):
    serializer_class = AppointmentSerializer
    queryset = Appointment.objects.all()

    def get_permissions(self):
        if self.action in ['destroy']:
            return [IsAppointmentOwner()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        queryset = Appointment.objects.select_related("field", "user")

        admin_group, _ = Group.objects.get_or_create(name='Admins')
        if user.groups.all().first() != admin_group:
            queryset = queryset.filter(user=user)

        field_id = self.request.query_params.get("field_id")
        date = self.request.query_params.get("date")
        upcoming = self.request.query_params.get("upcoming")

        if field_id:
            queryset = queryset.filter(field_id=field_id)

        if date:
            try:
                filter_date = datetime.strptime(date, '%d-%m-%Y').date()
                queryset = queryset.filter(
                    start_time__date=filter_date
                )
            except ValueError:
                pass
        if upcoming and upcoming.lower() == 'true':
            queryset = queryset.filter(start_time__gte=timezone.now())

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(methods=['get'], detail=False, url_path="my-appointments")
    def my_appointments(self, request):
        upcoming = request.query_params.get("upcoming")
        appointments = Appointment.objects.filter(user=request.user)

        if upcoming and upcoming.lower() == 'true':
            appointments = appointments.filter(start_time__gte=timezone.now())

        appointments.order_by('created_at')
        serializer = self.get_serializer(appointments, many=True)

        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='check-availability')
    def check_availability(self, request):
        serializer = FieldAvailabilitySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        field_id = serializer.validated_data['field_id']
        date = serializer.validated_data['date']
        start_time = serializer.validated_data.get('start_time')
        end_time = serializer.validated_data.get('end_time')

        try:
            field = FootballField.objects.get(id=field_id)
        except FootballField.DoesNotExist:
            return Response({'error': 'Field not found'}, status=status.HTTP_404_NOT_FOUND)

        if start_time and end_time:
            start_datetime = timezone.make_aware(
                datetime.combine(date, start_time)
            )
            end_datetime = timezone.make_aware(
                datetime.combine(date, end_time)
            )

            conflicts = Appointment.objects.filter(
                field=field,
                start_time__lt=end_datetime,
                end_time__gt=start_datetime
            )

            return Response({
                'available': not conflicts.exists(),
                'conflicts': conflicts.count()
            })

        day_start = timezone.make_aware(datetime.combine(date, time.min))
        day_end = timezone.make_aware(datetime.combine(date, time.max))

        appointments = Appointment.objects.filter(
            field=field,
            start_time__gte=day_start,
            start_time__lte=day_end
        ).order_by('start_time')

        busy_slots = []
        for appointment in appointments:
            busy_slots.append({
                'start_time': appointment.start_time,
                'end_time': appointment.end_time,
                'user': appointment.user.get_full_name() if appointment.user.get_full_name() else appointment.user.email
            })

        return Response({
            'field_name': field.name,
            'date': date,
            'busy_slots': busy_slots
        })

    @action(detail=False, methods=['get'], url_path='available-slots')
    def available_slots(self, request):
        field_id = request.query_params.get('field_id')
        date_str = request.query_params.get('date')
        duration = request.query_params.get('duration', '1')

        if not field_id or not date_str:
            return Response(
                {'error': 'field_id and date are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            field = FootballField.objects.get(id=field_id)
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            duration_hours = float(duration)
        except (FootballField.DoesNotExist, ValueError):
            return Response(
                {'error': 'Invalid field_id, date format, or duration'},
                status=status.HTTP_400_BAD_REQUEST
            )

        day_start = timezone.make_aware(datetime.combine(date, time(6, 0)))
        day_end = timezone.make_aware(datetime.combine(date, time(22, 0)))

        appointments = Appointment.objects.filter(
            field=field,
            start_time__date=date
        ).order_by('start_time')

        available_slots = []
        current_time = day_start

        for appointment in appointments:
            if current_time + timedelta(hours=duration_hours) <= appointment.start_time:
                slot_end = min(appointment.start_time, day_end)
                if current_time + timedelta(hours=duration_hours) <= slot_end:
                    available_slots.append({
                        'start_time': current_time,
                        'end_time': appointment.start_time,
                        'duration_hours': (appointment.start_time - current_time).total_seconds() / 3600
                    })

            current_time = max(current_time, appointment.end_time)

        if current_time + timedelta(hours=duration_hours) <= day_end:
            available_slots.append({
                'start_time': current_time,
                'end_time': day_end,
                'duration_hours': (day_end - current_time).total_seconds() / 3600
            })

        suitable_slots = []
        for slot in available_slots:
            slot_duration = slot['duration_hours']
            if slot_duration >= duration_hours:
                slot_start = slot['start_time']
                slot_end = slot['end_time']

                while slot_start + timedelta(hours=duration_hours) <= slot_end:
                    suitable_slots.append({
                        'start_time': slot_start,
                        'end_time': slot_start + timedelta(hours=duration_hours),
                        'duration_hours': duration_hours
                    })
                    slot_start += timedelta(minutes=60)

        return Response({
            'field_name': field.name,
            'date': date,
            'requested_duration': duration_hours,
            'available_slots': suitable_slots[:20]
        })
