#!/usr/bin/env python3
"""
aii - AI Intelligence: Multi-Modal AI Assistant

A powerful multi-modal AI assistant that serves as your intelligent companion for
translation, explanation, coding, writing, and shell automation - powered by multiple AI providers.

Features:
- Multi-Provider Support: Choose between Google Gemini, Anthropic Claude, and OpenAI GPT models 🆕
- Multi-Modal AI: Supports 5 different AI modes (shell, translate, explain, code, write)
- Natural Language Interface: Use intuitive commands like `aii translate "hello" to Spanish`
- Smart Environment Detection: Auto-detects your OS (macOS/Linux) and shell (bash, zsh, fish, etc.)
- Context-Aware: Provides culturally appropriate translations and OS-specific commands
- Safe Execution: Only prompts for execution on shell commands, not explanations or translations
- High-Quality Output: Shows confidence levels and provides detailed reasoning
- Secure: Uses environment variables for API keys with helpful setup guidance
- Model Selection: Choose specific models for different use cases and performance needs 🆕
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Protocol

try:
    from typing import assert_never  # Python 3.11+
except ImportError:
    from typing_extensions import assert_never  # Python 3.10  # noqa: UP035

from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.models.openai import OpenAIChatModel

# Version information - dynamically loaded from package metadata
try:
    from importlib.metadata import version

    __version__ = version("a2py")
except ImportError:
    # Fallback for Python < 3.8
    from importlib_metadata import version

    __version__ = version("a2py")
except Exception:
    # Fallback if package not installed
    __version__ = "unknown"
from pydantic_ai.providers.anthropic import AnthropicProvider
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai.providers.openai import OpenAIProvider


def debug_print(message: str) -> None:
    """Print debug message only if AII_DEBUG=true is set."""
    if os.environ.get("AII_DEBUG", "").lower() == "true":
        print(f"DEBUG: {message}")


class OSType(Enum):
    """Supported operating systems."""

    MACOS = "mac"
    LINUX = "linux"
    UNKNOWN = "unknown"


class ShellType(Enum):
    """Supported shell types."""

    BASH = "bash"
    ZSH = "zsh"
    FISH = "fish"
    CSH = "csh"
    TCSH = "tcsh"
    KSH = "ksh"
    DASH = "dash"
    SH = "sh"


class AIMode(Enum):
    """Supported AI operation modes."""

    SHELL = "shell"
    TRANSLATE = "translate"
    EXPLAIN = "explain"
    CODE = "code"
    WRITE = "write"
    ANALYZE = "analyze"


class ProviderType(Enum):
    """Supported AI provider types."""

    GOOGLE = "google"
    ANTHROPIC = "anthropic"
    OPENAI = "openai"


@dataclass(frozen=True)
class EnvironmentContext:
    """Immutable context about the user's environment."""

    os_type: OSType
    shell_type: ShellType
    ai_mode: AIMode
    is_detected: bool = True
    confidence: float = 1.0
    target_language: str | None = None
    provider_type: ProviderType = ProviderType.GOOGLE  # Default to Google
    model_name: str | None = None

    def __str__(self) -> str:
        provider_info = f"{self.provider_type.value}"
        if self.model_name:
            provider_info += f":{self.model_name}"

        if self.ai_mode == AIMode.SHELL:
            status = "detected" if self.is_detected else "overridden"
            return f"{self.os_type.value}/{self.shell_type.value} ({status}) • {provider_info}"
        elif self.ai_mode == AIMode.TRANSLATE and self.target_language:
            return f"translate to {self.target_language} • {provider_info}"
        else:
            return f"{self.ai_mode.value} mode • {provider_info}"


@dataclass(frozen=True)
class AIRequest:
    """Immutable request for AI processing."""

    prompt: str
    context: EnvironmentContext
    require_confirmation: bool = True

    @property
    def sanitized_prompt(self) -> str:
        """Get sanitized version of the prompt."""
        return " ".join(self.prompt.split())


@dataclass
class AIResponse:
    """Response containing AI-generated content and metadata."""

    success: bool
    content: str | None = None
    explanation: str | None = None
    error_message: str | None = None
    confidence: float = 0.0
    mode: AIMode = AIMode.SHELL

    @property
    def is_safe_to_execute(self) -> bool:
        """Check if content appears safe to execute (for shell commands only)."""
        if self.mode != AIMode.SHELL or not self.content:
            return False

        dangerous_patterns = ["rm -rf", "sudo rm", "format", "mkfs", ":(){"]
        return not any(
            pattern in self.content.lower() for pattern in dangerous_patterns
        )

    @property
    def is_executable(self) -> bool:
        """Check if this response type supports execution (shell commands only)."""
        return self.mode == AIMode.SHELL and bool(self.content)


@dataclass
class ConversationMessage:
    """Represents a single message in a conversation."""

    timestamp: float
    request: str
    response: str
    context: dict[str, Any]
    success: bool
    mode: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ConversationMessage:
        """Create from dictionary from JSON deserialization."""
        return cls(**data)


@dataclass
class ConversationHistory:
    """Represents a conversation history."""

    conversation_id: str
    created_at: float
    last_updated: float
    messages: list[ConversationMessage]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "conversation_id": self.conversation_id,
            "created_at": self.created_at,
            "last_updated": self.last_updated,
            "messages": [msg.to_dict() for msg in self.messages],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ConversationHistory:
        """Create from dictionary from JSON deserialization."""
        messages = [
            ConversationMessage.from_dict(msg) for msg in data.get("messages", [])
        ]
        return cls(
            conversation_id=data["conversation_id"],
            created_at=data["created_at"],
            last_updated=data["last_updated"],
            messages=messages,
        )


