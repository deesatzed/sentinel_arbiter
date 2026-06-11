# OpenRouter Model Comparison Implementation Plan

> **For Codex:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build and run a CLI-first OpenRouter model comparison harness for one limited, challenging constructed Sentinel example.

**Architecture:** Keep deterministic Sentinel as the authority. OpenRouter models produce schema-validated node proposals and summaries that are compared against deterministic node values, saved as artifacts, and never used as final graph judgment.

**Tech Stack:** Python stdlib HTTP client, Pydantic 2 models, existing Sentinel `DecisionEpisode`, `NodeAudit`, safety scanner, pytest.

---

### Task 1: Add Model Comparison Tests

**Files:**
- Create: `tests/test_openrouter_compare.py`
- Create: `src/sentinel_workbench/openrouter_compare.py`
- Modify: `pyproject.toml`

**Steps:**

1. Write failing tests for `.env` model loading, prompt construction, JSON extraction, schema validation, comparison summaries, and CLI script registration.
2. Run `python3 -m pytest tests/test_openrouter_compare.py -q` and confirm failure because the module does not exist.

### Task 2: Implement Harness

**Files:**
- Create: `src/sentinel_workbench/openrouter_compare.py`
- Modify: `pyproject.toml`

**Steps:**

1. Add Pydantic models for model node assessments, model results, and comparison reports.
2. Add `.env` parser that reads `OPENROUTER_API_KEY` and `MODEL_1..MODEL_N` without printing secrets.
3. Add prompt builder that uses redacted input, approved episode JSON, deterministic node audit context, and allowed node IDs.
4. Add OpenRouter chat call with `response_format={"type":"json_object"}` and timeout handling.
5. Add validation that rejects forbidden language, invalid node IDs, and out-of-range values.
6. Add comparison report writer with JSON and Markdown outputs.

### Task 3: Add Challenging Constructed Example

**Files:**
- Create: `data/model_comparison/challenging_constructed_case.txt`

**Steps:**

1. Add a short synthetic case with uncertain response after therapy, weak AI-derived claim, unclear home support, unclear return access, and pending low-burden information.
2. Keep it constructed and non-PHI.

### Task 4: Run And Report

**Commands:**

1. `python3 -m pytest tests/test_openrouter_compare.py -q`
2. `python3 -m pytest -q`
3. `PYTHONPATH=src python3 -m sentinel_workbench.openrouter_compare --input data/model_comparison/challenging_constructed_case.txt --out artifacts/model_comparison/challenging_case --review-question disposition_information_sufficiency`
4. Inspect `artifacts/model_comparison/challenging_case/comparison_report.md`.

**Acceptance Criteria:**

- No raw `.env` values are printed or committed.
- Each configured model is recorded as success, schema-invalid, safety-invalid, or request-failed.
- The report identifies which models are sufficient candidates and which may require stronger paid models.
