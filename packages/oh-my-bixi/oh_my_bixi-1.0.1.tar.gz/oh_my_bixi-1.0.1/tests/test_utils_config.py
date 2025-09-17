import tempfile
import os
import unittest
import textwrap
from pathlib import Path
from dataclasses import dataclass
from omegaconf import OmegaConf, DictConfig
from unittest.mock import patch, MagicMock

from bixi.utils.config import (
    compose_from_source,
    _clear_hydra,
    _store_structured_node,
    _supports_version_base,
    _init_ctx,
)


class TestComposeFromSource(unittest.TestCase):
    """Test cases for the compose_from_source function."""

    def test_yaml_config_basic(self):
        """Test compose_from_source with YAML file path."""
        # Create a temporary YAML file
        yaml_content = textwrap.dedent(
            """
            trainer:
              max_epochs: 10
              learning_rate: 0.001
            model:
              hidden_size: 128
              dropout: 0.1
        """
        ).strip()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            yaml_path = f.name

        try:
            # Test basic YAML loading
            cfg = compose_from_source(yaml_path)
            self.assertIsInstance(cfg, DictConfig)
            self.assertEqual(cfg.trainer.max_epochs, 10)
            self.assertEqual(cfg.trainer.learning_rate, 0.001)
            self.assertEqual(cfg.model.hidden_size, 128)
            self.assertEqual(cfg.model.dropout, 0.1)
        finally:
            os.unlink(yaml_path)

    def test_yaml_config_with_overrides(self):
        """Test compose_from_source with YAML file and overrides."""
        # Create a temporary YAML file
        yaml_content = textwrap.dedent(
            """
            trainer:
              max_epochs: 10
              learning_rate: 0.001
            model:
              hidden_size: 128
              dropout: 0.1
        """
        ).strip()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            yaml_path = f.name

        try:
            # Test with overrides
            cfg = compose_from_source(yaml_path, overrides=["trainer.max_epochs=5"])
            self.assertIsInstance(cfg, DictConfig)
            self.assertEqual(cfg.trainer.max_epochs, 5)  # Overridden
            self.assertEqual(cfg.trainer.learning_rate, 0.001)  # Original
            self.assertEqual(cfg.model.hidden_size, 128)  # Original
        finally:
            os.unlink(yaml_path)

    def test_yaml_config_with_path_object(self):
        """Test compose_from_source with Path object."""
        # Create a temporary YAML file
        yaml_content = textwrap.dedent(
            """
            trainer:
              max_epochs: 10
        """
        ).strip()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            yaml_path = Path(f.name)

        try:
            cfg = compose_from_source(yaml_path)
            self.assertIsInstance(cfg, DictConfig)
            self.assertEqual(cfg.trainer.max_epochs, 10)
        finally:
            os.unlink(yaml_path)

    def test_dataclass_type_basic(self):
        """Test compose_from_source with dataclass type."""

        @dataclass
        class DataCfg:
            root: str  # required
            batch_size: int = 64
            learning_rate: float = 0.001

        cfg = compose_from_source(DataCfg, overrides=["root=/data"])
        self.assertIsInstance(cfg, DictConfig)
        self.assertEqual(cfg.root, "/data")
        self.assertEqual(cfg.batch_size, 64)
        self.assertEqual(cfg.learning_rate, 0.001)

    def test_dataclass_type_with_overrides(self):
        """Test compose_from_source with dataclass type and overrides."""

        @dataclass
        class DataCfg:
            root: str  # required
            batch_size: int = 64
            learning_rate: float = 0.001

        cfg = compose_from_source(DataCfg, overrides=["root=/data", "batch_size=32"])
        self.assertIsInstance(cfg, DictConfig)
        self.assertEqual(cfg.root, "/data")
        self.assertEqual(cfg.batch_size, 32)  # Overridden
        self.assertEqual(cfg.learning_rate, 0.001)

    def test_dataclass_instance_basic(self):
        """Test compose_from_source with dataclass instance."""

        @dataclass
        class ModelCfg:
            hidden: int = 256
            lr: float = 1e-3
            dropout: float = 0.1

        instance = ModelCfg(hidden=128)
        cfg = compose_from_source(instance)
        self.assertIsInstance(cfg, DictConfig)
        self.assertEqual(cfg.hidden, 128)
        self.assertEqual(cfg.lr, 1e-3)
        self.assertEqual(cfg.dropout, 0.1)

    def test_dataclass_instance_with_overrides(self):
        """Test compose_from_source with dataclass instance and overrides."""

        @dataclass
        class ModelCfg:
            hidden: int = 256
            lr: float = 1e-3
            dropout: float = 0.1

        instance = ModelCfg(hidden=128)
        cfg = compose_from_source(instance, overrides=["lr=0.0005"])
        self.assertIsInstance(cfg, DictConfig)
        self.assertEqual(cfg.hidden, 128)
        self.assertEqual(cfg.lr, 0.0005)  # Overridden
        self.assertEqual(cfg.dropout, 0.1)

    def test_dataclass_with_nested_structure(self):
        """Test compose_from_source with nested dataclass structure."""

        @dataclass
        class OptimizerCfg:
            name: str = "adam"
            lr: float = 0.001

        @dataclass
        class ModelCfg:
            hidden_size: int = 128
            optimizer: OptimizerCfg = OptimizerCfg()

        cfg = compose_from_source(ModelCfg)
        self.assertIsInstance(cfg, DictConfig)
        self.assertEqual(cfg.hidden_size, 128)
        self.assertEqual(cfg.optimizer.name, "adam")
        self.assertEqual(cfg.optimizer.lr, 0.001)

    def test_invalid_source_type(self):
        """Test compose_from_source with invalid source type."""
        # Test with non-dataclass string (should be treated as path, not dataclass)
        # This will fail with MissingConfigException, not TypeError
        from hydra.errors import MissingConfigException

        with self.assertRaises(MissingConfigException):
            compose_from_source("not_a_dataclass")

        # Test with non-dataclass types
        with self.assertRaises(TypeError) as context:
            compose_from_source(123)
        self.assertIn(
            "source must be a path, a dataclass type, or a dataclass instance",
            str(context.exception),
        )

        with self.assertRaises(TypeError) as context:
            compose_from_source([])
        self.assertIn(
            "source must be a path, a dataclass type, or a dataclass instance",
            str(context.exception),
        )

    def test_nonexistent_yaml_file(self):
        """Test compose_from_source with nonexistent YAML file."""
        from hydra.errors import MissingConfigException

        with self.assertRaises(MissingConfigException):
            compose_from_source("nonexistent.yaml")

    def test_empty_overrides(self):
        """Test compose_from_source with empty overrides."""

        @dataclass
        class TestCfg:
            value: int = 42

        cfg = compose_from_source(TestCfg, overrides=[])
        self.assertIsInstance(cfg, DictConfig)
        self.assertEqual(cfg.value, 42)

    def test_multiple_overrides(self):
        """Test compose_from_source with multiple overrides."""

        @dataclass
        class TestCfg:
            a: int = 1
            b: str = "default"
            c: float = 0.5

        cfg = compose_from_source(TestCfg, overrides=["a=10", "b=override", "c=0.8"])
        self.assertIsInstance(cfg, DictConfig)
        self.assertEqual(cfg.a, 10)
        self.assertEqual(cfg.b, "override")
        self.assertEqual(cfg.c, 0.8)

    def test_override_with_different_types(self):
        """Test overrides with different data types."""

        @dataclass
        class TestCfg:
            int_val: int = 1
            float_val: float = 1.0
            str_val: str = "test"
            bool_val: bool = True

        cfg = compose_from_source(
            TestCfg,
            overrides=[
                "int_val=42",
                "float_val=3.14",
                "str_val=hello",
                "bool_val=false",
            ],
        )
        self.assertIsInstance(cfg, DictConfig)
        self.assertEqual(cfg.int_val, 42)
        self.assertEqual(cfg.float_val, 3.14)
        self.assertEqual(cfg.str_val, "hello")
        self.assertFalse(cfg.bool_val)


