import time

import torch
import torch.nn as nn

import timm


class QuantizeTrainModel(nn.Module):
    def __init__(self, model_name="resnet34", pretrained=True, num_classes=2):
        super().__init__()

        # Model settings
        self.model_name = model_name
        self.pretrained=pretrained
        self.num_classes = num_classes

        # Floating point -> Integer for input
        self.quant = torch.ao.quantization.QuantStub()

        # Check out the doc: https://rwightman.github.io/pytorch-image-models/
        #  for different models
        self.model = timm.create_model(model_name, pretrained=pretrained,
                block_args={"use_quantized": True})

        # Change the output linear layers to fit the output classes
        self.model.fc = nn.Linear(
            self.model.fc.weight.shape[1],
            num_classes
        )

        # Integer to Floating point for output
        self.dequant = torch.ao.quantization.DeQuantStub()

    def forward(self, x):
        x = self.quant(x)
        x = self.model(x)
        return self.dequant(x)

    def clone(self):
        clone = QuantizeTrainModel(self.model_name, self.pretrained, self.num_classes)
        clone.load_state_dict(self.state_dict())
        if self.is_cuda():
            clone.cuda()
        return clone

    def fused_module_inplace(self):
        """
        Fusing the model for resnet family only. Print out the model architecture
        to know how the logic works. Note that during the quantize fusion,
        conv + bn + act or conv + bn should be bundled to together
        """
        self.train()

        for module_name, module in self.named_children():
            # This coding style should not be correct but the code can be
            #  more readable
            if "model" not in module_name:
                continue

            torch.ao.quantization.fuse_modules_qat(
                module, [["conv1", "bn1", "act1"]], inplace=True
            )
            for basic_block_name, basic_block in module.named_children():
                # Same as above reason :)
                if "layer" not in basic_block_name:
                    continue

                for sub_block_name, sub_block in basic_block.named_children():
                    torch.ao.quantization.fuse_modules_qat(
                        sub_block,
                        [["conv1", "bn1", "act1"], ["conv2", "bn2", "act2"]],
                        inplace=True
                    )
                    for sub_sub_block_name, sub_sub_block in sub_block.named_children():
                        if sub_block_name == "downsample":
                            torch.ao.quantization.fuse_modules_qat(
                                sub_block, [["0", "1"]], inplace=True
                            )


# Build model
model = QuantizeTrainModel(pretrained=False)
model.fused_module_inplace()
model.qconfig = torch.ao.quantization.get_default_qat_qconfig("fbgemm")
torch.ao.quantization.prepare_qat(model, inplace=True)
model.eval()

# Load weight
quantized_model = torch.quantization.convert(model, inplace=False)
quantized_model.load_state_dict(torch.load("quantized.pt"))

# Test time
test_tensor = torch.randn(1, 3, 352, 352)

start = time.time()
for idx in range(10):
    _ = quantized_model(test_tensor)
print((time.time() - start)/10)
