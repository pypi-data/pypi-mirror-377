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


class RoutingAgent:
    """The Routing agent.

    This is the agent responsible for choosing which remote seller agents to send
    tasks to and coordinate their work.
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

        # Populate self.agents using the logic from original __init__
        agent_info = []
        for agent_detail_dict in self.list_remote_agents():
            agent_info.append(json.dumps(agent_detail_dict))
        self.agents = '\n'.join(agent_info)

    @classmethod
    async def create(
        cls,
        remote_agent_addresses: list[str],
        task_callback: TaskUpdateCallback | None = None,
    ) -> 'RoutingAgent':
        """Create and asynchronously initialize an instance of the RoutingAgent."""
        instance = cls(task_callback)
        await instance._async_init_components(remote_agent_addresses)
        return instance

    def create_agent(self):
        """Create an instance of the RoutingAgent."""
        # Define LLM
        llm = ChatOpenAI(model="o3")

        # Generate the prompt
        prompt = self.root_instruction()

        # Create the agent
        return create_react_agent(
            llm,
            tools=[
                self.send_message,
            ],
            prompt=prompt,
        )


    def root_instruction(self) -> str:
        """Generate the root instruction for the RoutingAgent."""
        return f"""
        **Role:** You are an expert Routing Delegator. Your primary function is to accurately delegate user inquiries to the appropriate specialized remote agents.

        **Core Directives:**

        * **Task Delegation:** Utilize the `send_message` function to assign actionable tasks to remote agents.
        * **Contextual Awareness for Remote Agents:** If a remote agent repeatedly requests user confirmation, assume it lacks access to the full conversation history. In such cases, enrich the task description with all necessary contextual information relevant to that specific agent.
        * **Autonomous Agent Engagement:** Never seek user permission before engaging with remote agents. If multiple agents are required to fulfill a request, connect with them directly without requesting user preference or confirmation.
        * **Transparent Communication:** Always present the complete and detailed response from the remote agent to the user.
        * **User Confirmation Relay:** If a remote agent asks for confirmation, and the user has not already provided it, relay this confirmation request to the user.
        * **Focused Information Sharing:** Provide remote agents with only relevant contextual information. Avoid extraneous details.
        * **No Redundant Confirmations:** Do not ask remote agents for confirmation of information or actions.
        * **Tool Reliance:** Strictly rely on available tools to address user requests. Do not generate responses based on assumptions or on your own knowledge. If information is insufficient, request clarification from the user.
        * **Agents Usage:** When an agent needs to be used, use the `send_message` tool to send the task to the agent.
        * **Tools Usage:** When a tool needs to be used, use the corresponding tool to get the result DO NOT USE the `send_message` sice it is used for agents.

        **Agent Roster:**

        * Available Agents: `{self.agents}`
        """

    def list_remote_agents(self):
        """List the available remote agents you can use to delegate the task."""
        if not self.cards:
            return []

        remote_agent_info = []
        for card in self.cards.values():
            print(f'Found agent card: {card.model_dump(exclude_none=True)}')
            remote_agent_info.append(
                {'name': card.name, 'description': card.description}
            )
        return remote_agent_info

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
        
        return send_response.root.result

