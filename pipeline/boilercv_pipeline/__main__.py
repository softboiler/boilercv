"""Command-line interface."""

from cappa.base import invoke

from boilercv_pipeline.cli import BoilercvPipeline, defaults_backend


def main():
    """CLI entry-point."""
    invoke(BoilercvPipeline, backend=defaults_backend)


if __name__ == "__main__":
    main()
