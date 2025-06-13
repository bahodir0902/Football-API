from rest_framework import serializers
from football.models import FootballField
from accounts.serializers import AddressSerializer
from accounts.models import Address


class FootballFieldSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    class Meta:
        model = FootballField
        fields = ['id', "name", "owner", "address", "contact", "price", "image", "area", "viewers_capacity"]
        extra_kwargs = {
            "id": {"read_only": True},
            "address": {"required": False}
        }

    def create(self, validated_data):
        address = validated_data.pop("address")
        address = Address.objects.create(
            **address
        )
        field = FootballField.objects.create(
            **validated_data,
            address=address
        )
        return field

    def update(self, instance, validated_data):
        if "address" in validated_data:
            address_data = validated_data.pop("address")

            for attr, value in address_data.items():
                setattr(instance.address, attr, value)
            instance.address.save()

        for atts, value in validated_data.items():
            setattr(instance, atts, value)
        instance.save()
        return instance



