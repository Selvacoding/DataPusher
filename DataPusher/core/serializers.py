from rest_framework import serializers
from .models import Account, Destination
from django.utils.crypto import get_random_string

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'email', 'account_id', 'account_name', 'app_secret_token', 'website']
    
    def create(self, validated_data):
        # Generate a random secret token
        validated_data['app_secret_token'] = get_random_string(50)
        return super().create(validated_data)

class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = ['id', 'account', 'url', 'http_method', 'headers']
