from typing import Any, Callable, Dict, List

from .keyboard import Button, KeyboardBuilder


class Paginator:
    """
    Утилита для создания клавиатур с пагинацией, автоматически соблюдая лимиты VK API
    для inline-клавиатур (не более 10 кнопок, не более 6 рядов).
    """

    MAX_BUTTONS_TOTAL = 10
    MAX_ROWS_TOTAL = 6
    MAX_BUTTONS_PER_ROW = 5


    def __init__(
            self,
            builder: KeyboardBuilder,
            items: List[Any],
            formatter: Callable[[Any], Dict],
            page: int = 1,
            items_per_page: int = 5,
            buttons_per_row: int = 1,
    ):
        if not builder.inline:
            raise ValueError("Paginator can only be used with inline keyboards.")

        self.builder = builder
        self.items = items
        self.formatter = formatter

        self.max_control_buttons = 3
        self.max_rows_for_items = self.MAX_ROWS_TOTAL - 1

        self.buttons_per_row = min(buttons_per_row, self.MAX_BUTTONS_PER_ROW)

        max_items_by_rows = self.max_rows_for_items * self.buttons_per_row
        max_items_by_total_buttons = self.MAX_BUTTONS_TOTAL - self.max_control_buttons

        self.items_per_page = min(items_per_page, max_items_by_rows, max_items_by_total_buttons)


        self.total_items = len(items)
        self.total_pages = (self.total_items + self.items_per_page - 1) // self.items_per_page
        self.page = max(1, min(page, self.total_pages))

    def _get_page_items(self) -> List[Any]:
        """Возвращает срез элементов для текущей страницы."""
        start = (self.page - 1) * self.items_per_page
        end = start + self.items_per_page
        return self.items[start:end]

    def add_items(self) -> "Paginator":
        """Добавляет кнопки элементов текущей страницы в клавиатуру."""
        page_items = self._get_page_items()

        if not page_items:
            return self

        self.builder.new_row_if_needed()

        for i, item in enumerate(page_items):
            button = self.formatter(item)
            self.builder.add(button)
            if (i + 1) % self.buttons_per_row == 0 and (i + 1) < len(page_items):
                self.builder.row()
        return self

    def add_controls(self, base_payload: Dict) -> "Paginator":
        """Добавляет кнопки 'Назад' и 'Вперед'."""
        self.builder.new_row_if_needed()

        control_buttons = []
        if self.page > 1:
            prev_payload = base_payload.copy()
            prev_payload["page"] = self.page - 1
            control_buttons.append(Button.callback("⬅️ Назад", payload=prev_payload))

        if self.total_pages > 1:
            control_buttons.append(Button.callback(f"{self.page}/{self.total_pages}", payload={"cmd": "ignore"}))

        if self.page < self.total_pages:
            next_payload = base_payload.copy()
            next_payload["page"] = self.page + 1
            control_buttons.append(Button.callback("Вперед ➡️", payload=next_payload))

        if control_buttons:
            self.builder.add(*control_buttons)

        return self

    def build(self, base_payload: Dict) -> "Paginator":
        """Строит полный блок пагинации (элементы + кнопки управления)."""
        self.add_items()
        self.add_controls(base_payload)
        return self