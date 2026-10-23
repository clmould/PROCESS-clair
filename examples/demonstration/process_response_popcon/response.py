"""Forward PROCESS Response calculations.

A Response calculation prescribes control variables and records the solved
steady-state plasma state and selected performance/constraint quantities.
"""

from __future__ import annotations

import copy
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import numpy as np

from .process_runner import (
    _constraint_margin,
    _constraint_residual,
    _file_sha256,
    _format_control_value,
    _full_chain_at_fixed_state,
    _isolated_process_workdir,
    _jsonable_specs,
    _metadata_signature,
    _new_controlled_solved_run_isolated,
    _new_single_run_quiet,
    _normalise_constraint_specs,
    _run_quiet,
    _to_float,
    _variable_value,
    _worker_count,
    set_process_variable,
)

def _include_reference_if_inside(values: np.ndarray, reference: float) -> np.ndarray:
    values = np.asarray(values, dtype=float).copy()
    if values.size == 0 or not np.isfinite(reference):
        return values

    lo = float(np.min(values))
    hi = float(np.max(values))
    if lo <= reference <= hi:
        idx = int(np.argmin(np.abs(values - reference)))
        values[idx] = reference

    return np.unique(np.sort(values))

def _control_values_from_spec(data: Any, spec: dict[str, Any]) -> np.ndarray:
    """Generate raw PROCESS values for one control specification."""
    variable = spec["variable"]
    reference = _variable_value(data, variable)

    if spec.get("values") is not None:
        values = np.asarray(spec["values"], dtype=float)
    elif spec.get("range") is not None:
        lo, hi = spec["range"]
        values = np.linspace(float(lo), float(hi), int(spec.get("n", 5)))
    elif spec.get("factor_range") is not None:
        if not np.isfinite(reference):
            raise ValueError(
                f"Cannot use factor_range for {variable!r}: reference value is not finite."
            )
        lo, hi = spec["factor_range"]
        values = reference * np.linspace(
            float(lo),
            float(hi),
            int(spec.get("n", 5)),
        )
    else:
        raise ValueError(
            f"Control {variable!r} needs one of: values, range, factor_range."
        )

    if bool(spec.get("include_reference", True)):
        values = _include_reference_if_inside(values, reference)

    return np.asarray(values, dtype=float)

def _control_label(spec: dict[str, Any]) -> str:
    return str(spec.get("short_label", spec.get("label", spec["variable"])))

def _solve_exact_point(
    *,
    input_file: str,
    control_specs: list[dict[str, Any]],
    control_values: tuple[float, ...],
    performance_variable: str,
    equalities: list[dict[str, Any]],
    limits: list[dict[str, Any]],
    equality_tolerance: float,
) -> dict[str, Any]:
    # Full PROCESS runs write output files, so isolate each solve.  This is
    # essential when several exact solutions are solved in parallel.
    with _isolated_process_workdir(input_file) as resolved_input:
        run = _new_single_run_quiet(resolved_input)
        for spec, value in zip(control_specs, control_values):
            set_process_variable(run.data, spec["variable"], float(value))
        _run_quiet(run)

    equality_residuals = np.asarray(
        [_constraint_residual(item["constraint"], run.data) for item in equalities],
        dtype=float,
    )
    limit_margins = np.asarray(
        [_constraint_margin(item["constraint"], run.data) for item in limits],
        dtype=float,
    )
    actual_controls = np.asarray(
        [_variable_value(run.data, spec["variable"]) for spec in control_specs],
        dtype=float,
    )

    te = _to_float(run.data.physics.temp_plasma_electron_vol_avg_kev)
    ne = _to_float(run.data.physics.nd_plasma_electrons_vol_avg)
    performance = _variable_value(run.data, performance_variable)

    equalities_ok = (
        True
        if equality_residuals.size == 0
        else bool(
            np.all(np.isfinite(equality_residuals))
            and np.all(np.abs(equality_residuals) <= equality_tolerance)
        )
    )

    return {
        "te": te,
        "ne": ne,
        "performance": performance,
        "equality_residuals": equality_residuals,
        "limit_margins": limit_margins,
        "actual_controls": actual_controls,
        "converged": bool(np.isfinite(te) and np.isfinite(ne) and equalities_ok),
    }

