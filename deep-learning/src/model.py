import torch.nn as nn
from torchvision.models import efficientnet_b0

from config import MODEL_PATH, DEVICE


_model = None


def load_model():

    global _model

    if _model is not None:
        return _model

    model = efficientnet_b0(weights=None)

    num_features = model.classifier[1].in_features

    model.classifier[1] = nn.Linear(
        num_features,
        5
    )

    checkpoint = __import__("torch").load(
        MODEL_PATH,
        map_location=DEVICE
    )

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    model = model.to(DEVICE)
    model.eval()

    _model = model

    return _model


def get_target_layer():

    model = load_model()

    return model.features[-1][0]