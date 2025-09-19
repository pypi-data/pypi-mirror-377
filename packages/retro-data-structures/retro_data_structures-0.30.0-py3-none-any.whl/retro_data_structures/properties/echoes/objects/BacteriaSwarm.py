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
from retro_data_structures.properties.echoes.archetypes.BasicSwarmProperties import BasicSwarmProperties
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.core.AnimationParameters import AnimationParameters
from retro_data_structures.properties.echoes.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.echoes.core.Color import Color

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class BacteriaSwarmJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        actor_information: json_util.JsonObject
        animation_information: json_util.JsonObject
        active: bool
        basic_swarm_properties: json_util.JsonObject
        unknown_0x4a85a2da: float
        containment_priority: float
        bacteria_patrol_speed: float
        unknown_0x7de56d56: float
        unknown_0x39098c47: float
        bacteria_acceleration: float
        bacteria_deceleration: float
        patrol_turn_speed: float
        unknown_0xbdcdb9c0: float
        bacteria_particle_effect: int
        bacteria_patrol_color: json_util.JsonValue
        bacteria_player_pursuit_color: json_util.JsonValue
        color_change_time: float
        patrol_sound: int
        pursuit_sound: int
        unknown_0xad4ce8f3: float
        unknown_0xa9d6d9d9: float
        patrol_sound_weight: float
        unknown_0x90f8e29f: float
        unknown_0x4b47b178: float
        pursuit_sound_weight: float
        unknown_0xd2986c43: float
        max_audible_distance: float
        min_volume: int
        max_volume: int
        bacteria_scan_model: int
        spawn_instantly: bool
    

