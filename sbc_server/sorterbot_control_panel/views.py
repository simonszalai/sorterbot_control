from django.http import HttpResponse
from rest_framework import viewsets
from .models import Arm, Session
from .serializers import ArmSerializer, SessionSerializer


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


class ArmViewSet(viewsets.ModelViewSet):
    queryset = Arm.objects.all()
    serializer_class = ArmSerializer


class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
