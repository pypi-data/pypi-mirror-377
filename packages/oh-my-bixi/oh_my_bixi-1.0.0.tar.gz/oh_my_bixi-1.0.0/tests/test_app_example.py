import sys
import unittest
from typing import Any, Dict, Optional, Callable, Union, Iterable, Mapping
import typer

from bixi import AppMixin
from bixi.cli import run_partial_typer


class HelloApp(AppMixin):
    def __init__(self):
        super().__init__(is_init_logging=True)

    def echo(self, string: str, *, n_times: int = 1) -> str:
        # normalized to a single space after the colon
        return f"Echo: {string * n_times}"

    def assign(self, **kwargs: Any) -> Dict[str, Any]:
        for k, v in kwargs.items():
            setattr(self, k, v)

    def get_val(self, key: str) -> Any:
        return getattr(self, key, None)

    def exec(self, command: str):
        return self.run_exec(command)

    @property
    def entries(self) -> Dict[str, Callable]:
        return {
            "echo":      self.echo,
            "print_val": self.get_val,
            "exec":      self.exec
        }


class TestHelloApp(unittest.TestCase):
    def test_echo_method(self):
        app = HelloApp()
        self.assertEqual(app.echo("abc", n_times=2), "Echo: abcabc")
        self.assertEqual(app.echo("x", n_times=1), "Echo: x")

    def test_assign_and_get_value(self):
        app = HelloApp()
        app.assign(tmp_text="this is a stored text", tmp_number=2)
        self.assertEqual(app.get_val("tmp_text"), "this is a stored text")
        self.assertEqual(app.get_val("tmp_number"), 2)


class TestCLI(unittest.TestCase):
    def setUp(self):
        self._cache_argv = sys.argv.copy()

    def tearDown(self):
        sys.argv = self._cache_argv

    def test_cli_help(self):
        app = HelloApp()
        sys.argv = [sys.argv[0]] + ["--help"]
        with self.assertRaises(SystemExit):
            run_partial_typer(app.entries)

    def test_cli_command(self):
        app = HelloApp()
        sys.argv = [sys.argv[0]] + ["echo", "hello", "--n-times", "3"]
        output_string = run_partial_typer(app.entries)
        self.assertEqual(output_string, "Echo: hellohellohello")

    def test_cli_run_exec(self):
        app = HelloApp()
        sys.argv = [sys.argv[0]] + ["exec", "assign(tmp_text='this is a stored text', tmp_number=2); assign(result=get_val('tmp_text') + '; ' + str(get_val('tmp_number'))); "]
        run_partial_typer(app.entries)
        self.assertEqual(app.result, "this is a stored text; 2")
