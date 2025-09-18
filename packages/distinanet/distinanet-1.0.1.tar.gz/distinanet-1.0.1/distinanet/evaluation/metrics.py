import numpy as np

def compute_overlap(a, b):
    """
    Parameters
    ----------
    a: (N, 4) ndarray of float
    b: (K, 4) ndarray of float
    Returns
    -------
    overlaps: (N, K) ndarray of overlap between boxes and query_boxes
    """
    area = (b[:, 2] - b[:, 0]) * (b[:, 3] - b[:, 1])

    iw = np.minimum(np.expand_dims(a[:, 2], axis=1), b[:, 2]) - np.maximum(np.expand_dims(a[:, 0], 1), b[:, 0])
    ih = np.minimum(np.expand_dims(a[:, 3], axis=1), b[:, 3]) - np.maximum(np.expand_dims(a[:, 1], 1), b[:, 1])

    iw = np.maximum(iw, 0)
    ih = np.maximum(ih, 0)

    ua = np.expand_dims((a[:, 2] - a[:, 0]) * (a[:, 3] - a[:, 1]), axis=1) + area - iw * ih

    ua = np.maximum(ua, np.finfo(float).eps)

    intersection = iw * ih

    return intersection / ua


def compute_ap(recall, precision):
    """ Compute the average precision, given the recall and precision curves.
    Code originally from https://github.com/rbgirshick/py-faster-rcnn.
    # Arguments
        recall:    The recall curve (list).
        precision: The precision curve (list).
    # Returns
        The average precision as computed in py-faster-rcnn.
    """
    # correct AP calculation
    # first append sentinel values at the end
    mrec = np.concatenate(([0.], recall, [1.]))
    mpre = np.concatenate(([0.], precision, [0.]))

    # compute the precision envelope
    for i in range(mpre.size - 1, 0, -1):
        mpre[i - 1] = np.maximum(mpre[i - 1], mpre[i])

    # to calculate area under PR curve, look for points
    # where X axis (recall) changes value
    i = np.where(mrec[1:] != mrec[:-1])[0]

    # and sum (\Delta recall) * prec
    ap = np.sum((mrec[i + 1] - mrec[i]) * mpre[i + 1])
    return ap

def mean_absolute_error(y_true, y_pred):
    return np.mean(np.abs(y_pred - y_true))

def root_mean_squared_error(y_true, y_pred):
    return np.sqrt(np.mean((y_pred - y_true)**2))

def log_root_mean_squared_error(y_pred, y_true):

    # Ensure there are no negative values
    y_true = np.maximum(y_true, 0)  # Clamp at zero
    y_pred = np.maximum(y_pred, 0)

    # Adding 1 and taking logs of predictions and true values
    log_true = np.log(y_true + 1)
    log_pred = np.log(y_pred + 1)

    # Calculating the squared differences of the logs
    squared_log_diff = (log_true - log_pred) ** 2

    # Mean of the squared differences
    mean_squared_log_diff = np.mean(squared_log_diff)

    # Taking the square root to compute RMSE
    log_rmse = np.sqrt(mean_squared_log_diff)

    return log_rmse

def mean_percentage_error(y_true, y_pred):
    return np.mean((y_pred - y_true) / y_true) * 100

def mean_relative_error(y_true, y_pred):
    return np.mean(np.abs((y_true - y_pred) / np.maximum(y_true, 1)))
