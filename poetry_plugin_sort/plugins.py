from __future__ import annotations

from typing import Type

from cleo.events import console_events
from cleo.events.console_terminate_event import ConsoleTerminateEvent
from cleo.events.event import Event
from cleo.events.event_dispatcher import EventDispatcher
from cleo.helpers import option
from cleo.io.io import IO
from poetry.console.application import Application
from poetry.console.commands.add import AddCommand
from poetry.console.commands.command import Command
from poetry.console.commands.init import InitCommand
from poetry.plugins.application_plugin import ApplicationPlugin

from poetry_plugin_sort import config
from poetry_plugin_sort.sort import Sorter


class SortCommand(Command):
    name = "sort"
    description = "Sorts the dependencies in pyproject.toml"
    options = [
        option(
            "check", flag=True, description="Don't sort, just check if already sorted."
        )
    ]

    def handle(self) -> int:
        sorter = Sorter(self.poetry, self.io, check=self.option("check"))
        return 0 if sorter.sort() else 1


class SortDependenciesPlugin(ApplicationPlugin):
    """Sorts dependencies in pyproject.toml file"""

    @property
    def commands(self) -> list[Type[Command]]:
        return [SortCommand]

    def activate(self, application: Application) -> None:
        application.event_dispatcher.add_listener(  # type: ignore[union-attr]
            console_events.TERMINATE, self.sort_dependencies
        )
        super().activate(application)

    def sort_dependencies(
        self, event: Event, event_name: str, dispatcher: EventDispatcher
    ) -> None:
        assert isinstance(event, ConsoleTerminateEvent)

        io = event.io
        command = event.command

        if event.exit_code != 0:
            self._write_debug_lines(
                io, "Skip sorting dependencies due to non-zero exit code."
            )
            return

        if not isinstance(command, (InitCommand, AddCommand)):
            self._write_debug_lines(
                io,
                f"Skip sorting dependencies due to {command} does not change the"
                " state.",
            )
            return

        if command.option("dry-run", False):
            self._write_debug_lines(
                io, "Skip sorting dependencies due to --dry-run option."
            )
            return

        if not config.is_sorting_enabled(command.poetry):
            self._write_debug_lines(
                io, "Skip sorting dependencies due to disabled sorting."
            )
            return

        sorter = Sorter(command.poetry, io)
        sorter.sort()

    def _write_debug_lines(self, io: IO, message: str) -> None:
        if io.is_debug():
            io.write_line(message)
