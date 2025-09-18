import logging
from typing import List
import numpy as np

from easyams.sahi_onnx.postprocess.utils import ObjectPredictionList, has_match, merge_object_prediction_pair
from easyams.sahi_onnx.prediction import ObjectPrediction
from easyams.sahi_onnx.utils.import_utils import check_requirements

logger = logging.getLogger(__name__)

def batched_greedy_nmm(
    object_predictions_as_array: np.ndarray, #torch.tensor,
    match_metric: str = "IOU",
    match_threshold: float = 0.5,
):
    """
    Apply greedy version of non-maximum merging per category to avoid detecting
    too many overlapping bounding boxes for a given object.
    Args:
        object_predictions_as_tensor: (tensor) The location preds for the image
            along with the class predscores, Shape: [num_boxes,5].
        match_metric: (str) IOU or IOS
        match_threshold: (float) The overlap thresh for
            match metric.
    Returns:
        keep_to_merge_list: (Dict[int:List[int]]) mapping from prediction indices
        to keep to a list of prediction indices to be merged.
    """
    # category_ids = object_predictions_as_tensor[:, 5].squeeze()
    category_ids = object_predictions_as_array[:, 5]
    keep_to_merge_list = {}

    # for category_id in torch.unique(category_ids):
    #     curr_indices = torch.where(category_ids == category_id)[0]
    #     curr_keep_to_merge_list = greedy_nmm(object_predictions_as_tensor[curr_indices], match_metric, match_threshold)
    #     curr_indices_list = curr_indices.tolist()
    #     for curr_keep, curr_merge_list in curr_keep_to_merge_list.items():
    #         keep = curr_indices_list[curr_keep]
    #         merge_list = [curr_indices_list[curr_merge_ind] for curr_merge_ind in curr_merge_list]
    #         keep_to_merge_list[keep] = merge_list

    for category_id in np.unique(category_ids):
        # Get indices of predictions belonging to the current category
        curr_indices = np.where(category_ids == category_id)[0]
        # Apply greedy_nmm to the subset of predictions for the current category
        curr_keep_to_merge_list = greedy_nmm(
            object_predictions_as_array[curr_indices], match_metric, match_threshold
        )
        # Map the indices back to the original array
        curr_indices_list = curr_indices.tolist()
        for curr_keep, curr_merge_list in curr_keep_to_merge_list.items():
            keep = curr_indices_list[curr_keep]
            merge_list = [curr_indices_list[curr_merge_ind] for curr_merge_ind in curr_merge_list]
            keep_to_merge_list[keep] = merge_list

    return keep_to_merge_list


