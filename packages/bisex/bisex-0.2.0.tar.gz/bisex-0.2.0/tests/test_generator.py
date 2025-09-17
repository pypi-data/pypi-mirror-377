import unittest
import tempfile
from pathlib import Path
import ast

from bisex import TsGen


def _generate_ts(src: str) -> str:
    with tempfile.TemporaryDirectory() as td:
        src_path = Path(td) / "types.py"
        src_path.write_text(src, encoding="utf-8")
        gen = TsGen(py_types=[src_path], out_ts=Path(td) / "out.ts")
        return gen.produce_ts()


class TestTsGen(unittest.TestCase):
    def test_static_types_generation(self):
        src = """
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional, Union, TypedDict

@dataclass
class User:
    name: str
    age: int
    tags: List[str]
    meta: Dict[str, int]
    nickname: Optional[str]
    rating: Union[int, float]

class Kind(Enum):
    A = "a"
    B = 2
    C = 1 + 1

try:
    from typing import TypeAlias
    type MyId = int | str
except Exception:
    pass

class UInfo(TypedDict):
    id: int
    label: str
"""

        ts = _generate_ts(src)
        self.assertIn("export interface User {", ts)
        self.assertIn("name: string;", ts)
        self.assertIn("age: number;", ts)
        self.assertIn("tags: (string)[];", ts)
        self.assertIn("meta: Record<string, number>;", ts)
        self.assertIn("nickname: string | null;", ts)
        self.assertIn("rating: number;", ts)

        self.assertIn("export enum Kind {", ts)
        self.assertIn('A = "a"', ts)
        self.assertIn("B = 2", ts)
        self.assertIn('C = "C"', ts)

        if hasattr(ast, "TypeAlias"):
            self.assertIn("export type MyId = number | string;", ts)

        self.assertIn("export interface UInfo {", ts)
        self.assertIn("id: number;", ts)
        self.assertIn("label: string;", ts)

    def test_callable_aliases(self):
        src = """
from typing import Callable

type Fn = Callable[[str], Callable[[int], str]]
"""

        ts = _generate_ts(src)
        self.assertIn("export type Fn = (a1: string) => (a1: number) => string;", ts)

    def test_special_collections_aliases(self):
        src = """
from typing import Deque, DefaultDict, Counter, Awaitable

Items = Deque[int]
Scores = DefaultDict[str, float]
Counts = Counter[str]
Task = Awaitable[int]
"""

        ts = _generate_ts(src)
        self.assertIn("export type Items = (number)[];", ts)
        self.assertIn("export type Scores = Record<string, number>;", ts)
        self.assertIn("export type Counts = Record<string, number>;", ts)
        self.assertIn("export type Task = Promise<number>;", ts)

    def test_interface_generation(self):
        gen = TsGen(py_types=[], out_ts=Path("dummy"))

        @gen.interface("API")
        def ping(name: str) -> None:
            ...

        @gen.interface("API")
        def add(a: int, b: int) -> int:
            ...

        @gen.interface("API")
        def maybe(x: str | None) -> str | None:
            ...

        ts = gen.produce_ts()
        self.assertIn("export interface API {", ts)
        self.assertIn("ping: (name: string) => null;", ts)
        self.assertIn("add: (a: number, b: number) => number;", ts)
        self.assertIn("maybe: (x: string | null) => string | null;", ts)

    def test_return_wrapper(self):
        gen = TsGen(py_types=[], out_ts=Path("dummy"), return_wrapper="() => Promise<{ret}>")

        @gen.interface("Svc")
        def hello(x: str) -> None:
            ...

        ts = gen.produce_ts()
        self.assertIn("export interface Svc {", ts)
        self.assertIn("hello: (x: string) => () => Promise<null>;", ts)

    def test_annotation_coverage_interfaces(self):
        from typing import Callable, Literal, Annotated, Mapping, MutableMapping, Sequence, Type

        gen = TsGen(py_types=[], out_ts=Path("dummy"))

        @gen.interface("More")
        def f_list(a: list[int]) -> list[str]:
            ...

        @gen.interface("More")
        def f_seq(a: Sequence[str]) -> Sequence[int]:
            ...

        @gen.interface("More")
        def f_map(m: dict[str, float]) -> Mapping[str, float]:
            ...

        @gen.interface("More")
        def f_mapping(m: Mapping[str, int]) -> MutableMapping[str, int]:
            ...

        @gen.interface("More")
        def f_set(s: set[int]) -> set[int]:
            ...

        @gen.interface("More")
        def f_call(cb: Callable[[int, str], bool]) -> None:
            ...

        @gen.interface("More")
        def f_ann(x: Annotated[int, "meta"]) -> Annotated[str, "m"]:
            ...

        @gen.interface("More")
        def f_lit(x: Literal['a', 1, True]) -> Literal['b']:
            ...

        @gen.interface("More")
        def f_type(t: Type[str]) -> Type[int]:
            ...

        ts = gen.produce_ts()
        self.assertIn("export interface More {", ts)
        self.assertIn("f_list: (a: (number)[]) => (string)[];", ts)
        self.assertIn("f_seq: (a: (string)[]) => (number)[];", ts)
        self.assertIn("f_map: (m: Record<string, number>) => Record<string, number>;", ts)
        self.assertIn("f_mapping: (m: Record<string, number>) => Record<string, number>;", ts)
        self.assertIn("f_set: (s: Set<number>) => Set<number>;", ts)
        self.assertIn("f_call: (cb: (a1: number, a2: string) => boolean) => null;", ts)
        self.assertIn("f_ann: (x: number) => string;", ts)
        self.assertIn("f_lit: (x: \"a\" | 1 | true) => \"b\";", ts)
        self.assertIn("f_type: (t: new (...args: any[]) => string) => new (...args: any[]) => number;", ts)

    def test_type_alias_variants(self):
        src = """
from typing import Optional, TypeAlias

MyNum = int
UserId: TypeAlias = str
MaybeStr: TypeAlias = Optional[str]
VERSION = "1.0.0"
FLAGS = 3
"""

        ts = _generate_ts(src)
        self.assertIn("export type MyNum = number;", ts)
        self.assertIn("export type UserId = string;", ts)
        self.assertIn("export type MaybeStr = string | null;", ts)
        self.assertNotIn("export type VERSION", ts)
        self.assertNotIn("export type FLAGS", ts)

    def test_forward_reference_and_tuple_variadic(self):
        src = """
from dataclasses import dataclass

@dataclass
class Node:
    label: str
    child: "Node"

@dataclass
class Bag:
    items: tuple[int, ...]
"""

        ts = _generate_ts(src)
        self.assertIn("export interface Node {", ts)
        self.assertIn("child: Node;", ts)
        self.assertIn("items: (number)[];", ts)

    def test_interface_missing_annotations_default_to_any(self):
        gen = TsGen(py_types=[], out_ts=Path("dummy"))

        @gen.interface("Fallback")
        def broken(arg, ok: int):
            ...

        ts = gen.produce_ts()
        self.assertIn("export interface Fallback {", ts)
        self.assertIn("arg: any", ts)

    def test_enum_negative_and_float(self):
        src = """
from enum import Enum

class K(Enum):
    NEG = -1
    PI = 3.14
    NAME = "n"
    SUM = 1 + 2
"""

        ts = _generate_ts(src)
        self.assertIn("export enum K {", ts)
        self.assertIn("NEG = -1", ts)
        self.assertIn("PI = 3.14", ts)
        self.assertIn('NAME = "n"', ts)
        self.assertIn('SUM = "SUM"', ts)


if __name__ == "__main__":
    unittest.main()
