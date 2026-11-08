"""AFP external resource file (.res) reader.

A .res file is a resource group (BRG .. ERG) that holds named resources, each
wrapped in a Begin/End Resource pair (BRS .. ERS).  The resource name is the
first 8 bytes of the BRS data; the kind of resource follows from its content:

* a **page overlay** contains BMO .. EMO
  [mo-dca-reference-mixed-object-document-content-architecture-reference p.181],
* a **page segment** contains BPS .. EPS
  [mo-dca-reference-mixed-object-document-content-architecture-reference p.199].
"""

from __future__ import annotations

from dataclasses import dataclass, field

from afp_render.afpstream import read_structures


@dataclass
class Resource:
    """One named resource taken from a .res file."""

    kind: str                     # "overlay" or "page segment"
    name: str
    structures: list = field(default_factory=list)


def parse_resource_file(path: str) -> dict[str, Resource]:
    """Return the resources of a .res file, keyed by name."""
    with open(path, "rb") as fh:
        buf = fh.read()
    structures = read_structures(buf)

    resources: dict[str, Resource] = {}
    current: Resource | None = None
    for st in structures:
        if st.acronym == "BRS":
            name = st.data[:8].decode("cp037")
            current = Resource(kind="", name=name)
        elif st.acronym == "ERS":
            if current is not None:
                resources[current.name] = current
            current = None
        elif current is not None:
            if st.acronym == "BMO":
                current.kind = "overlay"
            elif st.acronym == "BPS":
                current.kind = "page segment"
            current.structures.append(st)
    return resources
