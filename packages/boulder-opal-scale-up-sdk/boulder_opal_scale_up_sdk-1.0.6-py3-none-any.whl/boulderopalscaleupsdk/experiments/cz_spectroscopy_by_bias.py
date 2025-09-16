# Copyright 2025 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.

from typing import Literal

from pydantic import PrivateAttr

from .common import Experiment

DEFAULT_PREP_PADDING_NS = 16
DEFAULT_MEASUREMENT_PADDING_NS = 16
DEFAULT_MIN_DURATION_NS = 16
DEFAULT_MAX_DURATION_NS = 200
DEFAULT_TIME_STEP_NS = 8
DEFAULT_RECYCLE_DELAY_NS = 500_000
DEFAULT_SHOT_COUNT = 200


class CZSpectroscopyByBias(Experiment):
    """
    Parameters for running a Ramsey experiment.

    Parameters
    ----------
    control_transmon : str
        The control transmon to target in the experiment.
    target_transmon : str
        The target transmon to pair with the control transmon.
    min_vp : float
        The minimum voltage point, in volts.
    max_vp : float
        The maximum voltage point, in volts.
    num_vp : int
        The number of voltage points to sample.
    min_duration_ns : int
        The minimum duration for the pulse in the experiment, in nanoseconds.
    max_duration_ns : int
        The maximum duration for the pulse in the experiment, in nanoseconds.
    duration_step_ns : int
        The step size for the duration, in nanoseconds.
    prep_padding_ns : int
        The padding to apply before the CZ pulse, in nanoseconds.
    measurement_padding_ns : int
        The padding to apply after the CZ pulse, in nanoseconds.
    recycle_delay_ns : float
        The delay time between consecutive shots of the experiment, in nanoseconds.
        Defaults to 500000 ns.
    shot_count : int,
        The number of shots to be taken in the experiment.
        Defaults to 200.
    batch_analysis : bool
        Whether to perform batch analysis on the results.
    spectroscopy_waveform : ConstantWaveform
        The waveform to use in the spectroscopy pulse.
    """

    _experiment_name: str = PrivateAttr("cz_spectroscopy_by_bias")

    control_transmon: str
    target_transmon: str
    coupler: str
    min_vp: float
    max_vp: float
    num_vp: int
    coupler_flux_vp: float
    min_duration_ns: int = DEFAULT_MIN_DURATION_NS
    max_duration_ns: int = DEFAULT_MAX_DURATION_NS
    duration_step_ns: int = DEFAULT_TIME_STEP_NS
    prep_padding_ns: int = DEFAULT_PREP_PADDING_NS
    measurement_padding_ns: int = DEFAULT_MEASUREMENT_PADDING_NS
    recycle_delay_ns: int = DEFAULT_RECYCLE_DELAY_NS
    shot_count: int = DEFAULT_SHOT_COUNT
    batch_analysis: bool = False
    update: Literal["auto", "off", "prompt"] = "auto"
