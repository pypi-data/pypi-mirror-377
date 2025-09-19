import json
import os
from typing import Dict, List, Optional, Union

import pytest

from cheap_settings import CheapSettings


class TestBasicFunctionality:
    """Test basic CheapSettings functionality"""

    def test_simple_class_attributes(self):
        """Test that class attributes work without environment variables"""

        class MySettings(CheapSettings):
            name: str = "default"
            count: int = 42
            rate: float = 3.14
            enabled: bool = True

        assert MySettings.name == "default"
        assert MySettings.count == 42
        assert MySettings.rate == 3.14
        assert MySettings.enabled is True

    def test_environment_override(self, monkeypatch):
        """Test that environment variables override class attributes"""

        class MySettings(CheapSettings):
            name: str = "default"
            count: int = 42

        monkeypatch.setenv("NAME", "from_env")
        monkeypatch.setenv("COUNT", "100")

        assert MySettings.name == "from_env"
        assert MySettings.count == 100
        assert isinstance(MySettings.count, int)

    def test_type_conversion_int(self, monkeypatch):
        """Test integer type conversion from environment"""

        class MySettings(CheapSettings):
            port: int = 8080

        monkeypatch.setenv("PORT", "3000")
        assert MySettings.port == 3000
        assert isinstance(MySettings.port, int)

    def test_type_conversion_float(self, monkeypatch):
        """Test float type conversion from environment"""

        class MySettings(CheapSettings):
            rate: float = 1.0

        monkeypatch.setenv("RATE", "2.5")
        assert MySettings.rate == 2.5
        assert isinstance(MySettings.rate, float)

    def test_type_conversion_bool_true(self, monkeypatch):
        """Test boolean type conversion for true values"""

        class MySettings(CheapSettings):
            debug: bool = False

        # Test various true values
        for value in ["true", "True", "TRUE"]:
            monkeypatch.setenv("DEBUG", value)
            assert MySettings.debug is True

    def test_type_conversion_bool_false(self, monkeypatch):
        """Test boolean type conversion for false values"""

        class MySettings(CheapSettings):
            debug: bool = True

        # Test various false values
        for value in ["false", "False", "FALSE"]:
            monkeypatch.setenv("DEBUG", value)
            assert MySettings.debug is False

    def test_type_conversion_bool_invalid(self, monkeypatch):
        """Test boolean type conversion with invalid values"""

        class MySettings(CheapSettings):
            debug: bool = True

        monkeypatch.setenv("DEBUG", "invalid")
        with pytest.raises(ValueError, match="invalid is not a valid boolean value"):
            _ = MySettings.debug

    def test_list_from_json(self, monkeypatch):
        """Test list parsing from JSON string"""

        class MySettings(CheapSettings):
            items: list = []

        test_list = ["a", "b", "c"]
        monkeypatch.setenv("ITEMS", json.dumps(test_list))
        assert MySettings.items == test_list
        assert isinstance(MySettings.items, list)

    def test_dict_from_json(self, monkeypatch):
        """Test dict parsing from JSON string"""

        class MySettings(CheapSettings):
            config: dict = {}

        test_dict = {"key": "value", "number": 42}
        monkeypatch.setenv("CONFIG", json.dumps(test_dict))
        assert MySettings.config == test_dict
        assert isinstance(MySettings.config, dict)

    def test_invalid_json(self, monkeypatch):
        """Test that invalid JSON raises a helpful ValueError"""

        class MySettings(CheapSettings):
            items: list = []

        monkeypatch.setenv("ITEMS", "not valid json")
        with pytest.raises(
            ValueError, match=r"Invalid JSON in environment variable ITEMS"
        ):
            _ = MySettings.items

    def test_wrong_json_type_list(self, monkeypatch):
        """Test that providing dict JSON for list type raises a helpful ValueError"""

        class MySettings(CheapSettings):
            items: list = []

        monkeypatch.setenv("ITEMS", json.dumps({"key": "value"}))
        with pytest.raises(
            ValueError,
            match=r"Invalid JSON type in environment variable ITEMS. Expected list, but got dict.",
        ):
            _ = MySettings.items

    def test_wrong_json_type_dict(self, monkeypatch):
        """Test that providing list JSON for dict type raises a helpful ValueError"""

        class MySettings(CheapSettings):
            config: dict = {}

        monkeypatch.setenv("CONFIG", json.dumps(["a", "b"]))
        with pytest.raises(
            ValueError,
            match=r"Invalid JSON type in environment variable CONFIG. Expected dict, but got list.",
        ):
            _ = MySettings.config

    def test_attribute_error(self):
        """Test that accessing undefined attributes raises AttributeError"""

        class MySettings(CheapSettings):
            name: str = "default"

        with pytest.raises(AttributeError):
            _ = MySettings.undefined_attribute

    def test_multiple_settings_classes(self, monkeypatch):
        """Test that multiple settings classes work independently"""

        class Settings1(CheapSettings):
            name: str = "default1"

        class Settings2(CheapSettings):
            name: str = "default2"

        monkeypatch.setenv("NAME", "from_env")

        assert Settings1.name == "from_env"
        assert Settings2.name == "from_env"

    def test_setattr(self):
        """Test that setting attributes works"""

        class MySettings(CheapSettings):
            name: str = "default"

        MySettings.name = "new_value"
        assert MySettings.name == "new_value"

        # Environment should still override
        os.environ["NAME"] = "from_env"
        assert MySettings.name == "from_env"
        os.environ.pop("NAME")

    def test_inheritance(self):
        """Test that inheritance works properly"""

        class BaseSettings(CheapSettings):
            base_value: str = "base"

        class DerivedSettings(BaseSettings):
            derived_value: str = "derived"

        assert DerivedSettings.base_value == "base"
        assert DerivedSettings.derived_value == "derived"

    def test_no_type_annotation(self):
        """Test behavior with attributes that have no type annotation"""

        class MySettings(CheapSettings):
            # This should work but won't have type conversion
            untyped_value = "hello"

        assert MySettings.untyped_value == "hello"

        # Without type annotation, environment variable is returned as string
        os.environ["UNTYPED_VALUE"] = "from_env"
        assert MySettings.untyped_value == "from_env"
        os.environ.pop("UNTYPED_VALUE")


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_empty_string_remains_string(self, monkeypatch):
        """Test that empty string environment variable is preserved"""

        class MySettings(CheapSettings):
            value: str = "default"

        monkeypatch.setenv("VALUE", "")
        assert MySettings.value == ""

    def test_numeric_string_remains_string(self, monkeypatch):
        """Test that numeric strings remain strings when type is str"""

        class MySettings(CheapSettings):
            value: str = "default"

        monkeypatch.setenv("VALUE", "123")
        assert MySettings.value == "123"
        assert isinstance(MySettings.value, str)

    def test_whitespace_handling(self, monkeypatch):
        """Test that whitespace in values is preserved"""

        class MySettings(CheapSettings):
            value: str = "default"

        monkeypatch.setenv("VALUE", "  spaces  ")
        assert MySettings.value == "  spaces  "

    def test_case_sensitive_attributes(self, monkeypatch):
        """Test that attribute names are case sensitive but env vars are not"""

        class MySettings(CheapSettings):
            myValue: str = "default"

        monkeypatch.setenv("MYVALUE", "from_env")
        assert MySettings.myValue == "from_env"

    def test_special_characters_in_json(self, monkeypatch):
        """Test JSON parsing with special characters"""

        class MySettings(CheapSettings):
            config: dict = {}

        test_dict = {"key": 'value with "quotes"', "unicode": "😀"}
        monkeypatch.setenv("CONFIG", json.dumps(test_dict))
        assert MySettings.config == test_dict


