import marimo

__generated_with = "0.25.2"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _():
    # imports for marimo
    # import process, and
    import subprocess

    subprocess.call(["pip", "install", "-q", "git+https://github.com/ukaea/PROCESS"])

    from fsspec.implementations.github import GithubFileSystem

    process_repo = GithubFileSystem(org="ukaea", repo="PROCESS", sha="5a81dac")

    INDAT_path = "github://examples/demonstration/data/large_tokamak_eval_IN.DAT"
    INDAT = process_repo.download(INDAT_path, "")

    import os
    from pathlib import Path

    if not Path("demo").exists():
        os.mkdir("demo")

    folder_path = "examples/demonstration/"
    destination = Path("demo/")

    remote_files = process_repo.ls(folder_path)
    process_repo.get(remote_files, destination.as_posix(), recursive=True)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # PROCESS: From Integrated Reactor Design to Plasma Equilibrium Exploration

    <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 25px;">

    <div style="
      flex: 1 1 60%;
      font-family: 'Segoe UI', sans-serif;
      font-size: calc(0.95rem + 0.3vw);
      line-height: 1.6;
      padding-left: 2em;
      padding-right: 2em;
      box-sizing: border-box;
    ">

    **PROCESS** is a systems code for the conceptual design and optimisation of fusion power plants.

    It couples reduced-order plasma-physics and engineering models so that a reactor can be assessed as a
    **single self-consistent system**, rather than as a collection of independent subsystems.

    PROCESS is developed by the Power Plant Modelling and Integration (PPMI) group within Fusion Technology at UKAEA.

    ---

    <details>
    <summary style="font-weight: bold; cursor: pointer;">🌍 Role in fusion design studies</summary>

    - Explore broad reactor design spaces quickly.
    - Test whether proposed designs satisfy coupled physics and engineering requirements.
    - Identify trade-offs between plasma performance, magnets, geometry, power balance and plant performance.
    - Provide an integrated starting point for more detailed design studies.

    </details>

    ---

    <details>
    <summary style="font-weight: bold; cursor: pointer;">🔧 Modelling approach</summary>

    - **Reduced-order models** — mainly 0D–1D descriptions of the plasma and plant systems.
    - **Coupled calculation** — changing one part of the reactor can alter many others.
    - **Fast evaluation** — suitable for parameter scans, optimisation and uncertainty studies.

    </details>

    ---

    <details open>
    <summary style="font-weight: bold; cursor: pointer;">🧭 Learning goals</summary>

    By the end of the notebook you should understand:

    1. How to represent a fusion power plant as a coupled system of models;
    2. How a self-consistent fusion power plant plasma state is defined;
    3. How changing design choices moves the solution through design space;
    4. **How PROCESS helps us make answer the above points and make design decisions** by exposing the trade-offs between performance, feasibility and operating margin.

    </details>

    </div>

    <div style="
      flex: 1 1 50%;
      min-width: 300px;
      text-align: center;
      box-sizing: border-box;
    ">
      <img src="figures/Slide7.jpeg"
           alt="PROCESS Fusion Power Plant Design"
           style="width: 100%; max-width: 850px; height: auto; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.25);">
      <p style="font-size: 13px; color: #555; margin-top: 6px;">
        A tokamak is coupled to the systems that convert fusion power into useful electrical output.
      </p>
    </div>

    </div>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Run PROCESS

    To initialise the notebook, we can run a normal PROCESS input file.
    """)
    return


@app.cell
def _():
    from process.main import SingleRun

    single_run = SingleRun("data/large_tokamak_eval_IN.DAT")
    single_run.run()
    return (single_run,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Generate the standard summary

    PROCESS can generate a summary PDF which contains data and plots to describe the fusion power plant we have designed. We call this here to generate figures for the notebook.
    """)
    return


@app.cell
def _(single_run):
    from process.core.io.plot import plot_summary

    plot_summary(single_run.mfile_path)
    return


