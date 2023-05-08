"""
track in format:
int track_width
int track_height
bool[][] track_tiles (0 if there is no track, 1 if there is)
((int, int), (int, int))[] track_boundaries (track wall)
((int, int), (int, int))[] track_checkpoints
((int, int), (int, int)) track_start
"""


class Track:
    # you can declare empty track for ease of usage
    def __init__(self):
        self.width = 0
        self.height = 0
        self.tiles = [[]]
        self.boundaries = []
        self.checkpoints = []
        self.start = ((0, 0), (0, 0))

    # default init
    def __init__(self, width, height, tiles, boundaries, checkpoints, start):
        self.width = width
        self.height = height
        self.tiles = tiles
        self.boundaries = boundaries
        self.checkpoints = checkpoints
        self.start = start