class TestHelperFunctions(unittest.TestCase):
    """Test cases for helper functions."""

    def test_clear_hydra(self):
        """Test _clear_hydra function."""
        # This should not raise an exception
        _clear_hydra()

    @patch("bixi.utils.config.inspect.signature")
    def test_supports_version_base_true(self, mock_signature):
        """Test _supports_version_base when version_base is supported."""
        mock_params = MagicMock()
        mock_params.__contains__ = MagicMock(return_value=True)
        mock_signature.return_value.parameters = mock_params

        self.assertTrue(_supports_version_base())

    @patch("bixi.utils.config.inspect.signature")
    def test_supports_version_base_false(self, mock_signature):
        """Test _supports_version_base when version_base is not supported."""
        mock_params = MagicMock()
        mock_params.__contains__ = MagicMock(return_value=False)
        mock_signature.return_value.parameters = mock_params

        self.assertFalse(_supports_version_base())

    def test_store_structured_node_with_type(self):
        """Test _store_structured_node with dataclass type."""

        @dataclass
        class TestCfg:
            value: int = 42

        name = _store_structured_node(TestCfg)
        self.assertIsInstance(name, str)
        self.assertIn("TestCfg", name)
        self.assertGreater(len(name), len("TestCfg"))  # Should have unique suffix

    def test_store_structured_node_with_instance(self):
        """Test _store_structured_node with dataclass instance."""

        @dataclass
        class TestCfg:
            value: int = 42

        instance = TestCfg()
        name = _store_structured_node(instance)
        self.assertIsInstance(name, str)
        self.assertIn("TestCfg", name)
        self.assertGreater(len(name), len("TestCfg"))  # Should have unique suffix

    def test_store_structured_node_with_name_hint(self):
        """Test _store_structured_node with custom name hint."""

        @dataclass
        class TestCfg:
            value: int = 42

        name = _store_structured_node(TestCfg, name_hint="custom_name")
        self.assertIsInstance(name, str)
        self.assertIn("custom_name", name)
        self.assertGreater(len(name), len("custom_name"))  # Should have unique suffix

    @patch("bixi.utils.config._supports_version_base")
    @patch("bixi.utils.config.initialize")
    def test_init_ctx_with_version_base(self, mock_initialize, mock_supports):
        """Test _init_ctx when version_base is supported."""
        mock_supports.return_value = True
        mock_initialize.return_value.__enter__ = MagicMock()
        mock_initialize.return_value.__exit__ = MagicMock()

        with _init_ctx():
            pass

        mock_initialize.assert_called_once_with(version_base=None)

    @patch("bixi.utils.config._supports_version_base")
    @patch("bixi.utils.config.initialize")
    def test_init_ctx_without_version_base(self, mock_initialize, mock_supports):
        """Test _init_ctx when version_base is not supported."""
        mock_supports.return_value = False
        mock_initialize.return_value.__enter__ = MagicMock()
        mock_initialize.return_value.__exit__ = MagicMock()

        with _init_ctx():
            pass

        mock_initialize.assert_called_once_with()

    @patch("bixi.utils.config._supports_version_base")
    @patch("bixi.utils.config.initialize_config_dir")
    def test_init_ctx_with_config_dir(self, mock_initialize_config_dir, mock_supports):
        """Test _init_ctx with config_dir parameter."""
        mock_supports.return_value = True
        mock_initialize_config_dir.return_value.__enter__ = MagicMock()
        mock_initialize_config_dir.return_value.__exit__ = MagicMock()

        with _init_ctx(config_dir="/test/config"):
            pass

        mock_initialize_config_dir.assert_called_once_with(
            config_dir="/test/config", version_base=None
        )


