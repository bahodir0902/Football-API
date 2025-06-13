from datetime import timedelta
from django.utils import timezone
from rest_framework import serializers
from appointments.models import Appointment
import decimal

class AppointmentSerializer(serializers.ModelSerializer):
    field_name = serializers.CharField(source='field.name', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    duration_hours = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = ['id', 'user', 'field', 'start_time', 'end_time',
                  'field_name', 'user_name', 'duration_hours']
        extra_kwargs = {
            "id": {"read_only": True}
        }

    def get_duration_hours(self, obj):
        duration = obj.end_time - obj.start_time
        return round(duration.total_seconds() / 3600, 2)

    def validate(self, data):
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        field = data.get('field')
        user = data.get('user')

        if start_time >= end_time:
            raise serializers.ValidationError("End time must be after start time.")

        if start_time < timezone.now():
            raise serializers.ValidationError("Cannot book appointments in the past.")

        existing_appointments = Appointment.objects.filter(
            field=field,
            start_time__lt=end_time,
            end_time__gt=start_time
        )

        if self.instance:
            existing_appointments = existing_appointments.exclude(id=self.instance.id)

        if existing_appointments.exists():
            raise serializers.ValidationError("This time slot conflicts with an existing appointment.")

        return data

    def create(self, validated_data):
        start_time = validated_data.get('start_time')
        end_time = validated_data.get('end_time')
        field = validated_data.get('field')

        duration = end_time - start_time
        total_hours = duration.total_seconds() / 3600
        total_cost = decimal.Decimal(float(total_hours)) * field.price

        validated_data['total_cost'] = round(total_cost, 3)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        start_time = validated_data.get('start_time', instance.start_time)
        end_time = validated_data.get('end_time', instance.end_time)
        field = validated_data.get('field', instance.field)

        duration = end_time - start_time
        total_hours = duration.total_seconds() / 3600
        total_cost = decimal.Decimal(float(total_hours)) * field.price
        validated_data['total_cost'] = round(total_cost, 3)
        return super().update(instance, validated_data)


class FieldAvailabilitySerializer(serializers.Serializer):
    field_id = serializers.IntegerField()
    date = serializers.DateField()
    start_time = serializers.TimeField(required=False)
    end_time = serializers.TimeField(required=False)
