# Dataclass objects to specify parameters for the QEC experiment
# This includes the type of error correction code, distance,
# number of rounds, appropriate decoder to be used, noise model specification as Enums

from enum import Enum
from random import randint
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# Type aliases
CheckMatrix = list[list[int]]


class StrictBaseModel(BaseModel):
    """
    In pydantic v2, the base model allows extra fields by default.
    This custom base model forbids that
    """

    model_config = ConfigDict(extra="forbid")


class Code(str, Enum):
    """
    Enum representing different quantum error correction codes supported
    """

    ROTATEDSURFACECODE = "rotatedsurfacecode"
    REPETITIONCODE = "repetitioncode"
    STEANECODE = "steanecode"
    SHORCODE = "shorcode"
    HGPCODE = "hgpcode"
    COLORCODE = "colorcode"

    @classmethod
    def _missing_(cls, value):
        # Convert the input value to lowercase for case-insensitive matching
        value = str(value).lower()
        for member in cls:
            if member.value.lower() == value:
                return member
        # If no match found, raise a ValueError as default behavior
        raise ValueError(f"'{value}' is not a valid {cls.__name__}")


class Decoder(str, Enum):
    """
    Enum representing different decoders to be used for QEC experiment.
    """

    PYMATCHING = "pymatching"
    BELIEFPROPAGATION = "beliefpropagation"
    UNIONFIND = "unionfind"
    LUT = "lut"
    BPOSD = "bposd"
    CHROMOBIUS = "chromobius"

    @classmethod
    def _missing_(cls, value):
        # Convert the input value to lowercase for case-insensitive matching
        value = str(value).lower()
        for member in cls:
            if member.value.lower() == value:
                return member
        # If no match found, raise a ValueError as default behavior
        raise ValueError(f"'{value}' is not a valid {cls.__name__}")


class NoiseParameters(StrictBaseModel):
    """
    Enum representing different noise models that can be used in
    quantum error correction experiments.
    """

    depolarizing: float = Field(
        default=0, validate_default=True, description="Depolarizing error rate"
    )
    measurement: float = Field(
        default=0, validate_default=True, description="Measurement error rate"
    )
    reset: float = Field(
        default=0, validate_default=True, description="Reset error rate"
    )


