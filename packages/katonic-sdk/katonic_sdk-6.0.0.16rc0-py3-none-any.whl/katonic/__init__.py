#!/usr/bin/env python
#
# Copyright (c) 2023 Katonic Pty Ltd. All rights reserved.
#
from .version import get_version

# Import LLM functions for API access
try:
    from .llm.completion import generate_completion, generate_completion_with_schema
    from .llm.schemas import PredictSchema
    __all__ = ["__version__", "generate_completion", "generate_completion_with_schema", "PredictSchema"]
except ImportError:
    __all__ = ["__version__"]

__version__: str = get_version()
