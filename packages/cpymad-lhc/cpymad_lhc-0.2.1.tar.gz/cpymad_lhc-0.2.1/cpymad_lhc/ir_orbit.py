"""
IR Orbit
----------

Functions to setup and check the orbit in the IRs.

The values in the `on_` knobs (see `CROSSING_SCHEMES` and `get_orbit_variables()`)
refer to the settings in mm and urad in Beam 1 (i.e. not only the Beam 1
reference frame but Beam 1 itself). Beam 2 or Beam 4 are then configured
accordingly. To check the twiss if everything is set correctly, the following
symmetry/sign relations should hold true:

Beam 1 and Beam 2 share coordinate system.
Crossing angles - opposite sign
Crossing offsets (same plane) - same sign
Separation - opposite sign

Beam 1 and Beam 4 have x-axis inverted.
Y Crossing Angles - same sign
Y Crossing offsets - same sign (i.e. same side)
X Separation - same sign (i.e. opposite sides)

X Crossing Angles - opposite sign
X Crossing offsets - opposite sign (i.e. same sides)
Y Separation - opposite sign (i.e. opposite sides)
"""
from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING

import numpy as np

from cpymad_lhc.general import get_tfs

if TYPE_CHECKING:
    from collections.abc import Iterable

    from cpymad.madx import Madx
    from pandas import DataFrame
    from tfs import TfsDataFrame


LOG = logging.getLogger(__name__)


def crossing_schemes(scheme: str, accel: str, year: int = 2018) -> dict[str, float]:  # from tracking masks
    if scheme == 'flat':
        return {}

    if accel == 'lhc':
        # Old crossing variables before run III
        if year < 2020:
            return{
                'inj': {
                    'on_x1':  170, 'on_sep1': -2,
                    'on_x2':  170, 'on_sep2': 3.5,
                    'on_x5':  170, 'on_sep5': 2,
                    'on_x8': -170, 'on_sep8': -3.5,
                    'phi_ir1': 90, 'phi_ir5': 0,
                    'phi_ir2': 90, 'phi_ir8': 180,
                },
                'top': {
                    'on_x1':  160, 'on_sep1': -0.55,
                    'on_x2':  200, 'on_sep2': 1.4,
                    'on_x5':  160, 'on_sep5': 0.55,
                    'on_x8': -250, 'on_sep8': -1,
                    'phi_ir1': 90, 'phi_ir5': 0,
                    'phi_ir2': 90, 'phi_ir8': 180,
                },
            }[scheme]

        # New crossing variables since run III
        return {
            'top': {
                'on_x1_v': -160, 'on_sep1_h': -0.55,
                'on_x1_h':    0, 'on_sep1_v':  0.0,
                'on_x2v':   200, 'on_sep2h':   1.0,
                'on_x2h':     0, 'on_sep2v':   0.0,
                'on_x5_h':  160, 'on_sep5_v':  0.55,
                'on_x5_v':    0, 'on_sep5_h':  0.0,
                'on_x8h':  -200, 'on_sep8v':  -1.0,
                'on_x8v':     0, 'on_sep8h':   0.0,
            },
        }[scheme]

    if accel == 'hllhc':
        return {
            'inj': {
                'on_x1':  295, 'on_sep1': -2,
                'on_x2':  170, 'on_sep2': 3.5, 'on_a2': -40,
                'on_x5':  295, 'on_sep5': 2,
                'on_x8': -170, 'on_sep8': -3.5, 'on_a8': -40,
                'on_crab1': 0, 'on_crab5': 0,
                'phi_ir1': 0, 'phi_ir5': 90,
                'phi_ir2': 90, 'phi_ir8': 0,
            },
            'top': {
                'on_x1':  250, 'on_sep1': -0.75,
                'on_x2':  170, 'on_sep2': 1,
                'on_x5':  250, 'on_sep5': 0.75,
                'on_x8': -200, 'on_sep8': -1,
                'on_crab1': -190, 'on_crab5': -190,
                'phi_ir1': 0, 'phi_ir5': 90,
                'phi_ir2': 90, 'phi_ir8': 0,
            },
        }[scheme]

    raise KeyError(f"Unknown crossing scheme: {scheme}")