class ChannelSpecifiedNoiseModel(StrictBaseModel):
    """
    A new interface for specifying noise models.
    Users either specify a list of individual noise parameters (depolarizing, 
    measurement and reset) for each experiment, or they specify a list of base
    probabilities or alphas.
    """

    depolarizing: list[float] = Field(
        description="Depolarizing error rates for each experiment",
        default_factory=list,
    )
    measurement: list[float] = Field(
        description="Measurement error rates for each experiment",
        default_factory=list,
    )
    reset: list[float] = Field(
        description="Reset error rates for each experiment",
        default_factory=list,
    )
    threshold_x_parameter: Literal["depolarizing", "measurement", "reset", "base_probability"] | None = Field(
        description="The noise parameter to be used for the x-axis in threshold computations",
        default=None,
    )
    base_probabilities: list[float] = Field(
        description="Base probability values for threshold computations. Used if threshold_x_parameter is 'base_probability'",
        default_factory=list,
    )
    alphas: list[float] = Field(
        description="Alpha values for threshold computations. Used if threshold_x_parameter is 'base_probability'",
        default_factory=list,
    )

    @model_validator(mode="after")
    @classmethod
    def validate_threshold_x_parameter(cls, values):
        """
        If noise parameters are specified, threshold_x_parameter must be one of depolarizing, measurement or reset.
        If only base_probabilities and alphas are specified, threshold_x_parameter can be None or base_probability.
        """
        if (
            values.depolarizing != []
            and values.measurement != []
            and values.reset != []
        ):
            if values.threshold_x_parameter not in [
                "depolarizing",
                "measurement",
                "reset",
            ]:
                raise ValueError(
                    "If noise parameters are specified, threshold_x_parameter must be one of depolarizing, measurement or reset." # TODO: Missing unittest
                )
        elif (
            values.base_probabilities != []
            and values.alphas != []
        ):
            if values.threshold_x_parameter not in [
                None,
                "base_probability",
            ]:
                raise ValueError(
                    "If only base_probabilities and alphas are specified, threshold_x_parameter can be None or base_probability." # TODO: Missing unittest
                )
        return values

    @model_validator(mode="after")
    @classmethod
    def validate_equal_length(cls, values):
        """
        Specifically for individual noise parameters, if any of depolarizing, measurement or reset
        are specified, they must all be of equal length.
        """
        if (
            values.depolarizing != []
            or values.measurement != []
            or values.reset != []
        ):
            lengths = [
                len(lst)
                for lst in [
                    values.depolarizing,
                    values.measurement,
                    values.reset,
                ]
                if lst is not None
            ]
            if len(set(lengths)) > 1:
                raise ValueError("depolarizing, measurement and reset must be of equal length.")
            if lengths[0] == 0:
                raise ValueError("depolarizing, measurement and reset cannot be empty lists.") # TODO: Missing unittest
        return values

    @model_validator(mode="after")
    @classmethod
    def validate_initialization_parameters(cls, values):
        """
        If any of base_probabilities or alphas are specified, individual noise parameters must not be specified.
        If any of individual noise parameters are specified, base_probabilities or alphas must not be specified.
        If all input parameters are empty lists, raise a ValueError.
        """
        if (
            (values.base_probabilities != [] or values.alphas != [])
            and (values.depolarizing != [] or values.measurement != [] or values.reset != [])
        ):
            raise ValueError("base_probabilities or alphas cannot be specified together with individual noise parameters (depolarizing, measurement, reset).") # TODO: Missing unittest
        if (
            values.base_probabilities == []
            and values.alphas == []
            and values.depolarizing == []
            and values.measurement == []
            and values.reset == []
        ):
            raise ValueError("At least one of base_probabilities and alphas, or individual noise parameters (depolarizing, measurement, reset) must be specified.")

        return values
    
    @model_validator(mode="after")
    @classmethod
    def validate_base_probabilities(cls, values):
        """
        Values of base_probabilities must be between 0 and 1 (inclusive).
        base_probabilities cannot be an empty list if alphas is specified.
        """
        if values.base_probabilities != []:
            if not all(isinstance(p, (float, int)) and 0 <= float(p) <= 1 for p in values.base_probabilities):
                raise ValueError("All base probability values must be between 0 and 1 (inclusive).") # TODO: Missing unittest
        if values.alphas != [] and values.base_probabilities == []:
            raise ValueError("base_probabilities cannot be an empty list if alphas is specified.")
        return values

    @field_validator("alphas", mode="before")
    def validate_alphas(cls, alphas):
        """
        Values of alphas must be greater than 0.
        Length of alphas list must be exactly 3 if specified.
        """
        if alphas is not None:
            if not all(isinstance(alpha, (float, int)) and float(alpha) >= 0 for alpha in alphas):
                raise ValueError("All alpha values must be greater than or equal to 0.")
            if len(alphas) != 3:
                raise ValueError("Length of alphas list must be exactly 3 if specified.")
        return alphas

    def model_post_init(self, __context) -> None:
        """
        If only base_probabilities and alphas are specified, set threshold_x_parameter to 'base_probability' if it is None.
        """
        if (
            self.base_probabilities != []
            and self.alphas != []
            and self.threshold_x_parameter is None
        ):
            self.threshold_x_parameter = "base_probability"

    def return_noise_parameters(self) -> list[NoiseParameters]:
        """
        Return a list of NoiseParameters based on the initialization parameters.
        """
        if (
            self.depolarizing != []
            and self.measurement != []
            and self.reset != []
        ):
            # Individual noise parameters are specified.
            max_length = max(
                len(self.depolarizing),
                len(self.measurement),
                len(self.reset),
            )
            noise_parameters_list = []
            for i in range(max_length):
                noise_parameters_list.append(
                    NoiseParameters(
                        depolarizing=self.depolarizing[i] if self.depolarizing and i < len(self.depolarizing) else 0.0,
                        measurement=self.measurement[i] if self.measurement and i < len(self.measurement) else 0.0,
                        reset=self.reset[i] if self.reset and i < len(self.reset) else 0.0,
                    )
                )
            return noise_parameters_list
        elif self.base_probabilities is not None and self.alphas is not None:
            # Base probabilities are specified.
            # For alphas = [a_1, a_2, a_3] and base_probabilities = [p_1, p_2, ..., p_n]
            # The noise parameters are:
            # p_depolarizing = p_i * a_1
            # p_measurement = p_i * a_2
            # p_reset = p_i * a_3
            # for each p_i in base_probabilities
            noise_parameters_list = []
            for p in self.base_probabilities:
                noise_parameters_list.append(
                    NoiseParameters(
                        depolarizing=p*self.alphas[0],
                        measurement=p*self.alphas[1],
                        reset=p*self.alphas[2],
                    )
                )
            return noise_parameters_list
        else:
            raise ValueError("Insufficient parameters to generate NoiseParameters. Either individual noise parameters (depolarizing, measurement, reset) or both base_probabilities and alphas must be specified.")


class ColorCodeTiling(StrictBaseModel):
    """
    Class representing the tiling of the color code.
    Currently we only support (4, 8, 8) and (6, 6, 6)
    NOTE: Change to 1 input list 
    """
    tiling: list[int] = Field(
        description="The number of sides of the polygons in vertex configuration notation used for tiling."
    )

    @model_validator(mode="after")
    @classmethod
    def validate_tiling(cls, values):
        if values.tiling == [4, 8, 8]:
            return values
        if values.tiling == [6, 6, 6]:
            return values
        raise ValueError("Invalid tiling configuration. Supported configurations are (4, 8, 8) and (6, 6, 6).")
    
    @field_validator("tiling", mode="before")
    @classmethod
    def validate_tiling_list(cls, v):
        """
        Must be a list of size 3.
        """
        if not isinstance(v, list) or len(v) != 3 or not all(isinstance(i, int) for i in v):
            raise ValueError("tiling must be a list of 3 integers.")
        return v



