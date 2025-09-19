from dataclasses import dataclass

from sema4ai.data import DataSource

from sema4ai_docint.agent_server_client.transport.base import TransportBase

from ..agent_server_client import AgentServerClient
from ._extraction import _ExtractionService


@dataclass
class _DIContext:
    """Shared context containing all external dependencies for document intelligence services.

    This context provides centralized access to database connections and external clients,
    avoiding complex dependency injection while maintaining type safety.
    """

    # Core database connection (always required)
    datasource: DataSource

    # Optional external clients
    extraction_service: _ExtractionService | None = None

    # Optional agent server transport
    agent_server_transport: TransportBase | None = None

    # Lazy-loaded agent client to avoid initialization requests
    _agent_client: AgentServerClient | None = None

    # PGVector datasource (required for the knowledge base service creation)
    pg_vector: DataSource | None = None

    @property
    def agent_client(self) -> AgentServerClient:
        """Lazy-loaded agent client that initializes only when first accessed."""
        if self._agent_client is None:
            self._agent_client = AgentServerClient(transport=self.agent_server_transport)
        return self._agent_client

    @classmethod
    def create(
        cls,
        datasource: DataSource,
        sema4_api_key: str | None = None,
        disable_ssl_verification: bool = False,
        *,
        agent_server_transport: TransportBase | None = None,
        pg_vector: DataSource | None = None,
    ) -> "_DIContext":
        extraction_service = None
        if sema4_api_key:
            extraction_service = _ExtractionService(
                sema4_api_key, disable_ssl_verification=disable_ssl_verification
            )

        return cls(
            datasource=datasource,
            extraction_service=extraction_service,
            agent_server_transport=agent_server_transport,
            pg_vector=pg_vector,
        )
