import time

import torch
import torch.nn as nn

import timm


def rewrite_weight(weight):
    weight = torch.load(weight, map_location="cpu")

    new_keys = dict()
    for key, val in weight.items():
        new_keys[key.replace("model.", "")] = val
    return new_keys


# Build model
model = timm.create_model("resnet34")
# Change the output linear layers to fit the output classes
model.fc = nn.Linear(
    model.fc.weight.shape[1],
    2
)

# Load weight
model.load_state_dict(rewrite_weight("resnet.pt"))

# Test time
test_tensor = torch.randn(1, 3, 352, 352)

start = time.time()
for _ in range(10):
    _ = model(test_tensor)
print((time.time() - start) / 10)
