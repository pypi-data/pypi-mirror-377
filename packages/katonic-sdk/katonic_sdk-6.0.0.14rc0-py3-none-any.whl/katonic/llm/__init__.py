#!/usr/bin/env python
#
# Copyright (c) 2024 Katonic Pty Ltd. All rights reserved.
#

# Import LLM functions for API access
try:
    from .completion import generate_completion, generate_completion_with_schema
    from .schemas import PredictSchema
    from .platform_logger import (
        log_to_katonic_platform,
        log_to_katonic_platform_sync
    )
    __all__ = [
        "generate_completion", 
        "generate_completion_with_schema", 
        "PredictSchema",
        "log_to_katonic_platform",
        "log_to_katonic_platform_sync"
    ]
except ImportError as e:
    import warnings
    warnings.warn(
        f"Failed to import LLM modules: {e}. "
        "Please install with 'pip install katonic[llm_deps]' to use LLM functionality.",
        UserWarning
    )
    __all__ = []