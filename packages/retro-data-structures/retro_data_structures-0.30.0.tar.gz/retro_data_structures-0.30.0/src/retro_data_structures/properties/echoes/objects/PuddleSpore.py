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
from retro_data_structures.properties.echoes.archetypes.ActorParameters import ActorParameters
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.archetypes.PatternedAITypedef import PatternedAITypedef
from retro_data_structures.properties.echoes.archetypes.ShockWaveInfo import ShockWaveInfo

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class PuddleSporeJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        flavor: int
        patterned: json_util.JsonObject
        actor_information: json_util.JsonObject
        unknown_0x5cdc877d: bool
        charge_time: float
        time_open: float
        platform_time: float
        unknown_0xf1c2d224: float
        unknown_0x3c6af2ac: float
        hit_detection_angle: float
        shock_wave_height: float
        sound: int
        shock_wave_info: json_util.JsonObject
    

@dataclasses.dataclass()
class PuddleSpore(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    flavor: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xbe73724a, original_name='Flavor'
        ),
    })
    patterned: PatternedAITypedef = dataclasses.field(default_factory=PatternedAITypedef, metadata={
        'reflection': FieldReflection[PatternedAITypedef](
            PatternedAITypedef, id=0xb3774750, original_name='Patterned', from_json=PatternedAITypedef.from_json, to_json=PatternedAITypedef.to_json
        ),
    })
    actor_information: ActorParameters = dataclasses.field(default_factory=ActorParameters, metadata={
        'reflection': FieldReflection[ActorParameters](
            ActorParameters, id=0x7e397fed, original_name='ActorInformation', from_json=ActorParameters.from_json, to_json=ActorParameters.to_json
        ),
    })
    unknown_0x5cdc877d: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x5cdc877d, original_name='Unknown'
        ),
    })
    charge_time: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x44de9d92, original_name='ChargeTime'
        ),
    })
    time_open: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x69415fae, original_name='TimeOpen'
        ),
    })
    platform_time: float = dataclasses.field(default=7.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc1202d77, original_name='PlatformTime'
        ),
    })
    unknown_0xf1c2d224: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf1c2d224, original_name='Unknown'
        ),
    })
    unknown_0x3c6af2ac: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3c6af2ac, original_name='Unknown'
        ),
    })
    hit_detection_angle: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xdaddebe7, original_name='HitDetectionAngle'
        ),
    })
    shock_wave_height: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x42ad1392, original_name='ShockWaveHeight'
        ),
    })
    sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0xfe20b4f5, original_name='Sound'
        ),
    })
    shock_wave_info: ShockWaveInfo = dataclasses.field(default_factory=ShockWaveInfo, metadata={
        'reflection': FieldReflection[ShockWaveInfo](
            ShockWaveInfo, id=0x8f4787cb, original_name='ShockWaveInfo', from_json=ShockWaveInfo.from_json, to_json=ShockWaveInfo.to_json
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.ECHOES

    def get_name(self) -> str | None:
        return self.editor_properties.name

    def set_name(self, name: str) -> None:
        self.editor_properties.name = name

    @classmethod
    def object_type(cls) -> str:
        return 'SPOR'

    @classmethod
    def modules(cls) -> list[str]:
        return ['PuddleSpore.rel']

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
        if property_count != 14:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbe73724a
        flavor = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb3774750
        patterned = PatternedAITypedef.from_stream(data, property_size, default_override={'detection_range': 35.0, 'detection_height_range': 3.0, 'detection_angle': 180.0, 'damage_wait_time': 0.0, 'collision_radius': 2.5, 'collision_height': 3.0, 'creature_size': 1})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7e397fed
        actor_information = ActorParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5cdc877d
        unknown_0x5cdc877d = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x44de9d92
        charge_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x69415fae
        time_open = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc1202d77
        platform_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf1c2d224
        unknown_0xf1c2d224 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3c6af2ac
        unknown_0x3c6af2ac = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdaddebe7
        hit_detection_angle = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x42ad1392
        shock_wave_height = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfe20b4f5
        sound = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8f4787cb
        shock_wave_info = ShockWaveInfo.from_stream(data, property_size)
    
        return cls(editor_properties, flavor, patterned, actor_information, unknown_0x5cdc877d, charge_time, time_open, platform_time, unknown_0xf1c2d224, unknown_0x3c6af2ac, hit_detection_angle, shock_wave_height, sound, shock_wave_info)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x0e')  # 14 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xbesrJ')  # 0xbe73724a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.flavor))

        data.write(b'\xb3wGP')  # 0xb3774750
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.patterned.to_stream(data, default_override={'detection_range': 35.0, 'detection_height_range': 3.0, 'detection_angle': 180.0, 'damage_wait_time': 0.0, 'collision_radius': 2.5, 'collision_height': 3.0, 'creature_size': 1})
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

        data.write(b'\\\xdc\x87}')  # 0x5cdc877d
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x5cdc877d))

        data.write(b'D\xde\x9d\x92')  # 0x44de9d92
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.charge_time))

        data.write(b'iA_\xae')  # 0x69415fae
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.time_open))

        data.write(b'\xc1 -w')  # 0xc1202d77
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.platform_time))

        data.write(b'\xf1\xc2\xd2$')  # 0xf1c2d224
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xf1c2d224))

        data.write(b'<j\xf2\xac')  # 0x3c6af2ac
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x3c6af2ac))

        data.write(b'\xda\xdd\xeb\xe7')  # 0xdaddebe7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.hit_detection_angle))

        data.write(b'B\xad\x13\x92')  # 0x42ad1392
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.shock_wave_height))

        data.write(b'\xfe \xb4\xf5')  # 0xfe20b4f5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound))

        data.write(b'\x8fG\x87\xcb')  # 0x8f4787cb
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.shock_wave_info.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("PuddleSporeJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            flavor=json_data['flavor'],
            patterned=PatternedAITypedef.from_json(json_data['patterned']),
            actor_information=ActorParameters.from_json(json_data['actor_information']),
            unknown_0x5cdc877d=json_data['unknown_0x5cdc877d'],
            charge_time=json_data['charge_time'],
            time_open=json_data['time_open'],
            platform_time=json_data['platform_time'],
            unknown_0xf1c2d224=json_data['unknown_0xf1c2d224'],
            unknown_0x3c6af2ac=json_data['unknown_0x3c6af2ac'],
            hit_detection_angle=json_data['hit_detection_angle'],
            shock_wave_height=json_data['shock_wave_height'],
            sound=json_data['sound'],
            shock_wave_info=ShockWaveInfo.from_json(json_data['shock_wave_info']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'flavor': self.flavor,
            'patterned': self.patterned.to_json(),
            'actor_information': self.actor_information.to_json(),
            'unknown_0x5cdc877d': self.unknown_0x5cdc877d,
            'charge_time': self.charge_time,
            'time_open': self.time_open,
            'platform_time': self.platform_time,
            'unknown_0xf1c2d224': self.unknown_0xf1c2d224,
            'unknown_0x3c6af2ac': self.unknown_0x3c6af2ac,
            'hit_detection_angle': self.hit_detection_angle,
            'shock_wave_height': self.shock_wave_height,
            'sound': self.sound,
            'shock_wave_info': self.shock_wave_info.to_json(),
        }

    def _dependencies_for_sound(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.editor_properties.dependencies_for, "editor_properties", "EditorProperties"),
            (self.patterned.dependencies_for, "patterned", "PatternedAITypedef"),
            (self.actor_information.dependencies_for, "actor_information", "ActorParameters"),
            (self._dependencies_for_sound, "sound", "int"),
            (self.shock_wave_info.dependencies_for, "shock_wave_info", "ShockWaveInfo"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for PuddleSpore.{field_name} ({field_type}): {e}"
                )


def _decode_flavor(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_patterned(data: typing.BinaryIO, property_size: int) -> PatternedAITypedef:
    return PatternedAITypedef.from_stream(data, property_size, default_override={'detection_range': 35.0, 'detection_height_range': 3.0, 'detection_angle': 180.0, 'damage_wait_time': 0.0, 'collision_radius': 2.5, 'collision_height': 3.0, 'creature_size': 1})


def _decode_unknown_0x5cdc877d(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_charge_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_time_open(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_platform_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xf1c2d224(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x3c6af2ac(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_hit_detection_angle(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_shock_wave_height(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_sound(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0xbe73724a: ('flavor', _decode_flavor),
    0xb3774750: ('patterned', _decode_patterned),
    0x7e397fed: ('actor_information', ActorParameters.from_stream),
    0x5cdc877d: ('unknown_0x5cdc877d', _decode_unknown_0x5cdc877d),
    0x44de9d92: ('charge_time', _decode_charge_time),
    0x69415fae: ('time_open', _decode_time_open),
    0xc1202d77: ('platform_time', _decode_platform_time),
    0xf1c2d224: ('unknown_0xf1c2d224', _decode_unknown_0xf1c2d224),
    0x3c6af2ac: ('unknown_0x3c6af2ac', _decode_unknown_0x3c6af2ac),
    0xdaddebe7: ('hit_detection_angle', _decode_hit_detection_angle),
    0x42ad1392: ('shock_wave_height', _decode_shock_wave_height),
    0xfe20b4f5: ('sound', _decode_sound),
    0x8f4787cb: ('shock_wave_info', ShockWaveInfo.from_stream),
}
