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

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class TimerJson(typing_extensions.TypedDict):
        name: str
        start_time: float
        max_random_delay: float
        loop: bool
        auto_start: bool
        active: bool
    

@dataclasses.dataclass()
class Timer(BaseObjectType):
    name: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x00000000, original_name='Name'
        ),
    })
    start_time: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000001, original_name='Start Time'
        ),
    })
    max_random_delay: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000002, original_name='Max Random Delay'
        ),
    })
    loop: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000003, original_name='Loop'
        ),
    })
    auto_start: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000004, original_name='Auto-Start'
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
        return 0x5

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        property_count = struct.unpack(">L", data.read(4))[0]
        name = b"".join(iter(lambda: data.read(1), b'\x00')).decode("utf-8")
        start_time = struct.unpack('>f', data.read(4))[0]
        max_random_delay = struct.unpack('>f', data.read(4))[0]
        loop = struct.unpack('>?', data.read(1))[0]
        auto_start = struct.unpack('>?', data.read(1))[0]
        active = struct.unpack('>?', data.read(1))[0]
        return cls(name, start_time, max_random_delay, loop, auto_start, active)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x00\x00\x06')  # 6 properties
        data.write(self.name.encode("utf-8"))
        data.write(b'\x00')
        data.write(struct.pack('>f', self.start_time))
        data.write(struct.pack('>f', self.max_random_delay))
        data.write(struct.pack('>?', self.loop))
        data.write(struct.pack('>?', self.auto_start))
        data.write(struct.pack('>?', self.active))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("TimerJson", data)
        return cls(
            name=json_data['name'],
            start_time=json_data['start_time'],
            max_random_delay=json_data['max_random_delay'],
            loop=json_data['loop'],
            auto_start=json_data['auto_start'],
            active=json_data['active'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'name': self.name,
            'start_time': self.start_time,
            'max_random_delay': self.max_random_delay,
            'loop': self.loop,
            'auto_start': self.auto_start,
            'active': self.active,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []
