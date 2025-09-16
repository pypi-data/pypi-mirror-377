from __future__ import annotations
from typing import Optional, Sequence, Tuple, Union, List
import numpy as np


# xywhn # x_center_n, y_center_n, w_n, h_n
# xyxyn # x1_n, y1_n, x2_n, y2_n
# xywh # x_center, y_center, w, h
# xyxy # x1, y1, x2, y2

class Box:
    ...


if __name__ == "__main__":
    b = Box()
    b.set_xywhn(0.3, 0.8, 0.2, 0.1)
    b.set_size((100,100))

