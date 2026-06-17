import numpy as np
import cv2
from model import detect_and_segment
from datetime import datetime
from PIL import Image

def draw_result_on_image(image, object):
    cv_img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    box = object["box"]
    cv2.rectangle(cv_img, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), color=(0, 255, 0), thickness=1)

    coords = object["coords"]
    for coord in coords:
        color = cv_img[coord[0], coord[1]]
        
        color[1] = color[1]/2
        cv_img[coord[0], coord[1]] = color

    cy, cx = coords.mean(axis=0).astype(int)
    cv_img[cx, cy] = [255, 0 , 0]

    cv2.imwrite(f"./out/result_{datetime.now().time()}.jpg", cv_img )
    print(f"Result drawn on image and saved to ./out/result_{datetime.now().time()}.jpg")
    # return image

def get_image_path(index):
    return f"../images/image_{index}.jpg"

not_found = []
found = []

for i in range(0, 158):
    simpel = "Tafelschwamm"
    englisch = "sponge"
    umgebung = "Ein Tafelschwamm steht auf einer Oberfläche"
    sehr_explizit = "Ein Tafelschwamm steht auf einer Oberfläche, suche den Tafelschwamm"

    try:
        image = Image.open(get_image_path(i)).convert("RGB")
    except:
        print("Image not found, skipping")
        continue
    
    result = detect_and_segment(image, sehr_explizit)

    if result:
        box = result["box"] 
        print(f"{i} | {datetime.now()} | {box}")
        draw_result_on_image(image, result)
        found.append(i)
    else:
        print(f"{i} | {datetime.now()} | Not found")
        not_found.append(i)

print(f"found {len(found)} of {len(found) + len (not_found)}")
print(f"not found: {not_found}")