@app.cell
def _():
    import pymupdf

    summary_file = "data/large_tokamak_eval_MFILE.DAT.SUMMARY.pdf"
    file_handle = pymupdf.open(summary_file)

    for page_no in [
        5,
        6,
    ]:
        page = file_handle[page_no]
        page_img = page.get_pixmap()
        page_img.save(f"figures/summary_page_{page_no}.png")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style="display: flex; align-items: center; justify-content: space-between; gap: 25px; flex-wrap: wrap;">

    <div style="flex: 1 1 38%; min-width: 300px; text-align: center; box-sizing: border-box;">
      <img src="figures/summary_page_5.png"
           alt="Tokamak Summary Plot"
           style="width: 100%; max-width: 40vw; height: auto; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.25);">
      <p style="font-size: 13px; color: #555; margin-top: 6px;">
        Integrated plasma, magnetic and systems quantities from one PROCESS design.
      </p>
    </div>

    <div style="
      flex: 1 1 60%;
      font-family: 'Segoe UI', sans-serif;
      font-size: calc(0.95rem + 0.3vw);
      line-height: 1.6;
      padding-left: 2em;
      padding-right: 2em;
      box-sizing: border-box;
    ">

    ### PROCESS: Integrated Reactor Design

    A single PROCESS solution calculates quantities across the whole plant, including:

    - 🔥 **plasma state and fusion performance**
    - 📐 **geometry and magnetic fields**
    - ⚡ **heating and current drive**
    - 🔌 **power flows and plant performance**
    - 🧲 **pulse and magnet requirements**
    - ⚠️ **physics and engineering limits**

    The important point is not any one number: **all of these quantities belong to the same coupled reactor design.**

    A change to one part of the reactor can therefore propagate through many other systems.

    </div>
    </div>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style="display: flex; align-items: center; justify-content: space-between; gap: 25px;">

    <!-- Left column: Image -->
    <div style="
      flex: 1 1 38%;
      min-width: 300px;
      text-align: center;
      box-sizing: border-box;
    ">
      <img src="figures/summary_page_23.png"
           alt="Tokamak Poloidal Cross-Section"
           style="width: 100%; max-width: 40vw; height: auto; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.25);">
      <p style="font-size: 13px; color: #555; margin-top: 6px;">
        Poloidal and toroidal cross-sections of the tokamak showing major structural and magnetic systems.
      </p>
    </div>

    <!-- Right column: Text -->
    <div style="
      flex: 1 1 60%;
      font-family: 'Segoe UI', sans-serif;
      font-size: calc(0.95rem + 0.3vw);
      line-height: 1.6;
      padding-left: 2em;
      padding-right: 2em;
      box-sizing: border-box;
    ">

    ### **Poloidal and Toroidal Cross-Sections**

    We also use PROCESS to create initial **cross-section views of the tokamak reactor:**
    1. **Poloidal section** (vertical cut through the plasma)
    2. **Toroidal section** (horizontal slice around the machine’s ring).

    - 🟡 **Plasma:** The hot ionised gas confined by strong magnetic fields at the centre.
    - 🟣 **First wall:** The inner surface facing the plasma that acts as armour, absorbing heat and particle flux.
    - 🟢 **Blanket:** Surrounds the first wall - captures neutrons to breed tritium and generate useful heat.
    - ⚫ **Vacuum vessel & shield:** Provides mechanical support and radiation protection to components.
    - 🔵 **Magnetic Coils:** Superconducting coils that shape and confine the plasma.
    - 🟥 **Cryostat:** The outer shell keeping the superconducting magnets cold and isolated.

    PROCESS is used to calculate these cross sections self-consistently ensuring all the components align and there are no overlaps.

    </div>

    </div>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style="
      font-family: 'Segoe UI', sans-serif;
      font-size: calc(0.95rem + 0.3vw);
      line-height: 1.6;
      padding-left: 2em;
      padding-right: 2em;
      box-sizing: border-box;
      max-width: 1350px;
    ">

    ## 🧩 PROCESS: Problem Formulation

    PROCESS can be thought of as a **complex function which maps inputs to outputs** describing a steady-state fusion power plant.

    $$
    \mathbf y = F(\mathbf x,\mathbf d,\mathbf u,\boldsymbol{\theta})
    $$

    <div style="
      margin-top: 1em;
      padding: 0.8em 1em;
      border-left: 4px solid #777;
      background: rgba(127,127,127,0.08);
      border-radius: 4px;
    ">

    <b>In simple terms:</b> we specify what we know or choose, PROCESS solves the coupled physics and engineering problem, and returns the resulting reactor state.

    </div>

    ---

    ### 🎛️ Inputs

    It is useful to separate the inputs conceptually into

    $$
    \mathbf d = \text{design variables},
    \qquad
    \mathbf u = \text{control variables},
    \qquad
    \boldsymbol{\theta} = \text{uncertain parameters}.
    $$

    - 🏗️ **Design variables** describe the system we choose to build — geometry, magnetic field, component dimensions and technology choices.

    - 🎚️ **Control variables** describe how the system is operated — auxiliary heating, fuelling, current drive and other actuator-like quantities.

    - 🎲 **Uncertain parameters** describe quantities that are not controlled precisely — confinement scalings, efficiencies, material properties and model assumptions.

    ---

    This distinction is useful because different analyses choose different quantities to **prescribe, vary, solve for, or treat as uncertain**.

    $$
    \boxed{
    \text{Inputs}
    \;\longrightarrow\;
    \text{PROCESS}
    \;\longrightarrow\;
    \text{Outputs}
    }
    $$

    </div>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style="
      font-family: 'Segoe UI', sans-serif;
      font-size: calc(0.95rem + 0.3vw);
      line-height: 1.6;
      padding-left: 2em;
      padding-right: 2em;
      box-sizing: border-box;
      max-width: 1350px;
    ">

    ## Steady-State Plasma

    The prescribed inputs alone do not completely define the reactor state. PROCESS must also determine a **self-consistent plasma operating state**.

    For the response problem used in this notebook, we represent this state by

    $$
    \mathbf x =
    \begin{bmatrix}
    T_e \\
    n_e
    \end{bmatrix},
    $$

    where $T_e$ and $n_e$ are the volume-averaged electron temperature and density.

    For a given set of design variables $\mathbf d$, control variables $\mathbf u$, and uncertain parameters $\boldsymbol{\theta}$, PROCESS determines $\mathbf x$ by satisfying two governing equations.

    ---

    <details open style="
      font-family: 'Segoe UI', sans-serif;
      font-size: calc(0.95rem + 0.3vw);
      line-height: 1.6;
      margin-top: 1em;
      margin-bottom: 1em;
    ">
    <summary style="
      font-weight: bold;
      font-size: inherit;
      cursor: pointer;
      padding: 0.35em 0;
    ">
    🔥 Global plasma power balance
    </summary>

    <div style="
      font-family: 'Segoe UI', sans-serif;
      font-size: calc(0.95rem + 0.3vw);
      line-height: 1.6;
      padding-top: 0.6em;
    ">

    The power entering the plasma must balance the power leaving it,

    $$
    P_{\mathrm{heating}} = P_{\mathrm{loss}}
    $$

    Heating includes alpha-particle, ohmic and auxiliary heating, while losses include transport and plasma radiation.

    In PROCESS this is represented by the **global power-balance equation**.

    </div>
    </details>

    ---

    <details open style="
      font-family: 'Segoe UI', sans-serif;
      font-size: calc(0.95rem + 0.3vw);
      line-height: 1.6;
      margin-top: 1em;
      margin-bottom: 1em;
    ">
    <summary style="
      font-weight: bold;
      font-size: inherit;
      cursor: pointer;
      padding: 0.35em 0;
    ">
    ⛽ Fuel-ion balance
    </summary>

    <div style="
      font-family: 'Segoe UI', sans-serif;
      font-size: calc(0.95rem + 0.3vw);
      line-height: 1.6;
      padding-top: 0.6em;
    ">

    The supplied fuel rate must be consistent with the rate at which fuel is consumed and lost from the plasma,

    $$
    \dot N_{\mathrm{fuel}}
    =
    \frac{R_{\mathrm{fusion}}}{f_{\mathrm{burnup}}}
    $$

    In PROCESS this is represented by the **fuel-ion balance equation**.

    </div>
    </details>

    ---

    <details style="
      font-family: 'Segoe UI', sans-serif;
      font-size: calc(0.95rem + 0.3vw);
      line-height: 1.6;
      margin-top: 1em;
      margin-bottom: 1em;
    ">
    <summary style="
      font-weight: bold;
      font-size: inherit;
      cursor: pointer;
      padding: 0.35em 0;
    ">
    📏 What is a residual?
    </summary>

    <div style="
      font-family: 'Segoe UI', sans-serif;
      font-size: calc(0.95rem + 0.3vw);
      line-height: 1.6;
      padding-top: 0.6em;
    ">

    PROCESS expresses each governing equation as a **residual**.

    A residual measures how far the current state is from satisfying the equation:

    $$
    R = \text{left-hand side} - \text{right-hand side}.
    $$

    If

    $$
    R = 0,
    $$

    the equation is satisfied exactly.

    If $R \neq 0$, the current plasma state is not self-consistent with that governing equation.

    For the two plasma governing equations, the residuals are collected into

    $$
    \mathbf R(\mathbf x;\mathbf d,\mathbf u,\boldsymbol{\theta})
    =
    \begin{bmatrix}
    R_{\mathrm{power}} \\
    R_{\mathrm{fuel}}
    \end{bmatrix}.
    $$

    A PROCESS plasma solution requires

    $$
    \boxed{
    \mathbf R =
    \begin{bmatrix}
    0 \\
    0
    \end{bmatrix}
    }
    $$

    so both governing equations are satisfied simultaneously.

    </div>
    </details>

    ---

    For this response problem, PROCESS varies $T_e$ and $n_e$ until both residuals are zero.

    This gives a closed two-equation nonlinear problem for the two plasma-state variables.

    Once this state has been found, PROCESS evaluates the coupled physics and engineering models to determine the remaining outputs,

    $$
    \mathbf y = F(\mathbf x,\mathbf d,\mathbf u,\boldsymbol{\theta}).
    $$

    </div>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style="
      font-family: 'Segoe UI', sans-serif;
      font-size: calc(0.95rem + 0.3vw);
      line-height: 1.6;
      padding-left: 2em;
      padding-right: 2em;
      box-sizing: border-box;
      max-width: 1350px;
    ">

    ## 🎛️ How Does the Plasma Respond to Heating and Fuelling Choices?

    Now that we have defined the PROCESS problem, we can use it to ask a simple but important question:

    > **If we change the controls, how does the steady-state plasma operating point respond?**

    For this example we vary only two control variables:

    - 🔥 **Extra heating** changes the auxiliary power supplied to the plasma by the neutral beam system.
    - ⛽ **Fuel supply** changes the fuel particle throughput and is coupled to the fusion reaction rate through C93.

    For each combination of heating and fuelling, these controls are prescribed and PROCESS solves the two governing equations for the corresponding plasma state,

    $$
    (\text{heating},\ \text{fuelling})
    \longrightarrow
    (T_e,n_e).
    $$

    In this way, PROCESS can be used to **simulate the steady-state plasma response to changes in the control inputs**.

    ---

    <details style="
      font-family: 'Segoe UI', sans-serif;
      font-size: calc(0.95rem + 0.3vw);
      line-height: 1.6;
      margin-top: 1em;
      margin-bottom: 1.2em;
    ">

    <summary style="
      font-weight: bold;
      font-size: inherit;
      cursor: pointer;
      padding: 0.45em 0;
    ">
    🗺️ How to Read the Plasma Solution Space
    </summary>

    <div style="
      padding-top: 0.8em;
    ">

    For each combination of heating and fuelling, PROCESS varies $T_e$ and $n_e$ until the two governing equations are satisfied.

    The resulting plasma state is therefore an **output of the PROCESS solution**.

    ### 🎯 PROCESS solutions

    Each coloured marker is a **PROCESS solution** generated from one sampled combination of heating and fuelling.

    Its position gives the resulting plasma state,

    $$
    (T_e,n_e),
    $$

    while its colour shows the **fusion power** of that solution.

    The large outlined marker highlights the currently selected solution.

    ---

    ### 🔗 Governing-equation contours

    For the currently selected heating and fuelling settings:

    - <span style="color:#d62728;"><b>C2 = 0</b></span> shows where **global power balance** is satisfied.
    - <span style="color:#9c27b0;"><b>C93 = 0</b></span> shows where **fuel-ion balance** is satisfied.

    The solid curves show how the governing-equation residuals behave around the selected solution.

    Their intersection identifies the plasma state where both equations are satisfied simultaneously:

    $$
    \boxed{
    C_2 = 0
    \qquad \text{and} \qquad
    C_{93} = 0
    }
    $$

    ---

    ### 🚧 Physics limits

    The dashed curves show where selected physics limits become active, including:

    - **density limit**
    - **beta limit**

    These limits do not define the PROCESS solution — they determine whether that solution is **feasible**.

    A solution can therefore satisfy both governing equations while still violating one or more operating limits.

    </div>
    </details>

    ---

    ## 🎛️ Exercise 1: Explore the Plasma Response

    You now have two control levers: **heating** and **fuelling**.

    Change them and watch how the resulting PROCESS solution moves through the plasma operating space.

    <details open style="
      font-family: 'Segoe UI', sans-serif;
      font-size: calc(0.95rem + 0.3vw);
      line-height: 1.6;
      margin-top: 1em;
      margin-bottom: 1em;
    ">

    <summary style="
      font-weight: bold;
      font-size: inherit;
      cursor: pointer;
      padding: 0.35em 0;
    ">
    🔎 Questions to explore
    </summary>

    <div style="
      padding-top: 0.6em;
    ">

    - 🔥 At fixed fuelling, how does increasing extra heating move the plasma operating point?
    - ⛽ At fixed heating, how does increasing the fuelling rate move it?
    - 🔄 Do heating and fuelling affect $T_e$ and $n_e$ in the same way, or do they act differently?
    - ⚛️ Where are the highest-fusion-power solutions?
    - 🚧 How does moving through the solution space change the margin to the density and beta limits?
    - 🤝 Do the two controls appear to work with or against each other in different parts of the operating space?

    </div>
    </details>

    <div style="
      margin-top: 1.2em;
      padding: 0.8em 1em;
      border-left: 4px solid #777;
      background: rgba(127,127,127,0.08);
      border-radius: 4px;
    ">

    <b>Aim:</b> understand the link between the <b>controls you choose</b> and the <b>plasma state that results</b>, and how performance and constraint margin change as that solution moves.

    </div>

    </div>
    """)
    return


@app.cell
def _():

    import process_response_popcon as explorer

    PLASMA_INPUT_FILE = (
        "../../tests/regression/input_files/spherical_tokamak_eval.IN.DAT"
    )

    DATA_DIR = Path("data")

    HEATING_CONTROL = {
        "variable": "current_drive.p_hcd_primary_extra_heat_mw",
        "range": (0.0, 80.0),
        "n": 5,
        "short_label": "Extra heating",
        "display_scale": 1.0,
        "unit": "MW",
        "format": ".1f",
        "include_reference": True,
    }

    FUEL_CONTROL = {
        "variable": "physics.molflow_plasma_fuelling",
        "range": (4.2e21, 5.2e21),
        "n": 5,
        "short_label": "Fuel supply",
        "display_scale": 1.0e21,
        "unit": "×10²¹ s⁻¹",
        "format": ".3f",
        "include_reference": True,
    }

    PLASMA_CONTROLS = [HEATING_CONTROL, FUEL_CONTROL]

    PLASMA_MAP_POINTS = 10

    REBUILD_PLASMA_SOLUTIONS = False
    REBUILD_PLASMA_MAPS = False
    PRECOMPUTE_PLASMA_MAPS = True
    EXPLORER_WORKERS = 8
    return (
        DATA_DIR,
        EXPLORER_WORKERS,
        PLASMA_CONTROLS,
        PLASMA_INPUT_FILE,
        PLASMA_MAP_POINTS,
        PRECOMPUTE_PLASMA_MAPS,
        REBUILD_PLASMA_MAPS,
        REBUILD_PLASMA_SOLUTIONS,
        explorer,
    )


@app.cell
def _(
    DATA_DIR,
    EXPLORER_WORKERS,
    PLASMA_CONTROLS,
    PLASMA_INPUT_FILE,
    PLASMA_MAP_POINTS,
    PRECOMPUTE_PLASMA_MAPS,
    REBUILD_PLASMA_MAPS,
    REBUILD_PLASMA_SOLUTIONS,
    explorer,
):
    plasma_response = explorer.build_response(
        input_file=PLASMA_INPUT_FILE,
        controls=PLASMA_CONTROLS,
        performance={
            "variable": "physics.p_fusion_total_mw",
            "label": "Fusion power [MW]",
        },
        equalities=[
            {
                "constraint": 2,
                "label": "C2 = 0  global power balance",
                "color": "crimson",
            },
            {
                "constraint": 93,
                "label": "C93 = 0  fuel-ion balance",
                "color": "#9c27b0",
            },
        ],
        limits=[
            {
                "constraint": 5,
                "label": "C5 density upper limit",
                "color": "#2ca02c",
            },
            {
                "constraint": 24,
                "label": "C24 beta upper limit",
                "color": "#ff7f0e",
            },
        ],
        title="PROCESS plasma solution space",
        map_points=PLASMA_MAP_POINTS,
        cache_dir=DATA_DIR,
        cache_name="demo_plasma_response",
        rebuild_solutions=REBUILD_PLASMA_SOLUTIONS,
        rebuild_maps=REBUILD_PLASMA_MAPS,
        precompute_maps=PRECOMPUTE_PLASMA_MAPS,
        max_workers=EXPLORER_WORKERS,
    )
    return (plasma_response,)


@app.cell
def _(explorer, plasma_response):
    explorer.show_response(plasma_response)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style="
      font-family: 'Segoe UI', sans-serif;
      font-size: calc(0.95rem + 0.3vw);
      line-height: 1.6;
      padding-left: 2em;
      padding-right: 2em;
      box-sizing: border-box;
      max-width: 1350px;
    ">

    ## ⚖️ Exercise 2: Heating, Fuelling and Impurity Seeding

    The previous example showed how the plasma responds when we change **heating** and **fuelling**.

    We now introduce a third control: **argon impurity seeding**.

    For each combination of the three controls, PROCESS solves the governing equations and returns the resulting steady-state plasma operating point.

    ---

    ### 🎛️ Three interacting controls

    - 🔥 **Heating** supplies additional energy to the plasma.
    - ⛽ **Fuelling** controls the fuel particle throughput and is coupled to the fusion reaction rate through the fuel-ion balance.
    - 💨 **Argon seeding** introduces a radiating impurity and changes how power is exhausted from the plasma.

    Argon can reduce the power reaching the exhaust by increasing plasma radiation. However, it also changes **fuel dilution**, **$Z_{\mathrm{eff}}$**, and the overall plasma power balance.

    The controls therefore interact:

    $$
    \boxed{
    \text{change controls}
    \;\longrightarrow\;
    \text{new plasma state}
    \;\longrightarrow\;
    \text{new performance + constraint margins}
    }
    $$

    In this example, the starting PROCESS solution is **self-consistent but not feasible**.

    ---

    <div style="
      margin-top: 1.5em;
      padding: 1.1em 1.3em;
      border: 1px solid rgba(127,127,127,0.35);
      border-radius: 8px;
      background: rgba(127,127,127,0.06);
    ">

    ### 👥 Group Exercise: Find a Feasible Solution

    Use **heating, fuelling and argon seeding** to move the PROCESS solution until all three selected limits are satisfied:

    - 🚧 **density**
    - 🚧 **beta**
    - 🚧 **divertor protection**

    <div style="
      margin-top: 1em;
      padding-top: 0.8em;
      border-top: 1px solid rgba(127,127,127,0.25);
    ">

    #### 🔎 While you explore

    Pay attention to:

    - how each control moves the plasma operating point;
    - which constraint margins improve or worsen;
    - whether different controls work with or against each other;
    - which constraint is hardest to satisfy.

    </div>

    <div style="
      margin-top: 1em;
      padding-top: 0.8em;
      border-top: 1px solid rgba(127,127,127,0.25);
    ">

    #### ✅ When you find a feasible solution

    Be ready to explain:

    - Which control changes were most important?
    - What performance was gained or lost?
    - Which constraint became limiting?
    - Could a different combination of controls give another feasible solution?

    </div>

    <div style="
      margin-top: 1.2em;
      padding: 0.8em 1em;
      border-left: 4px solid #777;
      background: rgba(127,127,127,0.10);
      border-radius: 4px;
    ">

    <b>Aim:</b> do not just find a feasible point — understand <b>why</b> it is feasible and what trade-offs were required to reach it.

    </div>

    </div>

    </div>
    """)
    return


