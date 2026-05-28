from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

User = get_user_model()


class CustomObtainAuthToken(ObtainAuthToken):
    """Custom token authentication that returns user data along with token."""
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user': {
                'id': user.pk,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        })


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Handle user login with username/email and password.
    Returns a token for authenticated users.
    """
    username = request.data.get('username') or request.data.get('email')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'detail': 'Username and password are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Try to find user by email if username doesn't work
    user = authenticate(request, username=username, password=password)
    
    if user is None:
        # Try finding by email
        try:
            user = User.objects.get(email=username)
            user = authenticate(request, username=user.username, password=password)
        except User.DoesNotExist:
            user = None
    
    if user is not None:
        token, created = Token.objects.get_or_create(user=user)
        login(request, user)
        
        return Response({
            'token': token.key,
            'user': {
                'id': user.pk,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        })
    
    return Response(
        {'detail': 'Invalid credentials.'},
        status=status.HTTP_401_UNAUTHORIZED
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    Handle user registration.
    """
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not username or not email or not password:
        return Response(
            {'detail': 'Username, email, and password are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if User.objects.filter(username=username).exists():
        return Response(
            {'detail': 'Username already exists.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if User.objects.filter(email=email).exists():
        return Response(
            {'detail': 'Email already exists.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )
    
    token, created = Token.objects.get_or_create(user=user)
    
    return Response({
        'token': token.key,
        'user': {
            'id': user.pk,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Handle user logout. Deletes the auth token.
    """
    try:
        request.user.auth_token.delete()
    except:
        pass
    
    logout(request)
    
    return Response({'detail': 'Successfully logged out.'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    """
    Get current authenticated user's information.
    """
    user = request.user
    
    return Response({
        'id': user.pk,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token_view(request):
    """
    Refresh token endpoint.
    For simplicity, we'll return the same token if valid.
    """
    # Since we're using token auth, the token doesn't expire
    # This endpoint is for compatibility with frontend
    token_key = request.data.get('refresh') or request.data.get('token')
    
    if not token_key:
        return Response(
            {'detail': 'Token is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        token = Token.objects.get(key=token_key)
        return Response({
            'token': token.key,
            'user': {
                'id': token.user.pk,
                'username': token.user.username,
                'email': token.user.email,
                'first_name': token.user.first_name,
                'last_name': token.user.last_name,
            }
        })
    except Token.DoesNotExist:
        return Response(
            {'detail': 'Invalid token.'},
            status=status.HTTP_401_UNAUTHORIZED
        )