class TestIntegration:
    """Integration tests based on README examples"""

    def test_readme_example(self, monkeypatch):
        """Test the exact example from the README"""

        class MySettings(CheapSettings):
            port: int = 8080
            host: str = "localhost"
            debug: bool = False

        # Default values
        assert MySettings.port == 8080
        assert MySettings.host == "localhost"
        assert MySettings.debug is False

        # With environment variables
        monkeypatch.setenv("PORT", "3000")
        monkeypatch.setenv("HOST", "0.0.0.0")
        monkeypatch.setenv("DEBUG", "true")

        assert MySettings.port == 3000
        assert MySettings.host == "0.0.0.0"
        assert MySettings.debug is True

    def test_complex_types_example(self, monkeypatch):
        """Test complex types from README"""

        class MySettings(CheapSettings):
            allowed_hosts: list = ["localhost"]
            database_config: dict = {"host": "localhost", "port": 5432}

        # Test list override
        monkeypatch.setenv("ALLOWED_HOSTS", '["example.com", "api.example.com"]')
        assert MySettings.allowed_hosts == ["example.com", "api.example.com"]

        # Test dict override
        monkeypatch.setenv(
            "DATABASE_CONFIG", '{"host": "db.example.com", "port": 5433}'
        )
        assert MySettings.database_config == {"host": "db.example.com", "port": 5433}


