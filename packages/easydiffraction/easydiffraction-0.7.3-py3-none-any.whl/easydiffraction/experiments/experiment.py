# SPDX-FileCopyrightText: 2021-2025 EasyDiffraction contributors <https://github.com/easyscience/diffraction>
# SPDX-License-Identifier: BSD-3-Clause

from abc import abstractmethod
from typing import List
from typing import Optional

import numpy as np

from easydiffraction.core.objects import Datablock
from easydiffraction.experiments.collections.background import BackgroundFactory
from easydiffraction.experiments.collections.background import BackgroundTypeEnum
from easydiffraction.experiments.collections.excluded_regions import ExcludedRegions
from easydiffraction.experiments.collections.linked_phases import LinkedPhases
from easydiffraction.experiments.components.experiment_type import BeamModeEnum
from easydiffraction.experiments.components.experiment_type import ExperimentType
from easydiffraction.experiments.components.experiment_type import RadiationProbeEnum
from easydiffraction.experiments.components.experiment_type import SampleFormEnum
from easydiffraction.experiments.components.experiment_type import ScatteringTypeEnum
from easydiffraction.experiments.components.instrument import InstrumentBase
from easydiffraction.experiments.components.instrument import InstrumentFactory
from easydiffraction.experiments.components.peak import PeakFactory
from easydiffraction.experiments.components.peak import PeakProfileTypeEnum
from easydiffraction.experiments.datastore import DatastoreFactory
from easydiffraction.utils.decorators import enforce_type
from easydiffraction.utils.formatting import paragraph
from easydiffraction.utils.formatting import warning
from easydiffraction.utils.utils import render_cif
from easydiffraction.utils.utils import render_table


class InstrumentMixin:
    def __init__(self, *args, **kwargs):
        expt_type = kwargs.get('type')
        super().__init__(*args, **kwargs)
        self._instrument = InstrumentFactory.create(
            scattering_type=expt_type.scattering_type.value,
            beam_mode=expt_type.beam_mode.value,
        )

    @property
    def instrument(self):
        return self._instrument

    @instrument.setter
    @enforce_type
    def instrument(self, new_instrument: InstrumentBase):
        self._instrument = new_instrument


class BaseExperiment(Datablock):
    """Base class for all experiments with only core attributes.

    Wraps experiment type, instrument and datastore.
    """

    # TODO: Find better name for the attribute 'type'.
    #  1. It shadows the built-in type() function.
    #  2. It is not very clear what it refers to.
    def __init__(self, name: str, type: ExperimentType):
        self.name = name
        self.type = type
        self.datastore = DatastoreFactory.create(
            sample_form=self.type.sample_form.value,
            beam_mode=self.type.beam_mode.value,
        )

    # ---------------
    # Experiment type
    # ---------------

    @property
    def type(self):
        return self._type

    @type.setter
    @enforce_type
    def type(self, new_experiment_type: ExperimentType):
        self._type = new_experiment_type

    # ----------------
    # Misc. Need to be sorted
    # ----------------

    def as_cif(
        self,
        max_points: Optional[int] = None,
    ) -> str:
        """Export the sample model to CIF format.

        Returns:
            str: CIF string representation of the experiment.
        """
        # Data block header
        cif_lines: List[str] = [f'data_{self.name}']

        # Experiment type
        cif_lines += ['', self.type.as_cif()]

        # Instrument setup and calibration
        if hasattr(self, 'instrument'):
            cif_lines += ['', self.instrument.as_cif()]

        # Peak profile, broadening and asymmetry
        if hasattr(self, 'peak'):
            cif_lines += ['', self.peak.as_cif()]

        # Phase scale factors for powder experiments
        if hasattr(self, 'linked_phases') and self.linked_phases._items:
            cif_lines += ['', self.linked_phases.as_cif()]

        # Crystal scale factor for single crystal experiments
        if hasattr(self, 'linked_crystal'):
            cif_lines += ['', self.linked_crystal.as_cif()]

        # Background points
        if hasattr(self, 'background') and self.background._items:
            cif_lines += ['', self.background.as_cif()]

        # Excluded regions
        if hasattr(self, 'excluded_regions') and self.excluded_regions._items:
            cif_lines += ['', self.excluded_regions.as_cif()]

        # Measured data
        if hasattr(self, 'datastore'):
            cif_lines += ['', self.datastore.as_cif(max_points=max_points)]

        return '\n'.join(cif_lines)

    def show_as_cif(self) -> None:
        cif_text: str = self.as_cif(max_points=5)
        paragraph_title: str = paragraph(f"Experiment 🔬 '{self.name}' as cif")
        render_cif(cif_text, paragraph_title)

    @abstractmethod
    def _load_ascii_data_to_experiment(self, data_path: str) -> None:
        pass


