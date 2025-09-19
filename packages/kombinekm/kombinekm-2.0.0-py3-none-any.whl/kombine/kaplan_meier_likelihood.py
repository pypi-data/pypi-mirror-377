"""
Kaplan-Meier curve with error bars calculated using the log-likelihood method.
"""

import collections.abc
import dataclasses
import datetime
import functools
import os
import typing
import pathlib

import matplotlib.axes
import matplotlib.figure
import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
import scipy.optimize
import scipy.stats

from .discrete_optimization import binary_search_sign_change
from .kaplan_meier import (
  KaplanMeierBase,
  KaplanMeierInstance,
)
from .kaplan_meier_MINLP import MINLPForKM, KaplanMeierPatientNLL
from .utilities import InspectableCache, LOG_ZERO_EPSILON_DEFAULT

@dataclasses.dataclass
class KaplanMeierPlotConfig:  #pylint: disable=too-many-instance-attributes
  """
  Configuration for Kaplan-Meier likelihood plots.

  Attributes:
  times_for_plot: Sequence of time points for plotting the survival probabilities.
  include_binomial_only: If True, include error bands for the binomial error alone.
  include_greenwood: If True, include error bands for the binomial error
                     using the exponential Greenwood method.
  include_patient_wise_only: If True, include error bands for the patient-wise error alone.
  include_full_NLL: If True, include error bands for the full negative log-likelihood.
  include_best_fit: If True, include the best fit curve in the plot.
  include_nominal: If True, include the nominal Kaplan-Meier curve.
  nominal_label: Label for the nominal curve.
  nominal_color: Color for the nominal curve.
  best_label: Label for the best fit curve.
  best_color: Color for the best fit curve.
  patient_wise_only_suffix: Suffix for the patient-wise only error bands.
  binomial_only_suffix: Suffix for the binomial-only error bands.
  full_NLL_suffix: Suffix for the full NLL error bands.
  exponential_greenwood_suffix: Suffix for the exponential Greenwood error bands.
  CLs: List of confidence levels for the error bands.
  CL_colors: List of colors for the confidence levels.
  CL_colors_greenwood: List of colors for the Greenwood confidence levels.
  CL_hatches: List of hatches for the confidence levels
              for the binomial-only or patient-wise-only error bands.
  create_figure: If True, create a new matplotlib figure for the plot.
  close_figure: If True, close the figure after saving or showing.
  show: If True, display the plot.
  saveas: Path to save the plot image.
  legend_saveas: Path to save the legend separately, or None.
                 If provided, the legend will be left off the main plot.
  print_progress: If True, print progress messages during calculations.
  MIPGap: Relative MIP gap for the optimization solver.
  MIPGapAbs: Absolute MIP gap for the optimization solver.
  include_median_survival: If True, include the median survival time in the legend.
  title: Title for the plot.
  xlabel: Label for the x-axis.
  ylabel: Label for the y-axis.
  show_grid: If True, display a grid on the plot.
  figsize: Size of the figure as a tuple (width, height).
  tight_layout: If True, use tight layout for the plot.
  legend_fontsize: Font size for the legend.
  label_fontsize: Font size for the axis labels.
  title_fontsize: Font size for the plot title.
  tick_fontsize: Font size for the tick labels.
  legend_loc: Location of the legend in the plot.
  dpi: Dots per inch for the figure resolution.
  pvalue_fontsize: Font size for the p-value text.
  pvalue_format: Format string for p-value display (e.g., '.3g', '.2f').
  """
  times_for_plot: typing.Sequence[float] | None = None
  include_binomial_only: bool = False
  include_exponential_greenwood: bool = False
  include_patient_wise_only: bool = False
  include_full_NLL: bool = True
  include_best_fit: bool = True
  include_nominal: bool = True
  nominal_label: str = 'Nominal'
  nominal_color: str = 'red'
  best_label: str = 'Best Fit'
  best_color: str = 'blue'
  patient_wise_only_suffix: str = 'Patient-wise only'
  binomial_only_suffix: str = 'Binomial only'
  full_NLL_suffix: str = ''
  exponential_greenwood_suffix: str = 'Binomial only, exp. Greenwood'
  CLs: list[float] = dataclasses.field(default_factory=lambda: [0.68, 0.95])
  CL_colors: list[str] = dataclasses.field(
    default_factory=lambda: ['dodgerblue', 'skyblue', 'lightblue', 'lightcyan']
  )
  CL_colors_greenwood: list[str] = dataclasses.field(
    default_factory=lambda: ['darkorange', 'gold', 'khaki', 'lightyellow']
  )
  CL_hatches: list[str] = dataclasses.field(
    default_factory=lambda: ['//', '\\\\', 'xx', '++']
  )
  create_figure: bool = True
  close_figure: bool | None = None
  show: bool = False
  saveas: os.PathLike | str | None = None
  legend_saveas: os.PathLike | str | None = None
  print_progress: bool = False
  MIPGap: float | None = None
  MIPGapAbs: float | None = None
  include_median_survival: bool = False
  title: str | None = "Kaplan-Meier Curves"
  xlabel: str = "Time"
  ylabel: str = "Survival Probability"
  show_grid: bool = True
  figsize: tuple[float, float] = (10, 7)
  tight_layout: bool = True
  legend_fontsize: int = 10
  label_fontsize: int = 12
  title_fontsize: int = 14
  tick_fontsize: int = 10
  legend_loc: str | None = None
  dpi: int = 100
  pvalue_fontsize: int = 12
  pvalue_format: str = '.3g'

  def __post_init__(self):
    """
    Post-initialization validation and default adjustments.
    """
    if self.include_binomial_only and self.include_patient_wise_only:
      raise ValueError("include_binomial_only and include_patient_wise_only cannot both be True")
    if not (
      self.include_binomial_only
      or self.include_patient_wise_only
      or self.include_full_NLL
      or self.include_exponential_greenwood
    ):
      raise ValueError(
        "At least one of include_binomial_only, include_patient_wise_only, "
        "include_full_NLL, or include_greenwood must be True"
      )
    if len(self.CLs) > len(self.CL_colors):
      raise ValueError(
        f"Not enough colors provided for {len(self.CLs)} CLs, "
        f"got {len(self.CL_colors)} colors"
      )
    self.CL_colors = self.CL_colors[:len(self.CLs)]

    if (
      len(self.CLs) > len(self.CL_hatches)
      and self.include_full_NLL
      and (self.include_binomial_only or self.include_patient_wise_only)
    ):
      raise ValueError(
        f"Not enough hatches provided for {len(self.CLs)} CLs, "
        f"got {len(self.CL_hatches)} hatches"
      )
    self.CL_hatches = self.CL_hatches[:len(self.CLs)]

