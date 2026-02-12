"""Unified pipeline for paper-to-notebook conversion (Azure Only)."""
from __future__ import annotations

import json
from typing import Callable, Optional, Any

from .llm_client import call_llm_with_retry, parse_llm_json
from .pdf_handler import load_pdf_as_part
from .notebook_builder import build_notebook, notebook_to_bytes
from ..config import (
    DEFAULT_MODEL,
    MAX_TOKENS_ANALYSIS,
    MAX_TOKENS_DESIGN,
    MAX_TOKENS_GENERATE,
    MAX_TOKENS_VALIDATE,
)
from ..prompts import (
    ANALYSIS_PROMPT,
    DESIGN_PROMPT_TEMPLATE,
    GENERATE_PROMPT_TEMPLATE,
    SYSTEM_PROMPT,
    VALIDATE_PROMPT_TEMPLATE,
)

# Callbacks: (step_number, step_name, detail_message, extra_data)
ProgressCallback = Callable[[int, str, str, Optional[dict[str, Any]]], None]


def run_pipeline(
    pdf_source: str | bytes,
    model: str = DEFAULT_MODEL,
    on_progress: Optional[ProgressCallback] = None,
    verbose: bool = False,
) -> bytes:
    """
    Unified pipeline: PDF -> analysis -> design -> cells -> validated notebook.
    Returns the generated notebook as bytes.
    """

    def _notify(step: int, name: str, detail: str = "", extra: Optional[dict[str, Any]] = None):
        if verbose:
            print(f"\nStep {step}: {name} - {detail}")
        if on_progress:
            on_progress(step, name, detail, extra)

    # 1. Load PDF context
    _notify(0, "Initializing", "Loading Paper context...")
    paper_context = load_pdf_as_part(pdf_source)

    # 2. Paper Analysis
    _notify(1, "Analyzing Paper", "Extracting key concepts and structure...")
    analysis_raw = call_llm_with_retry(
        system_prompt=SYSTEM_PROMPT,
        user_content=[paper_context, ANALYSIS_PROMPT],
        max_tokens=MAX_TOKENS_ANALYSIS,
        model=model,
    )
    analysis = parse_llm_json(analysis_raw, "analysis")
    
    title = analysis.get("title", "Unknown Paper")
    _notify(1, "Analyzing Paper", f"Title: {title}", {"analysis": analysis})

    # 3. Design Implementation
    _notify(2, "Designing Implementation", "Planning code structure and mocks...")
    design_prompt = DESIGN_PROMPT_TEMPLATE.format(
        analysis_json=json.dumps(analysis, indent=2)
    )
    design_raw = call_llm_with_retry(
        system_prompt=SYSTEM_PROMPT,
        user_content=[paper_context, design_prompt],
        max_tokens=MAX_TOKENS_DESIGN,
        model=model,
    )
    design = parse_llm_json(design_raw, "design")
    _notify(2, "Designing Implementation", "Design complete.", {"design": design})

    # 4. Generate Cells
    _notify(3, "Generating Notebook", "Writing cells and explanations...")
    generate_prompt = GENERATE_PROMPT_TEMPLATE.format(
        analysis_json=json.dumps(analysis, indent=2),
        design_json=json.dumps(design, indent=2),
    )
    cells_raw = call_llm_with_retry(
        system_prompt=SYSTEM_PROMPT,
        user_content=[paper_context, generate_prompt],
        max_tokens=MAX_TOKENS_GENERATE,
        model=model,
    )
    cells = parse_llm_json(cells_raw, "generate")
    
    draft_nb = build_notebook(cells)
    _notify(3, "Generating Notebook", f"Generated {len(cells)} cells.", {
        "cells": (cells),
        "draft_bytes": notebook_to_bytes(draft_nb)
    })

    # 5. Validate & Repair
    _notify(4, "Validating Code", "Checking for errors and consistency...")
    validate_prompt = VALIDATE_PROMPT_TEMPLATE.format(
        cells_json=json.dumps(cells, indent=2)
    )
    validated_raw = call_llm_with_retry(
        system_prompt=SYSTEM_PROMPT,
        user_content=[validate_prompt],
        max_tokens=MAX_TOKENS_VALIDATE,
        model=model,
    )
    validated_cells = parse_llm_json(validated_raw, "validate")
    _notify(4, "Validating Code", "Validation complete.")

    # 6. Build Final Notebook
    nb = build_notebook(validated_cells)
    return notebook_to_bytes(nb)