class BasePowderExperiment(BaseExperiment):
    """Base class for all powder experiments."""

    def __init__(
        self,
        name: str,
        type: ExperimentType,
    ) -> None:
        super().__init__(name=name, type=type)

        self._peak_profile_type: str = PeakProfileTypeEnum.default(
            self.type.scattering_type.value,
            self.type.beam_mode.value,
        ).value
        self.peak = PeakFactory.create(
            scattering_type=self.type.scattering_type.value,
            beam_mode=self.type.beam_mode.value,
            profile_type=self._peak_profile_type,
        )

        self.linked_phases: LinkedPhases = LinkedPhases()
        self.excluded_regions: ExcludedRegions = ExcludedRegions(parent=self)

    @abstractmethod
    def _load_ascii_data_to_experiment(self, data_path: str) -> None:
        pass

    @property
    def peak_profile_type(self):
        return self._peak_profile_type

    @peak_profile_type.setter
    def peak_profile_type(self, new_type: str):
        if (
            new_type
            not in PeakFactory._supported[self.type.scattering_type.value][
                self.type.beam_mode.value
            ]
        ):
            supported_types = list(
                PeakFactory._supported[self.type.scattering_type.value][
                    self.type.beam_mode.value
                ].keys()
            )
            print(warning(f"Unsupported peak profile '{new_type}'"))
            print(f'Supported peak profiles: {supported_types}')
            print("For more information, use 'show_supported_peak_profile_types()'")
            return
        self.peak = PeakFactory.create(
            scattering_type=self.type.scattering_type.value,
            beam_mode=self.type.beam_mode.value,
            profile_type=new_type,
        )
        self._peak_profile_type = new_type
        print(paragraph(f"Peak profile type for experiment '{self.name}' changed to"))
        print(new_type)

    def show_supported_peak_profile_types(self):
        columns_headers = ['Peak profile type', 'Description']
        columns_alignment = ['left', 'left']
        columns_data = []

        scattering_type = self.type.scattering_type.value
        beam_mode = self.type.beam_mode.value

        for profile_type in PeakFactory._supported[scattering_type][beam_mode]:
            columns_data.append([profile_type.value, profile_type.description()])

        print(paragraph('Supported peak profile types'))
        render_table(
            columns_headers=columns_headers,
            columns_alignment=columns_alignment,
            columns_data=columns_data,
        )

    def show_current_peak_profile_type(self):
        print(paragraph('Current peak profile type'))
        print(self.peak_profile_type)


class PowderExperiment(
    InstrumentMixin,
    BasePowderExperiment,
):
    """Powder experiment class with specific attributes.

    Wraps background, peak profile, and linked phases.
    """

    def __init__(
        self,
        name: str,
        type: ExperimentType,
    ) -> None:
        super().__init__(name=name, type=type)

        self._background_type: BackgroundTypeEnum = BackgroundTypeEnum.default()
        self.background = BackgroundFactory.create(background_type=self.background_type)

    # -------------
    # Measured data
    # -------------

    def _load_ascii_data_to_experiment(self, data_path: str) -> None:
        """Loads x, y, sy values from an ASCII data file into the
        experiment.

        The file must be structured as:
            x  y  sy
        """
        try:
            data = np.loadtxt(data_path)
        except Exception as e:
            raise IOError(f'Failed to read data from {data_path}: {e}') from e

        if data.shape[1] < 2:
            raise ValueError('Data file must have at least two columns: x and y.')

        if data.shape[1] < 3:
            print('Warning: No uncertainty (sy) column provided. Defaulting to sqrt(y).')

        # Extract x, y data
        x: np.ndarray = data[:, 0]
        y: np.ndarray = data[:, 1]

        # Round x to 4 decimal places
        # TODO: This is needed for CrysPy, as otherwise it fails to
        #  match the size of the data arrays.
        x = np.round(x, 4)

        # Determine sy from column 3 if available, otherwise use sqrt(y)
        sy: np.ndarray = data[:, 2] if data.shape[1] > 2 else np.sqrt(y)

        # Replace values smaller than 0.0001 with 1.0
        # TODO: This is needed for minimization algorithms that fail
        #  with very small or zero uncertainties.
        sy = np.where(sy < 0.0001, 1.0, sy)

        # Attach the data to the experiment's datastore

        # The full pattern data
        self.datastore.full_x = x
        self.datastore.full_meas = y
        self.datastore.full_meas_su = sy

        # The pattern data used for fitting (without excluded points)
        # This is the same as full_x, full_meas, full_meas_su by default
        self.datastore.x = x
        self.datastore.meas = y
        self.datastore.meas_su = sy

        # Excluded mask
        # No excluded points by default
        self.datastore.excluded = np.full(x.shape, fill_value=False, dtype=bool)

        print(paragraph('Data loaded successfully'))
        print(f"Experiment 🔬 '{self.name}'. Number of data points: {len(x)}")

    @property
    def background_type(self):
        return self._background_type

    @background_type.setter
    def background_type(self, new_type):
        if new_type not in BackgroundFactory._supported:
            supported_types = list(BackgroundFactory._supported.keys())
            print(warning(f"Unknown background type '{new_type}'"))
            print(f'Supported background types: {supported_types}')
            print("For more information, use 'show_supported_background_types()'")
            return
        self.background = BackgroundFactory.create(new_type)
        self._background_type = new_type
        print(paragraph(f"Background type for experiment '{self.name}' changed to"))
        print(new_type)

    def show_supported_background_types(self):
        columns_headers = ['Background type', 'Description']
        columns_alignment = ['left', 'left']
        columns_data = []
        for bt in BackgroundFactory._supported:
            columns_data.append([bt.value, bt.description()])

        print(paragraph('Supported background types'))
        render_table(
            columns_headers=columns_headers,
            columns_alignment=columns_alignment,
            columns_data=columns_data,
        )

    def show_current_background_type(self):
        print(paragraph('Current background type'))
        print(self.background_type)


