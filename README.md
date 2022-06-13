# 3D Printer Anomaly Detected system

## Introduction
This project is to design a system for detecting the anomalies during the printing process. We collect our own dataset with a RPI and a Ender 3 pro.

## Installation
```bash
# Download the weights
$ wget -O weights/resnet.onnx https://github.com/Justin900429/3d-printer-anomaly-detect/releases/download/v0.0.1-alpha/resnet.onnx
$ wget -O weights/resnet.pt https://github.com/Justin900429/3d-printer-anomaly-detect/releases/download/v0.0.1-alpha/resnet.pt

# Install the python package
$ pip install -r requirements.txt
```

## Setup
### RPI
```
$ python send_image.py
```

### Backend
```
$ python main.py
```

## Dataset
We upload our data to [kaggle](https://www.kaggle.com/datasets/justin900429/3d-printer-defected-dataset)

