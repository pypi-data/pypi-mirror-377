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
from retro_data_structures.properties.prime.archetypes.DamageInfo import DamageInfo
from retro_data_structures.properties.prime.archetypes.DamageVulnerability import DamageVulnerability
from retro_data_structures.properties.prime.archetypes.HealthInfo import HealthInfo
from retro_data_structures.properties.prime.core.AnimationParameters import AnimationParameters
from retro_data_structures.properties.prime.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.prime.core.Vector import Vector

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class PatternedAITypedefJson(typing_extensions.TypedDict):
        mass: float
        speed: float
        turn_speed: float
        detection_range: float
        detection_height_range: float
        detection_angle: float
        min_attack_range: float
        max_attack_range: float
        average_attack_time: float
        attack_time_variation: float
        leash_radius: float
        player_leash_radius: float
        player_leash_time: float
        contact_damage: json_util.JsonObject
        damage_wait_time: float
        unnamed: json_util.JsonObject
        vulnerability: json_util.JsonObject
        unknown_1: float
        unknown_2: float
        unknown_3: json_util.JsonValue
        unknown_4: float
        unknown_5: float
        unknown_6: float
        unknown_7: float
        death_sound: int
        animation_parameters: json_util.JsonObject
        active: bool
        state_machine: int
        unknown_8: float
        unknown_9: float
        unknown_10: float
        unknown_11: int
        unknown_12: json_util.JsonValue
        particle_1: int
        unknown_13: int
        unknown_14: json_util.JsonValue
        particle_2: int
        ice_shatter_sound: int
    

