import os
import sys
import tempfile
import json
from unittest.mock import patch, mock_open

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from experiment.scripts.generate_report import generate_report

@patch('experiment.scripts.generate_report.os.makedirs')
def test_generate_report(mock_makedirs):
    # Arrange
    metrics = {
        "model_1": {
            "A": {"top_1_acc": 0.5, "top_3_acc": 0.8, "region_acc": 0.9, "invalid_rate": 0.1, "mrr": 0.6},
            "B": {"top_1_acc": 0.6, "top_3_acc": 0.8, "region_acc": 0.9, "invalid_rate": 0.1, "mrr": 0.7},
            "C": {"top_1_acc": 0.7, "top_3_acc": 0.8, "region_acc": 0.9, "invalid_rate": 0.1, "mrr": 0.8},
            "D": {"top_1_acc": 0.8, "top_3_acc": 0.9, "region_acc": 0.9, "invalid_rate": 0.1, "mrr": 0.9},
            "overall": {"top_1_acc": 0.65, "top_3_acc": 0.825, "region_acc": 0.9, "invalid_rate": 0.1, "mrr": 0.75}
        },
        "overall": {}
    }
    metadata = [
        {"task_id": "test_1", "safe_id": "test_1", "entry_point": "f1", "num_tests": 5}
    ]
    
    mock_metrics_json = json.dumps(metrics)
    mock_metadata_json = json.dumps(metadata)
    
    def side_effect_open(path, *args, **kwargs):
        if "metrics.json" in path:
            return mock_open(read_data=mock_metrics_json)()
        elif "final_metadata.json" in path:
            return mock_open(read_data=mock_metadata_json)()
        else:
            return mock_open()()
            
    with patch('builtins.open', side_effect=side_effect_open) as m_open:
        with patch('experiment.scripts.generate_report.os.path.exists', return_value=False):
            # Act
            generate_report()
            
    # Assert
    mock_makedirs.assert_called_once_with("experiment/website")
    assert m_open.call_count >= 4 # read 2, write 2
