from dataclasses import dataclass, field


@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str
    name: str | None = field(kw_only=True, default=None)
    tool_calls: object = field(kw_only=True, default=None)
    tool_call_id: str | None = field(kw_only=True, default=None)
