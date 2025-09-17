import warnings

import pandas as pd

from petsard.constrainer.constrainer_base import BaseConstrainer
from petsard.constrainer.field_combination_constrainer import (
    FieldCombinationConstrainer,
)
from petsard.constrainer.field_constrainer import FieldConstrainer
from petsard.constrainer.field_proportions_constrainer import (
    FieldProportionsConstrainer,
)
from petsard.constrainer.nan_group_constrainer import NaNGroupConstrainer


class Constrainer:
    """Factory class for creating and applying constraints"""

    _constraints = {
        "nan_groups": NaNGroupConstrainer,
        "field_constraints": FieldConstrainer,
        "field_combinations": FieldCombinationConstrainer,
        "field_proportions": FieldProportionsConstrainer,
    }

    def __init__(self, config: dict):
        """
        Initialize with full constraint configuration

        Args:
            config: Dictionary containing all constraint configurations
                {
                    'nan_groups': {...},
                    'field_constraints': [...],
                    'field_combinations': [...]
                }

        Attr.:
            resample_trails (int):
                Number of trials to reach the target number of rows,
                set after calling resample_until_satisfy
        """
        if not isinstance(config, dict):
            raise ValueError("Config must be a dictionary")
        self.config = config
        self._constrainers = {}
        self._setup_constrainers()

        self.resample_trails = None

    def _setup_constrainers(self):
        """Initialize all constraint instances"""
        for constraint_type, config in self.config.items():
            if constraint_type not in self._constraints:
                warnings.warn(
                    f"Warning: Unknown constraint type '{constraint_type}'",
                    stacklevel=2,
                )
                continue
            else:
                self._constrainers[constraint_type] = self._constraints[
                    constraint_type
                ](config)

    def apply(self, df: pd.DataFrame, target_rows: int = None) -> pd.DataFrame:
        """
        Apply all constraints in sequence

        Args:
            df: Input DataFrame
            target_rows: Target number of rows (used internally by resample_until_satisfy)

        Returns:
            DataFrame after applying all constraints
        """
        result = df.copy()
        for _constraint_type, constrainer in self._constrainers.items():
            # Set target rows for field proportions constrainer if needed
            if _constraint_type == "field_proportions" and target_rows is not None:
                constrainer._set_target_rows(target_rows)
            result = constrainer.apply(result)
        return result

    @classmethod
    def register(cls, name: str, constraint_class: type):
        """
        Register a new constraint type

        Args:
            name: Constraint type name
            constraint_class: Class implementing the constraint
        """
        if not issubclass(constraint_class, BaseConstrainer):
            raise ValueError("Must inherit from BaseConstrainer")
        cls._constraints[name] = constraint_class

    def resample_until_satisfy(
        self,
        data: pd.DataFrame,
        target_rows: int,
        synthesizer,
        postprocessor=None,
        max_trials: int = 300,
        sampling_ratio: float = 10.0,
        verbose_step: int = 10,
    ) -> pd.DataFrame:
        """
        Resample data until meeting the constraints with target number of rows.

        Args:
            data: Input DataFrame to be constrained
            target_rows: Number of rows to achieve
            synthesizer: Synthesizer instance for generating synthetic data
            postprocessor: Optional postprocessor for data transformation
            max_trials: Maximum number of trials before giving up
            sampling_ratio: Multiple of target_rows to generate in each trial.
                    Default is 10.0, meaning it will generate 10x the target rows
                    to compensate for data loss during constraint filtering.
            verbose_step: Print progress every verbose_step trials. Default is 10.

        Attr:
            resample_trails (int): Number of trials to reach the target number of rows

        Returns:
            DataFrame that satisfies all constraints with target number of rows

        Raises:
            ValueError: If data is empty or synthesizer is None
        """
        # Input validation
        if len(data) == 0:
            raise ValueError("Empty DataFrame is not allowed")
        if synthesizer is None:
            raise ValueError("Synthesizer cannot be None")

        self.resample_trails = 0
        result_df = None
        remain_rows = target_rows - data.shape[0]

        if remain_rows <= 0:
            # Apply constraints to the input data first
            constrained_data = self.apply(data, target_rows)

            if constrained_data.shape[0] >= target_rows:
                # If we have enough rows after applying constraints, sample the target number
                result = constrained_data.sample(
                    n=target_rows, random_state=42
                ).reset_index(drop=True)
                return result
            elif constrained_data.shape[0] > 0:
                # If we have some rows but not enough, continue with resampling
                result_df = constrained_data
                remain_rows = target_rows - constrained_data.shape[0]
            else:
                # If no rows remain after constraints, start fresh with resampling
                result_df = None
                remain_rows = target_rows

        while remain_rows > 0:
            self.resample_trails += 1
            if self.resample_trails >= max_trials:
                warnings.warn(
                    f"Maximum trials ({max_trials}) reached but only got {result_df.shape[0] if result_df is not None else 0} rows",
                    stacklevel=2,
                )
                break

            # Generate new samples
            synthesizer.config.update(
                {
                    "sample_from": "Constrainter",
                    "sample_num_rows": int(target_rows * sampling_ratio),
                }
            )

            new_samples = synthesizer.sample()

            # Apply postprocessor if provided
            if postprocessor is not None:
                new_samples = postprocessor.inverse_transform(new_samples)

            # Apply constraints
            filtered_samples = self.apply(new_samples, target_rows)

            # Combine with existing results
            if result_df is None:
                result_df = filtered_samples
            else:
                with warnings.catch_warnings():
                    warnings.filterwarnings(
                        "ignore",
                        category=FutureWarning,
                        message=".*behavior of DataFrame concatenation with empty or all-NA entries.*",
                    )

                    result_df = (
                        pd.concat(
                            [result_df, filtered_samples],
                            axis=0,
                            ignore_index=True,
                        )
                        .drop_duplicates()
                        .reset_index(drop=True)
                    )

            # Check if we have enough rows
            if result_df.shape[0] >= target_rows:
                # Randomly select target number of rows
                result_df = result_df.sample(
                    n=target_rows, random_state=42
                ).reset_index(drop=True)
                remain_rows = 0
            else:
                remain_rows = target_rows - result_df.shape[0]

            if verbose_step > 0 and self.resample_trails % verbose_step == 0:
                print(
                    f"Trial {self.resample_trails}: Got {result_df.shape[0] if result_df is not None else 0} rows, need {remain_rows} more"
                )

        return result_df
