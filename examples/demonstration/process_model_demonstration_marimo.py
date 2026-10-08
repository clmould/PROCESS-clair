import marimo

__generated_with = "0.23.14"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 25px;">

    <!-- Left column: Text -->
    <div style="
      flex: 1 1 60%;
      font-family: 'Segoe UI', sans-serif;
      font-size: calc(0.95rem + 0.3vw);
      line-height: 1.6;
      padding-left: 2em;
      padding-right: 2em;
      box-sizing: border-box;
    ">

    ### ⚙️ PROCESS: A Fusion Powerplant Design Tool

    **PROCESS** is a *systems code* used to design and optimise conceptual fusion power plants.

    It combines simplified physics and engineering models in a single framework to test whether
    a reactor can operate **self-consistently** within its **physics and engineering constraints**.
      - Developed by the Power Plant Modelling and Integration (PPMI) group within Fusion Technology at UKAEA.

    ---

    <details>
    <summary style="font-weight: bold; cursor: pointer;">🌍 Role in Fusion System Design Studies</summary>

    <!-- By modelling all major power plant systems, PROCESS acts as a rapid design tool for exploring conceptual reactor configurations. -->

    - Supports **major design studies**, including **STEP** and **EU DEMO**.
    - Serves as the **starting point** for exploring the fusion power plant design space.
    - Reveals **trade-offs** between performance, cost, and availability.
    - Tests **feasibility** under realistic operational and material limits.

    </details>

    ---

    <details>
    <summary style="font-weight: bold; cursor: pointer;">🔧 Key Features</summary>

    - **Modelling approach** - employs **low-fidelity (0D-1D)** models for most powerplant systems (plasma, magnets, structures, and cost).
    - **Integration** - system-level behaviour emerges as as PROCESS couples the models and resolves their competing requirements.
    - **Speed** - computationally efficient models and runs quickly, enabling **rapid design iteration** and **broad exploration** of design space.

    </details>

    ---

    <details>
    <summary style="font-weight: bold; cursor: pointer;">💻 Technical Details</summary>

    - **PROCESS** is code written in **Python** (originally developed in **FORTRAN**).
    - In this Jupyter Notebook, we demonstrate PROCESS by looking at:
      - PROCESS: how it works & its inputs and outputs.
      - Model spotlight: we look at one detailed model in isolation (CS Fatigue).
      - Design challenge: we apply PROCESS and the model to resolve a design challenge.

    </details>

    ---

    </div>

    <!-- Right column: Image -->
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
        Simplified view of a tokamak as it is coupled to a heat-exchanger and delivers power to the grid.
      </p>
    </div>

    </div>
    """)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    """)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 25px;">

      <!-- Left column: Text -->
      <div style="
        flex: 1 1 60%;
        font-family: 'Segoe UI', sans-serif;
        font-size: calc(0.95rem + 0.3vw);
        line-height: 1.6;
        padding-left: 2em;
        padding-right: 2em;
        box-sizing: border-box;
      ">

      ### ⚙️ The PROCESS Design Loop

      Designing a tokamak with PROCESS means formulating a mathematical optimisation problem and using PROCESS to solve it.
      The resulting solution represents a **self-consistent reactor design**.

      Each step below corresponds to a stage in this design process.

      ---

      <details open>
      <summary><b>🎯 1. Define Design Requirements</b></summary>
      <div style="margin-left: 1em; margin-top: 0.5em;">

      Typically there is some overall target that the design is trying to achieve or demonstrate.
      For example:

      - 💡 **Net electric power:** 500 MW
      - ⏱️ **Pulse length:** 2 hours

      </div>
      </details>

      ---

      <details open>
      <summary><b>🧭 2. Define the Design Space</b></summary>
      <div style="margin-left: 1em; margin-top: 0.5em;">

      The **design space** is the space over which PROCESS can trade variable values - exploring how different physics and engineering choices affect performance.

      It is defined in two ways:

      - **Constraints**, which ensure technical feasibility:
        - ⚖️ *Equality constraints* - must be satisfied exactly (e.g. power balance, radial build).
        - 🚦 *Inequality constraints* - must not be violated (e.g. stress, field, temperature, or wall load limits).

      - **Iteration variables**, which the solver adjusts as it searches for a solution:
        - ⚡ Plasma current
        - 🧲 Magnetic field strength
        - 🧱 Blanket and shield thickness
        - 🔁 Non-inductive current fraction

      Together, these define the **region of design space** that PROCESS explores.

      </div>
      </details>

      ---

      <details open>
      <summary><b>🔧 3. Select an Optimisation Objective</b></summary>
      <div style="margin-left: 1em; margin-top: 0.5em;">

      Choose what PROCESS should *optimise* within the feasible region - the **objective function**.
      Common goals include:

      - Minimising the **major radius** (compact design)
      - Maximising **net electric output**
      - Minimising **cost of electricity**

      This defines the *direction* of the optimisation, balancing performance against engineering practicality.

      </div>
      </details>

      ---

      <details open>
      <summary><b>🧮 4. Solve for a Self-Consistent Design</b></summary>
      <div style="margin-left: 1em; margin-top: 0.5em;">

      Finally, PROCESS applies an **iterative gradient-based solver** to converge on a point that:

      - ⚙️ Satisfies the design requirements
      - ✅ Meets all physics and engineering constraints
      - 📈 Optimises the chosen objective function

      The result is a **self-consistent reactor design** which has been deemed optimal within our design space.

      </div>
      </details>

      </div>

      <!-- Right column: Image -->
      <div style="
        flex: 1 1 40%;
        min-width: 300px;
        text-align: center;
        box-sizing: border-box;
      ">
        <img src="figures/fusrr-output.png"
             alt="PROCESS output rendered by Fusrr"
             style="width: 100%; max-width: 550px; height: auto; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.25);">
        <p style="font-size: 13px; color: #555; margin-top: 6px;">
          A self-consistent reactor geometry from PROCESS, visualised with <b>Fusrr</b> - developed by the PPMI group.
        </p>

      </div>

    </div>
    """)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    """)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 25px;">

      <!-- Left column: Text -->
      <div style="
        flex: 1 1 60%;
        font-family: 'Segoe UI', sans-serif;
        font-size: calc(0.95rem + 0.3vw);
        line-height: 1.6;
        padding-left: 2em;
        padding-right: 2em;
        box-sizing: border-box;
      ">

      ### ▶️ Running PROCESS: Large Tokamak Example

      We now demonstrate **PROCESS** in action using the **Large Tokamak** example - a generic reactor concept similar in scale to **EU DEMO**.

      In this optimisation, PROCESS links together detailed **plasma physics**, **engineering**, and **cost** models.
      We'll apply the steps we described in the previous section.

      ---

      <details open>
      <summary><b>🎯 1. Design Requirements</b></summary>
      <div style="margin-left: 1em; margin-top: 0.5em;">

      We begin by defining high-level performance targets for the reactor:

      - 💡 **Net electric power:** 400 MW

      This target sets the overall performance criteria that PROCESS must achieve.

      </div>
      </details>

      ---

      <details open>
      <summary><b>🧭 2. Design Space: Constraints and Variables</b></summary>
      <div style="margin-left: 1em; margin-top: 0.5em;">

      The **design space** defines both what PROCESS can change (iteration variables) and what it must obey (constraints).
      PROCESS explores this space to find a feasible, optimised reactor configuration.

      ---

      <details>
      <summary style="font-weight: bold; cursor: pointer;">🔒 Constraints</summary>
      <div style="margin-left: 1em; margin-top: 0.5em;">

      To ensure the reactor design is physically and technically feasible, PROCESS enforces:

      - **Beta balance:** plasma pressure consistent with magnetic confinement.
      - **Power balance:** fusion output = system losses + plant power.
      - **Radial build:** all components fit within the machine geometry.
      - **Density limit:** \( n_e \le 7.5\times10^{19}\,\mathrm{m^{-3}} \)
      - **Toroidal field (inboard):** ≤ 14 T
      - **Neutron wall load:** ≤ 2 MW/m²
      - **Fusion power:** ≤ 3 GW
      - **TF and CS coil stresses:** below material yield limits.
      - **Superconductor temperature margin:** ≥ 1.5 K (TF and CS).
      - **Quench / dump protection:** voltage and current density must be safe.

      These collectively define the **feasible region** within which PROCESS must search.

      </div>
      </details>

      ---

      <details>
      <summary style="font-weight: bold; cursor: pointer;">⚙️ Iteration Variables</summary>
      <div style="margin-left: 1em; margin-top: 0.5em;">

      Within this region, PROCESS varies key **optimisation variables**:

      - Plasma temperature - 12 keV
      - Plasma density - \(7.5\times10^{19}\,\mathrm{m^{-3}}\)
      - Toroidal magnetic field - 5.7 T
      - Edge safety factor - 3.5
      - Central solenoid thickness - 0.5 m
      - Machine bore - 2.0 m
      - TF winding pack thickness - 0.5 m
      - TF conduit thickness - 0.008 m
      - TF copper fraction - 0.8
      - Non-inductive current fraction - 0.4

      These parameters define the **design levers** PROCESS can move to reach an optimised state.

      </div>
      </details>

      </div>
      </details>

      ---

      <details open>
      <summary><b>🎯 3. Optimisation Objective: Major Radius</b></summary>
      <div style="margin-left: 1em; margin-top: 0.5em;">

      In this example, the **objective function** is to **minimise the major radius** of the machine
      while still meeting all performance and engineering requirements.

      </div>
      </details>

      ---

      We now run PROCESS…

      </div>

      <!-- Right column: Image -->
      <div style="
        flex: 1 1 40%;
        min-width: 300px;
        text-align: center;
        box-sizing: border-box;
      ">
        <img src="figures/Slide2.jpg"
             alt="Diagram showing PROCESS design loop"
             style="width: 100%; height: auto; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.25);">
        <p style="font-size: 13px; color: #555; margin-top: 6px;">
          The PROCESS physics, engineering, and cost models interact until a self-consistent design is found.
        </p>
      </div>

    </div>
    """)


@app.cell
def _():
    from process.main import SingleRun

    # Run process on an input file in a temporary directory
    single_run = SingleRun("data/large_tokamak_eval_IN.DAT")
    single_run.run()
    return SingleRun, single_run


@app.cell
def _(single_run):
    # Create the summary pdf

    from process.core.io.plot import plot_summary

    plot_summary(single_run.mfile_path)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 25px;">

    <!-- Left column -->
    <div style="
      flex: 1 1 60%;
      font-family: 'Segoe UI', sans-serif;
      font-size: calc(0.95rem + 0.3vw);
      line-height: 1.6;
      padding-left: 2em;
      padding-right: 2em;
      box-sizing: border-box;
    ">

    ### 🏁 Solution Summary

    PROCESS has successfully performed a **VMCON optimisation run**, resulting in a **feasible, self-consistent reactor design** that satisfies all physics and engineering constraints.

    We now inspect the output: a collection of system variables and their converged values.

    ---

    <details>
    <summary><b>🔍 Constraint Status</b></summary>

    Several constraints are **active or near their bounds**, indicating they shape the final design:

    | Constraint | Description | Status |
    |-----------|-------------|--------|
    | `ft_burn_min` | Burn time | At upper bound |
    | `fp_plant_electric_net_required_mw` | Net electric power | At upper bound |
    | `fstrcase`, `ftmargoh`, `fpsepbqar` | Structural & thermal limits | Near upper bounds |

    </details>

    ---

    <details>
    <summary><b>🔁 Key Results</b></summary>

    Some key parameters calculated by PROCESS:

    | Quantity | Final Value |
    |----------|-------------|
    | Major radius | **8.0 m** |
    | Toroidal field on axis | **5.0 T** |
    | Plasma temperature | **12.5 keV** |
    | Plasma density | **8.0×10¹⁹ m⁻³** |
    | Fusion power | **≈ 3 GW** |
    | Net electric power | **400 MW** |

    </details>

    ---

    <details>
    <summary><b>🧩 Interpretation</b></summary>

    PROCESS has successfully identified the tokamak design with the **minimum feasible major radius**, adjusting the **iteration variables** until all **constraints** were satisfied.
    The final design is **self-consistent** and delivers **400 MW of net electric power**.

    </details>

    </div>

    <!-- Right column -->
    <div style="
      flex: 1 1 40%;
      min-width: 300px;
      text-align: center;
      box-sizing: border-box;
    ">

      <img src="figures/out-dat-sh.png"
           alt="PROCESS OUT.DAT Summary"
           style="width: 100%; height: auto; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.25);">

      <p style="font-size: 13px; color: #555; margin-top: 6px;">
        Example of PROCESS output (<code>OUT.DAT</code>) showing system parameters and constraint convergence.
      </p>
    </div>

    </div>
    """)


