from __future__ import annotations

from typing import List, Callable, Any, Optional, Tuple, Dict

from ..exceptions import InstantiationError


class EventDispatcher(object):
    """Class implementing an event dispatcher for custom events."""
    __slots__ = ['events']

    __instance: EventDispatcher = None

    @staticmethod
    def get_instance() -> EventDispatcher:
        """Get an instance of the Dispatcher.

        Returns:
            EventDispatcher: An instance of the class.

        Raises:
            InstantiationError: If two instances of the class are created.
        """
        if EventDispatcher.__instance is None:
            EventDispatcher()

        return EventDispatcher.__instance

    def __init__(self) -> None:
        if EventDispatcher.__instance is not None:
            raise InstantiationError("This class is a singleton!")
        else:
            self.events: Dict[str, List[Tuple[Callable, Optional[Callable]]]] = {}

            EventDispatcher.__instance = self

    def get_subscribers(self, event: str) -> List[Callable]:
        """Return subscribers of a given event.

        Args:
            event (str): Name of the event.

        Returns:
            List[Callable]: Subscribed callbacks for the event.
        """
        return [run_callback for (run_callback, _) in self.events[event]]

    def register(self, event: str, obj: Any, method: Optional[str] = None) -> None:
        """Register a subscriber for a given event. Subscriber is composed of a class instance and
        an optional method name. If method name is not provided, by default the `run` method is searched.
        It also checks if the `unregister` method is present in the object, that is called during event unregistration.

        Args:
            event (str): Name of the event.
            obj (Any): instance of a class of a subscriber.
            method (Optional[str]): method name of the subscriber to run as callback. If method name is not provided,
                by default the `run` method is searched.

        Returns:
            None
        """
        if event not in self.events:
            self.events[event] = []

        self.events[event].append(
            (
                getattr(obj, 'run' if not method else method),
                getattr(obj, 'unregister') if hasattr(obj, 'unregister') else None
            )
        )

    def dispatch(self, event: str, **kwargs) -> None:
        """Dispatch a given event.

        Args:
            event (str): Name of the event.
            kwargs: Arguments to pass to the event callback.

        Returns:
            None
        """
        if event not in self.events:
            return

        for (run_callback, _) in self.events[event]:
            run_callback(**kwargs)

    def unregister(self, event: str) -> None:
        """Unregister all callbacks of a given event.

        Args:
            event (str): Name of the event.

        Returns:
            None
        """
        if event not in self.events:
            return

        for (_, unregister_callback) in self.events[event]:
            if unregister_callback:
                unregister_callback()

        del self.events[event]
