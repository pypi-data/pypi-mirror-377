import json
import uuid

import httpx

from a2a.client import A2ACardResolver
from a2a.types import (
    AgentCard,
    MessageSendParams,
    Part,
    SendMessageRequest,
    SendMessageResponse,
    SendMessageSuccessResponse,
    Task,
    SendStreamingMessageRequest
)
from a2a_client_handler.services.remote_agent_connection import (
    RemoteAgentConnections,
    TaskUpdateCallback
)

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent


class RoutingSequential:
    """
    Route the task to the remote agent sequentially.
    """

    def __init__(
        self,
        task_callback: TaskUpdateCallback | None = None,
    ):
        self.task_callback = task_callback
        self.remote_agent_connections: dict[str, RemoteAgentConnections] = {}
        self.cards: dict[str, AgentCard] = {}
        self.agents: str = ''

    async def _async_init_components(
        self, remote_agent_addresses: list[str]
    ) -> None:
        """Asynchronous part of initialization."""
        async with httpx.AsyncClient(timeout=30) as client:
            # Loop over agents addresses
            for address in remote_agent_addresses:
                # Define card resolver
                card_resolver = A2ACardResolver(
                    client, address
                )
                try:
                    # Get remote agent card
                    card = (
                        await card_resolver.get_agent_card()
                    )

                    # Create A2AClient for a remote agent
                    remote_connection = RemoteAgentConnections(
                        agent_card=card, agent_url=address
                    )

                    # Update dictionaries of remote agent connections and cards
                    self.remote_agent_connections[card.name] = remote_connection
                    self.cards[card.name] = card

                except httpx.ConnectError as e:
                    print(
                        f'ERROR: Failed to get agent card from {address}: {e}'
                    )
                except Exception as e:  # Catch other potential errors
                    print(
                        f'ERROR: Failed to initialize connection for {address}: {e}'
                    )

    @classmethod
    async def create(
        cls,
        remote_agent_addresses: list[str],
        task_callback: TaskUpdateCallback | None = None,
    ) -> 'RoutingSequential':
        """Create and asynchronously initialize an instance of the RoutingAgent."""
        instance = cls(task_callback)
        await instance._async_init_components(remote_agent_addresses)
        return instance

    async def send_message(self, agent_name: str, message_type: str, task: str):
        """Sends a task to remote agent.

        This will send a message to the remote agent named agent_name.

        Args:
            agent_name: The name of the agent to send the task to.
            message_type: The type of message to send to the agent (sync or async).
            task: The comprehensive conversation context summary
                and goal to be achieved regarding user inquiry and purchase request.

        Yields:
            A dictionary of JSON data.
        """
        client = self.remote_agent_connections[agent_name]

        message_id = str(uuid.uuid4())
        
        payload = {
            'message': {
                'role': 'user',
                'parts': [
                    {'type': 'text', 'text': task}
                ],
                'messageId': message_id,
            },
        }

        # Send message to remote agent (Sync)
        if message_type == 'sync':
            message_request = SendMessageRequest(
                id=message_id, 
                params=MessageSendParams.model_validate(payload)
            )

            send_response: SendMessageResponse = await client.send_message(
                message_request=message_request
            )

            return send_response.root.result

        # Send message to remote agent (Async)
        elif message_type == 'async':
            streaming_request = SendStreamingMessageRequest(
                id=message_id, params=MessageSendParams(**payload)
            )

            stream_response = await client.send_message_streaming(streaming_request)

            return stream_response
