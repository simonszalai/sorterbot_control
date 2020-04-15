from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import viewsets, status
from django.views.decorators.http import require_http_methods
from .models import Arm, Session, UI
from .serializers import ArmSerializer, SessionSerializer, UISerializer


@require_http_methods(["GET"])
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


@require_http_methods(["GET"])
def arm_checkin(request):
    return HttpResponse("Checked in")


class ArmViewSet(viewsets.ModelViewSet):
    queryset = Arm.objects.all()
    serializer_class = ArmSerializer


class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer


class UIViewSet(viewsets.ModelViewSet):
    queryset = UI.objects.all()
    serializer_class = UISerializer

    def create(self, request):
        """
        Explicitly provide primary key (id) so the entry is updated, instead of a new being added

        """

        new_ui = UI(id=request.data["id"], cloud_status=request.data["cloud_status"])
        new_ui.save()
        return Response(request.data, status=status.HTTP_201_CREATED)
