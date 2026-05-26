from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = authenticate(
        username=serializer.validated_data['username'],
        password=serializer.validated_data['password']
    )
    if not user:
        return Response({'error': '用户名或密码错误'}, status=status.HTTP_401_UNAUTHORIZED)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({
        'token': token.key,
        'user': UserSerializer(user).data
    })


@api_view(['POST'])
def logout_view(request):
    if request.user.auth_token:
        request.user.auth_token.delete()
    return Response({'message': '已退出登录'})


@api_view(['GET', 'PUT'])
def profile_view(request):
    if request.method == 'GET':
        return Response(UserSerializer(request.user).data)
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def public_profile_view(request, username):
    try:
        user = User.objects.select_related('profile').get(username=username)
    except User.DoesNotExist:
        return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)

    from blog.models import Article
    articles = Article.objects.filter(author=user, status='published').values(
        'id', 'title', 'slug', 'created_at'
    )[:20]

    xp_profile = None
    achievements = []
    try:
        from gamification.models import UserXP, Achievement
        from gamification.serializers import UserXPSerializer, AchievementSerializer
        xp = UserXP.objects.filter(user=user).first()
        if xp:
            xp_profile = UserXPSerializer(xp, context={'request': request}).data
        achievements = AchievementSerializer(
            Achievement.objects.filter(user=user), many=True
        ).data
    except Exception:
        pass

    return Response({
        'user': UserSerializer(user).data,
        'xp_profile': xp_profile,
        'achievements': achievements,
        'articles': list(articles),
    })