class QECExperiment(StrictBaseModel):
    """
    Parameters for a quantum error correction experiment.
    This includes the code type, distance, number of rounds,
    decoder to be used, and noise model.
    """

    qec_code: Code
    decoder: Decoder
    noise_parameters: NoiseParameters | list[NoiseParameters] = Field(
        default_factory=list,
        description="Parameters for the noise model used in the experiment",
    )
    max_shots: int = Field(
        default=1000000,
        description="Number of shots for the simulation of the quantum error correction experiment",
    )
    max_errors: int = Field(
        default=500,
        description="Maximum number of errors detected before the simulation is stopped",
    )
    gate_durations: dict[str, float] | None = Field(
        default=None,
        description="Duration of quantum gates used in the experiment",
        validate_default=True,
    )
    experiment_type: str = Field(
        description="Type of the experiment, e.g., memory",
    )
    pseudoseed: int = Field(
        default_factory=lambda _: randint(0, 2**32 - 1),
        description="Pseudorandom seed for the experiment. Randomized by default.",
    )

    @model_validator(mode="after")
    @classmethod
    def validate_chromobius_color_code(cls, values):
        """
        Chromobius decoder only supports Color Code.
        """
        if values.decoder == Decoder.CHROMOBIUS and values.qec_code != Code.COLORCODE:
            raise ValueError("Chromobius decoder only supports Color Code.")
        return values

    def model_post_init(self, __context) -> None:
        """
        Post-initialization that recasts noise_parameters to a list if it is a single instance.
        """
        self.noise_parameters = (
            [self.noise_parameters]
            if isinstance(self.noise_parameters, NoiseParameters)
            else self.noise_parameters
        )


class QECExperimentXZ(QECExperiment):
    """
    Parameters for a quantum error correction experiment with both X and Z memory types.
    Inherits from QECExperiment and can be extended with additional parameters if needed.
    """

    memory_type: Literal["Z", "X"] = Field(
        description="Type of memory used in the experiment, either 'Z' or 'X'",
    )

    @field_validator("memory_type", mode="before")
    @classmethod
    def validate_memory_type(cls, v: str) -> str:
        """
        Validate the memory_type field to ensure it is either 'Z' or 'X'.
        This is case-insensitive, so both 'Z' and 'z' are valid.
        """
        v = str(v).strip()
        if v.upper() not in {"Z", "X"}:
            raise ValueError("memory_type must be either 'Z' or 'X' (case-insensitive)")
        return v.upper()  # Normalize to uppercase if needed


class IndividualExperiment(QECExperimentXZ):
    """
    Parameters for a single instance of the Memory experiment with a single distance,
    number of rounds and a single set of noise parameters.
    Inherits from QECExperimentXZ and can be extended with additional parameters if needed.
    """

    distance: int = Field(
        description="The distance of the code all individual experiments will run for",
    )
    num_round: int = Field(
        description="The number of syndrome extraction rounds for the distance",
    )
    check_matrix: list[CheckMatrix] | None = Field(
        description="Check matrix pair for the individual experiment",
        default=None,
    )
    tiling: ColorCodeTiling | None = Field(
        description="Tiling information for the color code",
        default=None,
    )
    experiment_type: str = Field(default="individual", init=False, frozen=True)

    @model_validator(mode="after")
    @classmethod
    def validate_distance_and_tiling_for_color_code(cls, values):
        """
        For Color Codes, all distance values must be odd and tiling cannot be None.
        """
        if values.qec_code == Code.COLORCODE:
            if values.distance % 2 == 0:
                raise ValueError("Distance must be odd for Color Code.")
            if values.tiling is None:
                raise ValueError("Tiling information must be provided for Color Code.")
        return values
    
    @model_validator(mode="after")
    @classmethod
    def validate_check_matrix_for_hgp_code(cls, values):
        """
        For HGP Codes, check matrix must be provided.
        """
        if values.qec_code == Code.HGPCODE:
            if values.check_matrix is None:
                raise ValueError("Check matrix must be provided for HGP Code.")
        return values

    @model_validator(mode="after")
    @classmethod
    def validate_distance_for_steane_code(cls, values):
        """
        Steane Code has a fixed distance, set distance == 1 if using Steane Code.
        """
        if values.qec_code != Code.STEANECODE:
            return values
        if values.distance != 1:
            raise ValueError("Distance must be 1 for Steane code.")
        return values

    @field_validator("noise_parameters", mode="before")
    @classmethod
    def validate_noise_parameters(
        cls, v: NoiseParameters | list[NoiseParameters]
    ) -> NoiseParameters:
        """
        Validate the noise_parameters field to ensure that there is only 1 NoiseParameter.
        """
        if isinstance(v, NoiseParameters):
            return v
        if isinstance(v, list) and len(v) == 1 and isinstance(v[0], NoiseParameters):
            return v[0]
        raise ValueError(
            "noise_parameters must be a single NoiseParameters instance or a list with exactly one NoiseParameters instance"
        )

    def model_dump(self, *args, **kwargs):
        """
        Override model_dump to ensure distance and num_rounds get recasted to lists.
        """
        data = super().model_dump(*args, **kwargs)
        data["distance_range"] = [data["distance"]]
        data["num_rounds"] = [data["num_round"]]
        data["check_matrices"] = (
            [data["check_matrix"]] if data["check_matrix"] is not None else None
        )
        data["metadata"] = None
        data.pop("distance", None)
        data.pop("num_round", None)
        data.pop("check_matrix", None)
        return data


