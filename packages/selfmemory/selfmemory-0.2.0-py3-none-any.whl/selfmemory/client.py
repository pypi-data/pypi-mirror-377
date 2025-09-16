"""
SelfMemory Client - Managed solution for SelfMemory.

This module provides the client interface for the managed SelfMemory service,
similar to how  provides MemoryClient for their hosted solution.
"""

import logging
import os
from typing import Any

import httpx

from .common.constants import APIConstants

logger = logging.getLogger(__name__)


class SelfMemoryClient:
    """Client for interacting with the managed SelfMemory API.

    This class provides methods to create, retrieve, search, and delete
    memories using the hosted SelfMemory service.

    Attributes:
        api_key (str): The API key for authenticating with the SelfMemory API.
        host (str): The base URL for the SelfMemory API.
        client (httpx.Client): The HTTP client used for making API requests.
    """

    def __init__(
        self,
        api_key: str | None = None,
        host: str | None = None,
        client: httpx.Client | None = None,
    ):
        """Initialize the SelfMemory client.

        Args:
            api_key: The API key for authenticating with the SelfMemory API. If not
                     provided, it will attempt to use the INMEM_API_KEY
                     environment variable.
            host: The base URL for the SelfMemory API. If not provided, will
                  auto-discover the correct host by trying multiple endpoints.
            client: A custom httpx.Client instance. If provided, it will be
                    used instead of creating a new one.

        Raises:
            ValueError: If no API key is provided or found in the environment.
        """
        self.api_key = api_key or os.getenv("INMEM_API_KEY")

        if not self.api_key:
            raise ValueError(
                "SelfMemory API Key not provided. Please set INMEM_API_KEY environment variable or provide api_key parameter."
            )

        # Auto-discover host if not provided
        if host:
            self.host = host
        else:
            self.host = self._discover_host()

        if client is not None:
            self.client = client
            # Ensure the client has the correct base_url and headers
            self.client.base_url = httpx.URL(self.host)
            self.client.headers.update(
                {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
            )
        else:
            self.client = httpx.Client(
                base_url=self.host,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=APIConstants.DEFAULT_TIMEOUT,
            )

        # Validate API key on the discovered/provided host
        self.user_info = self._validate_api_key()
        logger.info(f"SelfMemory client initialized with host: {self.host}")

    def _discover_host(self) -> str:
        """Auto-discover the correct host for the API key by trying multiple endpoints."""
        # Priority order for host discovery
        candidate_hosts = [
            # Environment variable override
            os.getenv("SELFMEMORY_API_HOST"),
            # Production host
            APIConstants.DEFAULT_API_HOST,
            # Common local development hosts
            "http://localhost:8081",  # Default server port
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:3002",
            "http://127.0.0.1:8080",
            "http://127.0.0.1:3000",
        ]

        # Filter out None values
        candidate_hosts = [host for host in candidate_hosts if host]

        logger.info("Auto-discovering host for API key...")

        for host in candidate_hosts:
            try:
                # Create a temporary client to test this host
                temp_client = httpx.Client(
                    base_url=host,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    timeout=5.0,  # Short timeout for discovery
                )

                # Try to ping this host
                response = temp_client.get("/api/v1/ping")
                response.raise_for_status()
                data = response.json()

                # If we get a valid response, this is our host
                if data.get("status") == "ok":
                    temp_client.close()
                    logger.info(f"✅ Discovered host: {host}")
                    return host

            except Exception as e:
                logger.debug(f"Host {host} failed: {e}")
                continue
            finally:
                try:
                    temp_client.close()
                except:
                    pass

        # If no host worked, fall back to default
        logger.warning("Could not auto-discover host, using default")
        return APIConstants.DEFAULT_API_HOST

    def _validate_api_key(self) -> dict[str, Any]:
        """Validate the API key by making a test request (following selfmemory's pattern)."""
        try:
            response = self.client.get("/api/v1/ping")
            response.raise_for_status()
            data = response.json()

            # The ping endpoint returns user info on success
            if data.get("status") == "ok":
                return {
                    "user_id": data.get("user_id"),
                    "key_id": data.get("key_id"),
                    "permissions": data.get("permissions", []),
                    "name": data.get("name"),
                }
            raise ValueError("API key validation failed: Invalid response")

        except httpx.HTTPStatusError as e:
            try:
                error_data = e.response.json()
                error_message = error_data.get("detail", str(e))
            except Exception:
                error_message = str(e)
            raise ValueError(f"API key validation failed: {error_message}") from None
        except Exception as e:
            raise ValueError(f"Failed to connect to SelfMemory API: {str(e)}") from e

    def add(
        self,
        memory_content: str,
        tags: str | None = None,
        people_mentioned: str | None = None,
        topic_category: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Add a new memory to the managed service.

        Args:
            memory_content: The memory text to store
            tags: Optional comma-separated tags
            people_mentioned: Optional comma-separated people names
            topic_category: Optional topic category
            metadata: Optional additional metadata

        Returns:
            Dict: Result information including memory_id and status

        Examples:
            >>> selfmemory = SelfMemory()
            >>> selfmemory.add("Meeting notes from project discussion",
            ...           tags="work,meeting",
            ...           people_mentioned="Sarah,Mike")
        """
        try:
            payload = {
                "memory_content": memory_content,
                "tags": tags or "",
                "people_mentioned": people_mentioned or "",
                "topic_category": topic_category or "",
                "metadata": metadata or {},
            }

            response = self.client.post("/api/memories", json=payload)
            response.raise_for_status()

            result = response.json()
            logger.info(f"Memory added: {memory_content[:50]}...")
            return result

        except httpx.HTTPStatusError as e:
            try:
                error_data = e.response.json()
                error_message = error_data.get("detail", str(e))
            except Exception:
                error_message = str(e)
            logger.error(f"Failed to add memory: {error_message}")
            return {"success": False, "error": "An internal error occurred while adding a new memory."}
        except Exception as e:
            logger.error(f"Failed to add memory: {e}")
            return {"success": False, "error": "An internal error occurred while adding a new memory."}

    def search(
        self,
        query: str,
        limit: int = 10,
        tags: list[str] | None = None,
        people_mentioned: list[str] | None = None,
        topic_category: str | None = None,
        temporal_filter: str | None = None,
        threshold: float | None = None,
    ) -> dict[str, list[dict[str, Any]]]:
        """Search memories with various filters.

        Args:
            query: Search query string
            limit: Maximum number of results
            tags: Optional list of tags to filter by
            people_mentioned: Optional list of people to filter by
            topic_category: Optional topic category filter
            temporal_filter: Optional temporal filter (e.g., "today", "this_week")
            threshold: Optional minimum similarity score

        Returns:
            Dict: Search results with "results" key containing list of memories

        Examples:
            >>> selfmemory = SelfMemory()
            >>> results = selfmemory.search("pizza")
            >>> results = selfmemory.search("meetings", tags=["work"], limit=5)
        """
        try:
            payload = {
                "query": query,
                "limit": limit,
                "tags": ",".join(tags) if tags else "",
                "people_mentioned": ",".join(people_mentioned)
                if people_mentioned
                else "",
                "topic_category": topic_category or "",
                "temporal_filter": temporal_filter or "",
                "threshold": threshold or 0.0,
            }

            response = self.client.post("/api/memories/search", json=payload)
            response.raise_for_status()

            result = response.json()
            logger.info(f"Search completed: {len(result.get('results', []))} results")
            return result

        except httpx.HTTPStatusError as e:
            try:
                error_data = e.response.json()
                error_message = error_data.get("detail", str(e))
            except Exception:
                error_message = str(e)
            logger.error(f"Search failed: {error_message}")
            return {"results": [], "error": error_message}
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {"results": [], "error": str(e)}

    def get_all(
        self, limit: int = 100, offset: int = 0
    ) -> dict[str, list[dict[str, Any]]]:
        """Get all memories.

        Args:
            limit: Maximum number of memories to return
            offset: Number of memories to skip

        Returns:
            Dict: All memories with "results" key

        Examples:
            >>> selfmemory = SelfMemory()
            >>> all_memories = selfmemory.get_all()
            >>> recent_memories = selfmemory.get_all(limit=10)
        """
        try:
            params = {
                "limit": limit,
                "offset": offset,
            }

            response = self.client.get("/api/memories", params=params)
            response.raise_for_status()

            result = response.json()
            logger.info(f"Retrieved {len(result.get('results', []))} memories")
            return result

        except httpx.HTTPStatusError as e:
            try:
                error_data = e.response.json()
                error_message = error_data.get("detail", str(e))
            except Exception:
                error_message = str(e)
            logger.error(f"Failed to get memories: {error_message}")
            return {"results": [], "error": error_message}
        except Exception as e:
            logger.error(f"Failed to get memories: {e}")
            return {"results": [], "error": str(e)}

    def delete(self, memory_id: str) -> dict[str, Any]:
        """Delete a specific memory.

        Args:
            memory_id: Memory identifier to delete

        Returns:
            Dict: Deletion result
        """
        try:
            response = self.client.delete(f"/api/memories/{memory_id}")
            response.raise_for_status()

            result = response.json()
            logger.info(f"Memory {memory_id} deleted")
            return result

        except httpx.HTTPStatusError as e:
            try:
                error_data = e.response.json()
                error_message = error_data.get("detail", str(e))
            except Exception:
                error_message = str(e)
            logger.error(f"Error deleting memory {memory_id}: {error_message}")
            return {"success": False, "error": error_message}
        except Exception as e:
            logger.error(f"Error deleting memory {memory_id}: {e}")
            return {"success": False, "error": str(e)}

    def delete_all(self) -> dict[str, Any]:
        """Delete all memories.

        Returns:
            Dict: Deletion result with count of deleted memories
        """
        try:
            response = self.client.delete("/api/memories")
            response.raise_for_status()

            result = response.json()
            logger.info("All memories deleted")
            return result

        except httpx.HTTPStatusError as e:
            try:
                error_data = e.response.json()
                error_message = error_data.get("detail", str(e))
            except Exception:
                error_message = str(e)
            logger.error(f"Failed to delete all memories: {error_message}")
            return {"success": False, "error": error_message}
        except Exception as e:
            logger.error(f"Failed to delete all memories: {e}")
            return {"success": False, "error": str(e)}

    def temporal_search(
        self,
        temporal_query: str,
        semantic_query: str | None = None,
        limit: int = 10,
    ) -> dict[str, list[dict[str, Any]]]:
        """Search memories using temporal queries.

        Args:
            temporal_query: Temporal query (e.g., "yesterday", "this_week")
            semantic_query: Optional semantic search query
            limit: Maximum number of results

        Returns:
            Dict: Search results
        """
        try:
            payload = {
                "temporal_query": temporal_query,
                "semantic_query": semantic_query,
                "limit": limit,
            }

            response = self.client.post("/v1/memories/temporal-search/", json=payload)
            response.raise_for_status()

            result = response.json()
            return result

        except httpx.HTTPStatusError as e:
            try:
                error_data = e.response.json()
                error_message = error_data.get("detail", str(e))
            except Exception:
                error_message = str(e)
            logger.error(f"Temporal search failed: {error_message}")
            return {"results": [], "error": error_message}
        except Exception as e:
            logger.error(f"Temporal search failed: {e}")
            return {"results": [], "error": str(e)}

    def search_by_tags(
        self,
        tags: str | list[str],
        semantic_query: str | None = None,
        match_all: bool = False,
        limit: int = 10,
    ) -> dict[str, list[dict[str, Any]]]:
        """Search memories by tags.

        Args:
            tags: Tags to search for (string or list)
            semantic_query: Optional semantic search query
            match_all: Whether all tags must match (AND) vs any tag (OR)
            limit: Maximum number of results

        Returns:
            Dict: Search results
        """
        try:
            if isinstance(tags, str):
                tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
            else:
                tag_list = tags

            payload = {
                "tags": tag_list,
                "semantic_query": semantic_query,
                "match_all": match_all,
                "limit": limit,
            }

            response = self.client.post("/v1/memories/tag-search/", json=payload)
            response.raise_for_status()

            result = response.json()
            return result

        except httpx.HTTPStatusError as e:
            try:
                error_data = e.response.json()
                error_message = error_data.get("detail", str(e))
            except Exception:
                error_message = str(e)
            logger.error(f"Tag search failed: {error_message}")
            return {"results": [], "error": error_message}
        except Exception as e:
            logger.error(f"Tag search failed: {e}")
            return {"results": [], "error": str(e)}

    def search_by_people(
        self,
        people: str | list[str],
        semantic_query: str | None = None,
        limit: int = 10,
    ) -> dict[str, list[dict[str, Any]]]:
        """Search memories by people mentioned.

        Args:
            people: People to search for (string or list)
            semantic_query: Optional semantic search query
            limit: Maximum number of results

        Returns:
            Dict: Search results
        """
        try:
            if isinstance(people, str):
                people_list = [
                    person.strip() for person in people.split(",") if person.strip()
                ]
            else:
                people_list = people

            payload = {
                "people": people_list,
                "semantic_query": semantic_query,
                "limit": limit,
            }

            response = self.client.post("/v1/memories/people-search/", json=payload)
            response.raise_for_status()

            result = response.json()
            return result

        except httpx.HTTPStatusError as e:
            try:
                error_data = e.response.json()
                error_message = error_data.get("detail", str(e))
            except Exception:
                error_message = str(e)
            logger.error(f"People search failed: {error_message}")
            return {"results": [], "error": error_message}
        except Exception as e:
            logger.error(f"People search failed: {e}")
            return {"results": [], "error": str(e)}

    def get_stats(self) -> dict[str, Any]:
        """Get statistics for memories.

        Returns:
            Dict: Statistics including memory count, usage info, etc.
        """
        try:
            response = self.client.get("/v1/stats")
            response.raise_for_status()

            result = response.json()
            return result

        except httpx.HTTPStatusError as e:
            try:
                error_data = e.response.json()
                error_message = error_data.get("detail", str(e))
            except Exception:
                error_message = str(e)
            logger.error(f"Failed to get stats: {error_message}")
            return {"error": error_message}
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"error": str(e)}

    def health_check(self) -> dict[str, Any]:
        """Perform health check on the managed service.

        Returns:
            Dict: Health check results
        """
        try:
            response = self.client.get("/v1/health")
            response.raise_for_status()

            result = response.json()
            return result

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "service": "managed",
            }

    def close(self) -> None:
        """Close the HTTP client connection.

        Should be called when SelfMemory instance is no longer needed.
        """
        try:
            self.client.close()
            logger.info("SelfMemory client connection closed")
        except Exception as e:
            logger.error(f"Error closing client connection: {e}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.close()

    def __repr__(self) -> str:
        """String representation of SelfMemoryClient instance."""
        return f"SelfMemoryClient(host={self.host})"
