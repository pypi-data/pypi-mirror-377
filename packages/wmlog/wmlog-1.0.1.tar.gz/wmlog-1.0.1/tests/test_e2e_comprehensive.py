"""
Comprehensive End-to-End Test Suite for WML (Websocket MQTT Logging) Package
Tests all core functionality including logging, CLI, broadcasting, and integration patterns
"""

import asyncio
import json
import os
import tempfile
import time
import threading
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import pytest
import structlog
from click.testing import CliRunner

# Import wmlog components
from wmlog import WMLLogger, LoggingConfig, LogContext, WebSocketBroadcaster, MQTTBroadcaster
from wmlog.cli import cli


class TestWMLLoggerCore:
    """Test core WMLLogger functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.temp_dir, "test.log")
        
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_basic_logging_functionality(self):
        """Test basic logging operations"""
        config = LoggingConfig(
            service_name="test-service",
            log_level="DEBUG",
            console_enabled=True,
            file_enabled=True,
            file_path=self.log_file
        )
        
        logger = WMLLogger.get_logger(config)
        
        # Test all log levels
        logger.debug("Debug message", test_field="debug_value")
        logger.info("Info message", test_field="info_value")
        logger.warning("Warning message", test_field="warning_value")
        logger.error("Error message", test_field="error_value")
        logger.critical("Critical message", test_field="critical_value")
        
        # Verify log file was created and contains entries
        assert os.path.exists(self.log_file)
        with open(self.log_file, 'r') as f:
            log_content = f.read()
            assert "Debug message" in log_content
            assert "Info message" in log_content
            assert "Warning message" in log_content
            assert "Error message" in log_content
            assert "Critical message" in log_content
            assert "test_field" in log_content
    
    def test_context_enrichment(self):
        """Test log context enrichment functionality"""
        context = LogContext(
            service_name="context-test-service",
            version="1.0.0",
            environment="test",
            request_id="req-123",
            user_id="user-456",
            custom_fields={"module": "test_module", "operation": "test_op"}
        )
        
        config = LoggingConfig(
            service_name="context-test-service",
            file_enabled=True,
            file_path=self.log_file
        )
        
        logger = WMLLogger.get_logger(config, context=context)
        logger.info("Context test message")
        
        # Verify context fields in log
        with open(self.log_file, 'r') as f:
            log_content = f.read()
            assert "req-123" in log_content
            assert "user-456" in log_content
            assert "test_module" in log_content
            assert "test_op" in log_content
            assert "1.0.0" in log_content
    
    def test_context_update_and_bind(self):
        """Test dynamic context updates and binding"""
        config = LoggingConfig(
            service_name="bind-test-service",
            file_enabled=True,
            file_path=self.log_file
        )
        
        logger = WMLLogger.get_logger(config)
        
        # Test context updates
        logger.update_context(request_id="new-req-789")
        logger.bind(operation="new_operation", step="1")
        logger.info("Updated context message")
        
        # Verify updated context in log
        with open(self.log_file, 'r') as f:
            log_content = f.read()
            assert "new-req-789" in log_content
            assert "new_operation" in log_content
            assert "step" in log_content
    
    def test_logger_singleton_behavior(self):
        """Test singleton pattern per service name"""
        config = LoggingConfig(service_name="singleton-test")
        
        logger1 = WMLLogger.get_logger(config)
        logger2 = WMLLogger.get_logger(config)
        
        # Should be the same instance
        assert logger1 is logger2
        
        # Different service names should create different instances
        config2 = LoggingConfig(service_name="different-service")
        logger3 = WMLLogger.get_logger(config2)
        assert logger1 is not logger3


class TestWebSocketBroadcasting:
    """Test WebSocket broadcasting functionality"""
    
    @pytest.mark.asyncio
    async def test_websocket_broadcaster_setup(self):
        """Test WebSocket broadcaster initialization"""
        broadcaster = WebSocketBroadcaster(port=8765, path="/ws/logs", max_history=500)
        
        assert broadcaster.port == 8765
        assert broadcaster.path == "/ws/logs"
        assert broadcaster.max_history == 500
        assert broadcaster.connections == set()
    
    @pytest.mark.asyncio
    async def test_websocket_broadcasting_integration(self):
        """Test WebSocket broadcasting with WMLLogger"""
        # Mock WebSocket server to avoid actual network setup
        with patch('wmlog.mqtt.broadcaster.web.Application') as mock_app:
            mock_app.return_value = AsyncMock()
            
            config = LoggingConfig(
                service_name="websocket-test",
                websocket_enabled=True,
                websocket_port=8765
            )
            
            logger = WMLLogger.get_logger(config)
            
            # Test that broadcaster is initialized
            assert logger.websocket_broadcaster is not None
            assert logger.websocket_broadcaster.port == 8765
            
            # Test logging with broadcast
            logger.info("Broadcast test message", broadcast_data="test_value")
            
            # Verify broadcast was attempted (mock should be called)
            mock_serve.assert_called_once()


class TestMQTTBroadcasting:
    """Test MQTT broadcasting functionality"""
    
    def test_mqtt_broadcaster_setup(self):
        """Test MQTT broadcaster initialization"""
        broadcaster = MQTTBroadcaster(
            broker_host="localhost",
            broker_port=1883,
            topic_prefix="test/logs"
        )
        
        assert broadcaster.broker_host == "localhost"
        assert broadcaster.broker_port == 1883
        assert broadcaster.topic_prefix == "test/logs"
    
    @pytest.mark.asyncio
    async def test_mqtt_broadcasting_integration(self):
        """Test MQTT broadcasting with WMLLogger"""
        # Mock MQTT client to avoid actual broker connection
        with patch('wmlog.mqtt.broadcaster.mqtt.Client') as mock_client:
            mock_client_instance = Mock()
            mock_client.return_value = mock_client_instance
            
            config = LoggingConfig(
                service_name="mqtt-test",
                mqtt_enabled=True,
                mqtt_broker_host="localhost",
                mqtt_broker_port=1883,
                mqtt_topic_prefix="test/logs"
            )
            
            logger = WMLLogger.get_logger(config)
            
            # Test that broadcaster is initialized
            assert logger.mqtt_broadcaster is not None
            
            # Test logging with MQTT broadcast
            logger.info("MQTT test message", mqtt_data="test_value")
            
            # Verify MQTT client was created
            mock_client.assert_called_once()


class TestCLIInterface:
    """Test WML CLI interface"""
    
    def setup_method(self):
        """Setup CLI test environment"""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
        self.test_config = os.path.join(self.temp_dir, "test_config.yaml")
        
        # Create test configuration file
        config_content = """