@dataclasses.dataclass()
class PatternedAITypedef(BaseProperty):
    mass: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000000, original_name='Mass'
        ),
    })
    speed: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000001, original_name='Speed'
        ),
    })
    turn_speed: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000002, original_name='Turn Speed'
        ),
    })
    detection_range: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000003, original_name='Detection Range'
        ),
    })
    detection_height_range: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000004, original_name='Detection Height Range'
        ),
    })
    detection_angle: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000005, original_name='Detection Angle'
        ),
    })
    min_attack_range: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000006, original_name='Min Attack Range'
        ),
    })
    max_attack_range: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000007, original_name='Max Attack Range'
        ),
    })
    average_attack_time: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000008, original_name='Average Attack Time'
        ),
    })
    attack_time_variation: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000009, original_name='Attack Time Variation'
        ),
    })
    leash_radius: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0000000a, original_name='Leash Radius'
        ),
    })
    player_leash_radius: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0000000b, original_name='Player Leash Radius'
        ),
    })
    player_leash_time: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0000000c, original_name='Player Leash Time'
        ),
    })
    contact_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x0000000d, original_name='ContactDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    damage_wait_time: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0000000e, original_name='Damage Wait Time'
        ),
    })
    unnamed: HealthInfo = dataclasses.field(default_factory=HealthInfo, metadata={
        'reflection': FieldReflection[HealthInfo](
            HealthInfo, id=0x0000000f, original_name='15', from_json=HealthInfo.from_json, to_json=HealthInfo.to_json
        ),
    })
    vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0x00000010, original_name='Vulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    unknown_1: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000011, original_name='Unknown 1'
        ),
    })
    unknown_2: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000012, original_name='Unknown 2'
        ),
    })
    unknown_3: Vector = dataclasses.field(default_factory=Vector, metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x00000013, original_name='Unknown 3', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    unknown_4: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000014, original_name='Unknown 4'
        ),
    })
    unknown_5: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000015, original_name='Unknown 5'
        ),
    })
    unknown_6: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000016, original_name='Unknown 6'
        ),
    })
    unknown_7: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000017, original_name='Unknown 7'
        ),
    })
    death_sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x00000018, original_name='Death Sound'
        ),
    })
    animation_parameters: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0x00000019, original_name='AnimationParameters', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    active: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x0000001a, original_name='Active'
        ),
    })
    state_machine: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['AFSM'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0000001b, original_name='State Machine'
        ),
    })
    unknown_8: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0000001c, original_name='Unknown 8'
        ),
    })
    unknown_9: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0000001d, original_name='Unknown 9'
        ),
    })
    unknown_10: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0000001e, original_name='Unknown 10'
        ),
    })
    unknown_11: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x0000001f, original_name='Unknown 11'
        ),
    })
    unknown_12: Vector = dataclasses.field(default_factory=Vector, metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x00000020, original_name='Unknown 12', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    particle_1: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000021, original_name='Particle 1'
        ),
    })
    unknown_13: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000022, original_name='Unknown 13'
        ),
    })
    unknown_14: Vector = dataclasses.field(default_factory=Vector, metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x00000023, original_name='Unknown 14', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    particle_2: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000024, original_name='Particle 2'
        ),
    })
    ice_shatter_sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x00000025, original_name='Ice Shatter Sound'
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.PRIME

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        mass = struct.unpack('>f', data.read(4))[0]
        speed = struct.unpack('>f', data.read(4))[0]
        turn_speed = struct.unpack('>f', data.read(4))[0]
        detection_range = struct.unpack('>f', data.read(4))[0]
        detection_height_range = struct.unpack('>f', data.read(4))[0]
        detection_angle = struct.unpack('>f', data.read(4))[0]
        min_attack_range = struct.unpack('>f', data.read(4))[0]
        max_attack_range = struct.unpack('>f', data.read(4))[0]
        average_attack_time = struct.unpack('>f', data.read(4))[0]
        attack_time_variation = struct.unpack('>f', data.read(4))[0]
        leash_radius = struct.unpack('>f', data.read(4))[0]
        player_leash_radius = struct.unpack('>f', data.read(4))[0]
        player_leash_time = struct.unpack('>f', data.read(4))[0]
        contact_damage = DamageInfo.from_stream(data, property_size)
        damage_wait_time = struct.unpack('>f', data.read(4))[0]
        unnamed = HealthInfo.from_stream(data, property_size)
        vulnerability = DamageVulnerability.from_stream(data, property_size)
        unknown_1 = struct.unpack('>f', data.read(4))[0]
        unknown_2 = struct.unpack('>f', data.read(4))[0]
        unknown_3 = Vector.from_stream(data)
        unknown_4 = struct.unpack('>f', data.read(4))[0]
        unknown_5 = struct.unpack('>f', data.read(4))[0]
        unknown_6 = struct.unpack('>f', data.read(4))[0]
        unknown_7 = struct.unpack('>f', data.read(4))[0]
        death_sound = struct.unpack('>l', data.read(4))[0]
        animation_parameters = AnimationParameters.from_stream(data, property_size)
        active = struct.unpack('>?', data.read(1))[0]
        state_machine = struct.unpack(">L", data.read(4))[0]
        unknown_8 = struct.unpack('>f', data.read(4))[0]
        unknown_9 = struct.unpack('>f', data.read(4))[0]
        unknown_10 = struct.unpack('>f', data.read(4))[0]
        unknown_11 = struct.unpack('>l', data.read(4))[0]
        unknown_12 = Vector.from_stream(data)
        particle_1 = struct.unpack(">L", data.read(4))[0]
        unknown_13 = struct.unpack('>l', data.read(4))[0]
        unknown_14 = Vector.from_stream(data)
        particle_2 = struct.unpack(">L", data.read(4))[0]
        ice_shatter_sound = struct.unpack('>l', data.read(4))[0]
        return cls(mass, speed, turn_speed, detection_range, detection_height_range, detection_angle, min_attack_range, max_attack_range, average_attack_time, attack_time_variation, leash_radius, player_leash_radius, player_leash_time, contact_damage, damage_wait_time, unnamed, vulnerability, unknown_1, unknown_2, unknown_3, unknown_4, unknown_5, unknown_6, unknown_7, death_sound, animation_parameters, active, state_machine, unknown_8, unknown_9, unknown_10, unknown_11, unknown_12, particle_1, unknown_13, unknown_14, particle_2, ice_shatter_sound)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(struct.pack('>f', self.mass))
        data.write(struct.pack('>f', self.speed))
        data.write(struct.pack('>f', self.turn_speed))
        data.write(struct.pack('>f', self.detection_range))
        data.write(struct.pack('>f', self.detection_height_range))
        data.write(struct.pack('>f', self.detection_angle))
        data.write(struct.pack('>f', self.min_attack_range))
        data.write(struct.pack('>f', self.max_attack_range))
        data.write(struct.pack('>f', self.average_attack_time))
        data.write(struct.pack('>f', self.attack_time_variation))
        data.write(struct.pack('>f', self.leash_radius))
        data.write(struct.pack('>f', self.player_leash_radius))
        data.write(struct.pack('>f', self.player_leash_time))
        self.contact_damage.to_stream(data)
        data.write(struct.pack('>f', self.damage_wait_time))
        self.unnamed.to_stream(data)
        self.vulnerability.to_stream(data)
        data.write(struct.pack('>f', self.unknown_1))
        data.write(struct.pack('>f', self.unknown_2))
        self.unknown_3.to_stream(data)
        data.write(struct.pack('>f', self.unknown_4))
        data.write(struct.pack('>f', self.unknown_5))
        data.write(struct.pack('>f', self.unknown_6))
        data.write(struct.pack('>f', self.unknown_7))
        data.write(struct.pack('>l', self.death_sound))
        self.animation_parameters.to_stream(data)
        data.write(struct.pack('>?', self.active))
        data.write(struct.pack(">L", self.state_machine))
        data.write(struct.pack('>f', self.unknown_8))
        data.write(struct.pack('>f', self.unknown_9))
        data.write(struct.pack('>f', self.unknown_10))
        data.write(struct.pack('>l', self.unknown_11))
        self.unknown_12.to_stream(data)
        data.write(struct.pack(">L", self.particle_1))
        data.write(struct.pack('>l', self.unknown_13))
        self.unknown_14.to_stream(data)
        data.write(struct.pack(">L", self.particle_2))
        data.write(struct.pack('>l', self.ice_shatter_sound))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("PatternedAITypedefJson", data)
        return cls(
            mass=json_data['mass'],
            speed=json_data['speed'],
            turn_speed=json_data['turn_speed'],
            detection_range=json_data['detection_range'],
            detection_height_range=json_data['detection_height_range'],
            detection_angle=json_data['detection_angle'],
            min_attack_range=json_data['min_attack_range'],
            max_attack_range=json_data['max_attack_range'],
            average_attack_time=json_data['average_attack_time'],
            attack_time_variation=json_data['attack_time_variation'],
            leash_radius=json_data['leash_radius'],
            player_leash_radius=json_data['player_leash_radius'],
            player_leash_time=json_data['player_leash_time'],
            contact_damage=DamageInfo.from_json(json_data['contact_damage']),
            damage_wait_time=json_data['damage_wait_time'],
            unnamed=HealthInfo.from_json(json_data['unnamed']),
            vulnerability=DamageVulnerability.from_json(json_data['vulnerability']),
            unknown_1=json_data['unknown_1'],
            unknown_2=json_data['unknown_2'],
            unknown_3=Vector.from_json(json_data['unknown_3']),
            unknown_4=json_data['unknown_4'],
            unknown_5=json_data['unknown_5'],
            unknown_6=json_data['unknown_6'],
            unknown_7=json_data['unknown_7'],
            death_sound=json_data['death_sound'],
            animation_parameters=AnimationParameters.from_json(json_data['animation_parameters']),
            active=json_data['active'],
            state_machine=json_data['state_machine'],
            unknown_8=json_data['unknown_8'],
            unknown_9=json_data['unknown_9'],
            unknown_10=json_data['unknown_10'],
            unknown_11=json_data['unknown_11'],
            unknown_12=Vector.from_json(json_data['unknown_12']),
            particle_1=json_data['particle_1'],
            unknown_13=json_data['unknown_13'],
            unknown_14=Vector.from_json(json_data['unknown_14']),
            particle_2=json_data['particle_2'],
            ice_shatter_sound=json_data['ice_shatter_sound'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'mass': self.mass,
            'speed': self.speed,
            'turn_speed': self.turn_speed,
            'detection_range': self.detection_range,
            'detection_height_range': self.detection_height_range,
            'detection_angle': self.detection_angle,
            'min_attack_range': self.min_attack_range,
            'max_attack_range': self.max_attack_range,
            'average_attack_time': self.average_attack_time,
            'attack_time_variation': self.attack_time_variation,
            'leash_radius': self.leash_radius,
            'player_leash_radius': self.player_leash_radius,
            'player_leash_time': self.player_leash_time,
            'contact_damage': self.contact_damage.to_json(),
            'damage_wait_time': self.damage_wait_time,
            'unnamed': self.unnamed.to_json(),
            'vulnerability': self.vulnerability.to_json(),
            'unknown_1': self.unknown_1,
            'unknown_2': self.unknown_2,
            'unknown_3': self.unknown_3.to_json(),
            'unknown_4': self.unknown_4,
            'unknown_5': self.unknown_5,
            'unknown_6': self.unknown_6,
            'unknown_7': self.unknown_7,
            'death_sound': self.death_sound,
            'animation_parameters': self.animation_parameters.to_json(),
            'active': self.active,
            'state_machine': self.state_machine,
            'unknown_8': self.unknown_8,
            'unknown_9': self.unknown_9,
            'unknown_10': self.unknown_10,
            'unknown_11': self.unknown_11,
            'unknown_12': self.unknown_12.to_json(),
            'particle_1': self.particle_1,
            'unknown_13': self.unknown_13,
            'unknown_14': self.unknown_14.to_json(),
            'particle_2': self.particle_2,
            'ice_shatter_sound': self.ice_shatter_sound,
        }

    def _dependencies_for_death_sound(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.death_sound)

    def _dependencies_for_state_machine(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.state_machine)

    def _dependencies_for_particle_1(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.particle_1)

    def _dependencies_for_particle_2(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.particle_2)

    def _dependencies_for_ice_shatter_sound(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.ice_shatter_sound)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.contact_damage.dependencies_for, "contact_damage", "DamageInfo"),
            (self.unnamed.dependencies_for, "unnamed", "HealthInfo"),
            (self.vulnerability.dependencies_for, "vulnerability", "DamageVulnerability"),
            (self._dependencies_for_death_sound, "death_sound", "int"),
            (self.animation_parameters.dependencies_for, "animation_parameters", "AnimationParameters"),
            (self._dependencies_for_state_machine, "state_machine", "AssetId"),
            (self._dependencies_for_particle_1, "particle_1", "AssetId"),
            (self._dependencies_for_particle_2, "particle_2", "AssetId"),
            (self._dependencies_for_ice_shatter_sound, "ice_shatter_sound", "int"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for PatternedAITypedef.{field_name} ({field_type}): {e}"
                )
