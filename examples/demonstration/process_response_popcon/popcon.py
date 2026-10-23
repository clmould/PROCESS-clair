"""PROCESS POPCON / operating-space calculations.

POPCON prescribes Te and ne on a grid, lets the IN.DAT-defined equality problem
solve its free iteration variable(s), and records the resulting PROCESS state.
"""

from __future__ import annotations

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
    _isolated_process_workdir,
    _jsonable_specs,
    _metadata_signature,
    _new_single_run_quiet,
    _normalise_constraint_specs,
    _run_quiet,
    _to_float,
    _variable_value,
    _worker_count,
)

def _normalise_solved_variable_specs(
    specs: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None,
) -> list[dict[str, Any]]:
    """Normalise variables solved by PROCESS at each fixed Te-ne point."""
    result = []
    default_colours = ["black", "white", "#8c564b", "#9467bd"]
    for i, spec in enumerate(list(specs or [])):
        item = dict(spec)
        if "variable" not in item:
            raise ValueError("Each solved variable needs a PROCESS 'variable' path.")
        item.setdefault("label", item["variable"])
        item.setdefault("color", default_colours[i % len(default_colours)])
        item.setdefault("linewidth", 1.5)
        item.setdefault("linestyle", "-")
        item.setdefault("format", ".3g")
        item.setdefault("display_scale", 1.0)
        result.append(item)
    return result

def _normalise_popcon_field_specs(
    specs: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None,
) -> list[dict[str, Any]]:
    """Normalise scalar PROCESS variables recorded on a POPCON grid."""
    colours = [
        "#4c78a8", "#e45756", "#72b7b2", "#b279a2",
        "#f58518", "#54a24b", "#9d755d", "#79706e",
    ]
    result = []
    for i, spec in enumerate(specs or []):
        item = dict(spec)
        if "variable" not in item:
            raise ValueError("Each POPCON field needs a PROCESS 'variable' path.")
        item.setdefault("label", item["variable"])
        item.setdefault("color", colours[i % len(colours)])
        item.setdefault("linewidth", 1.4)
        item.setdefault("linestyle", "-")
        item.setdefault("format", ".3g")
        item.setdefault("display_scale", 1.0)
        result.append(item)
    return result

def _evaluate_popcon_field(data: Any, spec: dict[str, Any]) -> float:
    """Read one scalar PROCESS variable from a solved POPCON state."""
    return _variable_value(data, spec["variable"])

def _popcon_axis_values(
    values: Any | None,
    value_range: tuple[float, float] | None,
    points: int,
    *,
    name: str,
) -> np.ndarray:
    if values is not None:
        axis = np.asarray(values, dtype=float)
    elif value_range is not None:
        lo, hi = value_range
        axis = np.linspace(float(lo), float(hi), int(points))
    else:
        raise ValueError(f"Provide either {name}_values or {name}_range.")

    if axis.ndim != 1 or axis.size < 2 or not np.all(np.isfinite(axis)):
        raise ValueError(f"{name} grid must be a finite one-dimensional array with >=2 points.")
    return np.unique(np.sort(axis))

