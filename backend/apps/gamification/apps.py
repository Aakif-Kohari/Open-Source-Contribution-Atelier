from django.apps import AppConfig


class GamificationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.gamification"

    def ready(self):
        import apps.gamification.signals  # noqa: F401

        try:
            from django_q.models import Schedule

            Schedule.objects.get_or_create(
                name="assign-daily-quests",
                defaults={
                    "func": "apps.gamification.tasks.assign_daily_quests",
                    "schedule_type": Schedule.DAILY,
                },
            )
            Schedule.objects.get_or_create(
                name="expire-old-quests",
                defaults={
                    "func": "apps.gamification.tasks.expire_old_quests",
                    "schedule_type": Schedule.DAILY,
                },
            )
        except Exception:
            pass

        self.seed_default_quests()

    @staticmethod
    def seed_default_quests():
        from .models import Quest

        defaults = [
            {
                "title": "Lesson Learner",
                "description": "Complete 3 lessons today",
                "quest_type": "complete_lessons",
                "frequency": "daily",
                "requirement_count": 3,
                "xp_reward": 100,
            },
            {
                "title": "XP Hunter",
                "description": "Earn 200 XP today",
                "quest_type": "earn_xp",
                "frequency": "daily",
                "requirement_count": 200,
                "xp_reward": 80,
            },
            {
                "title": "Streak Keeper",
                "description": "Maintain your learning streak",
                "quest_type": "maintain_streak",
                "frequency": "daily",
                "requirement_count": 1,
                "xp_reward": 50,
            },
            {
                "title": "Quiz Master",
                "description": "Complete 2 quizzes today",
                "quest_type": "complete_quiz",
                "frequency": "daily",
                "requirement_count": 2,
                "xp_reward": 75,
            },
            {
                "title": "Weekly Warrior",
                "description": "Complete 10 lessons this week",
                "quest_type": "complete_lessons",
                "frequency": "weekly",
                "requirement_count": 10,
                "xp_reward": 500,
            },
            {
                "title": "XP Champion",
                "description": "Earn 1000 XP this week",
                "quest_type": "earn_xp",
                "frequency": "weekly",
                "requirement_count": 1000,
                "xp_reward": 400,
            },
            {
                "title": "Challenge Conqueror",
                "description": "Complete a challenge today",
                "quest_type": "complete_challenge",
                "frequency": "daily",
                "requirement_count": 1,
                "xp_reward": 120,
            },
            {
                "title": "Sandbox Explorer",
                "description": "Use the sandbox 2 times today",
                "quest_type": "use_sandbox",
                "frequency": "daily",
                "requirement_count": 2,
                "xp_reward": 60,
            },
            {
                "title": "Badge Collector",
                "description": "Earn 2 badges this week",
                "quest_type": "earn_badge",
                "frequency": "weekly",
                "requirement_count": 2,
                "xp_reward": 350,
            },
            {
                "title": "Review Helper",
                "description": "Review 3 peer submissions this week",
                "quest_type": "review_pr",
                "frequency": "weekly",
                "requirement_count": 3,
                "xp_reward": 300,
            },
        ]
        for quest_data in defaults:
            Quest.objects.get_or_create(
                title=quest_data["title"],
                defaults=quest_data,
            )
