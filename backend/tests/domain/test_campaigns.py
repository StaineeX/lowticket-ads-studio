from backend.app.domain.campaigns import CampaignCopy, Platform, validate_copy


def test_reports_platform_specific_copy_limits():
    issues = validate_copy(
        Platform.GOOGLE,
        CampaignCopy(
            google_headlines=["x" * 31],
            google_descriptions=["x" * 91],
        ),
    )

    assert {issue.field for issue in issues} == {"google_headlines", "google_descriptions"}
    assert {issue.maximum for issue in issues} == {30, 90}
    assert {issue.actual for issue in issues} == {31, 91}


def test_meta_copy_accepts_normal_length_variants():
    issues = validate_copy(
        Platform.META,
        CampaignCopy(
            primary_text="Aprenda uma habilidade prática em poucos minutos.",
            headline="Comece hoje",
            description="Acesso imediato.",
            cta="Saiba mais",
        ),
    )

    assert issues == []
