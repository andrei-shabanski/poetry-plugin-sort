from cleo.events import console_events
from cleo.events.console_command_event import ConsoleCommandEvent
from cleo.events.event_dispatcher import EventDispatcher
from cleo.io.io import IO
from poetry.console.application import Application
from poetry.console.commands.add import AddCommand
from poetry.console.commands.init import InitCommand
from poetry.console.commands.remove import RemoveCommand
from poetry.plugins.application_plugin import ApplicationPlugin

from poetry_plugin_sort.sort import Sorter


class SortDependenciesPlugin(ApplicationPlugin):
    """Sorts dependencies in pyproject.toml file"""

    def activate(self, application: Application):
        application.event_dispatcher.add_listener(
            console_events.TERMINATE, self.sort_dependencies
        )

    def sort_dependencies(
        self, event: ConsoleCommandEvent, event_name: str, dispatcher: EventDispatcher
    ) -> None:
        io = event.io
        command = event.command

        if event.exit_code != 0:
            self._write_debug_lines(
                io, "Skip sorting dependencies due to non-zero exit code."
            )
            return

        if not isinstance(command, (InitCommand, AddCommand, RemoveCommand)):
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

        sorter = Sorter(event.command.poetry, io)
        sorter.sort()

    def _write_debug_lines(self, io: IO, message: str) -> None:
        if io.is_debug():
            io.write_line(message)