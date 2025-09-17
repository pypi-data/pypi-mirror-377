from __future__ import annotations

import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent
from typing import Callable, Literal, Annotated, Mapping, MutableMapping, Sequence, Iterable, Type, Dict

from bisex import TsGen
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

# Make Windows console behave (ASCII-only frames, UTF-8 text)
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


@dataclass
class Case:
    name: str
    description: str
    python: str
    runner: Callable[[], str]
    detector: Callable[[str], tuple[bool, str]]


def _generate_from_source(src: str, write_to: Path | None = None) -> str:
    """Generate TS from a Python snippet. If write_to is given, also write to disk."""
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        src_path = base / "types.py"
        out_path = write_to or (base / "types.generated.ts")
        src_path.write_text(src, encoding="utf-8")
        gen = TsGen(py_types=[src_path], out_ts=out_path)
        # If caller asked for a file, write it; otherwise just produce the text
        return gen.generate().read_text(encoding="utf-8") if write_to else gen.produce_ts()


def _generate_from_sources(sources: dict[str, str], write_to: Path | None = None) -> str:
    """Generate TS from multiple Python source files.

    sources: mapping of filename -> python code
    write_to: optional output .ts path to write
    """
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        py_paths: list[Path] = []
        for name, code in sources.items():
            p = base / name
            p.write_text(code, encoding="utf-8")
            py_paths.append(p)
        out_path = write_to or (base / "types.generated.ts")
        gen = TsGen(py_types=py_paths, out_ts=out_path)
        return gen.generate().read_text(encoding="utf-8") if write_to else gen.produce_ts()


