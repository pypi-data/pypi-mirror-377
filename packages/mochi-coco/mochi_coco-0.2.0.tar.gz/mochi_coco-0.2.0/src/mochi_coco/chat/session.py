import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Any, Mapping, Tuple, Dict
from dataclasses import dataclass, asdict

from ollama import ChatResponse

@dataclass
class UserMessage:
    """
    A message sent by the user.
    """
    role: str = "user"
    content: str = ""
    message_id: Optional[str] = None
    timestamp: Optional[str] = None

    def __post_init__(self):
        if self.message_id is None:
            self.message_id = str(uuid.uuid4()).replace("-", "")[:10]
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

@dataclass
class SystemMessage:
    """
    A system message that sets the context/persona for the AI assistant.
    """
    role: str = "system"
    content: str = ""
    source_file: Optional[str] = None
    message_id: Optional[str] = None
    timestamp: Optional[str] = None

    def __post_init__(self):
        if self.message_id is None:
            self.message_id = str(uuid.uuid4()).replace("-", "")[:10]
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

@dataclass
class SessionMessage:
    role: str
    content: str
    model: Optional[str] = None
    message_id: Optional[str] = None
    timestamp: Optional[str] = None
    eval_count: Optional[int] = None
    prompt_eval_count: Optional[int] = None

    def __post_init__(self):
        if self.message_id is None:
            self.message_id = str(uuid.uuid4()).replace("-", "")[:10]
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


@dataclass
class SessionMetadata:
    session_id: str
    model: str
    created_at: str
    updated_at: str
    message_count: int = 0
    summary: Optional[Dict[str, Any]] = None
    summary_model: Optional[str] = None