service_name: cli-test-service
log_level: INFO
console_enabled: true
file_enabled: true
file_path: cli_test.log
        """
        with open(self.test_config, 'w') as f:
            f.write(config_content)
    
    def teardown_method(self):
        """Cleanup CLI test environment"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_cli_version_command(self):
        """Test CLI version command"""
        result = self.runner.invoke(cli, ['version'])
        assert result.exit_code == 0
        assert "WML (Websocket MQTT Logging)" in result.output
    
    def test_cli_init_command(self):
        """Test CLI service initialization"""
        config_path = os.path.join(self.temp_dir, "new_config.yaml")
        result = self.runner.invoke(cli, [
            'init', 
            '--service-name', 'new-service',
            '--config', config_path
        ])
        
        assert result.exit_code == 0
        assert os.path.exists(config_path)
        
        # Verify configuration content
        with open(config_path, 'r') as f:
            config_content = f.read()
            assert "new-service" in config_content
    
    def test_cli_log_command(self):
        """Test CLI logging command"""
        result = self.runner.invoke(cli, [
            'log',
            '--config', self.test_config,
            '--level', 'info',
            '--message', 'CLI test message'
        ])
        
        assert result.exit_code == 0
        
        # Verify log file was created
        log_file = os.path.join(os.path.dirname(self.test_config), "cli_test.log")
        assert os.path.exists(log_file)
        
        with open(log_file, 'r') as f:
            log_content = f.read()
            assert "CLI test message" in log_content
    
    def test_cli_monitor_command(self):
        """Test CLI log monitoring command"""
        # Create a log file with some content
        log_file = os.path.join(self.temp_dir, "monitor_test.log")
        with open(log_file, 'w') as f:
            f.write('{"timestamp": "2024-01-01T12:00:00", "level": "info", "message": "Test log entry"}\n')
        
        result = self.runner.invoke(cli, [
            'monitor',
            '--file', log_file,
            '--lines', '1'
        ])
        
        assert result.exit_code == 0
        assert "Test log entry" in result.output


