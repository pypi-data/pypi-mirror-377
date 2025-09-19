import abc
from typing import Any

from bayesline.api._src._utils import docstrings_from_sync


class UserPermissionsApi(abc.ABC):
    """Abstract base class for synchronous user permissions API operations."""

    @abc.abstractmethod
    def get_permissions_map(self) -> dict[str, Any]:
        """Retrieve the complete permissions map for the user.

        Returns
        -------
        dict[str, Any]
            A dictionary mapping permission keys to their boolean values.
        """
        ...

    @abc.abstractmethod
    def get_perm(self, key: str, default: bool = True) -> Any:
        """Get a single permission value for the specified key.

        Parameters
        ----------
        key : str
            The permission key to retrieve.
        default : bool, default=True
            Default value to return if the permission is not found.

        Returns
        -------
        Any
            The permission value or the default value if not found.
        """
        ...

    @abc.abstractmethod
    def get_perms(self, keys: list[str], default: bool = True) -> dict[str, Any]:
        """Get multiple permission values for the specified keys.

        Parameters
        ----------
        keys : list[str]
            List of permission keys to retrieve.
        default : bool, default=True
            Default value to return for permissions that are not found.

        Returns
        -------
        dict[str, Any]
            A dictionary mapping permission keys to their values.
        """
        ...


@docstrings_from_sync
class AsyncUserPermissionsApi(abc.ABC):

    @abc.abstractmethod
    async def get_permissions_map(self) -> dict[str, Any]: ...  # noqa: D102

    @abc.abstractmethod
    async def get_perm(self, key: str, default: bool = True) -> Any: ...  # noqa: D102

    @abc.abstractmethod
    async def get_perms(  # noqa: D102
        self, keys: list[str], default: bool = True
    ) -> dict[str, Any]: ...