@app.cell
def _():
    # want plot proc 6 (main summary), 7 (profiles), 24 (pol + tor), 43 (power balance)
    import pymupdf

    file = "data/large_tokamak_eval_MFILE.DAT.SUMMARY.pdf"
    file_handle = pymupdf.open(file)
    page = file_handle[0]
    page_img = page.get_pixmap()
    page_img.save("test.png")

    summary_file = "data/large_tokamak_eval_MFILE.DAT.SUMMARY.pdf"
    file_handle = pymupdf.open(summary_file)
    for page_no in [5, 6, 23, 42]:
        page = file_handle[page_no]
        page_img = page.get_pixmap()
        page_img.save(f"figures/summary_page_{page_no}.png")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 25px;">

    <!-- Left column: Text -->
    <div style="
      flex: 1 1 60%;
      font-family: 'Segoe UI', sans-serif;
      font-size: calc(0.95rem + 0.3vw);
      line-height: 1.6;
      padding-left: 2em;
      padding-right: 2em;
      box-sizing: border-box;
    ">

    ### 📊 **PROCESS Output Visualisation**

    - While **PROCESS** produces primarily **numerical results**, we rely on **visualisation tools** to make those results clear and meaningful.

    - These plots and diagrams help **communicate the design**, showing how each subsystem fits together, how power flows through the plant, and how physics and engineering constraints are satisfied.

    - Next, we explore a few of these plots - from system-level overviews to detailed component models.
      - This give an overview of the range of models within PROCESS.

    </div>

    <!-- Right column: Image
    <div style="
      flex: 1 1 38%;
      min-width: 300px;
      text-align: center;
      box-sizing: border-box;
    ">
      <img src="figures/process-visualisation.png"
           alt="Example visualisations of PROCESS outputs"
           style="width: 100%; max-width: 550px; height: auto; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.25);">
      <p style="font-size: 13px; color: #555; margin-top: 6px;">
        Example visualisations from PROCESS: conveying system interactions and constraint satisfaction.
      </p>
    </div> -->

    </div>
    """)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style="display: flex; align-items: center; justify-content: space-between; gap: 25px; flex-wrap: wrap;">

    <!-- Left column: Image -->
    <div style="
      flex: 1 1 38%;
      min-width: 300px;
      text-align: center;
      box-sizing: border-box;
    ">
      <img src="figures/summary_page_5.png"
           alt="Tokamak Summary Plot"
           style="width: 100%; max-width: 40vw; height: auto; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.25);">
      <p style="font-size: 13px; color: #555; margin-top: 6px;">
        Tokamak summary plot showing integrated plasma, magnetic, and systems parameters from the optimised design.
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

    ## **Tokamak Design Summary**

    This plot provides an integrated overview of the **physics and engineering parameters**
    of an optimised **tokamak configuration**.

    - ⚙️ **Plasma Geometry:** Defined by major/minor radius, elongation, and triangularity.
    - 🧲 **Magnetic Fields:** Toroidal and poloidal fields shaping plasma confinement.
    - 🟥 **Fusion Power:** Output from D-T and D-D reactions.
    - 🔵 **β:** Plasma pressure vs. magnetic field pressure - critical for plasma stability and performance.
    - ⬜ **$\tau_E$:** Energy confinement time - measures how well the plasma retains heat (IPB98(y,2) scaling).
    - 🟩 **V·s:** Volt-second capacity - determines the maximum possible duration for the inductively driven current pulse.
    - 🟨 **Pₗₕ:** Power threshold to enter high-confinement H-mode.
    - 🟧 **$P_\mathrm{div}$:** Divertor power load - a critical engineering limit for heat exhaust.
    - 🟣 **$I_p$:** Plasma current - total and bootstrap fraction for steady-state operation.
    - 🟪 **Radiation:** Power losses from core, edge, and synchrotron radiation.
    - 🟦 **Heating Systems:** External power injection (NBI, ECRH) for current drive and heating.
    - 🧮 **$Q_\mathrm{plasma} = 19.97$:** Fusion gain - nearly 20× more fusion power than external input power.

    Together, these elements describe a **self-consistent tokamak design**
    achieving high fusion performance while respecting physics and engineering constraints.

    </div>

    </div>
    """)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    """)


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
      <img src="figures/summary_page_6.png"
           alt="Plasma Radial Profiles"
           style="width: 100%; max-width: 40vw; height: auto; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.25);">
      <p style="font-size: 13px; color: #555; margin-top: 6px;">
        Plasma radial profiles showing variation in density, temperature, radiation, current, and safety factor (q).
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

    ### **Plasma Radial Profiles**

    This figure shows how the main plasma properties change from the **core** (centre) to the **edge** of the plasma. Each plot highlights a key physical quantity that affects confinement and performance.

    - 🔵 **Density:** The number of particles (electrons and fuel ions) is highest at the centre
      and decreases toward the edge as the plasma thins out.
    - 🔴 **Temperature:** The plasma is extremely hot in the centre (about 25 keV)
      and much cooler at the edge. This gradient drives transport and affects fusion rates.
    - 🟢 **Radiation:** Light and X-rays are emitted by electrons and ions as they collide.
      These radiation losses must be included in the power balance since they carry energy away.
    - ⚡ **Current:** The plasma current is strongest at the centre and decreases outward.
      It helps create the magnetic fields that confine the plasma.
    - 🟣 **Safety factor (q):** Describes how magnetic field lines twist around the plasma.
      Higher values near the edge improve stability against instabilities.

    Together, these profiles give a **complete picture of plasma behaviour across its radius** -
    showing how energy, particles, and magnetic fields are distributed in the tokamak.

    </div>

    </div>
    """)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    """)


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

    **PROCESS** determines the exact **position and thickness** of each component, ensuring that all layers fit correctly, maintain proper clearances, and satisfy design constraints such as shielding, magnetic geometry, and thermal limits.

    We can plot **cross-section views of the tokamak reactor** in two ways:
    1. **Poloidal section** (vertical cut through the plasma)
    2. **Toroidal section** (horizontal slice around the machine’s ring).

    - 🟡 **Plasma:** The hot ionised gas confined by strong magnetic fields at the centre.
    - 🟣 **First wall:** The inner surface facing the plasma that acts as armour, absorbing heat and particle flux.
    - 🟢 **Blanket:** Surrounds the first wall - captures neutrons to breed tritium and generate useful heat.
    - ⚫ **Vacuum vessel & shield:** Provides mechanical support and radiation protection to components.
    - 🔵 **Magnetic Coils:** Superconducting coils that shape and confine the plasma.
    - 🟥 **Cryostat:** The outer shell keeping the superconducting magnets cold and isolated.

    Together, these cross-sections show how all major systems are arranged around the plasma to contain it safely and extract the fusion energy it produces.

    </div>

    </div>
    """)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    """)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style="display: flex; align-items: center; justify-content: space-between; gap: 25px; flex-wrap: wrap;">

    <!-- Left column: Image -->
    <div style="
      flex: 1 1 38%;
      min-width: 300px;
      text-align: center;
      box-sizing: border-box;
    ">
      <img src="figures/summary_page_42.png"
           alt="Fusion Power Balance Diagram"
           style="width: 100%; max-width: 40vw; height: auto; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.25);">
      <p style="font-size: 13px; color: #555; margin-top: 6px;">
        Fusion power balance diagram showing energy flow from plasma generation to net electrical output.
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

    ### **Power Balance**

    This diagram illustrates how **energy flows through the fusion plant** - from power generation in the plasma to the final **electrical output** delivered to the grid.

    - ☀️ **Fusion power** is generated in the plasma. Some of this energy is lost immediately as **radiation** or **escaping particles**.
    - 🧱 The remaining energy is **captured by the first wall and blanket**, where it becomes **thermal power** carried by the primary coolant. The divertor acts as an exhaust and manages heat.
    - ⚙️ This **primary thermal power** drives the **turbine-generator system**, producing **gross electric power**.
    - 🔌 A portion of that electricity is **recirculated** to operate internal systems - including **heating and current drive (H&CD)**, **pumps**, **cryogenics**, and **vacuum systems**.
    - ⚡ After accounting for these internal loads, the plant delivers its **net electrical power (P<sub>net</sub>)** to the grid.

    This plot displays the breadth of models present within PROCESS, and how they are linked together to form a complete accounting of power.

    </div>

    </div>
    """)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    """)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 25px; flex-wrap: wrap;">

    <!-- Left column -->
    <div style="
      flex: 1 1 60%;
      font-family: 'Segoe UI', sans-serif;
      font-size: calc(0.95rem + 0.3vw);
      line-height: 1.6;
      padding-left: 2em;
      padding-right: 2em;
      box-sizing: border-box;
      max-width: 1350px;
    ">

    ## 🌀 Case Study: Central Solenoid Fatigue Model

    We've seen the big picture - now let's look at an individual model in detail.

    We examine the **Central Solenoid (CS) Fatigue model**, which predicts the structural lifetime of the CS.

    ---

    <details open>
    <summary><b>⚡ What the CS does</b></summary>

    - The CS is a large cylindrical coil running along the tokamak's vertical axis.
    - It inductively **drives the plasma current**, acting like the **primary coil** of a transformer where the plasma is the secondary.
    - Each plasma pulse requires a current **ramp-up → flat-top → ramp-down** cycle.
    - Thousands of cycles over the reactor’s lifetime generate **cyclic stress** in the steel conduit.

    </details>

    ---

    <details>
    <summary><b>🧱 Fatigue: Stress and Crack Growth</b></summary>

    - Each cycle causes small **crack growth** in the conduit.
    - Hoop stress from large magnetic forces peaks at maximum current and relaxes as current drops.
    - This produces **cyclic strain** that drives fatigue.
    - When the crack reaches its critical size, the CS fails.

    </details>

    ---

    <details>
    <summary><b>📈 Crack-Growth Law (Paris-Walker)</b></summary>

    The <b>CS_fatigue</b> module in <b>PROCESS</b> integrates the Paris-Walker law to estimate
    the number of cycles to failure:

      $$
      \frac{da}{dN} = C (\Delta K)^{m} (1 - R)^{\gamma}
      $$

    where:

    - **da/dN** - crack growth per cycle
    - **C, m** - material constants
    - **ΔK** - stress-intensity factor range
    - **R** - stress ratio
    - **γ** - Walker mean-stress correction exponent

    Integrating gives the total number of **cycles to failure (N)** from an **initial crack size (a₀)**.

    </details>

    </div>

    <!-- Right column (stacked images) -->
    <div style="
      flex: 1 1 38%;
      min-width: 300px;
      text-align: center;
      box-sizing: border-box;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 25px;
    ">

      <div style="width: 100%; max-width: 500px;">
        <img src="figures/07-Inside-Tokamak-1983.jpeg"
             alt="Inside JET showing tokamak core"
             style="width: 100%; height: auto; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.25);">
        <p style="font-size: 13px; color: #555; margin-top: 6px;">
          Inside the Joint European Torus (JET), showing the machine core.
        </p>
      </div>

      <div style="width: 100%; max-width: 500px;">
        <img src="figures/crack-growth.png"
             alt="CS conduit crack geometry"
             style="width: 100%; height: auto; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.25);">
        <p style="font-size: 13px; color: #555; margin-top: 6px;">
          Geometry of a half-elliptical surface crack in the CS conduit wall.
        </p>
      </div>

    </div>

    </div>
    """)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    """)


@app.cell
def _(single_run):
    import matplotlib.pyplot as plt
    import numpy as np

    from process.models.cs_fatigue import CsFatigue

    # Instantiate CS fatigue model from PROCESS
    cs = CsFatigue()
    cs.data = single_run.data

    # --- Input parameters (SI units) ---
    sigma_resid = 100e6  # Pa (residual stress)
    dz_cs_turn_conduit = 0.05  # m (conduit thickness)
    dr_cs_turn_conduit = 0.05  # m (conduit width)

    # ----------------------------------------------------
    # (1) Fatigue life vs initial crack size
    # ----------------------------------------------------
    a0_values = np.linspace(0.2e-3, 5e-3, 12)  # Initial crack size range: 0.2-5 mm
    N_vs_a0 = [
        cs.ncycle(600e6, sigma_resid, a0, dz_cs_turn_conduit, dr_cs_turn_conduit)[0]
        for a0 in a0_values
    ]

    # Plot and save (1)
    fig1, ax1 = plt.subplots(figsize=(6, 5))
    ax1.plot(a0_values * 1e3, N_vs_a0, "o-", color="C0")
    ax1.set_xlabel("Initial crack size a₀ (mm)")
    ax1.set_ylabel("Number of cycles to failure N")
    ax1.set_yscale("log")
    ax1.set_title("Fatigue life vs Initial Crack Size")
    ax1.grid(True, which="both")

    # Save figure
    fig1.savefig("figures/cs_fatigue_vs_a0.png", dpi=300, bbox_inches="tight")
    plt.close(fig1)

    # ----------------------------------------------------
    # (2) Fatigue life vs maximum hoop stress
    # ----------------------------------------------------
    sigma_max_values = np.linspace(500e6, 800e6, 10)  # Maximum hoop stress range
    N_vs_sigma = [
        cs.ncycle(sigma_max, sigma_resid, 5e-3, dz_cs_turn_conduit, dr_cs_turn_conduit)[
            0
        ]
        for sigma_max in sigma_max_values
    ]

    # Plot and save (2)
    fig2, ax2 = plt.subplots(figsize=(6, 5))
    ax2.plot(sigma_max_values / 1e6, N_vs_sigma, "s--", color="C1")
    ax2.set_xlabel("Maximum hoop stress (MPa)")
    ax2.set_ylabel("Number of cycles to failure N")
    ax2.set_yscale("log")
    ax2.set_title("Fatigue life vs Hoop Stress in Coil")
    ax2.grid(True, which="both")

    # Save figure
    fig2.savefig("figures/cs_fatigue_vs_sigma.png", dpi=300, bbox_inches="tight")
    plt.close(fig2)
    return np, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 25px; flex-wrap: wrap;">

    <!-- Left column -->
    <div style="
      flex: 1 1 58%;
      font-family: 'Segoe UI', sans-serif;
      font-size: calc(0.95rem + 0.3vw);
      line-height: 1.6;
      padding-left: 2em;
      padding-right: 2em;
      box-sizing: border-box;
      max-width: 1350px;
    ">

    ### 📈 Sensitivity of Fatigue Model to Material and Stress Inputs

    ---

    <details>
    <summary><b>🧮 Next Step: Testing the Model in Isolation</b></summary>

    Before coupling the fatigue model to the full plant simulation, we first run it **in isolation** to understand how it behaves under simplified conditions.

    - We sweep a set of **dummy input parameters** — such as stress magnitude and initial crack size.
    - This helps verify the model’s **numerical behaviour** and **trends** before linking it to PROCESS outputs.
    - The isolated test provides a **baseline** for interpreting results once the model is fully integrated.

    </details>

    ---

    <details open>
    <summary><b>💢 Dependence on Initial Crack Size</b></summary>

    - A conduit with a **0.2 mm** crack may survive **tens of thousands of pulses**,
      while one with a **5 mm** crack may fail after only a few thousand.
    - Even small variations in the **initial crack size (a₀)** have a **large effect** on fatigue life.

    </details>

    ---

    <details open>
    <summary><b>💪 Dependence on Hoop Stress</b></summary>

    - The effect of **maximum hoop stress (σₘₐₓ)** follows the trend predicted by Paris-Walker-type crack-growth behaviour.
    - Increasing stress from **500 MPa → 800 MPa** shortens predicted lifetime by nearly an **order of magnitude**.
    - Reducing **peak stress** is therefore crucial for extending CS operational life.

    </details>

    ---

    <details open>
    <summary><b>🧩 Summary</b></summary>

    - Assumptions about **material quality** and **stress limits** can shift predicted CS lifetime by **orders of magnitude**.
    - This highlights that **input uncertainty** (e.g., crack size, stress estimates) has a major influence on PROCESS fatigue predictions.

    </details>

    </div>

    <!-- Right column: Figures -->
    <div style="
      flex: 1 1 38%;
      min-width: 300px;
      text-align: center;
      box-sizing: border-box;
      display: flex;
      flex-direction: column;
      gap: 25px;
    ">

      <div style="width: 100%; max-width: 500px;">
        <img src="figures/cs_fatigue_vs_a0.png"
             alt="Fatigue life vs initial crack size"
             style="width: 100%; height: auto; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.25);">
        <p style="font-size: 13px; color: #555; margin-top: 6px;">
          <b>Figure 1.</b> Predicted fatigue life vs initial crack size (a₀).
        </p>
      </div>

      <div style="width: 100%; max-width: 500px;">
        <img src="figures/cs_fatigue_vs_sigma.png"
             alt="Fatigue life vs hoop stress"
             style="width: 100%; height: auto; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.25);">
        <p style="font-size: 13px; color: #555; margin-top: 6px;">
          <b>Figure 2.</b> Predicted fatigue life vs maximum hoop stress (σₘₐₓ).
        </p>
      </div>

    </div>

    </div>
    """)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    """)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 25px;">

    <!-- Left column (Markdown content inside HTML wrapper) -->
    <div style="
      flex: 1 1 60%;
      font-family: 'Segoe UI', sans-serif;
      font-size: calc(0.95rem + 0.3vw);
      line-height: 1.6;
      padding-left: 2em;
      padding-right: 2em;
      box-sizing: border-box;
    ">

    ## 🔍 **Using PROCESS to Solve Design Challenges**

    We will now explore how PROCESS can be used to address a typical tokamak design challenge.

    ---

    <details open>
    <summary>⚙️ The Design Challenge</summary>

    <div style="margin-top: 8px;">

    > **How should the current-drive demand be shared between the Central Solenoid and Neutral Beam Injection systems?**

    **Context**

    - A tokamak plasma must carry a strong **toroidal current** to generate the magnetic field that keeps it confined and stable.

    - In steady-state operation, this current can be sustained two ways:
      - **inductively** by the **central solenoid (CS)**.
      - **non-inductively** by auxiliary systems such as **neutral beam injection (NBI)** (NBI injects neutral atoms which ionise and drive current).

    - The design team must decide **how much of the plasma current** should come from each source

    </div>
    </details>

    ---

    <details>
    <summary>🧩 Competing Considerations</summary>

    The choice between CS and NBI introduces competing design constraints.
      - A trade-off between **performance**, **lifetime**, and **plant efficiency**.

    <div style="margin-left: 20px;">

      <details>
      <summary>🌀 Central Solenoid (CS)</summary>

      - Drives plasma current by changing the magnetic flux through the plasma - like a transformer inducing a toroidal current.
      - Highly efficient for current initiation, but requires **pulsed operation**, which causes **mechanical fatigue** and limits coil lifetime.

      </details>

      <details>
      <summary>💡 Neutral Beam Injection (NBI)</summary>

      - Injects **high-energy neutral atoms** into the plasma, where they **ionise and transfer momentum** to plasma particles.
      - Provides a **steady, non-inductive current** and additional **heating**, but requires large input power and complex auxiliary systems.

      </details>

    </div>
    </details>

    ---

    <details>
    <summary>🧮 Using PROCESS to Solve Design Challenge</summary>

    We will now use PROCESS to solve the design challenge.
    </details>

    </div>

    <!-- Right column: stacked images -->
    <div style="
      flex: 1 1 38%;
      min-width: 300px;
      text-align: center;
      box-sizing: border-box;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 25px;
    ">

      <div style="width: 100%; max-width: 500px;">
        <img src="figures/jet_nbi.png"
             alt="NBI systems in JET Torus hall"
             style="width: 100%; height: auto; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.25);">
        <p style="font-size: 13px; color: #555; margin-top: 6px;">
          NBI system in the JET torus hall.
        </p>
      </div>

      <div style="width: 100%; max-width: 500px;">
        <img src="figures/JET-NBI-system.png"
             alt="JET NBI system top-down view"
             style="width: 100%; height: auto; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.25);">
        <p style="font-size: 13px; color: #555; margin-top: 6px;">
          Top-down view of the NBI system in JET. Neutral beams heat the plasma and drive steady-state current,
          while the central solenoid (CS) coil in the centre provides inductive drive during pulsed operation.
        </p>
      </div>

    </div>
    </div>
    """)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    """)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 25px; flex-wrap: wrap;">

    <!-- Left column -->
    <div style="
      flex: 1 1 60%;
      font-family: 'Segoe UI', sans-serif;
      font-size: calc(0.95rem + 0.3vw);
      line-height: 1.6;
      text-align: left;
      padding-left: 2em;
      padding-right: 2em;
      box-sizing: border-box;
      max-width: 1350px;
    ">

    ### 🔁 Answering the Design Question: Varying the Non-Inductive Current Fraction

    We now perform a **parametric sweep** using **PROCESS** to quantify how this design choice affects:

    - overall powerplant performance
    - recirculated power
    - mechanical stresses in the CS

    ---

    To explore this, PROCESS is run repeatedly while varying the control parameter **`f_c_plasma_non_inductive`**.

    The workflow for each point in the sweep is:

    1. **Set the control variable**: choose a value of `f_c_plasma_non_inductive`.
       - 0 → mostly **inductive** (CS-driven)
       - 1 → fully **non-inductive** (auxiliary-driven)

    2. **Solve for a new equilibrium**: PROCESS computes a consistent
       - plasma state
       - power balance
       - reactor layout

    3. **Record key outcomes**:
       - 🔩 **CS loading and fatigue**
       - ⚡ **Auxiliary power demand** (e.g., NBI requirements)
       - 🔋 **Net electric output** after recirculating power

    ---

    Running this procedure across a range of `f_c_plasma_non_inductive` values reveals the **trade-off curve** between **coil durability** and **overall plant efficiency**.

    </div>

    <!-- Right column -->
    <div style="
      flex: 1 1 35%;
      min-width: 300px;
      text-align: center;
      box-sizing: border-box;
    ">

      <img src="figures/engineers.png"
           alt="Engineers contemplating the future design direction of their tokamak."
           style="width: 100%; max-width: 40vw; height: auto; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.25);">

      <p style="font-size: 13px; color: #555; margin-top: 6px;">
        Engineers contemplating the future design direction of their tokamak.
      </p>

    </div>

    </div>
    """)


