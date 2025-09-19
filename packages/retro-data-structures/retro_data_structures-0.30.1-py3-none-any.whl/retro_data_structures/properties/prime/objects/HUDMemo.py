# Generated File
from __future__ import annotations

import dataclasses
import enum
import struct
import typing
import typing_extensions

from retro_data_structures import json_util
from retro_data_structures.game_check import Game
from retro_data_structures.properties.base_property import BaseObjectType
from retro_data_structures.properties.field_reflection import FieldReflection
from retro_data_structures.properties.prime.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class HUDMemoJson(typing_extensions.TypedDict):
        name: str
        first_message_timer: float
        unknown_1: bool
        memo_type: int
        strg: int
        active: bool
    

class MemoType(enum.IntEnum):
    StatusMessage = 0
    MessageBox = 1

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None) -> typing_extensions.Self:
        return cls(struct.unpack(">L", data.read(4))[0])

    def to_stream(self, data: typing.BinaryIO) -> None:
        data.write(struct.pack(">L", self.value))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        assert isinstance(data, (int))
        return cls(data)

    def to_json(self) -> int:
        return self.value


@dataclasses.dataclass()
class HUDMemo(BaseObjectType):
    name: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x00000000, original_name='Name'
        ),
    })
    first_message_timer: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000001, original_name='First message timer'
        ),
    })
    unknown_1: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000002, original_name='Unknown 1'
        ),
    })
    memo_type: MemoType = dataclasses.field(default=MemoType.StatusMessage, metadata={
        'reflection': FieldReflection[MemoType](
            MemoType, id=0x00000003, original_name='Memo Type', from_json=MemoType.from_json, to_json=MemoType.to_json
        ),
    })
    strg: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['STRG'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000004, original_name='STRG'
        ),
    })
    active: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000005, original_name='Active'
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.PRIME

    def get_name(self) -> str | None:
        return self.name

    def set_name(self, name: str) -> None:
        self.name = name

    @classmethod
    def object_type(cls) -> int:
        return 0x17

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        property_count = struct.unpack(">L", data.read(4))[0]
        name = b"".join(iter(lambda: data.read(1), b'\x00')).decode("utf-8")
        first_message_timer = struct.unpack('>f', data.read(4))[0]
        unknown_1 = struct.unpack('>?', data.read(1))[0]
        memo_type = MemoType.from_stream(data)
        strg = struct.unpack(">L", data.read(4))[0]
        active = struct.unpack('>?', data.read(1))[0]
        return cls(name, first_message_timer, unknown_1, memo_type, strg, active)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x00\x00\x06')  # 6 properties
        data.write(self.name.encode("utf-8"))
        data.write(b'\x00')
        data.write(struct.pack('>f', self.first_message_timer))
        data.write(struct.pack('>?', self.unknown_1))
        self.memo_type.to_stream(data)
        data.write(struct.pack(">L", self.strg))
        data.write(struct.pack('>?', self.active))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("HUDMemoJson", data)
        return cls(
            name=json_data['name'],
            first_message_timer=json_data['first_message_timer'],
            unknown_1=json_data['unknown_1'],
            memo_type=MemoType.from_json(json_data['memo_type']),
            strg=json_data['strg'],
            active=json_data['active'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'name': self.name,
            'first_message_timer': self.first_message_timer,
            'unknown_1': self.unknown_1,
            'memo_type': self.memo_type.to_json(),
            'strg': self.strg,
            'active': self.active,
        }

    def _dependencies_for_strg(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.strg)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self._dependencies_for_strg, "strg", "AssetId"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for HUDMemo.{field_name} ({field_type}): {e}"
                )