class KaplanMeierLikelihood(KaplanMeierBase):
  """
  Kaplan-Meier curve with error bars calculated using the log-likelihood method.
  """
  __default_MIPGap = 1e-4
  __default_MIPGapAbs = 1e-7

  def __init__( # pylint: disable=too-many-arguments
    self,
    *,
    all_patients: list[KaplanMeierPatientNLL],
    parameter_min: float,
    parameter_max: float,
    endpoint_epsilon: float = 1e-6,
    log_zero_epsilon: float = LOG_ZERO_EPSILON_DEFAULT,
    collapse_consecutive_deaths: bool = True,
  ):
    self.__all_patients = all_patients
    self.__parameter_min = parameter_min
    self.__parameter_max = parameter_max
    self.__endpoint_epsilon = endpoint_epsilon
    self.__log_zero_epsilon = log_zero_epsilon
    self.__collapse_consecutive_deaths = collapse_consecutive_deaths

  @property
  def all_patients(self) -> list[KaplanMeierPatientNLL]:
    """
    The list of all patients.
    """
    return self.__all_patients

  @property
  def parameter_min(self) -> float:
    """
    The minimum parameter value.
    """
    return self.__parameter_min

  @property
  def parameter_max(self) -> float:
    """
    The maximum parameter value.
    """
    return self.__parameter_max

  @property
  def patient_death_times(self) -> frozenset:
    """
    The survival times of the patients who died.
    (excludes censored patients)
    """
    return frozenset(p.time for p in self.all_patients if not p.censored)
  @property
  def patient_censored_times(self) -> frozenset:
    """
    The survival times of the patients who were censored.
    """
    return frozenset(p.time for p in self.all_patients if p.censored)

  @functools.cached_property
  def nominalkm(self) -> KaplanMeierInstance:
    """
    The nominal Kaplan-Meier curve.
    """
    return KaplanMeierInstance(
      all_patients=[p.nominal for p in self.all_patients],
      parameter_min=self.parameter_min,
      parameter_max=self.parameter_max,
    )

  def minlp_for_km(
    self,
    time_point: float,
  ):
    """
    Get the MINLP for the given time point.
    """
    return MINLPForKM(
      all_patients=self.all_patients,
      parameter_min=self.parameter_min,
      parameter_max=self.parameter_max,
      time_point=time_point,
      endpoint_epsilon=self.__endpoint_epsilon,
      log_zero_epsilon=self.__log_zero_epsilon,
      collapse_consecutive_deaths=self.__collapse_consecutive_deaths,
    )

  def get_twoNLL_function( # pylint: disable=too-many-arguments
    self,
    time_point: float,
    *,
    binomial_only=False,
    patient_wise_only=False,
    verbose=False,
    print_progress=False,
    MIPGap=None,
    MIPGapAbs=None,
  ) -> tuple[
    collections.abc.Callable[[float | None], scipy.optimize.OptimizeResult],
    collections.abc.Callable[[float | None], float],
  ]:
    """
    Get the twoNLL function for the given time point.
    """
    if MIPGap is None:
      MIPGap = self.__default_MIPGap
    if MIPGapAbs is None:
      MIPGapAbs = self.__default_MIPGapAbs

    minlp = self.minlp_for_km(time_point=time_point)
    @InspectableCache
    def run_MINLP(expected_probability: float | None) -> scipy.optimize.OptimizeResult:
      """
      Run the MINLP for the given expected probability.
      """
      return minlp.run_MINLP(
        expected_probability=expected_probability,
        binomial_only=binomial_only,
        patient_wise_only=patient_wise_only,
        verbose=verbose,
        print_progress=print_progress,
        MIPGap=MIPGap,
        MIPGapAbs=MIPGapAbs,
      )
    @InspectableCache
    def twoNLL(expected_probability: float | None) -> float:
      """
      The negative log-likelihood function.
      """
      result = run_MINLP(expected_probability)
      if not result.success:
        return np.inf
      return result.x
    return run_MINLP, twoNLL

  def calculate_possible_probabilities(self, time_point: float) -> np.ndarray:
    """
    Get the possible probabilities for the given patients.
    """
    return np.array(sorted(self.minlp_for_km(time_point).possible_probabilities))

  @functools.cached_property
  def __possible_probabilities(self) -> dict[float, np.ndarray]:
    return {}

  def possible_probabilities(self, time_point: float) -> np.ndarray:
    """
    Get the possible probabilities for the given time point.
    This is a cached property to avoid recalculating the probabilities multiple times.
    """
    if time_point not in self.__possible_probabilities:
      self.__possible_probabilities[time_point] = self.calculate_possible_probabilities(time_point)
    return self.__possible_probabilities[time_point]

  def best_probability( #pylint: disable=too-many-arguments
    self,
    run_MINLP: collections.abc.Callable[[float | None], scipy.optimize.OptimizeResult],
    time_point: float | None = None,
  ) -> tuple[float, float]:
    """
    Find the expected probability that minimizes the negative log-likelihood
    for the given time point.
    """
    result = run_MINLP(None)
    if not result.success:
      raise RuntimeError(
        f"Failed to find the best probability for time point {time_point}"
      )
    best_prob = result.km_probability
    twoNLL_min = result.x
    if not 0 <= best_prob <= 1:
      raise ValueError(
        f"Best probability {best_prob} is not in [0, 1] for time point {time_point}"
      )
    return best_prob, twoNLL_min

  def survival_probabilities_exponential_greenwood(
    self,
    CLs: list[float],
    times_for_plot: typing.Sequence[float],
    *,
    binomial_only=False,
    patient_wise_only=False,
  ):
    """
    Calculate the survival probabilities using the exponential Greenwood method.
    """
    if patient_wise_only or not binomial_only:
      raise ValueError(
        "Exponential Greenwood confidence intervals"
        "can only include the binomial error"
      )
    return self.nominalkm.survival_probabilities_exponential_greenwood(
      CLs=CLs,
      times_for_plot=times_for_plot,
    )

  def survival_probabilities_likelihood( # pylint: disable=too-many-locals, too-many-branches, too-many-statements, too-many-arguments
    self,
    CLs: list[float],
    times_for_plot: typing.Sequence[float],
    *,
    binomial_only=False,
    patient_wise_only=False,
    gurobi_verbose=False,
    optimize_verbose=False,
    print_progress=False,
    MIPGap=None,
    MIPGapAbs=None,
  ) -> tuple[np.ndarray, np.ndarray]:
    """
    Get the survival probabilities for the given quantiles.
    
    Parameters
    ----------
    CLs : list[float]
        Confidence levels for the survival probabilities
    times_for_plot : sequence of float
        Time points for which to calculate survival probabilities
    binomial_only : bool, default False
        If True, only use binomial constraints
    patient_wise_only : bool, default False  
        If True, only use patient-wise constraints
    gurobi_verbose : bool, default False
        If True, enable verbose Gurobi output
    optimize_verbose : bool, default False
        If True, enable verbose optimization output
    print_progress : bool, default False
        If True, print progress information
    MIPGap : float, optional
        Gurobi MIP gap tolerance (used for objective function tolerance)
    MIPGapAbs : float, optional
        Gurobi absolute MIP gap tolerance (used for objective function tolerance)
        
    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        Best probabilities and survival probabilities for each confidence level
    """
    # Set default tolerance values if not provided
    if MIPGap is None:
      MIPGap = self.__default_MIPGap
    if MIPGapAbs is None:
      MIPGapAbs = self.__default_MIPGapAbs

    best_probabilities = []
    survival_probabilities = []
    for i, t in enumerate(times_for_plot, start=1):
      if print_progress:
        print(
          f"Calculating survival probabilities for time point {t:.2f} "
          f"({i} / {len(times_for_plot)}) at time {datetime.datetime.now()}"
        )
      survival_probabilities_time_point = []
      survival_probabilities.append(survival_probabilities_time_point)
      run_MINLP, twoNLL = self.get_twoNLL_function(
        time_point=t,
        binomial_only=binomial_only,
        patient_wise_only=patient_wise_only,
        verbose=gurobi_verbose,
        print_progress=print_progress,
        MIPGap=MIPGap,
        MIPGapAbs=MIPGapAbs,
      )
      # Find the expected probability that minimizes the negative log-likelihood
      # for the given time point
      try:
        best_prob, twoNLL_min = self.best_probability(
          run_MINLP=run_MINLP,
          time_point=t,
        )
      except Exception as e:
        raise RuntimeError(
          f"Failed to find the best probability for time point {t}"
        ) from e
      best_probabilities.append(best_prob)
      if patient_wise_only:
        best_prob_clipped = best_prob
      else:
        best_prob_clipped = np.clip(
          best_prob,
          self.__endpoint_epsilon,
          1 - self.__endpoint_epsilon,
        )

      for CL in CLs:
        if patient_wise_only and t < min(self.patient_death_times):
          # If the time point is outside the range of patient times, we cannot
          # calculate a patient-wise survival probability.
          survival_probabilities_time_point.append((1, 1))
          continue

        d2NLLcut = scipy.stats.chi2.ppf(CL, 1).item()
        def objective_function(
          expected_probability: float,
          twoNLL=twoNLL, twoNLL_min=twoNLL_min, d2NLLcut=d2NLLcut
        ) -> float:
          return twoNLL(expected_probability) - twoNLL_min - d2NLLcut
        if best_prob == best_prob_clipped:
          #only do this if it's not too close to the edge
          #to avoid edge effects
          np.testing.assert_allclose(
            objective_function(
              best_prob
            ),
            -d2NLLcut,
            atol=1e-2,
          )

        if patient_wise_only:
          probs = self.possible_probabilities(time_point=t)
          #Explicitly add best_prob to the probabilities
          #It should be there already, but sometimes isn't due to numerical issues
          if best_prob not in probs:
            probs = np.append(probs, best_prob)
            probs = np.sort(probs)
          i_best = int(np.searchsorted(probs, best_prob))
          np.testing.assert_equal(
            probs[i_best],
            best_prob,
            err_msg=f"Best probability {best_prob} not found in possible probabilities {probs}",
          )

          # Check edge case: upper bound
          if objective_function(probs[-1]) < 0:
            upper_bound = 1
          else:
            upper = binary_search_sign_change(
              objective_function=objective_function,
              probs=probs,
              lo=i_best,
              hi=len(probs) - 1,
              verbose=optimize_verbose,
              MIPGap=MIPGap,
              MIPGapAbs=MIPGapAbs,
            )
            if upper is None:
              raise RuntimeError("No upper sign change found")
            upper_bound = upper

          # Check edge case: lower bound
          if objective_function(probs[0]) < 0:
            lower_bound = 0
          else:
            lower = binary_search_sign_change(
              objective_function=objective_function,
              probs=probs,
              lo=0,
              hi=i_best,
              verbose=optimize_verbose,
              MIPGap=MIPGap,
              MIPGapAbs=MIPGapAbs,
            )
            if lower is None:
              raise RuntimeError("No lower sign change found")
            lower_bound = lower

        else:
          if (
            best_prob <= self.__endpoint_epsilon
            or objective_function(self.__endpoint_epsilon) < 0
          ):
            lower_bound = 0
          elif objective_function(best_prob_clipped) >= 0:
            lower_bound = best_prob_clipped
          else:
            lower_bound = scipy.optimize.brentq(
              objective_function,
              self.__endpoint_epsilon,
              best_prob_clipped,
              xtol=MIPGapAbs,
              rtol=np.float64(MIPGap),
            )
          if (
            best_prob >= 1 - self.__endpoint_epsilon
            or objective_function(1 - self.__endpoint_epsilon) < 0
          ):
            upper_bound = 1
          elif objective_function(best_prob_clipped) >= 0:
            upper_bound = best_prob_clipped
          else:
            upper_bound = scipy.optimize.brentq(
              objective_function,
              best_prob_clipped,
              1 - self.__endpoint_epsilon,
              xtol=MIPGapAbs,
              rtol=np.float64(MIPGap),
            )

        survival_probabilities_time_point.append((lower_bound, upper_bound))
    return np.array(best_probabilities), np.array(survival_probabilities)

  def plot(self, config: KaplanMeierPlotConfig | None = None, **kwargs) -> dict:
    """
    Plots the Kaplan-Meier curves based on the provided configuration.
    """
    if config is None:
      config = KaplanMeierPlotConfig(**kwargs)
    elif kwargs:
      # If config is provided and kwargs are also given, update config with kwargs
      config = dataclasses.replace(config, **kwargs)
    # Use config.times_for_plot, falling back to self.times_for_plot if None
    times_for_plot = config.times_for_plot
    if times_for_plot is None:
      times_for_plot = self.times_for_plot

    fig, ax = self._prepare_figure(config)

    # Plot nominal curve and censored points
    results: dict[str, npt.NDArray[np.float64]] = self._plot_nominal(ax, config, times_for_plot)

    # Calculate and plot confidence bands and best fit curve
    results.update(self._calculate_and_plot_confidence_bands(ax, config, times_for_plot))

    self._plot_censored(
      ax,
      config,
      results["x"],
      results["nominal"] if config.include_nominal else results["best_fit"],
    )

    # Finalize plot elements (legend, labels, grid, save/show/close)
    self._finalize_plot(fig, ax, config)

    # Return results for further inspection if needed
    return results

  def _prepare_figure(
    self,
    config: KaplanMeierPlotConfig,
  ) -> tuple[matplotlib.figure.Figure, matplotlib.axes.Axes]:
    """Prepares the matplotlib figure and axes."""
    if config.create_figure:
      fig, ax = plt.subplots(figsize=config.figsize, dpi=config.dpi)
    else:
      fig = plt.gcf() # Get current figure
      ax = plt.gca() # Get current axes if figure already exists
    return fig, ax

  def _plot_nominal(
    self,
    ax: matplotlib.axes.Axes,
    config: KaplanMeierPlotConfig,
    times_for_plot: typing.Sequence[float],
  ):
    """Plots the nominal Kaplan-Meier curve and censored patient markers."""
    nominal_x, nominal_y = self.nominalkm.points_for_plot(times_for_plot=times_for_plot)
    label = config.nominal_label
    if config.include_median_survival:
      MST = self.nominalkm.median_survival_time(
        times_for_plot=nominal_x,
        survival_probabilities=nominal_y,
      )
      label += f" (MST={MST:.1f})".replace("inf", r"$\infty$")
    if config.include_nominal:
      ax.plot(
        nominal_x,
        nominal_y,
        label=label,
        color=config.nominal_color,
        linestyle='--'
      )

    return {
      "x": nominal_x,
      "nominal": nominal_y,
    }

  def _plot_censored(
    self,
    ax: matplotlib.axes.Axes,
    config: KaplanMeierPlotConfig,
    x_for_plot: typing.Sequence[float] | npt.NDArray[np.float64],
    y_for_plot: typing.Sequence[float] | npt.NDArray[np.float64],
  ):
    patient_censored_times = sorted(self.nominalkm.patient_censored_times)
    censored_times_probabilities = [
      y_for_plot[
        max(i for i, t in enumerate(x_for_plot) if t <= patient_censored_time)
      ]
      for patient_censored_time in patient_censored_times
    ]
    ax.plot(
      patient_censored_times,
      censored_times_probabilities,
      marker='|',
      color=config.nominal_color if config.include_nominal else config.best_color,
      markersize=8,
      markeredgewidth=1.5,
      linestyle="",
    )

  def _plot_confidence_band_fill( # pylint: disable=too-many-arguments, too-many-locals
    self,
    ax: matplotlib.axes.Axes,
    config: KaplanMeierPlotConfig,
    times_for_plot: typing.Sequence[float],
    CL_probabilities_data: np.ndarray,
    *,
    label_suffix: str = "",
    use_hatches: bool = False,
    colors: list[str] | None = None,
  ):
    """
    Helper to plot confidence bands using fill_between.
    """
    results = {}
    if colors is None:
      colors = config.CL_colors
    for CL, color, hatch, (p_minus, p_plus) in zip(
      config.CLs,
      colors,
      config.CL_hatches,
      CL_probabilities_data.transpose(1, 2, 0),
      strict=True,
    ):
      x_minus, y_minus = self.get_points_for_plot(times_for_plot, p_minus)
      x_plus, y_plus = self.get_points_for_plot(times_for_plot, p_plus)
      np.testing.assert_array_equal(x_minus, x_plus)

      if CL > 0.9999:
        label = f'{CL:.6%} CL'
      elif CL > 0.99:
        label = f'{CL:.2%} CL'
      else:
        label = f'{CL:.0%} CL'

      if label_suffix:
        label += f' ({label_suffix})'

      if config.include_median_survival:
        MST_low = self.median_survival_time(
          times_for_plot=x_minus,
          survival_probabilities=y_minus,
        )
        MST_high = self.median_survival_time(
          times_for_plot=x_plus,
          survival_probabilities=y_plus,
        )
        label += f" (MST$\\in$({MST_low:.1f}, {MST_high:.1f}))".replace("inf", r"$\infty$")

      if use_hatches:
        ax.fill_between(
          x_minus,
          y_minus,
          y_plus,
          edgecolor=color,
          facecolor='none',
          hatch=hatch,
          alpha=0.5,
          label=label,
        )
      else:
        ax.fill_between(
          x_minus,
          y_minus,
          y_plus,
          color=color,
          alpha=0.5,
          label=label,
        )
      results[label] = (y_minus, y_plus)
    return results

  def _calculate_and_plot_confidence_bands( # pylint: disable=too-many-locals, too-many-branches, too-many-statements
    self,
    ax: matplotlib.axes.Axes,
    config: KaplanMeierPlotConfig,
    times_for_plot: typing.Sequence[float]
  ):
    """Calculates and plots the confidence bands and best-fit curve."""

    # --- storage for computed results (no plotting yet) ---
    best_probabilities = None
    CL_probabilities = None
    results = {}

    best_prob_full = None
    CL_prob_full = None

    best_prob_binomial = None
    CL_prob_binomial = None

    best_prob_greenwood = None
    CL_prob_greenwood = None

    best_prob_patient = None
    CL_prob_patient = None

    # --- compute required probability sets (no fills plotted here) ---
    if config.include_full_NLL:
      best_prob_full, CL_prob_full = self.survival_probabilities_likelihood(
        CLs=config.CLs,
        times_for_plot=times_for_plot,
        print_progress=config.print_progress,
        MIPGap=config.MIPGap,
        MIPGapAbs=config.MIPGapAbs,
      )

    if config.include_binomial_only:
      best_prob_binomial, CL_prob_binomial = self.survival_probabilities_likelihood(
        CLs=config.CLs,
        times_for_plot=times_for_plot,
        binomial_only=True,
        print_progress=config.print_progress,
        MIPGap=config.MIPGap,
        MIPGapAbs=config.MIPGapAbs,
      )

    if config.include_exponential_greenwood:
      best_prob_greenwood, CL_prob_greenwood = self.survival_probabilities_exponential_greenwood(
        CLs=config.CLs,
        times_for_plot=times_for_plot,
        binomial_only=True,
      )

    if config.include_patient_wise_only:
      best_prob_patient, CL_prob_patient = self.survival_probabilities_likelihood(
        CLs=config.CLs,
        times_for_plot=times_for_plot,
        patient_wise_only=True,
        print_progress=config.print_progress,
        MIPGap=config.MIPGap,
        MIPGapAbs=config.MIPGapAbs,
      )

    # --- determine which set is the 'best' (preserve original precedence) ---
    if config.include_full_NLL:
      best_probabilities = best_prob_full
      CL_probabilities = CL_prob_full

    if config.include_binomial_only:
      if not config.include_full_NLL:
        best_probabilities = best_prob_binomial
        CL_probabilities = CL_prob_binomial

    if config.include_exponential_greenwood:
      # does not override an explicit full/binomial preference
      if not config.include_full_NLL and not config.include_binomial_only:
        best_probabilities = best_prob_greenwood
        CL_probabilities = CL_prob_greenwood

    if config.include_patient_wise_only:
      if not config.include_full_NLL:
        best_probabilities = best_prob_patient
        CL_probabilities = CL_prob_patient

    # --- fail fast if we couldn't determine a best probability set ---
    if best_probabilities is None or CL_probabilities is None:
      raise ValueError(
        "Could not determine best_probabilities or CL_probabilities. "
        "Check config flags and data returned by likelihood/greenwood calls."
      )

    # --- PLOT PHASE: plot best-fit first (so it appears above fills added here) ---
    if config.include_best_fit:
      best_x, best_y = self.get_points_for_plot(times_for_plot, best_probabilities)
      label = config.best_label
      if config.include_median_survival:
        MST = self.median_survival_time(
          times_for_plot=best_x,
          survival_probabilities=best_y,
        )
        label += f" (MST={MST:.1f})"
      ax.plot(
        best_x,
        best_y,
        label=label,
        color=config.best_color,
        linestyle='--'
      )
      results["best_fit"] = best_y

    # --- now plot confidence-band fills in the original sequence ---
    if config.include_full_NLL:
      assert CL_prob_full is not None
      CL_results = self._plot_confidence_band_fill(
        ax, config, times_for_plot, CL_prob_full, use_hatches=False
      )
      results.update(CL_results)

    if config.include_binomial_only:
      assert CL_prob_binomial is not None
      if config.include_full_NLL:
        CL_results = self._plot_confidence_band_fill(
          ax, config, times_for_plot, CL_prob_binomial,
          label_suffix=config.binomial_only_suffix, use_hatches=True
        )
      else:
        CL_results = self._plot_confidence_band_fill(
          ax, config, times_for_plot, CL_prob_binomial,
          label_suffix=config.binomial_only_suffix, use_hatches=False
        )
      results.update(CL_results)

    if config.include_exponential_greenwood:
      assert CL_prob_greenwood is not None
      CL_results = self._plot_confidence_band_fill(
        ax, config, times_for_plot, CL_prob_greenwood,
        label_suffix=config.exponential_greenwood_suffix, use_hatches=False,
        colors=config.CL_colors_greenwood[:len(config.CLs)],
      )
      results.update(CL_results)

    if config.include_patient_wise_only:
      assert CL_prob_patient is not None
      if config.include_full_NLL:
        CL_results = self._plot_confidence_band_fill(
          ax, config, times_for_plot, CL_prob_patient,
          label_suffix=config.patient_wise_only_suffix, use_hatches=True
        )
      else:
        CL_results = self._plot_confidence_band_fill(
          ax, config, times_for_plot, CL_prob_patient,
          label_suffix=config.patient_wise_only_suffix, use_hatches=False
        )
      results.update(CL_results)

    return results

  def _finalize_plot(
    self,
    fig: matplotlib.figure.Figure,
    ax: matplotlib.axes.Axes,
    config: KaplanMeierPlotConfig,
  ):
    """Adds final plot elements and handles saving/showing/closing."""
    ax.set_xlabel(config.xlabel, fontsize=config.label_fontsize)
    ax.set_ylabel(config.ylabel, fontsize=config.label_fontsize)
    if config.title is not None:
      ax.set_title(config.title, fontsize=config.title_fontsize)
    ax.grid(visible=config.show_grid)
    ax.set_ylim(0, 1.05) # Ensure y-axis is from 0 to 1.05 for survival probability

    #set font sizes
    ax.tick_params(labelsize=config.tick_fontsize)
    if config.title is not None:
      ax.title.set_fontsize(config.title_fontsize)

    if config.tight_layout:
      fig.tight_layout()

    if config.saveas is not None:
      save_path = pathlib.Path(config.saveas)
      save_path.parent.mkdir(parents=True, exist_ok=True)
      fig.savefig(save_path, bbox_inches='tight', dpi=config.dpi)

    if config.legend_saveas is None:
      ax.legend(fontsize=config.legend_fontsize, loc=config.legend_loc)
    else:
      handles, labels = ax.get_legend_handles_labels()
      fig_legend, ax_legend = plt.subplots(figsize=config.figsize, dpi=config.dpi)
      ax_legend.axis("off")
      legend = ax_legend.legend(
        handles, labels,
        fontsize=config.legend_fontsize,
        loc="center"
      )
      #crop whitespace
      fig_legend.canvas.draw()
      bbox = legend.get_window_extent().transformed(fig_legend.dpi_scale_trans.inverted())
      fig_legend.set_size_inches(bbox.width, bbox.height)

      if config.legend_saveas != os.devnull:
        #can't just let it write to devnull because it appends .png
        fig_legend.savefig(config.legend_saveas, bbox_inches="tight")
      plt.close(fig_legend)

    if config.show:
      plt.show()

    if config.close_figure is None: # Default behavior: close if saving, don't close if showing
      if config.saveas is not None:
        plt.close(fig)
    elif config.close_figure:
      plt.close(fig)