# TODO: Refactor this class to reuse PowderExperiment
# TODO: This is not a specific experiment, but rather processed data
#  from PowderExperiment. So, we should think of a better design.
class PairDistributionFunctionExperiment(BasePowderExperiment):
    """PDF experiment class with specific attributes."""

    def __init__(
        self,
        name: str,
        type: ExperimentType,
    ):
        super().__init__(name=name, type=type)

    def _load_ascii_data_to_experiment(self, data_path):
        """Loads x, y, sy values from an ASCII data file into the
        experiment.

        The file must be structured as:
            x  y  sy
        """
        try:
            from diffpy.utils.parsers.loaddata import loadData
        except ImportError:
            raise ImportError('diffpy module not found.') from None
        try:
            data = loadData(data_path)
        except Exception as e:
            raise IOError(f'Failed to read data from {data_path}: {e}') from e

        if data.shape[1] < 2:
            raise ValueError('Data file must have at least two columns: x and y.')

        default_sy = 0.03
        if data.shape[1] < 3:
            print(f'Warning: No uncertainty (sy) column provided. Defaulting to {default_sy}.')

        # Extract x, y, and sy data
        x = data[:, 0]
        # We should also add sx = data[:, 2] to capture the e.s.d. of x.
        # It might be useful in future.
        y = data[:, 1]
        # Using sqrt isn’t appropriate here, as the y-scale isn’t raw
        # counts and includes both positive and negative values. For
        # now, set the e.s.d. to a fixed value of 0.03 if it’s not
        # included in the measured data file. We should improve this
        # later.
        # sy = data[:, 3] if data.shape[1] > 2 else np.sqrt(y)
        sy = data[:, 2] if data.shape[1] > 2 else np.full_like(y, fill_value=default_sy)

        # Attach the data to the experiment's datastore
        self.datastore.x = x
        self.datastore.meas = y
        self.datastore.meas_su = sy

        print(paragraph('Data loaded successfully'))
        print(f"Experiment 🔬 '{self.name}'. Number of data points: {len(x)}")


class SingleCrystalExperiment(BaseExperiment):
    """Single crystal experiment class with specific attributes."""

    def __init__(
        self,
        name: str,
        type: ExperimentType,
    ) -> None:
        super().__init__(name=name, type=type)
        self.linked_crystal = None

    def show_meas_chart(self) -> None:
        print('Showing measured data chart is not implemented yet.')


