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
from retro_data_structures.properties.echoes.archetypes.AudioPlaybackParms import AudioPlaybackParms
from retro_data_structures.properties.echoes.archetypes.DamageInfo import DamageInfo
from retro_data_structures.properties.echoes.archetypes.IngSpiderballGuardianStruct import IngSpiderballGuardianStruct

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class UnknownStruct31Json(typing_extensions.TypedDict):
        ing_spiderball_guardian_struct_0x152db484: json_util.JsonObject
        ing_spiderball_guardian_struct_0x2d163ff7: json_util.JsonObject
        ing_spiderball_guardian_struct_0x8c2fbb19: json_util.JsonObject
        ing_spiderball_guardian_struct_0x5d612911: json_util.JsonObject
        ing_spiderball_guardian_struct_0xfc58adff: json_util.JsonObject
        ing_spiderball_guardian_struct_0xc463268c: json_util.JsonObject
        damage_radius: float
        proximity_damage: json_util.JsonObject
        unknown: float
        audio_playback_parms_0xaed23abc: json_util.JsonObject
        sound_spiderball_rolling: json_util.JsonObject
        audio_playback_parms_0xcee38f10: json_util.JsonObject
        audio_playback_parms_0x796fa303: json_util.JsonObject
        sound_enter_stunned: json_util.JsonObject
        audio_playback_parms_0x44c1f241: json_util.JsonObject
    

