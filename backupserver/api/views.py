from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import File, Key
from .serializers import FileSerializer, KeySerializer

# ------------------------------------ #
# Services to be called by Logs Server #
# ------------------------------------ #


@api_view(['GET'])
def backup_data(request):
    pass

# ------------------------------------- #
# Services to be called by Files Server #
# ------------------------------------- #


@api_view(['GET'])
def get_data(request):
    pass