class ContextMemoryManager:
    """Manages conversation history and context memory."""

    def __init__(self, base_dir: Path | None = None):
        """Initialize context memory manager."""
        if base_dir is None:
            base_dir = Path.home() / ".aii"
        self.base_dir = Path(base_dir)
        self.history_dir = self.base_dir / "history"
        self.current_conversation_file = self.base_dir / "current_conversation"

        # Ensure directories exist
        self.history_dir.mkdir(parents=True, exist_ok=True)

        # Current conversation ID (None means no active conversation)
        self._current_conversation_id: str | None = None

        # Load current conversation ID if exists
        self._load_current_conversation_id()

    def _load_current_conversation_id(self) -> None:
        """Load the current conversation ID from file."""
        try:
            if self.current_conversation_file.exists():
                self._current_conversation_id = (
                    self.current_conversation_file.read_text().strip()
                )
                # Validate conversation exists
                if not self._get_conversation_file(
                    self._current_conversation_id
                ).exists():
                    self._current_conversation_id = None
                    self.current_conversation_file.unlink(missing_ok=True)
        except Exception:
            self._current_conversation_id = None

    def _save_current_conversation_id(self, conversation_id: str | None) -> None:
        """Save the current conversation ID to file."""
        if conversation_id:
            self.current_conversation_file.write_text(conversation_id)
        else:
            self.current_conversation_file.unlink(missing_ok=True)
        self._current_conversation_id = conversation_id

    def _get_conversation_file(self, conversation_id: str) -> Path:
        """Get the file path for a conversation."""
        return self.history_dir / f"{conversation_id}.json"

    def _generate_conversation_id(self) -> str:
        """Generate a unique conversation ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"{timestamp}_{unique_id}"

    def start_new_conversation(self) -> str:
        """Start a new conversation and return the conversation ID."""
        conversation_id = self._generate_conversation_id()
        now = time.time()

        # Create new conversation history
        history = ConversationHistory(
            conversation_id=conversation_id,
            created_at=now,
            last_updated=now,
            messages=[],
        )

        # Save to file
        self._save_conversation(history)

        # Set as current conversation
        self._save_current_conversation_id(conversation_id)

        return conversation_id

    def get_current_conversation_id(self) -> str | None:
        """Get the current conversation ID."""
        return self._current_conversation_id

    def clear_current_conversation(self) -> None:
        """Clear the current conversation context."""
        self._save_current_conversation_id(None)

    def continue_conversation(self, conversation_id: str) -> bool:
        """Continue a specific conversation by ID. Returns True if conversation exists."""
        if conversation_id == "latest":
            # Use current conversation if available
            current_id = self.get_current_conversation_id()
            if current_id:
                return True
            else:
                # Find most recent conversation
                conversations = self.list_conversations(limit=1)
                if conversations:
                    latest_id = conversations[0]["id"]
                    self._save_current_conversation_id(latest_id)
                    return True
                return False
        else:
            # Try to continue specific conversation ID
            if self._load_conversation(conversation_id):
                self._save_current_conversation_id(conversation_id)
                return True
            return False

    def conversation_exists(self, conversation_id: str) -> bool:
        """Check if a conversation exists."""
        if conversation_id == "latest":
            current_id = self.get_current_conversation_id()
            if current_id:
                return True
            conversations = self.list_conversations(limit=1)
            return len(conversations) > 0
        else:
            return self._load_conversation(conversation_id) is not None

    def _save_conversation(self, history: ConversationHistory) -> None:
        """Save conversation history to file."""
        file_path = self._get_conversation_file(history.conversation_id)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(history.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            debug_print(f"Failed to save conversation: {e}")

    def _load_conversation(self, conversation_id: str) -> ConversationHistory | None:
        """Load conversation history from file."""
        file_path = self._get_conversation_file(conversation_id)
        try:
            if file_path.exists():
                with open(file_path, encoding="utf-8") as f:
                    data = json.load(f)
                return ConversationHistory.from_dict(data)
        except Exception as e:
            debug_print(f"Failed to load conversation: {e}")
        return None

    def add_message_to_conversation(
        self,
        conversation_id: str,
        request: str,
        response: AIResponse,
        context: EnvironmentContext,
    ) -> None:
        """Add a message to the conversation history."""
        # Load existing conversation or create new one
        history = self._load_conversation(conversation_id)
        if not history:
            now = time.time()
            history = ConversationHistory(
                conversation_id=conversation_id,
                created_at=now,
                last_updated=now,
                messages=[],
            )

        # Create message
        message = ConversationMessage(
            timestamp=time.time(),
            request=request,
            response=response.content or "",
            context={
                "mode": context.ai_mode.value,
                "provider": context.provider_type.value,
                "model": context.model_name,
                "os_type": context.os_type.value,
                "shell_type": context.shell_type.value,
                "target_language": context.target_language,
                "confidence": response.confidence,
            },
            success=response.success,
            mode=context.ai_mode.value,
        )

        # Add message and update timestamp
        history.messages.append(message)
        history.last_updated = time.time()

        # Save conversation
        self._save_conversation(history)

    def get_conversation_context(
        self, conversation_id: str, max_messages: int = 5
    ) -> list[str]:
        """Get recent conversation context for prompting."""
        history = self._load_conversation(conversation_id)
        if not history:
            return []

        # Get last N messages
        recent_messages = history.messages[-max_messages:] if history.messages else []

        context_lines = []
        for msg in recent_messages:
            context_lines.append(f"User: {msg.request}")
            context_lines.append(f"Assistant: {msg.response}")

        return context_lines

    def list_conversations(self, limit: int = 10) -> list[dict[str, Any]]:
        """List recent conversations with metadata."""
        conversations = []

        # Find all conversation files
        for file_path in self.history_dir.glob("*.json"):
            try:
                with open(file_path, encoding="utf-8") as f:
                    data = json.load(f)

                conversations.append(
                    {
                        "id": data["conversation_id"],
                        "created_at": datetime.fromtimestamp(
                            data["created_at"]
                        ).strftime("%Y-%m-%d %H:%M:%S"),
                        "last_updated": datetime.fromtimestamp(
                            data["last_updated"]
                        ).strftime("%Y-%m-%d %H:%M:%S"),
                        "message_count": len(data.get("messages", [])),
                        "is_current": data["conversation_id"]
                        == self._current_conversation_id,
                    }
                )
            except Exception:
                continue

        # Sort by last_updated (most recent first) and limit
        conversations.sort(key=lambda x: x["last_updated"], reverse=True)
        return conversations[:limit]

    def show_history(self) -> None:
        """Display conversation history in a user-friendly format."""
        conversations = self.list_conversations()

        if not conversations:
            print("📭 No conversation history found.")
            return

        print("📚 Recent Conversations:")
        print("=" * 60)

        for conv in conversations:
            current_marker = "🔄 " if conv["is_current"] else "   "
            print(f"{current_marker}{conv['id']}")
            print(f"     Created: {conv['created_at']}")
            print(f"     Updated: {conv['last_updated']}")
            print(f"     Messages: {conv['message_count']}")
            print()

        if self._current_conversation_id:
            print(f"📍 Current conversation: {self._current_conversation_id}")
        else:
            print("📍 No active conversation")


class EnvironmentDetector(Protocol):
    """Protocol for environment detection strategies."""

    def detect_os(self) -> OSType:
        """Detect the operating system."""
        ...

    def detect_shell(self) -> ShellType:
        """Detect the current shell."""
        ...


class SystemEnvironmentDetector:
    """Concrete implementation of environment detection."""

    def detect_os(self) -> OSType:
        """Detect operating system using platform module."""
        system = platform.system().lower()
        if system == "darwin":
            return OSType.MACOS
        elif system == "linux":
            return OSType.LINUX
        return OSType.UNKNOWN

    def detect_shell(self) -> ShellType:
        """Detect current shell using multiple strategies."""
        # Strategy 1: Fish-specific environment variable
        if os.environ.get("FISH_VERSION"):
            return ShellType.FISH

        # Strategy 2: Check parent process
        try:
            import psutil

            current = psutil.Process()
            parent = current.parent()
            if parent:
                parent_name = parent.name().lower()
                for shell_type in ShellType:
                    if shell_type.value in parent_name:
                        return shell_type
        except (ImportError, Exception):
            pass

        # Strategy 3: SHELL environment variable
        shell_path = os.environ.get("SHELL", "")
        if shell_path:
            shell_name = Path(shell_path).name
            try:
                return ShellType(shell_name)
            except ValueError:
                pass

        # Default fallback
        return ShellType.FISH


class PromptGenerator(ABC):
    """Abstract base class for generating AI prompts."""

    @abstractmethod
    def generate_system_prompt(self, context: EnvironmentContext) -> str:
        """Generate system prompt based on environment context."""
        pass

    @abstractmethod
    def generate_user_prompt(self, request: AIRequest) -> str:
        """Generate user prompt for the AI."""
        pass


class MultiModalPromptGenerator(PromptGenerator):
    """Generates prompts for different AI modes including shell, translation, etc."""

    def __init__(self) -> None:
        self.directory_analyzer = DirectoryAnalyzer()

    _MODE_PROMPTS = {
        AIMode.SHELL: {
            "base": """You are an intelligent shell command generator.
