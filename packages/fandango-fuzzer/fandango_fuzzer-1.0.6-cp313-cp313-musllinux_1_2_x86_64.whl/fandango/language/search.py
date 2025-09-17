"""
The search module provides classes to search for specific non-terminals in a derivation tree that matches the
search criteria.
"""

import abc
from typing import Optional, Any

from fandango.language.symbols import NonTerminal
from fandango.language.tree import DerivationTree


class Container(abc.ABC):
    """
    Abstract class for a container that holds a list of derivation trees.
    It provides methods to get the list of trees and evaluate the container.
    The evaluation of a container can be anything.
    """

    @abc.abstractmethod
    def get_trees(self) -> list[DerivationTree]:
        """
        Get the list of derivation trees in the container.
        :return list[DerivationTree]: The list of derivation trees.
        """
        pass

    @abc.abstractmethod
    def evaluate(self) -> Any:
        """
        Evaluate the container.
        :return Any: The evaluation of the container.
        """
        pass


class Tree(Container):
    """
    Container that holds a single derivation tree.
    """

    def __init__(self, tree: DerivationTree):
        """
        Initialize the Tree container with the given derivation tree.
        :param DerivationTree tree: The derivation tree.
        """
        self.tree = tree

    def get_trees(self) -> list[DerivationTree]:
        """
        Get the list of derivation trees in the container.
        :return list[DerivationTree]: The list of derivation trees.
        """
        return [self.tree]

    def evaluate(self):
        """
        Evaluate the container. The evaluation of a Tree container is the tree itself.
        :return DerivationTree: The derivation tree.
        """
        return self.tree

    def __repr__(self):
        return "Tree(" + repr(self.tree.value()) + ")"

    def __str__(self):
        return str(self.tree)


class TreeList(Container):
    """
    Container that holds a list of derivation trees.
    """

    def __init__(self, trees: list[DerivationTree]):
        """
        Initialize the TreeList container with the given derivation trees.
        :param list[DerivationTree] trees: The list of derivation trees.
        """
        self.trees = trees

    def get_trees(self) -> list[DerivationTree]:
        """
        Get the list of derivation trees in the container.
        :return list[DerivationTree]: The list of derivation trees.
        """
        return self.trees

    def evaluate(self):
        """
        Evaluate the container. The evaluation of a TreeList container is the list of trees itself.
        :return list[DerivationTree]: The list of derivation trees.
        """
        return self.trees


class Length(Container):
    """
    Container that holds a list of derivation trees and evaluates to the length of the list.
    """

    def __init__(self, trees: list[DerivationTree]):
        """
        Initialize the Tree container with the given derivation trees.
        :param list[DerivationTree] trees: The list of derivation trees.
        """
        self.trees = trees

    def get_trees(self) -> list[DerivationTree]:
        """
        Get the list of derivation trees in the container.
        :return list[DerivationTree]: The list of derivation trees.
        """
        return self.trees

    def evaluate(self):
        """
        Evaluate the container. The evaluation of a Length container is the length of the list of trees.
        :return int: The length of the list of trees.
        """
        return len(self.trees)

    def __repr__(self):
        return "Length([" + ", ".join(repr(tree.value()) for tree in self.trees) + "])"

    def __str__(self):
        return repr(self)


