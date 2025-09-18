"""
Comprehensive unit tests for logging modules.

Tests logging setup and configuration functionality.
"""

import pytest
import logging
import sys
import tempfile
import os
from unittest.mock import patch, Mock, MagicMock

from mcmqtt.logging.setup import setup_logging


class TestSetupLogging:
    """Test logging configuration functionality."""
    
    def test_setup_logging_default_stderr(self):
        """Test logging setup with default stderr handler."""
        with patch('logging.basicConfig') as mock_basic, \
             patch('structlog.configure') as mock_structlog:
            
            setup_logging()
            
            # Verify logging.basicConfig called with stderr handler
            mock_basic.assert_called_once()
            call_args = mock_basic.call_args
            assert call_args[1]['level'] == logging.WARNING
            assert len(call_args[1]['handlers']) == 1
            assert isinstance(call_args[1]['handlers'][0], logging.StreamHandler)
            assert call_args[1]['handlers'][0].stream == sys.stderr
            
            # Verify structlog configured
            mock_structlog.assert_called_once()
    
    def test_setup_logging_file_handler(self):
        """Test logging setup with file handler."""
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            log_file = tf.name
        
        try:
            with patch('logging.basicConfig') as mock_basic, \
                 patch('structlog.configure') as mock_structlog:
                
                setup_logging(log_level="INFO", log_file=log_file)
                
                # Verify logging.basicConfig called with file handler
                mock_basic.assert_called_once()
                call_args = mock_basic.call_args
                assert call_args[1]['level'] == logging.INFO
                assert len(call_args[1]['handlers']) == 1
                assert isinstance(call_args[1]['handlers'][0], logging.FileHandler)
                
                # Verify structlog configured
                mock_structlog.assert_called_once()
        finally:
            os.unlink(log_file)
    
    def test_setup_logging_debug_level(self):
        """Test logging setup with DEBUG level."""
        with patch('logging.basicConfig') as mock_basic, \
             patch('structlog.configure') as mock_structlog:
            
            setup_logging(log_level="DEBUG")
            
            call_args = mock_basic.call_args
            assert call_args[1]['level'] == logging.DEBUG
    
    def test_setup_logging_info_level(self):
        """Test logging setup with INFO level."""
        with patch('logging.basicConfig') as mock_basic, \
             patch('structlog.configure') as mock_structlog:
            
            setup_logging(log_level="INFO")
            
            call_args = mock_basic.call_args
            assert call_args[1]['level'] == logging.INFO
    
    def test_setup_logging_warning_level(self):
        """Test logging setup with WARNING level."""
        with patch('logging.basicConfig') as mock_basic, \
             patch('structlog.configure') as mock_structlog:
            
            setup_logging(log_level="WARNING")
            
            call_args = mock_basic.call_args
            assert call_args[1]['level'] == logging.WARNING
    
    def test_setup_logging_error_level(self):
        """Test logging setup with ERROR level."""
        with patch('logging.basicConfig') as mock_basic, \
             patch('structlog.configure') as mock_structlog:
            
            setup_logging(log_level="ERROR")
            
            call_args = mock_basic.call_args
            assert call_args[1]['level'] == logging.ERROR
    
    def test_setup_logging_format_string(self):
        """Test logging setup with correct format string."""
        with patch('logging.basicConfig') as mock_basic, \
             patch('structlog.configure') as mock_structlog:
            
            setup_logging()
            
            call_args = mock_basic.call_args
            expected_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            assert call_args[1]['format'] == expected_format
    
    def test_setup_logging_structlog_configuration(self):
        """Test structlog configuration details."""
        with patch('logging.basicConfig') as mock_basic, \
             patch('structlog.configure') as mock_structlog:
            
            setup_logging()
            
            # Verify structlog.configure was called
            mock_structlog.assert_called_once()
            
            # Check the call arguments
            call_args = mock_structlog.call_args
            assert 'processors' in call_args[1]
            assert 'wrapper_class' in call_args[1]
            assert 'logger_factory' in call_args[1]
            assert 'cache_logger_on_first_use' in call_args[1]
            
            # Verify cache setting
            assert call_args[1]['cache_logger_on_first_use'] is True
    
    def test_setup_logging_structlog_processors(self):
        """Test structlog processor configuration."""
        import structlog
        
        with patch('logging.basicConfig'), \
             patch('structlog.configure') as mock_structlog:
            
            setup_logging()
            
            call_args = mock_structlog.call_args
            processors = call_args[1]['processors']
            
            # Should have multiple processors
            assert len(processors) == 5
            
            # Verify specific processors are included
            processor_names = [proc.__name__ if hasattr(proc, '__name__') else str(proc) for proc in processors]
            assert any('filter_by_level' in str(proc) for proc in processor_names)
            assert any('add_logger_name' in str(proc) for proc in processor_names)
            assert any('add_log_level' in str(proc) for proc in processor_names)
    
    def test_setup_logging_case_insensitive_levels(self):
        """Test logging setup with case variations in log level."""
        test_cases = [
            ("debug", logging.DEBUG),
            ("DEBUG", logging.DEBUG),
            ("Debug", logging.DEBUG),
            ("info", logging.INFO),
            ("INFO", logging.INFO),
            ("warning", logging.WARNING),
            ("WARNING", logging.WARNING),
            ("error", logging.ERROR),
            ("ERROR", logging.ERROR)
        ]
        
        for log_level_str, expected_level in test_cases:
            with patch('logging.basicConfig') as mock_basic, \
                 patch('structlog.configure'):
                
                setup_logging(log_level=log_level_str)
                
                call_args = mock_basic.call_args
                assert call_args[1]['level'] == expected_level
    
    def test_setup_logging_multiple_calls(self):
        """Test multiple calls to setup_logging."""
        with patch('logging.basicConfig') as mock_basic, \
             patch('structlog.configure') as mock_structlog:
            
            # First call
            setup_logging(log_level="DEBUG")
            
            # Second call with different settings
            setup_logging(log_level="ERROR", log_file="/tmp/test.log")
            
            # Both calls should work
            assert mock_basic.call_count == 2
            assert mock_structlog.call_count == 2
    
    def test_setup_logging_file_handler_creation(self):
        """Test file handler creation with actual file."""
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            log_file = tf.name
        
        try:
            with patch('logging.basicConfig') as mock_basic, \
                 patch('structlog.configure'):
                
                setup_logging(log_file=log_file)
                
                # Verify FileHandler was created
                call_args = mock_basic.call_args
                handler = call_args[1]['handlers'][0]
                assert isinstance(handler, logging.FileHandler)
                assert handler.baseFilename == os.path.abspath(log_file)
        finally:
            os.unlink(log_file)
    
    def test_setup_logging_stderr_stream_handler(self):
        """Test stderr stream handler configuration."""
        with patch('logging.basicConfig') as mock_basic, \
             patch('structlog.configure'):
            
            setup_logging()
            
            call_args = mock_basic.call_args
            handler = call_args[1]['handlers'][0]
            assert isinstance(handler, logging.StreamHandler)
            assert handler.stream == sys.stderr
    
    def test_setup_logging_no_stdout_interference(self):
        """Test that logging doesn't interfere with stdout."""
        with patch('logging.basicConfig') as mock_basic, \
             patch('structlog.configure'):
            
            setup_logging()
            
            # Verify no stdout handler
            call_args = mock_basic.call_args
            handlers = call_args[1]['handlers']
            
            for handler in handlers:
                if isinstance(handler, logging.StreamHandler):
                    assert handler.stream != sys.stdout