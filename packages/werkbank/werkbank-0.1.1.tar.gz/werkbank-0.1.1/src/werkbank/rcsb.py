from typing import Any
from rcsbapi.search import TextQuery

import requests


def fetch_rcsb_titles(pdb_ids: list[str]) -> dict[str, dict[str, Any]]:
    """
    Fetch struct.title for given PDB IDs using the RCSB REST API.
    """
    results = {}
    for pdb_id in pdb_ids:
        url = f"https://data.rcsb.org/rest/v1/core/entry/{pdb_id}"
        r = requests.get(url)
        if r.status_code == 200:
            data = r.json()
            title = data.get("struct", {}).get("title")
            results[pdb_id] = {"title": title}
        else:
            results[pdb_id] = {"title": None}
    return results


def search_rcsb_text(query: str, max_results: int = 10) -> dict[str, dict[str, Any]]:
    """
    Search RCSB PDB for a text query and return entry metadata.

    Parameters
    ----------
    query : str
        Free-text search query (e.g., "insulin", "hemoglobin").
    max_results : int
        Maximum number of results to return.

    Returns
    -------
    dict[str, dict[str, Any]]
        Mapping from PDB ID to metadata dictionary,
        e.g. {"1Z3I": {"title": "Human insulin"}}
    """
    # Step 1: run text search
    q = TextQuery(query)
    pdb_ids = []
    for identifier in q():
        pdb_ids.append(identifier)
        if len(pdb_ids) >= max_results:
            break

    if not pdb_ids:
        return {}

    return fetch_rcsb_titles(pdb_ids)