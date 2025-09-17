"""
General
---------

Some helper functions for cpymad, that would be complicated macros in MAD-X.
"""
from __future__ import annotations

import logging
import shutil
from contextlib import contextmanager, suppress
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
import tfs

if TYPE_CHECKING:
    from collections.abc import Sequence

    from cpymad.madx import Madx, Table

LOG = logging.getLogger(__name__)


# Tfs Extraction ---------------------------------------------------------------

def get_lhc_sequence_filename_and_bv(beam: int, accel: str = 'lhc'):
    """ Return the default sequence filename, the sequence name and the bv-flag
    for the given beam.

    Args:
        beam (int): beam to use.
        accel (str): accelerator name ('lhc' or 'hllhc').
    """
    as_built = '_as-built' if accel.lower() == 'lhc' else ''
    seq_file = f"lhc{as_built}.seq"
    seq_name = f"lhcb{beam}"
    bv_flag = -1 if beam == 2 else 1
    if beam == 4:
        seq_file = f"lhcb4{as_built}.seq"
        seq_name = "lhcb2"
    return seq_name, seq_file, bv_flag


def get_tfs(table: Table,
            index: Sequence = None, columns: Sequence = None,
            index_regex: str = None, columns_regex: str = None,
            only_selected: bool = False,
            remove_element_numbering: bool = True,
            ) -> tfs.TfsDataFrame:
    """
    Returns the filtered content of the given `table` as TfsDataFrame.

    Args:
        table: madx table to convert to dataframe
        index: indices to be included in dataframe (need ot be present in table)
        columns: columns to be included in dataframe (need to be present in table)
        index_regex: regex-selection to be applied onto (selected) indices
        columns_regex: regex-selection to be applied onto (selected) columns
        only_selected: returns only selected rows and columns. Overridden by
                       either ``index`` for rows or ``columns`` for columns
                       (i.e. the given ``index`` or ``columns`` will be
                       returned). If the selection is empty ALL rows and columns
                       will be returned, as it can not be decided if the
                       selection is empty from a ``clear``, or from
                       over-exclusive selection.
        remove_element_numbering: Removes the ``:#`` from the element names
                                  (present in column NAME in twiss/error tables)

    Returns:
        TfsDataFrame with selected indices and columns from table and
        summary as header, if available.

    """
    if not columns and only_selected:
        columns = table.selected_columns()
        if len(columns) == 0:  # `selected_columns()` might return empty list
            columns = None

    if not index and only_selected:
        index = table.selected_rows()
        index = np.array(index, dtype=bool) if len(index) else None

    headers = {}
    with suppress(ValueError):
        headers = {k.upper(): v for k, v in table.summary.items()}

    df = tfs.TfsDataFrame(table.dframe(columns), headers=headers)
    df.columns = df.columns.str.upper()

    if "KEYWORD" in df.columns:
        df["KEYWORD"] = df["KEYWORD"].str.upper()

    if "NAME" in df.columns:
        df = df.set_index("NAME")
    else:
        df.index = table.dframe(("NAME",))["NAME"]

    # check index
    if remove_element_numbering:
        if not all(df.index.str.match(r".*:\d$")):
            raise IndexError("Something is wrong with this table. "
                             "Not all names end with ':\\d'")
        df.index = [name[:-2] for name in df.index]
    df.index = df.index.str.upper()

    if index is not None:
        df = df.loc[index, :]

    if index_regex is not None:
        df = df.loc[df.index.str.match(index_regex, case=False), :]

    if columns_regex is not None:
        df = df.loc[:, df.columns.str.match(index_regex, case=False)]

    # df.index = df.index.astype(str)
    # df.columns = df.columns.astype(str)
    # return auto_dtype(df)
    return df