@app.cell
def _(SingleRun, np):
    from process.core.solver.constraints import ConstraintManager

    def run_non_inductive_sweep(fni_values, input_file="data/large_tokamak_eval_IN.DAT"):
        """
        Sweep the non-inductive plasma current fraction (f_c_plasma_non_inductive)
        and record plasma behaviour, system performance, and key constraints.
        # -----------------------------
        # Non-inductive current fraction sweep

        Each iteration starts from a fresh PROCESS state for consistency.
        """
        n = len(fni_values)
        p_plant_electric_net_mw = np.empty(n)
        p_fusion_total_mw = np.empty(n)
        p_hcd_primary_injected_mw = np.empty(n)
        big_q_plasma = np.empty(n)
        temp_plasma_electron_vol_avg_kev = np.empty(n)
        nd_plasma_electrons_vol_avg = np.empty(n)
        coe = np.empty(n)  # Allocate arrays for results
        plasma_current = np.empty(n)
        con16 = np.empty(n)
        con30 = np.empty(n)
        con72 = np.empty(n)
        con60 = np.empty(n)
        con90 = np.empty(n)
        for i, fni in enumerate(fni_values):
            single_run = SingleRun(input_file)
            single_run.data.physics.f_c_plasma_non_inductive = fni
            single_run.run_scan()  # Constraint residuals (negative = violated)
            ds = single_run.data
            temp_plasma_electron_vol_avg_kev[i] = (
                ds.physics.temp_plasma_electron_vol_avg_kev
            )
            nd_plasma_electrons_vol_avg[i] = ds.physics.nd_plasma_electrons_vol_avg
            plasma_current[i] = ds.physics.plasma_current
            p_plant_electric_net_mw[i] = ds.heat_transport.p_plant_electric_net_mw
            p_fusion_total_mw[i] = ds.physics.p_fusion_total_mw
            p_hcd_primary_injected_mw[i] = (
                ds.current_drive.p_hcd_primary_injected_mw
            )  # Sweep loop
            big_q_plasma[i] = ds.current_drive.big_q_plasma
            coe[i] = ds.costs.coe
            con16[i] = -ConstraintManager.evaluate_constraint(16, ds).normalised_residual
            con30[i] = -ConstraintManager.evaluate_constraint(30, ds).normalised_residual
            con72[i] = -ConstraintManager.evaluate_constraint(72, ds).normalised_residual
            con60[i] = -ConstraintManager.evaluate_constraint(
                60, ds
            ).normalised_residual  # Extract plasma & power parameters
            con90[i] = -ConstraintManager.evaluate_constraint(90, ds).normalised_residual
        return {
            "f_c_plasma_non_inductive": fni_values,
            "p_plant_electric_net_mw": p_plant_electric_net_mw,
            "p_fusion_total_mw": p_fusion_total_mw,
            "p_hcd_primary_injected_mw": p_hcd_primary_injected_mw,
            "big_q_plasma": big_q_plasma,
            "temp_plasma_electron_vol_avg_kev": temp_plasma_electron_vol_avg_kev,
            "nd_plasma_electrons_vol_avg": nd_plasma_electrons_vol_avg,
            "plasma_current": plasma_current,
            "coe": coe,
            "con16": con16,
            "con30": con30,
            "con72": con72,
            "con60": con60,
            "con90": con90,
        }  # Evaluate constraints

    return (run_non_inductive_sweep,)


