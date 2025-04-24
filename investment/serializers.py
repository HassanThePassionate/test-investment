from rest_framework import serializers
from .models import Property, PropertyDocument, PropertyPhoto

class PropertyPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyPhoto
        fields = ['id', 'image', 'uploaded_at', 'order']
        read_only_fields = ['uploaded_at']

class PropertyDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyDocument
        fields = ['id', 'document_type', 'file', 'uploaded_at']
        read_only_fields = ['uploaded_at']

class PropertySerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)
    is_public = serializers.BooleanField(read_only=True)
    photos = PropertyPhotoSerializer(many=True, read_only=True)
    documents = PropertyDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = Property
        fields = [
            'id', 'status', 'is_public', 'created_at', 'updated_at',
            'country', 'district', 'county', 'parish', 'city',
            'street', 'number_or_lot', 'floor_or_apartment', 'postal_code',
            'property_type', 'number_of_rooms', 'gross_area', 'construction_year',
            'condition', 'has_garage', 'has_elevator', 'has_air_conditioning',
            'has_private_garden', 'has_private_pool', 'has_storage',
            'has_basement', 'has_terrace',
            'urgent_sale', 'estimated_value',
            'contact_name', 'contact_surname', 'contact_email', 'contact_phone',
            'observations', 'how_found', 'marketing_consent', 'terms_accepted',
            'photos', 'documents'
        ]
        read_only_fields = ['created_at', 'updated_at', 'id']

    def validate_postal_code(self, value):
        if value:
            import re
            if not re.match(r'^\d{4}-\d{3}$', value):
                raise serializers.ValidationError("Postal code must be in the format ####-###")
        return value

    def validate(self, data):
        if self.context['request'].method == 'POST':
            if not data.get('terms_accepted'):
                raise serializers.ValidationError({
                    "terms_accepted": "You must accept the terms and conditions"
                })

        if 'estimated_value' in data and data['estimated_value'] <= 0:
            raise serializers.ValidationError({
                "estimated_value": "Estimated value must be greater than 0"
            })

        return data
