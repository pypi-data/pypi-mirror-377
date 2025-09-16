from enum import Enum
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional
from .pydantic_config import SageConfig

class ParameterType(Enum):
    NUMERIC = "numeric"
    STRING = "string"
    STRING_LIST = "string_list"
    BOOLEAN = "boolean"
    MULTISELECT = "multiselect"
    SELECT = "select"


@dataclass
class Parameter:
    """Dataclass representing a configuration parameter"""
    name: str
    param_type: ParameterType
    getter: Callable[[SageConfig], Any]
    setter: Callable[[SageConfig, Any], None]
    options: Optional[List[Any]] = None
    description: Optional[str] = None
    
    @property
    def display_name(self) -> str:
        """Generate human-readable name from enum"""
        return ' '.join(word.capitalize() for word in self.name.split('_'))

    @property
    def enum_name(self) -> str:
        """Get the raw enum name"""
        return self.name
    
    def get_value(self, config: SageConfig) -> Any:
        """Get the current value of this parameter from the config"""
        return self.getter(config)
    
    def set_value(self, config: SageConfig, value: Any) -> None:
        """Set the value of this parameter in the config"""
        self.setter(config, value)
    
    def validate_value(self, value: Any) -> bool:
        """Validate that a value is appropriate for this parameter"""
        if self.param_type == ParameterType.BOOLEAN:
            return isinstance(value, bool)
        elif self.param_type == ParameterType.NUMERIC:
            return isinstance(value, (int, float))
        elif self.param_type == ParameterType.STRING:
            return isinstance(value, str)
        elif self.param_type == ParameterType.SELECT:
            return value in self.options if self.options else True
        elif self.param_type == ParameterType.MULTISELECT:
            return (isinstance(value, (list, tuple)) and 
                    all(item in self.options for item in value) if self.options else True) # type: ignore
        return True