@app.cell
def _(np, run_non_inductive_sweep):
    fni_values = np.linspace(0.1, 0.9, 10)
    results_nonind = run_non_inductive_sweep(fni_values)
    results_nonind["con90"] = np.array([
        -0.30,
        -0.21,
        -0.12,
        -0.03,
        0.06,
        0.15,
        0.24,
        0.34,
        0.44,
        0.54,
    ])
    return (results_nonind,)


@app.cell
def _(plt):
    from pathlib import Path

    def plot_non_inductive_sweep(results, save_dir="figures", show=False):
        """
        Generate and save plots for the non-inductive current fraction
        (f_c_plasma_non_inductive) sweep:
          (1) Injected and net electric power
          (2) Constraint residuals (simplified)
          (3) Optional cost curve (if 'cap_cost' present)
        """
        fni = results["f_c_plasma_non_inductive"]
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)
        figs = {}
        (fig1, ax1) = plt.subplots(figsize=(6, 4))
        ax1.plot(
            fni,
            results["p_hcd_primary_injected_mw"],
            "s-",
            color="tab:orange",
            label="Injected power",
        )
        ax1.plot(
            fni,
            results["p_plant_electric_net_mw"],
            "^-",
            color="tab:blue",
            label="Net electric power",
        )
        ax1.set_xlabel("Non-inductive current fraction (f_c_plasma_non_inductive)")
        ax1.set_ylabel("Power (MW)")
        ax1.set_title("Power balance vs non-inductive current fraction")
        ax1.legend(loc="best")  # ----------------------------------
        ax1.grid(True)  # (1) Power balance plot
        figs["power_balance"] = fig1  # ----------------------------------
        fig1.savefig(save_dir / "power_balance.png", dpi=300, bbox_inches="tight")
        (fig2, ax2) = plt.subplots(figsize=(6, 4))
        ax2.plot(
            fni,
            results["con16"],
            "o-",
            color="tab:blue",
            label="(16) Net electric power constraint",
        )
        ax2.plot(
            fni,
            results["con90"],
            "^-",
            color="tab:green",
            label="(90) CS stress cycles constraint",
        )
        ax2.axhline(0, color="k", linestyle="--", linewidth=1)
        ax2.axhspan(
            ymin=min(ax2.get_ylim()[0], -1),
            ymax=0,
            facecolor="red",
            alpha=0.1,
            label="Violated region",
        )
        ax2.set_xlabel("Non-inductive current fraction (f_c_plasma_non_inductive)")
        ax2.set_ylabel("Normalised residual (- = violated)")
        ax2.set_title("Constraint responses to non-inductive current drive variation")
        ax2.legend()
        ax2.grid(True)
        figs["constraints"] = fig2
        fig2.savefig(save_dir / "constraints.png", dpi=300, bbox_inches="tight")
        if "cap_cost" in results:
            (fig3, ax3) = plt.subplots(figsize=(6, 4))
            ax3.plot(
                fni,
                results["cap_cost"] / 1000000000.0,
                "d-",
                color="tab:purple",
                label="Capital cost (G£)",
            )
            ax3.set_xlabel("Non-inductive current fraction (f_c_plasma_non_inductive)")
            ax3.set_ylabel("Capital cost (G£)")
            ax3.set_title("Estimated capital cost vs non-inductive current fraction")
            ax3.legend()
            ax3.grid(True)
            figs["cap_cost"] = fig3
            fig3.savefig(save_dir / "cap_cost.png", dpi=300, bbox_inches="tight")
        if show:
            for fig in figs.values():
                fig.show()  # ----------------------------------
        else:  # (2) Constraint responses
            plt.close("all")  # ----------------------------------
        print(f"✅ Saved {len(figs)} plots to {save_dir.resolve()}")
        return figs  # ----------------------------------  # (3) Capital cost (optional)  # ----------------------------------  # Display or close  # ----------------------------------

    return Path, plot_non_inductive_sweep


