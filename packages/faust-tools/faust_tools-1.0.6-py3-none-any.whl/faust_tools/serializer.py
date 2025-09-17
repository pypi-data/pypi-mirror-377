from collections.abc import Mapping

import faust
from faust.types.models import ModelT


class StreamSerializer(faust.Record):
    """
    Main Stream Serializer
    """

    id: str
    action: str
    detail: dict | None = None

    @classmethod
    def from_data(
        cls, data: Mapping, *, preferred_type: type[ModelT] | None = None
    ) -> faust.Record:
        attribute_type = preferred_type.__annotations__
        record = super().from_data(data, preferred_type=preferred_type)
        if record.detail and "detail" in attribute_type:
            detail_type = attribute_type["detail"]
            if (
                isinstance(record.detail, list)
                and hasattr(detail_type, "__args__")
                and getattr(detail_type.__args__[0], "_auto_assign", None)
            ):
                for index, value in enumerate(record.detail):
                    record.detail[index] = detail_type.__args__[0](**value)
            elif isinstance(record.detail, dict) and getattr(
                detail_type, "_auto_assign", None
            ):
                record.detail = detail_type(**record.detail)

        return record


class ReadStream(StreamSerializer):
    """
    Read Stream Serializer
    """


class WriteStream(StreamSerializer):
    """
    Write Stream Serializer
    """

    detail: dict | None
