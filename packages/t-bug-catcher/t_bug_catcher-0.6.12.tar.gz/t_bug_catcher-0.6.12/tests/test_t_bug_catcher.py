import os
import unittest
from unittest.mock import PropertyMock, patch

from t_bug_catcher.bug_catcher import BugCatcher
from t_bug_catcher.config import CONFIG
from t_bug_catcher.utils import logger


class TestBugCatcher(unittest.TestCase):
    """TestBugCatcher class."""

    def setUp(self):
        """Set up."""
        self.bug_catcher = BugCatcher()

    def test_report_error_with_local_environment(self):
        """Test report_error function."""
        with patch.object(logger, "warning") as mock_warning:
            self.bug_catcher.report_error()
            mock_warning.assert_called_once_with("Reporting an error is not supported in local environment.")

    @patch.object(CONFIG, "ENVIRONMENT", "robocloud")
    def test_report_error_with_no_configurations(self):
        """Test report_error function."""
        with patch.object(logger, "warning") as mock_warning:
            self.bug_catcher.report_error()
            mock_warning.assert_called_once_with(
                "Jira and BugSnag are not configured. Please configure them before reporting an error."
            )

    def test_jira_configure(self):
        """Test jira_configure function."""
        self.bug_catcher.configure.jira(
            login=os.getenv("JIRA_LOGIN"),
            api_token=os.getenv("JIRA_API_TOKEN"),
            project_key=os.getenv("JIRA_PROJECT_KEY"),
        )
        assert self.bug_catcher.configure.is_jira_configured

    def test_bugsnag_configure(self):
        """Test bugsnag_configure function."""
        self.bug_catcher.configure.bugsnag(api_key=os.getenv("BUGSNAG_API_KEY"))
        assert self.bug_catcher.configure.is_bugsnag_configured

    def test_attach_file(self):
        """Test attach_file function."""
        ex = Exception("some error")
        self.bug_catcher.attach_file_to_exception(exception=ex, attachment="test.txt")
        assert hasattr(ex, "custom_attachments")

    @patch.object(CONFIG, "ENVIRONMENT", "robocloud")
    def test_report_error_success(self):
        """Test report_error function when everything works correctly."""
        with patch.object(
            self.bug_catcher, "_BugCatcher__configurator", new_callable=PropertyMock
        ) as mock_configurator:
            patch.object(mock_configurator, "is_jira_configured", return_value=True)
            patch.object(mock_configurator, "is_bugsnag_configured", return_value=True)
            with patch.object(self.bug_catcher._BugCatcher__jira, "report_error") as mock_jira_report:
                mock_jira_report.return_value = {"key": "TEST-123", "id": "10001"}
                try:
                    raise Exception("Test exception")
                except Exception as ex:
                    with patch.object(logger, "info") as mock_info:
                        self.bug_catcher.report_error(exception=ex)
                        mock_jira_report.assert_called_once()
                        mock_info.assert_called()
                        if mock_info.call_args:
                            info_message = mock_info.call_args[0][0]
                            self.assertTrue("reported" in info_message.lower())

    @patch.object(CONFIG, "ENVIRONMENT", "robocloud")
    def test_report_error_failure(self):
        """Test report_error function when Jira API fails (original test intention)."""
        with patch.object(
            self.bug_catcher, "_BugCatcher__configurator", new_callable=PropertyMock
        ) as mock_configurator:
            patch.object(mock_configurator, "is_jira_configured", return_value=True)
            patch.object(mock_configurator, "is_bugsnag_configured", return_value=True)
            with patch.object(self.bug_catcher._BugCatcher__jira, "report_error") as mock_jira_report:
                mock_jira_report.return_value = False  # Simulate API failure

                try:
                    raise Exception("Test exception")
                except Exception as ex:
                    with patch.object(logger, "warning"):
                        self.bug_catcher.report_error(exception=ex)
                        mock_jira_report.assert_called_once()


if __name__ == "__main__":
    unittest.main()