def _build_solution_database(
    *,
    input_file: str,
    control_specs: list[dict[str, Any]],
    control_axes: list[np.ndarray],
    performance_variable: str,
    equalities: list[dict[str, Any]],
    limits: list[dict[str, Any]],
    cache_file: Path,
    metadata: dict[str, Any],
    rebuild: bool,
    equality_tolerance: float,
    max_workers: int | None,
    mp_start_method: str,
) -> dict[str, np.ndarray]:
    signature = _metadata_signature(metadata)

    if cache_file.exists() and not rebuild:
        with np.load(cache_file, allow_pickle=False) as cached:
            if "metadata_signature" in cached.files:
                cached_signature = str(cached["metadata_signature"].item())
                if cached_signature == signature:
                    print(f"Loading exact PROCESS solution database from {cache_file}")
                    return {
                        key: cached[key]
                        for key in cached.files
                        if key != "metadata_signature"
                    }
            else:
                print(
                    f"Ignoring legacy response solution cache without metadata: "
                    f"{cache_file}"
                )

    shape = tuple(len(axis) for axis in control_axes)
    n_controls = len(control_specs)
    n_equalities = len(equalities)
    n_limits = len(limits)

    solutions = {
        "te": np.full(shape, np.nan),
        "ne": np.full(shape, np.nan),
        "performance": np.full(shape, np.nan),
        "converged": np.zeros(shape, dtype=bool),
        "actual_controls": np.full(shape + (n_controls,), np.nan),
        "equality_residuals": np.full(shape + (n_equalities,), np.nan),
        "limit_margins": np.full(shape + (n_limits,), np.nan),
    }

    total = int(np.prod(shape)) if shape else 1
    jobs: list[tuple[tuple[int, ...], tuple[float, ...]]] = []
    for index in np.ndindex(shape):
        raw_values = tuple(
            float(control_axes[dim][index[dim]])
            for dim in range(n_controls)
        )
        jobs.append((index, raw_values))

    workers = _worker_count(max_workers, len(jobs))
    print(
        f"Pre-solving {total} exact PROCESS solutions "
        f"across {n_controls} control variable(s) using "
        f"{workers} worker{'s' if workers != 1 else ''} ..."
    )

    def store_point(index: tuple[int, ...], point: dict[str, Any]) -> None:
        solutions["te"][index] = point["te"]
        solutions["ne"][index] = point["ne"]
        solutions["performance"][index] = point["performance"]
        solutions["converged"][index] = point["converged"]
        solutions["actual_controls"][index] = point["actual_controls"]
        solutions["equality_residuals"][index] = point["equality_residuals"]
        solutions["limit_margins"][index] = point["limit_margins"]

    def print_result(
        counter: int,
        raw_values: tuple[float, ...],
        *,
        point: dict[str, Any] | None = None,
        exc: Exception | None = None,
    ) -> None:
        values_text = ", ".join(
            f"{_control_label(spec)}={_format_control_value(spec, value)}"
            for spec, value in zip(control_specs, raw_values)
        )
        if point is not None:
            state_text = (
                f"Te={point['te']:.3f} keV, "
                f"ne={point['ne']/1e20:.3f}×10²⁰ m⁻³"
                if point["converged"]
                else "not converged"
            )

            print(f"  {counter:>3}/{total}: {values_text} -> {state_text}")
        else:
            detail = str(exc).strip() if exc is not None else ""
            suffix = f": {detail}" if detail else ""
            print(
                f"  {counter:>3}/{total}: {values_text} -> "
                f"NO SOLUTION ({type(exc).__name__}{suffix})"
            )

    if workers == 1:
        for counter, (index, raw_values) in enumerate(jobs, start=1):
            try:
                point = _solve_exact_point(
                    input_file=input_file,
                    control_specs=control_specs,
                    control_values=raw_values,
                    performance_variable=performance_variable,
                    equalities=equalities,
                    limits=limits,
                    equality_tolerance=equality_tolerance,
                )
                store_point(index, point)
                print_result(counter, raw_values, point=point)
            except Exception as exc:
                print_result(counter, raw_values, exc=exc)
    else:
        context = mp.get_context(mp_start_method)
        with ProcessPoolExecutor(
            max_workers=workers,
            mp_context=context,
        ) as executor:
            future_to_job = {
                executor.submit(
                    _solve_exact_point,
                    input_file=input_file,
                    control_specs=control_specs,
                    control_values=raw_values,
                    performance_variable=performance_variable,
                    equalities=equalities,
                    limits=limits,
                    equality_tolerance=equality_tolerance,
                ): (index, raw_values)
                for index, raw_values in jobs
            }

            for counter, future in enumerate(as_completed(future_to_job), start=1):
                index, raw_values = future_to_job[future]
                try:
                    point = future.result()
                    store_point(index, point)
                    print_result(counter, raw_values, point=point)
                except Exception as exc:
                    print_result(counter, raw_values, exc=exc)

    np.savez_compressed(
        cache_file,
        metadata_signature=np.asarray(signature),
        **solutions,
    )
    print(f"Saved exact PROCESS solution database to {cache_file}")
    return solutions

