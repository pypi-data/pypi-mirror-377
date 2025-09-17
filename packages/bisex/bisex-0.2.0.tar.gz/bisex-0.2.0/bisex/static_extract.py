from __future__ import annotations

"""
Static type extraction from Python source files via AST.

Converts dataclasses/typed classes, Enums, TypedDicts, and type aliases to
TypeScript declarations using a TsTypeResolver.
"""

from typing import Any
from pathlib import Path
import ast

from .typescript import TsTypeResolver, DEFAULT_RESOLVER


def _base_is_enum(base: ast.expr) -> bool:
    return (isinstance(base, ast.Name) and base.id == "Enum") or (
        isinstance(base, ast.Attribute) and base.attr == "Enum"
    )


def _base_is_typed_dict(base: ast.expr) -> bool:
    return (isinstance(base, ast.Name) and base.id == "TypedDict") or (
        isinstance(base, ast.Attribute) and base.attr == "TypedDict"
    )


def _convert_enum(node: ast.ClassDef) -> str:
    members: list[tuple[str, str]] = []
    for stmt in node.body:
        if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1:
            name = getattr(stmt.targets[0], "id", None)
            if not name:
                continue
            value = stmt.value
            lit: str | None = None
            if isinstance(value, ast.Constant) and isinstance(value.value, (str, int, float)):
                v = value.value
                if isinstance(v, str):
                    lit = f'"{v}"'
                else:
                    lit = str(v)
            elif (
                isinstance(value, ast.UnaryOp)
                and isinstance(value.op, ast.USub)
                and isinstance(value.operand, ast.Constant)
                and isinstance(value.operand.value, (int, float))
            ):
                lit = f"-{value.operand.value}"
            if lit is not None:
                members.append((name, lit))
            else:
                members.append((name, f'"{name}"'))

    body = "\n".join(f"  {k} = {v}," for k, v in members)
    return f"export enum {node.name} {{\n{body}\n}}"


def _convert_dataclass(node: ast.ClassDef, resolver: TsTypeResolver) -> str:
    fields: list[tuple[str, str]] = []
    for stmt in node.body:
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            name = stmt.target.id
            ts_t = resolver.ts_from_ast(stmt.annotation) if stmt.annotation else "any"
            fields.append((name, ts_t))
    body = "\n".join(f"  {n}: {t};" for n, t in fields)
    return f"export interface {node.name} {{\n{body}\n}}"


def _convert_typed_dict(node: ast.ClassDef, resolver: TsTypeResolver) -> str:
    fields: list[tuple[str, str]] = []
    for stmt in node.body:
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            name = stmt.target.id
            ts_t = resolver.ts_from_ast(stmt.annotation) if stmt.annotation else "any"
            fields.append((name, ts_t))
    body = "\n".join(f"  {n}: {t};" for n, t in fields)
    return f"export interface {node.name} {{\n{body}\n}}"


def _convert_typealias(node: Any, resolver: TsTypeResolver) -> str:  # ast.TypeAlias on 3.12+
    name = node.name.id  # type: ignore[attr-defined]
    rhs = resolver.ts_from_ast(node.value)  # type: ignore[attr-defined]
    return f"export type {name} = {rhs};"


def _is_type_expr_ast(expr: ast.AST) -> bool:
    match expr:
        case ast.Name():
            return True
        case ast.Attribute():
            return True
        case ast.Subscript(value=_, slice=_):
            return True
        case ast.BinOp(op=ast.BitOr(), left=l, right=r):
            return _is_type_expr_ast(l) and _is_type_expr_ast(r)
        case ast.Tuple(elts=elts):
            return all(_is_type_expr_ast(e) for e in elts)
        case ast.Constant(value=None):
            return True
        case _:
            return False


def _maybe_convert_legacy_type_alias(node: ast.AST, resolver: TsTypeResolver) -> str | None:
    # Annotated alias:  MyT: TypeAlias = int | str
    if isinstance(node, ast.AnnAssign):
        target = node.target
        anno = node.annotation
        value = node.value
        if (
            isinstance(target, ast.Name)
            and value is not None
            and (
                (isinstance(anno, ast.Name) and anno.id == "TypeAlias")
                or (isinstance(anno, ast.Attribute) and anno.attr == "TypeAlias")
            )
            and _is_type_expr_ast(value)
        ):
            name = target.id
            rhs = resolver.ts_from_ast(value)
            return f"export type {name} = {rhs};"

    # Simple assignment alias: MyT = list[int] / int | str / Optional[str]
    if isinstance(node, ast.Assign) and len(node.targets) == 1:
        target = node.targets[0]
        value = node.value
        if isinstance(target, ast.Name) and _is_type_expr_ast(value):
            name = target.id
            rhs = resolver.ts_from_ast(value)
            return f"export type {name} = {rhs};"

    return None


def python_file_to_ts(path: Path, resolver: TsTypeResolver | None = None) -> str:
    resolver = resolver or DEFAULT_RESOLVER
    if not Path(path).exists():
        return ""
    tree = ast.parse(Path(path).read_text(encoding="utf-8"))
    parts: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if any(_base_is_enum(b) for b in node.bases):
                parts.append(_convert_enum(node))
            elif any(_base_is_typed_dict(b) for b in node.bases):
                parts.append(_convert_typed_dict(node, resolver))
            else:
                parts.append(_convert_dataclass(node, resolver))
        elif hasattr(ast, "TypeAlias") and isinstance(node, ast.TypeAlias):
            parts.append(_convert_typealias(node, resolver))
        else:
            maybe = _maybe_convert_legacy_type_alias(node, resolver)
            if maybe:
                parts.append(maybe)
    return "\n\n".join(p for p in parts if p)

