"""
Kaplan-Meier curves with systematic uncertainties, using the Monte Carlo method.
"""

import abc
import functools
import numbers

import matplotlib.pyplot as plt
import numpy as np
import scipy.stats

class KaplanMeierPatientBase(abc.ABC):
  """
  Base class for Kaplan-Meier patients.
  It contains the survival time and the parameter used to group the patients.
  """
  def __init__(self, time: float, censored: bool, parameter):
    self.__time = time
    self.__censored = censored
    self.__parameter = parameter
  @property
  def time(self):
    """
    Returns the survival time of the patient.
    """
    return self.__time
  @property
  def censored(self) -> bool:
    """
    Returns True if the patient is censored, False otherwise.
    """
    return self.__censored
  @property
  def parameter(self):
    """
    Returns the parameter used to group the patients.
    """
    return self.__parameter

class KaplanMeierPatient(KaplanMeierPatientBase):
  """
  Class to represent a patient with their survival time and parameter.
  """
  def __init__(self, time: float, censored: bool, parameter: float):
    super().__init__(time=time, censored=censored, parameter=parameter)
    if not isinstance(parameter, (numbers.Number)):
      raise TypeError("Parameter must be a number")

  @property
  def parameter(self) -> float:
    """
    Returns the parameter used to group the patients.
    """
    return super().parameter

class KaplanMeierBase(abc.ABC):
  """
  Base class for Kaplan-Meier curves with some utility functions.
  """
  @property
  @abc.abstractmethod
  def patient_death_times(self) -> frozenset[float]:
    """
    Returns the survival times of the patients who died.
    (excludes censored patients)
    """
  @property
  @abc.abstractmethod
  def patient_censored_times(self) -> frozenset[float]:
    """
    Returns the survival times of the patients who were censored.
    """
  @functools.cached_property
  def times_for_plot(self) -> list[float]:
    """
    Returns the survival times for the Kaplan-Meier curve.
    The times are the unique survival times of the patients,
    plus a point at 0 and a point beyond the last time.
    """
    times_for_plot = sorted(self.patient_death_times)
    times_for_plot = (
      [0]
      + times_for_plot
      + [1.1 * max((times_for_plot[-1], *self.patient_censored_times))]
    )
    return times_for_plot

  @staticmethod
  def get_points_for_plot(times_for_plot, survival_probabilities):
    """
    Return (x, y) points for the Kaplan-Meier curve based on the
    survival probabilities at each time.
    Each time enters twice in the plot in order to have a step function.
    """
    x = [times_for_plot[0]]
    y = [survival_probabilities[0]]
    for prevprob, time, prob in zip(
      survival_probabilities[:-1],
      times_for_plot[1:],
      survival_probabilities[1:],
      strict=True
    ):
      x.append(time)
      y.append(prevprob)
      x.append(time)
      y.append(prob)
    return np.array(x), np.array(y)

  @staticmethod
  def median_survival_time(*, times_for_plot, survival_probabilities):
    """
    Returns the median survival time.
    The median survival time is the time at which the survival probability is 0.5.
    """
    median_time = np.inf
    for t, p in zip(times_for_plot, survival_probabilities, strict=True):
      if p <= 0.5:
        median_time = t
        break
    return median_time

