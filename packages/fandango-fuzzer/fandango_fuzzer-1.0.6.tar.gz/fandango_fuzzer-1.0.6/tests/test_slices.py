#!/usr/bin/env pytest

import re
import unittest

from fandango.constraints.expression import ExpressionConstraint
from fandango.language.grammar.grammar import Grammar
from fandango.language.search import ItemSearch, RuleSearch
from fandango.language.symbols import NonTerminal, Terminal
from fandango.language.tree import DerivationTree
from fandango.language.parse import parse
from .utils import RESOURCES_ROOT, run_command


class TestSlices(unittest.TestCase):
    TEST_DIR = RESOURCES_ROOT

    def test_startswith(self):
        command = [
            "fandango",
            "fuzz",
            "-f",
            str(self.TEST_DIR / "twodigits.fan"),
            "-n",
            "1",
            "-c",
            'str(<start>).startswith("6")',
            "--format=none",
            "--validate",
            "--random-seed",
            "426912",
            "--population-size",
            "10",
        ]
        out, err, code = run_command(command)
        self.assertEqual("", err)
        self.assertEqual("", out)
        self.assertEqual(0, code)

    def test_slice_0(self):
        command = [
            "fandango",
            "fuzz",
            "-f",
            str(self.TEST_DIR / "twodigits.fan"),
            "-n",
            "1",
            "-c",
            '<start>[0] == "6"',
            "--format=none",
            "--validate",
            "--random-seed",
            "426912",
            "--population-size",
            "10",
        ]
        out, err, code = run_command(command)
        self.assertEqual("", err)
        self.assertEqual("", out)
        self.assertEqual(0, code)

    def test_slice_0plus(self):
        command = [
            "fandango",
            "fuzz",
            "-f",
            str(self.TEST_DIR / "twodigits.fan"),
            "-n",
            "1",
            "-c",
            '<start>[0:][0] == "6"',
            "--format=none",
            "--validate",
            "--random-seed",
            "426912",
            "--population-size",
            "10",
        ]
        out, err, code = run_command(command)
        self.assertEqual("", err)
        self.assertEqual("", out)
        self.assertEqual(0, code)

    def test_slice_1plus(self):
        command = [
            "fandango",
            "fuzz",
            "-f",
            str(self.TEST_DIR / "twodigits.fan"),
            "-n",
            "1",
            "-c",
            '<start>[1:][0] == "6"',
            "--format=none",
            "--validate",
            "--random-seed",
            "426912",
            "--population-size",
            "10",
        ]
        out, err, code = run_command(command)
        self.assertEqual("", err)
        self.assertEqual("", out)
        self.assertEqual(0, code)

    def test_slice_str0plus1(self):
        command = [
            "fandango",
            "fuzz",
            "-f",
            str(self.TEST_DIR / "twodigits.fan"),
            "-n",
            "1",
            "-c",
            'str(<start>)[0:1] == "6"',
            "--format=none",
            "--validate",
            "--random-seed",
            "426912",
            "--population-size",
            "10",
        ]
        out, err, code = run_command(command)
        self.assertEqual("", err)
        self.assertEqual("", out)
        self.assertEqual(0, code)

    def test_slice_plus1(self):
        command = [
            "fandango",
            "fuzz",
            "-f",
            str(self.TEST_DIR / "twodigits.fan"),
            "-n",
            "1",
            "-c",
            '<start>[:1][0] == "6"',
            "--format=none",
            "--validate",
            "--random-seed",
            "426912",
            "--population-size",
            "10",
        ]
        out, err, code = run_command(command)
        self.assertEqual("", err)
        self.assertEqual("", out)
        self.assertEqual(0, code)

    def test_slice_plus(self):
        command = [
            "fandango",
            "fuzz",
            "-f",
            str(self.TEST_DIR / "twodigits.fan"),
            "-n",
            "1",
            "-c",
            '<start>[:][0] == "6"',
            "--format=none",
            "--validate",
            "--random-seed",
            "426912",
            "--population-size",
            "10",
        ]
        out, err, code = run_command(command)
        self.assertEqual("", err)
        self.assertEqual("", out)
        self.assertEqual(0, code)

    def test_slice_str0(self):
        command = [
            "fandango",
            "fuzz",
            "-f",
            str(self.TEST_DIR / "twodigits.fan"),
            "-n",
            "1",
            "-c",
            'str(<start>)[0] == "6"',
            "--format=none",
            "--validate",
            "--random-seed",
            "426912",
            "--population-size",
            "10",
        ]
        out, err, code = run_command(command)
        self.assertEqual("", err)
        self.assertEqual("", out)
        self.assertEqual(0, code)

    def test_slice_paren(self):
        command = [
            "fandango",
            "fuzz",
            "-f",
            str(self.TEST_DIR / "twodigits.fan"),
            "-n",
            "1",
            "-c",
            '(<start>)[0] == "6"',
            "--format=none",
            "--validate",
            "--random-seed",
            "426912",
            "--population-size",
            "10",
        ]
        out, err, code = run_command(command)
        self.assertEqual("", err)
        self.assertEqual("", out)
        self.assertEqual(0, code)