@dataclasses.dataclass()
class UnknownStruct31(BaseProperty):
    ing_spiderball_guardian_struct_0x152db484: IngSpiderballGuardianStruct = dataclasses.field(default_factory=IngSpiderballGuardianStruct, metadata={
        'reflection': FieldReflection[IngSpiderballGuardianStruct](
            IngSpiderballGuardianStruct, id=0x152db484, original_name='IngSpiderballGuardianStruct', from_json=IngSpiderballGuardianStruct.from_json, to_json=IngSpiderballGuardianStruct.to_json
        ),
    })
    ing_spiderball_guardian_struct_0x2d163ff7: IngSpiderballGuardianStruct = dataclasses.field(default_factory=IngSpiderballGuardianStruct, metadata={
        'reflection': FieldReflection[IngSpiderballGuardianStruct](
            IngSpiderballGuardianStruct, id=0x2d163ff7, original_name='IngSpiderballGuardianStruct', from_json=IngSpiderballGuardianStruct.from_json, to_json=IngSpiderballGuardianStruct.to_json
        ),
    })
    ing_spiderball_guardian_struct_0x8c2fbb19: IngSpiderballGuardianStruct = dataclasses.field(default_factory=IngSpiderballGuardianStruct, metadata={
        'reflection': FieldReflection[IngSpiderballGuardianStruct](
            IngSpiderballGuardianStruct, id=0x8c2fbb19, original_name='IngSpiderballGuardianStruct', from_json=IngSpiderballGuardianStruct.from_json, to_json=IngSpiderballGuardianStruct.to_json
        ),
    })
    ing_spiderball_guardian_struct_0x5d612911: IngSpiderballGuardianStruct = dataclasses.field(default_factory=IngSpiderballGuardianStruct, metadata={
        'reflection': FieldReflection[IngSpiderballGuardianStruct](
            IngSpiderballGuardianStruct, id=0x5d612911, original_name='IngSpiderballGuardianStruct', from_json=IngSpiderballGuardianStruct.from_json, to_json=IngSpiderballGuardianStruct.to_json
        ),
    })
    ing_spiderball_guardian_struct_0xfc58adff: IngSpiderballGuardianStruct = dataclasses.field(default_factory=IngSpiderballGuardianStruct, metadata={
        'reflection': FieldReflection[IngSpiderballGuardianStruct](
            IngSpiderballGuardianStruct, id=0xfc58adff, original_name='IngSpiderballGuardianStruct', from_json=IngSpiderballGuardianStruct.from_json, to_json=IngSpiderballGuardianStruct.to_json
        ),
    })
    ing_spiderball_guardian_struct_0xc463268c: IngSpiderballGuardianStruct = dataclasses.field(default_factory=IngSpiderballGuardianStruct, metadata={
        'reflection': FieldReflection[IngSpiderballGuardianStruct](
            IngSpiderballGuardianStruct, id=0xc463268c, original_name='IngSpiderballGuardianStruct', from_json=IngSpiderballGuardianStruct.from_json, to_json=IngSpiderballGuardianStruct.to_json
        ),
    })
    damage_radius: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0f598739, original_name='DamageRadius'
        ),
    })
    proximity_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xba78d281, original_name='ProximityDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    unknown: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x32133b39, original_name='Unknown'
        ),
    })
    audio_playback_parms_0xaed23abc: AudioPlaybackParms = dataclasses.field(default_factory=AudioPlaybackParms, metadata={
        'reflection': FieldReflection[AudioPlaybackParms](
            AudioPlaybackParms, id=0xaed23abc, original_name='AudioPlaybackParms', from_json=AudioPlaybackParms.from_json, to_json=AudioPlaybackParms.to_json
        ),
    })
    sound_spiderball_rolling: AudioPlaybackParms = dataclasses.field(default_factory=AudioPlaybackParms, metadata={
        'reflection': FieldReflection[AudioPlaybackParms](
            AudioPlaybackParms, id=0x3a5e2f52, original_name='Sound_SpiderballRolling', from_json=AudioPlaybackParms.from_json, to_json=AudioPlaybackParms.to_json
        ),
    })
    audio_playback_parms_0xcee38f10: AudioPlaybackParms = dataclasses.field(default_factory=AudioPlaybackParms, metadata={
        'reflection': FieldReflection[AudioPlaybackParms](
            AudioPlaybackParms, id=0xcee38f10, original_name='AudioPlaybackParms', from_json=AudioPlaybackParms.from_json, to_json=AudioPlaybackParms.to_json
        ),
    })
    audio_playback_parms_0x796fa303: AudioPlaybackParms = dataclasses.field(default_factory=AudioPlaybackParms, metadata={
        'reflection': FieldReflection[AudioPlaybackParms](
            AudioPlaybackParms, id=0x796fa303, original_name='AudioPlaybackParms', from_json=AudioPlaybackParms.from_json, to_json=AudioPlaybackParms.to_json
        ),
    })
    sound_enter_stunned: AudioPlaybackParms = dataclasses.field(default_factory=AudioPlaybackParms, metadata={
        'reflection': FieldReflection[AudioPlaybackParms](
            AudioPlaybackParms, id=0xd5f3e9c4, original_name='Sound_EnterStunned', from_json=AudioPlaybackParms.from_json, to_json=AudioPlaybackParms.to_json
        ),
    })
    audio_playback_parms_0x44c1f241: AudioPlaybackParms = dataclasses.field(default_factory=AudioPlaybackParms, metadata={
        'reflection': FieldReflection[AudioPlaybackParms](
            AudioPlaybackParms, id=0x44c1f241, original_name='AudioPlaybackParms', from_json=AudioPlaybackParms.from_json, to_json=AudioPlaybackParms.to_json
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
        if property_count != 15:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x152db484
        ing_spiderball_guardian_struct_0x152db484 = IngSpiderballGuardianStruct.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2d163ff7
        ing_spiderball_guardian_struct_0x2d163ff7 = IngSpiderballGuardianStruct.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8c2fbb19
        ing_spiderball_guardian_struct_0x8c2fbb19 = IngSpiderballGuardianStruct.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5d612911
        ing_spiderball_guardian_struct_0x5d612911 = IngSpiderballGuardianStruct.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfc58adff
        ing_spiderball_guardian_struct_0xfc58adff = IngSpiderballGuardianStruct.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc463268c
        ing_spiderball_guardian_struct_0xc463268c = IngSpiderballGuardianStruct.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0f598739
        damage_radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xba78d281
        proximity_damage = DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 40.0, 'di_knock_back_power': 10.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x32133b39
        unknown = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xaed23abc
        audio_playback_parms_0xaed23abc = AudioPlaybackParms.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3a5e2f52
        sound_spiderball_rolling = AudioPlaybackParms.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcee38f10
        audio_playback_parms_0xcee38f10 = AudioPlaybackParms.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x796fa303
        audio_playback_parms_0x796fa303 = AudioPlaybackParms.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd5f3e9c4
        sound_enter_stunned = AudioPlaybackParms.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x44c1f241
        audio_playback_parms_0x44c1f241 = AudioPlaybackParms.from_stream(data, property_size)
    
        return cls(ing_spiderball_guardian_struct_0x152db484, ing_spiderball_guardian_struct_0x2d163ff7, ing_spiderball_guardian_struct_0x8c2fbb19, ing_spiderball_guardian_struct_0x5d612911, ing_spiderball_guardian_struct_0xfc58adff, ing_spiderball_guardian_struct_0xc463268c, damage_radius, proximity_damage, unknown, audio_playback_parms_0xaed23abc, sound_spiderball_rolling, audio_playback_parms_0xcee38f10, audio_playback_parms_0x796fa303, sound_enter_stunned, audio_playback_parms_0x44c1f241)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x0f')  # 15 properties

        data.write(b'\x15-\xb4\x84')  # 0x152db484
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.ing_spiderball_guardian_struct_0x152db484.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'-\x16?\xf7')  # 0x2d163ff7
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.ing_spiderball_guardian_struct_0x2d163ff7.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x8c/\xbb\x19')  # 0x8c2fbb19
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.ing_spiderball_guardian_struct_0x8c2fbb19.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b']a)\x11')  # 0x5d612911
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.ing_spiderball_guardian_struct_0x5d612911.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xfcX\xad\xff')  # 0xfc58adff
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.ing_spiderball_guardian_struct_0xfc58adff.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc4c&\x8c')  # 0xc463268c
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.ing_spiderball_guardian_struct_0xc463268c.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x0fY\x879')  # 0xf598739
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.damage_radius))

        data.write(b'\xbax\xd2\x81')  # 0xba78d281
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.proximity_damage.to_stream(data, default_override={'di_weapon_type': 11, 'di_damage': 40.0, 'di_knock_back_power': 10.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'2\x13;9')  # 0x32133b39
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown))

        data.write(b'\xae\xd2:\xbc')  # 0xaed23abc
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.audio_playback_parms_0xaed23abc.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b':^/R')  # 0x3a5e2f52
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.sound_spiderball_rolling.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xce\xe3\x8f\x10')  # 0xcee38f10
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.audio_playback_parms_0xcee38f10.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'yo\xa3\x03')  # 0x796fa303
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.audio_playback_parms_0x796fa303.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xd5\xf3\xe9\xc4')  # 0xd5f3e9c4
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.sound_enter_stunned.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'D\xc1\xf2A')  # 0x44c1f241
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.audio_playback_parms_0x44c1f241.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct31Json", data)
        return cls(
            ing_spiderball_guardian_struct_0x152db484=IngSpiderballGuardianStruct.from_json(json_data['ing_spiderball_guardian_struct_0x152db484']),
            ing_spiderball_guardian_struct_0x2d163ff7=IngSpiderballGuardianStruct.from_json(json_data['ing_spiderball_guardian_struct_0x2d163ff7']),
            ing_spiderball_guardian_struct_0x8c2fbb19=IngSpiderballGuardianStruct.from_json(json_data['ing_spiderball_guardian_struct_0x8c2fbb19']),
            ing_spiderball_guardian_struct_0x5d612911=IngSpiderballGuardianStruct.from_json(json_data['ing_spiderball_guardian_struct_0x5d612911']),
            ing_spiderball_guardian_struct_0xfc58adff=IngSpiderballGuardianStruct.from_json(json_data['ing_spiderball_guardian_struct_0xfc58adff']),
            ing_spiderball_guardian_struct_0xc463268c=IngSpiderballGuardianStruct.from_json(json_data['ing_spiderball_guardian_struct_0xc463268c']),
            damage_radius=json_data['damage_radius'],
            proximity_damage=DamageInfo.from_json(json_data['proximity_damage']),
            unknown=json_data['unknown'],
            audio_playback_parms_0xaed23abc=AudioPlaybackParms.from_json(json_data['audio_playback_parms_0xaed23abc']),
            sound_spiderball_rolling=AudioPlaybackParms.from_json(json_data['sound_spiderball_rolling']),
            audio_playback_parms_0xcee38f10=AudioPlaybackParms.from_json(json_data['audio_playback_parms_0xcee38f10']),
            audio_playback_parms_0x796fa303=AudioPlaybackParms.from_json(json_data['audio_playback_parms_0x796fa303']),
            sound_enter_stunned=AudioPlaybackParms.from_json(json_data['sound_enter_stunned']),
            audio_playback_parms_0x44c1f241=AudioPlaybackParms.from_json(json_data['audio_playback_parms_0x44c1f241']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'ing_spiderball_guardian_struct_0x152db484': self.ing_spiderball_guardian_struct_0x152db484.to_json(),
            'ing_spiderball_guardian_struct_0x2d163ff7': self.ing_spiderball_guardian_struct_0x2d163ff7.to_json(),
            'ing_spiderball_guardian_struct_0x8c2fbb19': self.ing_spiderball_guardian_struct_0x8c2fbb19.to_json(),
            'ing_spiderball_guardian_struct_0x5d612911': self.ing_spiderball_guardian_struct_0x5d612911.to_json(),
            'ing_spiderball_guardian_struct_0xfc58adff': self.ing_spiderball_guardian_struct_0xfc58adff.to_json(),
            'ing_spiderball_guardian_struct_0xc463268c': self.ing_spiderball_guardian_struct_0xc463268c.to_json(),
            'damage_radius': self.damage_radius,
            'proximity_damage': self.proximity_damage.to_json(),
            'unknown': self.unknown,
            'audio_playback_parms_0xaed23abc': self.audio_playback_parms_0xaed23abc.to_json(),
            'sound_spiderball_rolling': self.sound_spiderball_rolling.to_json(),
            'audio_playback_parms_0xcee38f10': self.audio_playback_parms_0xcee38f10.to_json(),
            'audio_playback_parms_0x796fa303': self.audio_playback_parms_0x796fa303.to_json(),
            'sound_enter_stunned': self.sound_enter_stunned.to_json(),
            'audio_playback_parms_0x44c1f241': self.audio_playback_parms_0x44c1f241.to_json(),
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.ing_spiderball_guardian_struct_0x152db484.dependencies_for, "ing_spiderball_guardian_struct_0x152db484", "IngSpiderballGuardianStruct"),
            (self.ing_spiderball_guardian_struct_0x2d163ff7.dependencies_for, "ing_spiderball_guardian_struct_0x2d163ff7", "IngSpiderballGuardianStruct"),
            (self.ing_spiderball_guardian_struct_0x8c2fbb19.dependencies_for, "ing_spiderball_guardian_struct_0x8c2fbb19", "IngSpiderballGuardianStruct"),
            (self.ing_spiderball_guardian_struct_0x5d612911.dependencies_for, "ing_spiderball_guardian_struct_0x5d612911", "IngSpiderballGuardianStruct"),
            (self.ing_spiderball_guardian_struct_0xfc58adff.dependencies_for, "ing_spiderball_guardian_struct_0xfc58adff", "IngSpiderballGuardianStruct"),
            (self.ing_spiderball_guardian_struct_0xc463268c.dependencies_for, "ing_spiderball_guardian_struct_0xc463268c", "IngSpiderballGuardianStruct"),
            (self.proximity_damage.dependencies_for, "proximity_damage", "DamageInfo"),
            (self.audio_playback_parms_0xaed23abc.dependencies_for, "audio_playback_parms_0xaed23abc", "AudioPlaybackParms"),
            (self.sound_spiderball_rolling.dependencies_for, "sound_spiderball_rolling", "AudioPlaybackParms"),
            (self.audio_playback_parms_0xcee38f10.dependencies_for, "audio_playback_parms_0xcee38f10", "AudioPlaybackParms"),
            (self.audio_playback_parms_0x796fa303.dependencies_for, "audio_playback_parms_0x796fa303", "AudioPlaybackParms"),
            (self.sound_enter_stunned.dependencies_for, "sound_enter_stunned", "AudioPlaybackParms"),
            (self.audio_playback_parms_0x44c1f241.dependencies_for, "audio_playback_parms_0x44c1f241", "AudioPlaybackParms"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for UnknownStruct31.{field_name} ({field_type}): {e}"
                )


def _decode_damage_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_proximity_damage(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 40.0, 'di_knock_back_power': 10.0})


