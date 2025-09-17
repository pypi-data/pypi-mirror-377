"""Pyne tests for behavior of __file__"""

from pathlib import Path

from pynetest.expectations import expect
from pynetest.pyne_test_collector import it, describe
from pynetest.pyne_tester import pyne
from pynetest.test_doubles.stub import spy_on
from tests.test_helpers.some_class import SomeClass


@pyne
def file_tests():
    @describe("#__file__")
    def _():
        @it("has a value")
        def _(self):
            expected = Path.cwd() / "tests/pynetests/file_test.py"
            expect(Path.cwd() / __file__).to_be(expected)
