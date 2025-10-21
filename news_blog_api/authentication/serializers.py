from django.contrib.auth import user_logged_in
from rest_framework import serializers
from django.contrib.auth.models import User
import re


class RegistrationSerializer(serializers.ModelSerializer):
    password_check = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=8, max_length=128)
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'password_check']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email вже використовується")

        email_rules = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_rules, value):
            raise serializers.ValidationError("Невірний формат email")
        return value

    def validate_password(self, value):
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Потрібна велика літера")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Потрібна мала літера")
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Потрібна цифра")
        return value
    def create(self, validated_data):
        validated_data.pop('password_check')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=validated_data['password']
        )
        return user