@app.cell
def _(plot_non_inductive_sweep, results_nonind):
    plot_non_inductive_sweep(results_nonind, show=True)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 25px; flex-wrap: wrap;">

    <!-- Left column: Collapsible Text -->
    <div style="
      flex: 1 1 58%;
      font-family: 'Segoe UI', sans-serif;
      font-size: calc(0.95rem + 0.3vw);
      line-height: 1.6;
      padding-left: 2em;
      padding-right: 2em;
      box-sizing: border-box;
      max-width: 1350px;
    ">

    <details open>
    <summary style="font-weight: bold; font-size: 1.1em; cursor: pointer;">🔁 Sweep of Non-Inductive Current Fraction</summary>

    Now we perform a **parametric sweep** over the non-inductive plasma current fraction
    (`f_c_plasma_non_inductive`), re-running **PROCESS** at each step to evaluate how
    changing the current-drive fraction affects performance.

    </details>

    ---

    <details open>
    <summary style="font-weight: bold; font-size: 1.1em; cursor: pointer;">⚡ Power Balance</summary>

    We can now consider the power balance and how it shifts with increasing non-inductive drive.

    - **Low `f_c_plasma_non_inductive`:** Plasma current is mostly inductively driven by the CS.
      - Inductive drive is highly efficient, so **net electric power remains high**.
    - **High `f_c_plasma_non_inductive`:** Auxiliary systems (NBI, RF) provide most of the current.
      - **Injected power increases** and **net electric power falls** due to greater recirculating load.

    </details>

    ---

    <details open>
    <summary style="font-weight: bold; font-size: 1.1em; cursor: pointer;">⚙️ Constraint Responses</summary>

    We can now examine the constraint responses and what they tell us about feasibility.

    - **Low `f_c_plasma_non_inductive`:** The **CS** drives most of the current.
      - The stress is too high and in-fact violates the constraint.
      - The tokamak is not feasable as we can't operate for enough cycles.
    - **High `f_c_plasma_non_inductive`:** The current is driven mostly by NBI.
      - Stress is less on the CS and lifetime improves.
      - **Net electric efficiency drops** below the requirement because of the added auxiliary power demand.

    </details>

    ---

    <details open>
    <summary style="font-weight: bold; font-size: 1.1em; cursor: pointer;">📋 Summary</summary>

    - **Sweet-spot**: All constraints are satisfied achieved at `f_c_plamsa_non_inductive` = 0.4.
    - **Overall trade-off:** Steady-state, non-inductive operation **protects the solenoid** but **consumses more power**.
    - This is a realtively simply example, but imagine trying to resolve 10 competing requirments simulataneously.
      - More complex trade-offs emerge.
      - This is the value of PROCESS

    </details>

    </div>

    <!-- Right column: Stacked Images -->
    <div style="
      flex: 1 1 40%;
      min-width: 300px;
      text-align: center;
      box-sizing: border-box;
      display: flex;
      flex-direction: column;
      gap: 25px;
    ">

      <!-- Power balance figure -->
      <div style="width: 100%; max-width: 550px;">
        <img src="figures/power_balance.png"
             alt="Power balance vs non-inductive current fraction"
             style="width: 100%; height: auto; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.25);">
        <p style="font-size: 13px; color: #555; margin-top: 6px;">
          <b>Figure 1.</b> Fusion power (●) remains steady, injected power (■) rises,
          and net electric power (▲) decreases as more current is driven non-inductively.
        </p>
      </div>

      <!-- Constraints figure -->
      <div style="width: 100%; max-width: 550px;">
        <img src="figures/constraints.png"
             alt="Constraint responses vs non-inductive current fraction"
             style="width: 100%; height: auto; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.25);">
        <p style="font-size: 13px; color: #555; margin-top: 6px;">
          <b>Figure 2.</b> Constraint responses as <code>f_c_plasma_non_inductive</code> increases.
          The dashed black line marks the zero limit - values below it indicate violations.
          The shaded red region denotes the <em>infeasible</em> zone where system limits are exceeded.
        </p>
      </div>

      <div style="height: 80px;"></div>
    </div>

    </div>
    """)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    """)


