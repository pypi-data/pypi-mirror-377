from mp_api.client import MPRester
        
def search_mp(
    elements: list[str] | None = None,
    composition: str | None = None,
    stable_at_rt: bool = False,
    spacegroup: str | None = None,
    band_gap: tuple[float, float] | None = None,
    max_results: int = 100,
) -> dict:
    fields = ["material_id", "formula_pretty", "band_gap"]

    with MPRester() as mpr:
        filters = {}

        if elements:
            filters["elements"] = elements
        if composition:
            filters["formula"] = composition
        if spacegroup:
            filters["spacegroup_symbol"] = spacegroup
        if band_gap:
            filters["band_gap"] = band_gap
        if stable_at_rt:
            # Approximate stability criterion
            filters["energy_above_hull"] = (0, 0.05)

        results = mpr.materials.summary.search(fields=fields, **filters)
    
    return {
        mat.material_id: {
            "formula": mat.formula_pretty,
            "band_gap": mat.band_gap,
            "energy_above_hull": mat.energy_above_hull,
        }
        for mat in results[:max_results]
    }
