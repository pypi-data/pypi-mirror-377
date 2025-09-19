import argparse
import os
import sys
from typing import Dict, List, Optional

import pytest

from cheap_settings import CheapSettings


class TestCommandLineBasics:
    """Test basic command line functionality"""

    def test_simple_command_line_override(self):
        """Test that command line arguments override defaults"""

        class MySettings(CheapSettings):
            host: str = "localhost"
            port: int = 8080
            debug: bool = False

        # Simulate command line args
        MySettings.set_config_from_command_line(
            args=["--host", "example.com", "--port", "3000", "--debug"]
        )

        assert MySettings.host == "example.com"
        assert MySettings.port == 3000
        assert MySettings.debug is True

    def test_command_line_overrides_env_vars(self, monkeypatch):
        """Test that command line arguments override environment variables"""

        class MySettings(CheapSettings):
            host: str = "localhost"
            port: int = 8080

        # Set environment variables
        monkeypatch.setenv("HOST", "env.example.com")
        monkeypatch.setenv("PORT", "9090")

        # Command line should override
        MySettings.set_config_from_command_line(
            args=["--host", "cli.example.com", "--port", "3000"]
        )

        assert MySettings.host == "cli.example.com"
        assert MySettings.port == 3000

    def test_partial_command_line_override(self, monkeypatch):
        """Test that only specified command line args override, others use env/defaults"""

        class MySettings(CheapSettings):
            host: str = "localhost"
            port: int = 8080
            debug: bool = False

        # Set environment variable for port
        monkeypatch.setenv("PORT", "9090")

        # Only override host via command line
        MySettings.set_config_from_command_line(args=["--host", "example.com"])

        assert MySettings.host == "example.com"  # From CLI
        assert MySettings.port == 9090  # From env
        assert MySettings.debug is False  # From default

    def test_no_command_line_args(self, monkeypatch):
        """Test behavior when no command line args are provided"""

        class MySettings(CheapSettings):
            host: str = "localhost"
            port: int = 8080

        monkeypatch.setenv("HOST", "env.example.com")

        # No args provided
        MySettings.set_config_from_command_line(args=[])

        # Should still use env vars and defaults
        assert MySettings.host == "env.example.com"
        assert MySettings.port == 8080


class TestCommandLineTypes:
    """Test different type conversions for command line arguments"""

    def test_boolean_flag_true(self):
        """Test boolean flags that default to False"""

        class MySettings(CheapSettings):
            debug: bool = False
            verbose: bool = False

        MySettings.set_config_from_command_line(args=["--debug", "--verbose"])

        assert MySettings.debug is True
        assert MySettings.verbose is True

    def test_boolean_flag_false(self):
        """Test boolean flags that default to True"""

        class MySettings(CheapSettings):
            production: bool = True
            secure: bool = True

        MySettings.set_config_from_command_line(args=["--no-production", "--no-secure"])

        assert MySettings.production is False
        assert MySettings.secure is False

    def test_boolean_with_value_true(self):
        """Test boolean with explicit 'true' value"""

        class MySettings(CheapSettings):
            debug: Optional[bool] = None

        MySettings.set_config_from_command_line(args=["--debug", "true"])
        assert MySettings.debug is True

    def test_boolean_with_value_false(self):
        """Test boolean with explicit 'false' value"""

        class MySettings(CheapSettings):
            debug: Optional[bool] = None

        MySettings.set_config_from_command_line(args=["--debug", "false"])
        assert MySettings.debug is False

    def test_boolean_with_value_1(self):
        """Test boolean with explicit '1' value"""

        class MySettings(CheapSettings):
            debug: Optional[bool] = None

        MySettings.set_config_from_command_line(args=["--debug", "1"])
        assert MySettings.debug is True

    def test_boolean_with_value_yes(self):
        """Test boolean with explicit 'yes' value"""

        class MySettings(CheapSettings):
            debug: Optional[bool] = None

        MySettings.set_config_from_command_line(args=["--debug", "yes"])
        assert MySettings.debug is True

    def test_integer_conversion(self):
        """Test integer type conversion from command line"""

        class MySettings(CheapSettings):
            port: int = 8080
            timeout: int = 30

        MySettings.set_config_from_command_line(
            args=["--port", "3000", "--timeout", "60"]
        )

        assert MySettings.port == 3000
        assert MySettings.timeout == 60
        assert isinstance(MySettings.port, int)
        assert isinstance(MySettings.timeout, int)

    def test_float_conversion(self):
        """Test float type conversion from command line"""

        class MySettings(CheapSettings):
            rate: float = 1.0
            threshold: float = 0.5

        MySettings.set_config_from_command_line(
            args=["--rate", "2.5", "--threshold", "0.75"]
        )

        assert MySettings.rate == 2.5
        assert MySettings.threshold == 0.75
        assert isinstance(MySettings.rate, float)
        assert isinstance(MySettings.threshold, float)

    def test_string_values(self):
        """Test string values from command line"""

        class MySettings(CheapSettings):
            host: str = "localhost"
            api_key: str = ""

        MySettings.set_config_from_command_line(
            args=["--host", "example.com", "--api-key", "secret123"]
        )

        assert MySettings.host == "example.com"
        assert MySettings.api_key == "secret123"

    def test_optional_types(self):
        """Test Optional type handling from command line"""

        class MySettings(CheapSettings):
            timeout: Optional[int] = None
            api_key: Optional[str] = None

        # Set values
        MySettings.set_config_from_command_line(
            args=["--timeout", "30", "--api-key", "secret"]
        )

        assert MySettings.timeout == 30
        assert MySettings.api_key == "secret"

    def test_list_and_dict_are_skipped(self):
        """Test that list and dict types are skipped in command line parsing"""

        class MySettings(CheapSettings):
            host: str = "localhost"
            servers: list = []
            config: dict = {}

        # Parser shouldn't have --servers or --config options
        result = MySettings.set_config_from_command_line(args=["--host", "example.com"])

        assert MySettings.host == "example.com"
        # These should still have default values
        assert MySettings.servers == []
        assert MySettings.config == {}


