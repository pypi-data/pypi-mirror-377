from autodistill.detection import DetectionTargetModel
from rfdetr import RFDETRBase as BaseModel
from rfdetr import RFDETRLarge as LargeModel
import supervision as sv

class RFDETR(DetectionTargetModel):
    def __init__(self):
        pass
        
    def predict(self, input:str, confidence=0.5) -> sv.Detections:
        self.model.optimize_for_inference()
        return self.model.predict(input, threshold=confidence)

    def train(self, dataset_yaml, epochs=25, output_dir="training-output"):
        self.model.train(
            dataset_dir=dataset_yaml,
            epochs=epochs,
            batch_size=4,
            grad_accum_steps=4,
            lr=1e-4,
            output_dir=output_dir
        )

class RFDETRBase(RFDETR):
    def __init__(self, checkpoints = None):
        if checkpoints:
            self.model = BaseModel(checkpoints=checkpoints)
        else:
            self.model = BaseModel()
        
class RFDETRLarge(RFDETR):
    def __init__(self, checkpoints = None):
        if checkpoints:
            self.model = LargeModel(checkpoints=checkpoints)
        else:
            self.model = LargeModel()
