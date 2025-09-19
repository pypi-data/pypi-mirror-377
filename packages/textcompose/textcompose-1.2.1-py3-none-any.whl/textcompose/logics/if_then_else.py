from typing import Optional

from textcompose.core import Condition, Value
from textcompose.logics.base import Logic


class If(Logic):
    def __init__(
        self,
        if_: Condition,
        then_: Optional[Value] = None,
        else_: Optional[Value] = None,
        when: Condition | None = None,
    ):
        super().__init__(when=when)
        self.if_ = if_
        self.then_ = then_
        self.else_ = else_

    def render(self, context, **kwargs) -> Optional[str]:
        if not self._check_when(context, **kwargs):
            return None

        if bool(self.resolve(value=self.if_, context=context, **kwargs)):
            return self.resolve(self.then_, context, **kwargs)
        return self.resolve(self.else_, context, **kwargs)