class TestCommandLineNaming:
    """Test command line argument naming conventions"""

    def test_underscore_to_dash_conversion(self):
        """Test that underscores in attribute names become dashes in CLI args"""

        class MySettings(CheapSettings):
            api_key: str = ""
            max_connections: int = 10
            enable_cache: bool = False

        MySettings.set_config_from_command_line(
            args=["--api-key", "secret", "--max-connections", "20", "--enable-cache"]
        )

        assert MySettings.api_key == "secret"
        assert MySettings.max_connections == 20
        assert MySettings.enable_cache is True

    def test_mixed_case_names(self):
        """Test that mixed case names are lowercased in CLI"""

        class MySettings(CheapSettings):
            apiKey: str = ""
            maxConnections: int = 10

        # CLI args should be lowercased
        MySettings.set_config_from_command_line(
            args=["--apikey", "secret", "--maxconnections", "20"]
        )

        assert MySettings.apiKey == "secret"
        assert MySettings.maxConnections == 20


class TestCustomParser:
    """Test using custom ArgumentParser"""

    def test_custom_parser_with_existing_args(self):
        """Test providing a parser with pre-existing arguments"""

        class MySettings(CheapSettings):
            host: str = "localhost"
            port: int = 8080

        # Create parser with custom argument
        parser = argparse.ArgumentParser(description="My App")
        parser.add_argument("--version", action="store_true", help="Show version")

        # Pass custom parser
        result = MySettings.set_config_from_command_line(
            arg_parser=parser, args=["--host", "example.com", "--version"]
        )

        assert MySettings.host == "example.com"
        assert MySettings.port == 8080
        assert result.version is True  # Custom arg

    def test_parser_conflict_handling(self):
        """Test that conflicting arguments are handled properly"""

        class MySettings(CheapSettings):
            help: str = "default"  # This might conflict with parser's --help

        # Should raise a ValueError with informative message
        with pytest.raises(ValueError, match="Cannot use 'help' as a setting name"):
            MySettings.set_config_from_command_line(args=["--help", "custom"])


class TestInheritance:
    """Test command line handling with inheritance"""

    def test_inherited_settings_command_line(self):
        """Test that inherited settings work with command line args"""

        class BaseSettings(CheapSettings):
            host: str = "localhost"
            port: int = 8080

        class AppSettings(BaseSettings):
            debug: bool = False

        AppSettings.set_config_from_command_line(
            args=["--host", "example.com", "--port", "3000", "--debug"]
        )

        assert AppSettings.host == "example.com"
        assert AppSettings.port == 3000
        assert AppSettings.debug is True

    def test_overridden_defaults_in_subclass(self):
        """Test command line with overridden defaults in subclass"""

        class BaseSettings(CheapSettings):
            port: int = 8080

        class TestSettings(BaseSettings):
            port: int = 9090  # Override default

        # Command line should still override
        TestSettings.set_config_from_command_line(args=["--port", "3000"])
        assert TestSettings.port == 3000


