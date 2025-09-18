import copy
import json
import os
import warnings
from collections.abc import Iterable
from typing import Union

import pandas as pd
import torch

from leaspy.exceptions import (
    LeaspyIndividualParamsInputError,
    LeaspyInputError,
    LeaspyTypeError,
)
from leaspy.utils.typing import DictParamsTorch, IDType, ParamType

from ..data import Data, Dataset

__all__ = ["Result"]


class Result:
    """
    Result object class.
    Used as logs by personalize algorithms & simulation algorithm.

    Parameters
    ----------
    data : :class:`.Data`
        Object containing the information of the individuals, 
        in particular the time-points :math:`(t_{i,j})` and the observations :math:`(y_{i,j})`.
    individual_parameters : :obj:`dict` [:obj:`str`, :class:`torch.Tensor`]
        Contains log-acceleration 'xi', time-shifts 'tau' & 'sources'
    noise_std : :obj:`float` or :class:`torch.FloatTensor`, optional (default None)
        Desired noise standard deviation level

    Attributes
    ----------
    data : :class:`.Data`
        Object containing the information of the individuals, 
        in particular the time-points :math:`(t_{i,j})` and the observations :math:`(y_{i,j})`.
    individual_parameters : :obj:`dict` [:obj:`str`, :class:`torch.Tensor`]
        Contains log-acceleration 'xi', time-shifts 'tau' & 'sources' (dictionary of `torch.Tensor`).
    ID_to_idx : :obj:`dict`
        The keys are the individual ID & the items are their respective ordered position in the data file given
        by the user. This order remains the same during the computation.
        Example - in Result.individual_parameters['xi'], the first element corresponds to the
        first patient in ID_to_idx.
    noise_std : :obj:`float` or :class:`torch.FloatTensor`
        Desired noise standard deviation level.
    """

    # TODO : Check consistency and ordering of subjects ID between Data and individual parameters io.
    def __init__(
        self, data: Data, individual_parameters: DictParamsTorch, noise_std=None
    ):
        self.data = data
        self.individual_parameters = individual_parameters
        self.ID_to_idx: dict[IDType, int] = {
            key: i for i, key in enumerate(data.individuals)
        }
        self.noise_std = noise_std

    # TODO : this method is used only once in plotting => delete it ?
    def get_torch_individual_parameters(
        self, ID: Union[IDType, list[IDType]] = None
    ) -> DictParamsTorch:
        """
        Getter function for the individual parameters.

        Parameters
        ----------
        ID : :obj:`str` or :obj:`list`[:obj:`str`], optional (default None)
            Contains the identifiers of the wanted subject.

        Returns
        -------
        :obj:`dict` [:obj:`str`, :class:`torch.Tensor`]
            Contains the individual parameters.
        """
        if ID is not None:
            if not isinstance(ID, list):
                if isinstance(ID, str) or not isinstance(ID, Iterable):
                    # If ID is not a Iterable (case where ID is a int) => convert into list
                    # If ID is a str => convert into list
                    ID = [ID]
                else:
                    raise LeaspyIndividualParamsInputError(
                        "Input argument 'ID' must be a single identifier or a list or identifiers!"
                    )

            list_idt = [self.ID_to_idx[id_patient] for id_patient in ID]
            ind_parameters = {
                key: value[list_idt]
                for key, value in self.individual_parameters.items()
            }
        else:
            ind_parameters = self.individual_parameters.copy()
        return ind_parameters

    # TODO: unit test & functional test
    def get_dataframe_individual_parameters(
        self, cofactors: Union[str, list[str]] = None
    ) -> pd.DataFrame:
        """
        Return the dataframe of the individual parameters.

        Each row corresponds to a subject. The columns correspond
        (in this order) to the subjects' ID, the individual parameters (one column per individual parameter) & the
        cofactors (one column per cofactor).

        Parameters
        ----------
        cofactors : :obj:`str` or :obj:`list`[:obj:`str`], optional (default None)
            Contains the cofactor(s) to join to the logs dataframe.

        Returns
        -------
        :class:`pandas.DataFrame`
            Contains for each patient his ID & his individual parameters (optional and his cofactors states)

        Notes
        -----
        The cofactors must be present in the leaspy data object stored into the .data attribute of the result instance.
        See the example.

        Examples
        --------
        Load a longitudinal multivariate dataset & the subjects' cofactors. Compute the individual parameters for this
        dataset & get the corresponding dataframe with the genetic APOE cofactor

        >>> import pandas as pd
        >>> from leaspy.api import Leaspy
        >>> from leaspy.algo import AlgorithmSettings
        >>> from leaspy.io.data import Data
        >>> from leaspy.io.logs.visualization import Plotter
        >>> leaspy_logistic = Leaspy('logistic')
        >>> data = Data.from_csv_file('data/my_leaspy_data.csv')  # replace with your own path!
        >>> genes_cofactors = pd.read_csv('data/genes_cofactors.csv')  # replace with your own path!
        >>> print(genes_cofactors.head())
                   ID      APOE4
        0  sub-HS0102          1
        1  sub-HS0112          0
        2  sub-HS0113          0
        3  sub-HS0114          1
        4  sub-HS0115          0

        >>> data.load_cofactors(genes_cofactors, ['GENES'])
        >>> model_settings = AlgorithmSettings('mcmc_saem', seed=0)
        >>> personalize_settings = AlgorithmSettings('mode_real', seed=0)
        >>> leaspy_logistic.fit(data, model_settings)
        >>> individual_results = leaspy_logistic.personalize(data, model_settings)
        >>> individual_results_df = individual_results.get_dataframe_individual_parameters('GENES')
        >>> print(individual_results_df.head())
                           tau        xi  sources_0  sources_1  APOE4
        ID
        sub-HS0102   70.329201  0.120465   5.969921  -0.245034      1
        sub-HS0112   95.156624 -0.692099   1.520273   3.477707      0
        sub-HS0113   74.900673 -1.769864  -1.222979   1.665889      0
        sub-HS0114   81.792763 -1.003620   1.021321   2.371716      1
        sub-HS0115   89.724648 -0.820971  -0.480975   0.741601      0
        """
        # Initialize patient dict with ID
        patient_dict = {"ID": list(self.ID_to_idx.keys())}

        # For each individual variable
        for variable_ind in list(self.individual_parameters.keys()):
            # Case tau / xi --> unidimensional
            if self.individual_parameters[variable_ind].shape[1] == 1:
                patient_dict[variable_ind] = (
                    self.individual_parameters[variable_ind].numpy().reshape(-1)
                )
            # Case sources --> multidimensional
            elif self.individual_parameters[variable_ind].shape[1] > 1:
                for dim in range(self.individual_parameters[variable_ind].shape[1]):
                    patient_dict[f"{variable_ind}_{dim}"] = (
                        self.individual_parameters[variable_ind][:, dim]
                        .numpy()
                        .reshape(-1)
                    )

        df_individual_parameters = pd.DataFrame(patient_dict).set_index("ID")

        # If you want to load cofactors too
        if cofactors is not None:
            if isinstance(cofactors, str):
                cofactors = [cofactors]

            cofactor_dict = {"ID": list(self.data.individuals.keys())}

            for cofactor in cofactors:
                cofactor_dict[cofactor] = [
                    self.data.individuals[idx].cofactors[cofactor]
                    for idx in cofactor_dict["ID"]
                ]

            df_cofactors = pd.DataFrame(cofactor_dict).set_index("ID")
            df_individual_parameters = df_individual_parameters.join(df_cofactors)

        return df_individual_parameters

    def save_individual_parameters_csv(
        self, path: str, idx: list[IDType] = None, cofactors=None, **args
    ):
        """
        Save the individual parameters in a csv format.

        Parameters
        ----------
        path : :obj:`str`
            The logs' path.
        idx : :obj:`list` [:obj:`str`], optional (default None)
            Contain the IDs of the selected subjects. If ``None``, all the subjects are selected.
        cofactors : :obj:`str` or :obj:`list` [:obj:`str`], optional (default None)
            Contains the cofactor(s) to join to the logs dataframe.
        **args
            Parameters to pass to :meth:`pandas.DataFrame.to_csv`.

        Notes
        -----
        The cofactors must be present in the leaspy data object stored into the :attr:`.data` attribute of the result instance.
        See the example.

        Examples
        --------
        Save the individual parameters of the twenty first subjects.

        >>> from leaspy.algo import AlgorithmSettings
        >>> from leaspy.api import Leaspy
        >>> from leaspy.io.data import Data
        >>> leaspy_logistic = Leaspy('logistic')
        >>> data = Data.from_csv_file('data/my_leaspy_data.csv') # replace with your own path!
        >>> genes_cofactors = pd.read_csv('data/genes_cofactors.csv')  # replace with your own path!
        >>> data.load_cofactors(genes_cofactors, ['GENES'])
        >>> model_settings = AlgorithmSettings('mcmc_saem', seed=0)
        >>> personalize_settings = AlgorithmSettings('mode_real', seed=0)
        >>> leaspy_logistic.fit(data, model_settings)
        >>> individual_results = leaspy_logistic.personalize(data, model_settings)
        >>> output_path = 'outputs/logistic_seed0-mode_real_seed0-individual_parameter.csv'
        >>> idx = list(individual_results.individual_parameters.keys())[:20]
        >>> individual_results.save_individual_parameters_csv(output_path, idx, cofactors='GENES')
        """
        self._check_folder_existence(path)

        df_individual_parameters = self.get_dataframe_individual_parameters(
            cofactors=cofactors
        )
        if idx:
            if not isinstance(idx, list):
                raise LeaspyIndividualParamsInputError(
                    "Input 'idx' must be a list, even if it contains only one element! "
                    f"You gave idx={idx} which is of type {type(idx)}."
                )
            df_individual_parameters = df_individual_parameters.loc[idx]
        df_individual_parameters.to_csv(path, index=True, **args)

    def save_individual_parameters_json(
        self, path: str, idx: list[IDType] = None, human_readable=None, **args
    ):
        """
        Save the individual parameters in a json format.

        Parameters
        ----------
        path : :obj:`str`
            The logs' path.
        idx : :obj:`list` [:obj:`str`], optional (default None)
            Contain the IDs of the selected subjects. If ``None``, all the subjects are selected.
        human_readable : Any, optional (default None) -->  TODO change to bool

            .. deprecated:: 1.0

                * If None (default): save as json file
                * If not None: call :meth:`.save_individual_parameters_torch`.
        **args
            Arguments to pass to json.dump.
            Default to: dict(indent=2)

        Raises
        ------
        :class:`NotADirectoryError`
            if parent directory of path does not exist.

        Examples
        --------
        Save the individual parameters of the twenty first subjects.

        >>> from leaspy.algo import AlgorithmSettings
        >>> from leaspy.api import Leaspy
        >>> from leaspy.io.data import Data
        >>> leaspy_logistic = Leaspy('logistic')
        >>> data = Data.from_csv_file('data/my_leaspy_data.csv')
        >>> model_settings = AlgorithmSettings('mcmc_saem', seed=0)
        >>> personalize_settings = AlgorithmSettings('mode_real', seed=0)
        >>> leaspy_logistic.fit(data, model_settings)
        >>> individual_results = leaspy_logistic.personalize(data, model_settings)
        >>> output_path = 'outputs/logistic_seed0-mode_real_seed0-individual_parameter.json'
        >>> idx = list(individual_results.individual_parameters.keys())[:20]
        >>> individual_results.save_individual_parameters_json(output_path, idx)
        """
        self._check_folder_existence(path)
        dump = self._get_dump(idx)
        if human_readable is not None:
            warnings.warn(
                "This parameter is deprecated! To save as a torch file, use the method "
                "'save_individual_parameters_torch'.",
                DeprecationWarning,
                stacklevel=2,
            )
            self.save_individual_parameters_torch(path, idx)
        else:
            # Default json.dump kwargs:
            args = {"indent": 2, **args}

            with open(path, "w") as fp:
                json.dump(dump, fp, **args)

    def save_individual_parameters_torch(
        self, path: str, idx: list[IDType] = None, **args
    ):
        """
        Save the individual parameters in a torch format.

        Parameters
        ----------
        path : :obj:`str`
            The logs' path.
        idx : :obj:`list` [:obj:`str`], optional (default None)
            Contain the IDs of the selected subjects. If ``None``, all the subjects are selected.
        **args
            Arguments to pass to torch.save.

        Raises
        ------
        :exc:`NotADirectoryError`
            if parent directory of path does not exist.

        Examples
        --------
        Save the individual parameters of the twenty first subjects.

        >>> from leaspy.algo import AlgorithmSettings
        >>> from leaspy.api import Leaspy
        >>> from leaspy.io.data import Data
        >>> leaspy_logistic = Leaspy('logistic')
        >>> data = Data.from_csv_file('data/my_leaspy_data.csv')
        >>> model_settings = AlgorithmSettings('mcmc_saem', seed=0)
        >>> personalize_settings = AlgorithmSettings('mode_real', seed=0)
        >>> leaspy_logistic.fit(data, model_settings)
        >>> individual_results = leaspy_logistic.personalize(data, model_settings)
        >>> output_path = 'outputs/logistic_seed0-mode_real_seed0-individual_parameter.pt'
        >>> idx = list(individual_results.individual_parameters.keys())[:20]
        >>> individual_results.save_individual_parameters_torch(output_path, idx)
        """
        self._check_folder_existence(path)
        dump = self._get_dump(idx)
        torch.save(dump, path, **args)

    @staticmethod
    def _check_folder_existence(path: str):
        """
        Checks whether the folder in the given file path exists.

        Parameters
        ----------
        path : :obj:`str`
            The file path to check. May include a directory component.

        Raises
        ------
        :exc:`NotADirectoryError`
            If the directory part of the path is non-empty and does not exist.
        """
        # Test path's folder existence (if path contain a folder)
        dir_path = os.path.dirname(path)
        if not (dir_path == "" or os.path.isdir(dir_path)):
            raise NotADirectoryError(
                f"Cannot save individual parameter at path {path}. The folder does not exist!"
            )

    def _get_dump(self, idx: list[IDType] = None):
        """
        Convert the individual_parameters attribute into a dictionary of list. The univariate parameters values
        like xi and tau are squeeze from shape (n_subjects, 1) to (n_subjects,).
        One can select only the wanted subject by specifying their ID with 'idx' parameter.

        Parameters
        ----------
        idx : :obj:`list`, optional (default None)
            Contains the ID of the selected subjects.

        Returns
        -------
        :obj:`dict`
            A dictionary where keys are parameter names and values are lists of parameter values,
            either as flat lists (for univariate parameters) or lists of lists (for multivariate ones).
        """
        dump: dict = copy.deepcopy(self.individual_parameters)
        # Ex: individual_parameters = {'param1': torch.tensor([[1], [2], [3]]), ...}

        # Select only the wanted subjects
        if idx is not None:
            if not isinstance(idx, list):
                raise LeaspyIndividualParamsInputError(
                    "Input 'idx' must be a list, even if it contains only one element! "
                    f"You gave idx={idx} which is of type {type(idx)}."
                )
            selected_id = [self.ID_to_idx[val] for val in idx]
            dump = {key: val[selected_id] for key, val in dump.items()}

        for key in dump.keys():
            if not isinstance(dump[key], list):
                # For multivariate parameter - like sources
                # convert tensor([[1, 2], [2, 3]]) into [[1, 2], [2, 3]]
                if dump[key].shape[1] == 2:
                    dump[key] = dump[key].tolist()
                # for univariate parameters - like xi & tau
                # convert tensor([[1], [2], [3]]) into [1, 2, 3] => squeeze it
                elif dump[key].shape[1] == 1:
                    dump[key] = dump[key].squeeze().tolist()
        return dump

    @classmethod
    def load_individual_parameters_from_csv(cls, path: str, *, verbose=True, **kwargs):
        """
        Load individual parameters from a csv.

        Parameters
        ----------
        path : :obj:`str`
            The file's path. The csv file musts contain two columns named 'tau' and 'xi'. If the individual parameters
            come from a multivariate model, it must also contain the columns 'sources_i' for i in [0, ..., n_sources].
        verbose : :obj:`bool` (default True)
            Whether to have verbose output or not
        **kwargs
            Parameters to pass to :func:`pandas.read_csv`.

        Returns
        -------
        :obj:`dict` [:obj:`str`, :class:`torch.Tensor`]
            A dictionary of torch.tensor which contains the individual parameters.

        Examples
        --------
        Load an individual parameters dictionary from a saved file.

        >>> from leaspy.io.outputs import Result
        >>> path = 'outputs/logistic_seed0-mode_real_seed0-individual_parameter.csv'
        >>> individual_parameters = Result.load_individual_parameters_from_csv(path)
        """
        df = pd.read_csv(path, **kwargs)
        if verbose:
            print("Load from csv file ... conversion to torch")
        return cls.load_individual_parameters_from_dataframe(df)

    @staticmethod
    def load_individual_parameters_from_dataframe(df: pd.DataFrame):
        """
        Load individual parameters from a :class:`pandas.DataFrame`.

        Parameters
        ----------
        df : :class:`pandas.DataFrame`
            Must contain two columns named 'tau' and 'xi'. If the individual parameters come from a multivariate model,
            it must also contain the columns 'sources_i' for i in [0, ..., n_sources].

        Returns
        -------
        :obj:`dict`[:obj:`str`, :class:`torch.Tensor`]
            A dictionary of torch.tensor which contains the individual parameters.
        """
        df.columns = [header.lower() for header in df.columns]
        sources_index = ["sources" in header for header in df.columns]
        ind_param = {
            "tau": torch.tensor(df["tau"].values, dtype=torch.float32).view(-1, 1),
            "xi": torch.tensor(df["xi"].values, dtype=torch.float32).view(-1, 1),
        }
        if any(sources_index):
            ind_param["sources"] = torch.tensor(
                df.iloc[:, sources_index].values, dtype=torch.float32
            )
        return ind_param

    @staticmethod
    def load_individual_parameters_from_json(path: str, *, verbose=True, **kwargs):
        """
        Load individual parameters from a json file.

        Deprecated : also load torch files.

        Parameters
        ----------
        path : :obj:`str`
            The file's path.
        verbose : :obj:`bool` (default True)
            Whether to have verbose output or not
        **kwargs
            Parameters to pass to :func:`json.load`.

        Returns
        -------
        :obj:`dict` [:obj:`str`, :class:`torch.Tensor`]
            A dictionary of `torch.Tensor` which contains the individual parameters.

        Examples
        --------
        Load an individual parameters dictionary from a saved file.

        >>> from leaspy.io.outputs import Result
        >>> path = 'outputs/logistic_seed0-mode_real_seed0-individual_parameter.json'
        >>> individual_parameters = Result.load_individual_parameters_from_json(path)
        """
        # Test if file is a json file
        try:
            with open(path, "r") as f:
                individual_parameters = json.load(f, **kwargs)
            if verbose:
                print("Load from json file ... conversion to torch")

            for key in individual_parameters.keys():
                # Convert every list in torch.tensor
                individual_parameters[key] = torch.tensor(
                    individual_parameters[key], dtype=torch.float32
                )
                # If tensor is 1-dimensional tensor([1, 2, 3]) => reshape it in tensor([[1], [2], [3]])
                if individual_parameters[key].dim() == 1:
                    individual_parameters[key] = individual_parameters[key].view(-1, 1)
        # Else if it is a torch file
        except UnicodeDecodeError:
            warnings.warn(
                "To load a torch file, use the static method result `load_individual_parameters_from_torch`",
                DeprecationWarning,
                stacklevel=2,
            )

            individual_parameters = torch.load(path)  # load function from torch
            if verbose:
                print("Load from torch file")

        return individual_parameters

    @staticmethod
    def load_individual_parameters_from_torch(path: str, *, verbose=True, **kwargs):
        """
        Load individual parameters from a torch file.

        Parameters
        ----------
        path : :obj:`str`
            The file's path.
        verbose : :obj:`bool` (default True)
            Whether to have verbose output or not
        **kwargs
            Parameters to pass to :func:`torch.load`.

        Returns
        -------
        :obj:`dict` [:obj:`str`, :class:`torch.Tensor`]
            A dictionary of `torch.Tensor` which contains the individual parameters.

        Examples
        --------
        Load an individual parameters dictionary from a saved file.

        >>> from leaspy.io.outputs import Result
        >>> path = 'outputs/logistic_seed0-mode_real_seed0-individual_parameter.pt'
        >>> individual_parameters = Result.load_individual_parameters_from_torch(path)
        """
        if verbose:
            print("Load from torch file")
        individual_parameters = torch.load(path, **kwargs)
        for key, val in individual_parameters.items():
            if not isinstance(val, torch.Tensor):
                individual_parameters[key] = torch.tensor(val, dtype=torch.float32)
            if individual_parameters[key].ndim != 2:
                individual_parameters[key] = individual_parameters[key].unsqueeze(-1)
        return individual_parameters

    @classmethod
    def load_individual_parameters(cls, path_or_df, **kwargs):
        """
        Load individual parameters from a :class:`pandas.DataFrame`, a csv, a json file or a torch file.

        Parameters
        ----------
        path_or_df : str or :class:`pandas.DataFrame`
            The file's path or a DataFrame containing the individual parameters.
        **kwargs
            Keyword-arguments to be passed to the corresponding load function.

        Returns
        -------
        :obj:`dict` [:obj:`str`, :class:`torch.Tensor`]
            A dictionary of torch.tensor which contains the individual parameters.

        Raises
        ------
        :exc:`FileNotFoundError`
            if path is invalid
        """
        if isinstance(path_or_df, pd.DataFrame):
            return cls.load_individual_parameters_from_dataframe(path_or_df)
        elif isinstance(path_or_df, str):
            file_extension = os.path.splitext(path_or_df)[-1]
            if file_extension == ".csv":
                return cls.load_individual_parameters_from_csv(path_or_df, **kwargs)
            elif file_extension == ".json":
                return cls.load_individual_parameters_from_json(path_or_df, **kwargs)
            else:
                if file_extension not in (".pt", ".p"):
                    warnings.warn(
                        f"File extension not recognized (got '{file_extension}')."
                        "Trying to load with torch by default.",
                        RuntimeWarning,
                        stacklevel=2,
                    )
                return cls.load_individual_parameters_from_torch(path_or_df, **kwargs)
        else:
            raise LeaspyIndividualParamsInputError(
                "The given input must be a pandas.DataFrame or a string "
                "giving the path of the file containing the individual parameters!"
            )

    @classmethod
    def load_result(cls, data, individual_parameters, *, cofactors=None, **kwargs):
        """
        Load a `Result` class object from two file - one for the individual data & one for the individual parameters.

        Parameters
        ----------
        data : :obj:`str` or :class:`pandas.DataFrame` or :class:`.Data`
            The file's path or a DataFrame containing the features' scores.
        individual_parameters : :obj:`str` or :class:`pandas.DataFrame`
            The file's path or a DataFrame containing the individual parameters.
        cofactors : :obj:`str` or :class:`pandas.DataFrame`, optional (default None)
            The file's path or a DataFrame containing the individual cofactors.
            The ID must be in index! Thus, the shape is (n_subjects, n_cofactors).
        **kwargs
            Parameters to pass to `Result.load_individual_parameters` method.

        Returns
        -------
        :class:`Result`
            A Result class object which contains the individual parameters and the individual data.

        Examples
        --------
        Launch an individual parameters estimation, save it and reload it.

        >>> from leaspy.algo import AlgorithmSettings
        >>> from leaspy.io.outputs import Result
        >>> from leaspy.api import Leaspy
        >>> from leaspy.io.data import Data
        >>> leaspy_logistic = Leaspy('logistic')
        >>> data = Data.from_csv_file('data/my_leaspy_data.csv')
        >>> model_settings = AlgorithmSettings('mcmc_saem', seed=0)
        >>> personalize_settings = AlgorithmSettings('mode_real', seed=0)
        >>> leaspy_logistic.fit(data, model_settings)
        >>> individual_results = leaspy_logistic.personalize(data, model_settings)
        >>> path_data = 'data/my_leaspy_data.csv'
        >>> path_individual_parameters = 'outputs/logistic_seed0-mode_real_seed0-individual_parameter.json'
        >>> individual_results.data.to_dataframe().to_csv(path_data)
        >>> individual_results.save_individual_parameters_json(path_individual_parameters)
        >>> individual_parameters = Result.load_result(path_data, path_individual_parameters)
        """
        if isinstance(data, Data):
            pass
        elif isinstance(data, str):
            data = Data.from_csv_file(data)
        elif isinstance(data, pd.DataFrame):
            data = Data.from_dataframe(data)
        else:
            raise LeaspyTypeError(
                "The given `data` input must be a Data instance, a pandas.DataFrame "
                "or a string giving the path of the file containing the features' scores! "
                f"You gave an object of type {type(data)}"
            )

        if cofactors is not None:
            if isinstance(cofactors, str):
                cofactors_df = pd.read_csv(cofactors, dtype={"ID": str}).set_index("ID")
            elif isinstance(cofactors, pd.DataFrame):
                cofactors_df = cofactors.copy()
            else:
                raise LeaspyTypeError(
                    "The given `cofactors` input must be a pandas.DataFrame "
                    "or a string giving the path of the file containing the cofactors! "
                    f"You gave an object of type {type(cofactors)}"
                )
            data.load_cofactors(cofactors_df)

        individual_parameters = cls.load_individual_parameters(
            individual_parameters, **kwargs
        )
        return cls(data, individual_parameters)

    def get_error_distribution_dataframe(self, model, cofactors=None):
        """
        Get signed residual distribution per patient, per sub-score & per visit. Each residual is equal to the
        modeled data minus the observed data.

        Parameters
        ----------
        model : :class:`~.models.abstract_model.AbstractModel`
        cofactors : str, list [str], optional (default None)
            Contains the cofactors' names to be included in the DataFrame. By default, no cofactors are returned.
            If cofactors == "all", all the available cofactors are returned.

        Returns
        -------
        residuals_dataframe : :class:`pandas.DataFrame` with index ['ID', 'TIME']

        Examples
        --------
        Get mean absolute error per feature:

        >>> from leaspy.algo import AlgorithmSettings
        >>> from leaspy.api import Leaspy
        >>> from leaspy.io.data import Data
        >>> data = Data.from_csv_file("/my/data/path")
        >>> leaspy_logistic = Leaspy('logistic')
        >>> settings = AlgorithmSettings("mcmc_saem", seed=0)
        >>> leaspy_logistic.calibrate(data, settings)
        >>> settings = AlgorithmSettings("mode_real", seed=0)
        >>> results = leaspy_logistic.personalize(data, settings)
        >>> residuals_dataframe = results.get_error_distribution_dataframe(model)
        >>> residuals_dataframe.abs().mean()
        """
        residuals_dataset = Dataset(self.data)
        residuals_dataset.values = (
            model.compute_individual_tensorized(
                residuals_dataset.timepoints, self.individual_parameters
            )
            - residuals_dataset.values
        )
        residuals_dataframe = residuals_dataset.to_pandas()

        if cofactors is not None:
            if isinstance(cofactors, str):
                if cofactors == "all":
                    cofactors_list = self.data.cofactors
                else:
                    cofactors_list = [cofactors]
            elif isinstance(cofactors, list):
                cofactors_list = cofactors
            else:
                raise LeaspyTypeError(
                    "The given `cofactors` input must be a string or a list of strings! "
                    f"You gave an object of type {type(cofactors)}"
                )
            cofactors_df = (
                self.data.to_dataframe(cofactors=cofactors)
                .groupby("ID")
                .first()[cofactors_list]
            )
            residuals_dataframe = residuals_dataframe.join(cofactors_df)

        return residuals_dataframe

    ###############################################################
    # DEPRECATION WARNINGS
    # These following methods will be removed in a future release
    ###############################################################

    @staticmethod
    def get_cofactor_states(cofactors: list) -> list:
        """
        .. deprecated:: 1.0

        Given a list of string return the list of unique elements.

        Parameters
        ----------
        cofactors : list[str]
            Distribution list of the cofactors.

        Returns
        -------
        list
            Unique occurrences of the input vector.
        """
        warnings.warn("This method will soon be removed!", DeprecationWarning)

        result = set(cofactors)
        return sorted(result)

    @staticmethod
    def _get_parameter_name_and_dim(param: str):
        """
        Splits a parameter string into its base name and optional dimension.

        Parameters
        ----------
        param : str
            The parameter name, possibly including a numeric suffix indicating a dimension.

        Returns
        -------
        tuple
            A tuple `(name, dim)`, where `name` is the base parameter name as a string,
            and `dim` is the parsed integer dimension, or `None` if no valid dimension is found.

        Examples
        --------
        >>> _get_parameter_name_and_dim(`abc_def_34`)
        ('abc_def', 34)
        """
        param_short, *param_dim = param.rsplit("_", maxsplit=1)  # from right

        if param_dim:
            # we found a last "***_NNN", return this split if and only if NNN can be interpreted as an integer
            try:
                return param_short, int(param_dim[0])
            except Exception:
                pass

        return param, None

    def get_parameter_distribution(self, parameter: ParamType, cofactor=None):
        """
        .. deprecated:: 1.0

        Return the wanted parameter distribution (one distribution per covariate state).

        Parameters
        ----------
        parameter : str
            The wanted parameter's name (ex: 'xi', 'tau', ...).
            It can also be `sources_i` to only get the i-th dimension of multivariate `sources` parameter.
        cofactor : str, optional (default None)
            The wanted cofactor's name.

        Returns
        -------
        list[float] or dict[str, Any]

        Raises
        ------
        :exc:`.LeaspyIndividualParamsInputError`
            if unsupported individual parameters
        :exc:`.LeaspyInputError`
            if unknown cofactor

        Notes
        -----
        If ``cofactor is None``:
            * If the parameter is univariate => return a list the parameter's distribution:
                list[float]
            * If the parameter is multivariate => return a dictionary:
                {'parameter1': distribution of parameter variable 1, 'parameter2': ...}

        If ``cofactor is not None``:
            * If the parameter is univariate => return a dictionary:
                {'cofactor1': parameter distribution such that patient.covariate = covariate1, 'cofactor2': ...}
            * If the parameter is multivariate => return a dictionary:
                {'cofactor1': {'parameter1': ..., 'parameter2': ...}, 'cofactor2': {...}, ...}
        """
        warnings.warn("This method will soon be removed!", DeprecationWarning)

        param_short, param_dim = self._get_parameter_name_and_dim(parameter)
        parameter_distribution = self.individual_parameters[
            param_short
        ]  # torch.tensor class object
        # parameter_distribution is of size (N_subjects, N_dimension_of_parameter)

        if param_dim is not None:
            parameter_distribution = parameter_distribution[:, [param_dim]]

        # Check the tensor's dimension is <= 2
        p_ndim = parameter_distribution.ndimension()
        if p_ndim > 2:
            raise LeaspyIndividualParamsInputError(
                f"The chosen parameter {parameter} is a tensor "
                f"of dimension {p_ndim}: it should be <= 2!"
            )
        ##############################################
        # If there is no cofactor to take into account
        ##############################################
        if cofactor is None:
            # If parameter is 1-dimensional
            if parameter_distribution.shape[1] == 1:
                # return a list of length = N_subjects
                parameter_distribution = parameter_distribution.view(-1).tolist()
            # Else transpose it and split it in a dictionary
            else:
                # return {'parameter1': distribution of parameter variable 1, 'parameter2': ... }
                parameter_distribution = {
                    parameter + str(i): val
                    for i, val in enumerate(
                        parameter_distribution.transpose(0, 1).tolist()
                    )
                }
            return parameter_distribution

        ############################################################
        # If the distribution as asked for different cofactor values
        ############################################################
        # Check if the cofactor exist
        all_cofactors = self.data[0].cofactors.keys()
        if cofactor not in all_cofactors:
            raise LeaspyInputError(
                f"The cofactor '{cofactor}' do not exist. "
                f"Here are the available cofactors: {list(all_cofactors)}"
            )
        # Get possible covariate stats
        # cofactors = [_.cofactors[cofactor] for _ in self.data if _.cofactors[cofactor] is not None]
        cofactors = self.get_cofactor_distribution(cofactor)
        cofactor_states = self.get_cofactor_states(cofactors)

        # Initialize the result
        distributions = {}

        # If parameter 1-dimensional
        if parameter_distribution.shape[1] == 1:
            parameter_distribution = parameter_distribution.view(
                -1
            ).tolist()  # ex: [1, 2, 3]
            # Create one entry per cofactor state
            for p in cofactor_states:
                if p not in distributions.keys():
                    distributions[p] = []
                # For each covariate state, get parameter distribution
                for i, v in enumerate(parameter_distribution):
                    if self.data[i].cofactors[cofactor] == p:
                        distributions[p].append(v)
                        # return {'cofactor1': ..., 'cofactor2': ...}
        else:
            # Create one dictionary per cofactor state
            for p in cofactor_states:
                if p not in distributions.keys():
                    # Create one dictionary per parameter dimension
                    distributions[p] = {
                        parameter + str(i): []
                        for i in range(parameter_distribution.shape[1])
                    }
                # Fill these entries by the corresponding values of the corresponding subject
                for i, v in enumerate(parameter_distribution.tolist()):
                    if self.data[i].cofactors[cofactor] == p:
                        for j, key in enumerate(distributions[p].keys()):
                            distributions[p][key].append(v[j])
                            # return {'cofactor1': {'parameter1': .., 'parameter2': ..}, 'cofactor2': { .. }, .. }
        return distributions

    def get_cofactor_distribution(self, cofactor: str):
        """
        .. deprecated:: 1.0

        Get the list of the cofactor's distribution.

        Parameters
        ----------
        cofactor : str
            Cofactor's name

        Returns
        -------
        list
            Cofactor's distribution.
        """
        warnings.warn("This method will soon be removed!", DeprecationWarning)

        return [d.cofactors[cofactor] for d in self.data]

    def get_patient_individual_parameters(self, idx: IDType):
        """
        .. deprecated:: 1.0

        Get the dictionary of the wanted patient's individual parameters

        Parameters
        ----------
        idx : str
            ID of the wanted patient

        Returns
        -------
        dict[param_name:str, `torch.Tensor`]
            Patient's individual parameters
        """
        warnings.warn("This method will soon be removed!", DeprecationWarning)

        # indices = list(self.data.individuals.keys())
        # idx_number = int(
        #     np.where(np.array(indices) == idx)[0])
        idx_number = [
            idx_nbr for idx_nbr, idxx in self.data.iter_to_idx.items() if idxx == idx
        ][0]

        patient_dict = dict.fromkeys(self.individual_parameters.keys())

        for variable_ind in list(self.individual_parameters.keys()):
            patient_dict[variable_ind] = self.individual_parameters[variable_ind][
                idx_number
            ]

        return patient_dict