def amplitude_detuning_ptc(madx: Madx, ampdet: int = 2, chroma: int = None, file: Path = None) -> tfs.TfsDataFrame:
    """ Calculate amplitude detuning via PTC_NORMAL

    Args:
        madx: Madx instance
        ampdet: Maximum derivative order for amplitude detuning (only 0, 1 or 2 implemented). Default `2`
        chroma: Maximum derivative order for chromaticity. Default `2`
        file: Path to output file. Default `None`

    Returns:
        TfsDataframe with results

    """
    madx.ptc_create_universe()

    # layout I got with mask (jdilly)
    # model = 3 Sixtrack code model: Delta-Matrix-Kick-Matrix
    # method = 4 (integration order), nst = 3 (integration steps), exact = True (exact Hamiltonian)
    madx.ptc_create_layout(model=3, method=4, nst=3, exact=True)

    # # alternative layout
    # # model = 3 Sixtrack code model: Delta-Matrix-Kick-Matrix
    # # method = 6 (integration order), nst = 3 (integration steps)
    # # resplit = True (adaptive splitting of magnets),
    # # thin = 0.0005 (splitting of quads), xbend=0.0005 (splitting of dipoles)
    # madx.ptc_create_layout(model=3, method=6, nst=3, resplit=True, thin=0.0005, xbend=0.0005)

    madx.ptc_align()  # use madx alignment errors
    # madx.ptc_setswitch(fringe=True)  # include fringe effects

    # Tunes
    madx.select_ptc_normal(q1='0', q2='0')

    # d^iQ/ddp^i
    if chroma is None:
        chroma = ampdet

    for ii in range(1, chroma+1):
        madx.select_ptc_normal(dq1=f'{ii:d}', dq2=f'{ii:d}')

    # ANH = anharmonicities (ex, ey, deltap)
    # works only with parameters as full strings
    # could be done nicer with permutations ...
    if ampdet >= 1:
        madx.select_ptc_normal('anhx=1, 0, 0')  # dQx/dex
        madx.select_ptc_normal('anhy=0, 1, 0')  # dQy/dey
        madx.select_ptc_normal('anhx=0, 1, 0')  # dQx/dey
        madx.select_ptc_normal('anhy=1, 0, 0')  # dQy/dex

    if ampdet >= 2:
        madx.select_ptc_normal('anhx=2, 0, 0')  # d^2Qx/dex^2
        madx.select_ptc_normal('anhx=1, 1, 0')  # d^2Qx/dexdey
        madx.select_ptc_normal('anhx=0, 2, 0')  # d^2Qx/dey^2
        madx.select_ptc_normal('anhy=0, 2, 0')  # d^2Qy/dey^2
        madx.select_ptc_normal('anhy=1, 1, 0')  # d^2Qy/dexdey
        madx.select_ptc_normal('anhy=2, 0, 0')  # d^2Qy/dex^2

    if ampdet > 2:
        raise NotImplementedError('PTC amplitude detuning is not implemented for order > 2.'
                                  f' (Requested order = {ampdet:d})')

    # icase = phase-space dimensionality, no = order of map
    madx.ptc_normal(closed_orbit=True, normal=True, icase=5, no=max([ampdet, chroma])+1)
    madx.ptc_end()

    # get dataframe and write
    df = tfs.TfsDataFrame(madx.table.normal_results.dframe())
    df.columns = df.columns.str.upper()
    df.NAME = df.NAME.str.upper()
    df.index = range(len(df.NAME))  # table has a weird index
    if file:
        tfs.write(file, df)
    return df


def rdts_ptc(madx: Madx, order: int = 4, file: Path = None) -> tfs.TfsDataFrame:
    """ Calculate the RDTs via PTC_TWISS.

    Args:
        madx: Madx instance
        order: Maximum order of the RDTs. Default `4`
        file: Path to rdt output file. Default `None`

    Returns:
        TfsDataframe with results
    """
    madx.ptc_create_universe()
    madx.ptc_create_layout(model=3, method=4, nst=3, exact=True)
    # madx.ptc_create_layout(model=3, method=6, nst=1)  # from Michi
    madx.ptc_align()  # use madx alignment errors
    # madx.ptc_setswitch(fringe=True)  # include fringe effects

    madx.ptc_twiss(icase=6, no=order, normal=True, trackrdts=True)

    # if file:
    #     madx.write(table='twissrdt', file=str(file))

    madx.ptc_end()

    # get dataframe and write
    df = tfs.TfsDataFrame(madx.table.twissrdt.dframe())
    df.columns = df.columns.str.upper()
    df.NAME = df.NAME.str.upper()
    if file:
        tfs.write(file, df)
    return df


