"""Factory for creating authentication strategy instances based on the strategy type."""

from typing import Any, ClassVar, Dict, Optional, Type

import structlog

from rasa.shared.agents.auth.auth_strategy import (
    AgentAuthStrategy,
    APIKeyAuthStrategy,
    BearerTokenAuthStrategy,
    OAuth2AuthStrategy,
)
from rasa.shared.agents.auth.types import AgentAuthType

structlogger = structlog.get_logger()


class AgentAuthFactory:
    """Factory for creating authentication strategy instances based on the
    authentication strategy type.
    """

    _auth_strategies: ClassVar[Dict[AgentAuthType, Type[AgentAuthStrategy]]] = {
        AgentAuthType.API_KEY: APIKeyAuthStrategy,
        AgentAuthType.OAUTH2: OAuth2AuthStrategy,
        AgentAuthType.BEARER_TOKEN: BearerTokenAuthStrategy,
    }

    @classmethod
    def create_client(
        cls, auth_type: AgentAuthType, config: Optional[Dict[str, Any]] = None
    ) -> AgentAuthStrategy:
        """Create an authentication strategy instance based on the strategy type.

        Args:
            auth_type: The type of the authentication strategy.
            config: The configuration dictionary for the authentication.

        Returns:
            An instance of the authentication strategy.
        """
        config = config or {}

        # Get the strategy class for the specified type
        auth_strategy_class = cls._get_auth_strategy_class(auth_type)
        if auth_strategy_class is None:
            raise ValueError(
                f"Unsupported strategy type: {auth_type}. "
                f"Supported types: {cls.get_supported_auth_strategy_types()}"
            )
        # Create instance based on strategy type
        return auth_strategy_class.from_config(config)

    @classmethod
    def get_supported_auth_strategy_types(cls) -> list[AgentAuthType]:
        """Get all supported authentication strategy types."""
        return list(cls._auth_strategies.keys())

    @classmethod
    def _get_auth_strategy_class(
        cls, auth_type: AgentAuthType
    ) -> Type[AgentAuthStrategy]:
        """Get the class that implements the authentication strategy."""
        if not cls.is_auth_strategy_supported(auth_type):
            raise ValueError(
                f"Unsupported authentication strategy type: {auth_type}. "
                f"Supported types: {cls.get_supported_auth_strategy_types()}"
            )
        return cls._auth_strategies[auth_type]

    @classmethod
    def is_auth_strategy_supported(cls, auth_type: AgentAuthType) -> bool:
        """Check if the authentication strategy type is supported."""
        return auth_type in cls._auth_strategies
