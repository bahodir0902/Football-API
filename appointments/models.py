from django.db import models
from accounts.models import User
from football.models import FootballField


class Appointment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="appointments")
    field = models.ForeignKey(FootballField, on_delete=models.CASCADE, related_name="appointments")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, default=0)

    class Meta:
        db_table = "Appointments"

    def __str__(self):
        return f"{self.user.first_name} - {self.user.email} - {self.field.name} from {self.start_time} to {self.end_time}"

