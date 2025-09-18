import inspect

# noinspection PyUnresolvedReferences
import hwo_disra.environment

from multiprocessing.managers import SyncManager
from pathlib import Path
from typing import Callable, Any
import astropy.units as u

from syotools.models import Source, SourcePhotometricExposure

from hwo_disra.EAC import create_syo_eac, EAC
from hwo_disra.Plotinator import Plotinator
from hwo_disra.Timeinator import Timeinator
from hwo_disra.Yieldinator import *
from hwo_disra.matrix_lookup_yieldinator import MatrixLookupYieldinator


class DisraNBApi:
  """
  This class implements the API for use in DISRA notebooks. It supports some
  standard plots as well as the capture of yieldinator and timeinator
  data.

  To support DISRA analysis and capture of data products a notebook must include
  a line that registers a timeinator evaluation, like this:

  >>> api = DisraNBApi()
  >>> yieldinator = api.yieldinator()
  >>> results = api.
  """
  _api_instances: list['DisraNBApi'] = []
  _parameters = {}
  _eacs = [create_syo_eac(n) for n in ['EAC1', 'EAC2', 'EAC3']]

  def __init__(self, show_plots: bool = True):
    self._yieldinators: list[Yieldinator] = []
    self._yield_results: list[YieldEvaluation] = []
    self._api_instances.append(self)
    self._plotinator = Plotinator(show_plots = show_plots,
                                  output_dir=Path("tests/outputs/"))

  @staticmethod
  def set_eacs(eacs):
    DisraNBApi._eacs = eacs

  @staticmethod
  def set_parameters(parameters):
    DisraNBApi._parameters.update(parameters)

  @staticmethod
  def get_parameter(key, default):
    print(DisraNBApi._parameters)
    return DisraNBApi._parameters.get(key, default)

  def add_yieldinator(self, yieldinator: Yieldinator)  -> None:
    self._yieldinators.append(yieldinator)

  def matrix_lookup_yieldinator(self, *args, **kwargs) -> MatrixLookupYieldinator:
    mly = MatrixLookupYieldinator(*args, **kwargs)
    self.add_yieldinator(mly)
    return mly

  def plotinator(self):
    return self._plotinator

  def contour_plot_yield(self, yield_eval: [YieldEvaluation], steps = 50, **kwargs):
    plt = self.plotinator()
    plt.contour_plot([y.sample_points for y in yield_eval], **kwargs)

  def eac_panels(self, evaluations: list[YieldEvaluation], x_key, y_key, z_key,
      figsize = None, contour_levels = None,
      num_color_levels=20, transforms=None,
      axis_labels=None):
    plotter = self.plotinator()

    eacs = self._eacs

    plotter.contour_plot([r.sample_points for r in evaluations],
                     x_key, y_key, z_key,
                     contour_levels=contour_levels,
                     num_color_levels=num_color_levels,
                     transforms=transforms,
                     axis_labels=axis_labels,
                     titles = [f"{eac.name}({eac.telescope.effective_aperture:.2f})" for eac in eacs],
                     figsize=figsize)
                     # title=f"{eac.name}({eac.telescope.effective_aperture})",
                     # file_prefix=eac.name)


  def evaluate(self, inator: Yieldinator | Timeinator, steps = 50, register = False) -> list[YieldEvaluation]:
    results = None

    if isinstance(inator, Timeinator):
      results = [inator.eval(eac, steps = steps) for eac in self._eacs]
    elif isinstance(inator, Yieldinator):
        yields = inator.eval(steps = steps)
        results = [yields]
    # else:
    #   raise NotImplementedError

    if register and results is not None:
      self._yield_results.extend(results)

    return results

  def exptime_from_magnitude_fun(self, snr_goal = 5.0,
      template = 'G2V Star',
      redshift = 0.0,
      extinction = 0.0,
      bandpass = "johnson,v",
      rband_index = 5):
    def exp_time_for_magnitude(eac, magnitude):
      hri = eac.camera()
      source = Source()
      source.set_sed(template, magnitude, redshift, extinction, bandpass)

      exp = SourcePhotometricExposure()
      exp.source = source

      exp._snr = [snr_goal] * u.Unit('electron(1/2)')
      exp.unknown = 'exptime'
      hri.add_exposure(exp)
      return exp.exptime[rband_index].value

    return exp_time_for_magnitude

  def timeinator(self, yieldinator: Yieldinator,
                       timeinate: Callable[[EAC, ScienceYield, Any], Time]) -> Timeinator:
    class Tim(Timeinator):
      def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
      def timeinate(self, eac: EAC, **kwargs) -> tuple[ScienceYield, Time]:
        yield_value = self._yieldinator.yieldinator(**kwargs)
        return yield_value, timeinate(eac, yield_value, **kwargs)
    return Tim(yieldinator)

  def yieldinator(self, name=None, thresholds=None,
                  yield_function=None, variables=None) -> Yieldinator:
      if not name:
          raise ValueError("Name must be set before building yieldinator")
      if not thresholds:
          raise ValueError("Thresholds must be set before building yieldinator")
      if not yield_function:
          raise ValueError("Yieldinator function must be set before building yieldinator")
      if not variables:
          raise ValueError("Independent variables must be set before building yieldinator")

      variable_names = set(variables.keys())
      sig = inspect.signature(yield_function)
      params = set(sig.parameters.keys())
      if len(variable_names.difference(params)) > 0:
          raise TypeError(f"The yield function signature {sig.parameters.keys()} does not match the independent variables {variable_names}.")
      the_yielder = TheYieldinator(name, thresholds, variables, yield_function)
      self.add_yieldinator(the_yielder)
      return the_yielder

  # The multiprocessing API is a disaster when trying to share
  # a data structure between two unrelated processes (no parent/child relationship)
  # https://docs.python.org/3/library/multiprocessing.html#using-a-remote-manager
  class QueueManager(SyncManager):
    pass
  QueueManager.register('get_queue')

  @staticmethod
  def write_outputs(address: str, authkey: bytes) -> None:
    print(f"DEBUG: Number of API instances: {len(DisraNBApi._api_instances)}")
    
    # Collect metadata about yieldinators instead of the objects themselves
    all_yieldinator_info = []
    all_evaluations = []
    for api_instance in DisraNBApi._api_instances:
      all_evaluations.extend(api_instance._yield_results)
      for yieldinator in api_instance._yieldinators:
        # Store only serializable information
        info = DisraNBApi.prepare_for_pickle(yieldinator)
        all_yieldinator_info.append(info)

    output = ApiResults(evaluations = all_evaluations, yieldinators = all_yieldinator_info)

    manager = DisraNBApi.QueueManager(address = address, authkey = authkey)
    manager.connect()
    queue = manager.get_queue()
    try:
      queue.put(output)
    except Exception as e:
      with open("log.txt", "a") as f:
        f.write(f"{e}\n")
      queue.put(e)

  @staticmethod
  def receive_data(address: str, authkey: bytes) -> Any:
    manager = DisraNBApi.QueueManager(address = address, authkey = authkey)
    manager.connect()
    queue = manager.get_queue()
    try:
      return queue.get(timeout = 60)
    except Exception as e:
      with open("log.txt", "a") as f:
        f.write(f"{e}\n")
      queue.put(e)

  @staticmethod
  def prepare_for_pickle(yieldinator):
    info = InatorInfo(
        name=getattr(yieldinator, 'name', 'unnamed'),
        type=type(yieldinator).__name__,
        thresholds=yieldinator.thresholds() if hasattr(yieldinator,
                                                       'thresholds') else {},
        variables=yieldinator.independent_variables() if hasattr(yieldinator,
                                                                 'independent_variables') else {}
    )
    return info


class TheYieldinator(Yieldinator):
    def __init__(self, name,
        thresholds,
        independent_variables,
        yieldinator_function):
        self.name = name
        self.the_thresholds = thresholds
        self.the_variables = independent_variables
        self.the_function = yieldinator_function

    def thresholds(self) -> Thresholds: return self.the_thresholds
    def independent_variables(self) -> VariableMap: return self.the_variables
    def yieldinator(self, *args: float, **kwargs) -> ScienceYield: return self.the_function(*args, **kwargs)
    def __str__(self): return f"{self.name}({', '.join([str(v) for v in self.independent_variables()])})"

@dataclasses.dataclass
class InatorInfo:
  name: str
  type: str
  thresholds: Thresholds
  variables: VariableMap

@dataclasses.dataclass
class ApiResults:
  evaluations: list[YieldEvaluation]
  yieldinators: list[InatorInfo]
