import cv2
import numpy as np


def draw_headpose_axis(img, headpose, tdx=None, tdy=None, size=100):
    yaw, pitch, roll = headpose

    # Convert degrees to radians
    pitch = np.radians(pitch)
    yaw = np.radians(yaw)
    roll = np.radians(-roll) # 3DDFA_V2 headpose is expected

    # Rotation matrices around X, Y, Z axes
    Rx = np.array([[1, 0, 0],
                   [0, np.cos(pitch), -np.sin(pitch)],
                   [0, np.sin(pitch), np.cos(pitch)]])
    Ry = np.array([[np.cos(yaw), 0, np.sin(yaw)],
                   [0, 1, 0],
                   [-np.sin(yaw), 0, np.cos(yaw)]])
    Rz = np.array([[np.cos(roll), -np.sin(roll), 0],
                   [np.sin(roll), np.cos(roll), 0],
                   [0, 0, 1]])

    # Combined rotation matrix
    R = Rz @ Ry @ Rx

    # Set origin (nose tip) - center face, or provided location
    if tdx is None or tdy is None:
        height, width = img.shape[:2]
        tdx = width // 2
        tdy = height // 2

    # Define axis points in 3D
    axis = np.float32([[size, 0, 0],
                       [0, -size, 0],  # y is negated to match image coords
                       [0, 0, -size]])

    # Rotate axis points
    axis_rotated = R.dot(axis.T).T

    # Project 3D points to 2D
    points = []
    for i in range(axis_rotated.shape[0]):
        x = int(tdx + axis_rotated[i, 0])
        y = int(tdy + axis_rotated[i, 1])
        points.append((x, y))

    # Draw axes
    img = cv2.line(img, (tdx, tdy), points[0], (0,0,255), 3)  # X - Red
    img = cv2.line(img, (tdx, tdy), points[1], (0,255,0), 3)  # Y - Green
    img = cv2.line(img, (tdx, tdy), points[2], (255,0,0), 2)  # Z - Blue

    return img
