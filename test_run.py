import coverage
import pytest
import os

class ExtractOutputPlugin:
    def __init__(self):
        self.results = {}
        self.failing_details = {}

    def pytest_runtest_logreport(self, report):
        if report.when == "call":
            name = report.nodeid.split("::")[-1]
            if report.failed:
                self.results[name] = "failed"
                self.failing_details[name] = str(report.longrepr)
            elif report.passed:
                self.results[name] = "passed"

plugin = ExtractOutputPlugin()

for test_node in ["test_is_prime_0", "test_is_prime_1"]:
    cov = coverage.Coverage(source=['src'])
    cov.start()
    pytest.main([f"tests/test_humaneval_31.py::{test_node}", "-q", "--tb=short"], plugins=[plugin])
    cov.stop()
    cov.save()
    data = cov.get_data()
    f = os.path.abspath("src/humaneval_31.py")
    print(test_node, data.lines(f))

print(plugin.results)
print(plugin.failing_details)

