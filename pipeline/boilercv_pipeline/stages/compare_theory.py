"""Bubble lifetimes compared with theoretical correlations."""

from boilercv_pipeline.config import default


def main():  # noqa: D103
    (default.params.paths.lifetimes / "theory").touch()


if __name__ == "__main__":
    main()
