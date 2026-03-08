from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import NutriUser, UserProfile, DailyLog, AIInsight, FoodItem

class NutriTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Allow both 'email' or 'username' in the request for flexibility
        if 'email' in attrs:
            attrs[self.username_field] = attrs.get('email')
        return super().validate(attrs)

class FoodItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodItem
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = NutriUser
        fields = ['id', 'email', 'username', 'password', 'language', 'country', 'onboarding_completed', 'role', 'registered_by']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        email = validated_data.get('email', '').lower().strip()
        validated_data['email'] = email
        user = NutriUser(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['full_name', 'age', 'gender', 'height', 'weight', 'activity_level', 'goal', 'region', 'preferred_language', 'medical_conditions', 'phone_number', 'district', 'muac_cm', 'whz_score']

class DailyLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyLog
        fields = '__all__'
        read_only_fields = ['user']

class AIInsightSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIInsight
        fields = '__all__'
