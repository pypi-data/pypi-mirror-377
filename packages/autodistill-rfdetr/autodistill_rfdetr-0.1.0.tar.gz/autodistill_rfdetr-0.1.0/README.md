<div align="center">
  <p>
    <a align="center" href="" target="_blank">
      <img
        width="850"
        src="https://media.roboflow.com/open-source/autodistill/autodistill-banner.png"
      >
    </a>
  </p>
</div>

# Autodistill RF-DETR Module

This repository contains the code supporting the RF-DETR target model for use with [Autodistill](https://github.com/autodistill/autodistill).

[RF-DETR](https://github.com/roboflow/rf-detr) is a real-time, transformer-based object detection model developed by Roboflow and released under the Apache 2.0 license.

RF-DETR-N outperforms YOLO11-N by 10 mAP points on the Microsoft COCO benchmark while running faster at inference. On RF100-VL, RF-DETR achieves state-of-the-art results, with RF-DETR-M beating YOLO11-M by an average of 5 mAP points across aerial datasets including drone, satellite, and radar.

Read the full [Autodistill documentation](https://autodistill.github.io/autodistill/).

## Installation

To use the RF-DETR target model, you will need to install the following dependency:

```bash
pip3 install autodistill-rfdetr
```

## Quickstart

```python
from autodistill_rfdetr import RFDETR

target_model = RFDETR("base")

# train a model
target_model.train("./labeled_data/data.yaml", epochs=200)

# run inference on the new model
pred = target_model.predict("./labeled_data/train/images/dog-7.jpg", conf=0.01)
```

## License

[Autodistill RF-DETR is licensed under an Apache 2.0 license.](LICENSE) [RF-DETR is licensed under an Apache 2.0 license.](https://github.com/roboflow/rf-detr?tab=Apache-2.0-1-ov-file#readme)

## 🏆 Contributing

We love your input! Please see the core Autodistill [contributing guide](https://github.com/autodistill/autodistill/blob/main/CONTRIBUTING.md) to get started. Thank you 🙏 to all our contributors!
