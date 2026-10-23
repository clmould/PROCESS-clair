"""Shared PROCESS execution and data-access helpers."""

from __future__ import annotations

import contextlib
import copy
import hashlib
import io
import json
import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

from process.core.caller import Caller
from process.core.solver.constraints import ConstraintManager
from process.main import SingleRun


_SEGMENT_RE = re.compile(
    r"^(?P<name>[A-Za-z_]\w*)"
    r"(?:\[(?P<python_index>\d+)\]|\((?P<process_index>\d+)\))?$"
)

def _parse_segment(segment: str) -> tuple[str, int | None]:
    """Parse one dotted-path segment.

    Supported indexed forms:

    * ``array[12]``: Python zero-based indexing.
    * ``array(13)``: PROCESS/Fortran-style one-based indexing.

    The latter makes it natural to copy a variable name from an IN.DAT file.
    """
    match = _SEGMENT_RE.fullmatch(segment)
    if match is None:
        raise ValueError(f"Invalid PROCESS variable path segment: {segment!r}")

    name = match.group("name")
    python_index = match.group("python_index")
    process_index = match.group("process_index")

    if python_index is not None:
        return name, int(python_index)
    if process_index is not None:
        return name, int(process_index) - 1
    return name, None

def get_process_variable(data: Any, path: str) -> Any:
    """Read a PROCESS variable from a dotted path.

    Examples
    --------
    ``physics.alphan``

    ``impurity_radiation.f_nd_impurity_electrons(13)``
    """
    obj = data
    for segment in path.split("."):
        name, index = _parse_segment(segment)
        obj = getattr(obj, name)
        if index is not None:
            obj = obj[index]
    return obj

def set_process_variable(data: Any, path: str, value: Any) -> None:
    """Set a PROCESS variable from a dotted path.

    Both scalar variables and indexed array elements are supported.
    """
    segments = path.split(".")
    obj = data

    for segment in segments[:-1]:
        name, index = _parse_segment(segment)
        obj = getattr(obj, name)
        if index is not None:
            obj = obj[index]

    final_name, final_index = _parse_segment(segments[-1])

    if final_index is None:
        setattr(obj, final_name, value)
    else:
        array = getattr(obj, final_name)
        array[final_index] = value

        # PROCESS impurity fractions are still read through this legacy array
        # on parts of the physics/model chain. Keep both representations in
        # sync so an impurity-seeding control genuinely changes the solve.
        if (
            final_name == "f_nd_impurity_electrons"
            and hasattr(obj, "f_nd_impurity_electron_array")
        ):
            obj.f_nd_impurity_electron_array[final_index] = value

def _to_float(value: Any, default=np.nan) -> float:
    if value is None:
        return default
    try:
        return float(value.item())
    except AttributeError:
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

def _variable_value(data: Any, path: str, default=np.nan) -> float:
    try:
        return _to_float(get_process_variable(data, path), default)
    except (AttributeError, IndexError, TypeError, ValueError):
        return default

def _constraint_residual(number: int, data: Any) -> float:
    """Return PROCESS normalised constraint residual."""
    try:
        result = ConstraintManager.evaluate_constraint(number, data)
        return _to_float(result.normalised_residual)
    except Exception:
        return np.nan

def _constraint_margin(number: int, data: Any) -> float:
    """Return a feasibility margin for a PROCESS inequality.

    ``ConstraintManager.evaluate_constraint(...).normalised_residual`` uses
    the solver residual convention in which the sign is opposite to the
    margin convention used by this response map.  Convert it here so that the
    plotting code has one unambiguous rule for every inequality:

    ``margin > 0``  satisfied
    ``margin = 0``  at the limit
    ``margin < 0``  violated

    This conversion is separate from the sign reported for inequality
    quantities in PROCESS output files.
    """
    residual = _constraint_residual(number, data)
    return -residual if np.isfinite(residual) else np.nan

def _run_quiet(run: SingleRun) -> None:
    captured = io.StringIO()
    with contextlib.redirect_stdout(captured), contextlib.redirect_stderr(captured):
        run.run()

@contextlib.contextmanager
def _quiet_process_output():
    """Suppress PROCESS stdout/stderr during notebook background work."""
    captured = io.StringIO()
    with contextlib.redirect_stdout(captured), contextlib.redirect_stderr(captured):
        yield

def _new_single_run_quiet(input_file: str) -> SingleRun:
    """Construct SingleRun without dumping the PROCESS banner/input text."""
    with _quiet_process_output():
        return SingleRun(input_file)

