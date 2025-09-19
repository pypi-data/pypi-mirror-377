from typing import Union, Callable, Any, Iterable, Optional, Mapping

from magic_filter import MagicFilter

from textcompose.containers.base import Container
from textcompose.core import Value, Condition


class List(Container):
    def __init__(
        self,
        *items: Value,
        getter: Union[MagicFilter, Callable[[Mapping[str, Any]], Iterable]],
        sep: Optional[str] = "\n\n",
        inner_sep: str = "\n",
        when: Condition | None = None,
    ) -> None:
        super().__init__(*items, when=when)
        self.items = items
        self.getter = getter
        self.sep = sep
        self.inner_sep = inner_sep

    def _render_item(self, context: Mapping[str, Any], **kwargs) -> str | None:
        rendered_parts = [self.resolve(item_tpl, context, **kwargs) for i, item_tpl in enumerate(self.items)]
        return self.inner_sep.join(filter(None, rendered_parts)) or None

    def render(self, context, **kwargs) -> str | None:
        if not self._check_when(context, **kwargs):
            return None

        items_iterable = self.resolve(self.getter, context, **kwargs)
        if not items_iterable:
            return None

        rendered_items = [
            self._render_item({"item": item_value, "context": getattr(context, "context", context), "i": i}, **kwargs)
            for i, item_value in enumerate(items_iterable)
        ]

        return self.sep.join(filter(None, rendered_items)) or None
