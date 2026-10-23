"""Plotting and notebook widgets for PROCESS Response and POPCON results."""

from __future__ import annotations

from typing import Any

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import numpy as np
from scipy.interpolate import RegularGridInterpolator
from IPython.display import display

from .process_runner import _format_control_value, _to_float
from .response import _build_map_slice, _control_label

try:
    import ipywidgets as widgets
except ImportError:
    widgets = None

def _contour_if_spanned(ax, x, y, z, level, **kwargs):
    finite = z[np.isfinite(z)]
    if finite.size and finite.min() <= level <= finite.max():
        return ax.contour(x, y, z, levels=[level], **kwargs)
    return None

def _shade_violated_region(
    ax,
    x,
    y,
    margin,
    *,
    color: str,
    alpha: float = 0.045,
    hatch: str = "xx",
):
    """Lightly shade where a PROCESS inequality is violated.

    PROCESS inequality residuals are positive when satisfied, zero at the
    allowable limit and negative when violated.  The fill therefore covers
    ``margin < 0``.  A sparse hatch is overlaid as a redundant, colour-blind
    accessible cue.  If the entire displayed map is violated, the whole valid
    region is shaded even though no zero-margin contour is present.
    """
    finite = margin[np.isfinite(margin)]
    if finite.size == 0 or not np.any(finite < 0.0):
        return None

    low = float(np.nanmin(finite))
    # contourf requires strictly increasing levels.  Extend slightly below the
    # minimum so an all-negative field still fills the complete valid region.
    span = max(abs(low), 1.0)
    lower = low - 1.0e-9 * span
    masked = np.ma.masked_invalid(margin)

    fill = ax.contourf(
        x,
        y,
        masked,
        levels=[lower, 0.0],
        colors=[color],
        alpha=alpha,
        antialiased=True,
        zorder=0.25,
    )

    # Keep the hatch deliberately neutral and fine: colour identifies the
    # individual limit contour, while the x-pattern always means "violated".
    if hatch:
        with mpl.rc_context({"hatch.color": "0.35", "hatch.linewidth": 0.25}):
            ax.contourf(
                x,
                y,
                masked,
                levels=[lower, 0.0],
                colors="none",
                hatches=[hatch],
                antialiased=True,
                zorder=0.30,
            )

    return fill

def _limit_mark(value: float) -> str:
    if not np.isfinite(value):
        return "n/a"
    return "✓" if value >= 0.0 else "✗"

