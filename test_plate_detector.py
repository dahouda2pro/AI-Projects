
from pathlib import Path

import cv2
from ultralytics import YOLO

# --------------------------------------------------
# PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "models" / "alpr_26n.onnx"

IMAGE_PATH = (
    BASE_DIR / "outputs" / "plate_samples" / "camera_sample.jpg"
)

OUTPUT_DIR = BASE_DIR / "outputs" / "detected_vehicles"
CROPS_DIR = OUTPUT_DIR / "plate_crops"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CROPS_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# DETECTION CONFIGURATION
# --------------------------------------------------

CONFIDENCE_THRESHOLD = 0.20
IMAGE_SIZE = 960
DEVICE = "cpu"
CROP_MARGIN = 8

# --------------------------------------------------
# VALIDATE INPUTS
# --------------------------------------------------

if not MODEL_PATH.exists():
    raise FileNotFoundError(f"Model not found: {MODEL_PATH}")

if not IMAGE_PATH.exists():
    raise FileNotFoundError(f"Image not found: {IMAGE_PATH}")

# --------------------------------------------------
# LOAD IMAGE AND MODEL
# --------------------------------------------------

image = cv2.imread(str(IMAGE_PATH))

if image is None:
    raise RuntimeError("Unable to read input image.")

print(f"Image dimensions: {image.shape[1]} x {image.shape[0]}")
print("Loading license plate detector...")

model = YOLO(str(MODEL_PATH), task="detect")

print("Model loaded successfully.")
print("Running inference on CPU...")

# --------------------------------------------------
# RUN DETECTION
# --------------------------------------------------

results = model.predict(
    source=image,
    imgsz=IMAGE_SIZE,
    conf=CONFIDENCE_THRESHOLD,
    device=DEVICE,
    verbose=False
)

result = results[0]

annotated_image = image.copy()
detections = []

# --------------------------------------------------
# PROCESS DETECTED PLATES
# --------------------------------------------------

if result.boxes is not None:

    for index, box in enumerate(result.boxes):

        x1, y1, x2, y2 = map(
            int,
            box.xyxy[0].cpu().numpy()
        )

        confidence = float(box.conf[0].cpu().numpy())

        # Add crop margin
        x1_crop = max(0, x1 - CROP_MARGIN)
        y1_crop = max(0, y1 - CROP_MARGIN)

        x2_crop = min(
            image.shape[1],
            x2 + CROP_MARGIN
        )

        y2_crop = min(
            image.shape[0],
            y2 + CROP_MARGIN
        )

        plate_crop = image[
            y1_crop:y2_crop,
            x1_crop:x2_crop
        ]

        if plate_crop.size == 0:
            continue

        crop_path = CROPS_DIR / f"plate_{index + 1}.jpg"

        cv2.imwrite(str(crop_path), plate_crop)

        # Draw detection
        cv2.rectangle(
            annotated_image,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            3
        )

        label = f"Plate: {confidence:.2f}"

        cv2.putText(
            annotated_image,
            label,
            (x1, max(25, y1 - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        detections.append({
            "detection": index + 1,
            "confidence": confidence,
            "coordinates": [x1, y1, x2, y2],
            "crop": str(crop_path)
        })

# --------------------------------------------------
# SAVE RESULTS
# --------------------------------------------------

annotated_path = OUTPUT_DIR / "plate_detection_result.jpg"

cv2.imwrite(
    str(annotated_path),
    annotated_image
)

print("\n========== DETECTION RESULTS ==========")

print(f"Number of plates detected: {len(detections)}")

for detection in detections:
    print(f"\nPlate {detection['detection']}")
    print(f"Confidence: {detection['confidence']:.4f}")
    print(f"Coordinates: {detection['coordinates']}")
    print(f"Crop: {detection['crop']}")

print("\nAnnotated image:")
print(annotated_path)

# --------------------------------------------------
# DISPLAY RESULT
# --------------------------------------------------

cv2.imshow(
    "YOLO License Plate Detection",
    annotated_image
)

print("\nPress Q to close the window.")

while True:

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cv2.destroyAllWindows()
