"""Command-line interface."""

from boilercv_pipeline.cli import BoilercvPipeline
from boilercv_pipeline.parser import invoke


def main():
    """CLI entry-point."""
    invoke(BoilercvPipeline)


if __name__ == "__main__":
    main()
