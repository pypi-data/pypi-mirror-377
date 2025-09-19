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
from retro_data_structures.properties.corruption.archetypes.DamageInfo import DamageInfo
from retro_data_structures.properties.corruption.archetypes.DamageVulnerability import DamageVulnerability
from retro_data_structures.properties.corruption.archetypes.UnknownStruct6 import UnknownStruct6
from retro_data_structures.properties.corruption.core.AnimationParameters import AnimationParameters
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    class UnknownStruct2Json(typing_extensions.TypedDict):
        camera_animation_info: json_util.JsonObject
        overload_damage_threshold: float
        open_hatch_vulnerability: json_util.JsonObject
        unknown_0xa4b62aa9: float
        unknown_0xb64ea21c: float
        unknown_0xa13b1ba9: float
        unknown_0xd294848c: float
        unknown_0x9c425325: float
        unknown_0xfa22836a: float
        unknown_0xed410449: float
        unknown_0xf768d625: float
        tentacle_animation_info: json_util.JsonObject
        unknown_0x52806eff: int
        missile_weapon: int
        missile_damage: json_util.JsonObject
        missile_explode_threshold: float
        part: int
        missile_explode_sound: int
        fire_missile_time: float
        unknown_0xa4166e3c: float
        unknown_0xaa7d527d: float
        unknown_0xf707c050: float
        unknown_0x4128ff6d: float
        unknown_0x3b6218da: float
        unknown_0x71946eec: float
        unknown_0xa184d013: float
        unknown_0x09d9bd17: float
        camera_sequence_duration: float
        min_camera_sequences: int
        max_camera_sequences: int
        unknown_0x193c7751: float
        unknown_0x0d55794a: float
        unknown_0x72fb67da: float
        camera_damage_threshold: float
        camera_shock_time: float
        dizzy_state_time: float
        unknown_0x0a072c48: float
        unknown_0xdde5ac10: float
        unknown_0x8c63f9d0: float
        unknown_0x6b7e5f47: float
        unknown_0x6afe0147: float
        unknown_0x04721a06: float
        unknown_struct6: json_util.JsonObject
    

