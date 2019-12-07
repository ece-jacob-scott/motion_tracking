import numpy as np
import cv2 as cv
from math import sqrt
from os import path, getcwd
from pprint import pprint
from typing import List, Union, Tuple, Dict
from utils import draw_rectangle, color_match, calculate_shape, calculate_center, calculate_tracking

VIDEO_FILE = "videos/grb_2.avi"
SCRIPT_DIR = getcwd()
# Got the reference color from finding the comet starting position
# [80:125, 290:330] and taking the average color based off a threshold of any
# average color value above 50.
REFERENCE_COLOR = (96, 96, 96)
# Starting (ROWS, COLS)
STARTING_POSITION = ((80, 125), (290, 330))
S_POS = STARTING_POSITION
# Found these threshold values by calculating the color match formula over the
# starting range and taking the average of what I say from the da & dm values
DA_THRESH = (200.0, 400.0)
DM_THRESH = (200.0, 600.0)
# Initial center point (x, y)
INIT_CENTER = (309, 96)
# Height and Width of interest area
WIDTH = 60
HEIGHT = 60
# Center weights
M_W, C_W, S_W = 0.50, 0.25, 0.25


def color_map(frame: np.array, start_x: int = 0, start_y: int = 0) -> Dict[str, float]:
    """
    Creates a color mapping for the passed frame 
    """
    m = dict()
    for r, row in enumerate(frame):
        for c, col in enumerate(row):
            key = f"{c + start_x}|{r + start_y}"
            if key in m:
                raise Exception(f"Duplicate key {key}")
            m[key] = color_match(col, REFERENCE_COLOR, DM_THRESH, DA_THRESH)
    return m


def testing_tracking():
    # Get two frames
    capture = cv.VideoCapture(path.join(SCRIPT_DIR, VIDEO_FILE))
    __, frame_1 = capture.read()
    __, frame_2 = capture.read()
    [I_X, I_Y] = INIT_CENTER
    H_W, H_H = WIDTH // 2, HEIGHT // 2

    p_frame = frame_1[I_Y-H_H:I_Y+H_H, I_X-H_W:I_X+H_W]
    c_frame = frame_2[I_Y-H_H:I_Y+H_H, I_X-H_W:I_X+H_W]

    p_m = color_map(p_frame, I_X-H_W, I_Y-H_H)
    c_m = color_map(c_frame, I_X-H_W, I_Y-H_H)

    # Have the color maps now I need to calculate shape
    c_s = calculate_tracking(c_m, p_m)
    center = calculate_center(c_s)

    cv.circle(frame_2, (center[0], center[1]), 1, (0, 0, 255), 1)
    cv.rectangle(frame_2, (I_X-H_W, I_Y-H_H),
                 (I_X+H_W, I_Y+H_H), (255, 0, 0), 1)

    cv.imshow("Image", frame_2)
    cv.waitKey(0)

    print(f"Old Center: {I_X}, {I_Y}")
    print(f"Motion Center: {center[0]}, {center[1]}")


def testing_shape():
    # Get two frames
    capture = cv.VideoCapture(path.join(SCRIPT_DIR, VIDEO_FILE))
    __, frame_1 = capture.read()
    __, frame_2 = capture.read()
    [I_X, I_Y] = INIT_CENTER
    H_W, H_H = WIDTH // 2, HEIGHT // 2

    p_frame = frame_1[I_Y-H_H:I_Y+H_H, I_X-H_W:I_X+H_W]
    c_frame = frame_2[I_Y-H_H:I_Y+H_H, I_X-H_W:I_X+H_W]

    p_m = color_map(p_frame, I_X-H_W, I_Y-H_H)
    c_m = color_map(c_frame, I_X-H_W, I_Y-H_H)

    # Have the color maps now I need to calculate shape
    c_s = calculate_shape(c_m, p_m)
    center = calculate_center(c_s)

    cv.circle(frame_2, (center[0], center[1]), 1, (0, 0, 255), 1)
    cv.rectangle(frame_2, (I_X-H_W, I_Y-H_H),
                 (I_X+H_W, I_Y+H_H), (255, 0, 0), 1)

    cv.imshow("Image", frame_2)
    cv.waitKey(0)


def testing():
    # Get two frames
    capture = cv.VideoCapture(path.join(SCRIPT_DIR, VIDEO_FILE))
    __, frame_1 = capture.read()
    __, frame_2 = capture.read()
    [I_X, I_Y] = INIT_CENTER
    H_W, H_H = WIDTH // 2, HEIGHT // 2

    frame = frame_1[I_Y-H_H:I_Y+H_H, I_X-H_W:I_X+H_W]

    m = color_map(frame, I_X-H_W, I_Y-H_H)

    center = calculate_center(m)

    cv.circle(frame_1, (center[0], center[1]), 1, (0, 0, 255), 1)
    cv.rectangle(frame_1, (I_X-H_W, I_Y-H_H),
                 (I_X+H_W, I_Y+H_H), (255, 0, 0), 1)

    cv.imshow("Image", frame_1)
    cv.waitKey(0)


def add_target(frame: np.array, center: Tuple[int]):
    [I_X, I_Y] = INIT_CENTER
    H_W, H_H = WIDTH // 2, HEIGHT // 2
    cv.circle(frame, center, 1, (0, 0, 255), 1)
    cv.rectangle(frame, (I_X-H_W, I_Y-H_H),
                 (I_X+H_W, I_Y+H_H), (255, 0, 0), 1)
    return frame


def main():
    cap = cv.VideoCapture(path.join(SCRIPT_DIR, VIDEO_FILE))
    prev_frame = None
    global INIT_CENTER
    H_W, H_H = WIDTH // 2, HEIGHT // 2
    while cap.isOpened():
        [I_X, I_Y] = INIT_CENTER
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame")
            break
        if cv.waitKey(1) == ord("q"):
            break
        # Break up frame into surrounding box
        sub_frame = frame[I_Y-H_H:I_Y+H_H, I_X-H_W:I_X+H_W]
        # if there was no previous frame then just map it out
        if prev_frame is None:
            prev_frame = color_map(sub_frame, I_X-H_W, I_Y-H_H)
            continue
        # if there was a previous frame
        # Calculate centers
        curr_frame_map = color_map(sub_frame, I_X-H_W, I_Y-H_H)
        c_center = calculate_center(curr_frame_map)
        shape = calculate_shape(curr_frame_map, prev_frame)
        s_center = calculate_center(shape)
        motion = calculate_tracking(curr_frame_map, prev_frame)
        m_center = calculate_center(motion)
        n_r = int((c_center[0] * C_W) +
                  (m_center[0] * M_W) + (s_center[0] * S_W))
        n_c = int((c_center[1] * C_W) +
                  (m_center[1] * M_W) + (s_center[1] * S_W))
        prev_frame = curr_frame_map
        INIT_CENTER = (n_r, n_c)
        frame = add_target(frame, (n_r, n_c))
        cv.imshow("Video", frame)
    cap.release()
    cv.destroyAllWindows()


if __name__ == "__main__":
    main()