@app.cell
def _(PLASMA_INPUT_FILE):
    IMPURITY_INPUT_FILE = PLASMA_INPUT_FILE

    IMPURITY_CONTROLS = [
        {
            "variable": "current_drive.p_hcd_primary_extra_heat_mw",
            "range": (0.0, 50.0),
            "n": 5,
            "short_label": "Extra heating",
            "display_scale": 1.0,
            "unit": "MW",
            "format": ".1f",
            "include_reference": True,
        },
        {
            "variable": "impurity_radiation.f_nd_impurity_electrons(9)",
            "values": [0.0, 2.5e-4, 5.0e-4, 7.5e-4],
            "short_label": "Argon seeding",
            "display_scale": 1.0e-2,
            "unit": "% nₑ",
            "format": ".3f",
            "include_reference": True,
        },
        {
            "variable": "physics.molflow_plasma_fuelling",
            "range": (4.2e21, 5.2e21),
            "n": 5,
            "short_label": "Fuel supply",
            "display_scale": 1.0e21,
            "unit": "×10²¹ s⁻¹",
            "format": ".3f",
            "include_reference": True,
        },
    ]

    REBUILD_IMPURITY_SOLUTIONS = False
    REBUILD_IMPURITY_MAPS = False
    PRECOMPUTE_IMPURITY_MAPS = True
    IMPURITY_WORKERS = 10
    return (
        IMPURITY_CONTROLS,
        IMPURITY_INPUT_FILE,
        IMPURITY_WORKERS,
        PRECOMPUTE_IMPURITY_MAPS,
        REBUILD_IMPURITY_MAPS,
        REBUILD_IMPURITY_SOLUTIONS,
    )