class TestOptionalAndUnionTypes:
    """Test Optional and Union type handling"""

    def test_optional_int(self, monkeypatch):
        """Test Optional[int] type handling"""

        class MySettings(CheapSettings):
            timeout: Optional[int] = None

        # Default None value
        assert MySettings.timeout is None

        # Set to integer
        monkeypatch.setenv("TIMEOUT", "30")
        assert MySettings.timeout == 30

        # Set to "none" string
        monkeypatch.setenv("TIMEOUT", "none")
        assert MySettings.timeout is None

        # Case insensitive "none"
        monkeypatch.setenv("TIMEOUT", "NONE")
        assert MySettings.timeout is None

    def test_optional_string(self, monkeypatch):
        """Test Optional[str] type handling"""

        class MySettings(CheapSettings):
            api_key: Optional[str] = None

        # Default None value
        assert MySettings.api_key is None

        # Set to string
        monkeypatch.setenv("API_KEY", "secret123")
        assert MySettings.api_key == "secret123"

        # Set to "none" string should return None
        monkeypatch.setenv("API_KEY", "none")
        assert MySettings.api_key is None

    def test_optional_list(self, monkeypatch):
        """Test Optional[list] type handling"""

        class MySettings(CheapSettings):
            servers: Optional[list] = None

        # Default None value
        assert MySettings.servers is None

        # Set to list
        monkeypatch.setenv("SERVERS", '["server1", "server2"]')
        assert MySettings.servers == ["server1", "server2"]

        # Set to "none"
        monkeypatch.setenv("SERVERS", "none")
        assert MySettings.servers is None

    def test_union_types(self, monkeypatch):
        """Test Union type handling"""

        class MySettings(CheapSettings):
            port: Union[int, str] = 8080

        # Default int value
        assert MySettings.port == 8080

        # Set to int string
        monkeypatch.setenv("PORT", "3000")
        assert MySettings.port == 3000

        # Set to non-numeric string
        monkeypatch.setenv("PORT", "http")
        assert MySettings.port == "http"

    def test_python310_union_syntax(self, monkeypatch):
        """Test Python 3.10+ union syntax (int | None)"""

        class MySettings(CheapSettings):
            count: Optional[int] = None

        # Default None value
        assert MySettings.count is None

        # Set to int
        monkeypatch.setenv("COUNT", "42")
        assert MySettings.count == 42

        # Set to "none"
        monkeypatch.setenv("COUNT", "none")
        assert MySettings.count is None

    def test_generic_list_type(self, monkeypatch):
        """Test generic list types like List[str]"""

        class MySettings(CheapSettings):
            tags: List[str] = []

        # Set to list
        monkeypatch.setenv("TAGS", '["python", "config", "settings"]')
        assert MySettings.tags == ["python", "config", "settings"]

    def test_generic_dict_type(self, monkeypatch):
        """Test generic dict types like Dict[str, int]"""

        class MySettings(CheapSettings):
            limits: Dict[str, int] = {}

        # Set to dict
        monkeypatch.setenv("LIMITS", '{"max_users": 100, "max_requests": 1000}')
        assert MySettings.limits == {"max_users": 100, "max_requests": 1000}


