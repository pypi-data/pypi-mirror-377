"""Copyright (c) 2024, Aydin Abdi."""

from diagrams import Diagram
from diagrams.aws.database import RDS
from diagrams.aws.compute import EC2


def component_diagram(output_path: str) -> None:
    """Create a simple diagram with an ELB and an EC2 instance."""
    with Diagram("Simple Diagram 2", show=False, filename=output_path):
        EC2("web") >> RDS("database")
