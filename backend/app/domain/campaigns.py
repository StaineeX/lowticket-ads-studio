from dataclasses import dataclass, field
from enum import Enum


class Platform(str, Enum):
    META = "meta"
    GOOGLE = "google"


@dataclass(frozen=True)
class CampaignCopy:
    primary_text: str = ""
    headline: str = ""
    description: str = ""
    cta: str = ""
    google_headlines: list[str] = field(default_factory=list)
    google_descriptions: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ValidationIssue:
    field: str
    maximum: int
    actual: int
    message: str


LIMITS = {
    Platform.META: {
        "primary_text": 500,
        "headline": 40,
        "description": 30,
        "cta": 40,
    },
    Platform.GOOGLE: {
        "google_headlines": 30,
        "google_descriptions": 90,
    },
}


def validate_copy(platform: Platform, copy: CampaignCopy) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for field_name, maximum in LIMITS[platform].items():
        values = getattr(copy, field_name)
        if isinstance(values, str):
            values = [values] if values else []
        for value in values:
            if len(value) > maximum:
                issues.append(
                    ValidationIssue(
                        field=field_name,
                        maximum=maximum,
                        actual=len(value),
                        message=f"{field_name} exceeds {maximum} characters",
                    )
                )
    return issues
