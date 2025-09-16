import re
from pathlib import Path

from dp_wizard_templates.converters import (
    convert_nb_to_html,
    convert_py_to_nb,
)
from faicons import icon_svg
from htmltools.tags import p
from shiny import Inputs, Outputs, Session, reactive, render, types, ui

from dp_wizard.shiny.components.outputs import (
    hide_if,
    info_md_box,
    tutorial_box,
)
from dp_wizard.types import AppState
from dp_wizard.utils.code_generators import AnalysisPlan, AnalysisPlanColumn
from dp_wizard.utils.code_generators.notebook_generator import (
    PLACEHOLDER_CSV_NAME,
    NotebookGenerator,
)
from dp_wizard.utils.code_generators.script_generator import ScriptGenerator

wait_message = "Please wait."


def button(
    name: str, ext: str, icon: str, primary=False, disabled=False
):  # pragma: no cover
    clean_name = re.sub(r"\W+", " ", name).strip().replace(" ", "_").lower()
    kwargs = {
        "id": f"download_{clean_name}",
        "label": f"Download {name} ({ext})",
        "icon": icon_svg(icon, margin_right="0.5em"),
        "width": "20em",
        "class_": "btn-primary" if primary else None,
    }
    if disabled:
        # Would prefer just to use ui.download_button,
        # but it doesn't have a "disabled" option.
        return ui.input_action_button(
            disabled=True,
            **kwargs,
        )
    return ui.download_button(**kwargs)