class MemoryExperiment(QECExperimentXZ):
    """
    Parameters for a quantum error correction memory experiment.
    Inherits from QECExperiment and can be extended with additional parameters if needed.
    """

    distance: int = Field(
        description="The distance of the code all memory experiments will run for",
    )
    num_rounds: list[int] = Field(
        description="The varying number of syndrome extraction rounds for the distance",
    )
    check_matrix: list[CheckMatrix] | None = Field(
        description="List of check matrix pairs for the HGP code. Each pair is used for 1 experiment. (Similar behaviour to 1 distance value.)",
        default=None,
    )
    tiling: ColorCodeTiling | None = Field(
        description="The tiling configuration for the color code.",
        default=None,
    )
    experiment_type: str = Field(default="memory", init=False, frozen=True)

    @model_validator(mode="after")
    @classmethod
    def validate_distance_and_tiling_for_color_code(cls, values):
        """
        For Color Codes, all distance values must be odd and tiling cannot be None.
        """
        if values.qec_code == Code.COLORCODE:
            if values.distance % 2 == 0:
                raise ValueError("Distance must be odd for Color Code.")
            if values.tiling is None:
                raise ValueError("Tiling information must be provided for Color Code.")
        return values
    
    @model_validator(mode="after")
    @classmethod
    def validate_check_matrix_for_hgp_code(cls, values):
        """
        For HGP Codes, check matrix must be provided.
        """
        if values.qec_code == Code.HGPCODE:
            if values.check_matrix is None:
                raise ValueError("Check matrix must be provided for HGP Code.")
            if len(values.check_matrix) != 2:
                raise ValueError("A pair of Check Matrices must be provided for HGP Code.")
        return values

    @model_validator(mode="after")
    @classmethod
    def validate_distance_for_steane_code(cls, values):
        """
        Steane Code has a fixed distance, set distance == 1 if using Steane Code.
        """
        if values.qec_code != Code.STEANECODE:
            return values
        if values.distance != 1:
            raise ValueError("Distance must be 1 for Steane code.")
        return values

    def model_dump(self, *args, **kwargs):
        """
        Override model_dump to ensure distance and num_rounds get recasted to lists.
        """
        data = super().model_dump(*args, **kwargs)
        data["distance_range"] = [data["distance"]] * len(data["num_rounds"])
        data["check_matrices"] = (
            [data["check_matrix"]] * len(data["num_rounds"]) if data["check_matrix"] is not None else None
        )
        data["metadata"] = None
        data.pop("distance", None)
        data.pop("check_matrix", None)
        return data
    

class RotatedSurfaceCodeMemoryExperiment(QECExperimentXZ):
    """
    Parameters for a Rotated Surface code memory experiment.
    Inherits from QECExperimentXZ and can be extended with additional parameters if needed.
    Specialized models help remove/auto-set certain parameters.
    """

    qec_code: Code = Field(default=Code.ROTATEDSURFACECODE, init=False, frozen=True)
    distance: int = Field(
        description="The distance of the code all memory experiments will run for",
    )
    num_rounds: list[int] = Field(
        description="The varying number of syndrome extraction rounds for the distance",
    )
    experiment_type: str = Field(default="memory", init=False, frozen=True)

    def model_dump(self, *args, **kwargs):
        """
        Override model_dump to ensure distance and num_rounds get recasted to lists.
        """
        data = super().model_dump(*args, **kwargs)
        data["distance_range"] = [data["distance"]] * len(data["num_rounds"])
        data["check_matrices"] = None
        data["metadata"] = None
        data["tiling"] = None
        data.pop("distance", None)
        return data
    

class RepetitionCodeMemoryExperiment(QECExperimentXZ):
    """
    Parameters for a Repetition code memory experiment.
    Inherits from QECExperimentXZ and can be extended with additional parameters if needed.
    Specialized models help remove/auto-set certain parameters.
    """

    qec_code: Code = Field(default=Code.REPETITIONCODE, init=False, frozen=True)
    distance: int = Field(
        description="The distance of the code all memory experiments will run for",
    )
    num_rounds: list[int] = Field(
        description="The varying number of syndrome extraction rounds for the distance",
    )
    experiment_type: str = Field(default="memory", init=False, frozen=True)

    def model_dump(self, *args, **kwargs):
        """
        Override model_dump to ensure distance and num_rounds get recasted to lists.
        """
        data = super().model_dump(*args, **kwargs)
        data["distance_range"] = [data["distance"]] * len(data["num_rounds"])
        data["check_matrices"] = None
        data["metadata"] = None
        data["tiling"] = None
        data.pop("distance", None)
        return data


