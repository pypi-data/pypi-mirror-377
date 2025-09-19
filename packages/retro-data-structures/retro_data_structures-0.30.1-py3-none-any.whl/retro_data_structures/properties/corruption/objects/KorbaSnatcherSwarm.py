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
from retro_data_structures.properties.corruption.archetypes.ActorParameters import ActorParameters
from retro_data_structures.properties.corruption.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.corruption.archetypes.KorbaSnatcherData import KorbaSnatcherData
from retro_data_structures.properties.corruption.archetypes.SwarmBasicsData import SwarmBasicsData
from retro_data_structures.properties.corruption.core.AnimationParameters import AnimationParameters

if typing.TYPE_CHECKING:
    class KorbaSnatcherSwarmJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        korba_snatcher_properties: json_util.JsonObject
        actor_information: json_util.JsonObject
        character_animation_information: json_util.JsonObject
        active: bool
        swarm_basics_data: json_util.JsonObject
        unknown_0x92827035: float
        unknown_0xdc30cb20: int
        unknown_0x48387110: int
        unknown_0x5d054897: int
    

@dataclasses.dataclass()
class KorbaSnatcherSwarm(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    korba_snatcher_properties: KorbaSnatcherData = dataclasses.field(default_factory=KorbaSnatcherData, metadata={
        'reflection': FieldReflection[KorbaSnatcherData](
            KorbaSnatcherData, id=0x5506094b, original_name='KorbaSnatcherProperties', from_json=KorbaSnatcherData.from_json, to_json=KorbaSnatcherData.to_json
        ),
    })
    actor_information: ActorParameters = dataclasses.field(default_factory=ActorParameters, metadata={
        'reflection': FieldReflection[ActorParameters](
            ActorParameters, id=0x7e397fed, original_name='ActorInformation', from_json=ActorParameters.from_json, to_json=ActorParameters.to_json
        ),
    })
    character_animation_information: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0xa244c9d8, original_name='CharacterAnimationInformation', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    active: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xc6bb2f45, original_name='Active'
        ),
    })
    swarm_basics_data: SwarmBasicsData = dataclasses.field(default_factory=SwarmBasicsData, metadata={
        'reflection': FieldReflection[SwarmBasicsData](
            SwarmBasicsData, id=0x4cfc46fe, original_name='SwarmBasicsData', from_json=SwarmBasicsData.from_json, to_json=SwarmBasicsData.to_json
        ),
    })
    unknown_0x92827035: float = dataclasses.field(default=0.44999998807907104, metadata={
        'reflection': FieldReflection[float](
            float, id=0x92827035, original_name='Unknown'
        ),
    })
    unknown_0xdc30cb20: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xdc30cb20, original_name='Unknown'
        ),
    })
    unknown_0x48387110: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x48387110, original_name='Unknown'
        ),
    })
    unknown_0x5d054897: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x5d054897, original_name='Unknown'
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.CORRUPTION

    def get_name(self) -> str | None:
        return self.editor_properties.name

    def set_name(self, name: str) -> None:
        self.editor_properties.name = name

    @classmethod
    def object_type(cls) -> str:
        return 'KRBA'

    @classmethod
    def modules(cls) -> list[str]:
        return ['RSO_KorbaMaw.rso']

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        struct_id, size, property_count = struct.unpack(">LHH", data.read(8))
        assert struct_id == 0xFFFFFFFF
        root_size_start = data.tell() - 2

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

        assert data.tell() - root_size_start == size
        return cls(**present_fields)

    @classmethod
    def _fast_decode(cls, data: typing.BinaryIO, property_count: int) -> typing_extensions.Self | None:
        if property_count != 10:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5506094b
        korba_snatcher_properties = KorbaSnatcherData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7e397fed
        actor_information = ActorParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa244c9d8
        character_animation_information = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc6bb2f45
        active = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4cfc46fe
        swarm_basics_data = SwarmBasicsData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x92827035
        unknown_0x92827035 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdc30cb20
        unknown_0xdc30cb20 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x48387110
        unknown_0x48387110 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5d054897
        unknown_0x5d054897 = struct.unpack('>l', data.read(4))[0]
    
        return cls(editor_properties, korba_snatcher_properties, actor_information, character_animation_information, active, swarm_basics_data, unknown_0x92827035, unknown_0xdc30cb20, unknown_0x48387110, unknown_0x5d054897)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\n')  # 10 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'U\x06\tK')  # 0x5506094b
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.korba_snatcher_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'~9\x7f\xed')  # 0x7e397fed
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.actor_information.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xa2D\xc9\xd8')  # 0xa244c9d8
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.character_animation_information.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc6\xbb/E')  # 0xc6bb2f45
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.active))

        data.write(b'L\xfcF\xfe')  # 0x4cfc46fe
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.swarm_basics_data.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x92\x82p5')  # 0x92827035
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x92827035))

        data.write(b'\xdc0\xcb ')  # 0xdc30cb20
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xdc30cb20))

        data.write(b'H8q\x10')  # 0x48387110
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x48387110))

        data.write(b']\x05H\x97')  # 0x5d054897
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x5d054897))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("KorbaSnatcherSwarmJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            korba_snatcher_properties=KorbaSnatcherData.from_json(json_data['korba_snatcher_properties']),
            actor_information=ActorParameters.from_json(json_data['actor_information']),
            character_animation_information=AnimationParameters.from_json(json_data['character_animation_information']),
            active=json_data['active'],
            swarm_basics_data=SwarmBasicsData.from_json(json_data['swarm_basics_data']),
            unknown_0x92827035=json_data['unknown_0x92827035'],
            unknown_0xdc30cb20=json_data['unknown_0xdc30cb20'],
            unknown_0x48387110=json_data['unknown_0x48387110'],
            unknown_0x5d054897=json_data['unknown_0x5d054897'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'korba_snatcher_properties': self.korba_snatcher_properties.to_json(),
            'actor_information': self.actor_information.to_json(),
            'character_animation_information': self.character_animation_information.to_json(),
            'active': self.active,
            'swarm_basics_data': self.swarm_basics_data.to_json(),
            'unknown_0x92827035': self.unknown_0x92827035,
            'unknown_0xdc30cb20': self.unknown_0xdc30cb20,
            'unknown_0x48387110': self.unknown_0x48387110,
            'unknown_0x5d054897': self.unknown_0x5d054897,
        }


def _decode_active(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x92827035(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xdc30cb20(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x48387110(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x5d054897(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0x5506094b: ('korba_snatcher_properties', KorbaSnatcherData.from_stream),
    0x7e397fed: ('actor_information', ActorParameters.from_stream),
    0xa244c9d8: ('character_animation_information', AnimationParameters.from_stream),
    0xc6bb2f45: ('active', _decode_active),
    0x4cfc46fe: ('swarm_basics_data', SwarmBasicsData.from_stream),
    0x92827035: ('unknown_0x92827035', _decode_unknown_0x92827035),
    0xdc30cb20: ('unknown_0xdc30cb20', _decode_unknown_0xdc30cb20),
    0x48387110: ('unknown_0x48387110', _decode_unknown_0x48387110),
    0x5d054897: ('unknown_0x5d054897', _decode_unknown_0x5d054897),
}
