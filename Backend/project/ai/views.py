from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
import os
from .ai_model import predict_disease  # Import your AI model function
from .permissions import IsAuthenticatedWithJWT  # Import your custom permission

class PredictViewSet(IsAuthenticatedWithJWT,viewsets.ViewSet):
    parser_classes = [MultiPartParser, FormParser]  # Allow file uploads

    def create(self, request):
        if "image" in request.FILES:
            image = request.FILES["image"]
            image_path = os.path.join("media/ai", image.name)

            # Save the uploaded image
            with open(image_path, "wb+") as destination:
                for chunk in image.chunks():
                    destination.write(chunk)

            # Run AI prediction
            result = predict_disease(image_path)

            return Response(result, status=status.HTTP_200_OK)

        return Response({"error": "No image provided"}, status=status.HTTP_400_BAD_REQUEST)