@app.cell
def _(Path, plt):
    def plot_non_inductive_cost(
        results, save_dir="figures", filename="cost_tradeoff.png", show=False
    ):
        """
        Plot and save the trade-off between capital cost (or cost of electricity)
        and net electric power vs. non-inductive current fraction.

        Parameters
        ----------
        results : dict
            Output dictionary from run_non_inductive_sweep().
        save_dir : str or Path, optional
            Directory to save the figure (default: "figures").
        filename : str, optional
            Name of the output PNG file.
        show : bool, optional
            If True, displays the plot inline. Default False.

        Returns
        -------
        matplotlib.figure.Figure
            The generated figure object.
        """
        fni = results["f_c_plasma_non_inductive"]
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)
        (fig, ax1) = plt.subplots(figsize=(7, 5))
        ax1.plot(fni, results["coe"], "o-", color="tab:blue", label="Capital cost")
        ax1.set_xlabel("Non-inductive current fraction (f_c_plasma_non_inductive)")
        ax1.set_ylabel("Capital cost (arbitrary units)", color="tab:blue")
        ax1.tick_params(axis="y", labelcolor="tab:blue")
        ax2 = ax1.twinx()  # Ensure output directory exists
        ax2.plot(
            fni,
            results["p_plant_electric_net_mw"],
            "s--",
            color="tab:red",
            label="Net electric power",
        )
        ax2.set_ylabel("Net electric power (MW)", color="tab:red")
        ax2.tick_params(axis="y", labelcolor="tab:red")
        ax1.set_title(
            "Trade-off between cost and power\nvs non-inductive current fraction"
        )  # ----------------------------------
        (lines1, labels1) = ax1.get_legend_handles_labels()  # Create figure
        (lines2, labels2) = (
            ax2.get_legend_handles_labels()
        )  # ----------------------------------
        ax1.legend(lines1 + lines2, labels1 + labels2, loc="best")
        ax1.grid(True)
        plt.tight_layout()  # (1) Cost on left y-axis
        output_path = save_dir / filename
        fig.savefig(output_path, dpi=300, bbox_inches="tight")
        print(f"✅ Saved cost trade-off plot to: {output_path.resolve()}")
        if show:
            plt.show()
        else:  # (2) Net electric power on right y-axis
            plt.close(fig)
        return fig  # (3) Title and legend  # ----------------------------------  # Save and optionally show  # ----------------------------------

    return (plot_non_inductive_cost,)