@dataclasses.dataclass()
class UnknownStruct2(BaseProperty):
    camera_animation_info: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0xc107a48a, original_name='CameraAnimationInfo', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    overload_damage_threshold: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa6c47cd3, original_name='OverloadDamageThreshold'
        ),
    })
    open_hatch_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0x0fce03ca, original_name='OpenHatchVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    unknown_0xa4b62aa9: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa4b62aa9, original_name='Unknown'
        ),
    })
    unknown_0xb64ea21c: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb64ea21c, original_name='Unknown'
        ),
    })
    unknown_0xa13b1ba9: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa13b1ba9, original_name='Unknown'
        ),
    })
    unknown_0xd294848c: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd294848c, original_name='Unknown'
        ),
    })
    unknown_0x9c425325: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9c425325, original_name='Unknown'
        ),
    })
    unknown_0xfa22836a: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xfa22836a, original_name='Unknown'
        ),
    })
    unknown_0xed410449: float = dataclasses.field(default=8.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xed410449, original_name='Unknown'
        ),
    })
    unknown_0xf768d625: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf768d625, original_name='Unknown'
        ),
    })
    tentacle_animation_info: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0xa229ff6a, original_name='TentacleAnimationInfo', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    unknown_0x52806eff: int = dataclasses.field(default=2, metadata={
        'reflection': FieldReflection[int](
            int, id=0x52806eff, original_name='Unknown'
        ),
    })
    missile_weapon: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x2ea31f83, original_name='MissileWeapon'
        ),
    })
    missile_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x258cfb4d, original_name='MissileDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    missile_explode_threshold: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7becdb66, original_name='MissileExplodeThreshold'
        ),
    })
    part: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x87afe8d8, original_name='PART'
        ),
    })
    missile_explode_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x3dfd1c4f, original_name='MissileExplodeSound'
        ),
    })
    fire_missile_time: float = dataclasses.field(default=6.75, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb8bf561e, original_name='FireMissileTime'
        ),
    })
    unknown_0xa4166e3c: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa4166e3c, original_name='Unknown'
        ),
    })
    unknown_0xaa7d527d: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xaa7d527d, original_name='Unknown'
        ),
    })
    unknown_0xf707c050: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf707c050, original_name='Unknown'
        ),
    })
    unknown_0x4128ff6d: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4128ff6d, original_name='Unknown'
        ),
    })
    unknown_0x3b6218da: float = dataclasses.field(default=0.25, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3b6218da, original_name='Unknown'
        ),
    })
    unknown_0x71946eec: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x71946eec, original_name='Unknown'
        ),
    })
    unknown_0xa184d013: float = dataclasses.field(default=3.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa184d013, original_name='Unknown'
        ),
    })
    unknown_0x09d9bd17: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x09d9bd17, original_name='Unknown'
        ),
    })
    camera_sequence_duration: float = dataclasses.field(default=8.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x53c1d089, original_name='CameraSequenceDuration'
        ),
    })
    min_camera_sequences: int = dataclasses.field(default=1, metadata={
        'reflection': FieldReflection[int](
            int, id=0x306fd39a, original_name='MinCameraSequences'
        ),
    })
    max_camera_sequences: int = dataclasses.field(default=3, metadata={
        'reflection': FieldReflection[int](
            int, id=0x232a3531, original_name='MaxCameraSequences'
        ),
    })
    unknown_0x193c7751: float = dataclasses.field(default=1.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x193c7751, original_name='Unknown'
        ),
    })
    unknown_0x0d55794a: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0d55794a, original_name='Unknown'
        ),
    })
    unknown_0x72fb67da: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x72fb67da, original_name='Unknown'
        ),
    })
    camera_damage_threshold: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xbdb18b2f, original_name='CameraDamageThreshold'
        ),
    })
    camera_shock_time: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0e958d9e, original_name='CameraShockTime'
        ),
    })
    dizzy_state_time: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x251c55e3, original_name='DizzyStateTime'
        ),
    })
    unknown_0x0a072c48: float = dataclasses.field(default=0.6000000238418579, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0a072c48, original_name='Unknown'
        ),
    })
    unknown_0xdde5ac10: float = dataclasses.field(default=0.30000001192092896, metadata={
        'reflection': FieldReflection[float](
            float, id=0xdde5ac10, original_name='Unknown'
        ),
    })
    unknown_0x8c63f9d0: float = dataclasses.field(default=0.75, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8c63f9d0, original_name='Unknown'
        ),
    })
    unknown_0x6b7e5f47: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6b7e5f47, original_name='Unknown'
        ),
    })
    unknown_0x6afe0147: float = dataclasses.field(default=0.75, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6afe0147, original_name='Unknown'
        ),
    })
    unknown_0x04721a06: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x04721a06, original_name='Unknown'
        ),
    })
    unknown_struct6: UnknownStruct6 = dataclasses.field(default_factory=UnknownStruct6, metadata={
        'reflection': FieldReflection[UnknownStruct6](
            UnknownStruct6, id=0xd8579ba3, original_name='UnknownStruct6', from_json=UnknownStruct6.from_json, to_json=UnknownStruct6.to_json
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.CORRUPTION

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
        if property_count != 43:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc107a48a
        camera_animation_info = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa6c47cd3
        overload_damage_threshold = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0fce03ca
        open_hatch_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa4b62aa9
        unknown_0xa4b62aa9 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb64ea21c
        unknown_0xb64ea21c = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa13b1ba9
        unknown_0xa13b1ba9 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd294848c
        unknown_0xd294848c = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9c425325
        unknown_0x9c425325 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfa22836a
        unknown_0xfa22836a = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xed410449
        unknown_0xed410449 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf768d625
        unknown_0xf768d625 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa229ff6a
        tentacle_animation_info = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x52806eff
        unknown_0x52806eff = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2ea31f83
        missile_weapon = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x258cfb4d
        missile_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7becdb66
        missile_explode_threshold = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x87afe8d8
        part = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3dfd1c4f
        missile_explode_sound = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb8bf561e
        fire_missile_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa4166e3c
        unknown_0xa4166e3c = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xaa7d527d
        unknown_0xaa7d527d = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf707c050
        unknown_0xf707c050 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4128ff6d
        unknown_0x4128ff6d = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3b6218da
        unknown_0x3b6218da = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x71946eec
        unknown_0x71946eec = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa184d013
        unknown_0xa184d013 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x09d9bd17
        unknown_0x09d9bd17 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x53c1d089
        camera_sequence_duration = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x306fd39a
        min_camera_sequences = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x232a3531
        max_camera_sequences = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x193c7751
        unknown_0x193c7751 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0d55794a
        unknown_0x0d55794a = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x72fb67da
        unknown_0x72fb67da = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbdb18b2f
        camera_damage_threshold = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0e958d9e
        camera_shock_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x251c55e3
        dizzy_state_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0a072c48
        unknown_0x0a072c48 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdde5ac10
        unknown_0xdde5ac10 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8c63f9d0
        unknown_0x8c63f9d0 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6b7e5f47
        unknown_0x6b7e5f47 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6afe0147
        unknown_0x6afe0147 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x04721a06
        unknown_0x04721a06 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd8579ba3
        unknown_struct6 = UnknownStruct6.from_stream(data, property_size)
    
        return cls(camera_animation_info, overload_damage_threshold, open_hatch_vulnerability, unknown_0xa4b62aa9, unknown_0xb64ea21c, unknown_0xa13b1ba9, unknown_0xd294848c, unknown_0x9c425325, unknown_0xfa22836a, unknown_0xed410449, unknown_0xf768d625, tentacle_animation_info, unknown_0x52806eff, missile_weapon, missile_damage, missile_explode_threshold, part, missile_explode_sound, fire_missile_time, unknown_0xa4166e3c, unknown_0xaa7d527d, unknown_0xf707c050, unknown_0x4128ff6d, unknown_0x3b6218da, unknown_0x71946eec, unknown_0xa184d013, unknown_0x09d9bd17, camera_sequence_duration, min_camera_sequences, max_camera_sequences, unknown_0x193c7751, unknown_0x0d55794a, unknown_0x72fb67da, camera_damage_threshold, camera_shock_time, dizzy_state_time, unknown_0x0a072c48, unknown_0xdde5ac10, unknown_0x8c63f9d0, unknown_0x6b7e5f47, unknown_0x6afe0147, unknown_0x04721a06, unknown_struct6)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        num_properties_offset = data.tell()
        data.write(b'\x00*')  # 42 properties
        num_properties_written = 42

        data.write(b'\xc1\x07\xa4\x8a')  # 0xc107a48a
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.camera_animation_info.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xa6\xc4|\xd3')  # 0xa6c47cd3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.overload_damage_threshold))

        data.write(b'\x0f\xce\x03\xca')  # 0xfce03ca
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.open_hatch_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xa4\xb6*\xa9')  # 0xa4b62aa9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xa4b62aa9))

        data.write(b'\xb6N\xa2\x1c')  # 0xb64ea21c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xb64ea21c))

        data.write(b'\xa1;\x1b\xa9')  # 0xa13b1ba9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xa13b1ba9))

        data.write(b'\xd2\x94\x84\x8c')  # 0xd294848c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xd294848c))

        data.write(b'\x9cBS%')  # 0x9c425325
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x9c425325))

        data.write(b'\xfa"\x83j')  # 0xfa22836a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xfa22836a))

        data.write(b'\xedA\x04I')  # 0xed410449
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xed410449))

        data.write(b'\xf7h\xd6%')  # 0xf768d625
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xf768d625))

        data.write(b'\xa2)\xffj')  # 0xa229ff6a
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.tentacle_animation_info.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'R\x80n\xff')  # 0x52806eff
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x52806eff))

        data.write(b'.\xa3\x1f\x83')  # 0x2ea31f83
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.missile_weapon))

        data.write(b'%\x8c\xfbM')  # 0x258cfb4d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.missile_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'{\xec\xdbf')  # 0x7becdb66
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.missile_explode_threshold))

        data.write(b'\x87\xaf\xe8\xd8')  # 0x87afe8d8
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.part))

        data.write(b'=\xfd\x1cO')  # 0x3dfd1c4f
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.missile_explode_sound))

        data.write(b'\xb8\xbfV\x1e')  # 0xb8bf561e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.fire_missile_time))

        data.write(b'\xa4\x16n<')  # 0xa4166e3c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xa4166e3c))

        data.write(b'\xaa}R}')  # 0xaa7d527d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xaa7d527d))

        data.write(b'\xf7\x07\xc0P')  # 0xf707c050
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xf707c050))

        data.write(b'A(\xffm')  # 0x4128ff6d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x4128ff6d))

        data.write(b';b\x18\xda')  # 0x3b6218da
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x3b6218da))

        data.write(b'q\x94n\xec')  # 0x71946eec
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x71946eec))

        data.write(b'\xa1\x84\xd0\x13')  # 0xa184d013
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xa184d013))

        data.write(b'\t\xd9\xbd\x17')  # 0x9d9bd17
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x09d9bd17))

        data.write(b'S\xc1\xd0\x89')  # 0x53c1d089
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.camera_sequence_duration))

        data.write(b'0o\xd3\x9a')  # 0x306fd39a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.min_camera_sequences))

        data.write(b'#*51')  # 0x232a3531
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.max_camera_sequences))

        data.write(b'\x19<wQ')  # 0x193c7751
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x193c7751))

        data.write(b'\rUyJ')  # 0xd55794a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x0d55794a))

        data.write(b'r\xfbg\xda')  # 0x72fb67da
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x72fb67da))

        data.write(b'\xbd\xb1\x8b/')  # 0xbdb18b2f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.camera_damage_threshold))

        data.write(b'\x0e\x95\x8d\x9e')  # 0xe958d9e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.camera_shock_time))

        data.write(b'%\x1cU\xe3')  # 0x251c55e3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.dizzy_state_time))

        data.write(b'\n\x07,H')  # 0xa072c48
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x0a072c48))

        data.write(b'\xdd\xe5\xac\x10')  # 0xdde5ac10
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xdde5ac10))

        data.write(b'\x8cc\xf9\xd0')  # 0x8c63f9d0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x8c63f9d0))

        data.write(b'k~_G')  # 0x6b7e5f47
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x6b7e5f47))

        data.write(b'j\xfe\x01G')  # 0x6afe0147
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x6afe0147))

        data.write(b'\x04r\x1a\x06')  # 0x4721a06
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x04721a06))

        if self.unknown_struct6 != default_override.get('unknown_struct6', UnknownStruct6()):
            num_properties_written += 1
            data.write(b'\xd8W\x9b\xa3')  # 0xd8579ba3
            before = data.tell()
            data.write(b'\x00\x00')  # size placeholder
            self.unknown_struct6.to_stream(data)
            after = data.tell()
            data.seek(before)
            data.write(struct.pack(">H", after - before - 2))
            data.seek(after)

        if num_properties_written != 42:
            struct_end_offset = data.tell()
            data.seek(num_properties_offset)
            data.write(struct.pack(">H", num_properties_written))
            data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct2Json", data)
        return cls(
            camera_animation_info=AnimationParameters.from_json(json_data['camera_animation_info']),
            overload_damage_threshold=json_data['overload_damage_threshold'],
            open_hatch_vulnerability=DamageVulnerability.from_json(json_data['open_hatch_vulnerability']),
            unknown_0xa4b62aa9=json_data['unknown_0xa4b62aa9'],
            unknown_0xb64ea21c=json_data['unknown_0xb64ea21c'],
            unknown_0xa13b1ba9=json_data['unknown_0xa13b1ba9'],
            unknown_0xd294848c=json_data['unknown_0xd294848c'],
            unknown_0x9c425325=json_data['unknown_0x9c425325'],
            unknown_0xfa22836a=json_data['unknown_0xfa22836a'],
            unknown_0xed410449=json_data['unknown_0xed410449'],
            unknown_0xf768d625=json_data['unknown_0xf768d625'],
            tentacle_animation_info=AnimationParameters.from_json(json_data['tentacle_animation_info']),
            unknown_0x52806eff=json_data['unknown_0x52806eff'],
            missile_weapon=json_data['missile_weapon'],
            missile_damage=DamageInfo.from_json(json_data['missile_damage']),
            missile_explode_threshold=json_data['missile_explode_threshold'],
            part=json_data['part'],
            missile_explode_sound=json_data['missile_explode_sound'],
            fire_missile_time=json_data['fire_missile_time'],
            unknown_0xa4166e3c=json_data['unknown_0xa4166e3c'],
            unknown_0xaa7d527d=json_data['unknown_0xaa7d527d'],
            unknown_0xf707c050=json_data['unknown_0xf707c050'],
            unknown_0x4128ff6d=json_data['unknown_0x4128ff6d'],
            unknown_0x3b6218da=json_data['unknown_0x3b6218da'],
            unknown_0x71946eec=json_data['unknown_0x71946eec'],
            unknown_0xa184d013=json_data['unknown_0xa184d013'],
            unknown_0x09d9bd17=json_data['unknown_0x09d9bd17'],
            camera_sequence_duration=json_data['camera_sequence_duration'],
            min_camera_sequences=json_data['min_camera_sequences'],
            max_camera_sequences=json_data['max_camera_sequences'],
            unknown_0x193c7751=json_data['unknown_0x193c7751'],
            unknown_0x0d55794a=json_data['unknown_0x0d55794a'],
            unknown_0x72fb67da=json_data['unknown_0x72fb67da'],
            camera_damage_threshold=json_data['camera_damage_threshold'],
            camera_shock_time=json_data['camera_shock_time'],
            dizzy_state_time=json_data['dizzy_state_time'],
            unknown_0x0a072c48=json_data['unknown_0x0a072c48'],
            unknown_0xdde5ac10=json_data['unknown_0xdde5ac10'],
            unknown_0x8c63f9d0=json_data['unknown_0x8c63f9d0'],
            unknown_0x6b7e5f47=json_data['unknown_0x6b7e5f47'],
            unknown_0x6afe0147=json_data['unknown_0x6afe0147'],
            unknown_0x04721a06=json_data['unknown_0x04721a06'],
            unknown_struct6=UnknownStruct6.from_json(json_data['unknown_struct6']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'camera_animation_info': self.camera_animation_info.to_json(),
            'overload_damage_threshold': self.overload_damage_threshold,
            'open_hatch_vulnerability': self.open_hatch_vulnerability.to_json(),
            'unknown_0xa4b62aa9': self.unknown_0xa4b62aa9,
            'unknown_0xb64ea21c': self.unknown_0xb64ea21c,
            'unknown_0xa13b1ba9': self.unknown_0xa13b1ba9,
            'unknown_0xd294848c': self.unknown_0xd294848c,
            'unknown_0x9c425325': self.unknown_0x9c425325,
            'unknown_0xfa22836a': self.unknown_0xfa22836a,
            'unknown_0xed410449': self.unknown_0xed410449,
            'unknown_0xf768d625': self.unknown_0xf768d625,
            'tentacle_animation_info': self.tentacle_animation_info.to_json(),
            'unknown_0x52806eff': self.unknown_0x52806eff,
            'missile_weapon': self.missile_weapon,
            'missile_damage': self.missile_damage.to_json(),
            'missile_explode_threshold': self.missile_explode_threshold,
            'part': self.part,
            'missile_explode_sound': self.missile_explode_sound,
            'fire_missile_time': self.fire_missile_time,
            'unknown_0xa4166e3c': self.unknown_0xa4166e3c,
            'unknown_0xaa7d527d': self.unknown_0xaa7d527d,
            'unknown_0xf707c050': self.unknown_0xf707c050,
            'unknown_0x4128ff6d': self.unknown_0x4128ff6d,
            'unknown_0x3b6218da': self.unknown_0x3b6218da,
            'unknown_0x71946eec': self.unknown_0x71946eec,
            'unknown_0xa184d013': self.unknown_0xa184d013,
            'unknown_0x09d9bd17': self.unknown_0x09d9bd17,
            'camera_sequence_duration': self.camera_sequence_duration,
            'min_camera_sequences': self.min_camera_sequences,
            'max_camera_sequences': self.max_camera_sequences,
            'unknown_0x193c7751': self.unknown_0x193c7751,
            'unknown_0x0d55794a': self.unknown_0x0d55794a,
            'unknown_0x72fb67da': self.unknown_0x72fb67da,
            'camera_damage_threshold': self.camera_damage_threshold,
            'camera_shock_time': self.camera_shock_time,
            'dizzy_state_time': self.dizzy_state_time,
            'unknown_0x0a072c48': self.unknown_0x0a072c48,
            'unknown_0xdde5ac10': self.unknown_0xdde5ac10,
            'unknown_0x8c63f9d0': self.unknown_0x8c63f9d0,
            'unknown_0x6b7e5f47': self.unknown_0x6b7e5f47,
            'unknown_0x6afe0147': self.unknown_0x6afe0147,
            'unknown_0x04721a06': self.unknown_0x04721a06,
            'unknown_struct6': self.unknown_struct6.to_json(),
        }


def _decode_overload_damage_threshold(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xa4b62aa9(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xb64ea21c(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xa13b1ba9(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xd294848c(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x9c425325(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xfa22836a(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xed410449(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xf768d625(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x52806eff(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_missile_weapon(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_missile_explode_threshold(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_part(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_missile_explode_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_fire_missile_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xa4166e3c(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xaa7d527d(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xf707c050(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x4128ff6d(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x3b6218da(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x71946eec(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xa184d013(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x09d9bd17(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_camera_sequence_duration(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_min_camera_sequences(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_max_camera_sequences(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x193c7751(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x0d55794a(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x72fb67da(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_camera_damage_threshold(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_camera_shock_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_dizzy_state_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x0a072c48(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xdde5ac10(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x8c63f9d0(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x6b7e5f47(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x6afe0147(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x04721a06(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xc107a48a: ('camera_animation_info', AnimationParameters.from_stream),
    0xa6c47cd3: ('overload_damage_threshold', _decode_overload_damage_threshold),
    0xfce03ca: ('open_hatch_vulnerability', DamageVulnerability.from_stream),
    0xa4b62aa9: ('unknown_0xa4b62aa9', _decode_unknown_0xa4b62aa9),
    0xb64ea21c: ('unknown_0xb64ea21c', _decode_unknown_0xb64ea21c),
    0xa13b1ba9: ('unknown_0xa13b1ba9', _decode_unknown_0xa13b1ba9),
    0xd294848c: ('unknown_0xd294848c', _decode_unknown_0xd294848c),
    0x9c425325: ('unknown_0x9c425325', _decode_unknown_0x9c425325),
    0xfa22836a: ('unknown_0xfa22836a', _decode_unknown_0xfa22836a),
    0xed410449: ('unknown_0xed410449', _decode_unknown_0xed410449),
    0xf768d625: ('unknown_0xf768d625', _decode_unknown_0xf768d625),
    0xa229ff6a: ('tentacle_animation_info', AnimationParameters.from_stream),
    0x52806eff: ('unknown_0x52806eff', _decode_unknown_0x52806eff),
    0x2ea31f83: ('missile_weapon', _decode_missile_weapon),
    0x258cfb4d: ('missile_damage', DamageInfo.from_stream),
    0x7becdb66: ('missile_explode_threshold', _decode_missile_explode_threshold),
    0x87afe8d8: ('part', _decode_part),
    0x3dfd1c4f: ('missile_explode_sound', _decode_missile_explode_sound),
    0xb8bf561e: ('fire_missile_time', _decode_fire_missile_time),
    0xa4166e3c: ('unknown_0xa4166e3c', _decode_unknown_0xa4166e3c),
    0xaa7d527d: ('unknown_0xaa7d527d', _decode_unknown_0xaa7d527d),
    0xf707c050: ('unknown_0xf707c050', _decode_unknown_0xf707c050),
    0x4128ff6d: ('unknown_0x4128ff6d', _decode_unknown_0x4128ff6d),
    0x3b6218da: ('unknown_0x3b6218da', _decode_unknown_0x3b6218da),
    0x71946eec: ('unknown_0x71946eec', _decode_unknown_0x71946eec),
    0xa184d013: ('unknown_0xa184d013', _decode_unknown_0xa184d013),
    0x9d9bd17: ('unknown_0x09d9bd17', _decode_unknown_0x09d9bd17),
    0x53c1d089: ('camera_sequence_duration', _decode_camera_sequence_duration),
    0x306fd39a: ('min_camera_sequences', _decode_min_camera_sequences),
    0x232a3531: ('max_camera_sequences', _decode_max_camera_sequences),
    0x193c7751: ('unknown_0x193c7751', _decode_unknown_0x193c7751),
    0xd55794a: ('unknown_0x0d55794a', _decode_unknown_0x0d55794a),
    0x72fb67da: ('unknown_0x72fb67da', _decode_unknown_0x72fb67da),
    0xbdb18b2f: ('camera_damage_threshold', _decode_camera_damage_threshold),
    0xe958d9e: ('camera_shock_time', _decode_camera_shock_time),
    0x251c55e3: ('dizzy_state_time', _decode_dizzy_state_time),
    0xa072c48: ('unknown_0x0a072c48', _decode_unknown_0x0a072c48),
    0xdde5ac10: ('unknown_0xdde5ac10', _decode_unknown_0xdde5ac10),
    0x8c63f9d0: ('unknown_0x8c63f9d0', _decode_unknown_0x8c63f9d0),
    0x6b7e5f47: ('unknown_0x6b7e5f47', _decode_unknown_0x6b7e5f47),
    0x6afe0147: ('unknown_0x6afe0147', _decode_unknown_0x6afe0147),
    0x4721a06: ('unknown_0x04721a06', _decode_unknown_0x04721a06),
    0xd8579ba3: ('unknown_struct6', UnknownStruct6.from_stream),
}
