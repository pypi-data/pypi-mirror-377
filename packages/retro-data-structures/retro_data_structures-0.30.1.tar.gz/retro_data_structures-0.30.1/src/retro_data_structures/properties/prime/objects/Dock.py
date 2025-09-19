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
from retro_data_structures.properties.prime.core.Vector import Vector

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class DockJson(typing_extensions.TypedDict):
        name: str
        active: bool
        position: json_util.JsonValue
        scale: json_util.JsonValue
        dock_number: int
        area_number: int
        load_connected_immediate: bool
    

@dataclasses.dataclass()
class Dock(BaseObjectType):
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
    position: Vector = dataclasses.field(default_factory=Vector, metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x00000002, original_name='Position', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    scale: Vector = dataclasses.field(default_factory=Vector, metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x00000003, original_name='Scale', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    dock_number: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000004, original_name='DockNumber'
        ),
    })
    area_number: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000005, original_name='AreaNumber'
        ),
    })
    load_connected_immediate: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000006, original_name='LoadConnectedImmediate'
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
        return 0xB

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        property_count = struct.unpack(">L", data.read(4))[0]
        name = b"".join(iter(lambda: data.read(1), b'\x00')).decode("utf-8")
        active = struct.unpack('>?', data.read(1))[0]
        position = Vector.from_stream(data)
        scale = Vector.from_stream(data)
        dock_number = struct.unpack('>l', data.read(4))[0]
        area_number = struct.unpack('>l', data.read(4))[0]
        load_connected_immediate = struct.unpack('>?', data.read(1))[0]
        return cls(name, active, position, scale, dock_number, area_number, load_connected_immediate)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x00\x00\x07')  # 7 properties
        data.write(self.name.encode("utf-8"))
        data.write(b'\x00')
        data.write(struct.pack('>?', self.active))
        self.position.to_stream(data)
        self.scale.to_stream(data)
        data.write(struct.pack('>l', self.dock_number))
        data.write(struct.pack('>l', self.area_number))
        data.write(struct.pack('>?', self.load_connected_immediate))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("DockJson", data)
        return cls(
            name=json_data['name'],
            active=json_data['active'],
            position=Vector.from_json(json_data['position']),
            scale=Vector.from_json(json_data['scale']),
            dock_number=json_data['dock_number'],
            area_number=json_data['area_number'],
            load_connected_immediate=json_data['load_connected_immediate'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'name': self.name,
            'active': self.active,
            'position': self.position.to_json(),
            'scale': self.scale.to_json(),
            'dock_number': self.dock_number,
            'area_number': self.area_number,
            'load_connected_immediate': self.load_connected_immediate,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []
