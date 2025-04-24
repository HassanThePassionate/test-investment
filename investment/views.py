from django.shortcuts import render
from django.db import models, transaction
from django.db.models import Count
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import Property, PropertyPhoto, PropertyDocument
from .serializers import PropertySerializer, PropertyPhotoSerializer, PropertyDocumentSerializer


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'

class PropertyViewSet(viewsets.ModelViewSet):
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def get_queryset(self):

        user = self.request.user
        if user.role == 'admin':
            return Property.objects.all()
        
        return Property.objects.filter(
            models.Q(user=user) |  
            models.Q(is_public=True, status='active')  
        ).distinct()

    @transaction.atomic
    def create(self, request, *args, **kwargs):

        property_data = request.data.dict() if hasattr(request.data, 'dict') else request.data.copy()
        photos = request.FILES.getlist('photos', [])
        documents = request.FILES.getlist('documents', [])
        
        property_data.pop('photos', None)
        property_data.pop('documents', None)

        serializer = self.get_serializer(data=property_data)
        if serializer.is_valid():
            property_instance = serializer.save(
                user=self.request.user,
                status='active' if self.request.user.role == 'admin' else 'pending',
                is_public=True if self.request.user.role == 'admin' else False
            )

            for index, photo in enumerate(photos):
                PropertyPhoto.objects.create(
                    property=property_instance,
                    image=photo,
                    order=index
                )

            for doc in documents:
                PropertyDocument.objects.create(
                    property=property_instance,
                    file=doc
                )

            updated_serializer = self.get_serializer(property_instance)
            return Response({
                'message': 'Property created successfully',
                'data': updated_serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'message': 'Error creating property',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], permission_classes=[IsAdminUser])
    def update_status(self, request, pk=None):

        property_instance = self.get_object()
        
        new_status = None
        if isinstance(request.data, dict):
            new_status = request.data.get('status')
        else:
            new_status = request.data.dict().get('status')

        if not new_status:
            return Response({
                'message': 'Status field is required',
                'valid_status': [choice[0] for choice in Property.STATUS_CHOICES]
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if new_status not in [choice[0] for choice in Property.STATUS_CHOICES]:
            return Response({
                'message': 'Invalid status value',
                'valid_status': [choice[0] for choice in Property.STATUS_CHOICES]
            }, status=status.HTTP_400_BAD_REQUEST)
        
        property_instance.status = new_status
        property_instance.is_public = (new_status == 'active')
        property_instance.save()
        
        return Response({
            'message': f'Property status updated to {new_status}',
            'data': self.get_serializer(property_instance).data
        })

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser])
    def add_photos(self, request, pk=None):

        property_instance = self.get_object()
        photos = request.FILES.getlist('photos', [])
        
        if not photos:
            return Response({
                'message': 'No photos provided'
            }, status=status.HTTP_400_BAD_REQUEST)

        last_order = property_instance.photos.order_by('-order').first()
        start_order = (last_order.order + 1) if last_order else 0

        new_photos = []
        for index, photo in enumerate(photos, start=start_order):
            new_photo = PropertyPhoto.objects.create(
                property=property_instance,
                image=photo,
                order=index
            )
            new_photos.append(new_photo)

        serializer = PropertyPhotoSerializer(new_photos, many=True)
        return Response({
            'message': f'{len(photos)} photos added successfully',
            'data': serializer.data
        })

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser])
    def add_documents(self, request, pk=None):

        property_instance = self.get_object()
        documents = request.FILES.getlist('documents', [])
        
        if not documents:
            return Response({
                'message': 'No documents provided'
            }, status=status.HTTP_400_BAD_REQUEST)

        new_documents = []
        for doc in documents:
            new_doc = PropertyDocument.objects.create(
                property=property_instance,
                file=doc
            )
            new_documents.append(new_doc)

        serializer = PropertyDocumentSerializer(new_documents, many=True)
        return Response({
            'message': f'{len(documents)} documents added successfully',
            'data': serializer.data
        })

    @action(detail=True, methods=['delete'], permission_classes=[IsAdminUser])
    def delete_property(self, request, pk=None):
        property_instance = self.get_object()
        
        try:
            property_instance.delete()
            return Response({
                'message': 'Property deleted successfully'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'message': 'Error deleting property',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def public_properties(self, request):

        properties = Property.objects.filter(
            status='active',
            is_public=True
        )
        
        serializer = self.get_serializer(properties, many=True)
        return Response({
            'message': 'Public properties retrieved successfully',
            'count': properties.count(),
            'data': serializer.data
        })

    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def properties_by_status(self, request):
        # Get all properties
        properties = Property.objects.all()
        return Response({
            'properties': self.get_serializer(properties, many=True).data
        })