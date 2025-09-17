"""
Coupling Knob
-------------

Creates a coupling knob from current optics.
Not implemented yet. TODO!
"""
from __future__ import annotations

import logging
from operator import itemgetter
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
import tfs

from cpymad_lhc.general import add_expression, get_coupling_knobs, get_tfs, lhc_arcs

if TYPE_CHECKING:
    from collections.abc import Sequence

    from cpymad.madx import Madx


LOG = logging.getLogger(__name__)

COL_REFERENCE = "Reference"


def replace_k0(attribute):
    replacements_map = {"k0l": "angle", "k0sl": "tilt"}
    if attribute in replacements_map:
        new_attribute = replacements_map[attribute]
        LOG.info(f"Attribute {attribute} is being replaced with {new_attribute}")
        attribute = new_attribute


def get_attribute_response(madx: Madx, sequence: str, variables: Sequence[str], attribute: str) -> pd.DataFrame:
    """ Creates the linear response matrix of the given `variables` for the desired `attributed`. """
    # find elements in sequence that have the attribute defined
    valid_elements = {e.name: idx for idx, e in enumerate(madx.sequence[sequence].elements) if attribute in e}
    if not len(valid_elements):
        raise AttributeError(f"No elements found in sequence '{sequence}' with attribute '{attribute}'.")

    get_valid_elements = itemgetter(*valid_elements.values())

    def get_attribute_values():
        return np.array([e[attribute] for e in get_valid_elements(madx.sequence[sequence].elements)])

    # create DataFrame
    df = pd.DataFrame(index=valid_elements.keys(), columns=variables)

    # all-zero reference
    for var in variables:
        madx.globals[var] = 0
    reference = get_attribute_values()

    # responses
    for var in variables:
        madx.globals[var] = 1
        df[var] = get_attribute_values() - reference
        madx.globals[var] = 0

    # drop all-zero rows
    return df.loc[(df!=0).any(axis=1)]


# Old-School Coupling Knobs -------------------
SINGLE_KQS_LISTS = {
# Sectors with commonly powered MQSs
    1: ['23', '45', '67', '81'],
    2: ['12', '34', '56', '78'],
}


def calculate_coupling_coefficients_per_sector(
        df: tfs.TfsDataFrame,
        deactivate_sectors: Sequence[str] = ('12', '45', '56', '81')
    ) -> tfs.TfsDataFrame:
    """ Calculate the coupling knob coefficients as in corr_MB_ats_v4.
    This is basically Eq. (59) in https://cds.cern.ch/record/522049/files/lhc-project-report-501.pdf ,
    with cosine for the real part and sine for the imaginary part.
    What is happening here is, that we are building a matrix for the equation-system
    M * [MQS12,..., MQS81] = -[RE, IM]
    where RE and IM are the real and imaginary parts of the coupling coefficients,
    and therefore the knobs we want to create.
    MQS12 - MQS81 is the total powering of the MQS per arc, which we steer with
    the knob. All MQS in a single arc are assumed to be powered equally.
    After building the matrix, we "solve" the equation system via pseudo-inverese M+
    and get therefore the definition of the coupling knob.
    [MQS12,..., MQS81] = - M+ * [RE, IM]
    HINT: The MINN function in corr_MB_ats_v4 is simply the calculation the pseudo-inverse:
    M+  = M' (M * M')^-1  (' = transpose, ^-1 = inverse)
    including the minus on the rhs of the equation.

    TODO:
      - Get beta and phases from the beamline directly (instead of the TFS dataframe)
      - Make the number of MQS more flexible, could maybe be parsed from the beamline
      - Why is there an absolute value in Eq. (59) but not in the code? (see also https://cds.cern.ch/record/2778887/files/CERN-ACC-NOTE-2021-0022.pdf)
      - Add a2 correction to the KQS definition (as in corr_MB_ats_v4)
      - Include the actual fractional tune split of the current machine (see also https://cds.cern.ch/record/2778887/files/CERN-ACC-NOTE-2021-0022.pdf)
      - Calculate also the contribution to f_1010 and try to set to zero
      - Does this still work when slicing the MQS?

    Args:
        df (tfs.TfsDataFrame):
            Dataframe containing the optics of the machine.
        deactivate_sectors (Sequence[str], optional):
            Deactivate these sectors, i.e. don't use their MQS.
            Defaults to ('12', '45', '56', '81'), the ATS sectors.

    """
    BETX, BETY, MUX, MUY = "BETX", "BETY", "MUX", "MUY"  # noqa: N806
    MQS_PER_SECTOR = 4  # TODO: get from line (?)  # noqa: N806
    LENGTH_MQS = 0.32  # TODO: get from l.mqs  # noqa: N806

    sectors = lhc_arcs()

    mqs_sectors = [fr"MQS\..*(R{s[0]}|L{s[1]})\.B" for s in sectors]
    m = np.ndarray([2, len(sectors)])

    for idx_sector, mqs_regex in enumerate(mqs_sectors):
        sector_mqs_slices = df.index.str.match(mqs_regex)
        df_mqs = df.loc[sector_mqs_slices]

        contribution_per_slice = MQS_PER_SECTOR / len(df_mqs)  # Knobs are not automatically normalized on slicing?
        coeff = contribution_per_slice * np.sqrt(df_mqs[BETX] * df_mqs[BETY])
        phase = 2*np.pi * (df_mqs[MUX] - df_mqs[MUY])

        for idx, fun in enumerate((np.cos, np.sin)):
            m[idx, idx_sector] =  (coeff * fun(phase)).sum()

    m = m * LENGTH_MQS  / (2 * np.pi)  # kqs knobs are multiplied by the length of the MQS

    if deactivate_sectors:
        mask = [s in deactivate_sectors for s in sectors]
        m[: , mask] = 0

    result = tfs.TfsDataFrame(
        data=-np.linalg.pinv(m),
        index=sectors,
        columns=["re", "im"]
    )

    # remove numerical noise:
    return result.where(result.abs() > 1e-15, 0)


