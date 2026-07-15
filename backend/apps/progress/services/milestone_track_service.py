import datetime
from django.db import transaction
from django.utils import timezone
from django.db.models import Sum

from apps.progress.models import (
    Season,
    TrackMilestone,
    UserMilestoneCompletion,
    LessonProgress,
    ExerciseAttempt,
    XPEvent,
    UserBadge,
    Badge,
)

class MilestoneTrackService:
    @staticmethod
    def get_active_season(user) -> Season | None:
        today = timezone.localdate()
        return Season.objects.filter(
            is_active=True,
            start_date__lte=today,
            end_date__gte=today
        ).first()

    @staticmethod
    def get_active_season_multiplier(user, activity_type: str) -> float:
        today = timezone.localdate()
        active_season = Season.objects.filter(
            is_active=True,
            start_date__lte=today,
            end_date__gte=today
        ).first()
        if active_season and active_season.boost_activity_type == activity_type:
            return active_season.xp_boost_multiplier
        return 1.0

    @staticmethod
    def calculate_progress(user, milestone: TrackMilestone) -> int:
        from django.utils.timezone import make_aware
        import datetime as dt_module

        season = milestone.season
        start_dt = make_aware(dt_module.datetime.combine(season.start_date, dt_module.time.min))
        end_dt = make_aware(dt_module.datetime.combine(season.end_date, dt_module.time.max))

        if milestone.activity_type == "lesson":
            return LessonProgress.objects.filter(
                user=user,
                completed=True,
                updated_at__range=(start_dt, end_dt)
            ).count()

        elif milestone.activity_type == "exercise":
            return ExerciseAttempt.objects.filter(
                user=user,
                is_correct=True,
                created_at__range=(start_dt, end_dt)
            ).count()

        elif milestone.activity_type == "xp":
            xp_sum = XPEvent.objects.filter(
                user=user,
                created_at__range=(start_dt, end_dt)
            ).exclude(
                source_type__in=["badge", "milestone"]
            ).aggregate(total=Sum("xp_delta"))["total"]
            return xp_sum or 0

        return 0

    @staticmethod
    def evaluate_milestones(user):
        from apps.notifications.signals import create_and_push_notification

        today = timezone.localdate()
        active_seasons = Season.objects.filter(
            is_active=True,
            start_date__lte=today,
            end_date__gte=today
        )

        for season in active_seasons:
            completed_ids = UserMilestoneCompletion.objects.filter(
                user=user, milestone__season=season
            ).values_list("milestone_id", flat=True)

            incomplete_milestones = season.milestones.exclude(id__in=completed_ids).order_by("target_value")

            for milestone in incomplete_milestones:
                progress = MilestoneTrackService.calculate_progress(user, milestone)
                if progress >= milestone.target_value:
                    with transaction.atomic():
                        completion, created = UserMilestoneCompletion.objects.select_for_update().get_or_create(
                            user=user,
                            milestone=milestone
                        )
                        if created:
                            # Award badge if one is configured
                            if milestone.badge:
                                UserBadge.objects.get_or_create(
                                    user=user,
                                    badge=milestone.badge
                                )
                                try:
                                    create_and_push_notification(
                                        recipient=user,
                                        notif_type="badge",
                                        title="🏆 Badge Unlocked!",
                                        message=f"You unlocked milestone badge: {milestone.badge.name}",
                                        meta={
                                            "badge_slug": milestone.badge.slug,
                                            "icon": milestone.badge.icon_asset_url,
                                        },
                                    )
                                except Exception:
                                    pass

                            # Award XP boost if configured
                            if milestone.xp_boost > 0:
                                XPEvent.objects.create(
                                    user=user,
                                    source_type="milestone",
                                    source_id=milestone.id,
                                    base_points=milestone.xp_boost,
                                    multiplier=1.0,
                                    xp_delta=milestone.xp_boost,
                                )

    @staticmethod
    def get_user_active_track_status(user) -> dict | None:
        today = timezone.localdate()
        active_season = Season.objects.filter(
            is_active=True,
            start_date__lte=today,
            end_date__gte=today
        ).first()
        if not active_season:
            return None

        completed_ids = UserMilestoneCompletion.objects.filter(
            user=user, milestone__season=active_season
        ).values_list("milestone_id", flat=True)

        milestones = active_season.milestones.all().order_by("target_value")
        completed_count = len(completed_ids)
        total_count = milestones.count()

        return {
            "season_name": active_season.name,
            "season_description": active_season.description,
            "xp_boost_multiplier": active_season.xp_boost_multiplier,
            "boost_activity_type": active_season.boost_activity_type,
            "completed_milestones_count": completed_count,
            "total_milestones_count": total_count,
        }

    @staticmethod
    def get_user_next_milestone(user) -> dict | None:
        today = timezone.localdate()
        active_season = Season.objects.filter(
            is_active=True,
            start_date__lte=today,
            end_date__gte=today
        ).first()
        if not active_season:
            return None

        completed_ids = UserMilestoneCompletion.objects.filter(
            user=user, milestone__season=active_season
        ).values_list("milestone_id", flat=True)

        milestones = active_season.milestones.all().order_by("target_value")
        next_milestone = milestones.exclude(id__in=completed_ids).first()

        if not next_milestone:
            return None

        progress = MilestoneTrackService.calculate_progress(user, next_milestone)

        return {
            "id": next_milestone.id,
            "name": next_milestone.name,
            "description": next_milestone.description,
            "activity_type": next_milestone.activity_type,
            "target_value": next_milestone.target_value,
            "current_value": progress,
            "xp_boost": next_milestone.xp_boost,
            "badge_name": next_milestone.badge.name if next_milestone.badge else None,
            "badge_slug": next_milestone.badge.slug if next_milestone.badge else None,
            "badge_icon_url": next_milestone.badge.icon_asset_url if next_milestone.badge else None,
        }
