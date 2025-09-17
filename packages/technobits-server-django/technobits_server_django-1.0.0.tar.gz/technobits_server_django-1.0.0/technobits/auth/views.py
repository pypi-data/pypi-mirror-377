"""
Authentication Views for Technobits Library
"""

import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.contrib.auth.models import User
from django.utils import timezone

from .serializers import (
    RegisterSerializer, LoginSerializer, GoogleLoginSerializer,
    UserSerializer, ForgotPasswordSerializer, ResetPasswordSerializer,
    ChangePasswordSerializer
)
from .utils import JWTCookieHelper, PasswordHelper, RequestHelper
from .services import AuthService

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def RegisterView(request):
    """Register a new user"""
    serializer = RegisterSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        try:
            user = serializer.save()
            
            # Create response with user data
            user_serializer = UserSerializer(user)
            response = Response({
                'user': user_serializer.data,
                'message': 'User registered successfully'
            }, status=status.HTTP_201_CREATED)
            
            # Set JWT cookies
            response = JWTCookieHelper.set_jwt_cookies(response, user)
            
            logger.info(f"User registered successfully: {user.email}")
            return response
            
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return Response({
                'error': 'Registration failed. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def LoginView(request):
    """Login user with email and password"""
    serializer = LoginSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        try:
            user = serializer.validated_data['user']
            
            # Create response with user data
            user_serializer = UserSerializer(user)
            response = Response({
                'user': user_serializer.data,
                'message': 'Login successful'
            }, status=status.HTTP_200_OK)
            
            # Set JWT cookies
            response = JWTCookieHelper.set_jwt_cookies(response, user)
            
            logger.info(f"User logged in successfully: {user.email}")
            return response
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return Response({
                'error': 'Login failed. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def GoogleLoginView(request):
    """Login or register user with Google credential"""
    serializer = GoogleLoginSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            user = serializer.validated_data['user']
            
            # Log the login attempt
            request_info = RequestHelper.get_request_info(request)
            AuthService.authenticate_user(
                user.email, None, 
                request_info['ip_address'], 
                request_info['user_agent']
            )
            
            # Create response with user data
            user_serializer = UserSerializer(user)
            response = Response({
                'user': user_serializer.data,
                'message': 'Google login successful'
            }, status=status.HTTP_200_OK)
            
            # Set JWT cookies
            response = JWTCookieHelper.set_jwt_cookies(response, user)
            
            logger.info(f"Google login successful: {user.email}")
            return response
            
        except Exception as e:
            logger.error(f"Google login error: {str(e)}")
            return Response({
                'error': 'Google login failed. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def RefreshTokenView(request):
    """Refresh JWT tokens using refresh token from cookies"""
    access_token, refresh_token = JWTCookieHelper.get_tokens_from_cookies(request)
    
    if not refresh_token:
        return Response({
            'error': 'Refresh token not found'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        # Validate and refresh the token
        refresh = RefreshToken(refresh_token)
        user = refresh.user
        
        response = Response({
            'message': 'Token refreshed successfully'
        }, status=status.HTTP_200_OK)
        
        # Set new JWT cookies
        response = JWTCookieHelper.set_jwt_cookies(response, user)
        
        logger.info(f"Token refreshed for user: {user.email}")
        return response
        
    except (TokenError, InvalidToken) as e:
        logger.warning(f"Token refresh failed: {str(e)}")
        return Response({
            'error': 'Invalid refresh token'
        }, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return Response({
            'error': 'Token refresh failed'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def MeView(request):
    """Get current authenticated user information"""
    serializer = UserSerializer(request.user)
    return Response({
        'user': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def LogoutView(request):
    """Logout user and clear JWT cookies"""
    try:
        # Get refresh token from cookies
        access_token, refresh_token = JWTCookieHelper.get_tokens_from_cookies(request)
        
        if refresh_token:
            # Blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        logger.info(f"User logged out: {request.user.email}")
    
    except Exception as e:
        # Log error but don't fail logout
        logger.warning(f"Error blacklisting token during logout: {str(e)}")
    
    response = Response({
        'message': 'Logout successful'
    }, status=status.HTTP_200_OK)
    
    # Clear JWT cookies
    response = JWTCookieHelper.clear_jwt_cookies(response)
    
    return response


@api_view(['POST'])
@permission_classes([AllowAny])
def ForgotPasswordView(request):
    """Send password reset email to user"""
    serializer = ForgotPasswordSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email, is_active=True)
            
            # Generate reset token
            reset_token = PasswordHelper.generate_reset_token(user)
            
            # Create reset URL (configurable base URL)
            from django.conf import settings
            base_url = getattr(settings, 'TECHNOBITS_FRONTEND_URL', 'http://localhost:3000')
            reset_url = f"{base_url}/reset-password?token={reset_token}"
            
            # Send email using SendInBlue service
            try:
                from ..email.services import EmailService
                email_service = EmailService()
                
                user_name = user.get_full_name() or user.first_name or user.email.split('@')[0]
                
                email_sent = email_service.send_password_reset_email(
                    to_email=email,
                    to_name=user_name,
                    reset_token=reset_token,
                    reset_url=reset_url
                )
                
                if email_sent:
                    logger.info(f"Password reset email sent to {email}")
                else:
                    logger.error(f"Failed to send password reset email to {email}")
                    
            except ImportError:
                # Fallback: log the reset URL for development
                logger.info(f"Password reset URL for {email}: {reset_url}")
            except Exception as e:
                logger.error(f"Email service error: {str(e)}")
                
        except User.DoesNotExist:
            # Don't reveal whether email exists for security
            logger.info(f"Password reset requested for non-existent email: {email}")
        
        # Always return success message for security
        return Response({
            'message': 'If an account with that email exists, password reset instructions have been sent.'
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def ResetPasswordView(request):
    """Reset user password with token"""
    serializer = ResetPasswordSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        try:
            user = serializer.validated_data['user']
            new_password = serializer.validated_data['password']
            
            # Set new password
            user.set_password(new_password)
            user.save()
            
            logger.info(f"Password reset successful for user {user.email}")
            
            return Response({
                'message': 'Password has been reset successfully. You can now log in with your new password.'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Password reset error: {str(e)}")
            return Response({
                'error': 'Password reset failed. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ChangePasswordView(request):
    """Change user password"""
    serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        try:
            user = serializer.save()
            
            logger.info(f"Password changed for user: {user.email}")
            
            return Response({
                'message': 'Password changed successfully.'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Password change error: {str(e)}")
            return Response({
                'error': 'Password change failed. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def HealthView(request):
    """Health check endpoint"""
    return Response({
        'status': 'OK',
        'message': 'Technobits Auth service is running',
        'timestamp': timezone.now().isoformat(),
        'version': '1.0.0'
    }, status=status.HTTP_200_OK)