def create_coupling_knobs(madx: Madx, beam: int, accel: str, optics: Path | tfs.TfsDataFrame | None = None):
    """ Create coupling knobs in the beam-line.
    WARNING: This function will not take a2 errors into account!
    Normally, the a2 errors are also corrected with the MQS, but in this function
    the MQS powering is fully controlled by the coupling knobs.
    See also the todo's in :func:`xmask.lhc.knob_manipulations.calculate_coupling_coefficients_per_sector`

    Args:
        madx (Madx): Madx instance to incorporate the knobs in
        beam (int): Beam number.
        optics (Path, tfs.TfsDataFrame, optional):
            Path or TfsDataFrame of the twiss containing the optics to be used.
            If not given, a twiss will be computed. Defaults to None.

    """
    LOG.info(f"Creating Coupling Knobs for beam {beam} ---")
    mvars = madx.globals

    if beam == 4:
        beam = 2  # same behaviour in this case

    beam_sign = 1 if beam == 1 else -1


    if optics is None:
        madx.twiss()
        df = get_tfs(madx.table.twiss)
    elif isinstance(optics, Path):
        df = tfs.read(optics, index="NAME")
    else:
        df = optics

    assert int(df.headers["SEQUENCE"][-1]) == beam, f"Wrong optics file for beam {beam}!"

    df = beam_sign * calculate_coupling_coefficients_per_sector(df)

    knob_name_real, knob_name_imag = get_coupling_knobs(accel, beam)

    mvars[knob_name_real] = 0
    mvars[knob_name_imag] = 0

    for sector in df.index:
        coeff_real = df.loc[sector, "re"]
        coeff_imag = df.loc[sector, "im"]

        coeff_name_real = f"coeff_skew_re_arc{sector}_b{beam}"
        coeff_name_imag = f"coeff_skew_im_arc{sector}_b{beam}"

        mvars[coeff_name_real] = coeff_real
        mvars[coeff_name_imag] = coeff_imag

        definition_str = f"{coeff_name_real} * {knob_name_real} + {coeff_name_imag} * {knob_name_imag}"

        if sector in SINGLE_KQS_LISTS[beam]:
            add_expression(madx, f"kqs.a{sector}b{beam}", definition_str)
        else:
            add_expression(madx, f"kqs.r{sector[0]}b{beam}", definition_str)
            add_expression(madx, f"kqs.l{sector[1]}b{beam}", definition_str)