class NonTerminalSearch(abc.ABC):
    """
    Abstract class for a non-terminal search.
    A non-terminal search is a search for specific non-terminals in a derivation tree.
    """

    IS_STAR = False  # Indicates that this is a star search

    @abc.abstractmethod
    def find(
        self,
        tree: DerivationTree,
        scope: Optional[dict[NonTerminal, DerivationTree]] = None,
        population: Optional[list[DerivationTree]] = None,
    ) -> list[Container]:
        """
        Find all the non-terminals in the derivation tree that match the search criteria.
        :param DerivationTree tree: The derivation tree.
        :param Optional[Dict[NonTerminal, list[DerivationTree]]] scope: The scope of non-terminals matching to trees.
        :param Optional[list[DerivationTree]] population: The population of derivation trees to search in.
        :return list[Container]: The list of containers that hold the matching derivation trees.
        """

    def quantify(
        self,
        tree: DerivationTree,
        scope: Optional[dict[NonTerminal, DerivationTree]] = None,
        population: Optional[list[DerivationTree]] = None,
    ) -> list[Container]:
        """
        Quantify the number of non-terminals in the derivation tree that match the search criteria.
        :param DerivationTree tree: The derivation tree.
        :param Optional[Dict[NonTerminal, list[DerivationTree]]] scope: The scope of non-terminals matching to trees.
        :param Optional[list[DerivationTree]] population: The population of derivation trees to search in.
        :return int: The number of matching non-terminals.
        """
        return self.find(tree, scope, population)

    @abc.abstractmethod
    def find_direct(
        self,
        tree: DerivationTree,
        scope: Optional[dict[NonTerminal, DerivationTree]] = None,
        population: Optional[list[DerivationTree]] = None,
    ) -> list[Container]:
        """
        Find the direct-child non-terminals in the derivation tree that match the search criteria.
        :param DerivationTree tree: The derivation tree.
        :param Optional[Dict[NonTerminal, list[DerivationTree]]] scope: The scope of non-terminals matching to trees.
        :param Optional[list[DerivationTree]] population: The population of derivation trees to search in.
        :return list[Container]: The list of containers that hold the matching derivation trees.
        """

    def find_all(
        self,
        trees: list[DerivationTree],
        scope: Optional[dict[NonTerminal, DerivationTree]] = None,
        population: Optional[list[DerivationTree]] = None,
    ) -> list[Container]:
        """
        Find all the non-terminals in the list of derivation trees that match the search criteria.
        :param list[DerivationTree] trees: The list of derivation trees.
        :param Optional[Dict[NonTerminal, list[DerivationTree]]] scope: The scope of non-terminals matching to trees.
        :param Optional[list[DerivationTree]] population: The population of derivation trees to search in.
        :return list[list[Container]]: The list of lists of containers that hold the matching derivation trees.
        """
        targets = []
        for tree in trees:
            targets.extend(self.find(tree, scope=scope, population=population))
        return targets

    def __repr__(self):
        raise NotImplementedError(
            "Repr not implemented, use method specific to your usecase"
        )

    def __str__(self):
        raise NotImplementedError(
            "Repr not implemented, use method specific to your usecase"
        )

    @abc.abstractmethod
    def format_as_spec(self) -> str:
        """
        Format as a string that can be used in a spec file.
        """

    @abc.abstractmethod
    def get_access_points(self) -> list[NonTerminal]:
        """
        Get the access points of the non-terminal search, i.e., the non-terminal that are considered in this search.
        :return list[NonTerminal]: The list of access points.
        """


class LengthSearch(NonTerminalSearch):
    """
    Non-terminal search that finds the length of the non-terminals that match the search criteria.
    """

    def __init__(self, value: NonTerminalSearch):
        """
        Initialize the LengthSearch with the given non-terminal search.
        :param NonTerminalSearch value: The non-terminal search.
        """
        self.value = value

    def find(
        self,
        tree: DerivationTree,
        scope: Optional[dict[NonTerminal, DerivationTree]] = None,
        population: Optional[list[DerivationTree]] = None,
    ) -> list[Container]:
        return [
            Length(
                sum(
                    [
                        container.get_trees()
                        for container in self.value.find(
                            tree, scope=scope, population=population
                        )
                    ],
                    [],
                )
            )
        ]

    def find_direct(
        self,
        tree: DerivationTree,
        scope: Optional[dict[NonTerminal, DerivationTree]] = None,
        population: Optional[list[DerivationTree]] = None,
    ) -> list[Container]:
        return [
            Length(
                sum(
                    [
                        container.get_trees()
                        for container in self.value.find_direct(
                            tree, scope=scope, population=population
                        )
                    ],
                    [],
                )
            )
        ]

    def format_as_spec(self) -> str:
        return f"|{self.value.format_as_spec()}|"

    def get_access_points(self):
        return self.value.get_access_points()


class RuleSearch(NonTerminalSearch):
    """
    Non-terminal search that finds the non-terminals that match the specific rule.
    """

    def __init__(self, symbol: NonTerminal):
        """
        Initialize the RuleSearch with the given non-terminal symbol.
        :param NonTerminal symbol: The non-terminal symbol.
        """
        self.symbol = symbol

    def find(
        self,
        tree: DerivationTree,
        scope: Optional[dict[NonTerminal, DerivationTree]] = None,
        population: Optional[list[DerivationTree]] = None,
    ) -> list[Container]:
        if scope and self.symbol in scope:
            return [Tree(scope[self.symbol])]
        else:
            return list(map(Tree, tree.find_all_trees(self.symbol)))

    def find_direct(
        self,
        tree: DerivationTree,
        scope: Optional[dict[NonTerminal, DerivationTree]] = None,
        population: Optional[list[DerivationTree]] = None,
    ) -> list[Container]:
        if scope and self.symbol in scope:
            return [Tree(scope[self.symbol])]
        else:
            return list(map(Tree, tree.find_direct_trees(self.symbol)))

    def get_access_points(self):
        return [self.symbol]

    def format_as_spec(self) -> str:
        return self.symbol.format_as_spec()


