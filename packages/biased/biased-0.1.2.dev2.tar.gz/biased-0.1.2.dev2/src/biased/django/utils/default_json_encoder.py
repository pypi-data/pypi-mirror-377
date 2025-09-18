from datetime import datetime
from decimal import Decimal
from enum import Enum

from django.core.serializers.json import DjangoJSONEncoder
from plaid.model_utils import ModelNormal
from pydantic import AnyUrl, BaseModel
from structlog.processors import _json_fallback_handler
from ulid import ULID


class DefaultJsonEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat().replace("+00:00", "Z")
        if isinstance(o, Decimal):
            return str(o)
        if isinstance(o, ULID):
            return o.str
        if isinstance(o, AnyUrl):
            return str(o)
        if isinstance(o, BaseModel):
            return o.model_dump()
        if isinstance(o, Enum):
            return o.value
        if isinstance(o, bytes):
            return o.decode()
        if isinstance(o, ModelNormal):
            return o.to_dict()
        return super().default(o)


class StructlogJsonEncoder(DefaultJsonEncoder):
    def default(self, o):
        try:
            return super().default(o)
        except TypeError:
            return _json_fallback_handler(o)
