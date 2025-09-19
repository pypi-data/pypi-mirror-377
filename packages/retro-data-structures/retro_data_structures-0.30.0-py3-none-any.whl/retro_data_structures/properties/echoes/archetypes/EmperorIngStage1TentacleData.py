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
from retro_data_structures.properties.echoes.archetypes.DamageVulnerability import DamageVulnerability
from retro_data_structures.properties.echoes.archetypes.HealthInfo import HealthInfo

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class EmperorIngStage1TentacleDataJson(typing_extensions.TypedDict):
        health: json_util.JsonObject
        normal_vulnerability: json_util.JsonObject
        warp_attack_vulnerability: json_util.JsonObject
        melee_attack_vulnerability: json_util.JsonObject
        projectile_attack_vulnerability: json_util.JsonObject
        stay_retracted_time: float
        tentacle_damaged_sound: int
    

@dataclasses.dataclass()
class EmperorIngStage1TentacleData(BaseProperty):
    health: HealthInfo = dataclasses.field(default_factory=HealthInfo, metadata={
        'reflection': FieldReflection[HealthInfo](
            HealthInfo, id=0xcf90d15e, original_name='Health', from_json=HealthInfo.from_json, to_json=HealthInfo.to_json
        ),
    })
    normal_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0x29df61e1, original_name='NormalVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    warp_attack_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0x8d7378a4, original_name='WarpAttackVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    melee_attack_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0x6c79054f, original_name='MeleeAttackVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    projectile_attack_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0x3c2d2492, original_name='ProjectileAttackVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    stay_retracted_time: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x491c2657, original_name='StayRetractedTime'
        ),
    })
    tentacle_damaged_sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0xe19f4608, original_name='TentacleDamagedSound'
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
        if property_count != 7:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcf90d15e
        health = HealthInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x29df61e1
        normal_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8d7378a4
        warp_attack_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6c79054f
        melee_attack_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3c2d2492
        projectile_attack_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x491c2657
        stay_retracted_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe19f4608
        tentacle_damaged_sound = struct.unpack('>l', data.read(4))[0]
    
        return cls(health, normal_vulnerability, warp_attack_vulnerability, melee_attack_vulnerability, projectile_attack_vulnerability, stay_retracted_time, tentacle_damaged_sound)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x07')  # 7 properties

        data.write(b'\xcf\x90\xd1^')  # 0xcf90d15e
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.health.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b')\xdfa\xe1')  # 0x29df61e1
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.normal_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x8dsx\xa4')  # 0x8d7378a4
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.warp_attack_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'ly\x05O')  # 0x6c79054f
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.melee_attack_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'<-$\x92')  # 0x3c2d2492
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.projectile_attack_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'I\x1c&W')  # 0x491c2657
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.stay_retracted_time))

        data.write(b'\xe1\x9fF\x08')  # 0xe19f4608
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.tentacle_damaged_sound))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("EmperorIngStage1TentacleDataJson", data)
        return cls(
            health=HealthInfo.from_json(json_data['health']),
            normal_vulnerability=DamageVulnerability.from_json(json_data['normal_vulnerability']),
            warp_attack_vulnerability=DamageVulnerability.from_json(json_data['warp_attack_vulnerability']),
            melee_attack_vulnerability=DamageVulnerability.from_json(json_data['melee_attack_vulnerability']),
            projectile_attack_vulnerability=DamageVulnerability.from_json(json_data['projectile_attack_vulnerability']),
            stay_retracted_time=json_data['stay_retracted_time'],
            tentacle_damaged_sound=json_data['tentacle_damaged_sound'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'health': self.health.to_json(),
            'normal_vulnerability': self.normal_vulnerability.to_json(),
            'warp_attack_vulnerability': self.warp_attack_vulnerability.to_json(),
            'melee_attack_vulnerability': self.melee_attack_vulnerability.to_json(),
            'projectile_attack_vulnerability': self.projectile_attack_vulnerability.to_json(),
            'stay_retracted_time': self.stay_retracted_time,
            'tentacle_damaged_sound': self.tentacle_damaged_sound,
        }

    def _dependencies_for_tentacle_damaged_sound(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.tentacle_damaged_sound)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.health.dependencies_for, "health", "HealthInfo"),
            (self.normal_vulnerability.dependencies_for, "normal_vulnerability", "DamageVulnerability"),
            (self.warp_attack_vulnerability.dependencies_for, "warp_attack_vulnerability", "DamageVulnerability"),
            (self.melee_attack_vulnerability.dependencies_for, "melee_attack_vulnerability", "DamageVulnerability"),
            (self.projectile_attack_vulnerability.dependencies_for, "projectile_attack_vulnerability", "DamageVulnerability"),
            (self._dependencies_for_tentacle_damaged_sound, "tentacle_damaged_sound", "int"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for EmperorIngStage1TentacleData.{field_name} ({field_type}): {e}"
                )


def _decode_stay_retracted_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_tentacle_damaged_sound(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xcf90d15e: ('health', HealthInfo.from_stream),
    0x29df61e1: ('normal_vulnerability', DamageVulnerability.from_stream),
    0x8d7378a4: ('warp_attack_vulnerability', DamageVulnerability.from_stream),
    0x6c79054f: ('melee_attack_vulnerability', DamageVulnerability.from_stream),
    0x3c2d2492: ('projectile_attack_vulnerability', DamageVulnerability.from_stream),
    0x491c2657: ('stay_retracted_time', _decode_stay_retracted_time),
    0xe19f4608: ('tentacle_damaged_sound', _decode_tentacle_damaged_sound),
}