class SteaneMemoryExperiment(QECExperimentXZ):
    """
    Parameters for a Steane code memory experiment.
    Inherits from QECExperimentXZ and can be extended with additional parameters if needed.
    Specialized models help remove/auto-set certain parameters.
    """

    qec_code: Code = Field(default=Code.STEANECODE, init=False, frozen=True)
    num_rounds: list[int] = Field(
        description="The varying number of syndrome extraction rounds for the distance",
    )
    experiment_type: str = Field(default="memory", init=False, frozen=True)

    def model_dump(self, *args, **kwargs):
        """
        Override model_dump to ensure distance and num_rounds get recasted to lists.
        """
        data = super().model_dump(*args, **kwargs)
        data["distance_range"] = [1] * len(
            data["num_rounds"]
        )  # Distance is ignored if using Steane Code, Code has fixed size.
        data["check_matrices"] = None
        data["metadata"] = None
        data["tiling"] = None
        return data


class HGPMemoryExperiment(QECExperimentXZ):
    """
    Parameters for a HGP code memory experiment.
    Inherits from QECExperimentXZ and can be extended with additional parameters if needed.
    Specialized models help remove/auto-set certain parameters.
    """

    qec_code: Code = Field(default=Code.HGPCODE, init=False, frozen=True)
    distance: int = Field(
        description="The distance of the code all memory experiments will run for. In the case of the HGPCode, this value can also be a proxy for the distance."
    )
    num_rounds: list[int] = Field(
        description="The varying number of syndrome extraction rounds for the distance",
    )
    check_matrix: list[CheckMatrix] = Field(
        description="List of check matrix pairs for the HGP code. Each pair is used for 1 experiment. (Similar behaviour to 1 distance value.)",
    )
    experiment_type: str = Field(default="memory", init=False, frozen=True)

    def model_dump(self, *args, **kwargs):
        """
        Override model_dump to ensure distance and num_rounds get recasted to lists.
        """
        data = super().model_dump(*args, **kwargs)
        data["distance_range"] = [data["distance"]] * len(data["num_rounds"])
        data["check_matrices"] = [data["check_matrix"]] * len(data["num_rounds"])
        data["metadata"] = None
        data["tiling"] = None
        data.pop("distance", None)
        data.pop("check_matrix", None)
        return data
    

class ColorCodeMemoryExperiment(QECExperimentXZ):
    """
    Parameters for a Color code memory experiment.
    Inherits from QECExperimentXZ and can be extended with additional parameters if needed.
    Specialized models help remove/auto-set certain parameters.
    """

    qec_code: Code = Field(default=Code.COLORCODE, init=False, frozen=True)
    distance: int = Field(
        description="The distance of the code all memory experiments will run for. In the case of the HGPCode, this value can also be a proxy for the distance."
    )
    num_rounds: list[int] = Field(
        description="The varying number of syndrome extraction rounds for the distance",
    )
    tiling: ColorCodeTiling = Field(
        description="The tiling configuration for the color code.",
    )
    experiment_type: str = Field(default="memory", init=False, frozen=True)

    @field_validator("distance", mode="after")
    @classmethod
    def validate_distance(cls, value: int) -> int:
        """
        distance value must be odd.
        """
        if value % 2 == 0:
            raise ValueError("Distance must be odd for Color Code.")
        return value

    def model_dump(self, *args, **kwargs):
        """
        Override model_dump to ensure distance and num_rounds get recasted to lists.
        """
        data = super().model_dump(*args, **kwargs)
        data["distance_range"] = [data["distance"]] * len(data["num_rounds"])
        data["check_matrices"] = None
        data["metadata"] = None
        data.pop("distance", None)
        return data