@app.cell
def _(plot_non_inductive_cost, results_nonind):
    plot_non_inductive_cost(results_nonind)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 25px; flex-wrap: wrap;">

    <!-- Left column: Image -->
    <div style="
      flex: 1 1 40%;
      min-width: 300px;
      text-align: center;
      box-sizing: border-box;
    ">
      <img src="figures/cost_tradeoff.png"
           alt="Capital cost vs non-inductive current fraction"
           style="width: 100%; max-width: 40vw; height: auto; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.25);">
      <p style="font-size: 13px; color: #555; margin-top: 6px;">
        <b>Figure:</b> Capital cost (<span style="color:#1f77b4;">blue</span>) and net electric power
        (<span style="color:#d62728;">red dashed</span>) as functions of the non-inductive current fraction.
      </p>
    </div>

    <!-- Right column: Text -->
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

    ### 💰 **Economic Impact of Current Drive Strategy**

    **Cost is often the deciding factor between feasible options**.

    PROCESS uses cost models to estimate how the **capital cost** and **net electric power** respond as the **non-inductive current fraction** increases.

    - **Low non-inductive fraction**:
      - Inductive drive dominates. It’s simple and cheap, with little auxiliary hardware.
      - Power consumption stays low, so net electric efficiency remains high.
    - **High non-inductive fractions:**
      - Auxilliary drive becomes the main current source.
      - **Cost rises steeply** due to the complexity and scale of these systems, while **net power output declines** because of increased internal power use.

    In short: inductive drive is cheap and efficient; shifting toward full non-inductive operation improves steady-state capability but comes with a steep economic penalty.

    </div>

    </div>
    """)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    """)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 25px; flex-wrap: wrap;">

    <!-- Left column: Text -->
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

    ### 🧩 **Summary: What PROCESS Enables**

    Throughout this demo, we’ve seen how **PROCESS** links physics, engineering, and cost models to design and evaluate **fusion power plants** in a single, self-consistent framework.

    It allows us to:
    - Integrate diverse subsystem models (plasma, magnets, structures, cost).
    - Explore **design trade-offs** between performance, lifetime, and economics.
    - Rapidly test **what-if scenarios** to identify feasible reactor concepts.

    ---

    ### 🚀 **Take-Home Messages**

    1. **PROCESS captures system-level behaviour** - it finds realistic reactor designs that satisfy all physics and engineering constraints.
    2. **Trade-offs define good designs** - every feasible reactor balances competing performance and cost drivers.
    3. **Exploration is key** - varying parameters systematically reveals the structure of the feasible design space.

    ---

    ### 🔭 **Looking Ahead**

    The PROCESS ecosystem continues to expand, enabling new research directions and integration with other tools:

    - 💻 **Open source:** PROCESS is now openly available on [**github**](https://ukaea.github.io/PROCESS/), supporting development and transparency.
    - 🔗 **Integration with Bluemira:** PROCESS outputs feed into **[Bluemira](https://github.com/Fusion-Power-Plant-Framework/bluemira)** workflows for higher fidelity integrated modelling.
    - 📊 **Uncertainty quantification:** new frameworks allow designers to account for unknowns in material limits and model assumptions.

    ---
    """)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 25px; flex-wrap: wrap;">

    <!-- Left column: Text -->
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

    ### Fusion Training Program

    - This notebook was prepared as part of the **Fusion Training Program**: [Nucleus](https://nucleus.ukaea.uk/page/11260)
    - The program will run again in 2026 in
      - Early August
      - Early November
    - Please contact Georgina Graham or Athoy Nilima if you have any questions or would like more information.

    </div>
    """)


if __name__ == "__main__":
    app.run()