class TestErrorHandling:
    """Test error handling in command line parsing"""

    def test_invalid_integer_value(self):
        """Test that invalid integer values raise appropriate errors"""

        class MySettings(CheapSettings):
            port: int = 8080

        with pytest.raises(SystemExit):  # argparse exits on error
            MySettings.set_config_from_command_line(args=["--port", "not-a-number"])

    def test_invalid_float_value(self):
        """Test that invalid float values raise appropriate errors"""

        class MySettings(CheapSettings):
            rate: float = 1.0

        with pytest.raises(SystemExit):  # argparse exits on error
            MySettings.set_config_from_command_line(args=["--rate", "not-a-float"])

    def test_invalid_boolean_value(self):
        """Test that invalid boolean values raise appropriate errors"""

        class MySettings(CheapSettings):
            debug: Optional[bool] = None

        # argparse exits with status 2 on parse errors
        with pytest.raises(SystemExit) as exc_info:
            MySettings.set_config_from_command_line(args=["--debug", "maybe"])
        assert exc_info.value.code == 2

    def test_missing_config_instance(self):
        """Test error when config instance is not set"""

        # Create a class that somehow has no config instance
        class BrokenSettings(CheapSettings):
            pass

        # Manually break it
        delattr(BrokenSettings, "__config_instance")

        with pytest.raises(AttributeError, match="Config instance has not been set"):
            BrokenSettings.set_config_from_command_line()


class TestReturnValue:
    """Test the return value of set_config_from_command_line"""

    def test_returns_namespace(self):
        """Test that the method returns an argparse.Namespace"""

        class MySettings(CheapSettings):
            host: str = "localhost"
            port: int = 8080

        result = MySettings.set_config_from_command_line(args=["--host", "example.com"])

        assert isinstance(result, argparse.Namespace)
        assert result.host == "example.com"
        assert result.port == 8080

    def test_namespace_includes_all_values(self):
        """Test that returned namespace includes all settings"""

        class MySettings(CheapSettings):
            host: str = "localhost"
            port: int = 8080
            debug: bool = False

        result = MySettings.set_config_from_command_line(args=["--debug"])

        assert hasattr(result, "host")
        assert hasattr(result, "port")
        assert hasattr(result, "debug")
        assert result.host == "localhost"
        assert result.port == 8080
        assert result.debug is True


class TestIntegration:
    """Integration tests for command line with other features"""

    def test_command_line_with_env_vars_and_defaults(self, monkeypatch):
        """Test full priority chain: CLI > env > defaults"""

        class MySettings(CheapSettings):
            host: str = "localhost"
            port: int = 8080
            debug: bool = False
            timeout: int = 30

        # Set some env vars
        monkeypatch.setenv("PORT", "9090")
        monkeypatch.setenv("DEBUG", "true")
        monkeypatch.setenv("TIMEOUT", "60")

        # Override some with CLI
        MySettings.set_config_from_command_line(
            args=["--host", "cli.example.com", "--port", "3000"]
        )

        assert MySettings.host == "cli.example.com"  # CLI (overrides default)
        assert MySettings.port == 3000  # CLI (overrides env)
        assert MySettings.debug is True  # Env (no CLI)
        assert MySettings.timeout == 60  # Env (no CLI)

    def test_multiple_calls_to_set_config(self):
        """Test that multiple calls to set_config_from_command_line work correctly"""

        class MySettings(CheapSettings):
            host: str = "localhost"
            port: int = 8080

        # First call
        MySettings.set_config_from_command_line(args=["--host", "first.com"])
        assert MySettings.host == "first.com"
        assert MySettings.port == 8080

        # Second call with different args
        MySettings.set_config_from_command_line(
            args=["--host", "second.com", "--port", "3000"]
        )
        assert MySettings.host == "second.com"
        assert MySettings.port == 3000

    def test_readme_example_with_cli(self):
        """Test the README example with command line args"""

        class TestSettings(CheapSettings):
            host: str = "localhost"
            port: int = 8080
            debug: bool = False

        # Simulate running: python myapp.py --host example.com --port 3000 --debug
        TestSettings.set_config_from_command_line(
            args=["--host", "example.com", "--port", "3000", "--debug"]
        )

        assert TestSettings.host == "example.com"
        assert TestSettings.port == 3000
        assert TestSettings.debug is True


class TestUnhandledTypes:
    """Test behavior with types not yet supported by command line"""

    def test_settings_without_type_annotations(self):
        """Test settings without type annotations"""

        class MySettings(CheapSettings):
            # No type annotation, should infer from default
            host = "localhost"
            port = 8080

        MySettings.set_config_from_command_line(
            args=["--host", "example.com", "--port", "3000"]
        )

        assert MySettings.host == "example.com"
        assert MySettings.port == 3000

    def test_settings_without_initializers(self):
        """Test settings with only type annotations"""

        class MySettings(CheapSettings):
            api_key: str
            timeout: int

        # Should use the type annotation
        MySettings.set_config_from_command_line(
            args=["--api-key", "secret", "--timeout", "30"]
        )

        assert MySettings.api_key == "secret"
        assert MySettings.timeout == 30


class TestCommandLineArgumentParsing:
    """Test argument parsing logic"""

    def test_partial_argument_name_matching(self):
        """Test that arguments are not matched by partial names"""

        class MySettings(CheapSettings):
            port: int = 1234
            port_number: int = 5678

        MySettings.set_config_from_command_line(args=["--port-number", "8765"])

        assert MySettings.port_number == 8765
        assert MySettings.port == 1234
