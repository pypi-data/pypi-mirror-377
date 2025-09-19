import abc

from bayesline.api._src._utils import docstrings_from_sync
from bayesline.api._src.equity.api import AsyncBayeslineEquityApi, BayeslineEquityApi
from bayesline.api._src.permissions import AsyncUserPermissionsApi, UserPermissionsApi
from bayesline.api._src.tasks import AsyncTasksApi, TasksApi


class BayeslineApi(abc.ABC):
    """Abstract base class for Bayesline API operations."""

    @property
    @abc.abstractmethod
    def equity(self) -> BayeslineEquityApi:
        """
        Get the equity API.

        Returns
        -------
        BayeslineEquityApi
            The equity API.
        """
        ...

    @property
    @abc.abstractmethod
    def permissions(self) -> UserPermissionsApi:
        """
        Get the user permissions API.

        Returns
        -------
        UserPermissionsApi
            The user permissions API.
        """
        ...

    @property
    @abc.abstractmethod
    def tasks(self) -> TasksApi:
        """
        Get the tasks API.

        Returns
        -------
        TasksApi
            The tasks API.
        """
        ...


@docstrings_from_sync
class AsyncBayeslineApi(abc.ABC):

    @property
    @abc.abstractmethod
    def equity(self) -> AsyncBayeslineEquityApi: ...  # noqa: D102

    @property
    @abc.abstractmethod
    def permissions(self) -> AsyncUserPermissionsApi: ...  # noqa: D102

    @property
    @abc.abstractmethod
    def tasks(self) -> AsyncTasksApi: ...  # noqa: D102