class KaplanMeierInstance(KaplanMeierBase):
  """
  Class to represent a Kaplan-Meier curve.
  It contains a list of patients with their survival times and parameters.
  The patients are filtered based on a parameter range.

  Parameters
  ----------
  all_patients : list of KMPatient
    List of all patients with their survival times and parameters.
  """
  def __init__(
    self,
    all_patients: list[KaplanMeierPatient],
    parameter_min: float = -np.inf,
    parameter_max: float = np.inf
  ):
    self.__all_patients = all_patients
    self.__parameter_min = parameter_min
    self.__parameter_max = parameter_max


  @property
  def all_patients(self):
    """
    Returns all the patients before filtering.
    """
    return self.__all_patients
  @property
  def patients(self):
    """
    Returns the patients who enter the Kaplan-Meier curve.
    The patients are filtered based on the parameter range.
    """
    return [
      p for p in self.all_patients
      if self.__parameter_min <= p.parameter < self.__parameter_max
    ]

  @property
  def patient_death_times(self):
    """
    Returns the survival times of the patients who died.
    (excludes censored patients)
    """
    patients = self.patients
    patient_times = frozenset({p.time for p in patients if not p.censored})
    return patient_times
  @property
  def patient_censored_times(self):
    """
    Returns the survival times of the patients who were censored.
    """
    patients = self.patients
    patient_times = frozenset({p.time for p in patients if p.censored})
    return patient_times

  def survival_probabilities(self, times_for_plot=None):
    """
    Returns the points for the Kaplan-Meier curve.
    The points are the survival times and the survival probabilities.
    """
    patients = self.patients
    patient_times = np.array([p.time for p in patients])
    unique_patient_times = np.unique(patient_times)
    patient_censored = np.array([p.censored for p in patients])

    survival_probabilities = np.zeros(len(unique_patient_times) + 1)
    survival_probabilities[0] = 1.0  # at time 0, all patients are alive
    for i, t in enumerate(unique_patient_times, start=1):
      patient_alive = (patient_times > t) | ((patient_times == t) & patient_censored)
      at_risk = patient_times >= t
      try:
        survival_probabilities[i] = (
          survival_probabilities[i - 1]
            * np.count_nonzero(patient_alive) / np.count_nonzero(at_risk)
        )
      except ZeroDivisionError:
        #after everyone is censored: keep the last survival probability
        survival_probabilities[i] = survival_probabilities[i - 1]

    if times_for_plot is None:
      times_for_plot = self.times_for_plot
    survival_probabilities_for_plot = np.zeros(len(times_for_plot))
    for i, t in enumerate(times_for_plot):
      if t < unique_patient_times[0]:
        survival_probabilities_for_plot[i] = 1.0
      elif t > unique_patient_times[-1]:
        survival_probabilities_for_plot[i] = survival_probabilities[-1]
      else:
        # find the index of the closest lower time
        idx = np.searchsorted(unique_patient_times, t, side='right')
        survival_probabilities_for_plot[i] = survival_probabilities[idx]

    return survival_probabilities_for_plot

  def survival_probability(self, time: float) -> float:
    """
    Returns the survival probability at a specific time.
    """
    result, = self.survival_probabilities(times_for_plot=[time])
    return result

  def points_for_plot(self, times_for_plot=None):
    """
    Returns the points for the Kaplan-Meier curve.
    The points are the survival times and the survival probabilities.
    """
    if times_for_plot is None:
      times_for_plot = self.times_for_plot
    survival_probabilities = self.survival_probabilities(times_for_plot)
    return self.get_points_for_plot(times_for_plot, survival_probabilities)

  def survival_probabilities_exponential_greenwood(  #pylint: disable=too-many-locals
    self,
    CLs: list[float],
    times_for_plot=None,
  ):
    """
    Returns the survival probabilities and confidence limits
    at the specified times using the exponential Greenwood method.
    This is the same behavior as lifelines.
    See https://www.math.wustl.edu/%7Esawyer/handouts/greenwood.pdf
    """
    if times_for_plot is None:
      times_for_plot = self.times_for_plot

    best_probabilities = []
    CL_probabilities = []
    for t in times_for_plot:
      CL_probabilities_time_point = []
      CL_probabilities.append(CL_probabilities_time_point)
      S = self.survival_probability(t)
      best_probabilities.append(S)
      for CL in CLs:
        alpha = 1 - CL
        if 0 < S < 1:
          z_alpha_over_2 = scipy.stats.norm.ppf(1 - alpha / 2)
          log_minus_log_S = np.log(-np.log(S))
          sum_in_sqrt = 0
          for t_prime in self.patient_death_times:
            if t_prime > t:
              continue
            at_risk = len([p for p in self.patients if p.time >= t_prime])
            died = len([p for p in self.patients if p.time == t_prime and not p.censored])
            survived = at_risk - died
            sum_in_sqrt += died / (at_risk * survived)
          error = z_alpha_over_2 / np.log(S) * np.sqrt(sum_in_sqrt)
          log_minus_log_S_upper = log_minus_log_S + error
          log_minus_log_S_lower = log_minus_log_S - error
          S_upper = np.exp(-np.exp(log_minus_log_S_upper))
          S_lower = np.exp(-np.exp(log_minus_log_S_lower))
        else:
          # If S is 0 or 1, 1 / log(S) is 0, so the error is 0.
          S_upper = S
          S_lower = S
        CL_probabilities_time_point.append((S_lower, S_upper))

    best_probabilities = np.asarray(best_probabilities)
    CL_probabilities = np.asarray(CL_probabilities)
    return best_probabilities, CL_probabilities

class KaplanMeierPlot(KaplanMeierBase):
  """
  Class to represent a set of Kaplan-Meier curves.
  It contains a list of patients with their survival times and parameters.
  The patients are filtered based on a parameter range, and each patient
  enters a different Kaplan-Meier curve.

  Parameters
  ----------
  all_patients : list of KMPatient
    List of all patients with their survival times and parameters.
  thresholds : list of float
    List of thresholds to filter the patients.
  """
  def __init__(
    self,
    all_patients: list[KaplanMeierPatient],
    thresholds: list[float],
  ):
    self.__all_patients = all_patients
    self.__thresholds = [-np.inf] + sorted(thresholds) + [np.inf]
    self.__curves: list[KaplanMeierInstance] = []
    for i in range(len(self.__thresholds) - 1):
      self.__curves.append(
        KaplanMeierInstance(
          all_patients,
          self.__thresholds[i],
          self.__thresholds[i + 1],
        )
      )

  @property
  def all_patients(self):
    """
    Returns the patients with their survival times and parameters.
    """
    return self.__all_patients

  def plot(self):
    """
    Plots the Kaplan-Meier curves.
    """
    plt.figure()
    for i, curve in enumerate(self.__curves):
      x, y = curve.points_for_plot(times_for_plot=self.times_for_plot)
      plt.plot(
        x,
        y,
        #where='post',
        label=f"Curve {i + 1}: {self.__thresholds[i]} <= parameter < {self.__thresholds[i + 1]}"
      )

    plt.xlabel("Time")
    plt.ylabel("Survival Probability")
    plt.title("Kaplan-Meier Curves")
    plt.legend()
    plt.grid()
    plt.show()

  @property
  def patient_death_times(self):
    """
    Returns the survival times of the patients who died.
    (excludes censored patients)
    """
    return frozenset.union(
      *[kmi.patient_death_times for kmi in self.__curves]
    )
  @property
  def patient_censored_times(self):
    """
    Returns the survival times of the patients who were censored.
    """
    return frozenset.union(
      *[kmi.patient_censored_times for kmi in self.__curves]
    )
