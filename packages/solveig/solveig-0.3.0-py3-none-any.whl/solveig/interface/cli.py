"""
CLI implementation of Solveig interface.
"""

import asyncio
import shutil
import sys
from collections import defaultdict
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import TYPE_CHECKING, Any

import solveig.utils.misc
from solveig.interface.base import SolveigInterface
from solveig.utils.file import Metadata

if TYPE_CHECKING:
    from solveig.schema import LLMMessage


class CLIInterface(SolveigInterface):
    """Command-line interface implementation."""

    DEFAULT_INPUT_PROMPT = "Reply:\n > "

    class TEXT_BOX:
        # Basic
        H = "─"
        V = "│"
        # Corners
        TL = "┌"  # top-left
        TR = "┐"  # top-right
        BL = "└"  # bottom-left
        BR = "┘"  # bottom-right
        # Junctions
        VL = "┤"
        VR = "├"
        HB = "┬"
        HT = "┴"
        # Cross
        X = "┼"

    def __init__(self, animation_interval: float = 0.1, **kwargs) -> None:
        super().__init__(**kwargs)
        self.animation_interval = animation_interval

    def _output(self, text: str) -> None:
        print(text)

    def _output_inline(self, text: str) -> None:
        sys.stdout.write(f"\r{text}")
        sys.stdout.flush()

    def _input(self, prompt: str) -> str:
        user_input = input(prompt)
        return user_input

    def _get_max_output_width(self) -> int:
        return shutil.get_terminal_size((80, 20)).columns

    def display_section(self, title: str) -> None:
        """
        Section header with line
        ─── User ───────────────
        """
        terminal_width = self._get_max_output_width()
        title_formatted = f"{self.TEXT_BOX.H * 3} {title} " if title else ""
        padding = (
            self.TEXT_BOX.H * (terminal_width - len(title_formatted))
            if terminal_width > 0
            else ""
        )
        self._output(f"\n{title_formatted}{padding}")

    def display_llm_response(self, llm_response: "LLMMessage") -> None:
        """Display the LLM response and requirements summary."""
        if llm_response.comment:
            self.display_comment(llm_response.comment.strip())

        if llm_response.requirements:
            with self.with_group("Requirements", len(llm_response.requirements)):
                indexed_requirements = defaultdict(list)
                for requirement in llm_response.requirements:
                    indexed_requirements[requirement.title].append(requirement)

                for requirement_type, requirements in indexed_requirements.items():
                    with self.with_group(
                        requirement_type.title(), count=len(requirements)
                    ):
                        for requirement in requirements:
                            requirement.display_header(interface=self)

    # display_requirement removed - requirements now display themselves directly

    def display_tree(
        self,
        metadata: Metadata,
        level: int | None = None,
        max_lines: int | None = None,
        title: str | None = None,
        display_metadata: bool = False,
    ) -> None:
        self.display_text_block(
            "\n".join(self._get_tree_element_str(metadata, display_metadata)),
            title=title or str(metadata.path),
            level=level,
            max_lines=max_lines,
        )

    def _get_tree_element_str(
        self, metadata: Metadata, display_metadata: bool = False, indent="  "
    ) -> list[str]:
        line = f"{'🗁 ' if metadata.is_directory else '🗎'} {metadata.path.name}"
        if display_metadata:
            if not metadata.is_directory:
                size_str = solveig.utils.misc.convert_size_to_human_readable(
                    metadata.size
                )
                line = f"{line}  |  size: {size_str}"
            modified_time = datetime.fromtimestamp(
                float(metadata.modified_time)
            ).isoformat()
            line = f"{line}  |  modified: {modified_time}"
        lines = [line]

        if metadata.is_directory and metadata.listing:
            for index, (_sub_path, sub_metadata) in enumerate(
                sorted(metadata.listing.items())
            ):
                is_last = index == len(metadata.listing) - 1
                entry_lines = self._get_tree_element_str(sub_metadata, indent=indent)

                # ├─🗁 d1                                                                                                                │
                lines.append(
                    f"{indent}{self.TEXT_BOX.BL if is_last else self.TEXT_BOX.VR}{self.TEXT_BOX.H}{entry_lines[0]}"
                )

                # │  ├─🗁 sub-d1
                # │  └─🗎 sub-f1
                for sub_entry in entry_lines[1:]:
                    lines.append(
                        f"{indent}{'' if is_last else self.TEXT_BOX.V}{sub_entry}"
                    )

        return lines

    def display_text_block(
        self,
        text: str,
        title: str | None = None,
        level: int | None = None,
        max_lines: int | None = None,
    ) -> None:
        if not self.max_lines or not text:
            return

        indent = self._indent(level)
        max_width = self._get_max_output_width()

        # ┌─── Content ─────────────────────────────┐
        top_bar = f"{indent}{self.TEXT_BOX.TL}"
        if title:
            top_bar = f"{top_bar}{self.TEXT_BOX.H * 3} {title} "
        self._output(
            f"{top_bar}{self.TEXT_BOX.H * (max_width - len(top_bar) - 2)}{self.TEXT_BOX.TR} "
        )

        vertical_bar_left = f"{indent}{self.TEXT_BOX.V} "
        vertical_bar_right = f" {self.TEXT_BOX.V} "
        max_line_length = (
            self._get_max_output_width()
            - len(vertical_bar_left)
            - len(vertical_bar_right)
        )

        lines = text.splitlines()
        for line_no, line in enumerate(lines):
            # truncate number of lines
            if line_no == self.max_lines:
                lines_missing = len(lines) - line_no
                truncated_line = f" ({lines_missing} more...)"
                truncated_line = (
                    f"{truncated_line}{' ' * (max_line_length - len(truncated_line))}"
                )
                self._output(f"{vertical_bar_left}{truncated_line}{vertical_bar_right}")
                break

            if len(line) > max_line_length:
                truncated_line = f"{line[0:max_line_length - 3]}..."
            else:
                truncated_line = f"{line}{' ' * (max_line_length - len(line))}"
            self._output(f"{vertical_bar_left}{truncated_line}{vertical_bar_right}")

        # └─────────────────────────────────────────┘
        self._output(
            f"{indent}{self.TEXT_BOX.BL}{self.TEXT_BOX.H * (max_width - len(indent) - 3)}{self.TEXT_BOX.BR} "
        )

    def display_animation_while(
        self, run_this: Callable, message: str | None = None
    ) -> None:
        animation = Animation()
        return asyncio.run(animation.animate_while(self, run_this, message))