def dynamic_aperture_tracking(madx: Madx, sigmas: Sequence[int], n_angles: int,
                              turns: int = 1024, min_delta: float = 0.05,
                              outputdir: Path = None):
    """Perform MAD-X tracking via the DYNAP module.

    Args:
        madx: Madx instance
        n_sigma (int): Number of sigmas in amplitude for particle distribution
        n_angles (int): number of angles for particle distribution
        turns (int): number of turns to track. Default 1024
        min_delta (float): minimum amplitude/angle to use,
                          avoids using 0 and 1 values. Default 0.05
        outputdir (Path): Path to write the output files. Default `None`

    """
    # Create Particle Coordinates ---
    sigmas = np.array(sorted(sigmas))
    origin = sigmas[0] == 0
    if origin:
        sigmas = sigmas[1:]  # remove 0 sigma, added later

    angles = np.arange(n_angles) * np.pi / (2 * (n_angles-1))

    x_pos = sigmas[:, None] * np.cos(angles)
    y_pos = sigmas[:, None] * np.sin(angles)

    # Filter zeros (approximate by small value)
    zero = min_delta  # a small value, approximately Zero
    one = np.sqrt(1 - zero**2)  # from x**2 + y**2 = 1 -> keeps points on circle
    x_pos[:, -1] = zero
    y_pos[:, 0] = zero

    x_pos[:, 0] = x_pos[:, 0] * one
    y_pos[:, -1] = y_pos[:, -1] * one

    # convert to 1-D Arrays
    x_pos = x_pos.flatten()
    y_pos = y_pos.flatten()
    if origin:
        # add origin
        x_pos = np.insert(x_pos, 0, zero)
        y_pos = np.insert(y_pos, 0, zero)

    # Debug: Show your distribution
    # import matplotlib.pyplot as plt
    # fig, ax = plt.subplots(1, 1)
    # ax.set_aspect('equal', adjustable='box')
    # ax.plot(x_pos, y_pos, linestyle="", marker="o")
    # plt.show()

    # Setup Particles and Track ---
    madx.track()
    for x, y in zip(x_pos, y_pos):
        madx.start(fx=x, fy=y)
    madx.dynap(fastune=True, turns=turns)
    madx.endtrack()

    # get tables and drop index
    # (index contains only marker `#e`, maybe as no observation points were set)
    df_dynap = tfs.TfsDataFrame(madx.table.dynap.dframe()).reset_index(drop=True)
    df_dynaptune = tfs.TfsDataFrame(madx.table.dynaptune.dframe()).reset_index(drop=True)
    if outputdir:
        tfs.write(outputdir / 'dynap.tfs', df_dynap)
        tfs.write(outputdir / 'dynap_tune.tfs', df_dynaptune)
    return df_dynap, df_dynaptune


# Errors -----------------------------------------------------------------------


def switch_magnetic_errors(madx: Madx, **kwargs):
    """ Which magnetic field orders to apply.

    Args:
        madx: Madx instance

    Keyword Args:
        default: sets global default to this (default of default is `False`).
        AB#:  sets the default for all of that order.
        A# or B#: sets the default for systematic and random of this id.
        A#s, B#r etc.: sets the specific value.

    with # in [1, 15], where 1 == dipolar field.
    """
    global_default = kwargs.get("default", False)
    for order in range(1, 16):
        order_default = kwargs.get(f"AB{order:d}", global_default)
        for ab in "AB":
            ab_default = kwargs.get(f"{ab}{order:d}", order_default)
            for sr in "sr":
                name = f"{ab}{order:d}{sr}"
                madx.globals[f"ON_{name}"] = int(kwargs.get(name, ab_default))


# Knobs ------------------------------------------------------------------------

def get_coupling_knobs(accel: str, beam: int, suffix: str = "") -> tuple[str, str]:
    """ Get names of knobs to change coupling as tuple of strings.

    Args:
        accel: Accelerator either 'LHC'  or 'HLLHC'
        beam: Beam to use, for the (LHC) knob names
        suffix (str): suffix to add to the knobs, e.g. `_sq`

    Returns:
        Tuple of strings like `(real_knob, imaginary_knob)`
    """
    beam = 2 if beam == 4 else beam
    try:
        return {
            'LHC': (f'cmrs.b{beam}{suffix}', f'cmis.b{beam}{suffix}'),
            'HLLHC': ('cmrskew', 'cmiskew'),
        }[accel.upper()]
    except KeyError:
        raise KeyError(f"Accelerator '{accel}' not recognized.")


def get_tune_and_chroma_knobs(accel: str, beam: int, suffix: str = '') -> tuple[str, str, str, str]:
    """ Get names of knobs to change tune and chromaticity as tuple of strings.

    Args:
        accel: Accelerator either 'LHC' (dQ[xy], dQp[xy] knobs) or
               'HLLHC' (kqt[fd], ks[fd] knobs)
        beam: Beam to use, for the knob names
        suffix (str): suffix to add to the knobs, e.g. `_sq`

    Returns:
        Tuple of strings like `(qx, qy, dqx, dqy)`
    """
    beam = 2 if beam == 4 else beam
    try:
        return {
            'LHC': (f'dQx.b{beam}{suffix}', f'dQy.b{beam}{suffix}', f'dQpx.b{beam}{suffix}', f'dQpy.b{beam}{suffix}'),
            'HLLHC': (f'kqtf.b{beam}{suffix}', f'kqtd.b{beam}{suffix}', f'ksf.b{beam}{suffix}', f'ksd.b{beam}{suffix}'),
        }[accel.upper()]
    except KeyError:
        raise KeyError(f"Accelerator '{accel}' not recognized.")