def greedy_nmm(
    object_predictions_as_array: np.ndarray,
    match_metric: str = "IOU",
    match_threshold: float = 0.5,
):
    """
    Apply greedy version of non-maximum merging to avoid detecting too many
    overlapping bounding boxes for a given object.
    Args:
        object_predictions_as_tensor: (tensor) The location preds for the image
            along with the class predscores, Shape: [num_boxes,5].
        object_predictions_as_list: ObjectPredictionList Object prediction objects
            to be merged.
        match_metric: (str) IOU or IOS
        match_threshold: (float) The overlap thresh for
            match metric.
    Returns:
        keep_to_merge_list: (Dict[int:List[int]]) mapping from prediction indices
        to keep to a list of prediction indices to be merged.
    """
    keep_to_merge_list = {}

    # we extract coordinates for every
    # prediction box present in P
    x1 = object_predictions_as_array[:, 0]
    y1 = object_predictions_as_array[:, 1]
    x2 = object_predictions_as_array[:, 2]
    y2 = object_predictions_as_array[:, 3]

    # we extract the confidence scores as well
    scores = object_predictions_as_array[:, 4]

    # calculate area of every block in P
    areas = (x2 - x1) * (y2 - y1)

    # sort the prediction boxes in P
    # according to their confidence scores
    # order = scores.argsort()
    order = np.argsort(scores)

    while len(order) > 0:
        # extract the index of the
        # prediction with highest score
        # we call this prediction S
        idx = order[-1]

        # remove S from P
        order = order[:-1]

        # sanity check
        if len(order) == 0:
            keep_to_merge_list[idx.tolist()] = []
            break

        # select coordinates of BBoxes according to
        # # the indices in order
        # xx1 = torch.index_select(x1, dim=0, index=order)
        # xx2 = torch.index_select(x2, dim=0, index=order)
        # yy1 = torch.index_select(y1, dim=0, index=order)
        # yy2 = torch.index_select(y2, dim=0, index=order)

        # # find the coordinates of the intersection boxes
        # xx1 = torch.max(xx1, x1[idx])
        # yy1 = torch.max(yy1, y1[idx])
        # xx2 = torch.min(xx2, x2[idx])
        # yy2 = torch.min(yy2, y2[idx])

        # # find height and width of the intersection boxes
        # w = xx2 - xx1
        # h = yy2 - yy1

        # take max with 0.0 to avoid negative w and h
        # due to non-overlapping boxes
        # w = torch.clamp(w, min=0.0)
        # h = torch.clamp(h, min=0.0)

        xx1 = np.maximum(x1[order], x1[idx])
        yy1 = np.maximum(y1[order], y1[idx])
        xx2 = np.minimum(x2[order], x2[idx])
        yy2 = np.minimum(y2[order], y2[idx])

        # Find height and width of the intersection boxes
        w = np.maximum(0.0, xx2 - xx1)
        h = np.maximum(0.0, yy2 - yy1)

        # find the intersection area
        inter = w * h

        # find the areas of BBoxes according the indices in order
        # rem_areas = torch.index_select(areas, dim=0, index=order)
        rem_areas = areas[order]

        if match_metric == "IOU":
            # find the union of every prediction T in P
            # with the prediction S
            # Note that areas[idx] represents area of S
            union = (rem_areas - inter) + areas[idx]
            # find the IoU of every prediction in P with S
            match_metric_value = inter / union

        elif match_metric == "IOS":
            # find the smaller area of every prediction T in P
            # with the prediction S
            # Note that areas[idx] represents area of S
            # smaller = torch.min(rem_areas, areas[idx])
            smaller = np.minimum(rem_areas, areas[idx])
            # find the IoS of every prediction in P with S
            match_metric_value = inter / smaller
        else:
            raise ValueError()

        # keep the boxes with IoU/IoS less than thresh_iou
        mask = match_metric_value < match_threshold
        # matched_box_indices = order[(mask == False).nonzero().flatten()].flip(dims=(0,))
        # unmatched_indices = order[(mask == True).nonzero().flatten()]
        matched_box_indices = order[~mask]
        unmatched_indices = order[mask]

        # update box pool
        # order = unmatched_indices[scores[unmatched_indices].argsort()]
        order = unmatched_indices[np.argsort(scores[unmatched_indices])]

        # create keep_ind to merge_ind_list mapping
        # keep_to_merge_list[idx.tolist()] = []
        keep_to_merge_list[idx] = []

        for matched_box_ind in matched_box_indices.tolist():
            # keep_to_merge_list[idx.tolist()].append(matched_box_ind)
            keep_to_merge_list[idx].append(matched_box_ind)

    return keep_to_merge_list


class PostprocessPredictions:
    """Utilities for calculating IOU/IOS based match for given ObjectPredictions"""

    def __init__(
        self,
        match_threshold: float = 0.5,
        match_metric: str = "IOU",
        class_agnostic: bool = True,
    ):
        self.match_threshold = match_threshold
        self.class_agnostic = class_agnostic
        self.match_metric = match_metric

        check_requirements(["torch"])

    def __call__(self):
        raise NotImplementedError()


class GreedyNMMPostprocess(PostprocessPredictions):
    def __call__(
        self,
        object_predictions: List[ObjectPrediction],
    ):
        object_prediction_list = ObjectPredictionList(object_predictions)
        # object_predictions_as_torch = object_prediction_list.totensor()
        object_predictions_as_array = object_prediction_list.tonumpy()
        if self.class_agnostic:
            keep_to_merge_list = greedy_nmm(
                object_predictions_as_array,
                match_threshold=self.match_threshold,
                match_metric=self.match_metric,
            )
        else:
            keep_to_merge_list = batched_greedy_nmm(
                object_predictions_as_array,
                match_threshold=self.match_threshold,
                match_metric=self.match_metric,
            )

        selected_object_predictions = []
        for keep_ind, merge_ind_list in keep_to_merge_list.items():
            for merge_ind in merge_ind_list:
                if has_match(
                    object_prediction_list[keep_ind].tolist(),
                    object_prediction_list[merge_ind].tolist(),
                    self.match_metric,
                    self.match_threshold,
                ):
                    object_prediction_list[keep_ind] = merge_object_prediction_pair(
                        object_prediction_list[keep_ind].tolist(), object_prediction_list[merge_ind].tolist()
                    )
            selected_object_predictions.append(object_prediction_list[keep_ind].tolist())

        return selected_object_predictions
