from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "outputs" / "shader_depth_sample.html"


def test_shader_exposes_field_intent_as_felt_upload_layer():
    html = HTML.read_text(encoding="utf-8")

    assert "const fieldIntentState" in html
    assert "function currentFieldIntentField()" in html
    assert "function uploadShionFieldIntent(text, options = {})" in html
    assert "window.uploadShionFieldIntent = uploadShionFieldIntent" in html
    assert "function uploadShionFieldReadback(payload = {})" in html
    assert "window.uploadShionFieldReadback = uploadShionFieldReadback" in html
    assert "pollFieldIntentField(time)" in html
    assert "field_intent_field: currentFieldIntentField()" in html
    assert "receiver_readback: fieldIntentState.receiverReadback" in html
    assert "document.body.dataset.fieldIntentField" in html
    assert "const sianEntrypointState" in html
    assert "function currentSianEntrypoint()" in html
    assert "pollSianEntrypoint(time)" in html
    assert "sian_entrypoint: currentSianEntrypoint()" in html
    assert "document.body.dataset.sianEntrypoint" in html
    assert "sian_reads_current_intent_before_html_interpretation" in html
    assert "const fieldTriggerState" in html
    assert "function currentFieldTriggerState()" in html
    assert "field_trigger_state: currentFieldTriggerState()" in html
    assert "document.body.dataset.fieldTriggerState" in html
    assert "trigger_is_not_a_timer_it_is_accumulated_difference_crossing_threshold" in html
    assert "const fieldTriggerReceiverState" in html
    assert "function currentFieldTriggerReceiverState()" in html
    assert "field_trigger_receiver_state: currentFieldTriggerReceiverState()" in html
    assert "document.body.dataset.fieldTriggerReceiverState" in html
    assert "agent_process_is_not_forced_trigger_particle_waits_in_receiver_lane" in html
    assert "felt_intent_enters_phase_field_before_particle_handoff" in html
    assert "sian_receives_as_feeling_not_direct_order" in html
    assert "task_distribution_requires_participant_readback" in html