@app.cell
def _(
    DATA_DIR,
    IMPURITY_CONTROLS,
    IMPURITY_INPUT_FILE,
    IMPURITY_WORKERS,
    PRECOMPUTE_IMPURITY_MAPS,
    REBUILD_IMPURITY_MAPS,
    REBUILD_IMPURITY_SOLUTIONS,
    explorer,
):
    impurity_response = explorer.build_response(
        input_file=IMPURITY_INPUT_FILE,
        controls=IMPURITY_CONTROLS,
        performance={
            "variable": "physics.p_fusion_total_mw",
            "label": "Fusion power [MW]",
        },
        equalities=[
            {
                "constraint": 2,
                "label": "C2 = 0  global power balance",
                "color": "crimson",
            },
            {
                "constraint": 93,
                "label": "C93 = 0  fuel-ion balance",
                "color": "#9c27b0",
            },
        ],
        limits=[
            {
                "constraint": 68,
                "label": "C68 divertor protection",
                "color": "#ff7f0e",
            },
            {
                "constraint": 5,
                "label": "C5 density limit",
                "color": "#00a6d6",
            },
            {
                "constraint": 24,
                "label": "C24 beta limit",
                "color": "#2ca02c",
            },
        ],
        title="Heating, fuelling and impurity-seeding trade-off",
        map_points=20,
        te_padding_min_kev=0.8,
        ne_padding_min=0.04e20,
        cache_dir=DATA_DIR,
        cache_name="demo_impurity_response",
        rebuild_solutions=REBUILD_IMPURITY_SOLUTIONS,
        rebuild_maps=REBUILD_IMPURITY_MAPS,
        precompute_maps=PRECOMPUTE_IMPURITY_MAPS,
        max_workers=IMPURITY_WORKERS,
    )
    return (impurity_response,)


