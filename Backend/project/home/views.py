from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import ClintReview
from .serializers import  ReviewSerializer
from rest_framework import generics

from .permissions import IsAuthenticatedWithJWT
class ReviewListCreateView(IsAuthenticatedWithJWT,generics.ListCreateAPIView):
    queryset = ClintReview.objects.all()
    serializer_class = ReviewSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)  # تعيين المستخدم تلقائيًا



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
from .serializers import ContactSerializer

class ContactUsView(APIView):
    
    def post(self, request):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            # Extract validated data
            name = serializer.validated_data['name']
            email = serializer.validated_data['email']
            phone = serializer.validated_data.get('phone', 'Not provided')
            message = serializer.validated_data['message']

            # Prepare email
            subject = f"New Contact Us Submission from {name}"
            email_body = f"Name: {name}\nEmail: {email}\nPhone: {phone}\n\nMessage:\n{message}"
            recipient_list = [settings.EMAIL_HOST_USER]  # Your Gmail

            try:
                send_mail(subject, email_body, settings.EMAIL_HOST_USER, recipient_list, fail_silently=False)
                return Response({"message": "Email sent successfully"}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
