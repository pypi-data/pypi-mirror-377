# Generated File
from __future__ import annotations

import dataclasses
import struct
import typing
import typing_extensions

from retro_data_structures import json_util
from retro_data_structures.game_check import Game
from retro_data_structures.properties.base_property import BaseObjectType
from retro_data_structures.properties.field_reflection import FieldReflection
import retro_data_structures.enums.prime as enums

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class ControllerActionJson(typing_extensions.TypedDict):
        name: str
        active: bool
        action: int
        deactivate_when_used: bool
    

@dataclasses.dataclass()
class ControllerAction(BaseObjectType):
    name: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x00000000, original_name='Name'
        ),
    })
    active: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000001, original_name='Active'
        ),
    })
    action: enums.PlayerActionEnum = dataclasses.field(default=enums.PlayerActionEnum.Forward, metadata={
        'reflection': FieldReflection[enums.PlayerActionEnum](
            enums.PlayerActionEnum, id=0x00000002, original_name='Action', from_json=enums.PlayerActionEnum.from_json, to_json=enums.PlayerActionEnum.to_json
        ),
    })
    deactivate_when_used: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000003, original_name='Deactivate When Used'
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
        return 0x55

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        property_count = struct.unpack(">L", data.read(4))[0]
        name = b"".join(iter(lambda: data.read(1), b'\x00')).decode("utf-8")
        active = struct.unpack('>?', data.read(1))[0]
        action = enums.PlayerActionEnum.from_stream(data)
        deactivate_when_used = struct.unpack('>?', data.read(1))[0]
        return cls(name, active, action, deactivate_when_used)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x00\x00\x04')  # 4 properties
        data.write(self.name.encode("utf-8"))
        data.write(b'\x00')
        data.write(struct.pack('>?', self.active))
        self.action.to_stream(data)
        data.write(struct.pack('>?', self.deactivate_when_used))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("ControllerActionJson", data)
        return cls(
            name=json_data['name'],
            active=json_data['active'],
            action=enums.PlayerActionEnum.from_json(json_data['action']),
            deactivate_when_used=json_data['deactivate_when_used'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'name': self.name,
            'active': self.active,
            'action': self.action.to_json(),
            'deactivate_when_used': self.deactivate_when_used,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []
