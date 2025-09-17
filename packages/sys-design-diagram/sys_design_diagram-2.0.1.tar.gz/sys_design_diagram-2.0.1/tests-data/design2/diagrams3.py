"""Copyright (c) 2024, Aydin Abdi."""

from diagrams import Diagram
from diagrams.aws.compute import EC2
from diagrams.aws.network import ELB


def component_diagram(output_path: str) -> None:
    """Create a simple diagram with an ELB and an EC2 instance."""
    with Diagram("Simple Diagram 1", show=False, filename=output_path):
        ELB("lb") >> EC2("web")
