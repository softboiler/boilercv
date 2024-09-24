from boilercv_pipeline.parser import invoke
from boilercv_pipeline.stages.skip_cloud import SkipCloud


def main(_params: SkipCloud):
    pass


if __name__ == "__main__":
    invoke(SkipCloud)