class ThresholdExperiment(QECExperimentXZ):
    """
    Parameters for a quantum error correction threshold experiment.
    Inherits from QECExperiment and can be extended with additional parameters if needed.
    """

    # All pairs of distance_range and num_rounds will be run for each noise rate.
    distance_range: list[int] = Field(
        description="The various distances the threshold experiment will run for",
    )
    num_rounds: list[int] = Field(
        description="The number of syndrome extraction rounds for each distance in distance_range OR each check matrix in check_matrices.",
    )
    noise_parameters: NoiseParameters | list[NoiseParameters] | ChannelSpecifiedNoiseModel = Field(
        description="The noise parameters to use for the threshold experiment.",
    )
    threshold_x_parameter: Literal["depolarizing", "measurement", "reset", "base_probability"] | None = Field(
        description="The threshold x parameter to use for the threshold experiment.",
        default=None,
    )
    # Base probabilities or alphas can be specified instead of individual noise parameters.
    base_probabilities: list[float] = Field(
        description="Base probability values for threshold computations. Used if threshold_x_parameter is 'base_probability'",
        default_factory=list,
    )
    # Check Matrices can be specified instead if qec_code == Code.HGPCODE
    check_matrices: list[list[CheckMatrix]] | None = Field(
        description="List of check matrix pairs for the HGP code. Each pair is used for 1 experiment. (Similar behaviour to 1 distance value.)",
        default=None,
    )
    # Used only for Threshold.
    weighted: bool = Field(
        description="Boolean setting whether weighted statistics are considered. Defaults to False",
        default=False,
    )
    # Used for Threshold and Pseudo-Threshold.
    interp_method: Literal["linear", "cubic"] = Field(
        description="Method to be used for interpolation between data points. Currently restricted to 'linear' and 'cubic'. Defaults to 'linear'.",
        default="linear",
    )
    # Used for Threshold and Pseudo-Threshold.
    num_subsamples: int | None = Field(
        description="Number of subsamples to consider from the original Logical vs Physical error rate samples. This should be a positive integer smaller or equal to the number of samples. If set to None, no subsamples will be considered. Defaults to None.",
        default=None,
    )
    # Used for Threshold and Pseudo-Threshold.
    forward_scan: float = Field(
        description="The percentage, given as a float between 0 and 1, of data to be discarded when starting the search for a crossing. The discarded data will correspond to lower values of `p`. For example, if set to 0.25, the first 25% (smaller) values of `p` will not be considered when searching for a crossing point. Defaults to 0.",
        default=0.0,
    )
    pseudo_threshold: bool = Field(
        description="Boolean setting whether to compute the pseudo-threshold. Defaults to False.",
        default=False,
    )
    # Required Parameters if bootstrapping threshold computations.
    bootstrap: bool = Field(
        description="Boolean setting whether to use bootstrap sampling. Defaults to False.",
        default=False,
    )
    n_bootstrap_samples: int = Field(
        description="Number of bootstrap samples to use if bootstrap is True. Defaults to 1000.",
        default=1000,
    )
    # For Color Code
    tiling: ColorCodeTiling | None = Field(
        description="Tiling pattern for the Color Code of all experiment runs.",
        default=None,
    )
    experiment_type: str = Field(default="threshold", init=False, frozen=True)

    @model_validator(mode="after")
    def set_values_if_channelspecifiednoisemodel_is_used(self):
        """
        If noise_parameters is of type ChannelSpecifiedNoiseModel, set threshold_x_parameter and base_probabilities accordingly.
        """
        if isinstance(self.noise_parameters, ChannelSpecifiedNoiseModel):
            self.threshold_x_parameter = self.noise_parameters.threshold_x_parameter
            if self.threshold_x_parameter == "base_probability":
                self.base_probabilities = self.noise_parameters.base_probabilities
            self.noise_parameters = self.noise_parameters.return_noise_parameters() # Convert to a list of NoiseParameters
        else:
            if self.threshold_x_parameter is None:
                raise ValueError("threshold_x_parameter must be specified if noise_parameters is not of type ChannelSpecifiedNoiseModel.")
        return self
    
    @model_validator(mode="after")
    def validate_distinct_noise_params(self):
        """
        Ensure that all noise parameters are distinct.
        """
        current_threshold_param = self.threshold_x_parameter
        if current_threshold_param == "base_probability":
            if len(self.base_probabilities) != len(set(self.base_probabilities)):
                raise ValueError("Values for base_probabilities must be distinct.")
        elif current_threshold_param in ["depolarizing", "measurement", "reset"]:
            get_all_values = [getattr(param, current_threshold_param) for param in self.noise_parameters]
            if len(get_all_values) != len(set(get_all_values)):
                raise ValueError("Values for {} must be distinct across noise_parameters.".format(current_threshold_param))
        return self

    @model_validator(mode="after")
    @classmethod
    def validate_distance_and_tiling_for_color_code(cls, values):
        """
        For Color Codes, all distance values must be odd and tiling cannot be None.
        """
        if values.qec_code == Code.COLORCODE:
            for each_distance in values.distance_range:
                if each_distance % 2 == 0:
                    raise ValueError("Distance must be odd for Color Code.")
            if values.tiling is None:
                raise ValueError("Tiling information must be provided for Color Code.")
        return values

    @model_validator(mode="after")
    @classmethod
    def validate_num_rounds_check_matrices_length(cls, values):
        """
        Validate the num_rounds and check_matrices fields to ensure they have the same length.
        If qec_code == Code.HGPCODE, the length of num_rounds must be equal to the length of check_matrices.
        """
        if values.qec_code == Code.HGPCODE and len(values.check_matrices) != len(
            values.num_rounds
        ):
            raise ValueError("check_matrices must have the same length as num_rounds.")
        return values

    @model_validator(mode="after")
    @classmethod
    def validate_distance_for_steane_code(cls, values):
        """
        Steane Code has a fixed distance, set distance_range == [1, ..., 1] if using Steane Code.
        The length of distance_range is equal to num_rounds.
        """
        if values.qec_code not in [Code.STEANECODE]:
            return values
        correct_distance_range_input = [1] * len(values.num_rounds)
        if values.distance_range != correct_distance_range_input:
            raise ValueError(
                "Distance must be 1 for Steane code. The appropriate input for distance_range is {}.".format(
                    correct_distance_range_input
                )
            )
        return values

    @model_validator(mode="after")
    @classmethod
    def validate_distance_num_rounds_for_rsc_code(cls, values):
        """
        If qec_code is rotated surface code, distance and num_rounds must be equal.
        """
        if (
            values.qec_code == Code.ROTATEDSURFACECODE
            and values.distance_range != values.num_rounds
        ):
            raise ValueError(
                "For rotated surface code, distance and num_rounds must be equal."
            )
        return values

    @model_validator(mode="after")
    @classmethod
    def validate_num_rounds_distance_range_length(cls, values):
        """
        Validate the num_rounds and distance_range fields to ensure they have the same length.
        """
        if len(values.num_rounds) != len(values.distance_range):
            raise ValueError("num_rounds must have the same length as distance_range")
        return values

    @model_validator(mode="after")
    @classmethod
    def validate_pseudo_threshold_if_only_one_distance_provided(cls, values):
        """
        Validate that pseudo_threshold is True, if only 1 distance is provided in distance_range.
        """
        if len(values.distance_range) == 1 and not values.pseudo_threshold:
            raise ValueError(
                "pseudo_threshold must be True if only 1 distance is provided"
            )
        return values

    @model_validator(mode="after")
    @classmethod
    def validate_noise_parameters_length(cls, values):
        """
        Validate the number of noise_parameters is equal to the number of base_probabilities.
        """
        if values.threshold_x_parameter == "base_probability" and len(values.noise_parameters) != len(values.base_probabilities):
            raise ValueError(
                "The number of noise_parameters must be equal to the number of base_probabilities."
            )
        return values

    @model_validator(mode="after")
    @classmethod
    def validate_base_probabilities(cls, values):
        """
        Validate that there are at least 2 base_probabilities.
        Validate that base_probabilities are provided if threshold_x_parameter is 'base_probability'.
        """
        if values.threshold_x_parameter == "base_probability":
            if values.base_probabilities == []:
                raise ValueError(
                    "base_probabilities must be provided if threshold_x_parameter is 'base_probability'."
                )
            if len(values.base_probabilities) < 2:
                raise ValueError("There must be at least 2 base_probabilities.")
        # If base_probabilities is provided, it must have the same length as noise_parameters.
        if values.base_probabilities != [] and len(values.noise_parameters) != len(values.base_probabilities):
            raise ValueError("The number of base_probabilities must be equal to the number of noise_parameters.")
        return values
    
    def model_dump(self, *args, **kwargs):
        """
        Override model_dump to repackage inputs that are threshold specific to metadata.
        """
        data = super().model_dump(*args, **kwargs)
        metadata = {
            "metadata": {
                "base_probabilities": data["base_probabilities"],
                "threshold_x_parameter": data["threshold_x_parameter"],
                "weighted": data["weighted"],
                "interp_method": data["interp_method"],
                "num_subsamples": data["num_subsamples"],
                "forward_scan": data["forward_scan"],
                "pseudo_threshold": data["pseudo_threshold"],
                "bootstrap": data["bootstrap"],
                "n_bootstrap_samples": data["n_bootstrap_samples"],
            }
        }
        data.update(metadata)
        # Remove original fields
        data.pop("base_probabilities", None)
        data.pop("threshold_x_parameter", None)
        data.pop("weighted", None)
        data.pop("interp_method", None)
        data.pop("num_subsamples", None)
        data.pop("forward_scan", None)
        data.pop("pseudo_threshold", None)
        data.pop("bootstrap", None)
        data.pop("n_bootstrap_samples", None)
        return data
    