def _solve_popcon_point(
    *,
    input_file: str,
    te: float,
    ne: float,
    performance: dict[str, Any],
    solved_variables: list[dict[str, Any]],
    contour_fields: list[dict[str, Any]],
    equalities: list[dict[str, Any]],
    limits: list[dict[str, Any]],
    equality_tolerance: float,
    fixed_state_rtol: float,
) -> dict[str, Any]:
    """Solve the IN.DAT equality problem at one prescribed Te-ne point."""
    with _isolated_process_workdir(input_file) as worker_input:
        run = _new_single_run_quiet(worker_input)
        run.data.physics.temp_plasma_electron_vol_avg_kev = float(te)
        run.data.physics.nd_plasma_electrons_vol_avg = float(ne)
        _run_quiet(run)

    data = run.data
    actual_te = _to_float(data.physics.temp_plasma_electron_vol_avg_kev)
    actual_ne = _to_float(data.physics.nd_plasma_electrons_vol_avg)
    equality_residuals = np.asarray(
        [_constraint_residual(item["constraint"], data) for item in equalities],
        dtype=float,
    )

    state_fixed = bool(
        np.isfinite(actual_te)
        and np.isfinite(actual_ne)
        and np.isclose(actual_te, te, rtol=fixed_state_rtol, atol=0.0)
        and np.isclose(actual_ne, ne, rtol=fixed_state_rtol, atol=0.0)
    )
    equalities_ok = bool(
        np.all(np.isfinite(equality_residuals))
        and np.all(np.abs(equality_residuals) <= equality_tolerance)
    )

    return {
        "performance": _evaluate_popcon_field(data, performance),
        "solved_values": np.asarray(
            [_variable_value(data, spec["variable"]) for spec in solved_variables],
            dtype=float,
        ),
        "contour_values": np.asarray(
            [_evaluate_popcon_field(data, spec) for spec in contour_fields],
            dtype=float,
        ),
        "equality_residuals": equality_residuals,
        "limit_margins": np.asarray(
            [_constraint_margin(item["constraint"], data) for item in limits],
            dtype=float,
        ),
        "state_fixed": state_fixed,
        "converged": bool(state_fixed and equalities_ok),
    }

def _solve_popcon_reference(
    *,
    input_file: str,
    equalities: list[dict[str, Any]],
    equality_tolerance: float,
) -> dict[str, Any]:
    """Solve the unmodified POPCON input once for an optional reference marker."""
    with _isolated_process_workdir(input_file) as worker_input:
        run = _new_single_run_quiet(worker_input)
        _run_quiet(run)

    data = run.data
    residuals = np.asarray(
        [_constraint_residual(item["constraint"], data) for item in equalities],
        dtype=float,
    )
    converged = bool(
        np.all(np.isfinite(residuals))
        and np.all(np.abs(residuals) <= equality_tolerance)
    )
    return {
        "te": _to_float(data.physics.temp_plasma_electron_vol_avg_kev),
        "ne": _to_float(data.physics.nd_plasma_electrons_vol_avg),
        "converged": converged,
    }

