from fastmcp import FastMCP
from werkbank import utils
try:
    from werkbank import mp
except ImportError:
    mp = None
try:
    from werkbank import rcsb
except ImportError:
    rcsb = None
from pathlib import Path

mcp = FastMCP("Werkbank")

FILE = Path(__file__).resolve()


@mcp.tool
def get_available_nodes() -> dict:
    """Get all available nodes sorted by package."""
    return utils.get_registered_nodes()


@mcp.tool
def get_node_info(package: str, node: str) -> dict:
    """Get information about a specific node."""
    return utils.get_node_info(package, node)

@mcp.tool
def get_node_code(package: str, node: str) -> str:
    """Get the source code of a specific node.
    
    Use only, if `get_node_info` is not sufficient.
    """
    return utils.get_node_code(package, node)


@mcp.tool
def build_workflow_instructions() -> str:
    """How to build a ZnTrack Workflow.
    
    Must read before building your first workflow!
    """
    return (FILE.parent / "resources" / "getting_started.md").read_text()


@mcp.tool(enabled=mp is not None)
def search_materials(
    elements: str | None = None,
    composition: str | None = None,
    stable_at_rt: bool = False,
    spacegroup: str | None = None,
    band_gap: str | None = None,
    max_results: int = 100,
) -> dict:
    """
    Search for materials in the Materials Project database.

    Parameters
    ----------
    elements : str or None, optional
        Comma-separated list of element symbols to filter materials by their constituent elements (e.g., "Fe,O").
    composition : str or None, optional
        Chemical composition to filter materials (e.g., "Fe2O3").
    stable_at_rt : bool, default: False
        If True, only return materials that are stable at room temperature.
    spacegroup : str or None, optional
        Space group symbol or number to filter materials by their crystallographic space group.
    band_gap : str or None, optional
        Comma-separated minimum and maximum band gap values (e.g., "1.0,3.0") to filter materials by their band gap.
    max_results : int, default: 100
        Maximum number of results to return.
    """
    return mp.search_mp(
        elements=elements.split(",") if elements else None,
        composition=composition,
        stable_at_rt=stable_at_rt,
        spacegroup=spacegroup,
        band_gap=tuple(map(float, band_gap.split(","))) if band_gap else None,
        max_results=max_results,
    )

@mcp.tool(enabled=rcsb is not None)
def search_protein_database(text: str) -> dict[str, dict]:
    """Search Protein Database (PDB)."""

    return rcsb.search_rcsb_text(text)


if __name__ == "__main__":
    mcp.run()