class TestIntegrationPatterns:
    """Test integration patterns with other ecosystem packages"""
    
    def setup_method(self):
        """Setup integration test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.temp_dir, "integration.log")
    
    def teardown_method(self):
        """Cleanup integration test environment"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_proserve_integration_pattern(self):
        """Test integration pattern with ProServe services"""
        # Simulate ProServe service integration
        service_context = LogContext(
            service_name="proserve-test-service",
            version="1.0.0",
            environment="development",
            custom_fields={
                "service_type": "proserve",
                "manifest_file": "test-manifest.yaml",
                "endpoint": "/api/test"
            }
        )
        
        config = LoggingConfig(
            service_name="proserve-test-service",
            file_enabled=True,
            file_path=self.log_file
        )
        
        logger = WMLLogger.get_logger(config, context=service_context)
        
        # Log service lifecycle events
        logger.info("ProServe service starting", manifest="test-manifest.yaml")
        logger.info("Endpoint registered", endpoint="/api/test", method="GET")
        logger.info("Request processed", endpoint="/api/test", status_code=200, response_time=0.05)
        
        # Verify ProServe-specific context in logs
        with open(self.log_file, 'r') as f:
            log_content = f.read()
            assert "proserve" in log_content
            assert "test-manifest.yaml" in log_content
            assert "/api/test" in log_content
            assert "status_code" in log_content
    
    def test_servos_integration_pattern(self):
        """Test integration pattern with Servos isolation"""
        # Simulate Servos isolation integration
        servos_context = LogContext(
            service_name="servos-test-service",
            custom_fields={
                "isolation_mode": "docker",
                "platform": "rp2040",
                "script_path": "/handlers/gpio_test.py"
            }
        )
        
        config = LoggingConfig(
            service_name="servos-test-service",
            file_enabled=True,
            file_path=self.log_file
        )
        
        logger = WMLLogger.get_logger(config, context=servos_context)
        
        # Log isolation events
        logger.info("Isolation manager initialized", mode="docker", platform="rp2040")
        logger.info("Script execution started", script="/handlers/gpio_test.py")
        logger.info("Script execution completed", execution_time=2.5, result="success")
        
        # Verify Servos-specific context in logs
        with open(self.log_file, 'r') as f:
            log_content = f.read()
            assert "isolation_mode" in log_content
            assert "docker" in log_content
            assert "rp2040" in log_content
            assert "gpio_test.py" in log_content
    
    def test_edpmt_integration_pattern(self):
        """Test integration pattern with EDPMT hardware operations"""
        # Simulate EDPMT hardware integration
        edpmt_context = LogContext(
            service_name="edpmt-test-service",
            custom_fields={
                "hardware_type": "gpio",
                "device_id": "rpi-gpio-18",
                "operation": "pin_read"
            }
        )
        
        config = LoggingConfig(
            service_name="edpmt-test-service",
            file_enabled=True,
            file_path=self.log_file,
            websocket_enabled=False,  # Disable for testing
            mqtt_enabled=False
        )
        
        logger = WMLLogger.get_logger(config, context=edpmt_context)
        
        # Log hardware operations
        logger.info("Hardware operation started", device="rpi-gpio-18", operation="pin_read")
        logger.info("GPIO pin read", pin=18, value=1, voltage=3.3)
        logger.info("Hardware operation completed", duration=0.001, result="success")
        
        # Verify EDPMT-specific context in logs
        with open(self.log_file, 'r') as f:
            log_content = f.read()
            assert "hardware_type" in log_content
            assert "gpio" in log_content
            assert "rpi-gpio-18" in log_content
            assert "pin_read" in log_content


