from django.utils import timezone

from rest_framework import permissions, serializers, status, views, viewsets
from rest_framework.response import Response

from .models import Badge, Quest, Streak, UserAchievement, UserQuest


class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = "__all__"


class UserAchievementSerializer(serializers.ModelSerializer):
    badge = BadgeSerializer(read_only=True)

    class Meta:
        model = UserAchievement
        fields = "__all__"


class StreakSerializer(serializers.ModelSerializer):
    class Meta:
        model = Streak
        fields = ["current_streak", "longest_streak", "last_activity_date"]


class QuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quest
        fields = "__all__"


class UserQuestSerializer(serializers.ModelSerializer):
    quest = QuestSerializer(read_only=True)

    class Meta:
        model = UserQuest
        fields = [
            "id",
            "quest",
            "progress",
            "completed",
            "reward_claimed",
            "assigned_at",
            "expires_at",
        ]


class BadgeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer
    permission_classes = [permissions.AllowAny]


class MyAchievementsView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        achievements = UserAchievement.objects.filter(user=request.user)
        serializer = UserAchievementSerializer(achievements, many=True)
        return Response(serializer.data)


class MyStreakView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        streak, _ = Streak.objects.get_or_create(user=request.user)
        serializer = StreakSerializer(streak)
        return Response(serializer.data)


class MyQuestsView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        quests = UserQuest.objects.filter(
            user=request.user,
            expires_at__gte=timezone.now(),
        ).select_related("quest")
        serializer = UserQuestSerializer(quests, many=True)
        return Response(serializer.data)

    def post(self, request):
        quest_id = request.data.get("quest_id")
        try:
            user_quest = UserQuest.objects.get(
                id=quest_id,
                user=request.user,
                completed=True,
                reward_claimed=False,
            )
        except UserQuest.DoesNotExist:
            return Response(
                {"error": "Quest not found or already claimed"},
                status=status.HTTP_404_NOT_FOUND,
            )

        from apps.progress.models import XPEvent

        XPEvent.objects.create(
            user=request.user,
            source_type="milestone",
            source_id=user_quest.quest_id,
            base_points=user_quest.quest.xp_reward,
            multiplier=1.0,
            xp_delta=user_quest.quest.xp_reward,
        )
        user_quest.reward_claimed = True
        user_quest.save(update_fields=["reward_claimed"])

        return Response({"xp_awarded": user_quest.quest.xp_reward})

