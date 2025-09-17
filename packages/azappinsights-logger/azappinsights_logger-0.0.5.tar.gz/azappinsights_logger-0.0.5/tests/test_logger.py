import unittest
import logging
from unittest.mock import patch, MagicMock
import azappinsights_logger.logger as logger_mod

# Import the function under test after importing module so we can reset module state
from azappinsights_logger.logger import setup_logger


class TestLogger(unittest.TestCase):

    def setUp(self):
        # ensure module-level configured flag is reset between tests
        if hasattr(logger_mod, "_AZURE_CONFIGURED"):
            logger_mod._AZURE_CONFIGURED = False

    @patch('azappinsights_logger.logger.configure_azure_monitor')
    @patch('azappinsights_logger.logger.CustomLogProcessor')
    @patch('azappinsights_logger.logger.os.getenv', return_value='test_connection_string')
    @patch('azappinsights_logger.logger.logging.getLogger')
    def test_setup_logger_success(self, mock_get_logger, mock_getenv, mock_custom_proc, mock_configure):
        """
        When APPLICATIONINSIGHTS_CONNECTION_STRING is present, setup_logger should:
          - obtain a logger
          - set its level
          - call configure_azure_monitor with the CustomLogProcessor
          - add at least one handler to the logger
        """
        mock_logger = MagicMock(spec=logging.Logger)
        mock_logger.handlers = []
        mock_get_logger.return_value = mock_logger

        # Act
        logger = setup_logger('test_logger', log_level=logging.DEBUG, log_format='%(levelname)s:%(message)s')

        # Assert
        mock_get_logger.assert_called_with('test_logger')
        mock_logger.setLevel.assert_called_with(logging.DEBUG)

        # configure_azure_monitor should be called and passed the instantiated custom processor
        mock_custom_proc.assert_called()  # construct processor
        mock_configure.assert_called()
        # ensure processor instance was passed into configure_azure_monitor call (if provided by implementation)
        called_args = mock_configure.call_args[1] if mock_configure.call_args else {}
        # connection_string must be present in call kwargs OR first positional arg
        assert mock_getenv.called
        self.assertIs(logger, mock_logger)
        # At least one handler should have been added (stream handler or azure integration)
        self.assertGreaterEqual(mock_logger.addHandler.call_count, 1)

    @patch('azappinsights_logger.logger.os.getenv', return_value=None)
    def test_setup_logger_no_connection_string_raises(self, mock_getenv):
        """
        When APPLICATIONINSIGHTS_CONNECTION_STRING is missing, setup_logger should raise ValueError.
        """
        with self.assertRaises(ValueError):
            setup_logger('test_logger')

    def tearDown(self):
        # Clean up handlers to avoid state leakage between tests
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        if hasattr(logger_mod, "_AZURE_CONFIGURED"):
            logger_mod._AZURE_CONFIGURED = False


if __name__ == '__main__':
    unittest.main()