def _map_cache_file(
    cache_dir: str | Path,
    cache_name: str,
    indices: tuple[int, ...],
) -> Path:
    suffix = "_".join(str(i) for i in indices) if indices else "reference"
    return Path(cache_dir) / f"{cache_name}_map_{suffix}.npz"

def _build_map_slice(
    result: dict[str, Any],
    indices: tuple[int, ...],
    announce: bool = True,
) -> dict[str, np.ndarray]:
    control_specs = result["controls"]
    control_axes = result["control_axes"]
    equalities = result["equalities"]
    limits = result["limits"]
    input_file = result["input_file"]
    config = result["config"]

    selected_controls = {
        spec["variable"]: float(control_axes[dim][indices[dim]])
        for dim, spec in enumerate(control_specs)
    }

    exact_te = float(result["solutions"]["te"][indices])
    exact_ne = float(result["solutions"]["ne"][indices])

    te_min, te_max = result["map_bounds"]["te"]
    ne_min, ne_max = result["map_bounds"]["ne"]
    n_points = int(config["map_points"])

    base_te = np.linspace(te_min, te_max, n_points)
    base_ne = np.linspace(ne_min, ne_max, n_points)

    if np.isfinite(exact_te):
        te_values = np.unique(np.sort(np.concatenate([base_te, [exact_te]])))
    else:
        te_values = base_te

    if np.isfinite(exact_ne):
        ne_values = np.unique(np.sort(np.concatenate([base_ne, [exact_ne]])))
    else:
        ne_values = base_ne

    cache_file = _map_cache_file(
        config["cache_dir"],
        config["cache_name"],
        indices,
    )
    map_metadata = {
        "base_signature": result["metadata_signature"],
        "indices": list(indices),
        "control_values": [selected_controls[spec["variable"]] for spec in control_specs],
        "te_values": te_values.tolist(),
        "ne_values": ne_values.tolist(),
        "model_passes": int(config["model_passes"]),
        "map_kind": "selected_response_baseline_v8",
    }
    signature = _metadata_signature(map_metadata)

    if cache_file.exists() and not bool(config["rebuild_maps"]):
        with np.load(cache_file, allow_pickle=False) as cached:
            if "metadata_signature" in cached.files:
                if str(cached["metadata_signature"].item()) == signature:
                    return {
                        key: cached[key]
                        for key in cached.files
                        if key != "metadata_signature"
                    }
            else:
                print(
                    f"Ignoring legacy response map cache without metadata: "
                    f"{cache_file}"
                )

    # Start the local map from the solved state for these controls.
    run = _new_controlled_solved_run_isolated(input_file, selected_controls)
    baseline_data = copy.deepcopy(run.data)

    shape = (len(ne_values), len(te_values))
    equality_residuals = np.full(shape + (len(equalities),), np.nan)
    limit_margins = np.full(shape + (len(limits),), np.nan)

    total = int(np.prod(shape))
    if announce:
        print(
            "Building Te-ne map for "
            + ", ".join(
                f"{_control_label(spec)}="
                f"{_format_control_value(spec, selected_controls[spec['variable']])}"
                for spec in control_specs
            )
            + f" ({total} fixed-state evaluations)"
        )

    for i, ne in enumerate(ne_values):
        for j, te in enumerate(te_values):
            try:
                data = _full_chain_at_fixed_state(
                    run,
                    baseline_data,
                    ne=float(ne),
                    te=float(te),
                    controls=selected_controls,
                    model_passes=int(config["model_passes"]),
                )

                for q, item in enumerate(equalities):
                    equality_residuals[i, j, q] = _constraint_residual(
                        item["constraint"], data
                    )
                for q, item in enumerate(limits):
                    limit_margins[i, j, q] = _constraint_margin(
                        item["constraint"], data
                    )

            except Exception:
                pass

    payload = {
        "te_values": te_values,
        "ne_values": ne_values,
        "equality_residuals": equality_residuals,
        "limit_margins": limit_margins,
    }

    np.savez_compressed(
        cache_file,
        metadata_signature=np.asarray(signature),
        **payload,
    )
    return payload