@dataclasses.dataclass()
class BacteriaSwarm(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    actor_information: ActorParameters = dataclasses.field(default_factory=ActorParameters, metadata={
        'reflection': FieldReflection[ActorParameters](
            ActorParameters, id=0x7e397fed, original_name='ActorInformation', from_json=ActorParameters.from_json, to_json=ActorParameters.to_json
        ),
    })
    animation_information: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0xe25fb08c, original_name='AnimationInformation', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    active: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xc6bb2f45, original_name='Active'
        ),
    })
    basic_swarm_properties: BasicSwarmProperties = dataclasses.field(default_factory=BasicSwarmProperties, metadata={
        'reflection': FieldReflection[BasicSwarmProperties](
            BasicSwarmProperties, id=0xe1ec7346, original_name='BasicSwarmProperties', from_json=BasicSwarmProperties.from_json, to_json=BasicSwarmProperties.to_json
        ),
    })
    unknown_0x4a85a2da: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4a85a2da, original_name='Unknown'
        ),
    })
    containment_priority: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7ff1469e, original_name='ContainmentPriority'
        ),
    })
    bacteria_patrol_speed: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf87fd6a9, original_name='BacteriaPatrolSpeed'
        ),
    })
    unknown_0x7de56d56: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7de56d56, original_name='Unknown'
        ),
    })
    unknown_0x39098c47: float = dataclasses.field(default=0.20000000298023224, metadata={
        'reflection': FieldReflection[float](
            float, id=0x39098c47, original_name='Unknown'
        ),
    })
    bacteria_acceleration: float = dataclasses.field(default=0.009999999776482582, metadata={
        'reflection': FieldReflection[float](
            float, id=0xfba2a53e, original_name='BacteriaAcceleration'
        ),
    })
    bacteria_deceleration: float = dataclasses.field(default=0.009999999776482582, metadata={
        'reflection': FieldReflection[float](
            float, id=0x5c9d2056, original_name='BacteriaDeceleration'
        ),
    })
    patrol_turn_speed: float = dataclasses.field(default=180.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x771a90e6, original_name='PatrolTurnSpeed'
        ),
    })
    unknown_0xbdcdb9c0: float = dataclasses.field(default=1440.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xbdcdb9c0, original_name='Unknown'
        ),
    })
    bacteria_particle_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x2301294a, original_name='BacteriaParticleEffect'
        ),
    })
    bacteria_patrol_color: Color = dataclasses.field(default_factory=lambda: Color(r=1.0, g=1.0, b=1.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xac2a467a, original_name='BacteriaPatrolColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    bacteria_player_pursuit_color: Color = dataclasses.field(default_factory=lambda: Color(r=1.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x6d5c1c94, original_name='BacteriaPlayerPursuitColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    color_change_time: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x311b0750, original_name='ColorChangeTime'
        ),
    })
    patrol_sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x4ab24275, original_name='PatrolSound'
        ),
    })
    pursuit_sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0xfe3e7bbf, original_name='PursuitSound'
        ),
    })
    unknown_0xad4ce8f3: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0xad4ce8f3, original_name='Unknown'
        ),
    })
    unknown_0xa9d6d9d9: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa9d6d9d9, original_name='Unknown'
        ),
    })
    patrol_sound_weight: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9fe253a5, original_name='PatrolSoundWeight'
        ),
    })
    unknown_0x90f8e29f: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x90f8e29f, original_name='Unknown'
        ),
    })
    unknown_0x4b47b178: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4b47b178, original_name='Unknown'
        ),
    })
    pursuit_sound_weight: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe678ebcf, original_name='PursuitSoundWeight'
        ),
    })
    unknown_0xd2986c43: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd2986c43, original_name='Unknown'
        ),
    })
    max_audible_distance: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x214e48a0, original_name='MaxAudibleDistance'
        ),
    })
    min_volume: int = dataclasses.field(default=20, metadata={
        'reflection': FieldReflection[int](
            int, id=0x57619496, original_name='MinVolume'
        ),
    })
    max_volume: int = dataclasses.field(default=127, metadata={
        'reflection': FieldReflection[int](
            int, id=0xc712847c, original_name='MaxVolume'
        ),
    })
    bacteria_scan_model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x757a1c34, original_name='BacteriaScanModel'
        ),
    })
    spawn_instantly: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xc5bc5ed0, original_name='SpawnInstantly'
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
        return 'BSWM'

    @classmethod
    def modules(cls) -> list[str]:
        return ['BacteriaSwarm.rel']

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
        if property_count != 32:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7e397fed
        actor_information = ActorParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe25fb08c
        animation_information = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc6bb2f45
        active = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe1ec7346
        basic_swarm_properties = BasicSwarmProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4a85a2da
        unknown_0x4a85a2da = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7ff1469e
        containment_priority = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf87fd6a9
        bacteria_patrol_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7de56d56
        unknown_0x7de56d56 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x39098c47
        unknown_0x39098c47 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfba2a53e
        bacteria_acceleration = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5c9d2056
        bacteria_deceleration = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x771a90e6
        patrol_turn_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbdcdb9c0
        unknown_0xbdcdb9c0 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2301294a
        bacteria_particle_effect = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xac2a467a
        bacteria_patrol_color = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6d5c1c94
        bacteria_player_pursuit_color = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x311b0750
        color_change_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4ab24275
        patrol_sound = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfe3e7bbf
        pursuit_sound = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xad4ce8f3
        unknown_0xad4ce8f3 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa9d6d9d9
        unknown_0xa9d6d9d9 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9fe253a5
        patrol_sound_weight = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x90f8e29f
        unknown_0x90f8e29f = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4b47b178
        unknown_0x4b47b178 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe678ebcf
        pursuit_sound_weight = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd2986c43
        unknown_0xd2986c43 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x214e48a0
        max_audible_distance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x57619496
        min_volume = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc712847c
        max_volume = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x757a1c34
        bacteria_scan_model = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc5bc5ed0
        spawn_instantly = struct.unpack('>?', data.read(1))[0]
    
        return cls(editor_properties, actor_information, animation_information, active, basic_swarm_properties, unknown_0x4a85a2da, containment_priority, bacteria_patrol_speed, unknown_0x7de56d56, unknown_0x39098c47, bacteria_acceleration, bacteria_deceleration, patrol_turn_speed, unknown_0xbdcdb9c0, bacteria_particle_effect, bacteria_patrol_color, bacteria_player_pursuit_color, color_change_time, patrol_sound, pursuit_sound, unknown_0xad4ce8f3, unknown_0xa9d6d9d9, patrol_sound_weight, unknown_0x90f8e29f, unknown_0x4b47b178, pursuit_sound_weight, unknown_0xd2986c43, max_audible_distance, min_volume, max_volume, bacteria_scan_model, spawn_instantly)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00 ')  # 32 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
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

        data.write(b'\xe2_\xb0\x8c')  # 0xe25fb08c
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.animation_information.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc6\xbb/E')  # 0xc6bb2f45
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.active))

        data.write(b'\xe1\xecsF')  # 0xe1ec7346
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.basic_swarm_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'J\x85\xa2\xda')  # 0x4a85a2da
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x4a85a2da))

        data.write(b'\x7f\xf1F\x9e')  # 0x7ff1469e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.containment_priority))

        data.write(b'\xf8\x7f\xd6\xa9')  # 0xf87fd6a9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.bacteria_patrol_speed))

        data.write(b'}\xe5mV')  # 0x7de56d56
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x7de56d56))

        data.write(b'9\t\x8cG')  # 0x39098c47
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x39098c47))

        data.write(b'\xfb\xa2\xa5>')  # 0xfba2a53e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.bacteria_acceleration))

        data.write(b'\\\x9d V')  # 0x5c9d2056
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.bacteria_deceleration))

        data.write(b'w\x1a\x90\xe6')  # 0x771a90e6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.patrol_turn_speed))

        data.write(b'\xbd\xcd\xb9\xc0')  # 0xbdcdb9c0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xbdcdb9c0))

        data.write(b'#\x01)J')  # 0x2301294a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.bacteria_particle_effect))

        data.write(b'\xac*Fz')  # 0xac2a467a
        data.write(b'\x00\x10')  # size
        self.bacteria_patrol_color.to_stream(data)

        data.write(b'm\\\x1c\x94')  # 0x6d5c1c94
        data.write(b'\x00\x10')  # size
        self.bacteria_player_pursuit_color.to_stream(data)

        data.write(b'1\x1b\x07P')  # 0x311b0750
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.color_change_time))

        data.write(b'J\xb2Bu')  # 0x4ab24275
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.patrol_sound))

        data.write(b'\xfe>{\xbf')  # 0xfe3e7bbf
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.pursuit_sound))

        data.write(b'\xadL\xe8\xf3')  # 0xad4ce8f3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xad4ce8f3))

        data.write(b'\xa9\xd6\xd9\xd9')  # 0xa9d6d9d9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xa9d6d9d9))

        data.write(b'\x9f\xe2S\xa5')  # 0x9fe253a5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.patrol_sound_weight))

        data.write(b'\x90\xf8\xe2\x9f')  # 0x90f8e29f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x90f8e29f))

        data.write(b'KG\xb1x')  # 0x4b47b178
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x4b47b178))

        data.write(b'\xe6x\xeb\xcf')  # 0xe678ebcf
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.pursuit_sound_weight))

        data.write(b'\xd2\x98lC')  # 0xd2986c43
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xd2986c43))

        data.write(b'!NH\xa0')  # 0x214e48a0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_audible_distance))

        data.write(b'Wa\x94\x96')  # 0x57619496
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.min_volume))

        data.write(b'\xc7\x12\x84|')  # 0xc712847c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.max_volume))

        data.write(b'uz\x1c4')  # 0x757a1c34
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.bacteria_scan_model))

        data.write(b'\xc5\xbc^\xd0')  # 0xc5bc5ed0
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.spawn_instantly))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("BacteriaSwarmJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            actor_information=ActorParameters.from_json(json_data['actor_information']),
            animation_information=AnimationParameters.from_json(json_data['animation_information']),
            active=json_data['active'],
            basic_swarm_properties=BasicSwarmProperties.from_json(json_data['basic_swarm_properties']),
            unknown_0x4a85a2da=json_data['unknown_0x4a85a2da'],
            containment_priority=json_data['containment_priority'],
            bacteria_patrol_speed=json_data['bacteria_patrol_speed'],
            unknown_0x7de56d56=json_data['unknown_0x7de56d56'],
            unknown_0x39098c47=json_data['unknown_0x39098c47'],
            bacteria_acceleration=json_data['bacteria_acceleration'],
            bacteria_deceleration=json_data['bacteria_deceleration'],
            patrol_turn_speed=json_data['patrol_turn_speed'],
            unknown_0xbdcdb9c0=json_data['unknown_0xbdcdb9c0'],
            bacteria_particle_effect=json_data['bacteria_particle_effect'],
            bacteria_patrol_color=Color.from_json(json_data['bacteria_patrol_color']),
            bacteria_player_pursuit_color=Color.from_json(json_data['bacteria_player_pursuit_color']),
            color_change_time=json_data['color_change_time'],
            patrol_sound=json_data['patrol_sound'],
            pursuit_sound=json_data['pursuit_sound'],
            unknown_0xad4ce8f3=json_data['unknown_0xad4ce8f3'],
            unknown_0xa9d6d9d9=json_data['unknown_0xa9d6d9d9'],
            patrol_sound_weight=json_data['patrol_sound_weight'],
            unknown_0x90f8e29f=json_data['unknown_0x90f8e29f'],
            unknown_0x4b47b178=json_data['unknown_0x4b47b178'],
            pursuit_sound_weight=json_data['pursuit_sound_weight'],
            unknown_0xd2986c43=json_data['unknown_0xd2986c43'],
            max_audible_distance=json_data['max_audible_distance'],
            min_volume=json_data['min_volume'],
            max_volume=json_data['max_volume'],
            bacteria_scan_model=json_data['bacteria_scan_model'],
            spawn_instantly=json_data['spawn_instantly'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'actor_information': self.actor_information.to_json(),
            'animation_information': self.animation_information.to_json(),
            'active': self.active,
            'basic_swarm_properties': self.basic_swarm_properties.to_json(),
            'unknown_0x4a85a2da': self.unknown_0x4a85a2da,
            'containment_priority': self.containment_priority,
            'bacteria_patrol_speed': self.bacteria_patrol_speed,
            'unknown_0x7de56d56': self.unknown_0x7de56d56,
            'unknown_0x39098c47': self.unknown_0x39098c47,
            'bacteria_acceleration': self.bacteria_acceleration,
            'bacteria_deceleration': self.bacteria_deceleration,
            'patrol_turn_speed': self.patrol_turn_speed,
            'unknown_0xbdcdb9c0': self.unknown_0xbdcdb9c0,
            'bacteria_particle_effect': self.bacteria_particle_effect,
            'bacteria_patrol_color': self.bacteria_patrol_color.to_json(),
            'bacteria_player_pursuit_color': self.bacteria_player_pursuit_color.to_json(),
            'color_change_time': self.color_change_time,
            'patrol_sound': self.patrol_sound,
            'pursuit_sound': self.pursuit_sound,
            'unknown_0xad4ce8f3': self.unknown_0xad4ce8f3,
            'unknown_0xa9d6d9d9': self.unknown_0xa9d6d9d9,
            'patrol_sound_weight': self.patrol_sound_weight,
            'unknown_0x90f8e29f': self.unknown_0x90f8e29f,
            'unknown_0x4b47b178': self.unknown_0x4b47b178,
            'pursuit_sound_weight': self.pursuit_sound_weight,
            'unknown_0xd2986c43': self.unknown_0xd2986c43,
            'max_audible_distance': self.max_audible_distance,
            'min_volume': self.min_volume,
            'max_volume': self.max_volume,
            'bacteria_scan_model': self.bacteria_scan_model,
            'spawn_instantly': self.spawn_instantly,
        }

    def _dependencies_for_bacteria_particle_effect(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.bacteria_particle_effect)

    def _dependencies_for_patrol_sound(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.patrol_sound)

    def _dependencies_for_pursuit_sound(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.pursuit_sound)

    def _dependencies_for_bacteria_scan_model(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.bacteria_scan_model)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.editor_properties.dependencies_for, "editor_properties", "EditorProperties"),
            (self.actor_information.dependencies_for, "actor_information", "ActorParameters"),
            (self.animation_information.dependencies_for, "animation_information", "AnimationParameters"),
            (self.basic_swarm_properties.dependencies_for, "basic_swarm_properties", "BasicSwarmProperties"),
            (self._dependencies_for_bacteria_particle_effect, "bacteria_particle_effect", "AssetId"),
            (self._dependencies_for_patrol_sound, "patrol_sound", "int"),
            (self._dependencies_for_pursuit_sound, "pursuit_sound", "int"),
            (self._dependencies_for_bacteria_scan_model, "bacteria_scan_model", "AssetId"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for BacteriaSwarm.{field_name} ({field_type}): {e}"
                )


