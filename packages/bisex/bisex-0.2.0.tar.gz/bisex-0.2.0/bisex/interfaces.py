from __future__ import annotations

"""
Interface collection and emission.

Provides an `InterfaceCollector` that offers a decorator to capture Python
function signatures and emit them as TypeScript interfaces.
"""

import inspect
from typing import Any, get_type_hints

from .typescript import TsTypeResolver, DEFAULT_RESOLVER, anno_to_ts, string_anno_to_ts


class InterfaceCollector:
    def __init__(self, resolver: TsTypeResolver | None = None, return_wrapper: str | None = None) -> None:
        self._resolver = resolver or DEFAULT_RESOLVER
        self._wrapper = return_wrapper
        self._interfaces: dict[str, list[dict[str, Any]]] = {}

    def interface(self, name: str):
        def deco(func):
            sig = inspect.signature(func)
            try:
                hints = get_type_hints(func)
            except Exception:
                hints = getattr(func, "__annotations__", {}) or {}
            params: list[tuple[str, str]] = []
            for idx, (param_name, param) in enumerate(sig.parameters.items()):
                param_id = param_name or f"arg{idx}"
                anno = hints.get(param_name, param.annotation)
                if anno is inspect._empty:
                    params.append((param_id, "any"))
                else:
                    params.append((param_id, anno_to_ts(anno)))
            ret_anno = hints.get("return", sig.return_annotation)
            ret = None if ret_anno is inspect._empty else anno_to_ts(ret_anno)
            self._interfaces.setdefault(name, []).append(
                {"name": func.__name__, "params": params, "ret": ret}
            )
            return func

        return deco

    def emit(self) -> str:
        parts: list[str] = []
        for iface, funcs in self._interfaces.items():
            lines = []
            for f in funcs:
                params = ", ".join(
                    f"{n}: {string_anno_to_ts(t) if isinstance(t, str) else t}"
                    for n, t in f["params"]
                ) or ""
                ret = f["ret"] or "void"
                if isinstance(ret, str):
                    ret = string_anno_to_ts(ret)
                ret_ts = self._wrapper.format(ret=ret) if self._wrapper else ret
                lines.append(f"  {f['name']}: ({params}) => {ret_ts};")
            body = "\n".join(lines)
            parts.append(f"export interface {iface} {{\n{body}\n}}")
        return "\n\n".join(parts)

