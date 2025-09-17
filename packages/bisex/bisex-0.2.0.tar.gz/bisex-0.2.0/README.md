Bisex — Python Types -> TypeScript Types, no nonsense
========================================

Tiny, dependency‑free helper that turns your Python types into TypeScript:
dataclasses and TypedDicts become TS interfaces, Enums become TS enums, and
type aliases cross the bridge intact. You can also “record” Python functions
into TypeScript interfaces for a clean API contract.

No runtime imports, no spooky side effects — we read your .py files with the
AST. Add a dash of decorators for functions and call it a day.

Why? Because wiring types by hand is boring. Let robots help.

TL;DR (30 seconds)
------------------

```python
from pathlib import Path
from bisex import TsGen

gen = TsGen(
    py_types=["server/types.py", "domain/models.py"],
    out_ts=Path("web/src/lib/types.generated.ts"),
)

@gen.interface("Backend")
def ping(name: str) -> None:
    ...

gen.generate()  # writes web/src/lib/types.generated.ts
```

What it converts
----------------
- Dataclasses -> `export interface` (field annotations only)
- TypedDicts -> `export interface`
- Enums -> `export enum` (string/number members; computed values fallback to the member name string; negatives and floats are OK)
- Type aliases -> `export type` (PEP 695 `type`, `typing.TypeAlias`, and simple `MyT = int | str` forms)
- Function signatures -> `export interface` via `@gen.interface("Name")`

- Forward refs like `child: "Node"` in dataclasses stay as `Node` in TS.
- Variadic tuples like `tuple[int, ...]` become `(number)[]`.
- `list[T]` / `Sequence[T]` -> `(T)[]`; `dict[K, V]` -> `Record<K, V>`; `set[T]` -> `Set<T>`.
- `Callable[[A, B], R]` -> `(a1: A, a2: B) => R`.
- Missing function param annotations (when using `@gen.interface`) default to `any`.
- Missing function return annotation defaults to `void`. If you annotate `-> None` you’ll get `null` (as expected).

Minimal example
---------------
Python source (`types.py`):

```python
from dataclasses import dataclass
from enum import Enum
from typing import TypedDict


@dataclass
class User:
    name: str
    friend: "User"              # forward ref preserved as User
    tags: list[str]

class Flavor(Enum):
    VANILLA = "vanilla"
    MAGIC = 1 + 2               # computed -> becomes "MAGIC"

class UInfo(TypedDict):
    id: int
    label: str

type Id = int | str              # PEP 695
```

Generated TypeScript (excerpt):

```ts
export interface User {
  name: string;
  friend: User;
  tags: (string)[];
}

export enum Flavor {
  VANILLA = "vanilla",
  MAGIC = "MAGIC",
}

export interface UInfo {
  id: number;
  label: string;
}

export type Id = number | string;
```

Recording function APIs
-----------------------

```python
from bisex import TsGen

gen = TsGen(py_types=[], out_ts="types.generated.ts")

@gen.interface("Backend")
def hello(name: str) -> None:  # returns null in TS because it’s explicitly None
    ...

@gen.interface("Backend")
def add(a: int, b: int):       # no return annotation -> void
    ...

@gen.interface("Backend")
def maybe(x: str | None) -> str | None:
    ...

print(gen.produce_ts())
```

You’ll get:

```ts
export interface Backend {
  hello: (name: string) => null;
  add: (a: number, b: number) => void;
  maybe: (x: string | null) => string | null;
}
```

Async wrapper trick
-------------------
If your frontend calls back into Python (Eel, RPC, etc.), wrap returns:

```python
gen = TsGen(py_types=["types.py"], out_ts="web/types.generated.ts", return_wrapper="() => Promise<{ret}>")
```

Now `ret` in each signature is wrapped as a promise factory. Example:

```ts
hello: (name: string) => () => Promise<null>;
```

API (no fluff)
--------------
- `TsGen(py_types, out_ts, return_wrapper=None)`
  - `py_types`: `str | Path | Iterable[str | Path]` — .py files to scan for static types (dataclasses, TypedDicts, Enums, aliases)
  - `out_ts`: `Path | str` — output .ts file
  - `return_wrapper`: `str | None` — format string; `{ret}` is replaced with the return type
- `gen.interface(name: str)` — decorator capturing a function signature into an exported TS interface
- `gen.produce_ts() -> str` — return TypeScript as a string (no writes)
- `gen.generate() -> Path` — write to disk and return the output path

What we don’t do (yet)
----------------------
- Execute your modules. Static shapes come from the AST — no import side effects.
- Infer field optionality from default values. TS output ignores Python defaults.
- Cover every edge case of the typing module. Exotic stuff may fall back to `any`.

Troubleshooting
---------------
- “Why is my enum member a string of its own name?” — The value wasn’t a string/number literal (e.g. computed). That’s by design.
- “Why is a type `any`?” — The shape was too dynamic or gnarly. Add annotations or simplify the type expression.

Name, vibe, license
-------------------
- Name: because it converts both ways across the Python/TypeScript border (we know, we know).
- Vibe: tiny, focused, no heavy magic. Bring your own build glue.
- License: this folder is part of the WuWa Mod Manager repo. Extract and publish as you see fit. The package source lives under `bisex/` and is built via `pyproject.toml` in this directory.