class ParameterEnum(Enum):
    """Enumeration of all editable Sage configuration parameters."""
    PRECURSOR_TOL_MIN_VALUE = Parameter(
        name='PRECURSOR_TOL_MIN_VALUE',
        param_type=ParameterType.NUMERIC,
        getter=lambda config: config.precursor_tol.value[0],
        setter=lambda config, value: setattr(config.precursor_tol, 'value', [value, config.precursor_tol.value[1]]),
        description="Minimum precursor tolerance value"
    )
    PRECURSOR_TOL_MAX_VALUE = Parameter(
        name='PRECURSOR_TOL_MAX_VALUE',
        param_type=ParameterType.NUMERIC,
        getter=lambda config: config.precursor_tol.value[1],
        setter=lambda config, value: setattr(config.precursor_tol, 'value', [config.precursor_tol.value[0], value]),
        description="Maximum precursor tolerance value"
    )
    PRECURSOR_TOL_UNIT = Parameter(
        name='PRECURSOR_TOL_UNIT',
        param_type=ParameterType.SELECT,
        getter=lambda config: config.precursor_tol.unit,
        setter=lambda config, value: setattr(config.precursor_tol, 'unit', value),
        options=["ppm", "da"],
        description="Unit for precursor tolerance"
    )
    FRAGMENT_TOL_MIN_VALUE = Parameter(
        name='FRAGMENT_TOL_MIN_VALUE',
        param_type=ParameterType.NUMERIC,
        getter=lambda config: config.fragment_tol.value[0],
        setter=lambda config, value: setattr(config.fragment_tol, 'value', [value, config.fragment_tol.value[1]]),
        description="Minimum fragment tolerance value"
    )
    FRAGMENT_TOL_MAX_VALUE = Parameter(
        name='FRAGMENT_TOL_MAX_VALUE',
        param_type=ParameterType.NUMERIC,
        getter=lambda config: config.fragment_tol.value[1],
        setter=lambda config, value: setattr(config.fragment_tol, 'value', [config.fragment_tol.value[0], value]),
        description="Maximum fragment tolerance value"
    )
    FRAGMENT_TOL_UNIT = Parameter(
        name='FRAGMENT_TOL_UNIT',
        param_type=ParameterType.SELECT,
        getter=lambda config: config.fragment_tol.unit,
        setter=lambda config, value: setattr(config.fragment_tol, 'unit', value),
        options=["ppm", "da"],
        description="Unit for fragment tolerance"
    )
    DATABASE_ENZYME_MISSED_CLEAVAGES = Parameter(
        name='DATABASE_ENZYME_MISSED_CLEAVAGES',
        param_type=ParameterType.NUMERIC,
        getter=lambda config: config.database.enzyme.missed_cleavages,
        setter=lambda config, value: setattr(config.database.enzyme, 'missed_cleavages', int(value)),
        description="Number of missed cleavages allowed"
    )
    DATABASE_ENZYME_MIN_LEN = Parameter(
        name='DATABASE_ENZYME_MIN_LEN',
        param_type=ParameterType.NUMERIC,
        getter=lambda config: config.database.enzyme.min_len,
        setter=lambda config, value: setattr(config.database.enzyme, 'min_len', int(value)),
        description="Minimum peptide length"
    )
    DATABASE_ENZYME_MAX_LEN = Parameter(
        name='DATABASE_ENZYME_MAX_LEN',
        param_type=ParameterType.NUMERIC,
        getter=lambda config: config.database.enzyme.max_len,
        setter=lambda config, value: setattr(config.database.enzyme, 'max_len', int(value)),
        description="Maximum peptide length"
    )
    DATABASE_ENZYME_CLEAVE_AT = Parameter(
        name='DATABASE_ENZYME_CLEAVE_AT',
        param_type=ParameterType.STRING,
        getter=lambda config: config.database.enzyme.cleave_at,
        setter=lambda config, value: setattr(config.database.enzyme, 'cleave_at', value),
        description="Amino acids where enzyme cleaves"
    )
    DATABASE_ENZYME_RESTRICT = Parameter(
        name='DATABASE_ENZYME_RESTRICT',
        param_type=ParameterType.STRING,
        getter=lambda config: config.database.enzyme.restrict,
        setter=lambda config, value: setattr(config.database.enzyme, 'restrict', value),
        description="Amino acids that restrict cleavage"
    )
    DATABASE_ENZYME_TERMINAL = Parameter(
        name='DATABASE_ENZYME_TERMINAL',
        param_type=ParameterType.BOOLEAN,
        getter=lambda config: config.database.enzyme.c_terminal,
        setter=lambda config, value: setattr(config.database.enzyme, 'c_terminal', value),
        options=[True, False],
        description="Whether enzyme cleaves at C-terminal"
    )
    DATABASE_ENZYME_SEMI_ENZYMATIC = Parameter(
        name='DATABASE_ENZYME_SEMI_ENZYMATIC',
        param_type=ParameterType.BOOLEAN,
        getter=lambda config: config.database.enzyme.semi_enzymatic,
        setter=lambda config, value: setattr(config.database.enzyme, 'semi_enzymatic', value),
        options=[True, False],
        description="Allow semi-enzymatic cleavage"
    )
    DATABASE_ION_KINDS = Parameter(
        name='DATABASE_ION_KINDS',
        param_type=ParameterType.MULTISELECT,
        getter=lambda config: config.database.ion_kinds,
        setter=lambda config, value: setattr(config.database, 'ion_kinds', value),
        options=["a", "b", "c", "x", "y", "z"],
        description="Types of ions to consider"
    )
    QUANT_TMT = Parameter(
        name='QUANT_TMT',
        param_type=ParameterType.SELECT,
        getter=lambda config: config.quant.tmt,
        setter=lambda config, value: setattr(config.quant, 'tmt', value),
        options=["Tmt6", "Tmt10", "Tmt11", "Tmt16", "Tmt18", None],
        description="TMT quantification type"
    )
    QUANT_LFQ = Parameter(
        name='QUANT_LFQ',
        param_type=ParameterType.BOOLEAN,
        getter=lambda config: config.quant.lfq,
        setter=lambda config, value: setattr(config.quant, 'lfq', value),
        options=[True, False],
        description="Enable label-free quantification"
    )
    QUANT_TMT_SETTINGS_LEVEL = Parameter(
        name='QUANT_TMT_SETTINGS_LEVEL',
        param_type=ParameterType.NUMERIC,
        getter=lambda config: config.quant.tmt_settings.level,
        setter=lambda config, value: setattr(config.quant.tmt_settings, 'level', int(value)),
        description="TMT quantification level"
    )
    QUANT_TMT_SETTINGS_SN = Parameter(
        name='QUANT_TMT_SETTINGS_SN',
        param_type=ParameterType.BOOLEAN,
        getter=lambda config: config.quant.tmt_settings.sn,
        setter=lambda config, value: setattr(config.quant.tmt_settings, 'sn', value),
        options=[True, False],
        description="Use signal/noise for TMT quantification"
    )
    QUANT_LFQ_SETTINGS_PEAK_SCORING = Parameter(
        name='QUANT_LFQ_SETTINGS_PEAK_SCORING',
        param_type=ParameterType.STRING,
        getter=lambda config: config.quant.lfq_settings.peak_scoring,
        setter=lambda config, value: setattr(config.quant.lfq_settings, 'peak_scoring', value),
        description="Peak scoring method for LFQ"
    )
    QUANT_LFQ_SETTINGS_INTEGRATION = Parameter(
        name='QUANT_LFQ_SETTINGS_INTEGRATION',
        param_type=ParameterType.SELECT,
        getter=lambda config: config.quant.lfq_settings.integration,
        setter=lambda config, value: setattr(config.quant.lfq_settings, 'integration', value),
        options=["Sum", "Apex"],
        description="Integration method for LFQ"
    )
    QUANT_LFQ_SETTINGS_SPECTRAL_ANGLE = Parameter(
        name='QUANT_LFQ_SETTINGS_SPECTRAL_ANGLE',
        param_type=ParameterType.NUMERIC,
        getter=lambda config: config.quant.lfq_settings.spectral_angle,
        setter=lambda config, value: setattr(config.quant.lfq_settings, 'spectral_angle', float(value)),
        description="Spectral angle threshold for LFQ"
    )
    QUANT_LFQ_SETTINGS_PPM_TOLERANCE = Parameter(
        name='QUANT_LFQ_SETTINGS_PPM_TOLERANCE',
        param_type=ParameterType.NUMERIC,
        getter=lambda config: config.quant.lfq_settings.ppm_tolerance,
        setter=lambda config, value: setattr(config.quant.lfq_settings, 'ppm_tolerance', float(value)),
        description="PPM tolerance for LFQ"
    )
    QUANT_LFQ_SETTINGS_MOBILITY_PCT_TOLERANCE = Parameter(
        name='QUANT_LFQ_SETTINGS_MOBILITY_PCT_TOLERANCE',
        param_type=ParameterType.NUMERIC,
        getter=lambda config: config.quant.lfq_settings.mobility_pct_tolerance,
        setter=lambda config, value: setattr(config.quant.lfq_settings, 'mobility_pct_tolerance', float(value)),
        description="Mobility percentage tolerance for LFQ"
    )
    QUANT_LFQ_SETTINGS_COMBINE_CHARGE_STATES = Parameter(
        name='QUANT_LFQ_SETTINGS_COMBINE_CHARGE_STATES',
        param_type=ParameterType.BOOLEAN,
        getter=lambda config: config.quant.lfq_settings.combine_charge_states,
        setter=lambda config, value: setattr(config.quant.lfq_settings, 'combine_charge_states', value),
        options=[True, False],
        description="Combine charge states in LFQ"
    )
    DATABASE_BUCKET_SIZE = Parameter(
        name='DATABASE_BUCKET_SIZE',
        param_type=ParameterType.NUMERIC,
        getter=lambda config: config.database.bucket_size,
        setter=lambda config, value: setattr(config.database, 'bucket_size', int(value)),
        description="Database bucket size"
    )
    DATABASE_FASTA = Parameter(
        name='DATABASE_FASTA',
        param_type=ParameterType.STRING,
        getter=lambda config: config.database.fasta,
        setter=lambda config, value: setattr(config.database, 'fasta', value),
        description="Path to FASTA database file"
    )
    DATABASE_PEPTIDE_MIN_MASS = Parameter(
        name='DATABASE_PEPTIDE_MIN_MASS',
        param_type=ParameterType.NUMERIC,
        getter=lambda config: config.database.peptide_min_mass,
        setter=lambda config, value: setattr(config.database, 'peptide_min_mass', float(value)),
        description="Minimum peptide mass"
    )
    DATABASE_PEPTIDE_MAX_MASS = Parameter(
        name='DATABASE_PEPTIDE_MAX_MASS',
        param_type=ParameterType.NUMERIC,
        getter=lambda config: config.database.peptide_max_mass,
        setter=lambda config, value: setattr(config.database, 'peptide_max_mass', float(value)),
        description="Maximum peptide mass"
    )
    DATABASE_MIN_ION_INDEX = Parameter(
        name='DATABASE_MIN_ION_INDEX',
        param_type=ParameterType.NUMERIC,
        getter=lambda config: config.database.min_ion_index,
        setter=lambda config, value: setattr(config.database, 'min_ion_index', int(value)),
        description="Minimum ion index"
    )
    DATABASE_DECOY_TAG = Parameter(
        name='DATABASE_DECOY_TAG',
        param_type=ParameterType.STRING,
        getter=lambda config: config.database.decoy_tag,
        setter=lambda config, value: setattr(config.database, 'decoy_tag', value),
        description="Tag for decoy sequences"
    )
    DATABASE_GENERATE_DECOYS = Parameter(
        name='DATABASE_GENERATE_DECOYS',
        param_type=ParameterType.BOOLEAN,
        getter=lambda config: config.database.generate_decoys,
        setter=lambda config, value: setattr(config.database, 'generate_decoys', value),
        options=[True, False],
        description="Generate decoy sequences"
    )
    DATABASE_MAX_VARIABLE_MODS = Parameter(
        name='DATABASE_MAX_VARIABLE_MODS',
        param_type=ParameterType.NUMERIC,
        getter=lambda config: config.database.max_variable_mods,
        setter=lambda config, value: setattr(config.database, 'max_variable_mods', int(value)),
        description="Maximum variable modifications per peptide"
    )
    OUTPUT_DIRECTORY = Parameter(
        name='OUTPUT_DIRECTORY',
        param_type=ParameterType.STRING,
        getter=lambda config: config.output_directory,
        setter=lambda config, value: setattr(config, 'output_directory', value),
        description="Directory for output files"
    )
    PRECURSOR_MIN_CHARGE = Parameter(
        name='PRECURSOR_MIN_CHARGE',
        param_type=ParameterType.NUMERIC,
        getter=lambda config: config.precursor_charge[0],
        setter=lambda config, value: setattr(config, 'precursor_charge', (int(value), config.precursor_charge[1])),
        description="Minimum precursor charge state"
    )
    PRECURSOR_MAX_CHARGE = Parameter(
        name='PRECURSOR_MAX_CHARGE',
        param_type=ParameterType.NUMERIC,
        getter=lambda config: config.precursor_charge[1],
        setter=lambda config, value: setattr(config, 'precursor_charge', (config.precursor_charge[0], int(value))),
        description="Maximum precursor charge state"
    )
    ISOTOPE_MIN_ERROR = Parameter(
        name='ISOTOPE_MIN_ERROR',
        param_type=ParameterType.NUMERIC,
        getter=lambda config: config.isotope_errors[0],
        setter=lambda config, value: setattr(config, 'isotope_errors', (int(value), config.isotope_errors[1])),
        description="Minimum isotope error"
    )
    ISOTOPE_MAX_ERROR = Parameter(
        name='ISOTOPE_MAX_ERROR',
        param_type=ParameterType.NUMERIC,
        getter=lambda config: config.isotope_errors[1],
        setter=lambda config, value: setattr(config, 'isotope_errors', (config.isotope_errors[0], int(value))),
        description="Maximum isotope error"
    )
    DEISOTOPE = Parameter(
        name='DEISOTOPE',
        param_type=ParameterType.BOOLEAN,
        getter=lambda config: config.deisotope,
        setter=lambda config, value: setattr(config, 'deisotope', value),
        options=[True, False],
        description="Perform deisotoping"
    )
    CHIMERA = Parameter(
        name='CHIMERA',
        param_type=ParameterType.BOOLEAN,
        getter=lambda config: config.chimera,
        setter=lambda config, value: setattr(config, 'chimera', value),
        options=[True, False],
        description="Enable chimera detection"
    )
    WIDE_WINDOW = Parameter(
        name='WIDE_WINDOW',
        param_type=ParameterType.BOOLEAN,
        getter=lambda config: config.wide_window,
        setter=lambda config, value: setattr(config, 'wide_window', value),
        options=[True, False],
        description="Use wide precursor window"
    )
    PREDICT_RT = Parameter(
        name='PREDICT_RT',
        param_type=ParameterType.BOOLEAN,
        getter=lambda config: config.predict_rt,
        setter=lambda config, value: setattr(config, 'predict_rt', value),
        options=[True, False],
        description="Predict retention time"
    )
    MIN_PEAKS = Parameter(
        name='MIN_PEAKS',
        param_type=ParameterType.NUMERIC,
        getter=lambda config: config.min_peaks,
        setter=lambda config, value: setattr(config, 'min_peaks', int(value)),
        description="Minimum number of peaks"
    )
    MAX_PEAKS = Parameter(
        name='MAX_PEAKS',
        param_type=ParameterType.NUMERIC,
        getter=lambda config: config.max_peaks,
        setter=lambda config, value: setattr(config, 'max_peaks', int(value)),
        description="Maximum number of peaks"
    )
    MIN_MATCHED_PEAKS = Parameter(
        name='MIN_MATCHED_PEAKS',
        param_type=ParameterType.NUMERIC,
        getter=lambda config: config.min_matched_peaks,
        setter=lambda config, value: setattr(config, 'min_matched_peaks', int(value)),
        description="Minimum number of matched peaks"
    )
    MAX_FRAGMENT_CHARGE = Parameter(
        name='MAX_FRAGMENT_CHARGE',
        param_type=ParameterType.NUMERIC,
        getter=lambda config: config.max_fragment_charge,
        setter=lambda config, value: setattr(config, 'max_fragment_charge', int(value) if value is not None else None),
        description="Maximum fragment charge state"
    )
    REPORT_PSMS = Parameter(
        name='REPORT_PSMS',
        param_type=ParameterType.NUMERIC,
        getter=lambda config: config.report_psms,
        setter=lambda config, value: setattr(config, 'report_psms', int(value)),
        description="Number of PSMs to report"
    )
    MZML_PATHS = Parameter(
        name='MZML_PATHS',
        param_type=ParameterType.STRING_LIST,
        getter=lambda config: config.mzml_paths,
        setter=lambda config, value: setattr(config, 'mzml_paths', value),
        description="List of paths to mzML files"
    )



