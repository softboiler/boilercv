"""Track bubbles."""

from boilercv_pipeline.config import default


def main():  # noqa: D103
    (default.params.paths.tracks / "tracks").touch()


if __name__ == "__main__":
    main()