def precompute_response_maps(
    result: dict[str, Any],
    *,
    max_workers: int | None = None,
    mp_start_method: str | None = None,
) -> None:
    """Build/cache every Te-ne map slice, optionally in parallel.

    Parallelism is applied at the map-slice level: one complete control
    combination per worker. Interactive on-demand maps remain serial.
    """
    shape = tuple(len(axis) for axis in result["control_axes"])
    indices = list(np.ndindex(shape))
    total_slices = len(indices)
    points = int(result["config"]["map_points"])

    if max_workers is None:
        max_workers = result["config"].get("max_workers")
    if mp_start_method is None:
        mp_start_method = str(result["config"].get("mp_start_method", "spawn"))

    workers = _worker_count(max_workers, total_slices)

    print(
        f"Precomputing {total_slices} response-map slices using "
        f"{workers} worker{'s' if workers != 1 else ''}. "
        f"Each is roughly {points}×{points} fixed-state evaluations."
    )

    if workers == 1:
        for counter, index in enumerate(indices, start=1):
            print(f"\nMap {counter}/{total_slices}: indices={index}")
            _build_map_slice(result, index, announce=True)
    else:
        context = mp.get_context(mp_start_method)
        with ProcessPoolExecutor(
            max_workers=workers,
            mp_context=context,
        ) as executor:
            future_to_index = {
                executor.submit(_build_map_slice, result, index, False): index
                for index in indices
            }

            for counter, future in enumerate(as_completed(future_to_index), start=1):
                index = future_to_index[future]
                try:
                    future.result()
                    print(
                        f"  {counter:>3}/{total_slices}: "
                        f"cached map indices={index}"
                    )
                except Exception as exc:
                    print(
                        f"  {counter:>3}/{total_slices}: "
                        f"FAILED indices={index} ({type(exc).__name__}: {exc})"
                    )

    # After an explicit rebuild/precompute, the interactive viewer should use
    # the newly written cache files rather than rebuilding them on each draw.
    result["config"]["rebuild_maps"] = False

