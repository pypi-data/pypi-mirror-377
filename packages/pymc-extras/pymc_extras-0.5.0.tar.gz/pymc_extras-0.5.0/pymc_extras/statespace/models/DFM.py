from collections.abc import Sequence
from typing import Any

import pytensor
import pytensor.tensor as pt

from pymc_extras.statespace.core.statespace import PyMCStateSpace
from pymc_extras.statespace.models.utilities import make_default_coords
from pymc_extras.statespace.utils.constants import (
    ALL_STATE_AUX_DIM,
    ALL_STATE_DIM,
    AR_PARAM_DIM,
    ERROR_AR_PARAM_DIM,
    EXOG_STATE_DIM,
    FACTOR_DIM,
    OBS_STATE_AUX_DIM,
    OBS_STATE_DIM,
    TIME_DIM,
)

floatX = pytensor.config.floatX


class BayesianDynamicFactor(PyMCStateSpace):
    r"""
    Dynamic Factor Models

    Notes
    -----
    The Dynamic Factor Model (DFM) is a multivariate state-space model used to represent high-dimensional time series
    as being driven by a smaller set of unobserved dynamic factors.

    Given a set of observed time series :math:`\{y_t\}_{t=0}^T`, where

    .. math::
        y_t = \begin{bmatrix} y_{1,t} & y_{2,t} & \cdots & y_{k_{\text{endog}},t} \end{bmatrix}^T,

    the DFM assumes that each series is a linear combination of a few latent factors and (optionally) autoregressive errors.

    Let:
    - :math:`k` be the number of dynamic factors (k_factors),
    - :math:`p` be the order of the latent factor process (factor_order),
    - :math:`q` be the order of the observation error process (error_order).

    The model equations are in reduced form is:

    .. math::
        y_t &= \Lambda f_t + B x_t + u_t + \eta_t \\
        f_t &= A_1 f_{t-1} + \cdots + A_p f_{t-p} + \varepsilon_{f,t} \\
        u_t &= C_1 u_{t-1} + \cdots + C_q u_{t-q} + \varepsilon_{u,t}

    Where:
    - :math:`f_t` is the vector of latent dynamic factors (size :math:`k`),
    - :math:`x_t` is an optional vector of exogenous variables
    - :math:`u_t` is a vector of autoregressive observation errors (if `error_var=True` with a VAR(q) structure, else treated as independent AR processes),
    - :math:`\eta_t \sim \mathcal{N}(0, H_t)` is an optional measurement error (if `measurement_error=True`),
    - :math:`\varepsilon_{f,t} \sim \mathcal{N}(0, I)` and :math:`\varepsilon_{u,t} \sim \mathcal{N}(0, \Sigma_u)` are independent noise terms.
        To identify the factors, the innovations to the factor process are standardized with identity covariance.

    Internally, the model is represented in state-space form by stacking all current and lagged latent factors and (if present)
    AR observation errors into a single state vector of dimension:  :math:: k_{\text{states}} = k \cdot p + k_{\text{endog}} \cdot q,
    where :math:`k_{\text{endog}}` is the number of observed time series.

    The state vector is defined as:

    .. math::
        s_t = \begin{bmatrix}
            f_t(1) \\
            \vdots \\
            f_t(k) \\
            f_{t-p+1}(1) \\
            \vdots \\
            f_{t-p+1}(k) \\
            u_t(1) \\
            \vdots \\
            u_t(k_{\text{endog}}) \\
            \vdots \\
            u_{t-q+1}(1) \\
            \vdots \\
            u_{t-q+1}(k_{\text{endog}})
        \end{bmatrix}
        \in \mathbb{R}^{k_{\text{states}}}

    The transition equation is given by:

    .. math::
        s_{t+1} = T s_t + R \epsilon_t

    Where:
    - :math:`T` is the state transition matrix, composed of:
        - VAR coefficients :math:`A_1, \dots, A_{p*k_factors}` for the factors,
        - (if enabled) AR coefficients :math:`C_1, \dots, C_q` for the observation errors.
        .. math::
            T = \begin{bmatrix}
            A_{1,1}  &   A_{1,2}  &   \cdots  &   A_{1,p}  &   0       &   0       &   \cdots  &   0 \\
            A_{2,1}  &   A_{2,2}  &   \cdots  &   A_{2,p}  &   0       &   0       &   \cdots  &   0 \\
            1       &   0       &   \cdots  &   0          &   0       &   0       &   \cdots  &   0 \\
            0       &   1       &   \cdots  &   0          &   0       &   0       &   \cdots  &   0 \\
            \vdots  &   \vdots  &   \ddots  &   \vdots     &   \vdots  &   \vdots  &   \ddots  &   \vdots \\
            \hline
            0       &   0       &   \cdots  &   0       &   C_{1,1}  &  \cdots  &    C_{1,2} &   C_{1,q} \\
            0       &   0       &   \cdots  &   0       &   1       &   0       &   \cdots  &   0 \\
            0       &   0       &   \cdots  &   0       &   0       &   1       &   \cdots  &   0 \\
            \vdots  &   \vdots  &           &   \vdots  &   \vdots  &   \vdots  &   \ddots  &   \vdots
            \end{bmatrix}
            \in \mathbb{R}^{k_{\text{states}} \times k_{\text{states}}}

    - :math:`\epsilon_t` contains the independent shocks (innovations) and has dimension :math:`k + k_{\text{endog}}` if AR errors are included.
        .. math::
            \epsilon_t = \begin{bmatrix}
            \epsilon_{f,t} \\
            \epsilon_{u,t}
            \end{bmatrix}
            \in \mathbb{R}^{k +  k_{\text{endog}}}

    - :math:`R` is a selection matrix mapping shocks to state transitions.
        .. math::
            R = \begin{bmatrix}
            1       &   0       &   \cdots  &   0       &   0       &   0       &   \cdots  &   0 \\
            0       &   1       &   \cdots  &   0       &   0       &   0       &   \cdots  &   0 \\
            \vdots  &   \vdots  &   \ddots  &   \vdots  &   \vdots  &   \vdots  &   \ddots  &   \vdots \\
            0       &   0       &   \cdots  &   1       &   0       &   0       &   \cdots  &   0 \\
            0       &   0       &   \cdots  &   0       &   1       &   0       &   \cdots  &   0 \\
            0       &   0       &   \cdots  &   0       &   0       &   1       &   \cdots  &   0 \\
            \vdots  &   \vdots  &   \ddots  &   \vdots  &   \vdots  &   \vdots  &   \ddots  &   \vdots \\
            \end{bmatrix}
            \in \mathbb{R}^{k_{\text{states}} \times (k + k_{\text{endog}})}

    The observation equation is given by:

    .. math::

        y_t = Z s_t + \eta_t

    where

    - :math:`y_t` is the vector of observed variables at time :math:`t`

    - :math:`Z` is the design matrix of the state space representation
        .. math::
            Z = \begin{bmatrix}
            \lambda_{1,1}       &   \lambda_{1,k}   &   \vdots    &   1   &   0   &   \cdots  &   0   &   0   &   \cdots  &   0 \\
            \lambda_{2,1}       &   \lambda_{2,k}   &   \vdots    &   0   &   1   &   \cdots   &   0   &   \cdots  &   0 \\
            \vdots              &   \vdots          &   \vdots  &   \vdots  &   \ddots  &   \vdots  &   \vdots  &   \ddots  &   \vdots \\
            \lambda_{k_{\text{endog}},1}  &   \cdots  &   \lambda_{k_{\text{endog}},k}  &   0   &   0   &   \cdots  &   1   &   0   &   \cdots  &   0 \\
            \end{bmatrix}
            \in \mathbb{R}^{k_{\text{endog}} \times k_{\text{states}}}

    - :math:`\eta_t` is the vector of observation errors at time :math:`t`

    When exogenous variables :math:`x_t` are present, the implementation follows `pymc_extras/statespace/models/structural/components/regression.py`.
    In this case, the state vector is extended to include the beta parameters, and the design matrix is modified accordingly,
    becoming 3-dimensional to handle time-varying exogenous regressors.
    This approach provides greater flexibility, controlled by the boolean flags `shared_exog_state` and `exog_innovations`.
    Unlike Statsmodels, where exogenous variables are included only in the observation equation, here they are fully integrated into the state-space
    representation.

    .. warning::

        Identification can be an issue, particularly when many observed series load onto only a few latent factors.
        These models are only identified up to a sign flip in the factor loadings. Proper prior specification is crucial
        for good estimation and inference.

    Examples
    --------
    The following code snippet estimates a dynamic factor model with 1 latent factors,
    a AR(2) structure on the factor and a AR(1) structure on the errors:

    .. code:: python

        import pymc_extras.statespace as pmss
        import pymc as pm

        # Create DFM Statespace Model
        dfm_mod = pmss.BayesianDynamicFactor(
                k_factors=1,                # Number of latent dynamic factors
                factor_order=2,             # Number of lags for the latent factor process
                endog_names=data.columns,   # Names of the observed time series (endogenous variables) (we could also use k_endog = len(data.columns))
                error_order=1,              # Order of the autoregressive process for the observation noise (i.e., AR(q) error, here q=1)
                error_var=False,            # If False, models errors as separate AR processes
                error_cov_type="diagonal",  # Structure of the observation error covariance matrix: uncorrelated noise across series
                measurement_error=True,     # Whether to include a measurement error term in the model
                verbose=True
            )

        # Unpack coords
        coords = dfm_mod.coords


        with pm.Model(coords=coords) as pymc_mod:
            # Priors for the initial state mean and covariance
            x0 = pm.Normal("x0", dims=["state_dim"])
            P0 = pm.HalfNormal("P0", dims=["state_dim", "state_dim"])

            # Factor loadings: shape (k_endog, k_factors)
            factor_loadings = pm.Normal("factor_loadings", sigma=1, dims=["k_endog", "k_factors"])

            # AR coefficients for factor dynamics: shape (k_factors, factor_order)
            factor_ar = pm.Normal("factor_ar", sigma=1, dims=["k_factors", "k_factors" * "factor_order"])

            # AR coefficients for observation noise: shape (k_endog, error_order)
            error_ar = pm.Normal("error_ar", sigma=1, dims=["k_endog", "error_order"])

            # Std devs for observation noise: shape (k_endog,)
            error_sigma = pm.HalfNormal("error_sigma", dims=["k_endog"])

            # Observation noise covariance matrix
            obs_sigma = pm.HalfNormal("sigma_obs", dims=["k_endog"])

            # Build the symbolic graph and attach it to the model
            dfm_mod.build_statespace_graph(data=data, mode="JAX")

            # Sampling
            idata = pm.sample(
                draws=500,
                chains=2,
                nuts_sampler="nutpie",
                nuts_sampler_kwargs={"backend": "jax", "gradient_backend": "jax"},
            )

    """

    def __init__(
        self,
        k_factors: int,
        factor_order: int,
        k_endog: int | None = None,
        endog_names: Sequence[str] | None = None,
        k_exog: int | None = None,
        exog_names: Sequence[str] | None = None,
        shared_exog_states: bool = False,
        exog_innovations: bool = False,
        error_order: int = 0,
        error_var: bool = False,
        error_cov_type: str = "diagonal",
        measurement_error: bool = False,
        verbose: bool = True,
    ):
        """
        Create a Bayesian Dynamic Factor Model.

        Parameters
        ----------
        k_factors : int
            Number of latent factors.

        factor_order : int
            Order of the VAR process for the latent factors. If set to 0, the factors have no autoregressive dynamics
            and are modeled as a white noise process, i.e., :math:`f_t = \varepsilon_{f,t}`.
            Therefore, the state vector will include one state per factor and "factor_ar" will not exist.

        k_endog : int, optional
            Number of observed time series. If not provided, the number of observed series will be inferred from `endog_names`.
            At least one of `k_endog` or `endog_names` must be provided.

        endog_names : list of str, optional
            Names of the observed time series. If not provided, default names will be generated as `endog_1`, `endog_2`, ..., `endog_k` based on `k_endog`.
            At least one of `k_endog` or `endog_names` must be provided.

        k_exog : int, optional
            Number of exogenous variables. If not provided, the model will not have exogenous variables.

        exog_names : Sequence[str], optional
            Names of the exogenous variables. If not provided, but `k_exog` is specified, default names will be generated as `exog_1`, `exog_2`, ..., `exog_k`.

        shared_exog_states: bool, optional
            Whether exogenous latent states are shared across the observed states. If True, there will be only one set of exogenous latent
            states, which are observed by all observed states. If False, each observed state has its own set of exogenous latent states.

        exog_innovations : bool, optional
            Whether to allow time-varying regression coefficients. If True, coefficients follow a random walk.

        error_order : int, optional
            Order of the AR process for the observation error component.
            Default is 0, corresponding to white noise errors.

        error_var : bool, optional
            If True, errors are modeled jointly via a VAR process;
            otherwise, each error is modeled separately.

        error_cov_type : {'scalar', 'diagonal', 'unstructured'}, optional
            Structure of the covariance matrix of the observation errors.

        measurement_error: bool, default True
            If true, a measurement error term is added to the model.

        verbose: bool, default True
            If true, a message will be logged to the terminal explaining the variable names, dimensions, and supports.

        """

        if k_endog is None and endog_names is None:
            raise ValueError("Either k_endog or endog_names must be provided.")
        if k_endog is None:
            k_endog = len(endog_names)
        if endog_names is None:
            endog_names = [f"endog_{i}" for i in range(k_endog)]

        self.endog_names = endog_names
        self.k_endog = k_endog
        self.k_factors = k_factors
        self.factor_order = factor_order
        self.error_order = error_order
        self.error_var = error_var
        self.error_cov_type = error_cov_type

        if k_exog is None and exog_names is None:
            self.k_exog = 0
        else:
            self.shared_exog_states = shared_exog_states
            self.exog_innovations = exog_innovations
            if k_exog is None:
                k_exog = len(exog_names) if exog_names is not None else 0
            elif exog_names is None:
                exog_names = [f"exog_{i}" for i in range(k_exog)] if k_exog > 0 else None
            self.k_exog = k_exog
            self.exog_names = exog_names

        self.k_exog_states = self.k_exog * self.k_endog if not shared_exog_states else self.k_exog
        self.exog_flag = self.k_exog > 0

        # Determine the dimension for the latent factor states.
        # For static factors, one use k_factors.
        # For dynamic factors with lags, the state include current factors and past lags.
        # If factor_order is 0, we treat the factor as static (no dynamics),
        # but it is still included in the state vector with one state per factor. Factor_ar paramter will not exist in this case.
        k_factor_states = max(self.factor_order, 1) * k_factors

        # Determine the dimension for the error component.
        # If error_order > 0 then we add additional states for error dynamics, otherwise white noise error.
        k_error_states = k_endog * error_order if error_order > 0 else 0

        # Total state dimension
        k_states = k_factor_states + k_error_states + self.k_exog_states

        # Number of independent shocks.
        # Typically, the latent factors introduce k_factors shocks.
        # If error_order > 0 and errors are modeled jointly or separately, add appropriate count.
        k_posdef = k_factors + (k_endog if error_order > 0 else 0) + self.k_exog_states
        # k_posdef = (k_factors + (k_endog if error_order > 0 else 0) + self.k_exog_states if self.exog_innovations else 0)

        # Initialize the PyMCStateSpace base class.
        super().__init__(
            k_endog=k_endog,
            k_states=k_states,
            k_posdef=k_posdef,
            verbose=verbose,
            measurement_error=measurement_error,
        )

    @property
    def param_names(self):
        names = [
            "x0",
            "P0",
            "factor_loadings",
            "factor_ar",
            "error_ar",
            "error_sigma",
            "error_cov",
            "sigma_obs",
            "beta",
            "beta_sigma",
        ]

        # Handle cases where parameters should be excluded based on model settings
        if self.factor_order == 0:
            names.remove("factor_ar")
        if self.error_order == 0:
            names.remove("error_ar")
        if self.error_cov_type in ["scalar", "diagonal"]:
            names.remove("error_cov")
        if self.error_cov_type == "unstructured":
            names.remove("error_sigma")
        if not self.measurement_error:
            names.remove("sigma_obs")
        if not self.exog_flag:
            names.remove("beta")
            names.remove("beta_sigma")
        if self.exog_flag and not self.exog_innovations:
            names.remove("beta_sigma")

        return names

    @property
    def param_info(self) -> dict[str, dict[str, Any]]:
        info = {
            "x0": {
                "shape": (self.k_states,),
                "constraints": None,
            },
            "P0": {
                "shape": (self.k_states, self.k_states),
                "constraints": "Positive Semi-definite",
            },
            "factor_loadings": {
                "shape": (self.k_endog, self.k_factors),
                "constraints": None,
            },
            "factor_ar": {
                "shape": (self.k_factors, self.factor_order * self.k_factors),
                "constraints": None,
            },
            "error_ar": {
                "shape": (
                    self.k_endog,
                    self.error_order * self.k_endog if self.error_var else self.error_order,
                ),
                "constraints": None,
            },
            "error_sigma": {
                "shape": (self.k_endog,) if self.error_cov_type == "diagonal" else (),
                "constraints": "Positive",
            },
            "error_cov": {
                "shape": (self.k_endog, self.k_endog),
                "constraints": "Positive Semi-definite",
            },
            "sigma_obs": {
                "shape": (self.k_endog,),
                "constraints": "Positive",
            },
            "beta": {
                "shape": (self.k_exog_states,),
                "constraints": None,
            },
            "beta_sigma": {
                "shape": (self.k_exog_states,),
                "constraints": "Positive",
            },
        }

        for name in self.param_names:
            info[name]["dims"] = self.param_dims[name]

        return {name: info[name] for name in self.param_names}

    @property
    def state_names(self) -> list[str]:
        """
        Returns the names of the hidden states: first factor states (with lags),
        idiosyncratic error states (with lags), then exogenous states.
        """
        names = [
            f"L{lag}.factor_{i}"
            for i in range(self.k_factors)
            for lag in range(max(self.factor_order, 1))
        ]

        if self.error_order > 0:
            names.extend(
                f"L{lag}.error_{i}" for i in range(self.k_endog) for lag in range(self.error_order)
            )

        if self.exog_flag:
            if self.shared_exog_states:
                names.extend([f"beta_{exog_name}[shared]" for exog_name in self.exog_names])
            else:
                names.extend(
                    f"beta_{exog_name}[{endog_name}]"
                    for exog_name in self.exog_names
                    for endog_name in self.endog_names
                )
        return names

    @property
    def observed_states(self) -> list[str]:
        """
        Returns the names of the observed states (i.e., the endogenous variables).
        """
        return self.endog_names

    @property
    def coords(self) -> dict[str, Sequence]:
        coords = make_default_coords(self)

        coords[FACTOR_DIM] = [f"factor_{i+1}" for i in range(self.k_factors)]

        if self.factor_order > 0:
            coords[AR_PARAM_DIM] = list(range(1, (self.factor_order * self.k_factors) + 1))

        if self.error_order > 0:
            if self.error_var:
                coords[ERROR_AR_PARAM_DIM] = list(range(1, (self.error_order * self.k_endog) + 1))
            else:
                coords[ERROR_AR_PARAM_DIM] = list(range(1, self.error_order + 1))

        if self.exog_flag:
            coords[EXOG_STATE_DIM] = list(range(1, self.k_exog_states + 1))

        return coords

    @property
    def shock_names(self) -> list[str]:
        shock_names = [f"factor_shock_{i}" for i in range(self.k_factors)]

        if self.error_order > 0:
            shock_names.extend(f"error_shock_{i}" for i in range(self.k_endog))

        if self.exog_flag:
            if self.shared_exog_states:
                shock_names.extend(f"exog_shock_{i}.shared" for i in range(self.k_exog))
            else:
                shock_names.extend(
                    f"exog_shock_{i}.endog_{j}"
                    for i in range(self.k_exog)
                    for j in range(self.k_endog)
                )

        return shock_names

    @property
    def param_dims(self):
        coord_map = {
            "x0": (ALL_STATE_DIM,),
            "P0": (ALL_STATE_DIM, ALL_STATE_AUX_DIM),
            "factor_loadings": (OBS_STATE_DIM, FACTOR_DIM),
        }
        if self.factor_order > 0:
            coord_map["factor_ar"] = (FACTOR_DIM, AR_PARAM_DIM)

        if self.error_order > 0:
            coord_map["error_ar"] = (OBS_STATE_DIM, ERROR_AR_PARAM_DIM)

        if self.error_cov_type in ["scalar"]:
            coord_map["error_sigma"] = ()

        elif self.error_cov_type in ["diagonal"]:
            coord_map["error_sigma"] = (OBS_STATE_DIM,)

        if self.error_cov_type == "unstructured":
            coord_map["error_cov"] = (OBS_STATE_DIM, OBS_STATE_AUX_DIM)

        if self.measurement_error:
            coord_map["sigma_obs"] = (OBS_STATE_DIM,)

        if self.exog_flag:
            coord_map["beta"] = (EXOG_STATE_DIM,)
            if self.exog_innovations:
                coord_map["beta_sigma"] = (EXOG_STATE_DIM,)

        return coord_map

    @property
    def data_info(self):
        if self.exog_flag:
            return {
                "exog_data": {
                    "shape": (None, self.k_exog),
                    "dims": (TIME_DIM, EXOG_STATE_DIM),
                },
            }
        return {}

    @property
    def data_names(self):
        if self.exog_flag:
            return ["exog_data"]
        return []

    def make_symbolic_graph(self):
        if not self.exog_flag:
            x0 = self.make_and_register_variable("x0", shape=(self.k_states,), dtype=floatX)
        else:
            initial_factor_loadings = self.make_and_register_variable(
                "x0", shape=(self.k_states - self.k_exog_states,), dtype=floatX
            )
            initial_betas = self.make_and_register_variable(
                "beta", shape=(self.k_exog_states,), dtype=floatX
            )
            x0 = pt.concatenate([initial_factor_loadings, initial_betas], axis=0)

        self.ssm["initial_state", :] = x0

        # Initial covariance
        P0 = self.make_and_register_variable(
            "P0", shape=(self.k_states, self.k_states), dtype=floatX
        )
        self.ssm["initial_state_cov", :, :] = P0

        # Design matrix (Z)
        # Construction with block structure:
        # When factor_order <= 1 and error_order = 0:
        #   [ A ]               A is the factor loadings matrix with shape (k_endog, k_factors)
        #
        # When factor_order > 1, add block of zeros for the factors lags:
        #   [ A | 0 ]           the zero block has shape (k_endog, k_factors * (factor_order - 1))
        #
        # When error_order > 0, add identity matrix and additional zero block for errors lags:
        #   [ A | 0 | I | 0 ]   I is the identity matrix (k_endog, k_endog) and the final zero block
        #                       has shape (k_endog, k_endog * (error_order - 1))
        #
        # When exog_flag=True, exogenous data (exog_data) is included and the design
        # matrix becomes 3D with the first dimension indexing time:
        #   - shared_exog_states=True: exog_data is broadcast across all endogenous series
        #       → shape (n_timepoints, k_endog, k_exog)
        #   - shared_exog_states=False: each endogenous series gets its own exog block
        #       → block-diagonal structure with shape (n_timepoints, k_endog, k_exog * k_endog)
        # In this case, the base design matrix (factors + errors) is repeated over
        # time and concatenated with the exogenous block. The final design matrix
        # has shape (n_timepoints, k_endog, n_columns) and combines all components.
        factor_loadings = self.make_and_register_variable(
            "factor_loadings", shape=(self.k_endog, self.k_factors), dtype=floatX
        )
        # Add factor loadings (A matrix)
        matrix_parts = [factor_loadings]

        # Add zero block for the factors lags when factor_order > 1
        if self.factor_order > 1:
            matrix_parts.append(
                pt.zeros((self.k_endog, self.k_factors * (self.factor_order - 1)), dtype=floatX)
            )
        # Add identity and zero blocks for error lags when error_order > 0
        if self.error_order > 0:
            error_matrix = pt.eye(self.k_endog, dtype=floatX)
            matrix_parts.append(error_matrix)
            matrix_parts.append(
                pt.zeros((self.k_endog, self.k_endog * (self.error_order - 1)), dtype=floatX)
            )
        if len(matrix_parts) == 1:
            design_matrix = factor_loadings * 1.0  # copy to ensure a new PyTensor variable
            design_matrix.name = "design"
            # TODO: This is a hack to ensure the design matrix isn't identically equal to the factor_loadings when error_order=0 and factor_order=0
        else:
            design_matrix = pt.concatenate(matrix_parts, axis=1)
            design_matrix.name = "design"
        # Handle exogenous variables (if any)
        if self.exog_flag:
            exog_data = self.make_and_register_data("exog_data", shape=(None, self.k_exog))
            if self.shared_exog_states:
                # Shared exogenous states: same exog data is used across all endogenous variables
                # Shape becomes (n_timepoints, k_endog, k_exog)
                Z_exog = pt.specify_shape(
                    pt.join(1, *[pt.expand_dims(exog_data, 1) for _ in range(self.k_endog)]),
                    (None, self.k_endog, self.k_exog),
                )
            else:
                # Separate exogenous states: each endogenous variable gets its own exog block
                # Create block-diagonal structure and reshape to (n_timepoints, k_endog, k_exog * k_endog)
                Z_exog = pt.linalg.block_diag(
                    *[pt.expand_dims(exog_data, 1) for _ in range(self.k_endog)]
                )
                Z_exog = pt.specify_shape(Z_exog, (None, self.k_endog, self.k_exog * self.k_endog))

            # Repeat base design_matrix over time dimension to match exogenous time series
            n_timepoints = Z_exog.shape[0]
            design_matrix_time = pt.tile(design_matrix, (n_timepoints, 1, 1))
            # Concatenate the repeated design matrix with exogenous matrix along the last axis
            # Final shape: (n_timepoints, k_endog, n_columns + n_exog_columns)
            design_matrix = pt.concatenate([design_matrix_time, Z_exog], axis=2)

        self.ssm["design"] = design_matrix

        # Transition matrix (T)
        # Construction with block-diagonal structure:
        # Each latent component (factors, errors, exogenous states) contributes its own transition block,
        # and the full transition matrix is assembled with block_diag.
        #   T = block_diag(A, B, C)
        #
        # - Factors (block A):
        #   If factor_order > 0, the factor AR coefficients are organized into a
        #   VAR(p) companion matrix of size (k_factors * factor_order, k_factors * factor_order).
        #   This block shifts lagged factor states and applies AR coefficients.
        #   If factor_order = 0, a zero matrix is used instead.
        #
        # - Errors (block B):
        #   If error_order > 0:
        #     * error_var=True → build a full VAR(p) companion matrix (cross-series correlations allowed).
        #     * error_var=False → build independent AR(p) companion matrices (no cross-series effects).
        #
        # - Exogenous states (block C):
        #   If exog_flag=True, exogenous states are either constant or follow a random walk, modeled with an identity
        #       transition block of size (k_exog_states, k_exog_states).
        #
        # The final transition matrix is block-diagonal, combining all active components:
        #   Transition = block_diag(Factors, Errors, Exogenous)

        # auxiliary functions to build transition matrix block
        def build_var_block_matrix(ar_coeffs, k_series, p):
            """
            Build the VAR(p) companion matrix for the factors.

            ar_coeffs: PyTensor matrix of shape (k_series, p * k_series)
                    [A1 | A2 | ... | Ap] horizontally concatenated.
            k_series: number of series
            p: lag order
            """
            size = k_series * p
            block = pt.zeros((size, size), dtype=floatX)

            # First block row: the AR coefficient matrices for each lag
            block = block[0:k_series, 0 : k_series * p].set(ar_coeffs)

            # Sub-diagonal identity blocks (shift structure)
            if p > 1:
                # Create the identity pattern for all sub-diagonal blocks
                identity_pattern = pt.eye(k_series * (p - 1), dtype=floatX)
                block = block[k_series:, : k_series * (p - 1)].set(identity_pattern)

            return block

        def build_independent_var_block_matrix(ar_coeffs, k_series, p):
            """
            Build a VAR(p)-style companion matrix for independent AR(p) processes
            with interleaved state ordering:
            (x1(t), x2(t), ..., x1(t-1), x2(t-1), ...).

            ar_coeffs: PyTensor matrix of shape (k_series, p)
            k_series: number of independent series
            p: lag order
            """
            size = k_series * p
            block = pt.zeros((size, size), dtype=floatX)

            # First block row: AR coefficients per series (block diagonal)
            for j in range(k_series):
                for lag in range(p):
                    col_idx = lag * k_series + j
                    block = pt.set_subtensor(block[j, col_idx], ar_coeffs[j, lag])

            # Sub-diagonal identity blocks (shift)
            if p > 1:
                identity_pattern = pt.eye(k_series * (p - 1), dtype=floatX)
                block = pt.set_subtensor(block[k_series:, : k_series * (p - 1)], identity_pattern)
            return block

        transition_blocks = []
        # Block A: Factors
        if self.factor_order > 0:
            factor_ar = self.make_and_register_variable(
                "factor_ar",
                shape=(self.k_factors, self.factor_order * self.k_factors),
                dtype=floatX,
            )
            transition_blocks.append(
                build_var_block_matrix(factor_ar, self.k_factors, self.factor_order)
            )
        else:
            transition_blocks.append(pt.zeros((self.k_factors, self.k_factors), dtype=floatX))
        # Block B: Errors
        if self.error_order > 0 and self.error_var:
            error_ar = self.make_and_register_variable(
                "error_ar", shape=(self.k_endog, self.error_order * self.k_endog), dtype=floatX
            )
            transition_blocks.append(
                build_var_block_matrix(error_ar, self.k_endog, self.error_order)
            )
        elif self.error_order > 0 and not self.error_var:
            error_ar = self.make_and_register_variable(
                "error_ar", shape=(self.k_endog, self.error_order), dtype=floatX
            )
            transition_blocks.append(
                build_independent_var_block_matrix(error_ar, self.k_endog, self.error_order)
            )
        # Block C: Exogenous states
        if self.exog_flag:
            transition_blocks.append(pt.eye(self.k_exog_states, dtype=floatX))

        self.ssm["transition", :, :] = pt.linalg.block_diag(*transition_blocks)

        # Selection matrix (R)
        for i in range(self.k_factors):
            self.ssm["selection", i, i] = 1.0

        if self.error_order > 0:
            for i in range(self.k_endog):
                row = max(self.factor_order, 1) * self.k_factors + i
                col = self.k_factors + i
                self.ssm["selection", row, col] = 1.0

        if self.exog_flag and self.exog_innovations:
            row_start = self.k_states - self.k_exog_states
            row_end = self.k_states

            if self.error_order > 0:
                col_start = self.k_factors + self.k_endog
                col_end = self.k_factors + self.k_endog + self.k_exog_states
            else:
                col_start = self.k_factors
                col_end = self.k_factors + self.k_exog_states

            self.ssm["selection", row_start:row_end, col_start:col_end] = pt.eye(
                self.k_exog_states, dtype=floatX
            )

        factor_cov = pt.eye(self.k_factors, dtype=floatX)

        # Handle error_sigma and error_cov depending on error_cov_type
        if self.error_cov_type == "scalar":
            error_sigma = self.make_and_register_variable("error_sigma", shape=(), dtype=floatX)
            error_cov = pt.eye(self.k_endog) * error_sigma
        elif self.error_cov_type == "diagonal":
            error_sigma = self.make_and_register_variable(
                "error_sigma", shape=(self.k_endog,), dtype=floatX
            )
            error_cov = pt.diag(error_sigma)
        elif self.error_cov_type == "unstructured":
            error_cov = self.make_and_register_variable(
                "error_cov", shape=(self.k_endog, self.k_endog), dtype=floatX
            )

        # State covariance matrix (Q)
        if self.error_order > 0:
            if self.exog_flag and self.exog_innovations:
                # Include AR noise in state vector
                beta_sigma = self.make_and_register_variable(
                    "beta_sigma", shape=(self.k_exog_states,), dtype=floatX
                )
                exog_cov = pt.diag(beta_sigma)
                self.ssm["state_cov", :, :] = pt.linalg.block_diag(factor_cov, error_cov, exog_cov)
            elif self.exog_flag and not self.exog_innovations:
                exog_cov = pt.zeros((self.k_exog_states, self.k_exog_states), dtype=floatX)
                self.ssm["state_cov", :, :] = pt.linalg.block_diag(factor_cov, error_cov, exog_cov)
            elif not self.exog_flag:
                self.ssm["state_cov", :, :] = pt.linalg.block_diag(factor_cov, error_cov)
        else:
            if self.exog_flag and self.exog_innovations:
                beta_sigma = self.make_and_register_variable(
                    "beta_sigma", shape=(self.k_exog_states,), dtype=floatX
                )
                exog_cov = pt.diag(beta_sigma)
                self.ssm["state_cov", :, :] = pt.linalg.block_diag(factor_cov, exog_cov)
            elif self.exog_flag and not self.exog_innovations:
                exog_cov = pt.zeros((self.k_exog_states, self.k_exog_states), dtype=floatX)
                self.ssm["state_cov", :, :] = pt.linalg.block_diag(factor_cov, exog_cov)
            elif not self.exog_flag:
                # Only latent factor in the state
                self.ssm["state_cov", :, :] = factor_cov

        # Observation covariance matrix (H)
        if self.error_order > 0:
            if self.measurement_error:
                sigma_obs = self.make_and_register_variable(
                    "sigma_obs", shape=(self.k_endog,), dtype=floatX
                )
                self.ssm["obs_cov", :, :] = pt.diag(sigma_obs)
            # else: obs_cov remains zero (no measurement noise and idiosyncratic noise captured in state)
        else:
            if self.measurement_error:
                # TODO: check this decision
                # in this case error_order = 0, so there is no error term in the state, so the sigma error could not be added there
                # Idiosyncratic + measurement error
                sigma_obs = self.make_and_register_variable(
                    "sigma_obs", shape=(self.k_endog,), dtype=floatX
                )
                total_obs_var = error_sigma**2 + sigma_obs**2
                self.ssm["obs_cov", :, :] = pt.diag(pt.sqrt(total_obs_var))
            else:
                self.ssm["obs_cov", :, :] = pt.diag(error_sigma)