class ChatSession:
    def __init__(self, model: str, session_id: Optional[str] = None, sessions_dir: Optional[str] = None):
        self.model = model
        self.session_id = session_id or self._generate_session_id()
        self.sessions_dir = Path(sessions_dir) if sessions_dir else Path.cwd() / "chat_sessions"
        self.sessions_dir.mkdir(exist_ok=True)

        self.messages: List[SessionMessage | UserMessage | SystemMessage] = []
        self.metadata = SessionMetadata(
            session_id=self.session_id,
            model=model,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )

        # Try to load existing session
        if session_id:
            self.load_session()

    def _generate_session_id(self) -> str:
        """Generate a random 10-character session ID using UUID."""
        return str(uuid.uuid4()).replace("-", "")[:10]

    @property
    def session_file(self) -> Path:
        """Get the path to the session JSON file."""
        return self.sessions_dir / f"{self.session_id}.json"

    def add_user_message(self, content: str, message_id: Optional[str] = None) -> None:
        """Add a user message to the session."""

        message = UserMessage(
            #role="user",
            content=content,
            message_id=message_id,
        )
        self.messages.append(message)
        self.metadata.message_count = len(self.messages)
        self.metadata.updated_at = datetime.now().isoformat()
        self.save_session()

    def add_system_message(self, content: str, source_file: Optional[str] = None, message_id: Optional[str] = None) -> None:
        """Add a system message as the first message in the session."""
        system_message = SystemMessage(
            content=content,
            source_file=source_file,
            message_id=message_id,
        )

        # Always insert system message at the beginning
        self.messages.insert(0, system_message)
        self.metadata.message_count = len(self.messages)
        self.metadata.updated_at = datetime.now().isoformat()
        self.save_session()

    def update_system_message(self, content: str, source_file: Optional[str] = None) -> None:
        """
        Update or add system message. System message is always at index 0 when present.

        Args:
            content: The system prompt content
            source_file: Optional filename of the source system prompt file
        """
        if self.messages and self.messages[0].role == "system":
            # Replace existing system message
            self.messages[0] = SystemMessage(
                content=content,
                source_file=source_file,
            )
        else:
            # Insert new system message at beginning
            system_message = SystemMessage(
                content=content,
                source_file=source_file,
            )
            self.messages.insert(0, system_message)

        self.metadata.message_count = len(self.messages)
        self.metadata.updated_at = datetime.now().isoformat()
        self.save_session()

    def has_system_message(self) -> bool:
        """Check if session has a system message (first message with role='system')."""
        return bool(self.messages and self.messages[0].role == "system")

    def get_current_system_prompt_file(self) -> Optional[str]:
        """Get filename of current system prompt for UI display."""
        if self.has_system_message() and hasattr(self.messages[0], 'source_file'):
            return self.messages[0].source_file
        return None

    def add_message(self, chunk: ChatResponse, message_id: Optional[str] = None) -> None:
        """Add a message to the session."""
        message = SessionMessage(
            role=chunk.message.role,
            content=chunk.message['content'],
            model=chunk.model,
            eval_count=chunk.eval_count,
            prompt_eval_count=chunk.prompt_eval_count,
            message_id=message_id
        )
        self.messages.append(message)
        self.metadata.message_count = len(self.messages)
        self.metadata.updated_at = datetime.now().isoformat()
        self.save_session()

    def get_messages_for_api(self) -> List[Mapping[str, Any]]:
        """Get messages in format suitable for API calls."""
        messages = []
        for message in self.messages:
            messages.append({
                "role": message.role,
                "content": message.content
            })

        return messages

    def save_session(self) -> None:
        """Save the current session to a JSON file."""
        session_data = {
            "metadata": asdict(self.metadata),
            "messages": [asdict(msg) for msg in self.messages]
        }

        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)

    def load_session(self) -> bool:
        """Load an existing session from JSON file. Returns True if successful."""
        if not self.session_file.exists():
            return False

        try:
            with open(self.session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)

            # Load metadata
            metadata_dict = session_data.get("metadata", {})
            self.metadata = SessionMetadata(**metadata_dict)

            # Load messages - handle UserMessage, SessionMessage, and SystemMessage types
            messages_data = session_data.get("messages", [])
            self.messages = []
            for msg_dict in messages_data:
                if msg_dict.get("role") == "user":
                    # For user messages, only use fields that UserMessage expects
                    user_msg_data = {
                        "role": msg_dict.get("role", "user"),
                        "content": msg_dict.get("content", ""),
                        "message_id": msg_dict.get("message_id"),
                        "timestamp": msg_dict.get("timestamp")
                    }
                    # Remove None values
                    user_msg_data = {k: v for k, v in user_msg_data.items() if v is not None}
                    self.messages.append(UserMessage(**user_msg_data))
                elif msg_dict.get("role") == "system":
                    # For system messages, only use fields that SystemMessage expects
                    system_msg_data = {
                        "role": msg_dict.get("role", "system"),
                        "content": msg_dict.get("content", ""),
                        "source_file": msg_dict.get("source_file"),
                        "message_id": msg_dict.get("message_id"),
                        "timestamp": msg_dict.get("timestamp")
                    }
                    # Remove None values
                    system_msg_data = {k: v for k, v in system_msg_data.items() if v is not None}
                    self.messages.append(SystemMessage(**system_msg_data))
                else:
                    self.messages.append(SessionMessage(**msg_dict))

            return True
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"Error loading session {self.session_id}: {e}")
            return False

    def get_session_summary(self) -> str:
        """Get a summary of the session."""
        if not self.messages:
            return f"Empty session with {self.model}"

        first_user_msg = next((msg.content for msg in self.messages if msg.role == "user"), "")
        preview = first_user_msg[:50] + "..." if len(first_user_msg) > 50 else first_user_msg

        return f"{self.session_id}: {preview}"

    @classmethod
    def list_sessions(cls, sessions_dir: Optional[str] = None) -> List["ChatSession"]:
        """List all existing chat sessions."""
        sessions_path = Path(sessions_dir) if sessions_dir else Path.cwd() / "chat_sessions"
        if not sessions_path.exists():
            return []

        sessions = []
        for session_file in sessions_path.glob("*.json"):
            session_id = session_file.stem
            try:
                # Create session object and load it
                session = cls(model="", session_id=session_id, sessions_dir=str(sessions_path))
                if session.load_session():
                    sessions.append(session)
            except Exception as e:
                print(f"Error loading session {session_id}: {e}")

        # Sort by updated_at (most recent first)
        sessions.sort(key=lambda s: s.metadata.updated_at, reverse=True)
        return sessions

    def delete_session(self) -> bool:
        """Delete the session file."""
        try:
            if self.session_file.exists():
                self.session_file.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting session {self.session_id}: {e}")
            return False

    def get_user_messages_with_indices(self) -> List[Tuple[int, int, UserMessage]]:
        """
        Get user messages with their display numbers and actual indices.

        Returns:
            List of tuples: (display_number, actual_index, message)
            where display_number is 1-based for UI, actual_index is 0-based for list operations
        """
        user_messages = []
        display_counter = 0

        for actual_index, message in enumerate(self.messages):
            if message.role == "user":
                display_counter += 1
                user_messages.append((display_counter, actual_index, message))

        return user_messages

    def edit_message_and_truncate(self, message_index: int, new_content: str) -> None:
        """
        Edit message at the given index and remove all subsequent messages.

        Args:
            message_index: The actual index (0-based) of the message to edit
            new_content: The new content for the message
        """
        if message_index < 0 or message_index >= len(self.messages):
            raise IndexError(f"Message index {message_index} is out of range")

        message = self.messages[message_index]
        if message.role != "user":
            raise ValueError(f"Can only edit user messages, but message at index {message_index} is {message.role}")

        # Update the message content
        message.content = new_content.strip()
        message.timestamp = datetime.now().isoformat()

        # Remove all messages after this index
        self.messages = self.messages[:message_index + 1]

        # Update metadata
        self.metadata.message_count = len(self.messages)
        self.metadata.updated_at = datetime.now().isoformat()

        # Save the session
        self.save_session()
