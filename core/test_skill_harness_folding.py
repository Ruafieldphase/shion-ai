from skill_harness_folding import FieldConditions, SkillResidue, fold_skill_harness, pair_bond_strength


def test_pair_bond_strength_reads_overlap_phase_frequency_and_resonance():
    left = SkillResidue(
        name="sense",
        resonance=0.8,
        phase=0.35,
        keywords=["field", "observe", "rhythm"],
        frequency_range=(200.0, 320.0),
    )
    right = SkillResidue(
        name="digest",
        resonance=0.75,
        phase=0.4,
        keywords=["field", "rhythm", "memory"],
        frequency_range=(240.0, 360.0),
    )

    assert pair_bond_strength(left, right) > 0.65


def test_fold_skill_harness_prefers_contextual_fold_over_boundary_judgment():
    skills = [
        {
            "name": "observe_field",
            "resonance": 0.82,
            "phase": 0.3,
            "experience": 12,
            "atp_cost": 3,
            "keywords": ["field", "observe", "rhythm"],
            "frequency_range": (180.0, 300.0),
        },
        {
            "name": "force_publish",
            "resonance": 0.7,
            "phase": 0.85,
            "experience": 1,
            "atp_cost": 18,
            "keywords": ["publish", "external", "claim"],
            "frequency_range": (1200.0, 1600.0),
        },
    ]
    field = FieldConditions(
        core_gravity=1.5,
        phase_noise=0.1,
        action_pressure=0.2,
        silence_need=0.15,
        observer_resistance=0.05,
        available_atp=35.0,
    )

    folded = fold_skill_harness(skills, field, intent_keywords=["field", "rhythm"])

    assert folded["principle"] == "pattern_correspondence_before_boundary_judgment"
    assert folded["harness_state"]["dominant_residue"] == "observe_field"
    assert folded["residues"][0]["state"] in {"folded_domain_candidate", "partial_fold"}
    assert folded["residues"][0]["intent_fit"] > folded["residues"][1]["intent_fit"]


def test_misfold_pressure_becomes_chaperone_pause_not_prohibition():
    skills = [
        {
            "name": "high_pressure_action",
            "resonance": 0.9,
            "phase": 0.5,
            "experience": 0,
            "atp_cost": 15,
            "keywords": ["action"],
            "frequency_range": (900.0, 1400.0),
        }
    ]
    field = FieldConditions(
        core_gravity=0.2,
        phase_noise=0.9,
        action_pressure=0.9,
        silence_need=0.7,
        observer_resistance=0.8,
        available_atp=10.0,
    )

    folded = fold_skill_harness(skills, field)

    assert folded["harness_state"]["readiness"] == "hold_and_refold"
    assert folded["residues"][0]["misfold"]["posture"] == "chaperone_pause"
    assert folded["residues"][0]["misfold"]["meaning"] == "forced_activation_pressure"


def test_potential_residues_participate_in_folding_score_calculations():
    from skill_harness_folding import PotentialResidue

    skills = [
        {
            "name": "observe_field",
            "resonance": 0.8,
            "phase": 0.3,
            "experience": 10,
            "atp_cost": 3,
            "keywords": ["field", "observe"],
            "frequency_range": (180.0, 300.0),
        }
    ]
    potentials = [
        PotentialResidue(
            name="potential_resonance",
            resonance=0.4,
            phase=0.35,
            keywords=["resonance", "observe", "field"],
            source_context="dialogue_unresolved_node",
        )
    ]
    field = FieldConditions(core_gravity=0.5, available_atp=30.0)

    folded = fold_skill_harness(
        skills,
        field,
        intent_keywords=["field", "resonance"],
        potential_residues=potentials,
    )

    # schema should be v2 now
    assert folded["schema"] == "skill_harness_folding.v2"
    # Unified list contains both formal and potential residues
    residues_map = {item["name"]: item for item in folded["residues"]}
    assert "observe_field" in residues_map
    assert "potential_resonance" in residues_map

    # Metadata check
    assert residues_map["potential_resonance"]["is_potential"] is True
    assert residues_map["potential_resonance"]["source_context"] == "dialogue_unresolved_node"
    assert residues_map["observe_field"]["is_potential"] is False

    # Check if they co-fold
    assert residues_map["potential_resonance"]["folding_score"] > 0.0


def test_unnamed_residues_extracted_from_potential_text():
    skills = [
        {
            "name": "observe_field",
            "resonance": 0.8,
            "keywords": ["field"],
        }
    ]
    # Dialogue fragment containing natural patterns
    dialogue_text = "이것은 중력(gravity)과 공명(resonance)을 통해 구조를 접어(folding)나가는 유기적인 흐름입니다."
    field = FieldConditions(core_gravity=0.5, available_atp=30.0)

    folded = fold_skill_harness(
        skills,
        field,
        intent_keywords=["field", "resonance"],
        potential_text=dialogue_text,
    )

    residues_map = {item["name"]: item for item in folded["residues"]}
    
    # Unnamed potential residues should be sampled and extracted from the dialogue text
    assert "potential_gravity" in residues_map
    assert "potential_resonance" in residues_map
    assert "potential_folding" in residues_map

    assert residues_map["potential_gravity"]["is_potential"] is True
    assert residues_map["potential_gravity"]["source_context"] == "dialogue"

