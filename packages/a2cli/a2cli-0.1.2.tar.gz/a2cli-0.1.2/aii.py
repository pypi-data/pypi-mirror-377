#!/usr/bin/env python3
"""
aii - AI Intelligence: Multi-Modal AI Assistant

A powerful multi-modal AI assistant that serves as your intelligent companion for
translation, explanation, coding, writing, and shell automation - all powered by Google Gemini AI.

Features:
- Multi-Modal AI: Supports 5 different AI modes (shell, translate, explain, code, write)
- Natural Language Interface: Use intuitive commands like `aii translate "hello" to Spanish`
- Smart Environment Detection: Auto-detects your OS (macOS/Linux) and shell (bash, zsh, fish, etc.)
- Context-Aware: Provides culturally appropriate translations and OS-specific commands
- Safe Execution: Only prompts for execution on shell commands, not explanations or translations
- High-Quality Output: Shows confidence levels and provides detailed reasoning
- Secure: Uses environment variables for API keys with helpful setup guidance
"""

from __future__ import annotations

import argparse
import os
import platform
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Protocol

try:
    from typing import assert_never  # Python 3.11+
except ImportError:
    from typing_extensions import assert_never  # Python 3.10  # noqa: UP035

from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel

# Version information - dynamically loaded from package metadata
try:
    from importlib.metadata import version

    __version__ = version("a2cli")
except ImportError:
    # Fallback for Python < 3.8
    from importlib_metadata import version

    __version__ = version("a2cli")
except Exception:
    # Fallback if package not installed
    __version__ = "unknown"
from pydantic_ai.providers.google import GoogleProvider


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


@dataclass(frozen=True)
class EnvironmentContext:
    """Immutable context about the user's environment."""

    os_type: OSType
    shell_type: ShellType
    ai_mode: AIMode
    is_detected: bool = True
    confidence: float = 1.0
    target_language: str | None = None

    def __str__(self) -> str:
        if self.ai_mode == AIMode.SHELL:
            status = "detected" if self.is_detected else "overridden"
            return f"{self.os_type.value}/{self.shell_type.value} ({status})"
        elif self.ai_mode == AIMode.TRANSLATE and self.target_language:
            return f"translate to {self.target_language}"
        else:
            return f"{self.ai_mode.value} mode"


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

        # All enum values should be covered above
        raise ValueError(f"Unsupported AI mode: {context.ai_mode}")


class AIGenerator:
    """Main class for AI-powered content generation across multiple modes."""

    def __init__(self, api_key: str, prompt_generator: PromptGenerator):
        self.api_key = api_key
        self.prompt_generator = prompt_generator
        self._agents: dict[str, Agent[Any, AIResponse]] = {}

    def _get_agent(self, context: EnvironmentContext) -> Agent[Any, AIResponse]:
        """Get or create agent for specific environment context."""
        # Create cache key based on mode and relevant context
        if context.ai_mode == AIMode.SHELL:
            cache_key = f"shell_{context.os_type.value}_{context.shell_type.value}"
        elif context.ai_mode == AIMode.TRANSLATE:
            cache_key = f"translate_{context.target_language or 'auto'}"
        else:
            cache_key = f"{context.ai_mode.value}_general"

        if cache_key not in self._agents:
            provider = GoogleProvider(api_key=self.api_key)
            system_prompt = self.prompt_generator.generate_system_prompt(context)

            agent = Agent(
                model=GoogleModel("gemini-2.0-flash", provider=provider),
                system_prompt=system_prompt,
                output_type=AIResponse,
            )

            self._setup_agent_tools(agent, context.ai_mode)
            self._agents[cache_key] = agent

        return self._agents[cache_key]

    def _setup_agent_tools(self, agent: Agent[Any, AIResponse], mode: AIMode) -> None:
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

        return EnvironmentContext(
            os_type=os_type,
            shell_type=shell_type,
            ai_mode=ai_mode,
            is_detected=is_detected,
            target_language=target_language,
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
  aii print hello world                    # Generate shell command
  aii --os mac install docker             # Force macOS mode
  aii -m -s fish list python files        # macOS + Fish shell

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

🔗 More info: https://github.com/ttware/aii
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

        # General options
        parser.add_argument(
            "--version",
            action="version",
            version=f"aii {__version__} - AI Intelligence Multi-Modal Assistant",
        )

        parser.add_argument(
            "prompt", nargs="+", help="Your request in natural language"
        )

        return parser

    def _detect_mode_from_prompt(
        self, prompt_words: list[str]
    ) -> tuple[str | None, list[str]]:
        """Detect mode from first word of prompt and return mode and remaining words."""
        if not prompt_words:
            return None, prompt_words

        first_word = prompt_words[0].lower()
        mode_mapping = {
            "translate": "translate",
            "trans": "translate",
            "explain": "explain",
            "exp": "explain",
            "code": "code",
            "coding": "code",
            "write": "write",
            "writing": "write",
            "shell": "shell",
            "cmd": "shell",
            "command": "shell",
        }

        detected_mode = mode_mapping.get(first_word)
        if detected_mode:
            return detected_mode, prompt_words[1:]  # Remove the mode word

        return None, prompt_words

    def run(self, args: list[str] | None = None) -> int:
        """Main application entry point."""
        parser = self._setup_argument_parser()
        parsed_args = parser.parse_args(args)

        # Initialize AI generator
        api_key = self._get_api_key()
        self.generator = AIGenerator(api_key, self.prompt_generator)

        # Detect mode from first word if not explicitly set
        prompt_words = parsed_args.prompt
        if not parsed_args.mode or parsed_args.mode == "shell":
            detected_mode, remaining_words = self._detect_mode_from_prompt(prompt_words)
            if detected_mode:
                parsed_args.mode = detected_mode
                prompt_words = remaining_words

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
        request = AIRequest(prompt=prompt_text, context=context)

        # Show context info
        print(f"🔍 Context: {context}")
        print(f"📝 Request: {request.sanitized_prompt}\n")

        # Generate AI response
        response = self.generator.generate(request)

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
