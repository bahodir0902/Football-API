from rest_framework import serializers
from accounts.models import User, Address
from django.contrib.auth.models import Group


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', "first_name", "last_name", "email", "date_joined"]
        extra_kwargs = {
            "id": {"read_only": True},
            "date_joined": {"read_only": True}
        }


class RegisterUserSerializer(serializers.ModelSerializer):
    re_password = serializers.CharField(max_length=255)

    class Meta:
        model = User
        fields = ['first_name', "last_name", "email", "password", "re_password"]
        extra_kwargs = {
            "password": {"write_only": True},
            "re_password": {"write_only": True}
        }

    def validate(self, attrs):
        password = attrs.get('password')
        re_password = attrs.pop('re_password', None)
        email = attrs.get("email")

        if not password or not re_password:
            raise serializers.ValidationError("Passwords didn\'t entered fully.")

        if str(password) != str(re_password):
            raise serializers.ValidationError("Passwords don\'t match")

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(f"User with {email} already exists in database!")
        return attrs

    def create(self, validated_data):
        password = validated_data.get('password')
        user = User.objects.create_user(
            **validated_data
        )

        user_group, _ = Group.objects.get_or_create(name='Users')
        user.groups.add(user_group)

        user.set_password(password)
        user.save()
        return user


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', "address_line_1", "address_line_2", "city", "state_or_province",
                  "country"
                  ]
        extra_kwargs = {
            "id": {"read_only": True}
        }

