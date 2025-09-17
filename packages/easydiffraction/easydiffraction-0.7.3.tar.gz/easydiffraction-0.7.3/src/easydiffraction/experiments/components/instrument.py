# SPDX-FileCopyrightText: 2021-2025 EasyDiffraction contributors <https://github.com/easyscience/diffraction>
# SPDX-License-Identifier: BSD-3-Clause

from typing import Optional

from easydiffraction.core.objects import Component
from easydiffraction.core.objects import Parameter
from easydiffraction.experiments.components.experiment_type import BeamModeEnum
from easydiffraction.experiments.components.experiment_type import ScatteringTypeEnum


class InstrumentBase(Component):
    @property
    def category_key(self) -> str:
        return 'instrument'

    @property
    def cif_category_key(self) -> str:
        return 'instr'


class ConstantWavelengthInstrument(InstrumentBase):
    def __init__(
        self,
        setup_wavelength: float = 1.5406,
        calib_twotheta_offset: float = 0.0,
    ) -> None:
        super().__init__()

        self.setup_wavelength: Parameter = Parameter(
            value=setup_wavelength,
            name='wavelength',
            cif_name='wavelength',
            units='Å',
            description='Incident neutron or X-ray wavelength',
        )
        self.calib_twotheta_offset: Parameter = Parameter(
            value=calib_twotheta_offset,
            name='twotheta_offset',
            cif_name='2theta_offset',
            units='deg',
            description='Instrument misalignment offset',
        )

        # Lock further attribute additions to prevent
        # accidental modifications by users
        self._locked: bool = True


class TimeOfFlightInstrument(InstrumentBase):
    def __init__(
        self,
        setup_twotheta_bank: float = 150.0,
        calib_d_to_tof_offset: float = 0.0,
        calib_d_to_tof_linear: float = 10000.0,
        calib_d_to_tof_quad: float = -0.00001,
        calib_d_to_tof_recip: float = 0.0,
    ) -> None:
        super().__init__()

        self.setup_twotheta_bank: Parameter = Parameter(
            value=setup_twotheta_bank,
            name='twotheta_bank',
            cif_name='2theta_bank',
            units='deg',
            description='Detector bank position',
        )
        self.calib_d_to_tof_offset: Parameter = Parameter(
            value=calib_d_to_tof_offset,
            name='d_to_tof_offset',
            cif_name='d_to_tof_offset',
            units='µs',
            description='TOF offset',
        )
        self.calib_d_to_tof_linear: Parameter = Parameter(
            value=calib_d_to_tof_linear,
            name='d_to_tof_linear',
            cif_name='d_to_tof_linear',
            units='µs/Å',
            description='TOF linear conversion',
        )
        self.calib_d_to_tof_quad: Parameter = Parameter(
            value=calib_d_to_tof_quad,
            name='d_to_tof_quad',
            cif_name='d_to_tof_quad',
            units='µs/Å²',
            description='TOF quadratic correction',
        )
        self.calib_d_to_tof_recip: Parameter = Parameter(
            value=calib_d_to_tof_recip,
            name='d_to_tof_recip',
            cif_name='d_to_tof_recip',
            units='µs·Å',
            description='TOF reciprocal velocity correction',
        )

        # Lock further attribute additions to prevent
        # accidental modifications by users
        self._locked: bool = True


class InstrumentFactory:
    ST = ScatteringTypeEnum
    BM = BeamModeEnum
    _supported = {
        ST.BRAGG: {
            BM.CONSTANT_WAVELENGTH: ConstantWavelengthInstrument,
            BM.TIME_OF_FLIGHT: TimeOfFlightInstrument,
        }
    }

    @classmethod
    def create(
        cls,
        scattering_type: Optional[ScatteringTypeEnum] = None,
        beam_mode: Optional[BeamModeEnum] = None,
    ):
        if beam_mode is None:
            beam_mode = BeamModeEnum.default()
        if scattering_type is None:
            scattering_type = ScatteringTypeEnum.default()

        supported_scattering_types = list(cls._supported.keys())
        if scattering_type not in supported_scattering_types:
            raise ValueError(
                f"Unsupported scattering type: '{scattering_type}'.\n "
                f'Supported scattering types: {supported_scattering_types}'
            )

        supported_beam_modes = list(cls._supported[scattering_type].keys())
        if beam_mode not in supported_beam_modes:
            raise ValueError(
                f"Unsupported beam mode: '{beam_mode}' for scattering type: "
                f"'{scattering_type}'.\n "
                f'Supported beam modes: {supported_beam_modes}'
            )

        instrument_class = cls._supported[scattering_type][beam_mode]
        instrument_obj = instrument_class()

        return instrument_obj