def _decode_unknown(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x152db484: ('ing_spiderball_guardian_struct_0x152db484', IngSpiderballGuardianStruct.from_stream),
    0x2d163ff7: ('ing_spiderball_guardian_struct_0x2d163ff7', IngSpiderballGuardianStruct.from_stream),
    0x8c2fbb19: ('ing_spiderball_guardian_struct_0x8c2fbb19', IngSpiderballGuardianStruct.from_stream),
    0x5d612911: ('ing_spiderball_guardian_struct_0x5d612911', IngSpiderballGuardianStruct.from_stream),
    0xfc58adff: ('ing_spiderball_guardian_struct_0xfc58adff', IngSpiderballGuardianStruct.from_stream),
    0xc463268c: ('ing_spiderball_guardian_struct_0xc463268c', IngSpiderballGuardianStruct.from_stream),
    0xf598739: ('damage_radius', _decode_damage_radius),
    0xba78d281: ('proximity_damage', _decode_proximity_damage),
    0x32133b39: ('unknown', _decode_unknown),
    0xaed23abc: ('audio_playback_parms_0xaed23abc', AudioPlaybackParms.from_stream),
    0x3a5e2f52: ('sound_spiderball_rolling', AudioPlaybackParms.from_stream),
    0xcee38f10: ('audio_playback_parms_0xcee38f10', AudioPlaybackParms.from_stream),
    0x796fa303: ('audio_playback_parms_0x796fa303', AudioPlaybackParms.from_stream),
    0xd5f3e9c4: ('sound_enter_stunned', AudioPlaybackParms.from_stream),
    0x44c1f241: ('audio_playback_parms_0x44c1f241', AudioPlaybackParms.from_stream),
}
