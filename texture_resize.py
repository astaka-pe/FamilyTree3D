import cv2
from pathlib import Path

def main():
    i_dir = Path("kanji")
    i_files = i_dir.glob("*.png")
    for file in i_files:
        img = cv2.imread(str(file))
        H, W, _ = img.shape
        if W - H > 0:
            left = (W - H) // 2
            right = left + H
            img = img[:, left:right, :]
        elif H - W > 0:
            top = (H - W) // 2
            bottom = top + W
            img = img[top:bottom, :, :]
        else:
            continue
        cv2.imwrite(str(file), img)

if __name__ == "__main__":
    main()