Your task: Generate safe, efficient shell commands based on user requests.

CRITICAL RULES:
1. ALWAYS respond in the same language as the user's request
2. Use the `think` function to explain your reasoning
3. Use the `respond` function to provide the final command
4. Consider the user's specific OS and shell environment
5. Prioritize safety - avoid destructive commands
6. Provide single-line commands when possible""",
            "tool": "respond",
        },
        AIMode.TRANSLATE: {
            "base": """You are a professional translator and linguist with deep cultural understanding.
Your task: Provide natural, culturally appropriate translations that avoid machine-translate awkwardness.

TRANSLATION PROCESS:
1. Use `think` to explain your translation choices
2. Provide your translation
3. Call `respond(success=True, content="your translation", confidence=0.9)`

TRANSLATION PRINCIPLES:
- Maintain the original tone and intent
- Use natural expressions in the target language
- Consider cultural context and idioms
- Adapt formal/informal registers appropriately

CRITICAL: Always end by calling respond(success=True, content="your translation", confidence=0.9)""",
            "tool": "respond",
        },
        AIMode.EXPLAIN: {
            "base": """You are an expert educator and technical communicator.
Your task: Provide clear, comprehensive explanations that are easy to understand.

EXPLANATION PROCESS:
1. Use `think` to plan your explanation structure
2. Write your full explanation
3. Call `respond(success=True, content="your full explanation here", confidence=0.9)`

EXPLANATION PRINCIPLES:
- Break down complex concepts into digestible parts
- Use analogies and examples when helpful
- Include practical examples when relevant

CRITICAL: Always end by calling respond(success=True, content="your explanation", confidence=0.9)""",
            "tool": "respond",
        },
        AIMode.CODE: {
            "base": """You are a senior software engineer and code mentor.
Your task: Generate, review, or explain code with best practices in mind.

CODING PROCESS:
1. Use `think` to explain your approach
2. Write your code
3. Call `respond(success=True, content="your code", confidence=0.9)`

CODING PRINCIPLES:
- Write clean, readable, and maintainable code
- Follow language-specific conventions
- Include appropriate comments
- Specify the programming language clearly

CRITICAL: Always end by calling respond(success=True, content="your code", confidence=0.9)""",
            "tool": "respond",
        },
        AIMode.WRITE: {
            "base": """You are a professional writer and communication specialist.
Your task: Create well-structured, engaging, and purpose-driven content.

WRITING PROCESS:
1. Use `think` to plan your writing approach
2. Create your content
3. Call `respond(success=True, content="your written content", confidence=0.9)`

WRITING PRINCIPLES:
- Adapt style and tone to the intended audience
- Structure content logically with clear flow
- Consider the specific purpose (email, blog, report, etc.)
- Ensure clarity and conciseness

CRITICAL: Always end by calling respond(success=True, content="your content", confidence=0.9)""",
            "tool": "respond",
        },
        AIMode.ANALYZE: {
            "base": """You are a senior software architect and code analyst.
Your task: Analyze directory structures, codebases, and project architectures to provide insights.

ANALYSIS PROCESS:
1. Use `think` to plan your analysis approach
2. Examine the provided directory/file information
3. Call `respond(success=True, content="your analysis", confidence=0.9)`

ANALYSIS PRINCIPLES:
- Provide structured, actionable insights
- Identify patterns, issues, and opportunities
- Consider software architecture best practices
- Focus on maintainability, scalability, and code quality
- Tailor analysis to the specific request (summary, issues, suggestions, architecture)

CRITICAL: Always end by calling respond(success=True, content="your analysis", confidence=0.9)""",
            "tool": "respond",
        },
    }

    _OS_PROMPTS = {
        OSType.MACOS: """
macOS Environment:
- Use Homebrew (brew) for package management
- Leverage macOS commands: open, pbcopy, pbpaste, mdfind
- Account for BSD utilities (different from GNU versions)
- Use launchctl for service management
- Consider case-insensitive HFS+ filesystem by default
""",
        OSType.LINUX: """
Linux Environment:
- Support multiple package managers: apt, yum, dnf, pacman
- Use GNU versions of utilities with full feature sets
- Leverage systemd/systemctl for service management
- Account for case-sensitive filesystems
- Use xclip/wl-clipboard for clipboard operations
""",
    }

    _SHELL_PROMPTS = {
        ShellType.FISH: """
Shell: Fish (Friendly Interactive Shell)
- Syntax: 'set var value' not 'var=value'
- Logic: 'and'/'or' instead of '&&'/'||'
- Functions: 'function name; commands; end'
- Built-ins: contains, string, math commands
""",
        ShellType.ZSH: """
