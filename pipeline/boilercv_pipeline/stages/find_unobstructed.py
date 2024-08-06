"""Select the subset of data corresponding to unobstructed bubbles."""

from boilercv_pipeline.config import default


def main():  # noqa: D103
    (default.params.paths.unobstructed / "unobstructed").touch()


if __name__ == "__main__":
    main()
