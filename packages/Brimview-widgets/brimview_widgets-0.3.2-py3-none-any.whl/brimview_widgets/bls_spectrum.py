import asyncio
from enum import Enum
import tempfile
import pandas as pd
import panel as pn
import param
import holoviews as hv
from holoviews import streams
import numpy as np
import yaml
import scipy
import inspect
import re

import time
import brimfile as bls
from .models import BlsProcessingModels, MultiPeakModel
from .bls_data_visualizer import BlsDataVisualizer

from .utils import catch_and_notify, safe_get

from panel.widgets.base import WidgetBase
from panel.custom import PyComponent
from .bls_types import bls_param
from .widgets import SwitchWithLabels

from bokeh.models.widgets.tables import HTMLTemplateFormatter


def _convert_numpy(obj):
    """
    Utility function to convert a Dict with numpy object into a Dict with "pure" python object.
    Usefull if you plan on serializing / dumping the dict.
    """
    if isinstance(obj, dict):
        return {k: _convert_numpy(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_numpy(v) for v in obj]
    elif isinstance(obj, np.generic):
        return obj.item()  # Convert NumPy scalar to Python scalar
    else:
        return obj


class FitParam(pn.viewable.Viewer):
    """
    Storing as a sub-parameterized to avoid polluting the main param space
    """

    # TODO: move this as it's own widget ?

    process = param.Boolean(
        default=True,
        label="Auto re-fit when clicking on a new pixel",
        doc="If enabled, the fit will be recomputed when clicking on a new pixel. If disabled, the previous fit will be used.",
        allow_refs=True,
    )

    model = param.Selector(
        objects=BlsProcessingModels.to_param_dict(),
        doc="Select which processing model to use",
        instantiate=True,
        allow_refs=True,
    )

    fitted_parameters = param.DataFrame(
        default=None,
        doc="""Parameters from the fit. This is expected to be in the form:
        {
            "peak_name": {"param1": value1, "param2": value2, ...}, 
            "peak_name2": {...},
            ...
        }""",
    )

    def __init__(self, **params):
        super().__init__(**params)
        # Creating some widget
        self._process_switch = SwitchWithLabels(
            name="",
            value=True,
            label_true="Enable",
            label_false="Disable",
        )
        self.process = self._process_switch.param.value

        self._model_dropdown = pn.widgets.Select.from_param(self.param.model, width=200)

        self._table = pn.widgets.Tabulator(
            self._default_dataframe(),
            show_index=False,
            disabled=False,
            groupby=["Peak"],
            hidden_columns=["Peak", "Description"],
            configuration={
                "groupStartOpen": True  # This makes all groups collapsed initially
            },
            editors={
                # Making sure these 2 columns are not editable
                "Parameter": None,
                "Value": None,
                "Description": None,
                "Lower bound": {"type": "number"},
                "Starting value": {"type": "number"},
                "Upper bound": {"type": "number"},
            },
            groups={
                "Fit constraints (🖉)": ["Lower bound", "Starting value", "Upper bound"]
            },
            formatters={
                "Parameter": HTMLTemplateFormatter(
                    template="""
                    <% if (typeof Description !== "undefined" && Description) { %>
                        <span class="dotted-tooltip" title="<%= Description %>"><%= value %></span>
                    <% } else { %>
                        <span><%= value %></span>
                    <% } %>
                    """
                )
            },
            stylesheets=[
                """
                .dotted-tooltip {
                    border-bottom: 1px dotted #333;  /* dotted underline */
                    cursor: help;                    /* cursor hint */
                }        
                """
            ],
            visible = False
        )

        self._reset_button = pn.widgets.Button(
            name="Reset constraints", button_type="primary", visible=False
        )
        self._reset_button.align = ("start", "end")
        self._reset_button.on_click(self._reset_fitted_parameters)

        # For type annotation
        self.model: BlsProcessingModels
        self.fitted_parameters
        self.process: bool

    def _update_model_widget(self):
        print(self.param.model.objects)
        if len(self.param.model.objects) == 1:
            self._model_dropdown.disabled = True
            self._model_dropdown.description = self.param.model.doc
        else:
            self._model_dropdown.disabled = False
            self._model_dropdown.description = self.param.model.doc

    @pn.depends("_table.value")
    def _test_table_update(self):
        print("table")

    def _reset_fitted_parameters(self, _event):
        self.fitted_parameters = None

    def _default_dataframe(self, with_fitting_constraint: bool = True):
        if with_fitting_constraint:
            return pd.DataFrame(
                {
                    "Parameter": [],
                    "Value": [],
                    "Description": [],
                    "Lower bound": [],
                    "Starting value": [],
                    "Upper bound": [],
                }
            )
        else:
            return pd.DataFrame(
                {
                    "Parameter": [],
                    "Value": [],
                    "Description": [],
                }
            )

    def force_single_model(
        self, model: BlsProcessingModels, tooltip_text: None | str = None
    ):
        self.param.model.objects = {model.label: model}
        self.model = model
        if tooltip_text is not None:
            self.param.model.doc = tooltip_text
        self._update_model_widget()

    @pn.depends(
        "fitted_parameters",
        watch=True,
    )
    def _update_table(self):
        if self.fitted_parameters is None:
            self._table.visible = False
            self._table.value = self._default_dataframe()
            return
        
        self._table.value = self.fitted_parameters
        self._table.visible = True

    def __panel__(self):
        return pn.Card(
            self._process_switch,
            pn.Row(self._model_dropdown, self._reset_button),
            self._table,
            title=self.name,
            margin=5,
            collapsed = True,
        )


class BlsSpectrumVisualizer(WidgetBase, PyComponent):
    """Class to display a spectrum from a pixel in the image."""

    text = param.String(
        default="Click on the image to get pixel coordinates", precedence=-1
    )

    dataset_zyx_coord = param.NumericTuple(
        default=None, length=3, allow_refs=True, doc=""
    )
    busy = param.Boolean(default=False, doc="Is the widget busy?")

    def get_coordinates(self) -> tuple[int, int, int]:
        """
        Returns:
            (z, y, x): as int/pixel coordinates
        """
        z = self.dataset_zyx_coord[0]
        y = self.dataset_zyx_coord[1]
        x = self.dataset_zyx_coord[2]
        return (z, y, x)

    saved_fit = FitParam(name="Saved fit")
    auto_refit = FitParam(name="Auto re-fit")
    # make the auto_refit off by default
    auto_refit._process_switch.value = False

    @pn.depends("auto_refit.model", watch=True)
    def _test_remodel_fit(self):
        print(f"Model fit changed to {self.auto_refit.model}")

    @pn.depends("auto_refit.process", watch=True)
    def _test_model_fit(self):
        print(self.auto_refit.process)

    value = param.ClassSelector(
        class_=bls_param,
        default=None,
        precedence=-1,
        doc="BLS file/data/analysis",
        allow_refs=True,
    )

    results_at_point = param.Dict(label="Result values at this point", precedence=-1)

    def __init__(self, result_plot: BlsDataVisualizer, **params):
        self.spinner = pn.indicators.LoadingSpinner(
            value=False, size=20, name="Idle", visible=True
        )
        self.bls_spectrum_in_image = None
        params["name"] = "Spectrum visualization"
        super().__init__(**params)
        # Watch tap stream updates

        # Reference to the "main" plot_click
        self.dataset_zyx_coord = result_plot.param.dataset_zyx_click

        # Test
        self.value: bls_param = bls_param(
            file=result_plot.param.bls_file,
            data=result_plot.param.bls_data,
            analysis=result_plot.param.bls_analysis,
        )

        # Configure saved_fit widget
        self.saved_fit.force_single_model(
            BlsProcessingModels.Lorentzian, "Using default peak model"
        )

        # Configure autore_fit widget
        self.auto_refit._reset_button.visible = True
        self._set_early_replot_exit(False)

        # Because we're not a pn.Viewer anymore, by default we lost the "card" display
        # so despite us returning a card from __panel__, the shown card didn't match
        # the card display (background color, shadows)
        self.css_classes.append("card")

        # Annoation help
        self.model_fit: BlsProcessingModels

    def _set_early_replot_exit(self, enable):
        self._early_replot_exit = enable

    @catch_and_notify(prefix="<b>Compute fitted curves: </b>")
    def _compute_fitted_curves(self, x_range: np.ndarray, z, y, x):
        if self.saved_fit.process is False:
            return []

        fits = {}
        qts = self.results_at_point
        fit_params = {}
        df_rows = []

        for peak in self.value.analysis.list_existing_peak_types():
            width = safe_get(
                qts,
                bls.Data.AnalysisResults.Quantity.Width.name,
                peak.name,
                default=None,
            )
            shift = safe_get(
                qts,
                bls.Data.AnalysisResults.Quantity.Shift.name,
                peak.name,
                default=None,
            )
            amplitude = safe_get(
                qts,
                bls.Data.AnalysisResults.Quantity.Amplitude.name,
                peak.name,
                default=None,
            )
            offset = safe_get(
                qts,
                bls.Data.AnalysisResults.Quantity.Offset.name,
                peak.name,
                default=None,
            )

            df_rows.append(
                {
                    "Peak": peak.name,
                    "Parameter": "width",
                    "Value": width,
                }
            )
            df_rows.append(
                {
                    "Peak": peak.name,
                    "Parameter": "shift",
                    "Value": shift,
                }
            )
            df_rows.append(
                {
                    "Peak": peak.name,
                    "Parameter": "amplitude",
                    "Value": amplitude,
                }
            )
            df_rows.append(
                {
                    "Peak": peak.name,
                    "Parameter": "offset",
                    "Value": offset,
                }
            )

            if width is None or shift is None or amplitude is None or offset is None:
                pn.state.notifications.warning(
                    f"Skipping peak {peak.name} due to missing parameters: "
                    f"width={width}, shift={shift}, amplitude={amplitude}, offset={offset}"
                )
                continue
            try:
                y_values = self.saved_fit.model.func_with_bls_args(
                    x_range, shift, width, amplitude, offset
                )
                fits[peak.name] = y_values
            except Exception as e:
                pn.state.notifications.error(
                    f"Error computing fit for peak {peak.name}: {e}"
                )
                continue

        self.saved_fit.fitted_parameters = pd.DataFrame(df_rows)
        return fits

    @pn.depends("loading", watch=True)
    def loading_spinner(self):
        """
        Controls an additional spinner UI.
        This goes on top of the `loading` param that comes with panel widgets.

        This is especially usefull in the `panel convert` case,
        because some UI elements can't updated easily (or at least in the same way as `panel serve`).
        In particular, the visible toggle is not always working, and elements inside Rows and Columns sometimes
        don't get updated.
        """
        if self.loading:
            self.spinner.value = True
            self.spinner.name = "Loading..."
            self.spinner.visible = True
        else:
            self.spinner.value = False
            self.spinner.name = "Idle"
            self.spinner.visible = True

    def rewrite_card_header(self, card: pn.Card):
        """
        Changes a bit how the header of the card is displayed.
        We replace the default title by
            [{self.name}     {spinner}]

        With self.name to the left and spinner to the right
        """
        params = {
            "object": f"<h3>{self.name}</h3>" if self.name else "&#8203;",
            "css_classes": card.title_css_classes,
            "margin": (5, 0),
        }
        self.spinner.align = ("end", "center")
        self.spinner.margin = (10, 30)
        header = pn.FlexBox(
            pn.pane.HTML(**params),
            # self.spinner,
            # pn.Spacer(),  # pushes next item to the right
            self.spinner,
            align_content="space-between",
            align_items="center",  # Vertical-ish
            sizing_mode="stretch_width",
            justify_content="space-between",
        )
        # header.styles = {"place-content": "space-between"}
        card.header = header
        card._header_layout.styles = {"width": "inherit"}

    def fitted_curves(self, x_range: np.ndarray, z, y, x):
        print(f"Computing fitted curves at ({time.time()})")
        fits = self._compute_fitted_curves(x_range, z, y, x)
        curves = []
        for fit in fits:
            curves.append(
                hv.Curve((x_range, fits[fit]), label=f"Fitted lorentzian ({fit})").opts(
                    axiswise=True
                )
            )

        return curves

    # TODO: rename to something better
    def auto_refit_and_plot(self, x_range, PSD, frequency, PSD_units, frequency_units):
        if self.auto_refit.process is False:
            return []

        print("Re-fitting curves...")
        # Creating the multipeak model function
        n_peaks = len(self.value.analysis.list_existing_peak_types())
        multi_peak_model = MultiPeakModel(
            base_model=self.auto_refit.model, n_peaks=n_peaks
        )

        # Retrieving paramters from saved fit
        previous_fits = {}
        qts = self.results_at_point
        i = 0
        for peak in self.value.analysis.list_existing_peak_types():
            width = safe_get(
                qts,
                bls.Data.AnalysisResults.Quantity.Width.name,
                peak.name,
                default=0,
            )
            shift = safe_get(
                qts,
                bls.Data.AnalysisResults.Quantity.Shift.name,
                peak.name,
                default=0,
            )
            amplitude = safe_get(
                qts,
                bls.Data.AnalysisResults.Quantity.Amplitude.name,
                peak.name,
                default=0,
            )
            offset = safe_get(
                qts,
                bls.Data.AnalysisResults.Quantity.Offset.name,
                peak.name,
                default=0,
            )

            # Converting to HDF5_BLS_treat naming
            previous_fits[f"b{i}"] = offset
            previous_fits[f"a{i}"] = amplitude
            previous_fits[f"nu0{i}"] = shift
            previous_fits[f"gamma{i}"] = width
            i += 1

        print(f"[TRACE] saved fit: {previous_fits}")

        # If possible, we use existing/previous information for the fit
        # This allows for GUI interaction
        stored_fitted_parameters = {}
        stored_upper_bounds = {}
        stored_starting_values = {}
        stored_lower_bounds = {}
        if self.auto_refit.fitted_parameters is not None:
            rows: pd.DataFrame = self.auto_refit.fitted_parameters
            # Converting from pd.DataFrame into the dict of parameters
            for (
                index,
                row,
            ) in (
                rows.iterrows()
            ):  # TODO: supposedly very slow, probably best to change this (make the model accept dataframes ? )
                peak = row["Peak"]
                param = row["Parameter"]

                stored_fitted_parameters[f"{param}{peak}"] = row["Value"]
                stored_upper_bounds[f"{param}{peak}"] = row["Upper bound"]
                stored_starting_values[f"{param}{peak}"] = row["Starting value"]
                stored_lower_bounds[f"{param}{peak}"] = row["Lower bound"]

        # Checking if what we got is still compatible with what we want
        # (ie parameters for 2 peaks and we want 2 peaks)
        if len(stored_starting_values) == multi_peak_model.n_args:
            # Using the values from the table for the fit
            p0 = multi_peak_model._flatten_kwargs(stored_starting_values)
            lower_bounds = multi_peak_model._flatten_kwargs(stored_lower_bounds)
            upper_bounds = multi_peak_model._flatten_kwargs(stored_upper_bounds)

        else:
            # Using "default" values: values from the saved fit + no bounds
            p0 = multi_peak_model._flatten_kwargs(previous_fits)
            lower_bounds = [-np.inf] * len(p0)
            upper_bounds = [np.inf] * len(p0)

        try:
            # perform fit
            print(
                "[TRACE] scipy.curve_fit called with: \n"
                + f"p0 = {p0} \n"
                + f"lower bounds = {lower_bounds} \n"
                + f"upper bounds = {upper_bounds}"
            )

            popt, pcov = scipy.optimize.curve_fit(
                multi_peak_model.function_flat,
                frequency,
                PSD,
                p0=p0,
                bounds=(lower_bounds, upper_bounds),
            )
            y_fit = multi_peak_model.function_flat(x_range, *popt)

            return [
                hv.Curve((x_range, y_fit), label=f"{multi_peak_model.label}").opts(
                    axiswise=True, line_dash="dotted", color="green", line_width=4
                )
            ]
        except Exception as e:
            # TODO: Make a cleaner way to put some values in storage
            popt = p0
            raise e
        finally:  # Whether the fit fails or not, we want to store the arguments
            arg_description = self.auto_refit.model.arguments_documentation

            # Saving the different informations from the curve_fit as dict
            # we use param.update to update all the variable *at the same time*,
            # and to only trigger the update event once

            fitted_parameters = multi_peak_model.unflatten_args_grouped(popt)
            upper_bounds = multi_peak_model.unflatten_args_grouped(upper_bounds)
            starting_values = multi_peak_model.unflatten_args_grouped(p0)
            lower_bounds = multi_peak_model.unflatten_args_grouped(lower_bounds)
            rows = []
            for name, value in fitted_parameters.items():
                for param_name, param_value in value.items():
                    rows.append(
                        {
                            "Peak": name,
                            "Parameter": param_name,
                            "Value": param_value,
                            "Upper bound": upper_bounds[name][param_name],
                            "Starting value": starting_values[name][param_name],
                            "Lower bound": lower_bounds[name][param_name],
                            "Description": arg_description.get(
                                param_name, "Fitting variable"
                            ),
                        }
                    )

            # To avoid recursion :
            self._set_early_replot_exit(True)
            self.auto_refit.fitted_parameters = pd.DataFrame(rows)
            self._set_early_replot_exit(False)

    @pn.depends("dataset_zyx_coord", watch=True, on_init=False)
    @catch_and_notify(prefix="<b>Retrieve data: </b>")
    def retrieve_point_rawdata(self):
        self.loading = True
        now = time.time()
        print(f"retrieve_point_rawdata at {now:.4f} seconds")

        (z, y, x) = self.get_coordinates()
        if self.value is not None and self.value.data is not None:

            # First updating self.saved_fit.model
            try:
                used_model = self.value.analysis.fit_model
                used_model = BlsProcessingModels.from_brimfile_models(used_model)
                tooltip_text = "The peak model was retrieved from the file's metadata"
            except Exception as e:

                # If the user is not wanting to display the saved_fit, then let's just do this silently
                if self.saved_fit.process:
                    pn.state.notifications.warning(
                        f"<b>Saved fit</b>: Continuing with default peak function <br/> ({e})"
                    )
                used_model = BlsProcessingModels.Lorentzian
                tooltip_text = f"Impossible to use file's metadata to determine the peak model. Using a default peak model instead. \n(Reported error: *{e}*)"

            self.saved_fit.force_single_model(used_model, tooltip_text)

            # Then updating the rest
            self.bls_spectrum_in_image, self.results_at_point = (
                self.value.data.get_spectrum_and_all_quantities_in_image(
                    self.value.analysis, (z, y, x)
                )
            )

        else:
            self.bls_spectrum_in_image = None

        # self.loading = False
        now = time.time()
        print(f"retrieve_point_rawdata at {now:.4f} seconds [done]")
        self.loading = False

    # TODO watch=true for side effect ?
    # Also: self.auto_refit._table.param.watch(plot_spectrum, 'value')
    @pn.depends(
        "results_at_point",
        "saved_fit.process",
        # "saved_fit.model", #this is not user changeable anymore - read from the brimfile instead
        "auto_refit.process",
        "auto_refit.model",
        "auto_refit._table.value",
        "value",
        on_init=False,
    )
    @catch_and_notify(prefix="<b>Plot spectrum: </b>")
    def plot_spectrum(self):
        # Stops recursion - ( plot_spectrum -> auto_refit_and_plot ->self.auto_refit.fitted_parameters -> auto_refit._table.value -> plot_spectrum -> ... )
        # We can't use self.loading, because it'S also set to true by retrieve_point_rawdata, and we have
        # retrieve_point_rawdata -> self.results_at_point -> *this function* and we want that run to be executed
        if self._early_replot_exit:
            return

        self.loading = True
        now = time.time()
        print(f"plot_spectrum at {now:.4f} seconds")
        (z, y, x) = self.get_coordinates()
        # Generate a fake spectrum for demonstration purposes
        curves = []
        if (
            self.value is not None
            and self.value.data is not None
            and self.bls_spectrum_in_image is not None
        ):
            (PSD, frequency, PSD_units, frequency_units) = self.bls_spectrum_in_image
            x_range = np.arange(np.nanmin(frequency), np.nanmax(frequency), 0.1)

            # Try catch clauses, so that an error in one curve doesn't
            # block the others to be displayed
            try:
                if self.saved_fit.process:
                    saved_curves = self.fitted_curves(x_range, z, y, x)
                    curves.extend(saved_curves)
            except Exception as e:
                pn.state.notifications.warning(f"<b>Plot saved fit: </b> {e}")

            try:
                if self.auto_refit.process:
                    refit_curves = self.auto_refit_and_plot(
                        x_range, PSD, frequency, PSD_units, frequency_units
                    )
                    curves.extend(refit_curves)
            except Exception as e:
                pn.state.notifications.warning(f"<b>Auto-refit: </b> {e}")

        else:
            print("Warning: No BLS data available. Cannot plot spectrum.")
            # If no data is available, we create empty values
            (PSD, frequency, PSD_units, frequency_units) = ([], [], "", "")
        print(f"Retrieving spectrum took {time.time() - now:.4f} seconds")
        # Get and plot raw spectrum
        h = [
            hv.Points(
                (frequency, PSD),
                kdims=[
                    hv.Dimension("Frequency", unit=frequency_units),
                    hv.Dimension("PSD", unit=PSD_units),
                ],
                label=f"Acquired points",
            ).opts(color="black", axiswise=True, marker="+", size=10)
            # * hv.Curve((frequency, PSD), label=f"interpolation").opts(
            #     color="black",
            #     axiswise=True,
            # )
        ]

        h.extend(curves)

        print(f"Creating holoview object took {time.time() - now:.4f} seconds")
        self.loading = False

        return hv.Overlay(h).opts(
            axiswise=True,
            legend_position="bottom",
            legend_cols=3,
            responsive=True,
            title=f"Spectrum at index (z={z}, y={y}, x={x})",
        )

    @catch_and_notify(prefix="<b>Export metadata: </b>")
    def _export_experiment_metadata(self) -> str:
        full_metadata = {}
        for type_name, type_dict in (
            self.value.data.get_metadata().all_to_dict().items()
        ):
            full_metadata[type_name] = {}
            # metadata_dict = metadata.to_dict(type)
            for parameter, item in type_dict.items():
                full_metadata[type_name][parameter] = {}
                full_metadata[type_name][parameter]["value"] = item.value
                full_metadata[type_name][parameter]["units"] = item.units

        metadata_dict = {
            "filename": self.value.file.filename,
            "dataset": {
                "name": self.value.data.get_name(),
                "metadata": full_metadata,
            },
        }
        return yaml.dump(metadata_dict, default_flow_style=False, sort_keys=False)

    def _csv_export_header(self):
        metadata = _convert_numpy(self.results_at_point)
        (z, y, x) = self.get_coordinates()
        header = f"Spectrum from a single point (z={z}, y={y}, x={x}).\n"
        header += " ==== Experiment Metadata ==== \n"
        header += self._export_experiment_metadata()
        header += " ==== Spectrum Metadata ==== \n"
        header += yaml.dump(metadata, default_flow_style=False, sort_keys=False)
        header += "\n"
        header = "\n".join(f"# {line}" for line in header.splitlines())
        return header

    @catch_and_notify(prefix="<b>Export CSV: </b>")
    def csv_export(self):
        """
        Create a (temporary) CSV file, with the data from the current plot. This file can then be downloaded.

        The file had a header part (in comment style #), with all the metadata regarding this specific acquisition point.

        Rough stucture:
        ```
        # Spectrum from (z, y, x)
        #
        # {Metadata from the bls file}
        #
        # {Metadata from the specific spectrum}
        frequency, PSD, [fits, ...]
        -5.086766652931395,705.0,537.789088340407,1035.9203244463108
        -5.245067426251495,995.0,537.681849973285,1206.9780168102159
        -5.403368199571595,1372.0,537.5790197104791,1473.234854548628
        ```

        """
        (z, y, x) = self.get_coordinates()

        # Get spectrum data
        if self.value.data is not None:
            PSD, frequency, PSD_unit, freq_unit = self.bls_spectrum_in_image
            fits = self._compute_fitted_curves(frequency, z, y, x)
        else:
            PSD, frequency = np.array([]), np.array([])
            fits = {}

        # Prepare DataFrame
        df = pd.DataFrame(
            {
                "Frequency": frequency,
                "PSD": PSD,
            }
        )
        for fit in fits:
            df[fit] = fits[fit]

        # Create temporary file
        tmp = tempfile.NamedTemporaryFile(
            delete=False, suffix=".csv", mode="w", newline=""
        )
        tmp.write(self._csv_export_header())
        tmp.write("\n")  # Starting at a new line
        # Write CSV
        df.to_csv(tmp, index=False, mode="a")

        # Important: flush so the file is ready
        tmp.flush()
        tmp.seek(0)

        return tmp.name

    def __panel__(self):

        card = pn.Card(
            pn.pane.HoloViews(
                self.plot_spectrum,
                height=300,  # Not the greatest solution
                sizing_mode="stretch_width",
            ),
            pn.widgets.FileDownload(callback=self.csv_export, filename="raw_data.csv"),
            pn.FlexBox(self.auto_refit, self.saved_fit),
            sizing_mode="stretch_height",
        )

        self.rewrite_card_header(card)
        return card
