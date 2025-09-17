from .alloy_compositions import alloy_compositions
from .types import Alloy

from tc.schema.composition import Composition


def get_alloy_composition(alloy: Alloy) -> Composition:
    """
    Returns (element_list, weight_fractions_dict) for a known alloy, normalized to sum=1.0.
    """
    compositions = alloy_compositions()
    composition = compositions.get(alloy.value)

    if composition is not None:

        out: dict[str, float] = {}
        for k, v in composition.items():
            if k in ("", None):
                continue
            out[k] = float(v)

        out = {k: v for k, v in out.items() if v and v > 0.0}
        total = sum(out.values())

        # If looks like percent, normalize from 100; otherwise from sum
        if abs(total - 100.0) < 1e-6:
            fractions = {el: wt / 100.0 for el, wt in out.items()}
        else:
            fractions = {el: wt / total for el, wt in out.items()}
        fractions = dict(sorted(fractions.items(), key=lambda kv: kv[1], reverse=True))
        return Composition(**fractions)

    else:
        raise ValueError(f"No numeric composition fields found for '{alloy}'.")
