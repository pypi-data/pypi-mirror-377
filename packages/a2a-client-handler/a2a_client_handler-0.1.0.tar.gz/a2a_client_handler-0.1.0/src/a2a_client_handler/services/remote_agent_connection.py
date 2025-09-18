from collections.abc import Callable

import httpx

from a2a.client import A2AClient
from a2a.types import (
    AgentCard,
    SendMessageRequest,
    SendMessageResponse,
    Task,
    TaskArtifactUpdateEvent,
    TaskStatusUpdateEvent,
    SendStreamingMessageRequest
)

TaskCallbackArg = Task | TaskStatusUpdateEvent | TaskArtifactUpdateEvent
TaskUpdateCallback = Callable[[TaskCallbackArg, AgentCard], Task]


class RemoteAgentConnections:
    """A class to hold the connections to the remote agents."""

    def __init__(self, agent_card: AgentCard, agent_url: str):
        self._httpx_client = httpx.AsyncClient(timeout=60)
        self.agent_client = A2AClient(
            self._httpx_client, 
            agent_card, 
            url=agent_url
        )
        self.card = agent_card

    def get_agent(self) -> AgentCard:
        return self.card

    async def send_message(self, message_request: SendMessageRequest) -> SendMessageResponse:
        return await self.agent_client.send_message(message_request)
    
    async def send_message_streaming(self, message_request: SendStreamingMessageRequest):
        stream_response = self.agent_client.send_message_streaming(message_request)
        
        chunks = []
        async for chunk in stream_response:
            chunks.append(chunk)
            print('Streaming Chunk: ', chunk.model_dump(mode='json', exclude_none=True))

        # Get the last 'working' status chunk before 'completed' status chunk
        text = chunks[-2].root.result

        return text
