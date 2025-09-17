import os
from pathlib import Path
import cv2
import numpy as np
from exordium import PathType


def visualize_bb(image: np.ndarray,
                 bb_xyxy: np.ndarray,
                 probability: float,
                 output_path: PathType | None = None) -> np.ndarray:
    if bb_xyxy.shape != (4,):
        raise Exception(f'Expected bounding box with shape (4,) got istead {bb_xyxy.shape}.')

    bb_xyxy = np.rint(bb_xyxy).astype(int)
    probability = np.round(probability, decimals=2)

    cv2.rectangle(image, bb_xyxy[:2], bb_xyxy[2:], (255,0,0), 2)
    cv2.putText(image, str(probability), bb_xyxy[:2] - 5, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)

    if output_path is not None:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(output_path), image)

    return image


def visualize_landmarks(image: np.ndarray,
                        landmarks: np.ndarray,
                        output_path: str | os.PathLike | None = None,
                        show_indices: bool = True,
                        radius: int = 1,
                        color: tuple[int, int, int] = (0, 255, 0),
                        thickness: int = 2,
                        font: int = cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale: float = 0.3,
                        font_thickness: int = 1) -> np.ndarray:
    """Landmarks are drawn to the given image"""

    if not (landmarks.ndim == 2 and landmarks.shape[1] == 2):
        raise Exception(f'Expected landmarks with shape (5,2) got instead {landmarks.shape}.')

    image_out = np.copy(image)
    landmarks = np.rint(landmarks).astype(int)

    for index in range(len(landmarks)):
        cv2.circle(image_out, landmarks[index, :], radius, color, thickness)
        if show_indices:
            cv2.putText(image_out, str(index), landmarks[index, :] + 5,
                        font, fontScale, color, font_thickness, cv2.LINE_AA)

    if output_path is not None:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(output_path), image_out)

    return image_out


def visualize_iris(image: np.ndarray,
                   landmarks: np.ndarray,
                   iris_landmarks: np.ndarray,
                   output_path: str | os.PathLike | None = None,
                   show_indices: bool = False) -> np.ndarray:
    """Landmarks are drawn to the given image"""

    if not (landmarks.ndim == 2 and landmarks.shape[1] == 2):
        raise Exception(f'Expected landmakrs with shape (N,2) got istead {landmarks.shape}.')

    if not (iris_landmarks.ndim == 2 and iris_landmarks.shape[1] == 2):
        raise Exception(f'Expected landmakrs with shape (5,2) got istead {iris_landmarks.shape}.')

    image_out = np.copy(image)
    landmarks = np.rint(landmarks).astype(int)
    iris_landmarks = np.rint(iris_landmarks).astype(int)

    radius = 0
    thickness = 1
    font = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 0.3
    font_thickness = 1

    for index in range(landmarks.shape[0]):
        cv2.circle(image_out, landmarks[index, :], radius, (0, 255, 0), thickness)
        if show_indices:
            cv2.putText(image_out, str(index), landmarks[index, :],
                        font, fontScale, (0, 0, 0), font_thickness, cv2.LINE_AA)

    for index in range(iris_landmarks.shape[0]):
        cv2.circle(image_out, iris_landmarks[index, :], radius, (255, 0, 0), thickness)
        if show_indices:
            cv2.putText(image_out, str(index), iris_landmarks[index, :],
                        font, fontScale, (0, 0, 0), font_thickness, cv2.LINE_AA)

    if output_path is not None:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(output_path), image_out)

    return image_out


if __name__ == '__main__':
    from exordium.video.tddfa_v2 import TDDFA_V2
    face_path = 'data/processed_v2/face_rgb/Gdrgw7Z6tLg.003/000000.png'
    face = cv2.imread(face_path)
    tddfa = TDDFA_V2()
    output_dict = tddfa(face)
    visualize_landmarks(face, output_dict['landmarks'], 'out.png', True)