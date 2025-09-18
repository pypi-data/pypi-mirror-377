
from .base import BaseFormatter
from .template import IMessageTemplate, MessageTemplate
from logging import LogRecord
from typing import Optional

class BasicFormatter(BaseFormatter[str]):
    def __init__(self, template:Optional[str|IMessageTemplate] = "${message}"):
        super().__init__(template)


    def format(self, record: LogRecord) -> str:
        if self.template:
            return self.template.render(record)
        return record.getMessage()
