import os
import cv2
import numpy as np
import torch
import torch.nn as nn

from config import PROJECT_ROOT, DEVICE


# ============================================================
# CONFIG
# ============================================================

LESION_MODEL_PATH = os.path.join(
    PROJECT_ROOT,
    "models",
    "retina_xai_unet_v2.pth"
)

LESION_OUTPUT_DIR = os.path.join(
    PROJECT_ROOT,
    "outputs",
    "lesion_evidence"
)

os.makedirs(LESION_OUTPUT_DIR, exist_ok=True)

PATCH_SIZE = 512
MIN_LESION_PIXELS = 50


# ============================================================
# LESION CLASSES
# ============================================================

CLASS_INFO = {
    1: ("MA", "Microaneurysm"),
    2: ("HE", "Haemorrhage"),
    3: ("EX", "Hard Exudate"),
    4: ("SE", "Soft Exudate")
}


# ============================================================
# U-NET
# ============================================================

class DoubleConv(nn.Module):

    def __init__(self, in_channels, out_channels):

        super().__init__()

        self.block = nn.Sequential(

            nn.Conv2d(
                in_channels,
                out_channels,
                kernel_size=3,
                padding=1,
                bias=False
            ),

            nn.BatchNorm2d(
                out_channels
            ),

            nn.ReLU(inplace=True),

            nn.Conv2d(
                out_channels,
                out_channels,
                kernel_size=3,
                padding=1,
                bias=False
            ),

            nn.BatchNorm2d(
                out_channels
            ),

            nn.ReLU(inplace=True)
        )


    def forward(self, x):

        return self.block(x)


class UNetV2(nn.Module):

    def __init__(self, num_classes=5):

        super().__init__()

        # Encoder

        self.enc1 = DoubleConv(3, 32)

        self.pool1 = nn.MaxPool2d(2)

        self.enc2 = DoubleConv(32, 64)

        self.pool2 = nn.MaxPool2d(2)

        self.enc3 = DoubleConv(64, 128)

        self.pool3 = nn.MaxPool2d(2)

        self.enc4 = DoubleConv(128, 256)

        self.pool4 = nn.MaxPool2d(2)

        # Bottleneck

        self.bottleneck = DoubleConv(
            256,
            512
        )

        # Decoder

        self.up4 = nn.ConvTranspose2d(
            512,
            256,
            kernel_size=2,
            stride=2
        )

        self.dec4 = DoubleConv(
            512,
            256
        )

        self.up3 = nn.ConvTranspose2d(
            256,
            128,
            kernel_size=2,
            stride=2
        )

        self.dec3 = DoubleConv(
            256,
            128
        )

        self.up2 = nn.ConvTranspose2d(
            128,
            64,
            kernel_size=2,
            stride=2
        )

        self.dec2 = DoubleConv(
            128,
            64
        )

        self.up1 = nn.ConvTranspose2d(
            64,
            32,
            kernel_size=2,
            stride=2
        )

        self.dec1 = DoubleConv(
            64,
            32
        )

        self.final = nn.Conv2d(
            32,
            num_classes,
            kernel_size=1
        )


    def forward(self, x):

        e1 = self.enc1(x)

        e2 = self.enc2(
            self.pool1(e1)
        )

        e3 = self.enc3(
            self.pool2(e2)
        )

        e4 = self.enc4(
            self.pool3(e3)
        )

        b = self.bottleneck(
            self.pool4(e4)
        )

        d4 = self.up4(b)

        d4 = torch.cat(
            [d4, e4],
            dim=1
        )

        d4 = self.dec4(d4)

        d3 = self.up3(d4)

        d3 = torch.cat(
            [d3, e3],
            dim=1
        )

        d3 = self.dec3(d3)

        d2 = self.up2(d3)

        d2 = torch.cat(
            [d2, e2],
            dim=1
        )

        d2 = self.dec2(d2)

        d1 = self.up1(d2)

        d1 = torch.cat(
            [d1, e1],
            dim=1
        )

        d1 = self.dec1(d1)

        return self.final(d1)


# ============================================================
# LOAD MODEL
# ============================================================

_lesion_model = None


def load_lesion_model():

    global _lesion_model

    if _lesion_model is not None:
        return _lesion_model

    model = UNetV2(
        num_classes=5
    )

    checkpoint = torch.load(
        LESION_MODEL_PATH,
        map_location=DEVICE
    )

    if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:

        model.load_state_dict(
            checkpoint["model_state_dict"]
        )

    else:

        model.load_state_dict(
            checkpoint
        )

    model = model.to(DEVICE)

    model.eval()

    _lesion_model = model

    return model


# ============================================================
# RETINA MASK
# ============================================================

def get_retina_mask(image):

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_RGB2GRAY
    )

    _, mask = cv2.threshold(
        gray,
        15,
        255,
        cv2.THRESH_BINARY
    )

    kernel = np.ones(
        (51, 51),
        np.uint8
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        kernel
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_OPEN,
        kernel
    )

    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if contours:

        largest = max(
            contours,
            key=cv2.contourArea
        )

        clean_mask = np.zeros_like(mask)

        cv2.drawContours(
            clean_mask,
            [largest],
            -1,
            255,
            cv2.FILLED
        )

        return clean_mask

    return mask


# ============================================================
# PATCH PREDICTION
# ============================================================

