"""Bodhi REST API client."""
import httpx
from typing import Optional, Dict, Any, List


class BodhiClient:
    """Client for Fedora Bodhi REST API."""

    def __init__(self, base_url: str = "https://bodhi.fedoraproject.org"):
        self.base_url = base_url.rstrip("/")
        self.api_url = f"{self.base_url}"

    async def get_updates(
        self,
        user: Optional[str] = None,
        packages: Optional[str] = None,
        status: Optional[str] = None,
        releases: Optional[str] = None,
        rows_per_page: int = 20,
        page: int = 1,
    ) -> Dict[str, Any]:
        """
        Query updates from Bodhi.

        NOTE: Bodhi API does not support combining 'user' with 'packages' filters.
        If both are provided, 'user' will be ignored and only 'packages' will be used.

        Args:
            user: Filter by username (ignored if packages is also specified)
            packages: Filter by package name
            status: Filter by status (pending, testing, stable, etc.)
            releases: Filter by release (F40, F41, etc.)
            rows_per_page: Number of results per page
            page: Page number

        Returns:
            JSON response from Bodhi API
        """
        params = {
            "rows_per_page": rows_per_page,
            "page": page,
        }

        # Bodhi API limitation: cannot combine user + packages filters
        # Prioritize packages filter over user filter
        if packages:
            params["packages"] = packages
            # Do NOT add user parameter when packages is specified
        elif user:
            params["user"] = user

        if status:
            params["status"] = status
        if releases:
            params["releases"] = releases

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/updates/",
                params=params,
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()

    async def get_update(self, update_id: str) -> Dict[str, Any]:
        """
        Get details for a specific update.

        Args:
            update_id: Update ID (e.g., FEDORA-2024-abc123)

        Returns:
            JSON response from Bodhi API
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/updates/{update_id}",
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()

    async def get_releases(self) -> Dict[str, Any]:
        """
        Get list of Fedora releases.

        Returns:
            JSON response from Bodhi API
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/releases/",
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()

    async def get_comments(self, update_id: str) -> Dict[str, Any]:
        """
        Get comments for a specific update.

        Args:
            update_id: Update ID (e.g., FEDORA-2024-abc123)

        Returns:
            JSON response from Bodhi API
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/comments/",
                params={"updates": update_id},
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()