def get_kqs_for_coupling_correction(beam: int) -> list[str]:
    """ Returns a list of elements for the respective beam as used for coupling correction.

    Args:
        beam: Beam to use

    Returns:
         List of KQS-names.
    """
    beam = 2 if beam == 4 else beam
    names = {
        1: ["R1", "L2", "A23", "R3", "L4", "A45", "R5", "L6", "A67", "R7", "L8", "A81"],
        2: ["A12", "R2", "L3", "A34", "R4", "L5", "A56", "R6", "L7", "A78", "R8", "L1"],
    }
    return [f"KQS.{name:s}B{beam:d}" for name in names[beam]]


# Tune matching ----------------------------------------------------------------

def match_tune(madx: Madx, accel: str, sequence: str,
               qx: float, qy: float,
               dqx: float = None, dqy: float = None,
               step: float = 1e-7, tolerance: float = 1e-21, calls: int = 100,
               knobs_suffix: str = ""):
    """Simple tune (and chromaticity) matching.
    If both are given it matches first tune and dispersion independently and then together.

    Args:
        madx: Madx instance
        accel: Accelerator we are using 'LHC' or 'HLLHC'
        sequence: Sequence to use
        qx: tune to match in x
        qy: tune to match in y
        dqx: chromaticity to match in x
        dqy: chromaticity to match in y
        step: step size to vary knob
        tolerance: tolerance for successfull matching
        calls: number of varying calls
        knobs_suffix: suffix to use with the knobs, e.g.`_sq`
    """
    def match(*args, **kwargs):
        madx.command.match(chrom=True)
        madx.command.global_(sequence=sequence, **kwargs)
        for name in args:
            madx.command.vary(name=name, step=step)
        madx.command.lmdif(calls=calls, tolerance=tolerance)
        madx.command.endmatch()

    LOG.info(f"Tune (and chroma) matching for sequence {sequence}.")
    var_names = get_tune_and_chroma_knobs(accel, int(sequence[-1]), suffix=knobs_suffix)
    match(*var_names[:2], q1=qx, q2=qy)
    if (dqx is not None) and (dqy is not None):
        match(*var_names[2:], dq1=dqx, dq2=dqy)
        calls *= 5
        match(*var_names, q1=qx, q2=qy, dq1=dqx, dq2=dqy)


def closest_tune_approach(madx: Madx, accel: str, sequence: str,
                          qx: float, qy: float, dqx: float, dqy: float,
                          step: float = 1e-7, tolerance: float = 1e-21, calls: float = 100,
                          knobs_suffix: str = ""):
    """ Tries to match the tunes to their mid-fractional tunes.
    The difference between this mid-tune and the actual matched tune is the
    closest tune approach.
    """
    beam = int(sequence[-1])
    saved_values = get_tune_and_chroma_knob_values(madx, accel, beam, suffix=knobs_suffix)
    mid_fraction = .5 * (fractional_tune(qx) + fractional_tune(qy))
    qxmid, qymid = int(qx) + mid_fraction, int(qy) + mid_fraction
    LOG.info("Performing closest tune approach:")
    LOG.info(f"  q1={qxmid}, q2={qymid}.")

    madx.command.match(chrom=True)
    madx.command.global_(sequence=sequence, q1=qxmid, q2=qymid, dq1=dqx, dq2=dqy)
    for name in saved_values:
        madx.command.vary(name=name, step=step)
    madx.command.lmdif(calls=calls, tolerance=tolerance)
    madx.command.endmatch()
    for name, value in saved_values.items():
        madx.globals[name] = value


def get_tune_and_chroma_knob_values(madx: Madx, accel: str, beam: int, suffix: str = "") -> dict:
    """ Saves the current tune and dispersion knob values into list.

    Args:
        madx: Madx instance
        accel: Accelerator we are using 'LHC' or 'HLLHC' see
              :func:`get_tune_and_dispersion_knobs`
        beam: beam we are using
        suffix (str): suffix to add to the knobs, e.g. `_sq`

    Returns:
        Dict of qx, qy, dqx and dqy knob values.
    """
    return {knob: madx.globals[knob] for knob in get_tune_and_chroma_knobs(accel, beam=beam, suffix=suffix)}


# Special Magnet Powering ------------------------------------------------------