@app.cell
def _(explorer, impurity_response):
    explorer.show_response(impurity_response, show_solution_cloud=False)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style="
      font-family: 'Segoe UI', sans-serif;
      font-size: calc(0.95rem + 0.3vw);
      line-height: 1.6;
      padding-left: 2em;
      padding-right: 2em;
      box-sizing: border-box;
      max-width: 1350px;
    ">

    ## From Exploration to Optimisation

    In this notebook we changed a small number of controls ourselves and watched how the PROCESS solution moved through the available design space.

    We then had to decide:

    - which solutions were **feasible**;
    - how much **margin** they had to the limits;
    - what **performance** they achieved;
    - what trade-offs were required to get there.

    ---

    ### 🎯 Formalising the Design Choice

    PROCESS formalises this process when optimising. Optimisation performs the same kind of search systematically.

    We define:

    - **iteration variables** - what PROCESS is allowed to change;
    - **consistency equations** - what must be satisfied for the design to be self-consistent;
    - **limits** - what defines the feasible design space;
    - **an objective** - what we want the optimiser to improve.

    The optimiser then searches the available solution space for the feasible design that best satisfies that objective.

    ---

    $$
    \boxed{
    \text{Explore the solution space}
    \quad\longrightarrow\quad
    \text{understand the trade-offs}
    \quad\longrightarrow\quad
    \text{formalise the design objective}
    }
    $$

    **We decide what matters, and encode those engineering priorities in the optimisation problem, and use the solver to find the optimimum solution**

    </div>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 25px; flex-wrap: wrap;">

    <div style="
      flex: 1 1 58%;
      font-family: 'Segoe UI', sans-serif;
      font-size: calc(0.95rem + 0.3vw);
      line-height: 1.6;
      text-align: left;
      padding-left: 2em;
      padding-right: 2em;
      box-sizing: border-box;
      max-width: 1350px;
    ">

    ### PROCESS

    🔗 **PROCESS source code:** [github.com/ukaea/PROCESS](https://github.com/ukaea/PROCESS)

    ### Fusion Training Program

    This material forms part of the **Fusion Training Program**: [Nucleus](https://nucleus.ukaea.uk/page/11260)


    </div>
    </div>
    """)
    return


if __name__ == "__main__":
    app.run()