def build_popcon(
    *,
    input_file: str,
    mode: str = "power_balance",
    performance: dict[str, Any] | None = None,
    contour_fields: list[dict[str, Any]] | None = None,
    solved_variables: list[dict[str, Any]] | None = None,
    equalities: list[dict[str, Any]] | None = None,
    limits: list[dict[str, Any]] | None = None,
    te_values: Any | None = None,
    ne_values: Any | None = None,
    te_range: tuple[float, float] | None = None,
    ne_range: tuple[float, float] | None = None,
    te_points: int = 31,
    ne_points: int = 31,
    title: str = "PROCESS POPCON",
    equality_tolerance: float = 1.0e-5,
    fixed_state_rtol: float = 1.0e-8,
    cache_dir: str | Path = "data",
    cache_name: str = "process_popcon",
    rebuild: bool = False,
    max_workers: int | None = None,
    mp_start_method: str = "spawn",
) -> dict[str, Any]:
    """Build a Te-ne POPCON from direct PROCESS solves.

    Te and ne are prescribed at every grid node. The IN.DAT supplies the
    iteration variables and equality constraints. ``mode`` only provides useful
    defaults; it does not rewrite ``ixc`` or ``icc``.

    ``power_balance`` defaults to C2 with auxiliary heating as the solved
    variable. ``full_solution`` defaults to C2+C93 with auxiliary heating and
    plasma fuelling as the solved variables. ``custom`` requires both lists.
    Cache files are written below ``cache_dir`` using ``cache_name``.
    """
    input_file = str(Path(input_file).expanduser().resolve())
    if not Path(input_file).is_file():
        raise FileNotFoundError(f"PROCESS input file not found: {input_file}")

    cache_dir = Path(cache_dir).expanduser()
    cache_dir.mkdir(parents=True, exist_ok=True)
    if not cache_name:
        raise ValueError("cache_name must not be empty.")

    mode = str(mode).strip().lower()
    valid_modes = {"power_balance", "full_solution", "custom"}
    if mode not in valid_modes:
        raise ValueError(f"mode must be one of {sorted(valid_modes)}, got {mode!r}.")

    te_axis = _popcon_axis_values(te_values, te_range, te_points, name="te")
    ne_axis = _popcon_axis_values(ne_values, ne_range, ne_points, name="ne")

    if performance is None:
        performance = {
            "variable": "physics.p_fusion_total_mw",
            "label": "Fusion power",
            "unit": "MW",
            "cmap": "viridis",
        }
    performance = _normalise_popcon_field_specs([performance])[0]
    performance.setdefault("cmap", "viridis")
    contour_fields = _normalise_popcon_field_specs(contour_fields)

    if equalities is None:
        if mode == "power_balance":
            equalities = [{"constraint": 2, "label": "C2 global power balance"}]
        elif mode == "full_solution":
            equalities = [
                {"constraint": 2, "label": "C2 global power balance"},
                {"constraint": 93, "label": "C93 fuel-ion balance"},
            ]
        else:
            raise ValueError("mode='custom' requires explicit equalities.")

    if solved_variables is None:
        if mode == "power_balance":
            solved_variables = [{
                "variable": "current_drive.p_hcd_primary_extra_heat_mw",
                "label": "Required auxiliary heating",
                "unit": "MW",
                "color": "black",
            }]
        elif mode == "full_solution":
            solved_variables = [
                {
                    "variable": "current_drive.p_hcd_primary_extra_heat_mw",
                    "label": "Required auxiliary heating",
                    "unit": "MW",
                    "color": "black",
                },
                {
                    "variable": "physics.molflow_plasma_fuelling",
                    "label": "Required plasma fuelling",
                    "unit": "particles/s",
                    "color": "#8c564b",
                },
            ]
        else:
            raise ValueError("mode='custom' requires explicit solved_variables.")

    solved_variables = _normalise_solved_variable_specs(solved_variables)
    equalities = _normalise_constraint_specs(equalities, equality=True)
    limits = _normalise_constraint_specs(limits, equality=False)

    try:
        reference = _solve_popcon_reference(
            input_file=input_file,
            equalities=equalities,
            equality_tolerance=equality_tolerance,
        )
    except Exception as exc:
        print(f"Reference PROCESS solution unavailable: {type(exc).__name__}: {exc}")
        reference = {"te": np.nan, "ne": np.nan, "converged": False}

    metadata = {
        "schema": 3,
        "input_sha256": _file_sha256(input_file),
        "mode": mode,
        "te_values": te_axis.tolist(),
        "ne_values": ne_axis.tolist(),
        "performance": _jsonable_specs([performance])[0],
        "contour_fields": _jsonable_specs(contour_fields),
        "solved_variables": _jsonable_specs(solved_variables),
        "equalities": equalities,
        "limits": limits,
        "equality_tolerance": float(equality_tolerance),
        "fixed_state_rtol": float(fixed_state_rtol),
    }
    signature = _metadata_signature(metadata)
    cache_file = cache_dir / f"{cache_name}_grid.npz"

    def make_result(payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "input_file": input_file,
            "title": title,
            "mode": mode,
            "performance": performance,
            "contour_fields": contour_fields,
            "solved_variables": solved_variables,
            "equalities": equalities,
            "limits": limits,
            "reference": reference,
            "metadata_signature": signature,
            "cache_file": str(cache_file),
            **payload,
        }

    if cache_file.exists() and not rebuild:
        with np.load(cache_file, allow_pickle=False) as cached:
            if (
                "metadata_signature" in cached.files
                and str(cached["metadata_signature"].item()) == signature
            ):
                print(f"Loading PROCESS POPCON grid from {cache_file}")
                return make_result({
                    key: cached[key]
                    for key in cached.files
                    if key != "metadata_signature"
                })

    shape = (len(ne_axis), len(te_axis))
    payload = {
        "te_values": te_axis,
        "ne_values": ne_axis,
        "performance_grid": np.full(shape, np.nan),
        "solved_value_grids": np.full(shape + (len(solved_variables),), np.nan),
        "contour_field_grids": np.full(shape + (len(contour_fields),), np.nan),
        "equality_residuals": np.full(shape + (len(equalities),), np.nan),
        "limit_margins": np.full(shape + (len(limits),), np.nan),
        "state_fixed": np.zeros(shape, dtype=bool),
        "converged": np.zeros(shape, dtype=bool),
    }

    jobs = [
        ((i, j), float(te), float(ne))
        for i, ne in enumerate(ne_axis)
        for j, te in enumerate(te_axis)
    ]
    workers = _worker_count(max_workers, len(jobs))
    equalities_text = ", ".join(f"C{item['constraint']}" for item in equalities)
    print(
        f"Building {len(te_axis)}×{len(ne_axis)} PROCESS POPCON "
        f"({len(jobs)} fixed Te-ne solves; {equalities_text}) using "
        f"{workers} worker{'s' if workers != 1 else ''} ..."
    )

    def store(index: tuple[int, int], point: dict[str, Any]) -> None:
        payload["performance_grid"][index] = point["performance"]
        payload["solved_value_grids"][index] = point["solved_values"]
        payload["contour_field_grids"][index] = point["contour_values"]
        payload["equality_residuals"][index] = point["equality_residuals"]
        payload["limit_margins"][index] = point["limit_margins"]
        payload["state_fixed"][index] = point["state_fixed"]
        payload["converged"][index] = point["converged"]

    def report(
        counter: int,
        te: float,
        ne: float,
        point: dict[str, Any] | None = None,
        exc: Exception | None = None,
    ) -> None:
        prefix = (
            f"  {counter:>4}/{len(jobs)}: Te={te:.3f} keV, "
            f"ne={ne/1e20:.3f}×10²⁰ m⁻³"
        )
        if point is None:
            detail = f" ({type(exc).__name__}: {exc})" if exc is not None else ""
            print(f"{prefix} -> FAILED{detail}")
        elif point["converged"]:
            solved = ", ".join(
                f"{spec['label']}={_format_control_value(spec, value)}"
                for spec, value in zip(solved_variables, point["solved_values"])
            )
            print(f"{prefix} -> {solved}")
        elif point["state_fixed"]:
            print(f"{prefix} -> no equality solution")
        else:
            print(f"{prefix} -> Te/ne moved; check POPCON IN.DAT")

    common = {
        "input_file": input_file,
        "performance": performance,
        "solved_variables": solved_variables,
        "contour_fields": contour_fields,
        "equalities": equalities,
        "limits": limits,
        "equality_tolerance": equality_tolerance,
        "fixed_state_rtol": fixed_state_rtol,
    }

    if workers == 1:
        for counter, (index, te, ne) in enumerate(jobs, start=1):
            try:
                point = _solve_popcon_point(te=te, ne=ne, **common)
                store(index, point)
                report(counter, te, ne, point=point)
            except Exception as exc:
                report(counter, te, ne, exc=exc)
    else:
        context = mp.get_context(mp_start_method)
        with ProcessPoolExecutor(max_workers=workers, mp_context=context) as executor:
            futures = {
                executor.submit(_solve_popcon_point, te=te, ne=ne, **common):
                (index, te, ne)
                for index, te, ne in jobs
            }
            for counter, future in enumerate(as_completed(futures), start=1):
                index, te, ne = futures[future]
                try:
                    point = future.result()
                    store(index, point)
                    report(counter, te, ne, point=point)
                except Exception as exc:
                    report(counter, te, ne, exc=exc)

    np.savez_compressed(
        cache_file,
        metadata_signature=np.asarray(signature),
        **payload,
    )
    print(f"Saved PROCESS POPCON grid to {cache_file}")

    if not np.any(payload["state_fixed"]):
        raise RuntimeError(
            "No POPCON point kept Te and ne fixed. Remove Te and ne from the "
            "POPCON IN.DAT iteration-variable list."
        )
    if not np.any(payload["converged"]):
        raise RuntimeError(
            "No fixed Te-ne point satisfied the requested equalities. Check the "
            "POPCON IN.DAT, iteration variables and grid."
        )

    return make_result(payload)

__all__ = ["build_popcon"]