class TestExplicitSlices(unittest.TestCase):
    EXAMPLE = "\n".join(
        [
            "<start> ::= <a>",
            "<a> ::= <b> <c> <d>",
            '<b> ::= "a" | "b"',
            '<c> ::= "c"',
            '<d> ::= "d"',
            "",
            "where str(<a>[0]).endswith('b')",
        ]
    )

    VALID_EXAMPLE = DerivationTree(
        NonTerminal("<start>"),
        [
            DerivationTree(
                NonTerminal("<a>"),
                [
                    DerivationTree(
                        NonTerminal("<b>"),
                        [
                            DerivationTree(
                                Terminal("b"),
                            )
                        ],
                    ),
                    DerivationTree(
                        NonTerminal("<c>"),
                        [
                            DerivationTree(
                                Terminal("c"),
                            )
                        ],
                    ),
                    DerivationTree(
                        NonTerminal("<d>"),
                        [
                            DerivationTree(
                                NonTerminal("d"),
                            )
                        ],
                    ),
                ],
            )
        ],
    )

    INVALID_EXAMPLE = DerivationTree(
        NonTerminal("<start>"),
        [
            DerivationTree(
                NonTerminal("<a>"),
                [
                    DerivationTree(
                        NonTerminal("<b>"),
                        [
                            DerivationTree(
                                Terminal("a"),
                            )
                        ],
                    ),
                    DerivationTree(
                        NonTerminal("<c>"),
                        [
                            DerivationTree(
                                Terminal("c"),
                            )
                        ],
                    ),
                    DerivationTree(
                        NonTerminal("<d>"),
                        [
                            DerivationTree(
                                NonTerminal("d"),
                            )
                        ],
                    ),
                ],
            )
        ],
    )

    # Type annotations for instance attributes set in setUp
    GRAMMAR: Grammar
    CONSTRAINT: ExpressionConstraint

    @classmethod
    def setUpClass(cls):
        grammar, constraints = parse(cls.EXAMPLE, use_cache=False, use_stdlib=False)
        assert len(constraints) == 1
        assert isinstance(constraints[0], ExpressionConstraint)
        assert grammar is not None
        cls.GRAMMAR = grammar
        cls.CONSTRAINT = constraints[0]

    def test_parsed(self):
        self.assertTrue(
            self.CONSTRAINT.expression.endswith(".endswith('b')")
            or self.CONSTRAINT.expression.endswith('.endswith("b")')
        )
        expr = self.CONSTRAINT.expression
        pattern = r"___fandango.*___"
        re_search = re.search(pattern, expr)
        assert re_search is not None
        tmp_var = str(re_search.group(0))
        self.assertIn(tmp_var, self.CONSTRAINT.searches)
        search = self.CONSTRAINT.searches[tmp_var]
        assert search is not None
        assert isinstance(search, ItemSearch)
        base = search.base
        assert isinstance(base, RuleSearch)
        self.assertEqual(base.symbol, NonTerminal("<a>"))
        self.assertEqual(1, len(search.slices))
        self.assertEqual(0, search.slices[0])

    def test_valid(self):
        print(self.CONSTRAINT.format_as_spec())
        print(self.VALID_EXAMPLE.to_tree())
        self.assertTrue(self.CONSTRAINT.check(self.VALID_EXAMPLE))

    def test_invalid(self):
        self.assertFalse(self.CONSTRAINT.check(self.INVALID_EXAMPLE))
