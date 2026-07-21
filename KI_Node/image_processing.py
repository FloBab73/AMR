from datetime import datetime

import cv2
import numpy as np
from PIL import Image

from model import detect_and_segment, get_top_edge_angle_from_mask


def draw_result_on_image(image, object, direction):
    cv_img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    if object:
        box = object["box"]
        cv2.rectangle(
            cv_img,
            (int(box[0]), int(box[1])),
            (int(box[2]), int(box[3])),
            color=(0, 255, 0),
            thickness=1,
        )

        cv_img[120, 160] = [255, 0 , 0]

        coords = object["coords"]
        for coord in coords:
            color = cv_img[coord[0], coord[1]]

            color[1] = color[1]/2
            cv_img[coord[0], coord[1]] = color

        cy, cx = coords.mean(axis=0).astype(int)
        cv_img[cy, cx] = [255, 0 , 0]

    cv2.imwrite(f"./out/result_{datetime.now().time()}_{direction}.jpg", cv_img)
    # return image


def get_image_path(index):
    return f"../images/image_{index}.jpg"


def main():
    not_found = []
    found = []

    for i in range(1, 2):
        PROMPT = "Ein Tafelschwamm steht auf einer Oberfläche, suche den Tafelschwamm. Gib lieber kein Ergebnis zurück, wenn du den Tafelschwamm nicht findest."

        simpel = "Tafelschwamm"
        englisch = "sponge"
        umgebung = "Ein Tafelschwamm steht auf einer Oberfläche"
        sehr_explizit = (
            "Ein Tafelschwamm steht auf einer Oberfläche, suche den Tafelschwamm"
        )

        try:
            image = Image.open(get_image_path(i)).convert("RGB")
        except:
            print("Image not found, skipping")
            continue

        result = detect_and_segment(image, PROMPT)

        if result:
            angle = get_top_edge_angle_from_mask(result["mask"])
            print(f"angle: {angle}")
            box = result["box"]
            print(f"{i} | {datetime.now()} | {box}")
            draw_result_on_image(image, result, i)
            found.append(i)
        else:
            # print(f"{i} | {datetime.now()} | Not found")
            not_found.append(i)

    print(f"found {len(found)} of {len(found) + len(not_found)}")
    print(f"not found: {not_found}")


if __name__ == "__main__":
    main()
