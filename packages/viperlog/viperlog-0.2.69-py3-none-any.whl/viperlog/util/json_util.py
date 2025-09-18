
import json, dataclasses, datetime, enum, pathlib, uuid

def to_jsonable(o):
    if isinstance(o, (str, int, float, bool)) or o is None:
        return o
    if isinstance(o, (datetime.datetime, datetime.date, datetime.time)):
        return o.isoformat()
    if isinstance(o, enum.Enum):
        return o.value
    if dataclasses.is_dataclass(o):
        return dataclasses.asdict(o)
    for attr in ("model_dump", "dict", "__json__", "to_dict", "as_dict"):
        if hasattr(o, attr):
            try:
                return getattr(o, attr)()
            except Exception:
                pass
    if isinstance(o, (set, frozenset, tuple, list)):
        return [to_jsonable(i) for i in o]
    if isinstance(o, dict):
        return {str(k): to_jsonable(v) for k, v in o.items()}
    if isinstance(o, (pathlib.Path, uuid.UUID)):
        return str(o)
    return repr(o)  # last resort

def json_dumps(o):
    return json.dumps(o,  default=to_jsonable, ensure_ascii=False)