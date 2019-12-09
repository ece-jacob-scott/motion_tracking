# Attempt at recreating basic algorithm described in paper
# - https://tinyurl.com/tdtrwkw (need IEEE access)

import numpy as np
import cv2 as cv
from math import sqrt
from os import path, getcwd
from pprint import pprint
from typing import List, Union, Tuple, Dict
from utils import color_match, calculate_shape, calculate_center, calculate_tracking

VIDEO_FILE = "videos/grb_2.avi"
SCRIPT_DIR = getcwd()
# Got the reference color from finding the comet starting position
# [80:125, 290:330] and taking the average color based off a threshold of any
# average color value above 50.
REFERENCE_COLOR = (125, 125, 125)
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


def add_target(frame: np.array, center: Tuple[int]):
    [I_X, I_Y] = INIT_CENTER
    H_W, H_H = WIDTH // 2, HEIGHT // 2
    cv.circle(frame, center, 1, (0, 0, 255), 1)
    cv.rectangle(frame, (I_X-H_W, I_Y-H_H),
                 (I_X+H_W, I_Y+H_H), (255, 0, 0), 1)
    return frame


def main():
    # Create a video capture object
    cap = cv.VideoCapture(path.join(SCRIPT_DIR, VIDEO_FILE))
    # Initialize previous frame map variable
    prev_frame = None
    global INIT_CENTER
    # Get the height and weight for the search area
    H_W, H_H = WIDTH // 2, HEIGHT // 2
    while cap.isOpened():
        # Get the approximate center point for the object
        [I_X, I_Y] = INIT_CENTER
        # Read the current frame
        ret, frame = cap.read()
        # If the reading the frame failed break out of the loop
        if not ret:
            print("Failed to read frame")
            break
        # If the user pressed 'q' break out of the loop
        if cv.waitKey(15) == ord("q"):
            print("Stopped")
            break
        # Strip out the object search area using the initial
        # points and the height and width values
        sub_frame = frame[I_Y-H_H:I_Y+H_H, I_X-H_W:I_X+H_W]
        # If there was no previous frame then create one
        # and move onto the next frame
        if prev_frame is None:
            prev_frame = color_map(sub_frame, I_X-H_W, I_Y-H_H)
            continue
        # If there was a previous frame calculate centers
        curr_frame_map = color_map(sub_frame, I_X-H_W, I_Y-H_H)
        c_center = calculate_center(curr_frame_map)
        shape = calculate_shape(curr_frame_map, prev_frame)
        s_center = calculate_center(shape)
        motion = calculate_tracking(curr_frame_map, prev_frame)
        m_center = calculate_center(motion)
        # Find center of the object using the weighted sum of
        # all the object's calculated centers.
        n_r = int((c_center[0] * C_W) +
                  (m_center[0] * M_W) + (s_center[0] * S_W))
        n_c = int((c_center[1] * C_W) +
                  (m_center[1] * M_W) + (s_center[1] * S_W))
        # Set the current frame to the previous frame for the next loop
        prev_frame = curr_frame_map
        # Update the initial center value
        INIT_CENTER = (n_r, n_c)
        # Add the target around the tracked object
        frame = add_target(frame, (n_r, n_c))
        # Show the frame with the target
        cv.imshow("Video", frame)
    cap.release()
    cv.destroyAllWindows()


if __name__ == "__main__":
    main()
