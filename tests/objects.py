from src.models.shared import ChatMessage, CompleteMessage, Model, ModelName


TEXT_1 = """\
[META id=0001]

[META schema_version=0.2]
[META number_of_messages=4]
[META current_time=2024-03-16 14:50:15]

[ROLE USER]
Hello

[ROLE ASSISTANT model=model_1]
Hi

[ROLE USER]
How are you?

[ROLE ASSISTANT model=model_2]
I'm fine."""

COMPLETE_MESSAGES_1 = [
    CompleteMessage(ChatMessage(role="user", content="Hello"), None),
    CompleteMessage(
        ChatMessage(role="assistant", content="Hi"),
        Model(None, ModelName("model_1")),
    ),
    CompleteMessage(ChatMessage(role="user", content="How are you?"), None),
    CompleteMessage(
        ChatMessage(role="assistant", content="I'm fine."),
        Model(None, ModelName("model_2")),
    ),
]