def build_response(
    *,
    input_file: str,
    controls: list[dict[str, Any]],
    performance: dict[str, Any],
    equalities: list[dict[str, Any]] | None = None,
    limits: list[dict[str, Any]] | None = None,
    title: str = "PROCESS Response",
    map_points: int = 21,
    map_padding_fraction: float = 0.20,
    te_padding_min_kev: float = 1.5,
    ne_padding_min: float = 0.08e20,
    model_passes: int = 2,
    equality_tolerance: float = 1.0e-5,
    cache_dir: str | Path = "data",
    cache_name: str = "process_response",
    rebuild_solutions: bool = False,
    rebuild_maps: bool = False,
    precompute_maps: bool = False,
    max_workers: int | None = None,
    mp_start_method: str = "spawn",
) -> dict[str, Any]:
    """Build a generic multi-control PROCESS solution database.

    ``controls`` can contain any number of scalar PROCESS variables.  Each
    control uses a dotted PROCESS variable path and one of ``values``, ``range``
    or ``factor_range``.

    PROCESS is solved for the Cartesian product of the control values. Te-ne
    residual maps are cached per control combination and built lazily. Cache
    files are written below ``cache_dir`` using ``cache_name`` as the prefix.
    """
    if not controls:
        raise ValueError("At least one control variable is required.")
    if "variable" not in performance:
        raise ValueError("performance must contain a PROCESS 'variable' path.")

    # Resolve before spawning workers; each worker runs from a private directory.
    input_file = str(Path(input_file).expanduser().resolve())
    if not Path(input_file).is_file():
        raise FileNotFoundError(f"PROCESS input file not found: {input_file}")

    cache_dir = Path(cache_dir).expanduser()
    cache_dir.mkdir(parents=True, exist_ok=True)
    if not cache_name:
        raise ValueError("cache_name must not be empty.")

    controls = [dict(spec) for spec in controls]
    equalities = _normalise_constraint_specs(equalities, equality=True)
    limits = _normalise_constraint_specs(limits, equality=False)
    performance = dict(performance)
    performance.setdefault("label", performance["variable"])
    performance.setdefault("cmap", "viridis")

    reference_run = _new_single_run_quiet(input_file)
    _run_quiet(reference_run)
    reference_data = reference_run.data

    control_axes = [
        _control_values_from_spec(reference_data, spec)
        for spec in controls
    ]
    reference_control_values = np.asarray(
        [_variable_value(reference_data, spec["variable"]) for spec in controls],
        dtype=float,
    )
    reference_indices = tuple(
        int(np.argmin(np.abs(axis - ref)))
        for axis, ref in zip(control_axes, reference_control_values)
    )

    metadata = {
        "solution_cache_schema": 6,
        "input_file": str(input_file),
        "input_sha256": _file_sha256(input_file),
        "controls": _jsonable_specs(controls),
        "control_axes": [axis.tolist() for axis in control_axes],
        "performance": performance,
        "equalities": equalities,
        "limits": limits,
        "equality_tolerance": float(equality_tolerance),
    }
    metadata_signature = _metadata_signature(metadata)

    solution_cache = cache_dir / f"{cache_name}_solutions.npz"
    solutions = _build_solution_database(
        input_file=input_file,
        control_specs=controls,
        control_axes=control_axes,
        performance_variable=performance["variable"],
        equalities=equalities,
        limits=limits,
        cache_file=solution_cache,
        metadata=metadata,
        rebuild=rebuild_solutions,
        equality_tolerance=equality_tolerance,
        max_workers=max_workers,
        mp_start_method=mp_start_method,
    )

    good = (
        solutions["converged"].astype(bool)
        & np.isfinite(solutions["te"])
        & np.isfinite(solutions["ne"])
    )
    if not np.any(good):
        raise RuntimeError("No PROCESS solutions converged.")

    te_good = solutions["te"][good]
    ne_good = solutions["ne"][good]

    te_span = float(np.nanmax(te_good) - np.nanmin(te_good))
    ne_span = float(np.nanmax(ne_good) - np.nanmin(ne_good))
    te_pad = max(float(te_padding_min_kev), float(map_padding_fraction) * te_span)
    ne_pad = max(float(ne_padding_min), float(map_padding_fraction) * ne_span)

    reference = {
        "te": _to_float(reference_data.physics.temp_plasma_electron_vol_avg_kev),
        "ne": _to_float(reference_data.physics.nd_plasma_electrons_vol_avg),
        "performance": _variable_value(reference_data, performance["variable"]),
        "controls": reference_control_values,
    }

    result = {
        "input_file": str(input_file),
        "controls": controls,
        "control_axes": control_axes,
        "performance": performance,
        "equalities": equalities,
        "limits": limits,
        "title": title,
        "solutions": solutions,
        "reference": reference,
        "reference_indices": reference_indices,
        "metadata_signature": metadata_signature,
        "map_bounds": {
            "te": (
                float(np.nanmin(te_good) - te_pad),
                float(np.nanmax(te_good) + te_pad),
            ),
            "ne": (
                float(np.nanmin(ne_good) - ne_pad),
                float(np.nanmax(ne_good) + ne_pad),
            ),
        },
        "config": {
            "map_points": int(map_points),
            "model_passes": int(model_passes),
            "cache_dir": str(cache_dir),
            "cache_name": str(cache_name),
            "rebuild_maps": bool(rebuild_maps),
            "max_workers": max_workers,
            "mp_start_method": str(mp_start_method),
        },
    }

    if precompute_maps:
        precompute_response_maps(
            result,
            max_workers=max_workers,
            mp_start_method=mp_start_method,
        )

    return result

__all__ = [
    "build_response",
    "precompute_response_maps",
]
