import sys
if sys.version_info < (3, 11):
    raise RuntimeError(
        f"PLANQK SDK requires Python 3.11 or higher; "
        f"you are running {sys.version_info.major}.{sys.version_info.minor}."
    )


"""
PLANQK Quantum SDK module providing unified access to quantum providers.
"""

from ._version import __version__
from .braket.braket_provider import PlanqkBraketProvider
from .qiskit.provider import PlanqkQuantumProvider

# Import DTOs and client classes
from .client.backend_dtos import BackendDto, BackendStateInfosDto
from .client.job_dtos import JobDto
from .client.model_enums import Provider, JobInputFormat, PlanqkSdkProvider
from .client.client import _PlanqkClient

# Also import submodules to make them accessible
from . import braket
from . import qiskit
from . import client

__all__ = ['PlanqkQuantumProvider', 'PlanqkBraketProvider', '__version__', 'braket', 'qiskit', 'client',
           'BackendDto', 'BackendStateInfosDto', 'JobDto', 'Provider', 'JobInputFormat',
           'PlanqkSdkProvider', '_PlanqkClient']

