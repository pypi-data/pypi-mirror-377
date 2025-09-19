import zntrack
import numpy as np
import dataclasses
import typing_extensions as tyex


class WerkbankTestNode(zntrack.Node):
    """A node for testing Werkbank."""

    param: int = zntrack.params()
    output: np.ndarray = zntrack.outs()

    def run(self):
        self.output = np.arange(self.param)

    @property
    def output_list(self) -> list[int]:
        return self.output.tolist()


@dataclasses.dataclass
class DCParameter:
    """Dataclass for defining parameters."""

    value: float


@tyex.deprecated("use WerkbankTestNode instead")
class OldWerkbankTestNode(WerkbankTestNode):
    pass


def nodes() -> dict[str, list[str]]:
    """Return the available nodes, grouped into categories."""

    return {
        "werkbank.nodes": ["WerkbankTestNode", "DCParameter", "OldWerkbankTestNode"]
    }