class RotatedSurfaceCodeThresholdExperiment(ThresholdExperiment):
    """
    Threshold experiment for the Rotated Surface code.
    Specialized models help remove/auto-set certain parameters.
    """

    qec_code: Code = Field(default=Code.ROTATEDSURFACECODE, init=False, frozen=True)
    num_rounds: list[int]  = Field(
        default=None, init=False
    )  # Remove from initialization
    check_matrices: list[list[CheckMatrix]] | None = Field(
        default=None, init=False
    )  # Remove from initialization
    tiling: ColorCodeTiling | None = Field(
        default=None, init=False
    )  # Remove from initialization

    def model_post_init(self, __context) -> None:
        """
        Assign distance_range automatically here.
        """
        super().model_post_init(__context)
        self.num_rounds = self.distance_range  # distance_range must be equal to num_rounds for RSC.


class RepetitionCodeThresholdExperiment(ThresholdExperiment):
    """
    Threshold experiment for the Repetition code.
    Specialized models help remove/auto-set certain parameters.
    """

    qec_code: Code = Field(default=Code.REPETITIONCODE, init=False, frozen=True)
    check_matrices: list[list[CheckMatrix]] | None = Field(
        default=None, init=False
    )  # Remove from initialization
    tiling: ColorCodeTiling | None = Field(
        default=None, init=False
    )  # Remove from initialization


