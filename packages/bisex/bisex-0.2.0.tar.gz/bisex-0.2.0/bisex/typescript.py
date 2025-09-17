from __future__ import annotations

"""
TypeScript type resolution utilities.

This module provides a single entry point, `TsTypeResolver`, which can
translate both Python AST type expressions and runtime annotations from the
`typing` module into TypeScript type strings. The resolver is designed to be
re-usable and testable, and is used by both static extraction (AST) and the
runtime interface decorator.
"""

from typing import Any, Final, List, Tuple, get_args, get_origin
import typing as _t
import collections.abc as _abc
import ast


PY_PRIMITIVE_TO_TS: Final[dict[str, str]] = {
    "str": "string",
    "int": "number",
    "float": "number",
    "bool": "boolean",
    "None": "null",
    "NoneType": "null",
    "Any": "any",
}


def _map_primitive(name: str) -> str:
    return PY_PRIMITIVE_TO_TS.get(name, name)


def _dedupe(parts: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for part in parts:
        if part not in seen:
            seen.add(part)
            result.append(part)
    return result


def _callable_ast_to_ts(resolver: "TsTypeResolver", node: ast.AST) -> str:
    if isinstance(node, ast.Tuple) and len(node.elts) == 2:
        args_expr, ret_expr = node.elts
        if isinstance(args_expr, ast.List):
            params = [
                f"a{i+1}: {resolver.ts_from_ast(arg)}"
                for i, arg in enumerate(args_expr.elts)
            ]
            params_ts = ", ".join(params)
        elif isinstance(args_expr, ast.Name) and args_expr.id == "Ellipsis":
            params_ts = "...args: any[]"
        else:
            params_ts = ""
        ret_ts = resolver.ts_from_ast(ret_expr)
        return f"({params_ts}) => {ret_ts}"
    return "(...args: any[]) => any"


class TsTypeResolver:
    """Translate Python AST and runtime annotations to TypeScript strings."""

    # ------------------ AST -> TS ------------------
    def ts_from_ast(self, expr: ast.AST) -> str:
        match expr:
            case ast.Name(id=name):
                return _map_primitive(name)
            case ast.Attribute(attr=attr):
                if attr in {"List", "Dict", "Union", "Optional"}:
                    return attr
                return _map_primitive(attr)
            case ast.BinOp(left=l, op=ast.BitOr(), right=r):
                return f"{self.ts_from_ast(l)} | {self.ts_from_ast(r)}"
            case ast.Subscript(value=v, slice=s):
                base = None
                if isinstance(v, ast.Name):
                    base = v.id
                elif isinstance(v, ast.Attribute):
                    base = v.attr

                # py<3.9
                if isinstance(s, ast.Index):  # type: ignore[attr-defined]
                    s = s.value  # type: ignore[attr-defined]

                if base in {"List", "list"}:
                    return f"({self.ts_from_ast(s)})[]"
                if base in {"Dict", "dict"}:
                    if isinstance(s, ast.Tuple) and len(s.elts) == 2:
                        k, v = s.elts
                    else:
                        k = v = ast.Name(id="Any")
                    return f"Record<{self.ts_from_ast(k)}, {self.ts_from_ast(v)}>"
                if base == "Union":
                    if isinstance(s, ast.Tuple):
                        parts = _dedupe([self.ts_from_ast(e) for e in s.elts])
                        return " | ".join(parts)
                    return self.ts_from_ast(s)
                if base == "Optional":
                    return f"{self.ts_from_ast(s)} | null"
                if base in {"Deque", "deque"}:
                    return f"({self.ts_from_ast(s)})[]"
                if base == "DefaultDict":
                    if isinstance(s, ast.Tuple) and len(s.elts) == 2:
                        k, v = s.elts
                    else:
                        k = v = ast.Name(id="Any")
                    return f"Record<{self.ts_from_ast(k)}, {self.ts_from_ast(v)}>"
                if base == "Counter":
                    key = self.ts_from_ast(s)
                    return f"Record<{key}, number>"
                if base == "Awaitable":
                    return f"Promise<{self.ts_from_ast(s)}>"
                if base == "Callable":
                    return _callable_ast_to_ts(self, s)
                if base in {"Tuple", "tuple"}:
                    if isinstance(s, ast.Tuple):
                        elts = list(s.elts)
                        # Detect tuple[T, ...]
                        if elts and (
                            (isinstance(elts[-1], ast.Constant) and elts[-1].value is Ellipsis)
                            or isinstance(elts[-1], ast.Ellipsis)
                            or (isinstance(elts[-1], ast.Name) and elts[-1].id == "Ellipsis")
                        ):
                            inner_node = elts[0] if elts[:-1] else ast.Name(id="Any")
                            return f"({self.ts_from_ast(inner_node)})[]"
                        return "[" + ", ".join(self.ts_from_ast(e) for e in elts) + "]"
                    # A single subscript: treat as array of that type
                    return f"({self.ts_from_ast(s)})[]"
                return "any"
            case ast.Constant(value=v):
                if v is None:
                    return "null"
                if isinstance(v, str):
                    # If it's a primitive alias, return it
                    mapped = _map_primitive(v)
                    if mapped != v:
                        return mapped
                    # Try to parse as a type expr (e.g. "list[int]")
                    try:
                        parsed = ast.parse(v, mode="eval")
                    except SyntaxError:
                        parsed = None
                    else:
                        expr = getattr(parsed, "body", None)
                        if not (
                            isinstance(expr, ast.Constant)
                            and isinstance(expr.value, str)
                            and expr.value == v
                        ):
                            return self.ts_from_ast(expr)
                    # If identifier-ish (including dotted), treat as nominal type
                    if all(part.isidentifier() for part in v.split(".")):
                        return v
                    return "string"
                if isinstance(v, (int, float)):
                    return "number"
                if isinstance(v, bool):
                    return "boolean"
                if v is Ellipsis:
                    return "..."
                return "any"
            case _:
                return "any"

    # -------------- Runtime -> TS --------------
    @staticmethod
    def string_anno_to_ts(text: str) -> str:
        import re as _re
        s = text.strip()
        for pat, rep in [
            (r"\bNone\b", "null"),
            (r"\bstr\b", "string"),
            (r"\bint\b", "number"),
            (r"\bfloat\b", "number"),
            (r"\bbool\b", "boolean"),
        ]:
            s = _re.sub(pat, rep, s)
        return s

    def anno_to_ts(self, anno: Any) -> str:
        if isinstance(anno, str):
            return self.string_anno_to_ts(anno)
        if anno is None or anno is type(None):  # noqa: E721
            return "null"
        origin = get_origin(anno)
        args = get_args(anno)

        if origin in (list, List, _t.Sequence, _t.MutableSequence, _t.Iterable, _abc.Sequence, _abc.MutableSequence, _abc.Iterable):
            inner = self.anno_to_ts(args[0]) if args else "any"
            return f"({inner})[]"
        if origin in (dict, _t.Dict, _t.Mapping, _t.MutableMapping, _abc.Mapping, _abc.MutableMapping):
            k = self.anno_to_ts(args[0]) if len(args) >= 1 else "any"
            v = self.anno_to_ts(args[1]) if len(args) >= 2 else "any"
            return f"Record<{k}, {v}>"
        if origin in (set, _t.Set, _t.AbstractSet, _t.FrozenSet, frozenset, _abc.Set):
            inner = self.anno_to_ts(args[0]) if args else "any"
            return f"Set<{inner}>"
        deque_type = getattr(_t, "Deque", None)
        if origin is deque_type:
            inner = self.anno_to_ts(args[0]) if args else "any"
            return f"({inner})[]"
        defaultdict_type = getattr(_t, "DefaultDict", None)
        if origin is defaultdict_type:
            key = self.anno_to_ts(args[0]) if len(args) >= 1 else "string"
            value = self.anno_to_ts(args[1]) if len(args) >= 2 else "any"
            return f"Record<{key}, {value}>"
        counter_type = getattr(_t, "Counter", None)
        if origin is counter_type:
            key = self.anno_to_ts(args[0]) if args else "string"
            return f"Record<{key}, number>"
        awaitable_type = getattr(_t, "Awaitable", None)
        if origin is awaitable_type:
            inner = self.anno_to_ts(args[0]) if args else "any"
            return f"Promise<{inner}>"
        if origin in (tuple, Tuple):
            if len(args) == 2 and args[1] is Ellipsis:
                inner = self.anno_to_ts(args[0])
                return f"({inner})[]"
            if args:
                inner = ", ".join(self.anno_to_ts(a) for a in args)
                return f"[{inner}]"
            return "[]"
        if origin is None and isinstance(anno, type):
            return _map_primitive(getattr(anno, "__name__", "any"))
        if args and (str(origin).endswith("typing.Union") or str(origin).endswith("UnionType")):
            parts: list[str] = []
            for a in args:
                parts.append("null" if a is type(None) else self.anno_to_ts(a))  # noqa: E721
            parts = _dedupe(parts)
            return " | ".join(parts)
        if origin in (_t.Literal, getattr(_t, "Literal", None)):
            lits: list[str] = []
            for val in args:
                if isinstance(val, str):
                    lits.append(f'"{val}"')
                elif isinstance(val, bool):
                    lits.append("true" if val else "false")
                elif isinstance(val, (int, float)):
                    lits.append(str(val))
            return " | ".join(lits) if lits else "any"
        if origin in (_t.Annotated, getattr(_t, "Annotated", None)) and args:
            return self.anno_to_ts(args[0])
        if origin in (_t.Callable, _abc.Callable):
            if args:
                try:
                    param_list, ret = args
                except ValueError:
                    param_list, ret = args[:-1], args[-1]
                if param_list is Ellipsis:
                    params_ts = "...args: any[]"
                else:
                    ptypes = param_list if isinstance(param_list, (list, tuple)) else []
                    params_ts = ", ".join(
                        f"a{i+1}: {self.anno_to_ts(t)}" for i, t in enumerate(ptypes)
                    ) or ""
                ret_ts = self.anno_to_ts(ret)
                return f"({params_ts}) => {ret_ts}"
            return "(...args: any[]) => any"
        if origin in (_t.Type, type):
            inner = self.anno_to_ts(args[0]) if args else "any"
            return f"new (...args: any[]) => {inner}"
        name = getattr(anno, "__name__", None) or str(anno)
        return _map_primitive(name)


# Shared default resolver
DEFAULT_RESOLVER = TsTypeResolver()


def ts_from_ast(expr: ast.AST) -> str:
    return DEFAULT_RESOLVER.ts_from_ast(expr)


def anno_to_ts(anno: Any) -> str:
    return DEFAULT_RESOLVER.anno_to_ts(anno)


def string_anno_to_ts(text: str) -> str:
    return DEFAULT_RESOLVER.string_anno_to_ts(text)
