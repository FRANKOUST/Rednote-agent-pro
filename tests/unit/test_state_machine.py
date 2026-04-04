from app.domain.models import ContentDraftStatus, PublishJobStatus, transition_draft_status


def test_review_flow_requires_sequential_draft_transitions() -> None:
    status = transition_draft_status(ContentDraftStatus.CREATED, "generate")
    assert status == ContentDraftStatus.GENERATED

    status = transition_draft_status(status, "submit_for_review")
    assert status == ContentDraftStatus.REVIEW_PENDING

    status = transition_draft_status(status, "approve")
    assert status == ContentDraftStatus.APPROVED

    status = transition_draft_status(status, "mark_publish_ready")
    assert status == ContentDraftStatus.PUBLISH_READY


def test_publish_job_terminal_states_are_marked_terminal() -> None:
    assert PublishJobStatus.PUBLISHED.is_terminal is True
    assert PublishJobStatus.FAILED.is_terminal is True
    assert PublishJobStatus.QUEUED.is_terminal is False