def _build_cases() -> list[Case]:
    cases: list[Case] = []

    # 1) Static types overview (dataclass, enum, TypedDict, alias) and write to dist/
    static_src = dedent(
        """
        from dataclasses import dataclass
        from enum import Enum
        from typing import TypedDict

        @dataclass
        class User:
            name: str
            friend: "User"  # forward ref preserved
            tags: list[str]

        class Kind(Enum):
            A = "a"
            B = -1
            C = 1 + 2  # computed -> becomes "C"

        class UInfo(TypedDict):
            id: int
            label: str

        type MyId = int | str
        """
    ).strip()

    def static_run() -> str:
        out = Path("dist/types.demo.generated.ts")
        out.parent.mkdir(parents=True, exist_ok=True)
        return _generate_from_source(static_src, write_to=out)

    def static_detect(ts: str) -> tuple[bool, str]:
        ok = (
            "export interface User {" in ts
            and "friend: User;" in ts
            and "export enum Kind {" in ts
            and "B = -1" in ts
            and 'C = "C"' in ts
            and "export interface UInfo {" in ts
            and "export type MyId = number | string;" in ts
        )
        note = "Wrote dist/types.demo.generated.ts and printed result here."
        return (not ok), (note if ok else "Static conversion missing expected parts.")

    cases.append(
        Case(
            name="Static Types Overview",
            description="Dataclass, Enum, TypedDict, and PEP 695 alias → TS (and file written).",
            python=static_src,
            runner=static_run,
            detector=static_detect,
        )
    )

    # 2) Forward reference (self-referential)
    forward_src = dedent(
        """
        from dataclasses import dataclass

        @dataclass
        class Node:
            label: str
            child: "Node"
        """
    ).strip()

    def forward_run() -> str:
        return _generate_from_source(forward_src)

    def forward_detect(ts: str) -> tuple[bool, str]:
        ok = ("child: Node;" in ts)
        note = "Forward ref preserved as Node."
        return (not ok), (note if ok else "Forward ref did not resolve.")

    cases.append(
        Case(
            name="Forward Reference",
            description="Self-referential dataclass using string annotation.",
            python=forward_src,
            runner=forward_run,
            detector=forward_detect,
        )
    )

    # 3) Interfaces + wrapper (unannotated param → any; wrapper for returns)
    interface_src = dedent(
        """
        from bisex import TsGen

        gen = TsGen(py_types=[], out_ts="types.generated.ts", return_wrapper="() => Promise<{ret}>")

        @gen.interface("Backend")
        def hello(name: str) -> None:
            ...

        @gen.interface("Backend")
        def add(a: int, b: int):  # no return annotation → void (then wrapped)
            ...

        @gen.interface("Backend")
        def echo(x: str | None) -> str | None:
            ...
        """
    ).strip()

    def interface_run() -> str:
        gen = TsGen(py_types=[], out_ts=Path("dummy.ts"), return_wrapper="() => Promise<{ret}>")

        @gen.interface("Backend")
        def hello(name: str) -> None:
            ...

        @gen.interface("Backend")
        def add(a: int, b: int):
            ...

        @gen.interface("Backend")
        def echo(x: str | None) -> str | None:
            ...

        return gen.produce_ts()

    def interface_detect(ts: str) -> tuple[bool, str]:
        ok = (
            "export interface Backend {" in ts
            and "hello: (name: string) => () => Promise<null>;" in ts
            and "add: (a: number, b: number) => () => Promise<void>;" in ts
            and "echo: (x: string | null) => () => Promise<string | null>;" in ts
        )
        return (not ok), ("Decorator capture looks good." if ok else "Interface output mismatch.")

    cases.append(
        Case(
            name="Interfaces + Wrapper",
            description="Capture functions into an interface; wrap returns as promises.",
            python=interface_src,
            runner=interface_run,
            detector=interface_detect,
        )
    )

    # 4) Multi-file project snapshot (realistic split modules)
    mf_models = dedent(
        """
        from dataclasses import dataclass

        @dataclass
        class User:
            id: int
            name: str

        @dataclass
        class Post:
            title: str
            author: "User"
            tags: list[str]
        """
    ).strip()
    mf_enums = dedent(
        """
        from enum import Enum

        class Role(Enum):
            ADMIN = "admin"
            USER = "user"
            GUEST = 0
            MIX = 1 + 1   # becomes "MIX"
        """
    ).strip()
    mf_aliases = "type UserId = int | str\n".strip()
    mf_schema = dedent(
        """
        from typing import TypedDict

        class ApiError(TypedDict):
            code: int
            message: str
        """
    ).strip()

    def mf_run() -> str:
        # Aggregate into a single demo output file
        out = Path("dist/project.demo.generated.ts")
        out.parent.mkdir(parents=True, exist_ok=True)
        return _generate_from_sources(
            {
                "models.py": mf_models,
                "enums.py": mf_enums,
                "aliases.py": mf_aliases,
                "schema.py": mf_schema,
            },
            write_to=out,
        )

    def mf_detect(ts: str) -> tuple[bool, str]:
        ok = (
            "export interface User {" in ts
            and "export interface Post {" in ts
            and "author: User;" in ts
            and "export enum Role {" in ts
            and 'ADMIN = "admin"' in ts
            and 'MIX = "MIX"' in ts
            and "export type UserId = number | string;" in ts
            and "export interface ApiError {" in ts
        )
        note = "Wrote dist/project.demo.generated.ts with combined declarations."
        return (not ok), (note if ok else "Multi-file conversion missing expected parts.")

    mf_display = (
        "# models.py\n" + mf_models + "\n\n# enums.py\n" + mf_enums + "\n\n# aliases.py\n" + mf_aliases + "\n\n# schema.py\n" + mf_schema
    )
    cases.append(
        Case(
            name="Multi-file Snapshot",
            description="Scan multiple source files and combine TS output.",
            python=mf_display,
            runner=mf_run,
            detector=mf_detect,
        )
    )

    # 5) Interface typing sampler (broader typing module coverage)
    sampler_src = dedent(
        """
        from typing import Callable, Literal, Annotated, Mapping, MutableMapping, Sequence, Iterable, Type, Dict
        from bisex import TsGen

        gen = TsGen(py_types=[], out_ts="demo.ts")

        @gen.interface("More")
        def f_list(a: list[int]) -> list[str]: ...

        @gen.interface("More")
        def f_seq(a: Sequence[str]) -> Sequence[int]: ...

        @gen.interface("More")
        def f_map(m: dict[str, float]) -> Dict[str, float]: ...

        @gen.interface("More")
        def f_mapping(m: Mapping[str, int]) -> MutableMapping[str, int]: ...

        @gen.interface("More")
        def f_set(s: set[int]) -> set[int]: ...

        @gen.interface("More")
        def f_call(cb: Callable[[int, str], bool]) -> None: ...

        @gen.interface("More")
        def f_ann(x: Annotated[int, "meta"]) -> Annotated[str, "m"]: ...

        @gen.interface("More")
        def f_lit(x: Literal['a', 1, True]) -> Literal['b']: ...

        @gen.interface("More")
        def f_type(t: Type[str]) -> Type[int]: ...
        """
    ).strip()

    def sampler_run() -> str:
        gen = TsGen(py_types=[], out_ts=Path("demo.ts"))

        @gen.interface("More")
        def f_list(a: list[int]) -> list[str]:
            ...

        @gen.interface("More")
        def f_seq(a: Sequence[str]) -> Sequence[int]:
            ...

        @gen.interface("More")
        def f_map(m: dict[str, float]) -> Dict[str, float]:
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

        return gen.produce_ts()

    def sampler_detect(ts: str) -> tuple[bool, str]:
        checks = [
            "f_list: (a: (number)[]) => (string)[];",
            "f_seq: (a: (string)[]) => (number)[];",
            "f_map: (m: Record<string, number>) => Record<string, number>;",
            "f_mapping: (m: Record<string, number>) => Record<string, number>;",
            "f_set: (s: Set<number>) => Set<number>;",
            "f_call: (cb: (a1: number, a2: string) => boolean) => null;",
            "f_ann: (x: number) => string;",
            'f_lit: (x: "a" | 1 | true) => "b";',
            "f_type: (t: new (...args: any[]) => string) => new (...args: any[]) => number;",
        ]
        ok = all(c in ts for c in checks)
        return (not ok), ("Covers a broad set of typing constructs." if ok else "Typing sampler mismatch.")

    cases.append(
        Case(
            name="Interface Typing Sampler",
            description="Showcase coverage of Python typing module in interfaces.",
            python=sampler_src,
            runner=sampler_run,
            detector=sampler_detect,
        )
    )

    # 6) Enum variants (negatives, floats, strings, computed)
    enum_src = dedent(
        """
        from enum import Enum

        class K(Enum):
            NEG = -1
            PI = 3.14
            NAME = "n"
            SUM = 1 + 2  # not a literal; becomes name string
        """
    ).strip()

    def enum_run() -> str:
        return _generate_from_source(enum_src)

    def enum_detect(ts: str) -> tuple[bool, str]:
        ok = (
            "export enum K {" in ts
            and "NEG = -1" in ts
            and "PI = 3.14" in ts
            and 'NAME = "n"' in ts
            and 'SUM = "SUM"' in ts
        )
        return (not ok), ("Enum literal handling looks correct." if ok else "Enum handling mismatch.")

    cases.append(
        Case(
            name="Enum Variants",
            description="Enum with negatives/floats/strings/computed values.",
            python=enum_src,
            runner=enum_run,
            detector=enum_detect,
        )
    )

    return cases


