import torch
from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection
from transformers import SamModel, SamProcessor
from PIL import Image
import cv2
import numpy as np

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# ── Grounding DINO ───────────────────────────────────────────────
dino_processor = AutoProcessor.from_pretrained("IDEA-Research/grounding-dino-base", local_files_only=True)
dino_model = AutoModelForZeroShotObjectDetection.from_pretrained("IDEA-Research/grounding-dino-base",local_files_only=True).to(DEVICE)

# ── SAM ─────────────────────────────────────────────────────────
sam_processor = SamProcessor.from_pretrained("facebook/sam-vit-base", local_files_only=True)
sam_model = SamModel.from_pretrained("facebook/sam-vit-base", local_files_only=True).to(DEVICE)


# ── Pipeline ─────────────────────────────────────────────────────
def detect_and_segment(image_path, text_prompt: str):
    image = Image.open(image_path).convert("RGB")

    # 1. Grounding DINO → Box
    inputs = dino_processor(
        images=image,
        text=text_prompt,
        return_tensors="pt"
    ).to(DEVICE)

    with torch.no_grad():
        outputs = dino_model(**inputs)

    results = dino_processor.post_process_grounded_object_detection(
        outputs,
        inputs.input_ids,
        threshold=0.3,
        target_sizes=[image.size[::-1]]
    )[0]

    if len(results["boxes"]) == 0:
        print("Kein Objekt gefunden!")
        return None

    box = results["boxes"][0].cpu().numpy()  # [x1, y1, x2, y2]
    print(f"Gefunden: '{results['text_labels'][0]}' | Score: {results['scores'][0]:.2f} | top left: [{box[0]}, {box[1]}] bottom right: [{box[2]}, {box[3]}]")

    # 2. SAM → Maske
    inputs_sam = sam_processor(
        images=image,
        input_boxes=[[box.tolist()]],
        return_tensors="pt"
    ).to(DEVICE)

    with torch.no_grad():
        outputs_sam = sam_model(**inputs_sam)

    mask = sam_processor.post_process_masks(
        outputs_sam.pred_masks.cpu(),
        inputs_sam["original_sizes"].cpu(),
        inputs_sam["reshaped_input_sizes"].cpu()
    )[0][0][0].numpy()

    # 3. Greifpunkt
    coords = np.argwhere(mask)

    return {"box": box, "mask": mask, "coords": coords}

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



# ── Ausführen ────────────────────────────────────────────────────
IMAGE_PATH = "images/image_109.jpg"
result = detect_and_segment(IMAGE_PATH, "tafelschwamm")
draw_result_on_image(IMAGE_PATH, result)