class TestInheritanceAndMRO:
    """Test inheritance and Method Resolution Order (MRO)"""

    def test_simple_inheritance(self, monkeypatch):
        """Test simple inheritance of settings"""

        class BaseSettings(CheapSettings):
            host: str = "localhost"
            port: int = 8080

        class AppSettings(BaseSettings):
            debug: bool = False

        assert AppSettings.host == "localhost"
        assert AppSettings.port == 8080
        assert AppSettings.debug is False

        # Override from environment
        monkeypatch.setenv("HOST", "example.com")
        monkeypatch.setenv("PORT", "3000")
        monkeypatch.setenv("DEBUG", "true")

        assert AppSettings.host == "example.com"
        assert AppSettings.port == 3000
        assert AppSettings.debug is True

    def test_override_in_subclass(self, monkeypatch):
        """Test overriding default values in a subclass"""

        class BaseSettings(CheapSettings):
            host: str = "localhost"
            port: int = 8080

        class TestSettings(BaseSettings):
            port: int = 9090  # Override default port

        assert TestSettings.host == "localhost"
        assert TestSettings.port == 9090

        # Environment should still override everything
        monkeypatch.setenv("PORT", "3000")
        assert TestSettings.port == 3000

    def test_multi_level_inheritance(self, monkeypatch):
        """Test multiple levels of inheritance"""

        class RootSettings(CheapSettings):
            root_value: str = "root"

        class MidSettings(RootSettings):
            mid_value: str = "mid"

        class LeafSettings(MidSettings):
            leaf_value: str = "leaf"

        assert LeafSettings.root_value == "root"
        assert LeafSettings.mid_value == "mid"
        assert LeafSettings.leaf_value == "leaf"

        # Environment overrides
        monkeypatch.setenv("ROOT_VALUE", "env_root")
        monkeypatch.setenv("LEAF_VALUE", "env_leaf")

        assert LeafSettings.root_value == "env_root"
        assert LeafSettings.mid_value == "mid"
        assert LeafSettings.leaf_value == "env_leaf"

    def test_diamond_inheritance(self, monkeypatch):
        """Test diamond inheritance pattern"""

        class Base(CheapSettings):
            value: str = "base"

        class Left(Base):
            value: str = "left"

        class Right(Base):
            value: str = "right"

        class Bottom(Left, Right):
            pass

        # MRO: Bottom -> Left -> Right -> Base
        assert Bottom.value == "left"

        # Environment override
        monkeypatch.setenv("VALUE", "env")
        assert Bottom.value == "env"

    def test_annotations_inheritance(self, monkeypatch):
        """Test that type annotations are inherited correctly"""

        class BaseSettings(CheapSettings):
            port: int = 8080

        class AppSettings(BaseSettings):
            # No annotation here, should be inherited from BaseSettings
            port = 9090

        monkeypatch.setenv("PORT", "3000")
        assert AppSettings.port == 3000
        assert isinstance(AppSettings.port, int)


class TestMethodsAndProperties:
    """Test that methods and properties on settings classes are preserved."""

    def test_methods_and_properties_are_preserved(self, monkeypatch):
        """Test that methods and properties are not treated as settings."""

        class MySettings(CheapSettings):
            host: str = "localhost"
            port: int = 8080

            @property
            def url(self):
                """A property that would work on an instance."""
                return f"http://{self.host}:{self.port}"

            @staticmethod
            def get_protocol() -> str:
                return "http"

            @classmethod
            def get_host_and_port(cls) -> str:
                return f"{cls.host}:{cls.port}"

        # Test that settings still work
        assert MySettings.host == "localhost"
        assert MySettings.port == 8080

        # Test that methods are preserved and callable
        assert MySettings.get_protocol() == "http"
        assert MySettings.get_host_and_port() == "localhost:8080"

        # Test that the property object is preserved on the class
        assert isinstance(MySettings.url, property)
        assert isinstance(MySettings.__dict__["url"], property)

        # Test that environment overrides still work for settings
        monkeypatch.setenv("HOST", "example.com")
        monkeypatch.setenv("PORT", "3000")

        assert MySettings.host == "example.com"
        assert MySettings.port == 3000
        assert MySettings.get_host_and_port() == "example.com:3000"


class TestDir:
    """Test __dir__ functionality."""

    def test_dir_includes_settings_and_methods(self):
        """Test that dir() on a settings class returns settings and methods."""

        class BaseSettings(CheapSettings):
            base_setting: str = "base"
            another_base_setting: int = 0

        class MySettings(BaseSettings):
            my_setting: int = 1
            another_base_setting: int = 1  # Override

            @classmethod
            def my_method(cls):
                pass

        directory = dir(MySettings)

        # Check for settings from current class and parent class
        assert "my_setting" in directory
        assert "base_setting" in directory
        assert "another_base_setting" in directory

        # Check for the method
        assert "my_method" in directory

        # Check for a standard dunder method
        assert "__repr__" in directory

        # Check that settings without initializers but with annotations are included
        class SettingsWithAnnotation(CheapSettings):
            no_initializer: str

        assert "no_initializer" in dir(SettingsWithAnnotation)
