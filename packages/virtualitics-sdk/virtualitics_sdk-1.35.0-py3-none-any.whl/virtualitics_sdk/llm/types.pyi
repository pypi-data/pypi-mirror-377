from _typeshed import Incomplete
from pydantic import BaseModel, computed_field
from typing import Literal
from virt_llm import AsyncLLMClient as AsyncLLMClient
from virtualitics_sdk.elements.element import ElementType as ElementType

logger: Incomplete

class RawChatContext(BaseModel):
    user_id: str
    app_id: str
    chat_id: str
    chat_index: int
    step_name: str
    element_id: str
    prompt: str
    llm_host: str
    model: str
    response: str | None
    llm_client: AsyncLLMClient | None
    class Config:
        arbitrary_types_allowed: bool

class ProcessedChatMessage(BaseModel):
    role: Literal['user', 'system']
    content: str

class ChatSource(BaseModel):
    title: str
    element_type: str

class ChatSourceCard(BaseModel):
    title: str
    data: list[ChatSource]
    def to_dict(self): ...

class StreamMessage(BaseModel):
    """Event for a single message token in the stream."""
    t: Literal['message']
    d: str

class StreamSourceInformation(BaseModel):
    """Event for the final, post-processed response."""
    t: Literal['post_processing']
    d: list[ChatSourceCard]

class StreamChatEnd(BaseModel):
    """Event to signal the end of the chat stream."""
    t: Literal['chat_end']
    d: Literal['']

class DashboardFilter(BaseModel):
    element_id: str
    selected: str | list | dict | None
    @computed_field
    @property
    def element_type(self) -> str: ...

class ActionPageUpdate(BaseModel):
    card_id: str
    step_name: str
    filters: list[DashboardFilter] | None

class StreamActionPageUpdate(BaseModel):
    """Trigger the frontend to perform a Page Update"""
    t: Literal['page_update']
    d: ActionPageUpdate

class StreamThinking(BaseModel):
    """Event to signal the end of the chat stream."""
    t: Literal['thinking']
    d: Literal['']

class StreamExecutingTool(BaseModel):
    """Event to signal the end of the chat stream."""
    t: Literal['tool']
    d: str

class StreamWaitingForInput(BaseModel):
    """Event to signal the end of the chat stream."""
    t: Literal['waiting']
    d: Literal['']

class StreamException(BaseModel):
    t: Literal['exception']
    d: str
StreamEvent = StreamMessage | StreamSourceInformation | StreamChatEnd | StreamActionPageUpdate | StreamThinking | StreamExecutingTool | StreamWaitingForInput | StreamException
