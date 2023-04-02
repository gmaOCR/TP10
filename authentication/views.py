from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@api_view(['POST'])
@permission_classes(
    [
        AllowAny,
    ]
)
@api_view(['POST'])
def signup(self, request):
    serializer = self.serializer_class(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        response_data = {
            'message': 'User registered successfully',
            'user_id': user.id,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    email = request.data['email']
    password = request.data['password']
    if User.objects.filter(email=email).exists():
        user = User.objects.get(email=email)
        if user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response(
                {"refresh": str(refresh), "access": str(refresh.access_token)},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {'message': 'Invalid Password'},
                status=status.HTTP_400_BAD_REQUEST,
            )
    else:
        return Response(
            {'message': 'User Does Not Exist'},
            status=status.HTTP_400_BAD_REQUEST,
        )
