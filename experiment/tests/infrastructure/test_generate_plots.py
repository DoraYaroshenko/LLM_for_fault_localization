import pytest
import json
import os
from unittest.mock import patch, mock_open, MagicMock

from experiment.scripts.generate_plots import generate_plots

@patch("experiment.scripts.generate_plots.plt")
@patch("experiment.scripts.generate_plots.os.makedirs")
@patch("experiment.scripts.generate_plots.os.path.exists")
def test_generate_plots_dir_not_exists(mock_exists, mock_makedirs, mock_plt):
    mock_exists.return_value = False
    mock_plt.subplots.return_value = (MagicMock(), MagicMock())
    
    mock_metrics = {
        "model_1": {
            "A": {"top_1_acc": 0.1, "top_3_acc": 0.2, "region_acc": 0.3},
            "B": {"top_1_acc": 0.2, "top_3_acc": 0.3, "region_acc": 0.4},
            "C": {"top_1_acc": 0.3, "top_3_acc": 0.4, "region_acc": 0.5},
            "D": {"top_1_acc": 0.4, "top_3_acc": 0.5, "region_acc": 0.6},
            "overall": {"top_1_acc": 0.25, "top_3_acc": 0.35, "region_acc": 0.45}
        },
        "model_2_very_long_name_here": {
            "A": {"top_1_acc": 0.1, "top_3_acc": 0.2, "region_acc": 0.3},
            "B": {"top_1_acc": 0.2, "top_3_acc": 0.3, "region_acc": 0.4},
            "C": {"top_1_acc": 0.3, "top_3_acc": 0.4, "region_acc": 0.5},
            "D": {"top_1_acc": 0.4, "top_3_acc": 0.5, "region_acc": 0.6},
            "overall": {"top_1_acc": 0.25, "top_3_acc": 0.35, "region_acc": 0.45}
        },
        "overall": {}
    }
    
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_metrics))):
        generate_plots()
        
    mock_exists.assert_called_once_with("experiment/website/assets")
    mock_makedirs.assert_called_once_with("experiment/website/assets")
    
    # 2 models -> 2 condition plots + 1 overall plot = 3 savefig calls
    assert mock_plt.savefig.call_count == 3
    
@patch("experiment.scripts.generate_plots.plt")
@patch("experiment.scripts.generate_plots.os.makedirs")
@patch("experiment.scripts.generate_plots.os.path.exists")
def test_generate_plots_dir_exists(mock_exists, mock_makedirs, mock_plt):
    mock_exists.return_value = True
    mock_plt.subplots.return_value = (MagicMock(), MagicMock())
    
    mock_metrics = {
        "model_1": {
            "A": {"top_1_acc": 0.1, "top_3_acc": 0.2, "region_acc": 0.3},
            "B": {"top_1_acc": 0.2, "top_3_acc": 0.3, "region_acc": 0.4},
            "C": {"top_1_acc": 0.3, "top_3_acc": 0.4, "region_acc": 0.5},
            "D": {"top_1_acc": 0.4, "top_3_acc": 0.5, "region_acc": 0.6},
            "overall": {"top_1_acc": 0.25, "top_3_acc": 0.35, "region_acc": 0.45}
        },
        "overall": {}
    }
    
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_metrics))):
        generate_plots()
        
    mock_exists.assert_called_once_with("experiment/website/assets")
    mock_makedirs.assert_not_called()