class AttributeSearch(NonTerminalSearch):
    """
    Non-terminal search that finds the non-terminals that first uses the base to find the non-terminals and then
    uses the attribute to find the non-terminals in the derivation trees found by the base.
    """

    def __init__(self, base: NonTerminalSearch, attribute: NonTerminalSearch):
        """
        Initialize the AttributeSearch with the given base and attribute non-terminal searches.
        :param NonTerminalSearch base: The base non-terminal search.
        :param NonTerminalSearch attribute: The attribute non-terminal search.
        """
        self.base = base
        self.attribute = attribute

    def find(
        self,
        tree: DerivationTree,
        scope: Optional[dict[NonTerminal, DerivationTree]] = None,
        population: Optional[list[DerivationTree]] = None,
    ) -> list[Container]:
        bases = self.base.find(tree, scope=scope, population=population)
        targets = []
        for base in bases:
            for t in base.get_trees():
                targets.extend(
                    self.attribute.find_direct(t, scope=scope, population=population)
                )
        return targets

    def find_direct(
        self,
        tree: DerivationTree,
        scope: Optional[dict[NonTerminal, DerivationTree]] = None,
        population: Optional[list[DerivationTree]] = None,
    ) -> list[Container]:
        bases = self.base.find_direct(tree, scope=scope, population=population)
        targets = []
        for base in bases:
            for t in base.get_trees():
                targets.extend(
                    self.attribute.find_direct(t, scope=scope, population=population)
                )
        return targets

    def format_as_spec(self) -> str:
        return f"{self.base.format_as_spec()}.{self.attribute.format_as_spec()}"

    def get_access_points(self):
        return self.attribute.get_access_points()


class DescendantAttributeSearch(NonTerminalSearch):
    """
    Non-terminal search that finds the non-terminals that first uses the base to find the non-terminals and then
    uses the attribute to find the non-terminals in the descendant derivation trees found by the base.
    """

    def __init__(self, base: NonTerminalSearch, attribute: NonTerminalSearch):
        """
        Initialize the DescendantAttributeSearch with the given base and attribute non-terminal searches.
        :param NonTerminalSearch base: The base non-terminal search.
        :param NonTerminalSearch attribute: The attribute non-terminal search.
        """
        self.base = base
        self.attribute = attribute

    def find(
        self,
        tree: DerivationTree,
        scope: Optional[dict[NonTerminal, DerivationTree]] = None,
        population: Optional[list[DerivationTree]] = None,
    ) -> list[Container]:
        bases = self.base.find(tree, scope=scope, population=population)
        targets = []
        for base in bases:
            for t in base.get_trees():
                targets.extend(
                    self.attribute.find(t, scope=scope, population=population)
                )
        return targets

    def find_direct(
        self,
        tree: DerivationTree,
        scope: Optional[dict[NonTerminal, DerivationTree]] = None,
        population: Optional[list[DerivationTree]] = None,
    ) -> list[Container]:
        bases = self.base.find_direct(tree, scope=scope, population=population)
        targets = []
        for base in bases:
            for t in base.get_trees():
                targets.extend(
                    self.attribute.find(t, scope=scope, population=population)
                )
        return targets

    def format_as_spec(self) -> str:
        return f"{self.base.format_as_spec()}..{self.attribute.format_as_spec()}"

    def get_access_points(self):
        return self.attribute.get_access_points()


