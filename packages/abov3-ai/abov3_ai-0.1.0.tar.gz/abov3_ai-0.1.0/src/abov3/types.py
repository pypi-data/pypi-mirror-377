"""Type definitions for ABOV3 AI SDK"""

from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field


class Model(BaseModel):
    """AI model information."""
    id: str
    name: str
    provider: Literal["anthropic", "openai", "google", "custom"]
    capabilities: List[str] = Field(default_factory=list)
    max_tokens: Optional[int] = None
    supports_streaming: bool = True
    supports_functions: bool = False


class Session(BaseModel):
    """Chat session."""
    id: str
    model: str
    system_prompt: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)
    message_count: int = 0
    total_tokens: int = 0


class Message(BaseModel):
    """Chat message."""
    id: str
    session_id: str
    role: Literal["user", "assistant", "system"]
    content: str
    created_at: datetime
    tokens: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class File(BaseModel):
    """Uploaded file."""
    id: str
    filename: str
    size: int
    mime_type: str
    purpose: str
    created_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Agent(BaseModel):
    """AI agent configuration."""
    id: str
    name: str
    description: Optional[str] = None
    model: str
    system_prompt: str
    capabilities: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class Project(BaseModel):
    """Project configuration."""
    id: str
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)


class StreamChunk(BaseModel):
    """Streaming response chunk."""
    type: Literal["text", "error", "done"]
    content: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)