class TestPerformanceAndReliability:
    """Test performance characteristics and reliability"""
    
    def setup_method(self):
        """Setup performance test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.temp_dir, "performance.log")
    
    def teardown_method(self):
        """Cleanup performance test environment"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_high_volume_logging_performance(self):
        """Test logging performance under high volume"""
        config = LoggingConfig(
            service_name="performance-test",
            file_enabled=True,
            file_path=self.log_file,
            console_enabled=False  # Disable console for performance
        )
        
        logger = WMLLogger.get_logger(config)
        
        # Log 1000 messages and measure time
        start_time = time.time()
        
        for i in range(1000):
            logger.info(f"Performance test message {i}", 
                       iteration=i, 
                       batch="high_volume_test",
                       data={"key": f"value_{i}"})
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Performance assertion (should complete in reasonable time)
        assert duration < 5.0, f"High volume logging took {duration:.2f}s, expected < 5.0s"
        
        # Verify all messages were logged
        with open(self.log_file, 'r') as f:
            log_lines = f.readlines()
            assert len(log_lines) >= 1000
    
    def test_concurrent_logging_thread_safety(self):
        """Test thread safety with concurrent logging"""
        config = LoggingConfig(
            service_name="concurrent-test",
            file_enabled=True,
            file_path=self.log_file
        )
        
        logger = WMLLogger.get_logger(config)
        
        def log_worker(worker_id, num_messages):
            """Worker function for concurrent logging"""
            for i in range(num_messages):
                logger.info(f"Worker {worker_id} message {i}", 
                           worker_id=worker_id, 
                           message_id=i)
        
        # Create multiple threads
        threads = []
        num_workers = 5
        messages_per_worker = 100
        
        for worker_id in range(num_workers):
            thread = threading.Thread(
                target=log_worker, 
                args=(worker_id, messages_per_worker)
            )
            threads.append(thread)
        
        # Start all threads
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        duration = time.time() - start_time
        
        # Verify all messages were logged
        with open(self.log_file, 'r') as f:
            log_lines = f.readlines()
            expected_messages = num_workers * messages_per_worker
            assert len(log_lines) >= expected_messages
        
        # Performance check
        assert duration < 10.0, f"Concurrent logging took {duration:.2f}s"
    
    def test_error_handling_and_graceful_degradation(self):
        """Test error handling and graceful degradation"""
        # Test with invalid file path
        config = LoggingConfig(
            service_name="error-test",
            file_enabled=True,
            file_path="/invalid/path/test.log",  # Invalid path
            console_enabled=True  # Should still work
        )
        
        # Logger should handle file error gracefully
        logger = WMLLogger.get_logger(config)
        
        # Should not raise exception despite invalid file path
        logger.info("Error handling test message")
        logger.error("Test error message")
        
        # Logger should still be functional for other operations
        assert logger is not None
        assert logger.service_name == "error-test"


class TestConfigurationOptions:
    """Test various configuration options and edge cases"""
    
    def setup_method(self):
        """Setup configuration test environment"""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Cleanup configuration test environment"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_minimal_configuration(self):
        """Test minimal configuration requirements"""
        config = LoggingConfig(service_name="minimal-test")
        logger = WMLLogger.get_logger(config)
        
        # Should work with minimal config
        logger.info("Minimal config test")
        assert logger.config.service_name == "minimal-test"
    
    def test_comprehensive_configuration(self):
        """Test comprehensive configuration with all options"""
        log_file = os.path.join(self.temp_dir, "comprehensive.log")
        
        config = LoggingConfig(
            service_name="comprehensive-test",
            log_level="DEBUG",
            environment="test",
            version="2.0.0",
            console_enabled=True,
            file_enabled=True,
            file_path=log_file,
            websocket_enabled=False,  # Disabled for testing
            mqtt_enabled=False        # Disabled for testing
        )
        
        context = LogContext(
            service_name="comprehensive-test",
            version="2.0.0",
            environment="test",
            custom_fields={"module": "test_config"}
        )
        
        logger = WMLLogger.get_logger(config, context=context)
        logger.info("Comprehensive configuration test")
        
        # Verify all configuration is applied
        assert os.path.exists(log_file)
        with open(log_file, 'r') as f:
            log_content = f.read()
            assert "comprehensive-test" in log_content
            assert "test_config" in log_content


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
