from typing import Optional

import matplotlib
import numpy as np
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    precision_score,
    recall_score,
    roc_auc_score,
)

from grizzly_main.orchestrator.prefect_poc.tools.mlflow_tools import save_plot

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402 # pylint: disable=C0411,C0412,C0413

metric_func_dict = {
    "accuracy": accuracy_score,
    "roc_auc": roc_auc_score,
    "f1_score": f1_score,
    "precision": precision_score,
    "recall": recall_score,
    "confusion_matrix": confusion_matrix,
    "mae": mean_absolute_error,
}


def plot_confusion_matrix(
    cm_result: np.ndarray,
    enable_mlflow_tracking: bool = False,
    mlflow_artifact_path: Optional[str] = None,
    fig_path: str = "confusion_matrix.png",
) -> None:
    """
    Create a heatmap for visualization of the confusion matrix result

    :param cm_result: Confusion matrix result
    :param enable_mlflow_tracking: True if MLflow tracking is enabled, False otherwise.
    :param mlflow_artifact_path: MLFlow artifact path
    :param fig_path: Figure path
    :return: None
    """
    disp = ConfusionMatrixDisplay(confusion_matrix=cm_result).plot(
        cmap=plt.cm.Blues,
    )
    disp.ax_.set_title("Confusion matrix", None)
    save_plot(
        plot=disp.figure_,
        enable_mlflow_tracking=enable_mlflow_tracking,
        mlflow_artifact_path=mlflow_artifact_path,
        fig_path=fig_path,
    )
