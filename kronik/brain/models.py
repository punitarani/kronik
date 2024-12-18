from enum import Enum

from pydantic import BaseModel


class TikTokCategoryEnum(Enum):
    ENTERTAINMENT = "ENTERTAINMENT"
    EDUCATION = "EDUCATION"
    LIFESTYLE = "LIFESTYLE"
    FOOD = "FOOD"
    CREATIVITY = "CREATIVITY"
    TRAVEL = "TRAVEL"
    BUSINESS_FINANCE = "BUSINESS_FINANCE"
    TECH = "TECH"
    GAMING = "GAMING"
    SPORTS = "SPORTS"
    CULTURE_HISTORY = "CULTURE_HISTORY"
    SOCIAL_ISSUES = "SOCIAL_ISSUES"
    MISC = "MISC"


class TikTokAnalysis(BaseModel):
    """TikTok Analysis"""

    transcript: str
    analysis: str
    tags: list[str]
    category: TikTokCategoryEnum
    rating: int
    like: bool
