import numpy as np
import cv2 as cv
from math import sqrt
from typing import List, Union, Tuple, Dict


def draw_rectangle(image: np.array, start: tuple, end: tuple) -> np.array:
    cv.rectangle(image, start, end, color=(0, 255, 0), thickness=1)
    return image


def save_frame_to_file(frame: np.array, size: Union[Tuple, None] = None) -> None:
    with open("frame.txt", "w+") as f:
        for index, row in enumerate(frame):
            f.write(f"{index}: ")
            for col in row:
                f.write(str(col))
            f.write("\n")


def average_color(frame: np.array, thresh_hold: int = 50) -> int:
    pixels = 0
    a_color = 0
    for row in frame:
        for col in row:
            color = sum(col)
            if color <= thresh_hold:
                print("TEST")
                continue
            pixels += 1
            a_color += color
    return a_color // pixels


def color_match(pixel: List[int], reference: List[int],
                dm_thresh: Tuple[int] = (0, 1000), da_thresh: Tuple[int] = (0, 1000)) -> float:
    [R, G, B] = pixel
    [Rr, Gr, Br] = reference
    d = (R*Rr) + (G*Gr) + (B*Br)
    mr = Rr ^ 2 + Gr ^ 2 + Br ^ 2
    m = R ^ 2 + G ^ 2 + B ^ 2
    # So the algorithm doesn't divide by 0
    if m < 0.1:
        m = 0.1
    dm = d / mr
    da = d / sqrt(mr * m)
    [dm_l, dm_h] = dm_thresh
    [da_l, da_h] = da_thresh
    if dm_l < dm < dm_h and da_l < da < da_h:
        return da * dm
    return 0.0


def calculate_shape(c_color_map: Dict[str, float], p_color_map: Dict[str, float]) -> Dict[str, float]:
    """
    Calculate shape of the figure using the current frame and the previous
    frames color value

    Algorithm:
    ----------
    if color existed in previous frame then keep the color value
    else set color value to 0
    """
    s = dict()
    for key, value in c_color_map.items():
        if key in p_color_map and p_color_map[key] > 0.0:
            s[key] = value
            continue
        s[key] = 0.0
    return s


def calculate_center(m: Dict[str, float]) -> List[int]:
    """
    Given a dictionary map of an image calculate the center point

    The dictionary is given as the [x|y]: color_match(x, y)
    """
    x_coor = 0.0
    y_coor = 0.0
    c_total = 0.0
    for key, value in m.items():
        [x, y] = list(map(int, key.split("|")))
        x_coor += (value * x)
        y_coor += (value * y)
        c_total += value
    try:
        return [int(x_coor // c_total), int(y_coor // c_total)]
    except:
        return [0, 0]


def calculate_tracking(c_color_map: Dict[str, float], p_color_map: Dict[str, float], d_thresh: int = 0, c_thresh: int = 0) -> Dict[str, float]:
    """
    Calculates the color map for tracking the figure. 

    Algorithm:
    If the differnce in color is above a threshold and the current color value is
    above a threshold then keep the color.
    """
    v = dict()
    for key, value in c_color_map.items():
        if key in p_color_map:
            difference = abs(c_color_map[key] - p_color_map[key])
            if difference > d_thresh and c_color_map[key] > c_thresh:
                v[key] = c_color_map[key]
                continue
        v[key] = 0
    return v