class TestIntegration(unittest.TestCase):
    """Integration tests combining multiple features."""

    def test_yaml_with_complex_overrides(self):
        """Test YAML config with complex override scenarios."""
        # Create a temporary YAML file
        yaml_content = textwrap.dedent(
            """
            trainer:
              max_epochs: 10
              learning_rate: 0.001
              optimizer:
                name: adam
                weight_decay: 0.01
            model:
              hidden_size: 128
              dropout: 0.1
              layers: 3
        """
        ).strip()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            yaml_path = f.name

        try:
            # Test complex overrides
            cfg = compose_from_source(
                yaml_path,
                overrides=[
                    "trainer.max_epochs=5",
                    "trainer.optimizer.weight_decay=0.001",
                    "model.layers=5",
                ],
            )
            self.assertIsInstance(cfg, DictConfig)
            self.assertEqual(cfg.trainer.max_epochs, 5)
            self.assertEqual(cfg.trainer.learning_rate, 0.001)  # Unchanged
            self.assertEqual(cfg.trainer.optimizer.name, "adam")  # Unchanged
            self.assertEqual(cfg.trainer.optimizer.weight_decay, 0.001)  # Overridden
            self.assertEqual(cfg.model.hidden_size, 128)  # Unchanged
            self.assertEqual(cfg.model.dropout, 0.1)  # Unchanged
            self.assertEqual(cfg.model.layers, 5)  # Overridden
        finally:
            os.unlink(yaml_path)

    def test_dataclass_with_required_fields(self):
        """Test dataclass with required fields and overrides."""

        @dataclass
        class RequiredCfg:
            required_field: str  # No default value
            optional_field: int = 42

        cfg = compose_from_source(RequiredCfg, overrides=["required_field=test_value"])
        self.assertIsInstance(cfg, DictConfig)
        self.assertEqual(cfg.required_field, "test_value")
        self.assertEqual(cfg.optional_field, 42)

    def test_omega_conf_compatibility(self):
        """Test that returned config is compatible with OmegaConf."""

        @dataclass
        class TestCfg:
            value: int = 42
            nested: dict = None

            def __post_init__(self):
                if self.nested is None:
                    self.nested = {"key": "value"}

        # Create an instance to avoid the None default issue
        instance = TestCfg()
        cfg = compose_from_source(instance)

        # Test OmegaConf operations on our composed config
        yaml_str = OmegaConf.to_yaml(cfg)
        self.assertIn("value: 42", yaml_str)

        # Test OmegaConf access patterns on our composed config
        self.assertEqual(OmegaConf.select(cfg, "value"), 42)
        self.assertEqual(OmegaConf.select(cfg, "nested"), {"key": "value"})

        # Test direct access to nested values
        self.assertEqual(cfg.nested.key, "value")

        # Test that non-existent keys are properly handled
        self.assertNotIn("nonexistent", cfg)