class ItemSearch(NonTerminalSearch):
    """
    Non-terminal search that finds the non-terminals that get the items from the base non-terminal.
    """

    def __init__(
        self,
        base: NonTerminalSearch,
        slices: list[tuple[Any] | slice | int],
    ):
        """
        Initialize the ItemSearch with the given base and slices.
        :param NonTerminalSearch base: The base non-terminal
        :param tuple[Any] slices: The slices to get the items from the base non-terminal.
        """
        self.base = base
        self.slices = slices

    def _find(self, bases: list[Container]):
        return list(
            map(
                Tree,
                [
                    t.__getitem__(self.slices)
                    for base in bases
                    for t in base.get_trees()
                ],
            )
        )

    def find(
        self,
        tree: DerivationTree,
        scope: Optional[dict[NonTerminal, DerivationTree]] = None,
        population: Optional[list[DerivationTree]] = None,
    ) -> list[Container]:
        return self._find(self.base.find(tree, scope=scope, population=population))

    def find_direct(
        self,
        tree: DerivationTree,
        scope: Optional[dict[NonTerminal, DerivationTree]] = None,
        population: Optional[list[DerivationTree]] = None,
    ) -> list[Container]:
        return self._find(
            self.base.find_direct(tree, scope=scope, population=population)
        )

    def format_as_spec(self) -> str:
        slice_reprs = []
        for slice_ in self.slices:
            if isinstance(slice_, slice):
                slice_repr = ""
                if slice_.start is not None:
                    slice_repr += repr(slice_.start)
                slice_repr += ":"
                if slice_.stop is not None:
                    slice_repr += repr(slice_.stop)
                if slice_.step is not None:
                    slice_repr += ":" + repr(slice_.step)
                slice_reprs.append(slice_repr)
            else:
                slice_reprs.append(repr(slice_))
        return f"{self.base.format_as_spec()}[{', '.join(slice_reprs)}]"

    def get_access_points(self):
        return self.base.get_access_points()


class SelectiveSearch(NonTerminalSearch):
    """
    Non-terminal search that finds the non-terminals that match the selective search criteria.
    """

    def __init__(
        self,
        base: NonTerminalSearch,
        symbols: list[tuple[NonTerminal, bool]],
        slices: Optional[list[Optional[Any]]] = None,
    ):
        """
        Initialize the SelectiveSearch with the given base, symbols, and slices.
        :param NonTerminalSearch base: The base non-terminal search.
        :param list[tuple[NonTerminal, bool]] symbols: The list of symbols and whether to find direct or all trees.
        :param list[Optional[Any]] slices: The list of slices to get the items from the symbols.
        """
        self.base = base
        self.symbols = symbols
        self.slices = slices or [None] * len(symbols)

    def _find(self, bases: list[Container]):
        result = []
        for symbol, is_direct, items in zip(*zip(*self.symbols), self.slices):
            if is_direct:
                children = [
                    t.find_direct_trees(symbol)
                    for base in bases
                    for t in base.get_trees()
                ]
            else:
                children = [
                    t.find_all_trees(symbol) for base in bases for t in base.get_trees()
                ]
            if items is not None:
                for index, child in enumerate(children):
                    values = child.__getitem__(items)
                    children[index] = values if isinstance(values, list) else [values]
            result.extend(sum(children, []))
        return list(map(Tree, result))

    def find(
        self,
        tree: DerivationTree,
        scope: Optional[dict[NonTerminal, DerivationTree]] = None,
        population: Optional[list[DerivationTree]] = None,
    ) -> list[Container]:
        ret = self._find(self.base.find(tree, scope=scope, population=population))
        return ret

    def find_direct(
        self,
        tree: DerivationTree,
        scope: Optional[dict[NonTerminal, DerivationTree]] = None,
        population: Optional[list[DerivationTree]] = None,
    ) -> list[Container]:
        ret = self._find(self.base.find_direct(tree, scope=scope, population=None))
        return ret

    def format_as_spec(self) -> str:
        slice_reprs: list[str] = []
        for symbol, is_direct, items in zip(*self.symbols, self.slices):
            slice_repr = f"{'' if is_direct else '*'}{symbol.format_as_spec()}"
            if items is not None:
                slice_repr += ": "
                if isinstance(items, slice):
                    if items.start is not None:
                        slice_repr += repr(items.start)
                    slice_repr += ":"
                    if items.stop is not None:
                        slice_repr += repr(items.stop)
                    if items.step is not None:
                        slice_repr += ":" + repr(items.step)
                else:
                    slice_reprs += repr(items)
            slice_reprs.append(slice_repr)
        return f"{self.base.format_as_spec()}{{{', '.join(slice_reprs)}}}"

    def get_access_points(self):
        return [symbol for symbol, _ in self.symbols]