class Animation:
    SPINNERS = {
        "dots": ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
        "line": ["|", "/", "-", "\\"],
        "bounce": ["⠁", "⠂", "⠄", "⠂"],
        "pulse": ["●", "○", "●", "○"],
        "thinking": ["🤔", "💭", "🧠", "✨"],
        "processing": ["⚡", "⚡", "⚡", "✨"],
    }

    def __init__(
        self,
        animation_type: str | None = "dots",
        frames: list[str] | None = None,
        interval: float = 0.1,
    ):
        """
        Initialize async spinner.

        Args:
            frames: List of icon frames to cycle through
            interval: Time between frame changes in seconds
        """
        self.frames = frames or self.SPINNERS[animation_type or "dots"]
        self.interval = interval
        self._current_frame = 0
        self._task: asyncio.Task | None = None
        self._stopped = False

    async def start(self, interface: CLIInterface, message: str) -> None:
        """Start the animation."""
        if self._task is None:
            self._task = asyncio.create_task(self._animate(interface, message))
        else:
            interface.display_error(
                "Interface error: Tried to start animation while previous one was not cancelled"
            )

    async def stop(self, completion_message: str = "✅ Done"):
        """Stop the animation and show completion message."""
        self._stopped = True
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def _animate(
        self, interface: CLIInterface, message: str | None = None
    ) -> None:
        """Run the animation loop."""
        while not self._stopped:
            # Show current frame with message
            frame = self.frames[self._current_frame]
            display_text = f"{frame} {message}" if message else frame
            interface._output_inline(display_text)

            # Advance to next frame
            self._current_frame = (self._current_frame + 1) % len(self.frames)

            # Wait for next frame
            await asyncio.sleep(self.interval)

    async def animate_while(
        self,
        interface: CLIInterface,
        run_this: Callable,
        message: str | None = None,
    ) -> Any:
        """
        Run a blocking function in a thread while showing an animated spinner.

        Args:
            interface: The CLIInterface instance to use for displaying information
            run_this: Function to run while animation plays
            message: Message to show with spinner

        Returns:
            Result from the blocking function
        """
        # Start spinner
        await self.start(interface, message or "")

        try:
            # Run blocking function in thread pool
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                result = await loop.run_in_executor(executor, run_this)

            # Stop spinner with success message
            await self.stop()
            return result

        finally:
            interface.show("")
            await self.stop()
