from rest_framework import serializers
from .models import AllUser

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AllUser
        fields = [
            'full_name', 
            'email', 
            'password',
            'location', 
            'phone_number', 
            'occupation',
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        validated_data['role'] = 'user'
        validated_data['status'] = 'pending'
        
        return AllUser.objects.create_user(**validated_data)

    def validate_phone_number(self, value):
        if not value.startswith('+'):
            raise serializers.ValidationError("Phone number must start with '+'")
        if not value[1:].isdigit():
            raise serializers.ValidationError("Phone number must contain only numbers after '+'")
        return value

    def validate_occupation(self, value):
        valid_occupations = dict(AllUser.OCCUPATION_CHOICES).keys()
        if value not in valid_occupations:
            raise serializers.ValidationError(f"Occupation must be one of: {', '.join(valid_occupations)}")
        return value

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            user = AllUser.objects.get(email=data['email'])
            
            if not user.check_password(data['password']):
                raise serializers.ValidationError("Incorrect password")
            
            if user.role == 'admin':
                admin = AllUser.objects.filter(role='admin', email=data['email']).first()
                if not admin:
                    raise serializers.ValidationError("Admin user not found")
                if admin.status != 'active':
                    raise serializers.ValidationError("Admin account is not active")
            
            data['user'] = user
            return data
            
        except AllUser.DoesNotExist:
            raise serializers.ValidationError("You are not registered. Please sign up.")

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AllUser
        fields = [
            'id',
            'full_name',
            'email',
            'location',
            'phone_number',
            'occupation',
            'role',
            'status',
            'registration_date',
            'updated_at'
        ]
        read_only_fields = ['id', 'email', 'status', 'registration_date', 'updated_at']

    def validate_phone_number(self, value):
        if not value.startswith('+'):
            raise serializers.ValidationError("Phone number must start with '+'")
        if not value[1:].isdigit():
            raise serializers.ValidationError("Phone number must contain only numbers after '+'")
        return value

    def validate_occupation(self, value):
        valid_occupations = dict(AllUser.OCCUPATION_CHOICES).keys()
        if value not in valid_occupations:
            raise serializers.ValidationError(f"Occupation must be one of: {', '.join(valid_occupations)}")
        return value

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AllUser
        fields = [
            'id',
            'full_name',
            'email',
            'location',
            'phone_number',
            'occupation',
            'status',
            'registration_date'
        ]
