from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List, Optional, Union

from .filters import (
    AndFilter,
    BaseFilter,
    CommandFilter,
    PayloadFilter,
    StateFilter,
    TextFilter,
    LambdaFilter,
)
from ..magic import MagicFilter
from ..types import VKEvent


FilterLike = Union[
    BaseFilter,
    MagicFilter,
    Callable[[VKEvent, Dict[str, Any]], Awaitable[bool]],
]


@dataclass
class Handler:
    callback: Callable[..., Any]
    filters: List[BaseFilter] = field(default_factory=list)


class Router:
    def __init__(self):
        self.handlers: List[Handler] = []

    def message(
        self,
        *filters: FilterLike,
        text: Union[str, List[str], None] = None,
        command: Union[str, List[str], None] = None,
        state: Any = None,
        payload: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Callable:
        resolved_filters = [self._normalize_filter(f) for f in filters]

        if text is not None:
            ignore_case = kwargs.get("ignore_case", True)
            resolved_filters.append(TextFilter(text, ignore_case=ignore_case))
        if command is not None:
            prefix = kwargs.get("prefix", "/")
            resolved_filters.append(CommandFilter(command, prefix=prefix))
        if state is not None:
            resolved_filters.append(StateFilter(state))
        if payload is not None:
            resolved_filters.append(PayloadFilter(payload))

        def decorator(callback: Callable[..., Any]) -> Callable[..., Any]:
            handler = Handler(callback=callback, filters=[AndFilter(*resolved_filters)])
            self.handlers.append(handler)
            return callback

        return decorator

    def callback(
        self,
        *filters: FilterLike,
        state: Any = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Callable:
        resolved_filters = [self._normalize_filter(f) for f in filters]

        if state is not None:
            resolved_filters.append(StateFilter(state))
        if payload is not None:
            resolved_filters.append(PayloadFilter(payload))

        def decorator(callback: Callable[..., Any]) -> Callable[..., Any]:
            handler = Handler(callback=callback, filters=[AndFilter(*resolved_filters)])
            self.handlers.append(handler)
            return callback

        return decorator

    def include_router(self, router: "Router") -> None:
        """Включает все обработчики из другого роутера в текущий."""
        self.handlers.extend(router.handlers)

    @staticmethod
    def _normalize_filter(f: FilterLike) -> BaseFilter:
        if isinstance(f, BaseFilter):
            return f
        if isinstance(f, MagicFilter):
            return f
        if callable(f):
            return LambdaFilter(f)
        raise TypeError(f"Unsupported filter type: {type(f)}")