def get_orbit_variables(accel: str, year: int = 2018):
    """ Get the variable names used for orbit setup.
    Args:
        accel (str): 'lhc' or 'hllhc'
        year (int): year of the models/optics (for 'lhc')

    Returns:
        tuple of 0: list of all orbit variables, apart form those in 1
                 1: dictionary of additional variables, that in the
                    default configurations have the same value as another variable

    """
    if accel == "hllhc":
        on_variables = (
            'crab1', 'crab5',  # exists only in HL-LHC
            'x1', 'sep1', 'o1', 'a1',
            'x2', 'sep2', 'o2', 'a2',
            'x5', 'sep5', 'o5', 'a5',
            'x8', 'sep8', 'o8', 'a8',
            'alice', 'sol_alice', 'lhcb', 'sol_atlas', 'sol_cms',
        )
        special = {}
    else:
        if year < 2020:
            on_variables = (
                'x1', 'sep1', 'o1', 'oh1', 'ov1',
                'x2', 'sep2', 'o2', 'oe2', 'a2', 'oh2', 'ov2',
                'x5', 'sep5', 'o5', 'oh5', 'ov5',
                'x8', 'sep8', 'o8', 'a8', 'sep8h', 'x8v', 'oh8', 'ov8',
                'alice', 'sol_alice', 'lhcb', 'sol_atlas', 'sol_cms',
            )
            special = {'on_ssep1': 'on_sep1', 'on_xx1': 'on_x1',
                       'on_ssep5': 'on_sep5', 'on_xx5': 'on_x5',
                       }
        else:
            on_variables = (
                'x1_v', 'sep1_v', 'x1_h', 'sep1_h',
                'x5_v', 'sep5_v', 'x5_h', 'sep5_h',
                'x2v', 'sep2v', 'x2h', 'sep2h', 'o2', 'a2', 'oh2', 'ov2',
                'x8v', 'sep8v', 'x8h', 'sep8h', 'o8', 'a8', 'oh8', 'ov8',
                'alice', 'sol_alice', 'lhcb', 'sol_atlas', 'sol_cms',
            )
            special = {}
    variables = [f'on_{var}' for var in on_variables] + [f'phi_ir{ir:d}' for ir in (1, 2, 5, 8)]
    return variables, special


def orbit_setup(madx: Madx, accel: str, year: int = 2018, **kwargs):
    """ Automated orbit setup for some default schemes.
    Please check if these are still valid.

    Args:
        madx: Madx instance
        accel (str): 'lhc' or 'hllhc'
        year (int): year of the models/optics (for 'lhc')

    Keyword Args:
        scheme: default orbit scheme to apply.
                Choices: 'flat', 'inj', 'top', None
                Default: 'flat' (all values 0)
        other: All standard crossing scheme variables. Values given here override
               the values in the scheme, which in turn override the ones already set.
               If the value of a variable is `None`, the variable is not used
               (i.e. the value in the `madx.globals` is kept).

    Returns:
        dictionary with current settings of the scheme.
    """
    kwargs = {k.lower(): v for k, v in kwargs.items()}
    variables, special = get_orbit_variables(accel, year)
    scheme_key = kwargs.get('scheme', 'flat')
    mvars = madx.globals
    full_scheme = {}
    scheme = {}
    default = None

    def set_value(key, value):
        if value is not None:
            mvars[key] = full_scheme[key] = value
        else:
            full_scheme[key] = mvars[key]

    if scheme_key is not None:
        default = 0
        scheme = crossing_schemes(scheme=scheme_key, accel=accel, year=year)

    for var in variables:
        set_value(var, kwargs.get(var, scheme.get(var, default)))

    for key, reference in special.items():
        set_value(key, kwargs.get(key, reference))

    return full_scheme


def get_current_orbit_scheme(madx: Madx, accel: str, year: int = 2018):
    """ Get the current values for the orbit variales.

    Args:
        madx: Madx instance
        accel (str): 'lhc' or 'hllhc'
        year (int): year of the models/optics (for 'lhc')

    Returns:
        Dictionary of all orbit variables and their value/definition.

    """
    variables, special = get_orbit_variables(accel, year)
    return {var: madx.globals.defs[var] for var in variables + list(special.keys()) if var in madx.globals}


def check_crabbing(madx: Madx, auto_set: bool = False):
    """ Check that the crabbing is not larger than the crossing angle.

    Args:
        madx: Madx instance
        auto_set: instead of throwing an error, set the crabbing to the xing.
    """
    for ip in (1, 5):
        on_crab = f"on_crab{ip:d}"
        on_xing = f"on_x{ip:d}"
        crab = madx.globals[on_crab]
        xing = madx.globals[on_xing]
        if abs(crab) > abs(xing):
            text = f"{on_crab} = {crab} is larger than {on_xing} = {xing}."
            if auto_set:
                LOG.warning(text)
                LOG.warning(f"Limiting {on_crab}!")
                madx.globals[on_crab] = np.sign(crab) * abs(xing)
            else:
                raise ValueError(text)


