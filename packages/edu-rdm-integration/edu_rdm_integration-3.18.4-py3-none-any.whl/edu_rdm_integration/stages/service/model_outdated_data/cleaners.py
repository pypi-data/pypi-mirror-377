from abc import (
    ABCMeta,
    abstractmethod,
)
from typing import (
    TYPE_CHECKING,
)


if TYPE_CHECKING:
    from m3_db_utils.models import (
        ModelEnumValue,
    )


class BaseModelOutdatedDataCleaner(metaclass=ABCMeta):
    """Базовый класс уборщика устаревших данных моделей РВД."""

    def __init__(
        self,
        model_enum_value: 'ModelEnumValue',
        *args,
        safe: bool = False,
        log_sql: bool = False,
        **kwargs,
    ):
        self._model_enum_value = model_enum_value
        self._safe = safe
        self._log_sql = log_sql

        super().__init__(*args, **kwargs)

    @abstractmethod
    def run(self):
        """Запуск очистки устаревших данных."""
