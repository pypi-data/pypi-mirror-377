# Generated File
from __future__ import annotations

import dataclasses
import struct
import typing
import typing_extensions

from retro_data_structures import json_util
from retro_data_structures.game_check import Game
from retro_data_structures.properties.base_property import BaseProperty
from retro_data_structures.properties.field_reflection import FieldReflection
from retro_data_structures.properties.echoes.archetypes.ControllerActionStruct import ControllerActionStruct

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class ControlHintStructJson(typing_extensions.TypedDict):
        command: json_util.JsonObject
        state: int
    

@dataclasses.dataclass()
class ControlHintStruct(BaseProperty):
    command: ControllerActionStruct = dataclasses.field(default_factory=ControllerActionStruct, metadata={
        'reflection': FieldReflection[ControllerActionStruct](
            ControllerActionStruct, id=0x359c7aaf, original_name='Command', from_json=ControllerActionStruct.from_json, to_json=ControllerActionStruct.to_json
        ),
    })
    state: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x4063422a, original_name='State'
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.ECHOES

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_count = struct.unpack(">H", data.read(2))[0]
        if (result := cls._fast_decode(data, property_count)) is not None:
            return result

        present_fields = default_override or {}
        for _ in range(property_count):
            property_id, property_size = struct.unpack(">LH", data.read(6))
            start = data.tell()
            try:
                property_name, decoder = _property_decoder[property_id]
                present_fields[property_name] = decoder(data, property_size)
            except KeyError:
                raise RuntimeError(f"Unknown property: 0x{property_id:08x}")
            assert data.tell() - start == property_size

        return cls(**present_fields)

    @classmethod
    def _fast_decode(cls, data: typing.BinaryIO, property_count: int) -> typing_extensions.Self | None:
        if property_count != 2:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x359c7aaf
        command = ControllerActionStruct.from_stream(data, property_size, default_override={'command': 0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4063422a
        state = struct.unpack('>l', data.read(4))[0]
    
        return cls(command, state)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x02')  # 2 properties

        data.write(b'5\x9cz\xaf')  # 0x359c7aaf
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.command.to_stream(data, default_override={'command': 0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'@cB*')  # 0x4063422a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.state))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("ControlHintStructJson", data)
        return cls(
            command=ControllerActionStruct.from_json(json_data['command']),
            state=json_data['state'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'command': self.command.to_json(),
            'state': self.state,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.command.dependencies_for, "command", "ControllerActionStruct"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for ControlHintStruct.{field_name} ({field_type}): {e}"
                )


def _decode_command(data: typing.BinaryIO, property_size: int) -> ControllerActionStruct:
    return ControllerActionStruct.from_stream(data, property_size, default_override={'command': 0})


def _decode_state(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x359c7aaf: ('command', _decode_command),
    0x4063422a: ('state', _decode_state),
}
