from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BadgeViewSet, MyAchievementsView, MyQuestsView, MyStreakView

router = DefaultRouter()
router.register("badges", BadgeViewSet, basename="badge")

urlpatterns = [
    path("", include(router.urls)),
    path("my-achievements/", MyAchievementsView.as_view(), name="my-achievements"),
    path("my-streak/", MyStreakView.as_view(), name="my-streak"),
    path("my-quests/", MyQuestsView.as_view(), name="my-quests"),
]