@dataclass(frozen=True)
class ParameterGroup:
    """Defines a group of related parameters for display purposes."""
    name: str
    description: str
    parameters: Dict[ParameterEnum, Parameter]

class ParameterGroupEnum(Enum):
    """Enumeration of available parameter groups."""
    TOLERANCE = ParameterGroup(
        name='Tolerance Settings',
        description='Precursor and fragment mass tolerance configuration',
        parameters={
            ParameterEnum.PRECURSOR_TOL_MIN_VALUE: ParameterEnum.PRECURSOR_TOL_MIN_VALUE.value,
            ParameterEnum.PRECURSOR_TOL_MAX_VALUE: ParameterEnum.PRECURSOR_TOL_MAX_VALUE.value,
            ParameterEnum.PRECURSOR_TOL_UNIT: ParameterEnum.PRECURSOR_TOL_UNIT.value,
            ParameterEnum.FRAGMENT_TOL_MIN_VALUE: ParameterEnum.FRAGMENT_TOL_MIN_VALUE.value,
            ParameterEnum.FRAGMENT_TOL_MAX_VALUE: ParameterEnum.FRAGMENT_TOL_MAX_VALUE.value,
            ParameterEnum.FRAGMENT_TOL_UNIT: ParameterEnum.FRAGMENT_TOL_UNIT.value
        }
    )
    ENZYME = ParameterGroup(
        name='Enzyme Configuration',
        description='Enzyme digestion parameters',
        parameters={
            ParameterEnum.DATABASE_ENZYME_MISSED_CLEAVAGES: ParameterEnum.DATABASE_ENZYME_MISSED_CLEAVAGES.value,
            ParameterEnum.DATABASE_ENZYME_MIN_LEN: ParameterEnum.DATABASE_ENZYME_MIN_LEN.value,
            ParameterEnum.DATABASE_ENZYME_MAX_LEN: ParameterEnum.DATABASE_ENZYME_MAX_LEN.value,
            ParameterEnum.DATABASE_ENZYME_CLEAVE_AT: ParameterEnum.DATABASE_ENZYME_CLEAVE_AT.value,
            ParameterEnum.DATABASE_ENZYME_RESTRICT: ParameterEnum.DATABASE_ENZYME_RESTRICT.value,
            ParameterEnum.DATABASE_ENZYME_TERMINAL: ParameterEnum.DATABASE_ENZYME_TERMINAL.value,
            ParameterEnum.DATABASE_ENZYME_SEMI_ENZYMATIC: ParameterEnum.DATABASE_ENZYME_SEMI_ENZYMATIC.value
        }
    )
    DATABASE = ParameterGroup(
        name='Database Settings',
        description='Database search and peptide generation settings',
        parameters={
            ParameterEnum.DATABASE_BUCKET_SIZE: ParameterEnum.DATABASE_BUCKET_SIZE.value,
            ParameterEnum.DATABASE_PEPTIDE_MIN_MASS: ParameterEnum.DATABASE_PEPTIDE_MIN_MASS.value,
            ParameterEnum.DATABASE_PEPTIDE_MAX_MASS: ParameterEnum.DATABASE_PEPTIDE_MAX_MASS.value,
            ParameterEnum.DATABASE_MIN_ION_INDEX: ParameterEnum.DATABASE_MIN_ION_INDEX.value,
            ParameterEnum.DATABASE_DECOY_TAG: ParameterEnum.DATABASE_DECOY_TAG.value,
            ParameterEnum.DATABASE_GENERATE_DECOYS: ParameterEnum.DATABASE_GENERATE_DECOYS.value,
            ParameterEnum.DATABASE_MAX_VARIABLE_MODS: ParameterEnum.DATABASE_MAX_VARIABLE_MODS.value,
            ParameterEnum.DATABASE_ION_KINDS: ParameterEnum.DATABASE_ION_KINDS.value
        }
    )
    QUANTIFICATION = ParameterGroup(
        name='Quantification Settings',
        description='TMT and LFQ quantification configuration',
        parameters={
            ParameterEnum.QUANT_TMT: ParameterEnum.QUANT_TMT.value,
            ParameterEnum.QUANT_LFQ: ParameterEnum.QUANT_LFQ.value,
            ParameterEnum.QUANT_TMT_SETTINGS_LEVEL: ParameterEnum.QUANT_TMT_SETTINGS_LEVEL.value,
            ParameterEnum.QUANT_TMT_SETTINGS_SN: ParameterEnum.QUANT_TMT_SETTINGS_SN.value,
            ParameterEnum.QUANT_LFQ_SETTINGS_PEAK_SCORING: ParameterEnum.QUANT_LFQ_SETTINGS_PEAK_SCORING.value,
            ParameterEnum.QUANT_LFQ_SETTINGS_INTEGRATION: ParameterEnum.QUANT_LFQ_SETTINGS_INTEGRATION.value,
            ParameterEnum.QUANT_LFQ_SETTINGS_SPECTRAL_ANGLE: ParameterEnum.QUANT_LFQ_SETTINGS_SPECTRAL_ANGLE.value,
            ParameterEnum.QUANT_LFQ_SETTINGS_PPM_TOLERANCE: ParameterEnum.QUANT_LFQ_SETTINGS_PPM_TOLERANCE.value,
            ParameterEnum.QUANT_LFQ_SETTINGS_MOBILITY_PCT_TOLERANCE: ParameterEnum.QUANT_LFQ_SETTINGS_MOBILITY_PCT_TOLERANCE.value,
            ParameterEnum.QUANT_LFQ_SETTINGS_COMBINE_CHARGE_STATES: ParameterEnum.QUANT_LFQ_SETTINGS_COMBINE_CHARGE_STATES.value
        }
    )
    SEARCH = ParameterGroup(
        name='Search Settings',
        description='General search and spectrum processing parameters',
        parameters={
            ParameterEnum.PRECURSOR_MIN_CHARGE: ParameterEnum.PRECURSOR_MIN_CHARGE.value,
            ParameterEnum.PRECURSOR_MAX_CHARGE: ParameterEnum.PRECURSOR_MAX_CHARGE.value,
            ParameterEnum.ISOTOPE_MIN_ERROR: ParameterEnum.ISOTOPE_MIN_ERROR.value,
            ParameterEnum.ISOTOPE_MAX_ERROR: ParameterEnum.ISOTOPE_MAX_ERROR.value,
            ParameterEnum.DEISOTOPE: ParameterEnum.DEISOTOPE.value,
            ParameterEnum.CHIMERA: ParameterEnum.CHIMERA.value,
            ParameterEnum.WIDE_WINDOW: ParameterEnum.WIDE_WINDOW.value,
            ParameterEnum.PREDICT_RT: ParameterEnum.PREDICT_RT.value,
            ParameterEnum.MIN_PEAKS: ParameterEnum.MIN_PEAKS.value,
            ParameterEnum.MAX_PEAKS: ParameterEnum.MAX_PEAKS.value,
            ParameterEnum.MIN_MATCHED_PEAKS: ParameterEnum.MIN_MATCHED_PEAKS.value,
            ParameterEnum.MAX_FRAGMENT_CHARGE: ParameterEnum.MAX_FRAGMENT_CHARGE.value,
            ParameterEnum.REPORT_PSMS: ParameterEnum.REPORT_PSMS.value
        }
    )
    FASTA_FILE = ParameterGroup(
        name='FASTA File',
        description='Display FASTA File Name',
        parameters={
            ParameterEnum.DATABASE_FASTA: ParameterEnum.DATABASE_FASTA.value
        }
    )
    OUTPUT_DIR = ParameterGroup(
        name='Output Directory',
        description='Display output directory',
        parameters={
            ParameterEnum.OUTPUT_DIRECTORY: ParameterEnum.OUTPUT_DIRECTORY.value
        }
    )

