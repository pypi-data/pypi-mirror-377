"""
Coupling Correction
---------------------

Creates a coupling knob from current optics.
Perform coupling correction.
The functionality is based on the FineTuneCoupling scripts.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from cpymad_lhc.general import get_coupling_knobs, get_tune_and_chroma_knobs

if TYPE_CHECKING:
    from collections.abc import Sequence

    from cpymad.madx import Madx


LOG = logging.getLogger(__name__)


def correct_coupling(madx: Madx, accel: str, sequence: str,
                     knobs_suffix: str = "", **kwargs):
    """ Wrapper for coupling correction to use the default knob-names if not
     otherwise given.

    Args:
        madx: Madx instance
        accel: Accelerator we are using 'LHC' or 'HLLHC'
        sequence: Sequence to use
        knobs_suffix: Use suffix with knobs ( e.g. `_sq`)

    Keyword Args:
        Other arguments of `correct_coupling_with_knobs`
    """
    def check_knobs(knobs):
        not_defined = [k for k in knobs if k not in madx.globals]
        if len(not_defined):
            raise KeyError(f"Knobs {not_defined} are not defined in sequence!")

    knobs_dict = _get_default_knob_names(accel, sequence, suffix=knobs_suffix)
    for knob_arg, knob_names in knobs_dict.items():
        if knob_arg not in kwargs:
            check_knobs(knob_names)
            kwargs[knob_arg] = knob_names

    correct_coupling_with_knobs(madx, sequence, **kwargs)


def correct_coupling_with_knobs(madx: Madx, sequence: str,
                                tune_knobs: list[str],
                                chroma_knobs: list[str],
                                coupling_knobs: list[str],
                                qx: float, qy: float, dqx: float, dqy: float,
                                iterations: int = 2, tolerance: float = 1e-7,
                                simplex: bool = False,
                                pre_estimation: bool = True,
                                match_tunes: bool = True,
                                ):
    """ Corrects coupling via the given knobs.

    If there is no coupling, the tunes should be able to be matched
    to the same factional tunes (mid-tunes). If there is a remaining tune split,
    this is the closest tune approach (cta) and indicates the presence of
    coupling.

    The algorithm is as follows:
    First the coupling knob settings are estimated by a one-step newton
    optimization (if `pre_estimate` is set).
    Then the tune-knobs and the coupling knobs are used
    alternatingly to match the tunes together. This is iterated according to the
    desired `iteration` parameter.
    Before and after this correction the cta is checked.

    Remark: The first `twiss` call in the first `_analytical_minimization` call
    is unneccessary as the nothing has changed between this one and the one in
    `_cta_check`. Could be somehow checked for speed optimization.

    Args:
        madx: Madx instance
        tune_knobs: names of elements/knobs to vary for tune matching
        chroma_knobs: names of elements/knobs to vary for chroma matching:
        coupling_knobs: names of elements/knobs to vary for coupling matching:
        sequence: Sequence to use
        qx: tune to match in x
        qy: tune to match in y
        dqx: chromaticity to match in x
        dqy: chromaticity to match in y
        tolerance: (final) tolerance for successfull matching
        iterations: number of iterations in empirical matching
        simplex: use simplex method in empirical matching
        pre_estimation: use analytical method to estimate coupling-knob settings.
                      This will only work if the given coupling knobs correspond
                      to the imaginary and real part of F1001.
        match_tunes: If true, also performs a tune and chroma match at the end,
                     otherwise, the original tune-knob values are recovered.
    """
    qx_mid, qy_mid = _get_middle_tunes(qx, qy)
    tune_knobs_saved = {k: madx.globals[k] for k in tune_knobs}

    cta = _cta_check(madx, sequence, tune_knobs, qx_mid, qy_mid,
                     tolerance=tolerance * 10 ** iterations,
                     text="Initial closest tune approach")

    if cta <= tolerance:
        LOG.info("Coupling already below tolerance. Skipping correction.")
        for k, val in tune_knobs_saved.items():
            madx.globals[k] = val
        return

    if pre_estimation:
        for knob in coupling_knobs:
            _analytical_minimization(madx, sequence, knob)

    _empirical_minimization(madx, sequence,
                            tune_knobs, coupling_knobs,
                            iterations, qx_mid, qy_mid, tolerance, simplex)

    _cta_check(madx, sequence, tune_knobs, qx_mid, qy_mid,
               tolerance=tolerance,
               text="Final closest tune approach")

    if match_tunes:
        _recover_tunes(madx, sequence, tune_knobs, chroma_knobs,
                       qx=qx, qy=qy, dqx=dqx, dqy=dqy)
    else:
        for k, val in tune_knobs_saved.items():
            madx.globals[k] = val


# Algorithm Steps --------------------------------------------------------------

def _get_middle_tunes(qx: float, qy: float) -> tuple[float, float]:
    """ Get the tunes with the factional part in the middle
    between the qx and qy fractional parts, but with the same integer part. """
    qx_frac, qy_frac = qx % 1, qy % 1
    qmid_frac = 0.5 * (qx_frac + qy_frac)
    qx_mid = int(qx) + qmid_frac
    qy_mid = int(qy) + qmid_frac
    return qx_mid, qy_mid


def _get_default_knob_names(accel: str, sequence: str, suffix: str = "") -> dict:
    """ Get tune, chroma and coupling knobs. """
    tune_chroma_knobs = list(get_tune_and_chroma_knobs(accel, int(sequence[-1]), suffix=suffix))
    coupling_knobs = list(get_coupling_knobs(accel, int(sequence[-1]), suffix=suffix))
    return dict( # noqa: C408
        tune_knobs=tune_chroma_knobs[:2],
        chroma_knobs=tune_chroma_knobs[2:],
        coupling_knobs=coupling_knobs,
    )


def _analytical_minimization(madx: Madx, sequence: str, knob: str):
    """ Analytical Minimization. """
    init_value = madx.globals[knob]
    cta = _get_current_tune_approach(madx, sequence)

    madx.globals[knob] = init_value + 0.5 * cta
    cta_plus = _get_current_tune_approach(madx, sequence)

    madx.globals[knob] = init_value - 0.5 * cta
    cta_minus = _get_current_tune_approach(madx, sequence)

    new_value = init_value + 0.5 * (cta_minus**2 - cta_plus**2) / cta
    LOG.debug(f"Knob {knob} updated: {init_value} -> {new_value}.")

    madx.globals[knob] = new_value


def _empirical_minimization(madx: Madx, sequence: str,
                            tune_knobs: Sequence[str], coupling_knobs: Sequence[str],
                            iterations: int, qx_mid: float, qy_mid: float,
                            tolerance: float, simplex: bool):
    """ Push tunes together by alternative matching of tune and coupling knobs. """
    calls_tune = 100 * (1+simplex)
    calls_coupling = 150 * (1+simplex)
    step = 1e-9
    for idx in range(iterations):
        current_tol = tolerance * 10**(iterations-idx-1)  # ends at final tolerance
        match(
            madx, sequence, tune_knobs,
            q1=qx_mid, q2=qy_mid,
            step=step, calls=calls_tune,
            tolerance=current_tol,
            # simplex=simplex,  # simplex is only used with coupling knobs
        )
        match(
            madx, sequence, coupling_knobs,
            q1=qx_mid, q2=qy_mid,
            step=step, calls=calls_coupling,
            tolerance=2*current_tol,
            simplex=simplex
        )


def _recover_tunes(madx: Madx, sequence: str, tune_knobs: list[str], chroma_knobs: list[str],
                   qx: float, qy: float, dqx: float, dqy: float):
    """ Recover Tunes (i.e. normal tune matching) """
    # match_tune(madx, accel, sequence, qx=qx, qy=qy, dqx=dqx, dqy=dqy)
    match(
        madx, sequence, tune_knobs,
        chrom=True,
        q1=qx, q2=qy,
        step=1e-7, calls=100, tolerance=1e-21
    )
    match(
        madx, sequence, chroma_knobs,
        chrom=True,
        dq1=dqx, dq2=dqy,
        step=1e-7, calls=100, tolerance=1e-21
    )
    match(
        madx, sequence, tune_knobs+chroma_knobs,
        chrom=True,
        q1=qx, q2=qy, dq1=dqx, dq2=dqy,
        step=1e-7, calls=100, tolerance=1e-21
    )


# Closest Tune Approach --------------------------------------------------------

def _cta_check(madx, sequence, tune_knobs, qx_mid, qy_mid, tolerance, text):
    """ Try to match tunes and log closest tune approach. """
    match(madx, sequence, tune_knobs,
          q1=qx_mid, q2=qy_mid, step=1e-9, calls=100, tolerance=tolerance)
    cta = _get_current_tune_approach(madx, sequence)
    LOG.info(f"{text}: {cta}")
    return cta


def _get_current_tune_approach(madx: Madx, sequence: str) -> float:
    """ Get the current tune approach in the sequence. """
    madx.twiss(sequence=sequence)
    qx, qy = madx.table.twiss.summary.q1, madx.table.twiss.summary.q2
    cta = _get_tune_approach_value(qx, qy)
    LOG.debug(f"Current tune approach value: {cta}")
    return cta


def _get_tune_approach_value(qx: float, qy: float) -> float:
    """ Calculate the (fractional) tune approach of qx and qy. """
    tune_split = int(qx) - int(qy)
    return abs(qx - qy - tune_split)


# General Matching function ----------------------------------------------------

def match(madx: Madx, sequence: str, knobs: Sequence[str],
          step: float = 1e-7, tolerance: float = 1e-21, calls: float = 100,
          chrom=False, simplex=False, **kwargs):
    """ Match the `knobs` to the settings in `kwargs`.

    Args:
        madx: Madx instance
        sequence: Sequence to use
        knobs: Sequence of variables to match
        chrom: use the `chrom` flag in match
        step: step size to vary knob
        calls: number of varying calls
        tolerance: (final) tolerance for successfull matching

    Keyword Args:
        Arguments for the MAD-X `global` command to be matched at,
        e.g. `q1=`, `dqy=` etc.

     """
    LOG.info(f"Matching knobs '{', '.join(knobs)}' for sequence '{sequence}'.")
    madx.command.match(chrom=chrom)
    madx.command.global_(sequence=sequence, **kwargs)
    for name in knobs:
        madx.command.vary(name=name, step=step)

    if simplex:
        madx.command.simplex(calls=calls, tolerance=tolerance)
    else:
        madx.command.lmdif(calls=calls, tolerance=tolerance)

    madx.command.endmatch()
