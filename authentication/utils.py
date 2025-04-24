import jwt
import random
import string

from rest_framework import authentication, exceptions 
from django.conf import settings

from django.core.cache import cache
from django.core.mail import send_mail

from .models import Auth


def generate_otp():
    otp = ''.join(random.choices(string.digits, k=6))  
    return otp

def send_otp_email(email, otp):
    subject = 'Your OTP for Registration'
    message = f'Your OTP is {otp}. Please use it to complete your registration.'
    send_mail(subject, message, settings.EMAIL_HOST_USER, [email])

def store_data_in_cache(email, username, password, otp):
    cache.set(email, {'username': username, 'password': password, 'otp': otp}, timeout=300) 

class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_data = authentication.get_authorization_header(request).decode('utf-8')

        if not auth_data or not auth_data.startswith('Bearer '):
            return None

        token = auth_data.split(' ')[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = Auth.objects.filter(email=payload['email']).first()

            if user is None:
                raise exceptions.AuthenticationFailed('User not found')
            return (user, None)

        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token expired')

        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token')


def generate_jwt_token(useremail):
    payload = {
        'email': useremail
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token    

def auth_by_token(request):
    try:
        jwt_auth= JWTAuthentication()
        auth= jwt_auth.authenticate(request)
        if auth:
            return auth[0]
        else:
            return None
    except exceptions.AuthenticationFailed:
        return exceptions.AuthenticationFailed