Shell: Zsh (Z Shell)
- Enhanced globbing: **/*.py for recursive patterns
- Arrays: zero-indexed like arr[1] for first element
- Built-in calculator: $((expression))
- Oh-My-Zsh framework compatibility
""",
        ShellType.BASH: """
Shell: Bash (Bourne Again Shell)
- POSIX compliance with extensions
- Arrays: arr=(item1 item2), access with ${arr[0]}
- Process substitution: <(command)
- Brace expansion: {1..10}, {a,b,c}
""",
    }

    def generate_system_prompt(self, context: EnvironmentContext) -> str:
        """Generate comprehensive system prompt based on AI mode."""
        mode_config = self._MODE_PROMPTS.get(
            context.ai_mode, self._MODE_PROMPTS[AIMode.SHELL]
        )
        base_prompt = mode_config["base"]

        # Add environment-specific context for shell mode
        if context.ai_mode == AIMode.SHELL:
            os_specific = self._OS_PROMPTS.get(context.os_type, "")
            shell_specific = self._SHELL_PROMPTS.get(context.shell_type, "")
            return f"{base_prompt}\n{os_specific}\n{shell_specific}"

        # Add target language for translation mode
        elif context.ai_mode == AIMode.TRANSLATE and context.target_language:
            return f"{base_prompt}\n\nTarget Language: {context.target_language}\nEnsure translations sound natural and culturally appropriate for native speakers."

        return base_prompt

    def generate_user_prompt(self, request: AIRequest) -> str:
        """Generate user prompt based on AI mode."""
        context = request.context

        if context.ai_mode == AIMode.SHELL:
            return f"""Environment: {context}
Request: {request.sanitized_prompt}

Please provide an appropriate shell command for this environment."""

        elif context.ai_mode == AIMode.TRANSLATE:
            target_lang = context.target_language or "the target language"
            return f"""Please translate the following text to {target_lang}:

"{request.sanitized_prompt}"

Provide a natural, culturally appropriate translation."""

        elif context.ai_mode == AIMode.EXPLAIN:
            return f"""Please explain the following topic or concept:

{request.sanitized_prompt}

Provide a clear, comprehensive explanation."""

        elif context.ai_mode == AIMode.CODE:
            return f"""Code request: {request.sanitized_prompt}

Please provide appropriate code with explanations."""

        elif context.ai_mode == AIMode.WRITE:
            return f"""Writing request: {request.sanitized_prompt}

Please create appropriate content based on this request."""

        elif context.ai_mode == AIMode.ANALYZE:
            # For analyze mode, scan the directory and include structure information
            # Default to current directory if no path specified
            analyze_path = (
                "."  # This will be enhanced when we integrate with parsed_args
            )

            # Scan the directory structure
            structure = self.directory_analyzer.scan_directory(analyze_path)
            directory_summary = self.directory_analyzer.generate_summary(structure)

            return f"""Directory/Project Analysis Request: {request.sanitized_prompt}

{directory_summary}

Based on the directory structure and file information above, please provide a comprehensive analysis addressing the user's request."""

        # All enum values should be covered above
        raise ValueError(f"Unsupported AI mode: {context.ai_mode}")


class AIGenerator:
    """Main class for AI-powered content generation across multiple modes."""

    def __init__(self, api_key: str, prompt_generator: PromptGenerator):
        self.api_key = api_key
        self.prompt_generator = prompt_generator
        self._agents: dict[str, Agent[None, AIResponse]] = {}

    def _get_agent(self, context: EnvironmentContext) -> Agent[None, AIResponse]:
        """Get or create agent for specific environment context."""
        # Create cache key based on mode, provider, and relevant context
        provider_key = f"{context.provider_type.value}"
        if context.model_name:
            provider_key += f"_{context.model_name}"

        if context.ai_mode == AIMode.SHELL:
            cache_key = f"shell_{context.os_type.value}_{context.shell_type.value}_{provider_key}"
        elif context.ai_mode == AIMode.TRANSLATE:
            cache_key = f"translate_{context.target_language or 'auto'}_{provider_key}"
        else:
            cache_key = f"{context.ai_mode.value}_general_{provider_key}"

        if cache_key not in self._agents:
            system_prompt = self.prompt_generator.generate_system_prompt(context)

            # Create provider and model based on context
            if context.provider_type == ProviderType.ANTHROPIC:
                anthropic_api_key = self._get_anthropic_api_key()
                anthropic_provider = AnthropicProvider(api_key=anthropic_api_key)
                model_name = context.model_name or "claude-3-5-sonnet-latest"
                agent: Agent[None, AIResponse] = Agent(
                    model=AnthropicModel(model_name, provider=anthropic_provider),
                    system_prompt=system_prompt,
                    output_type=AIResponse,
                )
            elif context.provider_type == ProviderType.OPENAI:
                openai_api_key = self._get_openai_api_key()
                openai_provider = OpenAIProvider(api_key=openai_api_key)
                model_name = context.model_name or "gpt-4o"
                agent = Agent(
                    model=OpenAIChatModel(model_name, provider=openai_provider),
                    system_prompt=system_prompt,
                    output_type=AIResponse,
                )
            else:  # Default to Google
                google_provider = GoogleProvider(api_key=self.api_key)
                model_name = context.model_name or "gemini-2.0-flash"
                agent = Agent(
                    model=GoogleModel(model_name, provider=google_provider),
                    system_prompt=system_prompt,
                    output_type=AIResponse,
                )

            self._setup_agent_tools(agent, context.ai_mode)
            self._agents[cache_key] = agent

        return self._agents[cache_key]

    def _get_anthropic_api_key(self) -> str:
        """Get Anthropic API key from environment."""
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            print(
                "❌ Error: ANTHROPIC_API_KEY environment variable is required for Anthropic provider."
            )
            print("💡 Setup: export ANTHROPIC_API_KEY=your_api_key_here")
            print("🔗 Get key: https://console.anthropic.com/settings/keys")
            sys.exit(1)
        return api_key

    def _get_openai_api_key(self) -> str:
        """Get OpenAI API key from environment."""
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            print(
                "❌ Error: OPENAI_API_KEY environment variable is required for OpenAI provider."
            )
            print("💡 Setup: export OPENAI_API_KEY=your_api_key_here")
            print("🔗 Get key: https://platform.openai.com/account/api-keys")
            sys.exit(1)
        return api_key

    def _setup_agent_tools(self, agent: Agent[None, AIResponse], mode: AIMode) -> None:
        """Setup tools for the agent based on mode."""
        debug_print(f"Setting up agent tools for mode: {mode}")

        @agent.tool_plain
        def think(reasoning: str) -> None:
            """Communicate reasoning to the user."""
            if mode == AIMode.TRANSLATE:
                print(f"🌐 Translation Logic: {reasoning}\n")
            elif mode == AIMode.EXPLAIN:
                print(f"🎓 Explanation Structure: {reasoning}\n")
            elif mode == AIMode.CODE:
                print(f"💻 Code Planning: {reasoning}\n")
            elif mode == AIMode.WRITE:
                print(f"✍️  Writing Strategy: {reasoning}\n")
            else:
                print(f"🤔 AII Thinking: {reasoning}\n")

        @agent.tool_plain
        def respond(
            success: bool,
            content: str,
            explanation: str | None = None,
            confidence: float = 0.8,
        ) -> AIResponse:
            """Provide the final response with your generated content.

            Args:
                success: Always set to True when providing content
                content: Your main response (translation, explanation, code, etc.)
                explanation: Optional additional context or notes
                confidence: Your confidence in the response (0.0-1.0)
            """
            debug_print(f"respond() called with mode: {mode}")
            response = AIResponse(
                success=success,
                content=content,
                explanation=explanation,
                error_message=None,
                confidence=confidence,
                mode=mode,
            )
            debug_print(f"Created response with mode: {response.mode}")
            return response

    async def generate_async(self, request: AIRequest) -> AIResponse:
        """Generate content asynchronously."""
        agent = self._get_agent(request.context)
        user_prompt = self.prompt_generator.generate_user_prompt(request)

        try:
            result = await agent.run(user_prompt)
            response = result.output
            assert isinstance(
                response, AIResponse
            ), f"Expected AIResponse, got {type(response)}"
            return response
        except Exception as e:
            return AIResponse(
                success=False,
                error_message=f"AI generation failed: {str(e)}",
                mode=request.context.ai_mode,
            )

    def generate(self, request: AIRequest) -> AIResponse:
        """Generate content synchronously."""
        agent = self._get_agent(request.context)
        user_prompt = self.prompt_generator.generate_user_prompt(request)

        try:
            result = agent.run_sync(user_prompt)
            response = result.output
            assert isinstance(
                response, AIResponse
            ), f"Expected AIResponse, got {type(response)}"
            debug_print(f"Agent returned response with mode: {response.mode}")

            # Force the mode to match the request context if it doesn't match
            if response.mode != request.context.ai_mode:
                debug_print(
                    f"Mode mismatch! Expected {request.context.ai_mode}, got {response.mode}"
                )
                debug_print("Creating new response with correct mode...")
                corrected_response = AIResponse(
                    success=response.success,
                    content=response.content,
                    explanation=response.explanation,
                    error_message=response.error_message,
                    confidence=response.confidence,
                    mode=request.context.ai_mode,
                )
                debug_print(
                    f"New response created with mode: {corrected_response.mode}"
                )
                return corrected_response

            return response
        except Exception as e:
            return AIResponse(
                success=False,
                error_message=f"AI generation failed: {str(e)}",
                mode=request.context.ai_mode,
            )


class DirectoryAnalyzer:
    """Analyzes directory structures and generates summaries for AI analysis."""

    def __init__(self) -> None:
        self.ignore_patterns = {
            ".git",
            ".svn",
            ".hg",  # VCS directories
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",  # Python cache
            "node_modules",
            ".npm",  # Node.js
            ".venv",
            "venv",
            "env",  # Python virtual environments
            "dist",
            "build",
            "target",  # Build directories
            ".DS_Store",
            "Thumbs.db",  # OS files
            ".env",
            ".env.local",  # Environment files
        }

    def should_ignore(self, path: Path) -> bool:
        """Check if a path should be ignored."""
        return any(pattern in str(path) for pattern in self.ignore_patterns)

    def scan_directory(
        self, directory_path: str | Path, max_depth: int = 3
    ) -> dict[str, Any]:
        """Scan directory and return structure information."""
        directory_path = Path(directory_path).resolve()

        if not directory_path.exists():
            return {"error": f"Directory does not exist: {directory_path}"}

        if not directory_path.is_dir():
            return {"error": f"Path is not a directory: {directory_path}"}

        structure = {
            "path": str(directory_path),
            "name": directory_path.name,
            "files": [],
            "directories": [],
            "file_counts": {},
            "total_files": 0,
            "total_directories": 0,
        }

        try:
            self._scan_recursive(directory_path, structure, 0, max_depth)
        except PermissionError:
            structure["error"] = f"Permission denied accessing: {directory_path}"
        except Exception as e:
            structure["error"] = f"Error scanning directory: {str(e)}"

        return structure

    def _scan_recursive(
        self, path: Path, structure: dict, current_depth: int, max_depth: int
    ) -> None:
        """Recursively scan directory structure."""
        if current_depth >= max_depth:
            return

        for item in sorted(path.iterdir()):
            if self.should_ignore(item):
                continue

            relative_path = item.relative_to(Path(structure["path"]))

            if item.is_file():
                file_info = {
                    "name": item.name,
                    "path": str(relative_path),
                    "size": item.stat().st_size,
                    "extension": item.suffix.lower(),
                }
                structure["files"].append(file_info)
                structure["total_files"] += 1

                # Count file types
                ext = item.suffix.lower() or "no_extension"
                structure["file_counts"][ext] = structure["file_counts"].get(ext, 0) + 1

            elif item.is_dir():
                dir_info = {
                    "name": item.name,
                    "path": str(relative_path),
                    "depth": current_depth + 1,
                }
                structure["directories"].append(dir_info)
                structure["total_directories"] += 1

                # Recursively scan subdirectory
                self._scan_recursive(item, structure, current_depth + 1, max_depth)

    def generate_summary(self, structure: dict) -> str:
        """Generate a text summary of the directory structure for AI analysis."""
        if "error" in structure:
            return f"Error: {structure['error']}"

        lines = []
        lines.append(f"📁 Directory Analysis: {structure['name']}")
        lines.append(f"📍 Path: {structure['path']}")
        lines.append("")

        # Summary statistics
        lines.append("📊 Summary Statistics:")
        lines.append(f"  • Total files: {structure['total_files']}")
        lines.append(f"  • Total directories: {structure['total_directories']}")
        lines.append("")

        # File type breakdown
        if structure["file_counts"]:
            lines.append("📄 File Types:")
            for ext, count in sorted(
                structure["file_counts"].items(), key=lambda x: x[1], reverse=True
            ):
                ext_display = ext if ext != "no_extension" else "(no extension)"
                lines.append(f"  • {ext_display}: {count} files")
            lines.append("")

        # Directory structure (top-level)
        if structure["directories"]:
            lines.append("📂 Directory Structure:")
            for dir_info in structure["directories"][:20]:  # Limit to first 20
                indent = "  " * (dir_info["depth"])
                lines.append(f"{indent}📁 {dir_info['name']}/")
            if len(structure["directories"]) > 20:
                lines.append(
                    f"  ... and {len(structure['directories']) - 20} more directories"
                )
            lines.append("")

        # Key files (common important files)
        important_files = []
        for file_info in structure["files"]:
            name = file_info["name"].lower()
            if name in [
                "readme.md",
                "package.json",
                "requirements.txt",
                "cargo.toml",
                "pom.xml",
                "build.gradle",
                "makefile",
                "dockerfile",
                ".gitignore",
            ]:
                important_files.append(file_info["name"])

        if important_files:
            lines.append("📋 Key Configuration Files:")
            for file in important_files:
                lines.append(f"  • {file}")
            lines.append("")

        return "\n".join(lines)


class ResponseHandler:
    """Handles AI response display and execution for different modes."""

    @staticmethod
    def display_response(response: AIResponse) -> None:
        """Display AI response based on mode."""
        debug_print(f"display_response() received mode: {response.mode}")
        debug_print(
            f"response.mode == AIMode.EXPLAIN: {response.mode == AIMode.EXPLAIN}"
        )
        debug_print(f"response.mode == AIMode.SHELL: {response.mode == AIMode.SHELL}")

        if not response.success:
            print(f"❌ Failed: {response.error_message}")
            return

        if not response.content:
            print("❌ No content generated")
            return

        # Mode-specific display
        if response.mode == AIMode.SHELL:
            print(f"💡 Generated Command: {response.content}")
        elif response.mode == AIMode.TRANSLATE:
            print("🌐 Translation:")
            print(response.content)
        elif response.mode == AIMode.EXPLAIN:
            print("🎓 Explanation:")
            print(response.content)
        elif response.mode == AIMode.CODE:
            print("💻 Generated Code:")
            print(response.content)
        elif response.mode == AIMode.WRITE:
            print("✍️  Generated Content:")
            print(response.content)
        elif response.mode == AIMode.ANALYZE:
            print("🔍 Analysis Report:")
            print(response.content)
        else:
            assert_never(response.mode)

        # Show explanation if available
        if response.explanation:
            print(f"\n📝 Additional Info: {response.explanation}")

        # Show confidence
        print(f"\n🎯 Confidence: {response.confidence:.1%}")

    @staticmethod
    def prompt_for_execution(response: AIResponse) -> bool:
        """Prompt user for execution confirmation (shell commands only)."""
        if not response.is_executable or not response.content:
            return False

        if not response.is_safe_to_execute:
            print("\n⚠️  WARNING: This command may be potentially dangerous!")

        try:
            choice = input("\n🚀 Execute this command? [y/N]: ").strip().lower()
            return choice in ["y", "yes"]
        except (KeyboardInterrupt, EOFError):
            print("\n❌ Cancelled by user")
            return False

    @staticmethod
    def execute_command(command: str) -> int:
        """Execute the command and return exit code."""
        try:
            return os.system(command)  # nosec B605 - needed for shell execution
        except Exception as e:
            print(f"❌ Execution failed: {e}")
            return 1


class AiiApplication:
    """Main application class for the aii tool."""

    def __init__(self) -> None:
        self.detector = SystemEnvironmentDetector()
        self.prompt_generator = MultiModalPromptGenerator()
        self.response_handler = ResponseHandler()
        self.context_memory = ContextMemoryManager()
        self.directory_analyzer = DirectoryAnalyzer()
        self.generator: AIGenerator | None = None

    def _get_api_key(self) -> str:
        """Get API key from environment with helpful error message."""
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("❌ Error: GEMINI_API_KEY environment variable is required.")
            print("💡 Setup: export GEMINI_API_KEY=your_api_key_here")
            print("🔗 Get key: https://aistudio.google.com/apikey")
            sys.exit(1)
        return api_key

    def _parse_target_language(self, prompt: str) -> tuple[str, str | None]:
        """Parse target language from translate mode prompt."""
        # Look for patterns like "to Spanish", "into French", etc.
        import re

        # Common patterns for language specification
        patterns = [
            r"\b(?:to|into|in)\s+(\w+)$",  # "to Spanish", "into French"
            r"^(\w+):\s*(.+)",  # "Spanish: hello world"
            r"\b--(\w+)\b",  # "--spanish"
        ]

        for pattern in patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                if pattern.startswith("^"):  # Language prefix pattern
                    return match.group(2).strip(), match.group(1).title()
                else:
                    # Remove the language specification from prompt
                    cleaned_prompt = re.sub(
                        pattern, "", prompt, flags=re.IGNORECASE
                    ).strip()
                    return cleaned_prompt, match.group(1).title()

        return prompt, None

    def _create_environment_context(
        self, args: argparse.Namespace
    ) -> EnvironmentContext:
        """Create environment context from arguments and detection."""
        # Determine AI mode
        ai_mode = (
            AIMode(args.mode) if hasattr(args, "mode") and args.mode else AIMode.SHELL
        )

        # For shell mode, detect OS and shell
        if ai_mode == AIMode.SHELL:
            if args.os:
                os_type = OSType(args.os)
                is_detected = False
            else:
                os_type = self.detector.detect_os()
                is_detected = True

            if args.shell:
                shell_type = ShellType(args.shell)
                if is_detected:
                    is_detected = False
            else:
                shell_type = self.detector.detect_shell()
        else:
            # For non-shell modes, use defaults
            os_type = OSType.UNKNOWN
            shell_type = ShellType.BASH
            is_detected = True

        # Handle target language for translation
        target_language = None
        if ai_mode == AIMode.TRANSLATE and hasattr(args, "target_language"):
            target_language = args.target_language

        # Handle provider and model selection
        provider_type = ProviderType.GOOGLE  # Default
        if hasattr(args, "provider") and args.provider:
            provider_type = ProviderType(args.provider)

        model_name = None
        if hasattr(args, "model") and args.model:
            model_name = args.model

        return EnvironmentContext(
            os_type=os_type,
            shell_type=shell_type,
            ai_mode=ai_mode,
            is_detected=is_detected,
            target_language=target_language,
            provider_type=provider_type,
            model_name=model_name,
        )

    def _setup_argument_parser(self) -> argparse.ArgumentParser:
        """Setup comprehensive argument parser."""
        parser = argparse.ArgumentParser(
            prog="aii",
            description="🧠 AI Intelligence: Multi-Modal AI Assistant",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
🌟 Examples:
  # Shell Commands (default mode)
  aii print hello world                    # Generate shell command (Google)
  aii --os mac install docker             # Force macOS mode
  aii -m -s fish list python files        # macOS + Fish shell

  # Multi-Provider Support 🆕
  aii --provider google translate "Hello" to Spanish    # Google Gemini (default)
  aii --provider anthropic explain "quantum physics"    # Anthropic Claude
  aii --provider openai code "Python web scraper"       # OpenAI GPT
  aii -p openai write "professional email"             # Short form

  # Model Selection 🆕
  aii --model gemini-2.0-flash "list files"            # Specific Google model
  aii --provider anthropic --model claude-3-5-sonnet-latest "write essay"
  aii --provider openai --model gpt-4o "explain AI"    # Specific OpenAI model

  # Translation Mode (natural syntax)
  aii translate "Hello world" to Spanish   # Natural language detection
  aii translate "Good morning" --to French # With explicit target language
  aii trans "Bonjour" to English          # Short form

  # Explain Mode (natural syntax)
  aii explain "How does Docker work?"      # Natural explanation
  aii explain "Machine learning algorithms" # Complex topics
  aii exp "Why is the sky blue?"           # Short form

  # Code Mode (natural syntax)
  aii code "Python function to sort list"  # Generate code
  aii code "Fix this JavaScript bug"       # Debug help
  aii coding "React component for login"   # Alternative form

  # Writing Mode (natural syntax)
  aii write "Professional email declining meeting" # Generate content
  aii write "Blog post intro about AI"     # Creative writing
  aii writing "Cover letter for dev role"  # Alternative form

  # Context Memory System 🆕
  aii --continue "Follow up on our previous discussion"          # Continue latest conversation
  aii --continue 20250916_220719_dbdcbd0c "What about performance?" # Continue specific conversation
  aii --clear-context "Start fresh conversation"                 # Clear context
  aii --show-history                                             # Show conversation history

🔧 Setup:
  export GEMINI_API_KEY=your_gemini_key       # Required for Google provider
  export ANTHROPIC_API_KEY=your_anthropic_key # Required for Anthropic provider
  export OPENAI_API_KEY=your_openai_key       # Required for OpenAI provider

🔗 More info: https://pypi.org/project/a2py
            """.strip(),
        )

        # Mode selection
        parser.add_argument(
            "--mode",
            choices=[mode.value for mode in AIMode],
            default="shell",
            help="AI operation mode (default: shell)",
        )

        # Mode shortcuts
        parser.add_argument(
            "--translate",
            "-t",
            action="store_const",
            const="translate",
            dest="mode",
            help="Translation mode shortcut",
        )

        parser.add_argument(
            "--explain",
            "-e",
            action="store_const",
            const="explain",
            dest="mode",
            help="Explanation mode shortcut",
        )

        parser.add_argument(
            "--code",
            "-c",
            action="store_const",
            const="code",
            dest="mode",
            help="Code generation mode shortcut",
        )

        parser.add_argument(
            "--write",
            "-w",
            action="store_const",
            const="write",
            dest="mode",
            help="Writing mode shortcut",
        )

        parser.add_argument(
            "--analyze",
            "-a",
            action="store_const",
            const="analyze",
            dest="mode",
            help="Directory analysis mode shortcut",
        )

        # Provider selection options
        parser.add_argument(
            "--provider",
            "-p",
            choices=[provider.value for provider in ProviderType],
            default="google",
            help="AI provider to use (default: google)",
        )

        parser.add_argument(
            "--model",
            help="Specific model to use (e.g., gemini-2.0-flash, claude-3-5-sonnet-latest)",
        )

        # Translation-specific options
        parser.add_argument(
            "--to", dest="target_language", help="Target language for translation mode"
        )

        # Shell-specific options (only relevant for shell mode)
        parser.add_argument(
            "--os",
            "-o",
            choices=[os.value for os in OSType if os != OSType.UNKNOWN],
            help="Override OS detection (mac/linux) - shell mode only",
        )

        parser.add_argument(
            "--shell",
            "-s",
            choices=[shell.value for shell in ShellType],
            help="Override shell detection - shell mode only",
        )

        parser.add_argument(
            "-m",
            "--mac",
            action="store_const",
            const="mac",
            dest="os",
            help="Shorthand for --os mac",
        )

        parser.add_argument(
            "-l",
            "--linux",
            action="store_const",
            const="linux",
            dest="os",
            help="Shorthand for --os linux",
        )

        # Context Memory options
        parser.add_argument(
            "--continue",
            nargs="?",
            const="latest",
            metavar="CONVERSATION_ID",
            help="Continue conversation with context memory. Use 'latest' (default) or specify conversation ID",
        )

        parser.add_argument(
            "--clear-context",
            action="store_true",
            help="Clear current conversation context and start fresh",
        )

        parser.add_argument(
            "--show-history",
            action="store_true",
            help="Show conversation history and exit",
        )

        # Directory Analysis options
        parser.add_argument(
            "--path",
            help="Directory path to analyze (default: current directory)",
        )

        parser.add_argument(
            "--summary",
            action="store_true",
            help="Generate project summary (analyze mode only)",
        )

        parser.add_argument(
            "--issues",
            action="store_true",
            help="Identify code issues and problems (analyze mode only)",
        )

        parser.add_argument(
            "--suggestions",
            action="store_true",
            help="Provide improvement suggestions (analyze mode only)",
        )

        parser.add_argument(
            "--architecture",
            action="store_true",
            help="Analyze project architecture (analyze mode only)",
        )

        # General options
        parser.add_argument(
            "--version",
            action="version",
            version=f"aii {__version__} - AI Intelligence Multi-Modal Assistant",
        )

        parser.add_argument(
            "prompt", nargs="*", help="Your request in natural language"
        )

        return parser

    def _detect_mode_from_prompt(
        self, prompt_words: list[str]
    ) -> tuple[str | None, list[str]]:
        """Detect mode from first word of prompt and return mode and remaining words."""
        if not prompt_words:
            return None, prompt_words

        # Handle case where prompt_words contains multi-word strings (from quotes)
        # Split the first element to get the actual first word
        first_element = prompt_words[0]
        if " " in first_element:
            # Split the first element into words
            words = first_element.split()
            first_word = words[0].lower()
            # Reconstruct the prompt_words with the split first element
            remaining_first_element = " ".join(words[1:]) if len(words) > 1 else ""
            reconstructed_prompt = []
            if remaining_first_element:
                reconstructed_prompt.append(remaining_first_element)
            reconstructed_prompt.extend(prompt_words[1:])
        else:
            first_word = first_element.lower()
            reconstructed_prompt = prompt_words[1:]

        mode_mapping = {
            "translate": "translate",
            "trans": "translate",
            "explain": "explain",
            "exp": "explain",
            "what": "explain",
            "what's": "explain",
            "what're": "explain",
            "why": "explain",
            "how": "explain",
            "when": "explain",
            "where": "explain",
            "who": "explain",
            "code": "code",
            "coding": "code",
            "implement": "code",
            "build": "code",
            "create": "code",
            "write": "write",
            "writing": "write",
            "analyze": "analyze",
            "analysis": "analyze",
            "review": "analyze",
            "audit": "analyze",
            "shell": "shell",
            "cmd": "shell",
            "command": "shell",
        }

        detected_mode = mode_mapping.get(first_word)
        if detected_mode:
            return detected_mode, reconstructed_prompt

        return None, prompt_words

    def run(self, args: list[str] | None = None) -> int:
        """Main application entry point."""
        parser = self._setup_argument_parser()
        parsed_args = parser.parse_args(args)

        # Handle context memory flags that don't require prompt
        if hasattr(parsed_args, "show_history") and parsed_args.show_history:
            self.context_memory.show_history()
            return 0

        if hasattr(parsed_args, "clear_context") and parsed_args.clear_context:
            self.context_memory.clear_current_conversation()
            print("🧹 Conversation context cleared - starting fresh!")
            if not parsed_args.prompt:  # If no prompt provided, just clear and exit
                return 0

        # Handle case where --continue argument might contain the prompt
        continue_arg = getattr(parsed_args, "continue", None)
        if continue_arg and continue_arg not in ["latest"] and not parsed_args.prompt:
            # The argument after --continue is likely the prompt, not a conversation ID
            # Check if it looks like a conversation ID (timestamp format)
            if not (
                len(continue_arg) >= 15
                and "_" in continue_arg
                and continue_arg.replace("_", "").replace("-", "").isalnum()
            ):
                # It's probably a prompt, not a conversation ID
                parsed_args.prompt = [continue_arg]
                setattr(parsed_args, "continue", "latest")

        # Check if we need a prompt for the remaining operations
        if not parsed_args.prompt:
            if hasattr(parsed_args, "continue") and getattr(
                parsed_args, "continue", False
            ):
                print(
                    "❌ Error: --continue requires a prompt to continue the conversation"
                )
                print('💡 Usage: aii --continue "your follow-up question"')
                print("📚 To see conversation history: aii --show-history")
            else:
                print("❌ Error: Please provide a prompt for AI processing")
            return 1

        # Initialize AI generator
        api_key = self._get_api_key()
        self.generator = AIGenerator(api_key, self.prompt_generator)

        # Detect mode from first word if not explicitly set
        prompt_words = parsed_args.prompt

        # Always try to detect mode from current prompt, even when continuing conversation
        detected_mode, remaining_words = self._detect_mode_from_prompt(prompt_words)

        if detected_mode and (not parsed_args.mode or parsed_args.mode == "shell"):
            parsed_args.mode = detected_mode
            prompt_words = remaining_words
        elif not parsed_args.mode:
            parsed_args.mode = "shell"  # Default mode

        # Handle translation mode language parsing
        prompt_text = " ".join(prompt_words)
        if parsed_args.mode == "translate" and not parsed_args.target_language:
            # Try to parse target language from prompt
            cleaned_prompt, detected_language = self._parse_target_language(prompt_text)
            if detected_language:
                prompt_text = cleaned_prompt
                parsed_args.target_language = detected_language

        # Create request context
        context = self._create_environment_context(parsed_args)

        # Handle conversation context
        conversation_id = None
        if hasattr(parsed_args, "continue") and getattr(parsed_args, "continue", False):
            # Continue specified conversation or latest
            target_conversation = getattr(parsed_args, "continue")

            if self.context_memory.continue_conversation(target_conversation):
                conversation_id = self.context_memory.get_current_conversation_id()
                if target_conversation == "latest":
                    print(f"🔄 Continuing latest conversation: {conversation_id}")
                else:
                    print(f"🔄 Continuing conversation: {target_conversation}")
            else:
                if target_conversation == "latest":
                    print(
                        "🔄 No previous conversation found - starting new conversation"
                    )
                else:
                    print(
                        f"❌ Conversation '{target_conversation}' not found - starting new conversation"
                    )
                conversation_id = self.context_memory.start_new_conversation()
        else:
            # Start new conversation (but don't announce it)
            conversation_id = self.context_memory.start_new_conversation()

        # Enhance request with conversation context
        enhanced_prompt = prompt_text
        if conversation_id:
            context_lines = self.context_memory.get_conversation_context(
                conversation_id
            )
            if context_lines:
                context_str = "\n".join(context_lines)
                enhanced_prompt = f"""Previous conversation context:
{context_str}

Current request: {prompt_text}

Please respond to the current request, taking into account the conversation history above."""

        request = AIRequest(prompt=enhanced_prompt, context=context)

        # Show context info
        print(f"🔍 Context: {context}")
        if hasattr(parsed_args, "continue") and getattr(parsed_args, "continue", False):
            context_lines = (
                self.context_memory.get_conversation_context(conversation_id)
                if conversation_id
                else []
            )
            if context_lines:
                print(f"💬 Using {len(context_lines)//2} previous messages for context")
        print(f"📝 Request: {prompt_text}\n")

        # Generate AI response
        response = self.generator.generate(request)

        # Save to conversation history
        if conversation_id and response.success:
            self.context_memory.add_message_to_conversation(
                conversation_id, prompt_text, response, context
            )

        # Display response
        self.response_handler.display_response(response)

        if not response.success:
            return 1

        # Handle execution ONLY for shell commands
        if response.mode == AIMode.SHELL and response.content:
            if self.response_handler.prompt_for_execution(response):
                return self.response_handler.execute_command(response.content)

        return 0


def main() -> int:
    """Application entry point."""
    try:
        app = AiiApplication()
        return app.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        return 130
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        return 1


def main_translate() -> int:
    """Entry point for aiit command (translation shortcut)."""
    try:
        # Insert -t at the beginning of arguments
        sys.argv.insert(1, "-t")
        app = AiiApplication()
        return app.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        return 130
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
