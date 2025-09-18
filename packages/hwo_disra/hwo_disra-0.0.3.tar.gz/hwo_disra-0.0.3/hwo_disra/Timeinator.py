from itertools import product
from typing import Mapping
from hwo_disra.EAC import EAC
from hwo_disra.Yieldinator import Yieldinator, Thresholds, YieldEvaluation
from hwo_disra.Types import *
from hwo_disra.yield_sample import YieldSample


class Timeinator(object):
    """
    This class wraps a Yieldinator, which supports Panel 1 analysis and
    extends it to support Panel 2 analysis.  e.g. for a specific
    observatory, what is the cost of achieving the yield, in exposure time.
    """

    def __init__(self, yieldinator: Yieldinator) -> None:
        self._yieldinator = yieldinator

    def thresholds(self) -> Thresholds:
        return self._yieldinator.thresholds()

    def independent_variables(self) -> Mapping[str, float | Range]:
        """
        Return a dictionary of additional variables needed to compute the
        yield. e.g.
        {'magnitude': (26, 33), 'sky_coverage': (0, 0.2)}

        The DRMinator will draw from these ranges when analyzing the
        yield.  e.g. a call may then be:
        self.yieldinator(eac1, magnitude=27, sky_coverage=0.15)

        NOTE: 'time' and 'yield' may _not_ be variable names in the
              dictionary.
        """
        return self._yieldinator.independent_variables()

    def timeinate(self, eac: EAC, **kwargs) -> tuple[ScienceYield, Time]:
        """"
        Compute the yield from the parameters, which are drawn from
        the independent_variables method values.
        """
        return ScienceYield(0), Time(0)

    def eval(self, eac: EAC, steps = 11) -> YieldEvaluation:
        idv = self.independent_variables()
        if not idv or len(idv) == 0:
            yield_result, time = self.timeinate(eac)
            return YieldEvaluation([YieldSample(yield_result = yield_result,
                                                time = time)])
        else:
            sample_points = Yieldinator.generate_variable_combinations(idv, steps)
            results = []
            for combo in product(*sample_points):
                var_dict = dict(combo)
                yield_result, time = self.timeinate(eac, **var_dict)
                results.append(YieldSample(
                    yield_result = yield_result,
                    time = time,
                    variable_values = var_dict.copy()
                ))
            return YieldEvaluation(results, eac.name)
