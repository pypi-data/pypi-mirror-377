"""bisex -- General-purpose Python->TypeScript generator.

Public surface:
  - TsGen: main facade to collect static types and exposed function signatures
           and emit a single .ts file.
"""

from .generator import TsGen

__all__ = ["TsGen"]