def predict_full_image(model, image):

    height, width = image.shape[:2]

    full_prediction = np.zeros(
        (height, width),
        dtype=np.uint8
    )

    for y in range(
        0,
        height,
        PATCH_SIZE
    ):

        for x in range(
            0,
            width,
            PATCH_SIZE
        ):

            y2 = min(
                y + PATCH_SIZE,
                height
            )

            x2 = min(
                x + PATCH_SIZE,
                width
            )

            patch = image[
                y:y2,
                x:x2
            ]

            original_h, original_w = patch.shape[:2]

            # Padding if edge patch is smaller than 512
            padded = np.zeros(
                (
                    PATCH_SIZE,
                    PATCH_SIZE,
                    3
                ),
                dtype=np.uint8
            )

            padded[
                :original_h,
                :original_w
            ] = patch

            # 0-1 normalization
            tensor = (
                torch.from_numpy(
                    padded.astype(
                        np.float32
                    ) / 255.0
                )
                .permute(2, 0, 1)
                .unsqueeze(0)
                .to(DEVICE)
            )

            with torch.no_grad():

                output = model(
                    tensor
                )

                prediction = torch.argmax(
                    output,
                    dim=1
                )[0].cpu().numpy()

            full_prediction[
                y:y2,
                x:x2
            ] = prediction[
                :original_h,
                :original_w
            ]

    return full_prediction


# ============================================================
# LESION EVIDENCE
# ============================================================

def generate_lesion_evidence(image_path):

    model = load_lesion_model()

    # --------------------------------------------------------
    # Read image
    # --------------------------------------------------------

    image_bgr = cv2.imread(
        image_path
    )

    if image_bgr is None:

        raise ValueError(
            f"Could not read image: {image_path}"
        )

    image = cv2.cvtColor(
        image_bgr,
        cv2.COLOR_BGR2RGB
    )

    original = image.copy()

    # --------------------------------------------------------
    # Predict
    # --------------------------------------------------------

    prediction = predict_full_image(
        model,
        image
    )

    # --------------------------------------------------------
    # Retina mask
    # --------------------------------------------------------

    retina_mask = get_retina_mask(
        image
    )

    prediction[
        retina_mask == 0
    ] = 0

    # --------------------------------------------------------
    # Output image
    # --------------------------------------------------------

    output = original.copy()

    detected_classes = []

    # --------------------------------------------------------
    # Draw lesion contours
    # --------------------------------------------------------

    for class_id in range(1, 5):

        binary_mask = (
            prediction == class_id
        ).astype(
            np.uint8
        ) * 255

        # Remove tiny noise
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
            binary_mask,
            connectivity=8
        )

        clean_mask = np.zeros_like(
            binary_mask
        )

        for i in range(
            1,
            num_labels
        ):

            area = stats[
                i,
                cv2.CC_STAT_AREA
            ]

            if area >= MIN_LESION_PIXELS:

                clean_mask[
                    labels == i
                ] = 255

        # Find contours
        contours, _ = cv2.findContours(
            clean_mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        if len(contours) == 0:
            continue

        short_name, full_name = CLASS_INFO[
            class_id
        ]

        detected_classes.append(
            short_name
        )

        # Draw filled contour
        cv2.drawContours(
            output,
            contours,
            -1,
            get_class_color(class_id),
            thickness=cv2.FILLED
        )

    # --------------------------------------------------------
    # Legend
    # --------------------------------------------------------

    legend_x = 30
    legend_y = 40

    cv2.rectangle(
        output,
        (
            legend_x - 15,
            legend_y - 30
        ),
        (
            legend_x + 230,
            legend_y + 150
        ),
        (0, 0, 0),
        -1
    )

    cv2.putText(
        output,
        "AI Lesion Evidence",
        (
            legend_x,
            legend_y
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2
    )

    y_offset = 30

    for class_id in range(1, 5):

        short_name, full_name = CLASS_INFO[
            class_id
        ]

        color = get_class_color(
            class_id
        )

        y_offset += 28

        cv2.rectangle(
            output,
            (
                legend_x,
                legend_y + y_offset - 15
            ),
            (
                legend_x + 18,
                legend_y + y_offset + 3
            ),
            color,
            -1
        )

        cv2.putText(
            output,
            f"{short_name} - {full_name}",
            (
                legend_x + 28,
                legend_y + y_offset
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.48,
            (255, 255, 255),
            1
        )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    image_name = os.path.splitext(
        os.path.basename(image_path)
    )[0]

    output_path = os.path.join(
        LESION_OUTPUT_DIR,
        f"{image_name}_lesion_evidence.png"
    )

    output_bgr = cv2.cvtColor(
        output,
        cv2.COLOR_RGB2BGR
    )

    cv2.imwrite(
        output_path,
        output_bgr
    )

    return {
        "image": os.path.basename(
            image_path
        ),

        "lesion_evidence_path":
            output_path,

        "detected_classes":
            detected_classes
    }


# ============================================================
# COLORS
# ============================================================

def get_class_color(class_id):

    colors = {

        1: (30, 90, 220),      # MA

        2: (50, 220, 50),      # HE

        3: (255, 220, 0),      # EX

        4: (0, 220, 255)       # SE
    }

    return colors.get(
        class_id,
        (255, 255, 255)
    )