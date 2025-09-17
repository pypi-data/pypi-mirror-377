"""
Corrector Limits
-------------------

Checks whether the assigned strengths do not exceed a given maxima.
If it does exceed it, depending on `limit_to_max` either an error is thrown
or the strength is redefined to the maximum (while its sign is retained).
All values are energy independent.

The python script was adapted from
errors/corr_limit.madx or errors/corr_value_limit.madx (depending on HL-LHC version)
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from cpymad_lhc.general import lhc_arc_names

if TYPE_CHECKING:
    from cpymad.madx import Madx


LOG = logging.getLogger(__name__)
LOG_FORMAT = "{name:<10s}    {val_str:>10s}    {max_str:>10s}    {allowed_str:>10s}"


# All values are defined as multiples of 0.3/Energy
LIMITS = {
    'HLLHC': dict(  # noqa
        MQSX1='kmax_MQSXF',
        MQSX2=1.360/0.017,            # 1.36 T @ 17 mm in IR2&IR8
        MCSX1='kmax_MCSXF',
        MCSX2=0.028*2/(0.017**2),     # 0.028 T @ 17 mm in IR2&IR8
        MCSSX1='kmax_MCSSXF',
        MCSSX2=0.11*2/(0.017**2),     # 0.11 T @ 17 mm in IR2&IR8
        MCOX1='kmax_MCOXF',
        MCOX2=0.045*6/(0.017**3),     # 0.045 T @ 17 mm in IR2&IR8
        MCOSX1='kmax_MCOSXF',
        MCOSX2=0.048*6/(0.017**3),    # 0.048 T @ 17 mm in IR2&IR8
        MCDX1='kmax_MCDXF',
        MCDSX1='kmax_MCDSXF',
        MCTX1='kmax_MCTXF',
        MCTX2=0.01*120/(0.017**5),    # 0.010 T @ 17 mm in IR2&IR8
        MCTSX1='kmax_MCTSXF',
        # MQT=120,                      # 120 T/m    Deactivated in HLv1.4
        # MQS=120,                      # 120 T/m    Deactivated in HLv1.4
        # MS=1.280*2/(0.017**2),        # 1.28 T @ 17 mm  Deactivated in HLv1.4
        MSS=1.280*2/(0.017**2),       # 1.28 T @ 17 mm
        MCS=0.471*2/(0.017**2),       # 0.471 T @ 17 mm
        MCO=0.040*6/(0.017**3),       # 0.04 T @ 17 mm
        MCD=0.100*24/(0.017**4),      # 0.1 T @ 17 mm
        # MO=0.29*6/(0.017**3),         # 0.29 T @ 17 mm  Deactivated in HLv1.4
    )
}
FD_FAMILIES = {'MO', 'MS', 'MQT'}  # Magnets that have F and D families
TWO_FAMILIES = {'MS'}              # Magnets that have 1 and 2 families
SPECIAL_FAMILIES = {'MQS'}         # Magnets in every second arc

REL_ALLOWED = 0.3 / 7000  # see corr_limit.madx


class LimitChecks:
    def __init__(self, madx: Madx, beam: int, limit_to_max: bool, values_dict: dict):
        """ Setup checks 'global' variables. """
        self.mvars = madx.globals
        self.beam = 2 if beam == 4 else beam
        self.limit_to_max = limit_to_max
        self.values_dict = values_dict
        self.success = True  # reset at each `run_checks`

    def check_strength(self, name, max_value):
        try:
            rel = self.mvars[name] / max_value
        except KeyError:
            LOG.debug(
                LOG_FORMAT.format(name=name,
                                  val_str=f"{self.mvars[name]}: .3e",
                                  max_str="unknown",
                                  allowed_str="unknown",
                                  )
            )
            return

        msg = LOG_FORMAT.format(name=name,
                                val_str=f"{self.mvars[name]: .3e}",
                                max_str=f"{rel*100: .1e}%",
                                allowed_str=f"{rel/REL_ALLOWED*100: .0f}%")

        if abs(rel) > REL_ALLOWED:
            LOG.warning(msg)
            if self.limit_to_max:
                # same as max_value*REL_ALLOWED*sign(self.mvars[name])
                self.mvars[name] = self.mvars[name] * REL_ALLOWED / abs(rel)
                LOG.info(
                    f'  -> set {name} to {self.mvars[name]: .1e} '
                    f'({self.mvars[name] / max_value * 100: .1e}% of max, 100% of allowed).'
                )
            else:
                self.success = False
        else:
            LOG.debug(msg)

    def check_ir(self, family, value):
        """ Loop over irs """
        irs = '15' if family[-1] == '1' else '28'
        name = f'K{family[1:-1]}3'
        for ir in irs:
            for side in 'LR':
                self.check_strength(f'{name}.{side}{ir}', value)

    def check_arcs(self, family, value):
        """ Loop over arcs """
        fd_list = 'FD' if family in FD_FAMILIES else ['']
        num_list = '12' if family in TWO_FAMILIES else ['']
        for arc in lhc_arc_names(self.beam):
            for fd in fd_list:
                for num in num_list:
                    self.check_strength(f'K{family[1:]}{fd}{num}.{arc}', value)

    def check_special(self, family, value):
        """ Loop over arcs but only every second one. """
        arcs = lhc_arc_names(self.beam)[(self.beam % 2)::2]
        for arc in arcs:
            self.check_strength(f'K{family[1:]}.{arc}', value)
            self.check_strength(f'K{family[1:]}.L{arc[1]}B{self.beam:d}', value)
            self.check_strength(f'K{family[1:]}.R{arc[2]}B{self.beam:d}', value)

    def run_checks(self):
        """ Main check-loop over all families given in values_dict. """
        LOG.info(LOG_FORMAT.format(name="Corrector", val_str="Value", max_str="Maximum", allowed_str="Allowed"))
        self.success = True

        for family, value in self.values_dict.items():
            if isinstance(value, str):
                value = self.mvars[value]

            if family[-1] in '12':
                self.check_ir(family, value)
            elif family in SPECIAL_FAMILIES:
                self.check_special(family, value)
            else:
                self.check_arcs(family, value)


def check_corrector_limits(madx: Madx, accel: str,  beam: int, limit_to_max: bool = False):
    """ Wrapper to run the limit checks.

    Args:
        madx (Madx): MAD-X instance
        accel (str): Accelerator to check.
        beam (int): Beam to check
        limit_to_max (bool): If ``True`` set the value to the max if above limit.
                             If ``False`` will raise ``ValueError`` after finding
                             too high values. Default: ``False``.
    """
    try:
        values_dict = LIMITS[accel.upper()]
    except KeyError as e:
        raise NotImplementedError(f'Accelerator {accel} not implemented.') from e

    LOG.info(f"Checking corrector limits for {accel} beam {beam}.")
    checks = LimitChecks(madx=madx, beam=beam,
                         limit_to_max=limit_to_max,
                         values_dict=values_dict)
    checks.run_checks()
    if not checks.success:
        raise ValueError("One or more strengths are out of its limits, see log.")
