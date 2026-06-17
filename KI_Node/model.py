import torch
import cv2
from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection
from transformers import SamModel, SamProcessor
import numpy as np

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(DEVICE)

# set False once when running the first time
LOCAL_FILES_ONLY = True

dino_processor = AutoProcessor.from_pretrained("IDEA-Research/grounding-dino-base", local_files_only=LOCAL_FILES_ONLY)
dino_model = AutoModelForZeroShotObjectDetection.from_pretrained("IDEA-Research/grounding-dino-base", local_files_only=LOCAL_FILES_ONLY).to(DEVICE)

sam_processor = SamProcessor.from_pretrained("facebook/sam-vit-base", local_files_only=LOCAL_FILES_ONLY)
sam_model = SamModel.from_pretrained("facebook/sam-vit-base", local_files_only=LOCAL_FILES_ONLY).to(DEVICE)

def get_box_with_dino(image, text_prompt):
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
        return []

    box = results["boxes"][0].cpu().numpy()  # [x1, y1, x2, y2]
    return box

def get_mask_from_sam(image, box):
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

    coords = np.argwhere(mask)
    
    return mask, coords


def get_top_edge_angle_from_mask(mask):
    contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) == 0:
        return None

    contour = max(contours, key=cv2.contourArea)
    if cv2.contourArea(contour) == 0:
        return None

    rect = cv2.minAreaRect(contour)
    box = cv2.boxPoints(rect)

    best_edge = None
    best_error = float("inf")
    best_mean_y = float("inf")

    for i in range(4):
        p1 = box[i]
        p2 = box[(i + 1) % 4]
        dx, dy = p2 - p1
        angle = np.degrees(np.arctan2(dy, dx))
        if angle >= 90:
            angle -= 180
        elif angle < -90:
            angle += 180

        abs_angle = abs(angle)
        mean_y = (p1[1] + p2[1]) / 2.0

        # Prefer the most horizontal edge, then the upper one if tied.
        if abs_angle < best_error or (abs_angle == best_error and mean_y < best_mean_y):
            best_error = abs_angle
            best_mean_y = mean_y
            best_edge = (p1, p2)

    if best_edge is None:
        return None

    p1, p2 = np.array(best_edge[0], dtype=np.float32), np.array(best_edge[1], dtype=np.float32)
    dx, dy = p2 - p1
    angle = np.degrees(np.arctan2(dy, dx))
    if angle >= 90:
        angle -= 180
    elif angle < -90:
        angle += 180

    return angle


def detect_and_segment(image, text_prompt: str):

    box = get_box_with_dino(image, text_prompt)
    if not len(box):
        return None
    
    box_width = box[2] - box[0]

    mask, coords = get_mask_from_sam(image, box)

    meany, meanx = coords.mean(axis=0).astype(int)
    angle = get_top_edge_angle_from_mask(mask)

    return {"box": box, "box_width": box_width, "mask": mask, "coords": coords, "mean": {"x": meanx, "y": meany}, "angle": angle}