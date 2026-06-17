import torch
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


def detect_and_segment(image, text_prompt: str):

    box = get_box_with_dino(image, text_prompt)
    if not len(box):
        return None
    
    box_width = box[2] - box[0]

    mask, coords = get_mask_from_sam(image, box)

    meany, meanx = coords.mean(axis=0).astype(int)


    return {"box": box, "box_width": box_width, "mask": mask, "coords": coords, "mean": {"x": meanx, "y": meany}}