import os
import time
import uuid
from django.core.validators import FileExtensionValidator
from django.db import models
from accounts.models import User, Address
from django.core.exceptions import ValidationError


def positive_number_of_viewers_capacity(value):
    if value < 0:
        raise ValidationError("Number of viewsers should be greater than 0")
    return value


def validate_image_size(image):
    max_size = 4 * 1024 * 1024
    if image.size > max_size:
        raise ValidationError('Image size can\'t exceed 4 MB.')


def unique_image_path(instance, filename):
    ext = filename.split('.')[-1]
    unique_filename = f"{int(time.time())}_{uuid.uuid4().hex}.{ext}"
    return str(os.path.join('fields_images/', unique_filename))


class FootballField(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Football_fields')
    address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name="Football_fields")
    contact = models.CharField(max_length=255, null=True, blank=True)
    price = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    area = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    viewers_capacity = models.IntegerField(default=0, validators=[positive_number_of_viewers_capacity])
    image = models.ImageField(
        upload_to=unique_image_path,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']), validate_image_size],
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "Football Fields"
        verbose_name = "Football Field"
        verbose_name_plural = "Football Fields"

    def __str__(self):
        return f"{self.name} - {self.address.city} - {self.address.address_line_1} belonging to {self.owner.first_name} - {self.owner.email}"

