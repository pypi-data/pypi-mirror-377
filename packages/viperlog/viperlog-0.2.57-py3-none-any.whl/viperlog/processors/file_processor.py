from io import TextIOWrapper
from viperlog.util.json_util import json_dumps
from viperlog.formatters.basic import BasicFormatter
from viperlog.formatters.base import IFormatter
from viperlog.processors import GenericProcessor
from typing import Dict, Any, Optional, List
#import json


class FileProcessor(GenericProcessor[Any]):

    def __init__(self, file:str, formatter:Optional[IFormatter[Any]]=BasicFormatter(), lazy_open:bool=False, auto_flush_message_count:int=50):
        """
        Logs to a file,
        Output of the formatter is expected to be either a string or an dict (which will be dumped as json)
        """
        super().__init__(formatter)
        self._records_since_flush:int = 0
        self._auto_flush_message_count = auto_flush_message_count
        self._file = file
        self._stream:Optional[TextIOWrapper] = None if lazy_open else open(self._get_filename(), "a")

    def _get_filename(self) -> str:
        return self._file

    def _get_stream(self):
        if not self._stream:
            self._stream = open(self._get_filename(), "a")
        return self._stream


    def process_messages(self, records: List[Any]) -> None:
        if len(records) > 0:
            if not isinstance(records[0], str):
                records = [json_dumps(x) + '\n' for x in records]
            stream = self._get_stream()
            stream.writelines(records)
            # check flush
            self._records_since_flush += len(records)
            if self._records_since_flush >= self._auto_flush_message_count:
                self._records_since_flush = 0
                stream.flush()
