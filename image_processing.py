import cv2
from model import detect_and_segment
from datetime import datetime

def draw_result_on_image(image_path, object):
    image = cv2.imread(image_path)

    box = object["box"]
    cv2.rectangle(image, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), color=(0, 255, 0), thickness=1)

    coords = object["coords"]
    for coord in coords:
        color = image[coord[0], coord[1]]
        color[1] += 100
        image[coord[0], coord[1]] = color

    cy, cx = coords.mean(axis=0).astype(int)
    image[cx, cy] = [255, 0 , 0]

    cv2.imshow("result", image)
    cv2.waitKey(0)


def get_image_path(index):
    return f"images/image_{index}.jpg"

for i in range(84, 125):
    result = detect_and_segment(get_image_path(i), "tafelschwamm")
    box = result["box"] if result else 'Not found'
    print(f"{i} | {datetime.now()} | {box}")

# draw_result_on_image(IMAGE_PATH, result)
