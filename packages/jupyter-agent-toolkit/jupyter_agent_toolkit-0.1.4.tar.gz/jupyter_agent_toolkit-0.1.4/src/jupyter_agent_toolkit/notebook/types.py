"""
Canonical dataclasses and types for the notebook subsystem.
"""


from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class NotebookCodeExecutionResult:
    """
    Result of executing code in a notebook session (includes cell information).
    
    This extends ExecutionResult with notebook-specific information like
    cell index and enhanced output processing for AI agents.
    """
    status: str = "ok"
    execution_count: Optional[int] = None
    cell_index: int = -1
    stdout: str = ""
    stderr: str = ""
    outputs: List[Dict[str, Any]] = field(default_factory=list)
    
    # Enhanced fields for AI agents
    text_outputs: List[str] = field(default_factory=list)
    formatted_output: str = ""
    error_message: Optional[str] = None
    elapsed_seconds: Optional[float] = None


@dataclass
class NotebookMarkdownCellResult:
    """
    Result of inserting a markdown cell in a notebook session.
    Structured for robust agent workflows and error handling.
    """
    status: str = "ok"  # "ok" or "error"
    cell_index: Optional[int] = None  # Index of the inserted cell, or None on error
    error_message: Optional[str] = None  # Error message if insertion failed
    elapsed_seconds: Optional[float] = None  # Time taken for insertion