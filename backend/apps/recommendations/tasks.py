from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from .engine import RecommendationEngine
from .models import OSSIssue

import requests
import logging

logger = logging.getLogger(__name__)

def generate_user_recommendations(user_id):
    try:
        user = User.objects.get(id=user_id)
        engine = RecommendationEngine(user)
        engine.generate_recommendations()
    except ObjectDoesNotExist:
        pass


def fetch_github_good_first_issues():
    """
    Simulates fetching 'good first issue' tickets from curated GitHub repositories.
    """
    curated_repos = [
        "django/django",
        "facebook/react",
        "pallets/flask"
    ]
    
    for repo in curated_repos:
        url = f"https://api.github.com/repos/{repo}/issues"
        params = {
            "state": "open",
            "labels": "good first issue",
            "per_page": 5
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                issues = response.json()
                for issue in issues:
                    if "pull_request" in issue:
                        continue
                        
                    OSSIssue.objects.update_or_create(
                        repo_name=repo,
                        issue_number=issue["number"],
                        defaults={
                            "title": issue["title"],
                            "url": issue["html_url"],
                            "labels": [label["name"] for label in issue.get("labels", [])],
                            "difficulty": "beginner",
                            "is_open": True,
                        }
                    )
            else:
                logger.warning(f"Failed to fetch issues for {repo}: {response.status_code}")
        except Exception as e:
            logger.error(f"Error fetching issues for {repo}: {e}")
