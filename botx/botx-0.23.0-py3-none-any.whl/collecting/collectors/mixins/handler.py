"""Definition for mixin with handler decorator."""
from functools import partial
from typing import Any, Callable, List, Optional, Sequence, Union, cast

from botx import converters
from botx.dependencies.models import Depends

try:
    from typing import Protocol  # noqa: WPS433
except ImportError:
    from typing_extensions import Protocol  # type: ignore  # noqa: WPS433, WPS440, F401


class AddHandlerProtocol(Protocol):
    """Protocol for definition add_handler method."""

    def add_handler(  # noqa: WPS211
        self,
        handler: Callable,
        *,
        body: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        full_description: Optional[str] = None,
        include_in_status: Union[bool, Callable] = True,
        dependencies: Optional[Sequence[Depends]] = None,
        dependency_overrides_provider: Any = None,
    ) -> None:
        """Create new handler from passed arguments and store it inside."""


class HandlerDecoratorProtocol(Protocol):
    """Protocol for definition handler decorator."""

    def handler(  # noqa: WPS211
        self,
        handler: Optional[Callable] = None,
        *,
        command: Optional[str] = None,
        commands: Optional[Sequence[str]] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        full_description: Optional[str] = None,
        include_in_status: Union[bool, Callable] = True,
        dependencies: Optional[Sequence[Depends]] = None,
        dependency_overrides_provider: Any = None,
    ) -> Callable:
        """Add new handler to collector."""


class HandlerMixin:
    """Mixin that defines handler decorator."""

    def handler(  # noqa: WPS211
        self: AddHandlerProtocol,
        handler: Optional[Callable] = None,
        *,
        command: Optional[str] = None,
        commands: Optional[Sequence[str]] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        full_description: Optional[str] = None,
        include_in_status: Union[bool, Callable] = True,
        dependencies: Optional[Sequence[Depends]] = None,
        dependency_overrides_provider: Any = None,
    ) -> Callable:
        """Add new handler to collector.

        !!! info
            If `include_in_status` is a function, then `body` argument will be checked
            for matching public commands style, like `/command`.

        Arguments:
            handler: callable that will be used for executing handler.
            command: body template that will trigger this handler.
            commands: list of body templates that will trigger this handler.
            name: optional name for handler that will be used in generating body.
            description: description for command that will be shown in bot's menu.
            full_description: full description that can be used for example in `/help`
                command.
            include_in_status: should this handler be shown in bot's menu, can be
                callable function with no arguments *(for now)*.
            dependencies: sequence of dependencies that should be executed before
                handler.
            dependency_overrides_provider: mock of callable for handler.

        Returns:
            Passed in `handler` callable.
        """
        if handler:
            handler_commands: List[
                Optional[str]
            ] = converters.optional_sequence_to_list(commands)

            if command and commands:
                handler_commands.insert(0, command)
            elif not commands:
                handler_commands = [command]

            for command_body in handler_commands:
                self.add_handler(
                    body=command_body,
                    handler=handler,
                    name=name,
                    description=description,
                    full_description=full_description,
                    include_in_status=include_in_status,
                    dependencies=dependencies,
                    dependency_overrides_provider=dependency_overrides_provider,
                )

            return handler

        return partial(
            cast(HandlerDecoratorProtocol, self).handler,
            command=command,
            commands=commands,
            name=name,
            description=description,
            full_description=full_description,
            include_in_status=include_in_status,
            dependencies=dependencies,
            dependency_overrides_provider=dependency_overrides_provider,
        )