def _render_case(console: Console, case: Case, ts: str, flagged: bool, note: str) -> None:
    console.rule(f"{case.name}", characters="-")
    console.print(Text(case.description, style="bold"))
    console.print(
        Panel(
            Syntax(case.python, "python", theme="monokai", line_numbers=True),
            title="Python input",
            box=box.SIMPLE,
        )
    )
    console.print(
        Panel(
            Syntax(ts.rstrip() or "(no output)", "ts", theme="monokai", line_numbers=True),
            title="Generated TypeScript",
            box=box.SIMPLE,
        )
    )
    status_style = "bold red" if flagged else "bold green"
    status_title = "Check" if flagged else "Status"
    console.print(Panel(Text(note, style=status_style), title=status_title, box=box.SIMPLE))


def main() -> None:
    console = Console(legacy_windows=False)
    cases = _build_cases()
    console.print(Text("Bisex TsGen demo", style="bold magenta"))
    results: list[tuple[Case, bool, str, str]] = []
    for case in cases:
        ts = case.runner()
        flagged, note = case.detector(ts)
        results.append((case, flagged, note, ts))
        _render_case(console, case, ts, flagged, note)

    summary = Table(title="Demo Summary", header_style="bold cyan", box=box.SIMPLE)
    summary.add_column("Scenario", style="cyan")
    summary.add_column("Pass", style="magenta")
    summary.add_column("Note", style="yellow")
    for case, flagged, note, _ in results:
        status = "[bold green]yes[/]" if not flagged else "[bold red]no[/]"
        summary.add_row(case.name, status, note)

    console.print()
    console.print(summary)


if __name__ == "__main__":
    main()
