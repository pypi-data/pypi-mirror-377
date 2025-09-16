from typing import Tuple, Dict
from bluer_objects import objects

from bluer_algo.yolo.model.predictor import YoloPredictor
from bluer_algo.yolo.dataset.classes import YoloDataset


def prediction_test(
    dataset_object_name: str,
    model_object_name: str,
    record_index: int = 0,
    prediction_object_name: str = "",
    verbose: bool = True,
) -> Tuple[bool, Dict]:
    dataset = YoloDataset(object_name=dataset_object_name)
    if not dataset.valid:
        return False, {}

    success, predictor = YoloPredictor.load(object_name=model_object_name)
    if not success:
        return False, {}

    record_id = dataset.list_of_records[record_index]

    success, image = dataset.load_image(
        record_id=record_id,
        verbose=verbose,
    )
    if not success:
        return False, {}

    return predictor.predict(
        image=image,
        header=objects.signature(
            record_id,
            object_name=dataset_object_name,
        ),
        verbose=verbose,
        prediction_object_name=prediction_object_name,
        record_id=record_id,
    )