# Orbit Checks -----------------------------------------------------------------


def log_orbit(
    madx: Madx,
    accel: str,
    year: int = 2018,
    twiss: TfsDataFrame | None = None,
    ip: Iterable[int] | int | None = None
    ):
    """ Get the orbit from madx-instance and twiss-dataframe and
    log the configuration per IP. """
    if twiss is None:
        twiss = get_tfs(madx.table.twiss, columns=['NAME', 'S', 'X', 'Y', 'PX', 'PY'])

    variables = get_current_orbit_scheme(madx, accel, year)  # takes a few seconds, so do here
    for ip in _get_ip_iterable(ip):
        log_orbit_from_madx(madx, accel=accel, year=year, ip=ip, variables=variables)
        log_orbit_from_twiss(twiss, ip)


def log_orbit_from_madx(
    madx: Madx,
    accel: str,
    year: int = 2018,
    ip: Iterable[int] | int | None = None,
    variables: Iterable[str] | None = None,
    ):
    """ Log current orbit scheme sorted by IP. """
    if variables is None:
        variables = get_current_orbit_scheme(madx, accel, year)

    for ip in _get_ip_iterable(ip):
        for k, v in variables.items():
            if str(ip) in k:
                LOG.info(f"{k} = {v}")


def log_orbit_from_twiss(twiss: TfsDataFrame, ip: Iterable[int] | int | None = None):
    """ Log orbit from twiss-dataframe. """
    for ip in _get_ip_iterable(ip):
        ip_marker = f'IP{ip:d}'
        try:
            next_element = _get_next_element(twiss, ip)
        except ValueError:
            next_element = None

        for plane in ('X', 'Y'):
            try:
                offset = twiss.loc[ip_marker, plane]
            except KeyError:
                offset_txt = '-unknown-'
            else:
                offset_txt = f'{offset*1e3:.2f} mm'

            xing = ''
            if next_element is not None:
                angle = _get_angle(twiss, ip_marker, next_element, plane)
                xing += f'{angle*1e6:.2f} urad (calc) '

            try:
                angle_p = twiss.loc[ip_marker, f'P{plane}']
            except KeyError:
                pass
            else:
                xing += f'{angle_p*1e6:.2f} urad (p{plane.lower()}) '

            if not len(xing):
                xing = '-unknown-'

            LOG.info(f"IP{ip:d} {plane}: xing {xing}, offset {offset_txt}")


def _get_angle(twiss: TfsDataFrame, ip_name: str, element: str, plane: str):
    """ Get the beam angle at the IP calculated from the orbit at `element`."""
    length = np.inf
    try:
        length = twiss.headers["LENGTH"]
    except KeyError:
        LOG.warning("No length found in twiss. This might cause problems, if"
                    "your IP is near the wrap-around point of the ring"
                    "as there is no way of knowing how to wrap around.")
    ds = twiss.loc[element, "S"] - twiss.loc[ip_name, "S"]
    if abs(ds) > length / 2:
        ds += length if ds < 0 else -length
    dz = twiss.loc[element, plane] - twiss.loc[ip_name, plane]
    return np.arctan(dz / ds)


def _get_ip_iterable(ip: Iterable[int] | int | None) -> Iterable[int]:
    """ Returns `ip` as iterable, or tuple of all ips if `ip` is `None`. """
    if ip is None:
        return 1, 2, 5, 8
    if isinstance(ip, int):
        return ip,
    return ip


def _get_next_element(twiss: DataFrame, ip: int):
    """ Get the next element after the IP. """
    idx_ip = twiss.index.get_loc(f"IP{ip:d}")
    idx = 0
    while True:
        idx += 1
        element = twiss.index[(idx_ip + idx) % len(twiss.index)]
        match = re.match(fr'(MQ|BPM).*(?P<pos>\d)[LR]{ip:d}(\.B\d)?$', element)
        LOG.debug(f"Checking element: {element}")

        if match is not None:
            pos = int(match.group('pos'))
            if pos == 1:
                LOG.debug(f"Next Element to IP{ip} found: {element}")
                return element
            break
        if idx >= 200:
            break
    raise ValueError(f"No suitable element for angle-calculation found in IP{ip}")
