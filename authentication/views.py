from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from rest_framework_simplejwt.tokens import RefreshToken
from .models import AllUser
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserListSerializer
)

class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'

class UserViewSet(viewsets.ModelViewSet):
    queryset = AllUser.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['register', 'login']:
            return [AllowAny()]
        elif self.action in ['list_users', 'list', 'update_user_status', 'delete_user']:
            return [IsAdminUser()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'register':
            return UserRegistrationSerializer
        elif self.action == 'login':
            return UserLoginSerializer
        elif self.action in ['list_users', 'list']:
            return UserListSerializer
        return UserProfileSerializer

    def list(self, request, *args, **kwargs):
        users = AllUser.objects.filter(role='user')
        serializer = self.get_serializer(users, many=True)
        return Response({
            'message': 'Users retrieved successfully',
            'users': serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'User registered successfully',
                'user': UserProfileSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Check if user status is active
            if user.status != 'active':
                return Response({
                    'error': 'Your account is not active.'
                }, status=status.HTTP_403_FORBIDDEN)
                
            token = RefreshToken.for_user(user).access_token
            return Response({
                'message': 'Login successful',
                'id': user.id,
                'email': user.email,
                'role': user.role,
                'status': user.status,
                'token': str(token)
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token = RefreshToken.for_user(user).access_token
            return Response({
                'message': 'Login successful',
                'id': user.id,
                'email': user.email,
                'role': user.role,
                'status': user.status,
                'token': str(token)
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get', 'put', 'patch'])
    def profile(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
            
        partial = request.method == 'PATCH'
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=partial
        )
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Profile updated successfully',
                'user': serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'])
    def update_user_status(self, request, pk=None):
        try:
            user = AllUser.objects.get(pk=pk, role='user')
            new_status = request.data.get('status')
            
            if new_status not in ['active', 'cancel']:
                return Response({
                    'error': 'Invalid status. Must be either "active" or "cancel"'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user.status = new_status
            user.save()
            
            return Response({
                'message': f'User status updated successfully to {new_status}',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'full_name': user.full_name,
                    'status': user.status
                }
            }, status=status.HTTP_200_OK)
            
        except AllUser.DoesNotExist:
            return Response({
                'error': 'User not found or is not a regular user'
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['delete'])
    def delete_user(self, request, pk=None):
        try:
            user = AllUser.objects.get(pk=pk)
            
            if user.role == 'admin':
                return Response({
                    'error': 'Cannot delete admin users'
                }, status=status.HTTP_403_FORBIDDEN)
            
            user.delete()
            
            return Response({
                'message': 'User deleted successfully'
            }, status=status.HTTP_200_OK)
            
        except AllUser.DoesNotExist:
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        return Response(
            {"message": "Method not allowed"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def update(self, request, *args, **kwargs):
        return Response(
            {"message": "Method not allowed"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def destroy(self, request, *args, **kwargs):
        return Response(
            {"message": "Method not allowed"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )