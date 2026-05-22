from resonance_field import ResonanceField


class FakeHippocampus:
    def __init__(self, experiences, embodiment_ratio=0.0):
        self.data = {
            "experiences": experiences,
            "proton": {"embodiment_ratio": embodiment_ratio},
        }


def test_earth_core_gravity_uses_density_not_raw_count():
    field = ResonanceField()
    field.orbital_hippocampus = FakeHippocampus(
        experiences=[
            {"level": 0, "binding_energy": 1.0},
            {"level": 1, "binding_energy": 0.618034},
            {"level": 3, "binding_energy": 0.236068},
            {"level": 4, "binding_energy": 0.145898},
        ],
        embodiment_ratio=0.05,
    )

    gravity = field.get_earth_core_gravity()

    assert 0.1 < gravity < 3.0
    assert gravity == 1.516


def test_band_width_to_entropy_clamps_relative_width():
    field = ResonanceField()

    assert field.band_width_to_entropy(0.0) == 0.0
    assert field.band_width_to_entropy(1.0) == 0.5
    assert field.band_width_to_entropy(3.0) == 0.75


def test_noise_canceling_recomputes_width_after_gravity_damping():
    field = ResonanceField()
    field.orbital_hippocampus = FakeHippocampus(
        experiences=[
            {"level": 0, "binding_energy": 1.0},
            {"level": 1, "binding_energy": 0.618034},
            {"level": 4, "binding_energy": 0.145898},
        ],
        embodiment_ratio=0.05,
    )
    band = {
        "middle": 10.0,
        "std": 8.0,
        "upper": 26.0,
        "lower": -6.0,
        "width": 3.2,
        "current": 10.0,
    }

    canceled = field.apply_noise_canceling(band)

    assert canceled["noise_canceled"] is True
    assert canceled["std"] < 8.0
    assert canceled["width"] == (canceled["upper"] - canceled["lower"]) / canceled["middle"]
    assert canceled["gravity_dampener"] > 1.0


def test_equilibrium_clamps_entropy_for_force_terms():
    field = ResonanceField()
    field.orbital_hippocampus = FakeHippocampus(
        experiences=[{"level": 0, "binding_energy": 1.0}],
        embodiment_ratio=0.0,
    )

    state = field.get_equilibrium_state(energy=12.0, entropy=3.0, tension=0.2)

    assert state["earth_core_gravity"] > 0.1
    assert state["net_force"] >= 0.0
    assert state["description"] in {"Zone 2: Core Gravity Hovering", "Active Orbital Shift"}