def _decode_active(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x4a85a2da(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_containment_priority(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_bacteria_patrol_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x7de56d56(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x39098c47(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_bacteria_acceleration(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_bacteria_deceleration(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_patrol_turn_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xbdcdb9c0(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_bacteria_particle_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_bacteria_patrol_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_bacteria_player_pursuit_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_color_change_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_patrol_sound(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_pursuit_sound(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0xad4ce8f3(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xa9d6d9d9(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_patrol_sound_weight(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x90f8e29f(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x4b47b178(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_pursuit_sound_weight(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xd2986c43(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_audible_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_min_volume(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_max_volume(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_bacteria_scan_model(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_spawn_instantly(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0x7e397fed: ('actor_information', ActorParameters.from_stream),
    0xe25fb08c: ('animation_information', AnimationParameters.from_stream),
    0xc6bb2f45: ('active', _decode_active),
    0xe1ec7346: ('basic_swarm_properties', BasicSwarmProperties.from_stream),
    0x4a85a2da: ('unknown_0x4a85a2da', _decode_unknown_0x4a85a2da),
    0x7ff1469e: ('containment_priority', _decode_containment_priority),
    0xf87fd6a9: ('bacteria_patrol_speed', _decode_bacteria_patrol_speed),
    0x7de56d56: ('unknown_0x7de56d56', _decode_unknown_0x7de56d56),
    0x39098c47: ('unknown_0x39098c47', _decode_unknown_0x39098c47),
    0xfba2a53e: ('bacteria_acceleration', _decode_bacteria_acceleration),
    0x5c9d2056: ('bacteria_deceleration', _decode_bacteria_deceleration),
    0x771a90e6: ('patrol_turn_speed', _decode_patrol_turn_speed),
    0xbdcdb9c0: ('unknown_0xbdcdb9c0', _decode_unknown_0xbdcdb9c0),
    0x2301294a: ('bacteria_particle_effect', _decode_bacteria_particle_effect),
    0xac2a467a: ('bacteria_patrol_color', _decode_bacteria_patrol_color),
    0x6d5c1c94: ('bacteria_player_pursuit_color', _decode_bacteria_player_pursuit_color),
    0x311b0750: ('color_change_time', _decode_color_change_time),
    0x4ab24275: ('patrol_sound', _decode_patrol_sound),
    0xfe3e7bbf: ('pursuit_sound', _decode_pursuit_sound),
    0xad4ce8f3: ('unknown_0xad4ce8f3', _decode_unknown_0xad4ce8f3),
    0xa9d6d9d9: ('unknown_0xa9d6d9d9', _decode_unknown_0xa9d6d9d9),
    0x9fe253a5: ('patrol_sound_weight', _decode_patrol_sound_weight),
    0x90f8e29f: ('unknown_0x90f8e29f', _decode_unknown_0x90f8e29f),
    0x4b47b178: ('unknown_0x4b47b178', _decode_unknown_0x4b47b178),
    0xe678ebcf: ('pursuit_sound_weight', _decode_pursuit_sound_weight),
    0xd2986c43: ('unknown_0xd2986c43', _decode_unknown_0xd2986c43),
    0x214e48a0: ('max_audible_distance', _decode_max_audible_distance),
    0x57619496: ('min_volume', _decode_min_volume),
    0xc712847c: ('max_volume', _decode_max_volume),
    0x757a1c34: ('bacteria_scan_model', _decode_bacteria_scan_model),
    0xc5bc5ed0: ('spawn_instantly', _decode_spawn_instantly),
}