class StarSearch(NonTerminalSearch):
    """
    Non-terminal search that finds the non-terminals that match the star search criteria.
    """

    IS_STAR = True  # Indicates that this is a star search

    def __init__(self, base: NonTerminalSearch):
        """
        Initialize the StarSearch with the given base non-terminal search.
        :param NonTerminalSearch base: The base non-terminal search.
        """
        self.base = base

    def _find(
        self,
        tree: DerivationTree,
        scope: Optional[dict[NonTerminal, DerivationTree]] = None,
        population: Optional[list[DerivationTree]] = None,
    ) -> list[DerivationTree]:
        return sum(
            [
                r.get_trees()
                for r in self.base.find(tree, scope=scope, population=population)
            ],
            [],
        )

    def find(
        self,
        tree: DerivationTree,
        scope: Optional[dict[NonTerminal, DerivationTree]] = None,
        population: Optional[list[DerivationTree]] = None,
    ) -> list[Container]:
        return [TreeList(self._find(tree, scope=scope, population=population))]

    def quantify(
        self,
        tree: DerivationTree,
        scope: Optional[dict[NonTerminal, DerivationTree]] = None,
        population: Optional[list[DerivationTree]] = None,
    ) -> list[Container]:
        """
        Quantify the number of non-terminals in the derivation tree that match the star search criteria.
        :param DerivationTree tree: The derivation tree.
        :param Optional[Dict[NonTerminal, list[DerivationTree]]] scope: The scope of non-terminals matching to trees.
        :param Optional[list[DerivationTree]] population: The population of derivation trees to search in.
        :return int: The number of matching non-terminals.
        """
        return [
            Tree(tree) for tree in self._find(tree, scope=scope, population=population)
        ]

    def find_direct(
        self,
        tree: DerivationTree,
        scope: Optional[dict[NonTerminal, DerivationTree]] = None,
        population: Optional[list[DerivationTree]] = None,
    ) -> list[Container]:
        trees = sum(
            [
                r.get_trees()
                for r in self.base.find_direct(tree, scope=scope, population=population)
            ],
            [],
        )
        return [TreeList(trees)]

    def format_as_spec(self) -> str:
        return f"*{self.base.format_as_spec()}"

    def get_access_points(self) -> list[NonTerminal]:
        return self.base.get_access_points()


class PopulationSearch(NonTerminalSearch):
    """
    Non-terminal search that finds the non-terminals that match the star search criteria in the entire population.
    """

    IS_STAR = True

    def __init__(self, base: NonTerminalSearch):
        """
        Initialize the PopulationSearch with the given base non-terminal search.
        :param NonTerminalSearch base: The base non-terminal search.
        """
        self.base = base

    def _find(
        self,
        scope: Optional[dict[NonTerminal, DerivationTree]] = None,
        population: Optional[list[DerivationTree]] = None,
    ) -> list[DerivationTree]:
        if population is None:
            raise ValueError("Population is required for PopulationSearch")
        return sum(
            [
                r.get_trees()
                for r in self.base.find_all(
                    population, scope=scope, population=population
                )
            ],
            [],
        )

    def find(
        self,
        tree: DerivationTree,
        scope: Optional[dict[NonTerminal, DerivationTree]] = None,
        population: Optional[list[DerivationTree]] = None,
    ) -> list[Container]:
        return [TreeList(self._find(scope=scope, population=population))]

    def quantify(
        self,
        tree: DerivationTree,
        scope: Optional[dict[NonTerminal, DerivationTree]] = None,
        population: Optional[list[DerivationTree]] = None,
    ) -> list[Container]:
        """
        Quantify the number of non-terminals in the derivation tree that match the star search criteria.
        :param DerivationTree tree: The derivation tree.
        :param Optional[Dict[NonTerminal, list[DerivationTree]]] scope: The scope of non-terminals matching to trees.
        :param Optional[list[DerivationTree]] population: The population of derivation trees to search in.
        :return int: The number of matching non-terminals.
        """
        return [Tree(tree) for tree in self._find(scope=scope, population=population)]

    def find_direct(
        self,
        tree: DerivationTree,
        scope: Optional[dict[NonTerminal, DerivationTree]] = None,
        population: Optional[list[DerivationTree]] = None,
    ) -> list[Container]:
        if population is None:
            raise ValueError("Population is required for PopulationSearch")
        trees = sum(
            [
                r.get_trees()
                for r in self.base.find_all(
                    population, scope=scope, population=population
                )
            ],
            [],
        )
        return [TreeList(trees)]

    def format_as_spec(self) -> str:
        return f"**{self.base.format_as_spec()}"

    def get_access_points(self) -> list[NonTerminal]:
        return self.base.get_access_points()
