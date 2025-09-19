"""
Backboard API data models
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass
from enum import Enum
import uuid


class DocumentStatus(str, Enum):
    """Document processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"


class MessageRole(str, Enum):
    """Message role types"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class ToolParameterProperties:
    """Tool parameter property definition"""
    type: str
    description: Optional[str] = None
    enum: Optional[List[str]] = None
    properties: Optional[Dict[str, Any]] = None
    items: Optional[Dict[str, Any]] = None


@dataclass
class ToolParameters:
    """Tool parameters definition"""
    type: str = "object"
    properties: Dict[str, ToolParameterProperties] = None
    required: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}


@dataclass
class FunctionDefinition:
    """Function definition for tools"""
    name: str
    description: Optional[str]
    parameters: ToolParameters


@dataclass
class ToolDefinition:
    """Tool definition"""
    type: str = "function"
    function: FunctionDefinition = None


@dataclass
class Assistant:
    """Assistant model"""
    assistant_id: uuid.UUID
    name: str
    description: Optional[str]
    tools: Optional[List[ToolDefinition]]
    created_at: datetime

    @classmethod
    def from_dict(cls, data: dict) -> 'Assistant':
        """Create Assistant from API response dict"""
        tools = None
        if data.get('tools'):
            tools = [
                ToolDefinition(
                    type=tool.get('type', 'function'),
                    function=FunctionDefinition(
                        name=tool['function']['name'],
                        description=tool['function'].get('description'),
                        parameters=ToolParameters(
                            type=tool['function']['parameters'].get('type', 'object'),
                            properties={
                                k: ToolParameterProperties(**v) 
                                for k, v in tool['function']['parameters'].get('properties', {}).items()
                            },
                            required=tool['function']['parameters'].get('required')
                        )
                    )
                )
                for tool in data['tools']
            ]
        
        return cls(
            assistant_id=uuid.UUID(data['assistant_id']),
            name=data['name'],
            description=data.get('description'),
            tools=tools,
            created_at=datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
        )


@dataclass
class AttachmentInfo:
    """Message attachment information"""
    document_id: uuid.UUID
    filename: str
    status: str
    file_size_bytes: int
    summary: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'AttachmentInfo':
        """Create AttachmentInfo from API response dict"""
        return cls(
            document_id=uuid.UUID(data['document_id']),
            filename=data['filename'],
            status=data['status'],
            file_size_bytes=data['file_size_bytes'],
            summary=data.get('summary')
        )


@dataclass
class Message:
    """Message model"""
    message_id: uuid.UUID
    role: MessageRole
    content: Optional[str]
    created_at: datetime
    status: Optional[str] = None
    metadata_: Optional[Dict[str, Any]] = None
    attachments: Optional[List[AttachmentInfo]] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'Message':
        """Create Message from API response dict"""
        attachments = None
        if data.get('attachments'):
            attachments = [AttachmentInfo.from_dict(att) for att in data['attachments']]
        
        return cls(
            message_id=uuid.UUID(data['message_id']),
            role=MessageRole(data['role']),
            content=data.get('content'),
            created_at=datetime.fromisoformat(data['created_at'].replace('Z', '+00:00')),
            status=data.get('status'),
            metadata_=data.get('metadata_'),
            attachments=attachments
        )


@dataclass
class Thread:
    """Thread model"""
    thread_id: uuid.UUID
    created_at: datetime
    messages: List[Message]
    metadata_: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'Thread':
        """Create Thread from API response dict"""
        messages = [Message.from_dict(msg) for msg in data.get('messages', [])]
        
        return cls(
            thread_id=uuid.UUID(data['thread_id']),
            created_at=datetime.fromisoformat(data['created_at'].replace('Z', '+00:00')),
            messages=messages,
            metadata_=data.get('metadata_')
        )


@dataclass
class Document:
    """Document model"""
    document_id: uuid.UUID
    filename: str
    status: DocumentStatus
    created_at: datetime
    status_message: Optional[str] = None
    summary: Optional[str] = None
    updated_at: Optional[datetime] = None
    file_size_bytes: Optional[int] = None
    total_tokens: Optional[int] = None
    chunk_count: Optional[int] = None
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    document_type: Optional[str] = None
    metadata_: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'Document':
        """Create Document from API response dict"""
        updated_at = None
        if data.get('updated_at'):
            updated_at = datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00'))
        
        processing_started_at = None
        if data.get('processing_started_at'):
            processing_started_at = datetime.fromisoformat(data['processing_started_at'].replace('Z', '+00:00'))
            
        processing_completed_at = None
        if data.get('processing_completed_at'):
            processing_completed_at = datetime.fromisoformat(data['processing_completed_at'].replace('Z', '+00:00'))
        
        return cls(
            document_id=uuid.UUID(data['document_id']),
            filename=data['filename'],
            status=DocumentStatus(data['status']),
            created_at=datetime.fromisoformat(data['created_at'].replace('Z', '+00:00')),
            status_message=data.get('status_message'),
            summary=data.get('summary'),
            updated_at=updated_at,
            file_size_bytes=data.get('file_size_bytes'),
            total_tokens=data.get('total_tokens'),
            chunk_count=data.get('chunk_count'),
            processing_started_at=processing_started_at,
            processing_completed_at=processing_completed_at,
            document_type=data.get('document_type'),
            metadata_=data.get('metadata_')
        )


@dataclass
class MessageResponse:
    """Response from adding a message to a thread"""
    message: str
    thread_id: uuid.UUID
    content: Optional[str]
    message_id: uuid.UUID
    role: MessageRole
    status: Optional[str]
    tool_calls: Optional[List[Dict[str, Any]]]
    run_id: Optional[str]
    latest_message: Message
    attachments: Optional[List[AttachmentInfo]]
    timestamp: datetime

    @classmethod
    def from_dict(cls, data: dict) -> 'MessageResponse':
        """Create MessageResponse from API response dict"""
        attachments = None
        if data.get('attachments'):
            attachments = [AttachmentInfo.from_dict(att) for att in data['attachments']]
        
        return cls(
            message=data['message'],
            thread_id=uuid.UUID(data['thread_id']),
            content=data.get('content'),
            message_id=uuid.UUID(data['message_id']),
            role=MessageRole(data['role']),
            status=data.get('status'),
            tool_calls=data.get('tool_calls'),
            run_id=data.get('run_id'),
            latest_message=Message.from_dict(data['latest_message']),
            attachments=attachments,
            timestamp=datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        )


@dataclass
class ToolOutput:
    """Tool output for submitting tool results"""
    tool_call_id: str
    output: str


@dataclass
class SubmitToolOutputsRequest:
    """Request for submitting tool outputs"""
    tool_outputs: List[ToolOutput]


@dataclass
class ToolOutputsResponse:
    """Response from submitting tool outputs"""
    message: str
    thread_id: uuid.UUID
    run_id: str
    content: Optional[str]
    message_id: uuid.UUID
    role: MessageRole
    status: Optional[str]
    tool_calls: Optional[List[Dict[str, Any]]]
    latest_message: Message
    timestamp: datetime

    @classmethod
    def from_dict(cls, data: dict) -> 'ToolOutputsResponse':
        """Create ToolOutputsResponse from API response dict"""
        return cls(
            message=data['message'],
            thread_id=uuid.UUID(data['thread_id']),
            run_id=data['run_id'],
            content=data.get('content'),
            message_id=uuid.UUID(data['message_id']),
            role=MessageRole(data['role']),
            status=data.get('status'),
            tool_calls=data.get('tool_calls'),
            latest_message=Message.from_dict(data['latest_message']),
            timestamp=datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        )