def _solution_slice_for_display(
    result: dict[str, Any],
    indices: tuple[int, ...],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return the pre-solved Response points on the selected control slice."""
    solutions = result["solutions"]
    n_controls = len(result["controls"])

    if n_controls == 1:
        slicer = slice(None)
    else:
        slicer = tuple(
            [slice(None), slice(None)]
            + [indices[k] for k in range(2, n_controls)]
        )

    return (
        np.asarray(solutions["te"][slicer], dtype=float).reshape(-1),
        np.asarray(solutions["ne"][slicer], dtype=float).reshape(-1),
        np.asarray(solutions["performance"][slicer], dtype=float).reshape(-1),
        np.asarray(solutions["converged"][slicer], dtype=bool).reshape(-1),
    )

def _dense_feasibility(
    te: np.ndarray,
    ne20: np.ndarray,
    margins: np.ndarray,
    converged: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Interpolate limit margins for smooth aggregate feasibility hatching."""
    nx = max(201, 20 * max(len(te) - 1, 1) + 1)
    ny = max(201, 20 * max(len(ne20) - 1, 1) + 1)
    te_dense = np.linspace(te.min(), te.max(), nx)
    ne_dense = np.linspace(ne20.min(), ne20.max(), ny)
    te_grid, ne_grid = np.meshgrid(te_dense, ne_dense)
    query = np.column_stack([ne_grid.ravel(), te_grid.ravel()])

    fields = []
    for q in range(margins.shape[2]):
        field = np.where(converged, margins[:, :, q], np.nan)
        interpolator = RegularGridInterpolator(
            (ne20, te),
            field,
            bounds_error=False,
            fill_value=np.nan,
        )
        fields.append(interpolator(query).reshape(ne_grid.shape))

    dense = np.stack(fields, axis=2)
    finite = np.all(np.isfinite(dense), axis=2)
    feasible = finite & np.all(dense >= 0.0, axis=2)
    violated = finite & np.any(dense < 0.0, axis=2)
    return te_grid, ne_grid, feasible, violated

def show_response(
    result: dict[str, Any],
    *,
    show_solution_cloud: bool = True,
    show_reference: bool = False,
    reference_label: str = "Reference PROCESS solution",
    shade_violations: bool = True,
    hatch_violations: bool = True,
) -> None:
    """Show an interactive PROCESS Response view.

    The Te-ne plane is used to visualise the two governing consistency
    equations.  Their contours are computed from the cached fixed-state map for
    the currently selected controls.  Exact pre-solved PROCESS solutions are
    overlaid as coloured markers rather than as a filled background, so only
    genuine equality-satisfying solutions are shown as performance data.
    """
    controls = result["controls"]
    control_axes = result["control_axes"]
    performance_spec = result["performance"]
    equalities = result["equalities"]
    limits = result["limits"]
    solutions = result["solutions"]

    def selected_indices(selected: dict[str, float]) -> tuple[int, ...]:
        return tuple(
            int(np.argmin(np.abs(axis - selected[f"control_{i}"])))
            for i, axis in enumerate(control_axes)
        )

    def draw(show_limits=True, **selected):
        indices = selected_indices(selected)
        map_data = _build_map_slice(result, indices)

        te_values = map_data["te_values"]
        ne_values = map_data["ne_values"]
        te_grid, ne_grid = np.meshgrid(te_values, ne_values / 1.0e20)
        # Each plotted field carries its own finite-value mask.  Do not use a
        # shared map-validity mask here: an unrelated consistency equation can
        # be non-finite at a forced Te-ne state while another equality or limit
        # is still perfectly evaluable.

        # Fixed presentation layout.  Do not use constrained_layout here:
        # long legend/footer text in the information panel can otherwise force
        # Matplotlib to shrink the Te-ne axes into a tall, narrow shape.
        fig = plt.figure(figsize=(13.6, 5.6))
        gs = fig.add_gridspec(
            1,
            2,
            width_ratios=(1.25, 0.62),
            wspace=0.30,
        )
        fig.subplots_adjust(left=0.07, right=0.985, bottom=0.13, top=0.92)

        ax = fig.add_subplot(gs[0, 0])
        ax.set_box_aspect(1)  # keep the Te-ne plotting panel square

        # Anchor the colourbar directly to the plotting axes.  A separate
        # GridSpec column leaves a large gap once set_box_aspect(1) shrinks the
        # axes inside its slot; an inset axis stays tight to the visible square.
        cax = inset_axes(
            ax,
            width="4.5%",
            height="100%",
            loc="lower left",
            bbox_to_anchor=(1.035, 0.0, 1.0, 1.0),
            bbox_transform=ax.transAxes,
            borderpad=0,
        )

        info_ax = fig.add_subplot(gs[0, 1])
        info_ax.axis("off")

        # ------------------------------------------------------------------
        # Exact pre-solved PROCESS solutions on the currently selected slice.
        # First two controls span the displayed family; any remaining controls
        # define the slice.
        # ------------------------------------------------------------------
        cloud_te, cloud_ne, cloud_perf, cloud_conv = _solution_slice_for_display(result, indices)
        exact_mask = (
            cloud_conv
            & np.isfinite(cloud_te)
            & np.isfinite(cloud_ne)
            & np.isfinite(cloud_perf)
        )

        finite_perf = cloud_perf[exact_mask]
        perf_lo = perf_hi = np.nan
        if finite_perf.size:
            perf_lo = float(np.nanmin(finite_perf))
            perf_hi = float(np.nanmax(finite_perf))
            if np.isclose(perf_hi, perf_lo):
                perf_hi = perf_lo + 1.0

            norm = plt.Normalize(vmin=perf_lo, vmax=perf_hi)
            cmap = plt.get_cmap(performance_spec.get("cmap", "viridis"))

            if show_solution_cloud:
                ax.scatter(
                    cloud_te[exact_mask],
                    cloud_ne[exact_mask] / 1.0e20,
                    c=cloud_perf[exact_mask],
                    cmap=cmap,
                    norm=norm,
                    s=115,
                    alpha=0.92,
                    edgecolors="white",
                    linewidths=0.9,
                    zorder=4,
                )

            mappable = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
            mappable.set_array([])
            cbar = fig.colorbar(mappable, cax=cax)
            cbar.set_label(performance_spec["label"])
        else:
            cax.axis("off")

        # All plotted markers are exact equality-satisfying PROCESS solutions.
        # Inequality constraints are separate feasibility checks.  Dashed limit
        # contours show where a selected physics or engineering quantity reaches
        # its allowable bound; the selected-solution status is reported separately.
        legend_items = []

        # ------------------------------------------------------------------
        # Consistency-equation and limit contours for the currently selected
        # controls.  These are explanatory contours, not solution curves.  A
        # dashed limit contour is the zero-margin locus: calculated value = bound.
        # ------------------------------------------------------------------
        for q, spec in enumerate(equalities):
            # Plot this equality wherever *its own* residual is finite.
            # Requiring all equalities to be finite would unnecessarily clip
            # an otherwise valid contour.
            field = np.asarray(map_data["equality_residuals"][:, :, q], dtype=float)
            _contour_if_spanned(
                ax, te_grid, ne_grid, field, 0.0,
                colors=spec["color"], linewidths=spec["linewidth"], linestyles=spec["linestyle"],
            )
            legend_items.append(
                Line2D([0], [0], color=spec["color"], linewidth=spec["linewidth"],
                       linestyle=spec["linestyle"], label=spec["label"])
            )

        any_violated_region = False
        if show_limits:
            for q, spec in enumerate(limits):
                # Limit contours use the finite values of this constraint only.
                # A failure/NaN in C2, C93, or another inequality must not mask
                # a limit that PROCESS can still evaluate at the same forced
                # Te-ne state.
                field = np.asarray(map_data["limit_margins"][:, :, q], dtype=float)

                finite_field = field[np.isfinite(field)]
                has_violation = bool(
                    finite_field.size and np.any(finite_field < 0.0)
                )
                if shade_violations and has_violation:
                    _shade_violated_region(
                        ax,
                        te_grid,
                        ne_grid,
                        field,
                        color=spec["color"],
                        hatch="xx" if hatch_violations else "",
                    )
                    any_violated_region = True

                _contour_if_spanned(
                    ax, te_grid, ne_grid, field, 0.0,
                    colors=spec["color"],
                    linewidths=spec["linewidth"],
                    linestyles=spec["linestyle"],
                )
                legend_items.append(
                    Line2D([0], [0], color=spec["color"], linewidth=spec["linewidth"],
                           linestyle=spec["linestyle"], label=spec["label"])
                )

            if any_violated_region and shade_violations:
                legend_items.append(
                    Patch(
                        facecolor="0.5",
                        edgecolor="0.35",
                        alpha=0.12,
                        hatch="xx" if hatch_violations else None,
                        label="Violated region",
                    )
                )

        # Optional reference / optimised PROCESS solution.
        if show_reference:
            ax.plot(
                result["reference"]["te"], result["reference"]["ne"] / 1.0e20,
                marker='o', markersize=10, markerfacecolor='white', markeredgecolor='black',
                markeredgewidth=1.5, linestyle='none', zorder=11,
            )
            legend_items.append(
                Line2D(
                    [0], [0], marker="o", markersize=8,
                    markerfacecolor="white", markeredgecolor="black",
                    markeredgewidth=1.4, linestyle="none", label=reference_label,
                )
            )

        # Selected exact solution on top, coloured by its performance.
        exact_te = float(solutions["te"][indices])
        exact_ne = float(solutions["ne"][indices])
        converged = bool(solutions["converged"][indices])
        selected_perf = float(solutions["performance"][indices])

        selected_face = 'black'
        if np.isfinite(selected_perf) and np.isfinite(perf_lo):
            norm = plt.Normalize(vmin=perf_lo, vmax=perf_hi)
            cmap = plt.get_cmap(performance_spec.get("cmap", "viridis"))
            selected_face = cmap(norm(selected_perf))

        if converged and np.isfinite(exact_te) and np.isfinite(exact_ne):
            ax.scatter(
                [exact_te], [exact_ne / 1.0e20],
                s=260,
                marker="o",
                facecolors=[selected_face],
                edgecolors="black",
                linewidths=2.0,
                zorder=12,
            )
            ax.scatter(
                [exact_te], [exact_ne / 1.0e20],
                s=42, marker='o', facecolors='white', edgecolors='white', linewidths=0.0, zorder=13,
            )
            legend_items.append(
                Line2D([0], [0], marker='o', markersize=11, markerfacecolor='gray',
                       markeredgecolor='black', linestyle='none', label='Selected PROCESS solution')
            )

        if show_solution_cloud:
            legend_items.append(
                Line2D(
                    [0], [0],
                    marker="o",
                    markersize=9,
                    markerfacecolor="gray",
                    markeredgecolor="white",
                    linestyle="none",
                    label="PROCESS solutions (C2 = 0, C93 = 0)",
                )
            )

        ax.set_xlabel(r"Volume-averaged electron temperature, $T_e$ [keV]")
        ax.set_ylabel(r"Volume-averaged electron density, $n_e$ [$10^{20}$ m$^{-3}$]")
        ax.set_title(result["title"])
        ax.grid(alpha=0.15)

        info_ax.legend(
            handles=legend_items,
            loc='upper left', bbox_to_anchor=(0.0, 1.0), frameon=False,
            fontsize=8.7, borderaxespad=0.0, handlelength=2.4, labelspacing=0.45,
        )

        control_lines = []
        for dim, spec in enumerate(controls):
            requested = float(control_axes[dim][indices[dim]])
            actual = float(solutions["actual_controls"][indices + (dim,)])
            label = _control_label(spec)
            if np.isfinite(actual) and not np.isclose(actual, requested, rtol=1e-8, atol=0.0):
                control_lines.append(
                    f"{label:<12}= {_format_control_value(spec, actual)} "
                    f"(asked {_format_control_value(spec, requested)})"
                )
            else:
                control_lines.append(f"{label:<12}= {_format_control_value(spec, requested)}")

        if converged:
            diagnostic_lines = [
                'Selected PROCESS solution', '', *control_lines, '',
                f'Te          = {exact_te:.3f} keV',
                f'ne          = {exact_ne/1e20:.3f} ×10²⁰ m⁻³',
                f'{performance_spec["label"]:<12}= {selected_perf:.4g}',
            ]
            if equalities:
                eq_values = solutions["equality_residuals"][indices]
                diagnostic_lines.append('')
                diagnostic_lines.extend(
                    f"C{spec['constraint']} resid = {eq_values[q]:.2e}"
                    for q, spec in enumerate(equalities)
                )
            if limits:
                margin_values = solutions["limit_margins"][indices]
                diagnostic_lines.append('')
                diagnostic_lines.append('Inequality margins (+ feasible, 0 active):')
                diagnostic_lines.extend(
                    f"C{spec['constraint']:<3} margin = {margin_values[q]: .2e} "
                    f"{_limit_mark(margin_values[q])}"
                    for q, spec in enumerate(limits)
                )
            diagnostic = "\n".join(diagnostic_lines)
        else:
            diagnostic = "No converged PROCESS solution\n\n" + "\n".join(control_lines)

        info_ax.text(
            0.0, 0.52, diagnostic,
            va='top', ha='left', fontsize=8.8, family='monospace', linespacing=1.18,
        )

        plt.show()

    widget_map = {}
    control_rows = []

    for i, (spec, axis) in enumerate(zip(controls, control_axes)):
        default_index = result["reference_indices"][i]
        default_value = float(axis[default_index])
        widget = widgets.SelectionSlider(
            options=[(_format_control_value(spec, float(value)), float(value)) for value in axis],
            value=default_value,
            description="",
            continuous_update=True,
            layout=widgets.Layout(width="335px", flex="0 0 335px"),
        ) if widgets is not None else None

        if widget is not None:
            # Keep the label outside SelectionSlider.  ipywidgets can render the
            # built-in description with slightly different intrinsic widths,
            # which makes the first slider look offset when several controls are
            # stacked.  A fixed label column guarantees aligned slider tracks.
            label_widget = widgets.HTML(
                value=(
                    "<div style='width:100%; text-align:right; padding-right:10px; "
                    "box-sizing:border-box'>" + _control_label(spec) + "</div>"
                ),
                layout=widgets.Layout(width="155px", flex="0 0 155px"),
            )
            row = widgets.HBox(
                [label_widget, widget],
                layout=widgets.Layout(width="500px", align_items="center"),
            )
            widget_map[f"control_{i}"] = widget
            control_rows.append(row)

    limits_widget = None
    if limits and widgets is not None:
        limits_widget = widgets.Checkbox(
            value=True,
            description='Show limit contours',
            indent=False,
        )
        widget_map['show_limits'] = limits_widget

    if widgets is None:
        selected = {
            f"control_{i}": float(axis[result["reference_indices"][i]])
            for i, axis in enumerate(control_axes)
        }
        draw(show_limits=True, **selected)
        return

    output = widgets.interactive_output(draw, widget_map)

    total_solutions = int(np.prod([len(axis) for axis in control_axes]))
    cloud_text = (
        " Coloured markers show the pre-solved PROCESS solution cloud."
        if show_solution_cloud
        else ""
    )
    header = widgets.HTML(
        "<b>PROCESS Response</b><br>"
        f"<span style='font-size:12px;color:#666'>"
        f"{len(controls)} control variable(s), {total_solutions} exact pre-solved "
        f"PROCESS solutions.{cloud_text} "
        "Solid curves show the governing equations. "
        "Dashed contours mark selected physics or engineering limits; "
        "shaded / hatched areas violate them."
        "</span>"
    )

    ui = [header, *control_rows]
    if limits_widget is not None:
        ui.append(limits_widget)

    display(widgets.VBox(ui), output)

def show_popcon(
    result: dict[str, Any],
    *,
    performance_levels: int | list[float] = 18,
    show_filled: bool = True,
    show_solved_contours: bool = True,
    show_contour_fields: bool = True,
    show_limits: bool = True,
    shade_violations: bool = True,
    hatch_violations: bool = True,
    hatch_invalid: bool = True,
    show_reference: bool = False,
    reference_label: str = "Reference PROCESS solution",
) -> None:
    """Plot solved POPCON fields and feasibility boundaries in Te-ne space."""
    te = np.asarray(result["te_values"], dtype=float)
    ne = np.asarray(result["ne_values"], dtype=float)
    ne20 = ne / 1.0e20
    te_grid, ne_grid = np.meshgrid(te, ne20)
    converged = np.asarray(result["converged"], dtype=bool)

    performance = result["performance"]
    performance_raw = np.asarray(result["performance_grid"], dtype=float)
    performance_values = performance_raw / float(performance.get("display_scale", 1.0))
    performance_masked = np.ma.masked_where(
        ~converged | ~np.isfinite(performance_values),
        performance_values,
    )

    fig = plt.figure(figsize=(14.4, 6.2))
    grid = fig.add_gridspec(1, 2, width_ratios=(1.15, 0.78), wspace=0.27)
    fig.subplots_adjust(left=0.065, right=0.985, bottom=0.13, top=0.92)

    ax = fig.add_subplot(grid[0, 0])
    ax.set_box_aspect(1)
    info_ax = fig.add_subplot(grid[0, 1])
    info_ax.axis("off")

    cax = inset_axes(
        ax,
        width="4.5%",
        height="100%",
        loc="lower left",
        bbox_to_anchor=(1.035, 0.0, 1.0, 1.0),
        bbox_transform=ax.transAxes,
        borderpad=0,
    )

    if show_filled and np.any(~performance_masked.mask):
        filled = ax.contourf(
            te_grid,
            ne_grid,
            performance_masked,
            levels=performance_levels,
            cmap=performance.get("cmap", "viridis"),
            extend="both",
        )
        cbar = fig.colorbar(filled, cax=cax)
        unit = str(performance.get("unit", "")).strip()
        label = str(performance.get("label", performance["variable"]))
        cbar.set_label(label + (f" [{unit}]" if unit else ""))
    else:
        cax.axis("off")

    legend_items: list[Any] = []

    def draw_family(field: np.ndarray, spec: dict[str, Any], default_levels=7) -> None:
        scale = float(spec.get("display_scale", 1.0))
        values = np.ma.masked_where(
            ~converged | ~np.isfinite(field),
            field / scale,
        )
        finite = values.compressed()
        if finite.size < 2 or np.isclose(finite.min(), finite.max()):
            return

        contour = ax.contour(
            te_grid,
            ne_grid,
            values,
            levels=spec.get("levels", default_levels),
            colors=spec.get("color", "black"),
            linewidths=float(spec.get("linewidth", 1.4)),
            linestyles=spec.get("linestyle", "-"),
            zorder=float(spec.get("zorder", 4.0)),
        )
        fmt = str(spec.get("format", ".3g"))
        try:
            ax.clabel(
                contour,
                inline=True,
                fontsize=float(spec.get("label_fontsize", 8)),
                fmt=lambda value, f=fmt: format(value, f),
            )
        except (TypeError, ValueError):
            ax.clabel(contour, inline=True, fontsize=8)

        unit = str(spec.get("unit", "")).strip()
        label = str(spec.get("label", spec.get("variable", "Field")))
        legend_items.append(
            Line2D(
                [0],
                [0],
                color=spec.get("color", "black"),
                linewidth=float(spec.get("linewidth", 1.4)),
                linestyle=spec.get("linestyle", "-"),
                label=label + (f" [{unit}]" if unit else ""),
            )
        )

    if show_solved_contours:
        solved = np.asarray(result["solved_value_grids"], dtype=float)
        for q, spec in enumerate(result["solved_variables"]):
            draw_family(solved[:, :, q], spec)

    if show_contour_fields:
        fields = np.asarray(result["contour_field_grids"], dtype=float)
        for q, spec in enumerate(result["contour_fields"]):
            draw_family(fields[:, :, q], spec)

    margins = np.asarray(result["limit_margins"], dtype=float)
    feasible_nodes = np.zeros_like(converged, dtype=bool)
    violated_nodes = np.zeros_like(converged, dtype=bool)

    if show_limits and result["limits"]:
        for q, spec in enumerate(result["limits"]):
            field = np.where(converged, margins[:, :, q], np.nan)
            contour = _contour_if_spanned(
                ax,
                te_grid,
                ne_grid,
                field,
                0.0,
                colors=spec["color"],
                linewidths=spec["linewidth"],
                linestyles="--",
            )
            if contour is not None:
                legend_items.append(
                    Line2D(
                        [0],
                        [0],
                        color=spec["color"],
                        linewidth=spec["linewidth"],
                        linestyle="--",
                        label=spec["label"],
                    )
                )

        finite = np.isfinite(margins)
        feasible_nodes = (
            converged
            & np.all(finite, axis=2)
            & np.all(margins >= 0.0, axis=2)
        )
        violated_nodes = converged & np.any(finite & (margins < 0.0), axis=2)

        dense_te, dense_ne, dense_feasible, dense_violated = _dense_feasibility(
            te,
            ne20,
            margins,
            converged,
        )
        if np.any(dense_violated):
            if shade_violations:
                ax.contourf(
                    dense_te,
                    dense_ne,
                    dense_violated.astype(float),
                    levels=[0.5, 1.5],
                    colors=["0.35"],
                    alpha=0.055,
                    zorder=5.05,
                )
            if hatch_violations:
                with mpl.rc_context({"hatch.color": "0.30", "hatch.linewidth": 0.28}):
                    ax.contourf(
                        dense_te,
                        dense_ne,
                        dense_violated.astype(float),
                        levels=[0.5, 1.5],
                        colors="none",
                        hatches=["xx"],
                        zorder=5.1,
                    )
            legend_items.append(
                Patch(
                    facecolor="0.5" if shade_violations else "none",
                    edgecolor="0.35",
                    alpha=0.15 if shade_violations else 1.0,
                    hatch="xx" if hatch_violations else None,
                    label="At least one selected limit violated",
                )
            )

        if np.any(dense_feasible):
            legend_items.append(
                Patch(
                    facecolor="none",
                    edgecolor="0.45",
                    label="Unhatched: all selected limits satisfied",
                )
            )

    invalid = ~converged
    if hatch_invalid and np.any(invalid):
        with mpl.rc_context({"hatch.color": "0.45", "hatch.linewidth": 0.25}):
            ax.contourf(
                te_grid,
                ne_grid,
                invalid.astype(float),
                levels=[0.5, 1.5],
                colors="none",
                hatches=["...."],
                zorder=6,
            )
        legend_items.append(
            Patch(
                facecolor="none",
                edgecolor="0.45",
                hatch="....",
                label="No converged equality solution",
            )
        )

    reference_note = None
    if show_reference:
        reference = result["reference"]
        ref_te = _to_float(reference.get("te"))
        ref_ne = _to_float(reference.get("ne"))
        if reference.get("converged", False) and np.isfinite(ref_te) and np.isfinite(ref_ne):
            ref_ne20 = ref_ne / 1.0e20
            if te.min() <= ref_te <= te.max() and ne20.min() <= ref_ne20 <= ne20.max():
                ax.scatter(
                    [ref_te],
                    [ref_ne20],
                    marker="o",
                    s=105,
                    facecolor="white",
                    edgecolor="black",
                    linewidth=1.6,
                    zorder=14,
                )
                legend_items.append(
                    Line2D(
                        [0],
                        [0],
                        marker="o",
                        markersize=8,
                        markerfacecolor="white",
                        markeredgecolor="black",
                        linestyle="none",
                        label=reference_label,
                    )
                )
            else:
                reference_note = "Reference solution lies outside plotted Te-ne window"
        else:
            reference_note = "Reference PROCESS solution did not converge"

    ax.set_xlabel(r"Volume-averaged electron temperature, $T_e$ [keV]")
    ax.set_ylabel(r"Volume-averaged electron density, $n_e$ [$10^{20}$ m$^{-3}$]")
    ax.set_title(result["title"])
    ax.grid(alpha=0.15)

    if legend_items:
        info_ax.legend(
            handles=legend_items,
            loc="upper left",
            bbox_to_anchor=(0.0, 1.0),
            frameon=False,
            fontsize=7.8,
            borderaxespad=0.0,
            handlelength=2.5,
            labelspacing=0.35,
        )

    if reference_note:
        info_ax.text(
            0.0,
            0.02,
            reference_note,
            transform=info_ax.transAxes,
            ha="left",
            va="bottom",
            fontsize=8,
            color="0.35",
        )

    n_valid = int(np.count_nonzero(converged))
    n_total = int(converged.size)
    summary = [f"{n_valid}/{n_total} fixed Te-ne points converged"]
    if show_limits and result["limits"]:
        summary.append(
            f"{np.count_nonzero(feasible_nodes)}/{n_total} sampled nodes satisfy "
            "all selected limits"
        )
        summary.append(
            f"{np.count_nonzero(violated_nodes)}/{n_total} sampled nodes violate ≥1 selected limit"
        )

    ax.text(
        0.01,
        0.01,
        "\n".join(summary),
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=8,
        color="0.3",
        zorder=20,
    )
    plt.show()

def show_popcon_contours(
    result: dict[str, Any],
    **kwargs,
) -> None:
    """Show an ARC-style line-contour POPCON without a filled background.

    This is a convenience wrapper around :func:`show_popcon`.  All contour
    families are still evaluated from the same solved POPCON grid.
    """
    kwargs.setdefault("show_filled", False)
    kwargs.setdefault("shade_violations", False)
    kwargs.setdefault("hatch_violations", False)
    return show_popcon(result, **kwargs)

__all__ = [
    "show_response",
    "show_popcon",
    "show_popcon_contours",
]