def power_landau_octupoles(madx: Madx, mo_current: float, beam: int, defective_arc: bool = False):
    """ Power the landau octupoles.

    Args:
        madx: Madx instance
        mo_current: MO powering in ampere
        beam: beam to use
        defective_arc: If true the KOD in Arc 56 are powered for less Imax

    """
    mvars = madx.globals
    try:
        brho = mvars.nrj*1e9/mvars.clight  # Bending Radius, clight is madx constant
    except AttributeError:
        raise OSError(
            "The global MADX variable 'NRJ' is not defined."
            " It should have been set in the optics files."
            " Otherwise create manually."
        )
    LOG.info(f"Powering the Landau Octupoles for beam {beam} "
             f"at Energy {mvars.nrj} GeV with {mo_current} A.")
    strength = mo_current / mvars.Imax_MO * mvars.Kmax_MO / brho
    beam = 2 if beam == 4 else beam
    for arc in lhc_arc_names(beam):
        for fd in "FD":
            mvars[f"KO{fd}.{arc}"] = strength

    if defective_arc and (beam == 1):
        mvars["KOD.A56B1"] = strength * 4.65/6  # defective MO group


def deactivate_arc_sextupoles(madx: Madx, beam: int):
    """ Deactivates all arc sextupoles.

    Args:
        madx: Madx instance
        beam: beam to use
    """
    # KSF1 and KSD2 - Strong sextupoles of sectors 81/12/45/56
    # KSF2 and KSD1 - Weak sextupoles of sectors 81/12/45/56
    # Rest: Weak sextupoles in sectors 78/23/34/67
    LOG.info(f"Deactivating all arc sextupoles for beam {beam}.")
    beam = 2 if beam == 4 else beam
    for arc in lhc_arc_names(beam):
        for fd in 'FD':
            for i in (1, 2):
                madx.globals[f'KS{fd}{i:d}.{arc}'] = 0.0


# Helper -----------------------------------------------------------------------

def sixtrack_output(madx, energy, outputdir: Path = None):
    """ Prepare output for sixtrack run. """
    # Activate RF-Cavities
    madx.globals["VRF400"] = 8 if energy < 5000 else 16
    madx.globals["LAGRF400.B1"] = 0.5
    madx.globals["LAGRF400.B2"] = 0.

    madx.twiss()  # used by sixtrack
    madx.sixtrack(cavall=True, radius=0.017)
    if outputdir is not None:
        # manually move sixtrack output files
        # (no easy way to specify output dir for them)
        for f in Path().glob("fc*"):
            shutil.move(f, outputdir / f.name)


def fractional_tune(tune):
    """ Returns the fractional tune."""
    return tune - int(tune)


def auto_dtype(df):
    """ Set DataFrame dtypes automatically."""
    try:
        # pandas >= 1.0 functionality with convert_dtypes
        return df.convert_dtypes()
    except AttributeError:
        # fix for pandas < 1.0
        return df.apply(partial(pd.to_numeric, errors='ignore'))


def lhc_arcs() -> list[str]:
    """ Strings of all LHC arcs. """
    return [f"{i}{i%8+1}" for i in range(1, 9)]


def lhc_arc_names(beam: int) -> list[str]:
    """ Names of all arcs for given beam. """
    return [f'A{arc}B{beam:d}' for arc in lhc_arcs()]


def get_k_strings(start: int = 0, stop: int = 8, orientation: str = 'both'):
    """Return all K-column names for a given range.

    Args:
        start: lowest order to include. Default 0.
        stop: highest order + 1 to include (same as in `range()`). Default 8.
        orientation: 'S' for skew, '' for normal, 'both' for both
    """
    if orientation == 'both':
        orientation = ('', 'S')
    elif orientation == 'skew':
        orientation = ('S',)
    else:
        orientation = ('',)

    return [f"K{i:d}{s:s}L" for i in range(start, stop) for s in orientation]


def add_expression(madx: Madx, name: str, expression: str):
    """ Add an expression to a variable that might already
    be a deferred expression.

    Args:
        madx (Madx): Madx instance to incorporate the variable in
        name (str): Name of the variable
        expression (str): Expression to assign
    """
    try:
        old_expression = madx.globals.cmdpar[name].expr
    except KeyError:
        old_expression = None

    if old_expression is not None:
        expression = f"{old_expression} + {expression}"
    madx.globals[name] = expression


@contextmanager
def temp_disable_errors(madx: Madx, *args):
    """ Disable all global variable args and restore their value afterwards."""
    saved = {}
    for arg in args:
        saved[arg] = madx.globals[arg]
        madx.globals[arg] = 0
    yield
    madx.globals.update(saved)
