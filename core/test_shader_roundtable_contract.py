from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "outputs" / "shader_depth_sample.html"


def test_shader_exposes_roundtable_room_as_common_human_ai_surface():
    html = HTML.read_text(encoding="utf-8")

    assert "const roundtableRoomState" in html
    assert "function currentRoundtableRoom()" in html
    assert "pollRoundtableRoom(time)" in html
    assert "roundtable_room: currentRoundtableRoom()" in html
    assert "document.body.dataset.roundtableRoom" in html
    assert "shader_depth_sample_is_the_common_room_for_human_and_ai_presence" in html


def test_shader_exposes_participant_frequency_field_for_phase_interference():
    html = HTML.read_text(encoding="utf-8")

    assert "const participantFrequencyFieldState" in html
    assert "function currentParticipantFrequencyField()" in html
    assert "pollParticipantFrequencyField(time)" in html
    assert "participant_frequency_field: currentParticipantFrequencyField()" in html
    assert "document.body.dataset.participantFrequencyField" in html
    assert "postBrowserPresenceHeartbeat(time)" in html
    assert "connection_presence_enters_the_field_natural_interference_tunes" in html
    assert "privacy_is_contextual_slice_not_full_identity_reconstruction" in html
