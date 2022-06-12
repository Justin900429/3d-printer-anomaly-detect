import numpy as np
import time
import onnxruntime as ort


ort_session = ort.InferenceSession("resnet.onnx")
img = np.random.rand(1, 3, 352, 352).astype("float32")

start = time.time()
outputs = ort_session.run(None, {"input": img})
print(time.time() - start)
