import json

from protein_prism import ProteinPrismPrior
from resonance_field import ResonanceField


def write_profile(tmp_path):
    path = tmp_path / "aqp4_resonance_profile.json"
    profile = {
        "protein": "Human Aquaporin-4 (AQP4)",
        "uniprot_accession": "P55087",
        "mean_plddt": 81.03699690402478,
        "topology_summary": {
            "total_residues": 323,
            "solidified_membrane_core_count": 204,
            "flexible_resonance_boundary_count": 37,
            "transitional_membrane_count": 16,
            "active_void_disorder_count": 66,
        },
        "residues": [],
    }
    path.write_text(json.dumps(profile), encoding="utf-8")
    return path


def test_aqp4_profile_becomes_bounded_runtime_tuning(tmp_path):
    prior = ProteinPrismPrior.from_profile_json(write_profile(tmp_path))
    tuning = prior.as_runtime_tuning()

    assert prior.total_residues == 323
    assert prior.accession == "P55087"
    assert tuning["solidified_core"] == 0.631579
    assert tuning["active_void"] == 0.204334
    assert 0.18 <= tuning["damping_gain"] <= 0.42
    assert tuning["epistemic_status"] == "alphafold_plddt_distribution_as_design_prior_not_biological_law"


def test_resonance_field_uses_protein_prism_as_prior_not_replacement(tmp_path):
    field = ResonanceField()
    field.protein_prism_prior = ProteinPrismPrior.from_profile_json(write_profile(tmp_path))
    field.orbital_hippocampus = None
    band = {
        "middle": 10.0,
        "std": 8.0,
        "upper": 26.0,
        "lower": -6.0,
        "width": 3.2,
        "current": 10.0,
    }

    canceled = field.apply_noise_canceling(band)
    equilibrium = field.get_equilibrium_state(energy=12.0, entropy=0.2, tension=0.2)

    assert canceled["noise_canceled"] is True
    assert canceled["protein_prism"]["accession"] == "P55087"
    assert canceled["gravity_dampener"] > 1.0
    assert equilibrium["protein_prism"]["accession"] == "P55087"
    assert equilibrium["hover_threshold"] > field.hover_threshold
