import os
import sys
import json
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from experiment.scripts.sbfl_runner import ExtractOutputPlugin, main

def test_extract_output_plugin():
    # Arrange
    plugin = ExtractOutputPlugin()
    
    report_failed = MagicMock()
    report_failed.when = "call"
    report_failed.nodeid = "test_file.py::test_fail"
    report_failed.failed = True
    report_failed.passed = False
    report_failed.longrepr = "error"
    
    report_passed = MagicMock()
    report_passed.when = "call"
    report_passed.nodeid = "test_file.py::test_pass"
    report_passed.failed = False
    report_passed.passed = True
    
    report_setup = MagicMock()
    report_setup.when = "setup"
    
    # Act
    plugin.pytest_runtest_logreport(report_failed)
    plugin.pytest_runtest_logreport(report_passed)
    plugin.pytest_runtest_logreport(report_setup)
    
    # Assert
    assert plugin.results["test_fail"] == "failed"
    assert plugin.failing_details["test_fail"] == "error"
    assert plugin.results["test_pass"] == "passed"

@patch('experiment.scripts.sbfl_runner.subprocess.run')
@patch('experiment.scripts.sbfl_runner.pytest.main')
@patch('experiment.scripts.sbfl_runner.coverage.Coverage')
@patch('experiment.scripts.sbfl_runner.sys.argv', ['sbfl_runner.py', 'test_1', 'src/test_1.py', 'tests/test_test_1.py'])
def test_sbfl_runner_main(mock_coverage, mock_pytest_main, mock_subprocess):
    # Arrange
    mock_subprocess.return_value = MagicMock(stdout="test_test_1.py::test_pass \n test_test_1.py::test_fail \n", stderr="")
    
    mock_cov_instance = MagicMock()
    mock_coverage.return_value = mock_cov_instance
    mock_data = MagicMock()
    mock_data.lines.return_value = [1, 2, 3]
    mock_cov_instance.get_data.return_value = mock_data
    
    with patch('builtins.open', new_callable=MagicMock) as mock_open_file:
        # Act
        main()
        
        # Assert
        assert mock_pytest_main.call_count == 2
        mock_open_file.assert_called_with("sbfl_runner_out.json", "w")

@patch('experiment.scripts.sbfl_runner.subprocess.run')
@patch('experiment.scripts.sbfl_runner.sys.argv', ['sbfl_runner.py', 'test_1', 'src/test_1.py', 'tests/test_test_1.py'])
def test_sbfl_runner_main_no_nodes(mock_subprocess):
    # Arrange
    mock_subprocess.return_value = MagicMock(stdout="", stderr="error")
    
    with patch('builtins.open', new_callable=MagicMock) as mock_open_file:
        # Act
        main()
        
        # Assert
        mock_open_file.assert_any_call("sbfl_runner_error.log", "w")

@patch('experiment.scripts.sbfl_runner.sys.argv', ['sbfl_runner.py'])
def test_sbfl_runner_main_wrong_args():
    # Arrange
    # Missing arguments
    
    # Act / Assert
    try:
        main()
    except SystemExit:
        pass
