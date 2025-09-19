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
from retro_data_structures.properties.echoes.archetypes.DamageVulnerability import DamageVulnerability
from retro_data_structures.properties.echoes.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class UnknownStruct14Json(typing_extensions.TypedDict):
        unknown_0xa0d037ee: float
        unknown_0x4f522994: float
        shadow_dash_speed: float
        unknown_0x5d02f384: float
        part: int
        audio_playback_parms: json_util.JsonObject
        sound_cloak: json_util.JsonObject
        sound_de_cloak: json_util.JsonObject
        shadow_decoy_vulnerability: json_util.JsonObject
        shadow_dash_vulnerability: json_util.JsonObject
    

@dataclasses.dataclass()
class UnknownStruct14(BaseProperty):
    unknown_0xa0d037ee: float = dataclasses.field(default=25.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa0d037ee, original_name='Unknown'
        ),
    })
    unknown_0x4f522994: float = dataclasses.field(default=40.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4f522994, original_name='Unknown'
        ),
    })
    shadow_dash_speed: float = dataclasses.field(default=25.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x87461cc6, original_name='ShadowDashSpeed'
        ),
    })
    unknown_0x5d02f384: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x5d02f384, original_name='Unknown'
        ),
    })
    part: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x2dc80b4b, original_name='PART'
        ),
    })
    audio_playback_parms: AudioPlaybackParms = dataclasses.field(default_factory=AudioPlaybackParms, metadata={
        'reflection': FieldReflection[AudioPlaybackParms](
            AudioPlaybackParms, id=0x03392283, original_name='AudioPlaybackParms', from_json=AudioPlaybackParms.from_json, to_json=AudioPlaybackParms.to_json
        ),
    })
    sound_cloak: AudioPlaybackParms = dataclasses.field(default_factory=AudioPlaybackParms, metadata={
        'reflection': FieldReflection[AudioPlaybackParms](
            AudioPlaybackParms, id=0x9dedcff1, original_name='Sound_Cloak', from_json=AudioPlaybackParms.from_json, to_json=AudioPlaybackParms.to_json
        ),
    })
    sound_de_cloak: AudioPlaybackParms = dataclasses.field(default_factory=AudioPlaybackParms, metadata={
        'reflection': FieldReflection[AudioPlaybackParms](
            AudioPlaybackParms, id=0xf740e01d, original_name='Sound_DeCloak', from_json=AudioPlaybackParms.from_json, to_json=AudioPlaybackParms.to_json
        ),
    })
    shadow_decoy_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0xb2f64bb4, original_name='ShadowDecoyVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    shadow_dash_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0xed067447, original_name='ShadowDashVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
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
        if property_count != 10:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa0d037ee
        unknown_0xa0d037ee = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4f522994
        unknown_0x4f522994 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x87461cc6
        shadow_dash_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5d02f384
        unknown_0x5d02f384 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2dc80b4b
        part = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x03392283
        audio_playback_parms = AudioPlaybackParms.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9dedcff1
        sound_cloak = AudioPlaybackParms.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf740e01d
        sound_de_cloak = AudioPlaybackParms.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb2f64bb4
        shadow_decoy_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xed067447
        shadow_dash_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        return cls(unknown_0xa0d037ee, unknown_0x4f522994, shadow_dash_speed, unknown_0x5d02f384, part, audio_playback_parms, sound_cloak, sound_de_cloak, shadow_decoy_vulnerability, shadow_dash_vulnerability)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\n')  # 10 properties

        data.write(b'\xa0\xd07\xee')  # 0xa0d037ee
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xa0d037ee))

        data.write(b'OR)\x94')  # 0x4f522994
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x4f522994))

        data.write(b'\x87F\x1c\xc6')  # 0x87461cc6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.shadow_dash_speed))

        data.write(b']\x02\xf3\x84')  # 0x5d02f384
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x5d02f384))

        data.write(b'-\xc8\x0bK')  # 0x2dc80b4b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.part))

        data.write(b'\x039"\x83')  # 0x3392283
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.audio_playback_parms.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x9d\xed\xcf\xf1')  # 0x9dedcff1
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.sound_cloak.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xf7@\xe0\x1d')  # 0xf740e01d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.sound_de_cloak.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xb2\xf6K\xb4')  # 0xb2f64bb4
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.shadow_decoy_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xed\x06tG')  # 0xed067447
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.shadow_dash_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct14Json", data)
        return cls(
            unknown_0xa0d037ee=json_data['unknown_0xa0d037ee'],
            unknown_0x4f522994=json_data['unknown_0x4f522994'],
            shadow_dash_speed=json_data['shadow_dash_speed'],
            unknown_0x5d02f384=json_data['unknown_0x5d02f384'],
            part=json_data['part'],
            audio_playback_parms=AudioPlaybackParms.from_json(json_data['audio_playback_parms']),
            sound_cloak=AudioPlaybackParms.from_json(json_data['sound_cloak']),
            sound_de_cloak=AudioPlaybackParms.from_json(json_data['sound_de_cloak']),
            shadow_decoy_vulnerability=DamageVulnerability.from_json(json_data['shadow_decoy_vulnerability']),
            shadow_dash_vulnerability=DamageVulnerability.from_json(json_data['shadow_dash_vulnerability']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unknown_0xa0d037ee': self.unknown_0xa0d037ee,
            'unknown_0x4f522994': self.unknown_0x4f522994,
            'shadow_dash_speed': self.shadow_dash_speed,
            'unknown_0x5d02f384': self.unknown_0x5d02f384,
            'part': self.part,
            'audio_playback_parms': self.audio_playback_parms.to_json(),
            'sound_cloak': self.sound_cloak.to_json(),
            'sound_de_cloak': self.sound_de_cloak.to_json(),
            'shadow_decoy_vulnerability': self.shadow_decoy_vulnerability.to_json(),
            'shadow_dash_vulnerability': self.shadow_dash_vulnerability.to_json(),
        }

    def _dependencies_for_part(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.part)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self._dependencies_for_part, "part", "AssetId"),
            (self.audio_playback_parms.dependencies_for, "audio_playback_parms", "AudioPlaybackParms"),
            (self.sound_cloak.dependencies_for, "sound_cloak", "AudioPlaybackParms"),
            (self.sound_de_cloak.dependencies_for, "sound_de_cloak", "AudioPlaybackParms"),
            (self.shadow_decoy_vulnerability.dependencies_for, "shadow_decoy_vulnerability", "DamageVulnerability"),
            (self.shadow_dash_vulnerability.dependencies_for, "shadow_dash_vulnerability", "DamageVulnerability"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for UnknownStruct14.{field_name} ({field_type}): {e}"
                )


def _decode_unknown_0xa0d037ee(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x4f522994(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_shadow_dash_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x5d02f384(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_part(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xa0d037ee: ('unknown_0xa0d037ee', _decode_unknown_0xa0d037ee),
    0x4f522994: ('unknown_0x4f522994', _decode_unknown_0x4f522994),
    0x87461cc6: ('shadow_dash_speed', _decode_shadow_dash_speed),
    0x5d02f384: ('unknown_0x5d02f384', _decode_unknown_0x5d02f384),
    0x2dc80b4b: ('part', _decode_part),
    0x3392283: ('audio_playback_parms', AudioPlaybackParms.from_stream),
    0x9dedcff1: ('sound_cloak', AudioPlaybackParms.from_stream),
    0xf740e01d: ('sound_de_cloak', AudioPlaybackParms.from_stream),
    0xb2f64bb4: ('shadow_decoy_vulnerability', DamageVulnerability.from_stream),
    0xed067447: ('shadow_dash_vulnerability', DamageVulnerability.from_stream),
}