class SteaneThresholdExperiment(ThresholdExperiment):
    """
    Threshold experiment for the Steane code.
    Specialized models help remove/auto-set certain parameters.
    """

    qec_code: Code = Field(default=Code.STEANECODE, init=False, frozen=True)
    distance_range: list[int] = Field(
        default=None, init=False
    )  # Remove from initialization
    check_matrices: list[list[CheckMatrix]] | None = Field(
        default=None, init=False
    )  # Remove from initialization
    tiling: ColorCodeTiling | None = Field(
        default=None, init=False
    )  # Remove from initialization

    def model_post_init(self, __context) -> None:
        """
        Assign distance_range automatically here.
        """
        super().model_post_init(__context)
        self.distance_range = [1] * len(
            self.num_rounds
        )  # Distance is ignored if using Steane Code, Code has fixed size.

class HGPThresholdExperiment(ThresholdExperiment):
    """
    Threshold experiment for the HGP code.
    Specialized models help remove/auto-set certain parameters.
    """

    qec_code: Code = Field(default=Code.HGPCODE, init=False, frozen=True)
    tiling: ColorCodeTiling | None = Field(
        default=None, init=False
    )  # Remove from initialization


class ColorCodeThresholdExperiment(ThresholdExperiment):
    """
    Threshold experiment for the Color Code.
    Specialized models help remove/auto-set certain parameters.
    """

    qec_code: Code = Field(default=Code.COLORCODE, init=False, frozen=True)
    check_matrices: list[list[CheckMatrix]] | None = Field(
        default=None, init=False
    )  # Remove from initialization


class QECResult(StrictBaseModel):
    """
    Result of a quantum error correction experiment.
    """

    timestamp: str = Field(
        description="Timestamp when the experiment was executed",
    )
    noise_parameters: NoiseParameters | list[NoiseParameters] = Field(
        description="Parameters for the noise model used in the experiment",
    )
    logical_error_rate: list[list[float]] = Field(
        description="Logical error rate of the quantum error correction experiment",
    )
    raw_results: dict = Field(
        description="Raw results of the quantum error correction experiment",
    )
    code_threshold: dict[str, float | list | None] | None = Field(
        default=None,
        description="Computed threshold for the quantum error correction code used in the experiment",
    )
    code_pseudothreshold: dict[str, float | dict | None] | None = Field(
        default=None,
        description="Computed pseudothreshold for the quantum error correction code used in the experiment. The key is the code distance and the values is the pseudo-threshold (or information about the pseudo-threshold if bootstrapped is True.)",
    )

    @classmethod
    def from_dict(cls, data: dict):
        """
        Create an instance of QECResult from a dictionary.
        This is useful for deserializing results from JSON or other formats.
        """
        # Select result
        data = data["result"]
        # Format the noise_parameters field based on its length
        if len(data["noise_parameters"]) > 1:
            output_noise_parameters = [
                NoiseParameters(**np) for np in data["noise_parameters"]
            ]
        else:
            output_noise_parameters = NoiseParameters(**data["noise_parameters"][0])

        return cls(
            timestamp=data["timestamp"],
            noise_parameters=output_noise_parameters,
            logical_error_rate=data["logical_error_rate"],
            code_threshold=data["threshold"],
            code_pseudothreshold=data.get("pseudo_threshold", None),
            raw_results=data,
        )

    @property
    def results_overview(self) -> dict:
        """
        Returns a summary of the results sorted by noise parameters:
        - Each noise parameter will have a list of dictionaries for the various
          combinations of distance, num_rounds runs and their respective
          logical_error_rate.
        - This is useful for quickly accessing the results of the experiment.

        Example output:
        {
            "timestamp": "2023-10-01T12:00:00Z",
            "results": [
                {
                    "noise_parameters": NoiseParameters(depolarizing=0.01, measurement=0.01, reset=0.01),
                    "runs": [
                        {
                            "distance": 3,
                            "num_rounds": 5,
                            "logical_error_rate": 0.001
                        },
                        {
                            "distance": 5,
                            "num_rounds": 10,
                            "logical_error_rate": 0.002
                        }
                    ]
                },
                ...
            ],
            "code_threshold": 0.1
        }
        """
        temp_noise_parameters = (
            [self.noise_parameters]
            if isinstance(self.noise_parameters, NoiseParameters)
            else self.noise_parameters
        )
        formatted_results = []

        for i, noise_parameters in enumerate(temp_noise_parameters):
            formatted_results.append({"noise_parameters": noise_parameters, "runs": []})
            for j, (distance, num_rounds) in enumerate(
                zip(self.raw_results["distance_range"], self.raw_results["num_rounds"])
            ):
                formatted_results[i]["runs"].append(
                    {
                        "distance": distance,
                        "num_rounds": num_rounds,
                        "logical_error_rate": self.logical_error_rate[i][j],
                    }
                )

        return {
            "timestamp": self.timestamp,
            "experiment_type": self.raw_results["experiment_type"],
            "results": formatted_results,
            "code_threshold": self.code_threshold,
            "code_pseudothreshold": self.code_pseudothreshold,
            "error_message": self.raw_results.get("error_message", None),
        }