class ExperimentFactory:
    """Creates Experiment instances with only relevant attributes."""

    _valid_arg_sets = [
        {
            'required': ['cif_path'],
            'optional': [],
        },
        {
            'required': ['cif_str'],
            'optional': [],
        },
        {
            'required': [
                'name',
                'data_path',
            ],
            'optional': [
                'sample_form',
                'beam_mode',
                'radiation_probe',
                'scattering_type',
            ],
        },
        {
            'required': ['name'],
            'optional': [
                'sample_form',
                'beam_mode',
                'radiation_probe',
                'scattering_type',
            ],
        },
    ]

    _supported = {
        ScatteringTypeEnum.BRAGG: {
            SampleFormEnum.POWDER: PowderExperiment,
            SampleFormEnum.SINGLE_CRYSTAL: SingleCrystalExperiment,
        },
        ScatteringTypeEnum.TOTAL: {
            SampleFormEnum.POWDER: PairDistributionFunctionExperiment,
        },
    }

    @classmethod
    def create(cls, **kwargs):
        """Main factory method for creating an experiment instance.

        Validates argument combinations and dispatches to the
        appropriate creation method. Raises ValueError if arguments are
        invalid or no valid dispatch is found.
        """
        # Check for valid argument combinations
        user_args = [k for k, v in kwargs.items() if v is not None]
        if not cls.is_valid_args(user_args):
            raise ValueError(f'Invalid argument combination: {user_args}')

        # Validate enum arguments if provided
        if 'sample_form' in kwargs:
            SampleFormEnum(kwargs['sample_form'])
        if 'beam_mode' in kwargs:
            BeamModeEnum(kwargs['beam_mode'])
        if 'radiation_probe' in kwargs:
            RadiationProbeEnum(kwargs['radiation_probe'])
        if 'scattering_type' in kwargs:
            ScatteringTypeEnum(kwargs['scattering_type'])

        # Dispatch to the appropriate creation method
        if 'cif_path' in kwargs:
            return cls._create_from_cif_path(kwargs)
        elif 'cif_str' in kwargs:
            return cls._create_from_cif_str(kwargs)
        elif 'data_path' in kwargs:
            return cls._create_from_data_path(kwargs)
        elif 'name' in kwargs:
            return cls._create_without_data(kwargs)

    @staticmethod
    def _create_from_cif_path(cif_path):
        """Create an experiment from a CIF file path.

        Not yet implemented.
        """
        # TODO: Implement CIF file loading logic
        raise NotImplementedError('CIF file loading not implemented yet.')

    @staticmethod
    def _create_from_cif_str(cif_str):
        """Create an experiment from a CIF string.

        Not yet implemented.
        """
        # TODO: Implement CIF string loading logic
        raise NotImplementedError('CIF string loading not implemented yet.')

    @classmethod
    def _create_from_data_path(cls, kwargs):
        """Create an experiment from a raw data ASCII file.

        Loads the experiment and attaches measured data from the
        specified file.
        """
        expt_type = cls._make_experiment_type(kwargs)
        scattering_type = expt_type.scattering_type.value
        sample_form = expt_type.sample_form.value
        expt_class = cls._supported[scattering_type][sample_form]
        expt_name = kwargs['name']
        expt_obj = expt_class(name=expt_name, type=expt_type)
        data_path = kwargs['data_path']
        expt_obj._load_ascii_data_to_experiment(data_path)
        return expt_obj

    @classmethod
    def _create_without_data(cls, kwargs):
        """Create an experiment without measured data.

        Returns an experiment instance with only metadata and
        configuration.
        """
        expt_type = cls._make_experiment_type(kwargs)
        scattering_type = expt_type.scattering_type.value
        sample_form = expt_type.sample_form.value
        expt_class = cls._supported[scattering_type][sample_form]
        expt_name = kwargs['name']
        expt_obj = expt_class(name=expt_name, type=expt_type)
        return expt_obj

    @classmethod
    def _make_experiment_type(cls, kwargs):
        """Helper to construct an ExperimentType from keyword arguments,
        using defaults as needed.
        """
        return ExperimentType(
            sample_form=kwargs.get('sample_form', SampleFormEnum.default()),
            beam_mode=kwargs.get('beam_mode', BeamModeEnum.default()),
            radiation_probe=kwargs.get('radiation_probe', RadiationProbeEnum.default()),
            scattering_type=kwargs.get('scattering_type', ScatteringTypeEnum.default()),
        )

    @staticmethod
    def is_valid_args(user_args):
        """Validate user argument set against allowed combinations.

        Returns True if the argument set matches any valid combination,
        else False.
        """
        user_arg_set = set(user_args)
        for arg_set in ExperimentFactory._valid_arg_sets:
            required = set(arg_set['required'])
            optional = set(arg_set['optional'])
            # Must have all required, and only required+optional
            if required.issubset(user_arg_set) and user_arg_set <= (required | optional):
                return True
        return False


class Experiment:
    """User-facing API for creating an experiment.

    Accepts keyword arguments and delegates validation and creation to
    ExperimentFactory.
    """

    def __new__(cls, **kwargs):
        return ExperimentFactory.create(**kwargs)
