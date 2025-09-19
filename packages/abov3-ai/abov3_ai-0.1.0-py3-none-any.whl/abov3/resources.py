"""Resource classes for ABOV3 AI SDK"""

from typing import Optional, List, Dict, Any, AsyncIterator
from .types import Session, Message, File, Agent, Project, StreamChunk


class BaseResource:
    """Base class for API resources."""

    def __init__(self, client):
        self._client = client


class Sessions(BaseResource):
    """Session management resource."""

    async def create(
        self,
        model: str,
        system_prompt: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Session:
        """Create a new session."""
        response = await self._client.request(
            "POST",
            "/sessions",
            json={
                "model": model,
                "system_prompt": system_prompt,
                "metadata": metadata or {},
            },
        )
        return Session(**response.json())

    async def get(self, session_id: str) -> Session:
        """Get a session by ID."""
        response = await self._client.request("GET", f"/sessions/{session_id}")
        return Session(**response.json())

    async def list(
        self,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Session]:
        """List sessions."""
        response = await self._client.request(
            "GET",
            "/sessions",
            params={"limit": limit, "offset": offset},
        )
        return [Session(**item) for item in response.json()["sessions"]]

    async def delete(self, session_id: str) -> None:
        """Delete a session."""
        await self._client.request("DELETE", f"/sessions/{session_id}")


class Messages(BaseResource):
    """Message management resource."""

    async def create(
        self,
        session_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Message:
        """Send a message and get response."""
        response = await self._client.request(
            "POST",
            f"/sessions/{session_id}/messages",
            json={
                "content": content,
                "metadata": metadata or {},
            },
        )
        return Message(**response.json())

    async def stream(
        self,
        session_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AsyncIterator[StreamChunk]:
        """Stream a message response."""
        # This would be implemented with SSE or WebSocket support
        # Simplified for now
        response = await self.create(session_id, content, metadata)
        yield StreamChunk(type="text", content=response.content)
        yield StreamChunk(type="done")

    async def list(
        self,
        session_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Message]:
        """List messages in a session."""
        response = await self._client.request(
            "GET",
            f"/sessions/{session_id}/messages",
            params={"limit": limit, "offset": offset},
        )
        return [Message(**item) for item in response.json()["messages"]]


class Files(BaseResource):
    """File management resource."""

    async def upload(
        self,
        file_path: str,
        purpose: str = "general",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> File:
        """Upload a file."""
        with open(file_path, "rb") as f:
            response = await self._client.request(
                "POST",
                "/files",
                files={"file": f},
                data={"purpose": purpose, "metadata": metadata or {}},
            )
        return File(**response.json())

    async def get(self, file_id: str) -> File:
        """Get file metadata."""
        response = await self._client.request("GET", f"/files/{file_id}")
        return File(**response.json())

    async def list(
        self,
        limit: int = 20,
        offset: int = 0,
    ) -> List[File]:
        """List files."""
        response = await self._client.request(
            "GET",
            "/files",
            params={"limit": limit, "offset": offset},
        )
        return [File(**item) for item in response.json()["files"]]

    async def delete(self, file_id: str) -> None:
        """Delete a file."""
        await self._client.request("DELETE", f"/files/{file_id}")


class Agents(BaseResource):
    """Agent management resource."""

    async def create(
        self,
        name: str,
        model: str,
        system_prompt: str,
        description: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
    ) -> Agent:
        """Create a new agent."""
        response = await self._client.request(
            "POST",
            "/agents",
            json={
                "name": name,
                "model": model,
                "system_prompt": system_prompt,
                "description": description,
                "capabilities": capabilities or [],
            },
        )
        return Agent(**response.json())

    async def get(self, agent_id: str) -> Agent:
        """Get an agent by ID."""
        response = await self._client.request("GET", f"/agents/{agent_id}")
        return Agent(**response.json())

    async def list(
        self,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Agent]:
        """List agents."""
        response = await self._client.request(
            "GET",
            "/agents",
            params={"limit": limit, "offset": offset},
        )
        return [Agent(**item) for item in response.json()["agents"]]

    async def delete(self, agent_id: str) -> None:
        """Delete an agent."""
        await self._client.request("DELETE", f"/agents/{agent_id}")


class Projects(BaseResource):
    """Project management resource."""

    async def create(
        self,
        name: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Project:
        """Create a new project."""
        response = await self._client.request(
            "POST",
            "/projects",
            json={
                "name": name,
                "description": description,
                "metadata": metadata or {},
            },
        )
        return Project(**response.json())

    async def get(self, project_id: str) -> Project:
        """Get a project by ID."""
        response = await self._client.request("GET", f"/projects/{project_id}")
        return Project(**response.json())

    async def list(
        self,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Project]:
        """List projects."""
        response = await self._client.request(
            "GET",
            "/projects",
            params={"limit": limit, "offset": offset},
        )
        return [Project(**item) for item in response.json()["projects"]]

    async def delete(self, project_id: str) -> None:
        """Delete a project."""
        await self._client.request("DELETE", f"/projects/{project_id}")