def _strip_ansi(e):
    """
    >>> e = Exception('\x1b[0;31mValueError\x1b[0m: ...')
    >>> _strip_ansi(e)
    'ValueError: ...'
    """
    # From https://stackoverflow.com/a/14693789
    import re

    return re.sub(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", str(e))


def make_download_or_modal_error(download_generator):  # pragma: no cover
    try:
        with ui.Progress() as progress:
            progress.set(message=wait_message)
            return download_generator()
    except Exception as e:
        message = _strip_ansi(e)
        modal = ui.modal(
            ui.pre(message),
            title="Error generating code",
            size="xl",
            easy_close=True,
        )
        ui.modal_show(modal)
        raise types.SilentException("code generation")


def results_ui():  # pragma: no cover
    return ui.nav_panel(
        "Download Results",
        ui.output_ui("results_requirements_warning_ui"),
        ui.output_ui("synthetic_data_ui"),
        ui.output_ui("download_results_ui"),
        ui.output_ui("download_code_ui"),
        value="results_panel",
    )


def results_server(
    input: Inputs,
    output: Outputs,
    session: Session,
    state: AppState,
):  # pragma: no cover
    # CLI options:
    # is_sample_csv = state.is_sample_csv
    in_cloud = state.in_cloud
    qa_mode = state.qa_mode

    # Top-level:
    is_tutorial_mode = state.is_tutorial_mode

    # Dataset choices:
    # initial_private_csv_path = state.initial_private_csv_path
    private_csv_path = state.private_csv_path
    # initial_public_csv_path = state.initial_private_csv_path
    public_csv_path = state.public_csv_path
    contributions = state.contributions
    max_rows = state.max_rows

    # Analysis choices:
    # column_names = state.column_names
    groups = state.groups
    epsilon = state.epsilon

    # Per-column choices:
    # (Note that these are all dicts, with the ColumnName as the key.)
    analysis_types = state.analysis_types
    lower_bounds = state.lower_bounds
    upper_bounds = state.upper_bounds
    bin_counts = state.bin_counts
    weights = state.weights
    # analysis_errors = state.analysis_errors

    # Release state:
    is_synthetic_data = state.synthetic_data
    released = state.released

    @render.ui
    def results_requirements_warning_ui():
        return hide_if(
            bool(weights()),
            info_md_box(
                """
                Please define your analysis on the previous tab
                before downloading results.
                """
            ),
        )

    @render.ui
    def synthetic_data_ui():
        return ui.card(
            ui.card_header("Statistics or Synthetic Data?"),
            ui.markdown(
                """
                You can generate either differentially private statistics
                or synthetic data.

                With synthetic data, your privacy budget is used to
                infer the distributions of values within the selected columns,
                and the correlations between columns.
                This is less accurate than calculating the desired
                statistics directly, but can be easier to work with.
                """
            ),
            ui.input_checkbox("is_synthetic_data", "Release synthetic data", False),
        )

    @render.ui
    def download_results_ui():
        if in_cloud:
            return None
        disabled = not weights()
        return [
            ui.h3("Download Results"),
            tutorial_box(
                is_tutorial_mode(),
                """
                Now you can download a notebook for your analysis.
                The Jupyter notebook could be used locally or on Colab,
                but the HTML version can be viewed in the brower.
                """,
            ),
            # Find more icons on Font Awesome: https://fontawesome.com/search?ic=free
            ui.accordion(
                ui.accordion_panel(
                    "Notebooks",
                    button(
                        "Notebook", ".ipynb", "book", primary=True, disabled=disabled
                    ),
                    p(
                        """
                        An executed Jupyter notebook which references your CSV
                        and shows the result of a differentially private analysis.
                        """
                    ),
                    button("HTML", ".html", "file-code", disabled=disabled),
                    p("The same content, but exported as HTML."),
                ),
                ui.accordion_panel(
                    "Reports",
                    button(
                        "Report", ".txt", "file-lines", primary=True, disabled=disabled
                    ),
                    p(
                        """
                        A report which includes your parameter choices and the results.
                        Intended to be human-readable, but it does use YAML,
                        so it can be parsed by other programs.
                        """
                    ),
                    button("Table", ".csv", "file-csv", disabled=disabled),
                    p("The same information, but condensed into a CSV."),
                ),
            ),
        ]

    @render.ui
    def download_code_ui():
        disabled = not weights()
        return [
            ui.h3("Download Code"),
            tutorial_box(
                is_tutorial_mode(),
                (
                    """
                    When [installed and run
                    locally](https://pypi.org/project/dp_wizard/),
                    there are more download options because DP Wizard
                    can read your private CSV and release differentially
                    private statistics.

                    In the cloud, DP Wizard only provides unexecuted
                    notebooks and scripts.
                    """
                    if in_cloud
                    else """
                    Alternatively, you can download a script or unexecuted
                    notebook that demonstrates the steps of your analysis,
                    but does not contain any data or analysis results.
                    """
                ),
            ),
            ui.accordion(
                ui.accordion_panel(
                    "Unexecuted Notebooks",
                    [
                        button(
                            "Notebook (unexecuted)",
                            ".ipynb",
                            "book",
                            primary=True,
                            disabled=disabled,
                        ),
                        p(
                            """
                            An unexecuted Jupyter notebook which shows the steps
                            in a differentially private analysis.
                            It can also be updated with the path
                            to a private CSV and executed locally.
                            """
                            if in_cloud
                            else """
                            This contains the same code as Jupyter notebook above,
                            but none of the cells are executed,
                            so it does not contain any results.
                            """
                        ),
                        button(
                            "HTML (unexecuted)", ".html", "file-code", disabled=disabled
                        ),
                        p("The same content, but exported as HTML."),
                    ],
                ),
                ui.accordion_panel(
                    "Scripts",
                    button("Script", ".py", "python", primary=True, disabled=disabled),
                    p(
                        """
                        The same code as the notebooks, but extracted into
                        a Python script which can be run from the command line.
                        """
                    ),
                    button("Notebook Source", ".py", "python", disabled=disabled),
                    p(
                        """
                        Python source code converted by jupytext into notebook.
                        Primarily of interest to DP Wizard developers.
                        """
                    ),
                ),
                # If running locally, we do not want it open by default.
                # https://shiny.posit.co/py/api/core/ui.accordion.html#shiny.ui.accordion
                # > The default value of None will open the first accordion_panel.
                # > Use a value of True to open all (or False to open none)
                # > of the items.
                open=None if in_cloud else False,
            ),
        ]

    @reactive.effect
    @reactive.event(input.is_synthetic_data)
    def _on_is_synthetic_data_change():
        is_synthetic_data.set(input.is_synthetic_data())

    @reactive.calc
    def analysis_plan() -> AnalysisPlan:
        # weights().keys() will reflect the desired columns:
        # The others retain inactive columns, so user
        # inputs aren't lost when toggling checkboxes.
        columns = {
            col: [
                AnalysisPlanColumn(
                    analysis_name=analysis_types()[col],
                    lower_bound=lower_bounds()[col],
                    upper_bound=upper_bounds()[col],
                    bin_count=int(bin_counts()[col]),
                    weight=int(weights()[col]),
                )
            ]
            for col in weights().keys()
        }
        return AnalysisPlan(
            is_synthetic_data=is_synthetic_data(),
            # Prefer private CSV, if available:
            csv_path=private_csv_path() or public_csv_path() or PLACEHOLDER_CSV_NAME,
            contributions=contributions(),
            epsilon=epsilon(),
            max_rows=int(max_rows()),
            groups=groups(),
            columns=columns,
        )

    @reactive.calc
    def download_stem() -> str:
        return analysis_plan().to_stem()

    @reactive.calc
    def notebook_nb():
        # This creates the notebook, and evaluates it,
        # and drops reports in the tmp dir.
        # Could be slow!
        # Luckily, reactive calcs are lazy.
        released.set(True)
        plan = analysis_plan()
        notebook_py = (
            "raise Exception('qa_mode!')"
            if qa_mode
            else NotebookGenerator(plan).make_py()
        )
        return convert_py_to_nb(notebook_py, title=str(plan), execute=True)

    @reactive.calc
    def notebook_nb_unexecuted():
        plan = analysis_plan()
        notebook_py = NotebookGenerator(plan).make_py()
        return convert_py_to_nb(notebook_py, title=str(plan), execute=False)

    @reactive.calc
    def notebook_html():
        return convert_nb_to_html(notebook_nb())

    @reactive.calc
    def notebook_html_unexecuted():
        return convert_nb_to_html(notebook_nb_unexecuted())

    @render.download(
        filename=lambda: download_stem() + ".py",
        media_type="text/x-python",
    )
    async def download_script():
        yield make_download_or_modal_error(ScriptGenerator(analysis_plan()).make_py)

    @render.download(
        filename=lambda: download_stem() + ".ipynb.py",
        media_type="text/x-python",
    )
    async def download_notebook_source():
        with ui.Progress() as progress:
            progress.set(message=wait_message)
            yield NotebookGenerator(analysis_plan()).make_py()

    @render.download(
        filename=lambda: download_stem() + ".ipynb",
        media_type="application/x-ipynb+json",
    )
    async def download_notebook():
        yield make_download_or_modal_error(notebook_nb)

    @render.download(
        filename=lambda: download_stem() + ".unexecuted.ipynb",
        media_type="application/x-ipynb+json",
    )
    async def download_notebook_unexecuted():
        yield make_download_or_modal_error(notebook_nb_unexecuted)

    @render.download(  # pyright: ignore
        filename=lambda: download_stem() + ".html",
        media_type="text/html",
    )
    async def download_html():
        yield make_download_or_modal_error(notebook_html)

    @render.download(  # pyright: ignore
        filename=lambda: download_stem() + ".unexecuted.html",
        media_type="text/html",
    )
    async def download_html_unexecuted():
        yield make_download_or_modal_error(notebook_html_unexecuted)

    @render.download(
        filename=lambda: download_stem() + ".txt",
        media_type="text/plain",
    )
    async def download_report():
        def make_report():
            notebook_nb()  # Evaluate just for the side effect of creating report.
            return (Path(__file__).parent.parent / "tmp" / "report.txt").read_text()

        yield make_download_or_modal_error(make_report)

    @render.download(
        filename=lambda: download_stem() + ".csv",
        media_type="text/csv",
    )
    async def download_table():
        def make_table():
            notebook_nb()  # Evaluate just for the side effect of creating report.
            return (Path(__file__).parent.parent / "tmp" / "report.csv").read_text()

        yield make_download_or_modal_error(make_table)
