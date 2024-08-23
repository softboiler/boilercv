from cappa.base import invoke

from boilercv_pipeline.stages.e230920_find_tracks import E230920FindTracks


def main(_params: E230920FindTracks):
    pass


if __name__ == "__main__":
    invoke(E230920FindTracks)