def _worker_count(max_workers: int | None, n_tasks: int) -> int:
    """Return a sensible worker count without oversubscribing tiny jobs."""
    if n_tasks <= 1:
        return 1
    if max_workers is None:
        return 1
    workers = int(max_workers)
    if workers < 1:
        raise ValueError("max_workers must be >= 1 or None.")
    return min(workers, n_tasks)

@contextlib.contextmanager
def _isolated_process_workdir(input_file: str):
    """Run a full PROCESS solve from a private copy of the input file.

    PROCESS derives several output filenames from the *input-file path* (for
    example ``*_OUT.DAT``, ``*_MFILE.DAT`` and ``*_IDEM_OUT.DAT``).  Merely
    changing ``cwd`` is therefore not sufficient for parallel execution if all
    workers still open the same absolute IN.DAT path: they can race on files in
    the original input directory.

    Each worker gets its own temporary directory *and its own copy of IN.DAT*.
    Passing that private path to ``SingleRun`` keeps all derived output files
    private to the worker as well.
    """
    source_input = Path(input_file).expanduser().resolve()
    if not source_input.is_file():
        raise FileNotFoundError(f"PROCESS input file not found: {source_input}")

    original_cwd = os.getcwd()
    with tempfile.TemporaryDirectory(prefix="process_response_") as tmpdir:
        workdir = Path(tmpdir)
        worker_input = workdir / source_input.name
        shutil.copy2(source_input, worker_input)
        try:
            os.chdir(workdir)
            yield str(worker_input)
        finally:
            os.chdir(original_cwd)

def _new_controlled_solved_run_isolated(
    input_file: str,
    controls: dict[str, float],
) -> SingleRun:
    """Solve PROCESS at one selected control combination in isolation.

    Use the solved state for the selected controls as the map baseline.
    """
    with _isolated_process_workdir(input_file) as resolved_input:
        run = _new_single_run_quiet(resolved_input)
        for variable, value in controls.items():
            set_process_variable(run.data, variable, float(value))
        _run_quiet(run)
    return run

def _reset_run(run: SingleRun, baseline_data: Any) -> None:
    run.data = copy.deepcopy(baseline_data)
    run.models.data = run.data
    with _quiet_process_output():
        run.models.setup_data_structure()

def _full_chain_at_fixed_state(
    run: SingleRun,
    baseline_data: Any,
    *,
    ne: float,
    te: float,
    controls: dict[str, float],
    model_passes: int,
) -> Any:
    """Evaluate the coupled PROCESS model chain at a prescribed state."""
    _reset_run(run, baseline_data)
    data = run.data

    data.physics.nd_plasma_electrons_vol_avg = float(ne)
    data.physics.temp_plasma_electron_vol_avg_kev = float(te)

    for variable, value in controls.items():
        set_process_variable(data, variable, float(value))

    caller = Caller(run.models, data)
    xc = np.asarray([], dtype=float)

    with _quiet_process_output():
        for _ in range(model_passes):
            caller._call_models_once(xc)

    return data

def _format_control_value(spec: dict[str, Any], value: float) -> str:
    scale = float(spec.get("display_scale", 1.0))
    shown = value / scale
    fmt = str(spec.get("format", ".3g"))
    try:
        text = format(shown, fmt)
    except ValueError:
        text = f"{shown:.3g}"

    unit = str(spec.get("unit", "")).strip()
    return f"{text} {unit}".rstrip()

def _normalise_constraint_specs(
    specs: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None,
    *,
    equality: bool,
) -> list[dict[str, Any]]:
    specs = list(specs or [])

    eq_colours = ["crimson", "#9c27b0", "#1f77b4", "#8c564b", "#e377c2"]
    limit_colours = ["#2ca02c", "#00a6d6", "#ff7f0e", "#9467bd", "#8c564b"]
    colours = eq_colours if equality else limit_colours

    result = []
    for i, spec in enumerate(specs):
        item = dict(spec)
        number = int(item["constraint"])
        item.setdefault("label", f"C{number}")
        item.setdefault("color", colours[i % len(colours)])
        item.setdefault("linewidth", 3.0 if equality else 2.2)
        item.setdefault("linestyle", "-" if equality else "--")
        result.append(item)
    return result

def _jsonable_specs(controls: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep only user-facing, JSON-safe control configuration."""
    result = []
    for spec in controls:
        item = {}
        for key, value in spec.items():
            if isinstance(value, np.ndarray):
                item[key] = value.tolist()
            elif isinstance(value, (np.floating, np.integer)):
                item[key] = value.item()
            else:
                item[key] = value
        result.append(item)
    return result

def _metadata_signature(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)

def _file_sha256(path: str | Path) -> str:
    """Return a content hash used to invalidate caches when an IN.DAT changes."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

__all__ = [
    "get_process_variable",
    "set_process_variable",
]