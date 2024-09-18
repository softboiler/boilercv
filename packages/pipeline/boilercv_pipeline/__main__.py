"""Command-line interface."""

from cappa.base import invoke

from boilercv_pipeline.cli import BoilercvPipeline


def main():
    """CLI entry-point."""
    invoke(BoilercvPipeline)


if __name__ == "__main__":
    main()
