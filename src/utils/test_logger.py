import os
import unittest
import logging
from src.utils.logger import setup_logger, get_log_directory

class TestLogger(unittest.TestCase):
    def test_logger_setup(self):
        """Test that the logger is properly configured"""
        logger = setup_logger()
        
        # Test logger level
        self.assertEqual(logger.level, logging.DEBUG, "Logger level should be DEBUG")
        
        # Test that logger has handlers
        self.assertTrue(len(logger.handlers) > 0, "Logger should have handlers")
        
        # Check that log directory exists
        log_dir = get_log_directory()
        self.assertTrue(os.path.exists(log_dir), "Log directory should exist")
        
        # Test logging functionality
        logger.debug("Debug test message")
        logger.info("Info test message")
        logger.warning("Warning test message")
        logger.error("Error test message")
        
        # Check that log file exists
        latest_log_path = os.path.join(log_dir, 'latest.log')
        self.assertTrue(os.path.exists(latest_log_path), "latest.log file should exist")
        
        # Basic check that log has content
        with open(latest_log_path, 'r', encoding='utf-8') as f:
            log_content = f.read()
            self.assertIn("Debug test message", log_content)
            self.assertIn("Info test message", log_content)
            self.assertIn("Warning test message", log_content)
            self.assertIn("Error test message", log_content)
            
        return True

if __name__ == '__main__':
    unittest.main() 