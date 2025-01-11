class Helperly:
    @staticmethod
    def rotate_right(x, n, width=64):
        return ((x >> n) | (x << (width - n))) & ((1 << width) - 1)

    @staticmethod
    def rotate_left(x, n, width=64):
        return ((x << n) | (x >> (width - n))) & ((1 << width) - 1)