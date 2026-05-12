import pytest
from app.domain.topic import Topic, TopicStatus


def _make_topic(**overrides) -> Topic:
    defaults = dict(
        id="abc",
        name="Atomic Structure",
        slug="atomic-structure",
        domain="chemistry",
        status=TopicStatus.AVAILABLE,
        explanation_level=1,
        content_ready=False,
        description="Atoms.",
        complexity=3,
    )
    return Topic(**{**defaults, **overrides})


# ── open ──────────────────────────────────────────────────────────────────────

def test_open_available_topic_transitions_to_in_progress():
    topic = _make_topic(status=TopicStatus.AVAILABLE)
    topic.open()
    assert topic.status == TopicStatus.IN_PROGRESS


def test_open_locked_topic_raises():
    topic = _make_topic(status=TopicStatus.LOCKED)
    with pytest.raises(ValueError, match="available"):
        topic.open()


def test_open_already_in_progress_raises():
    topic = _make_topic(status=TopicStatus.IN_PROGRESS)
    with pytest.raises(ValueError):
        topic.open()


# ── master ────────────────────────────────────────────────────────────────────

def test_master_in_progress_topic_transitions_to_mastered():
    topic = _make_topic(status=TopicStatus.IN_PROGRESS)
    topic.master()
    assert topic.status == TopicStatus.MASTERED


def test_master_available_topic_raises():
    topic = _make_topic(status=TopicStatus.AVAILABLE)
    with pytest.raises(ValueError, match="in_progress"):
        topic.master()


def test_master_locked_topic_raises():
    topic = _make_topic(status=TopicStatus.LOCKED)
    with pytest.raises(ValueError):
        topic.master()


# ── unlock ────────────────────────────────────────────────────────────────────

def test_unlock_locked_topic_transitions_to_available():
    topic = _make_topic(status=TopicStatus.LOCKED)
    topic.unlock()
    assert topic.status == TopicStatus.AVAILABLE


def test_unlock_available_topic_raises():
    topic = _make_topic(status=TopicStatus.AVAILABLE)
    with pytest.raises(ValueError, match="locked"):
        topic.unlock()


# ── escalate_explanation ──────────────────────────────────────────────────────

def test_escalate_from_level_1_to_2():
    topic = _make_topic(explanation_level=1)
    topic.escalate_explanation()
    assert topic.explanation_level == 2


def test_escalate_from_level_2_to_3():
    topic = _make_topic(explanation_level=2)
    topic.escalate_explanation()
    assert topic.explanation_level == 3


def test_escalate_at_max_level_raises():
    topic = _make_topic(explanation_level=3)
    with pytest.raises(ValueError, match="maximum"):
        topic.escalate_explanation()


def test_full_state_machine_sequence():
    topic = _make_topic(status=TopicStatus.LOCKED)
    topic.unlock()
    assert topic.status == TopicStatus.AVAILABLE
    topic.open()
    assert topic.status == TopicStatus.IN_PROGRESS
    topic.master()
    assert topic.status == TopicStatus.MASTERED
