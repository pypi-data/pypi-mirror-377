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
from retro_data_structures.properties.echoes.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class UnknownStruct30Json(typing_extensions.TypedDict):
        state_machine: int
        health: json_util.JsonObject
        puddle_speed: float
        blob_effect: int
        part_0xe8a6e174: int
        part_0x1ab2b090: int
        puddle_death: int
        sound_ing_spot_idle: int
        sound_ing_spot_move: int
        sound_0xb392943a: int
        sound_0x24ecc1e9: int
        sound_ing_spot_death: int
        vulnerability: json_util.JsonObject
    

@dataclasses.dataclass()
class UnknownStruct30(BaseProperty):
    state_machine: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['AFSM', 'FSM2'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x55744160, original_name='StateMachine'
        ),
    })
    health: HealthInfo = dataclasses.field(default_factory=HealthInfo, metadata={
        'reflection': FieldReflection[HealthInfo](
            HealthInfo, id=0xcf90d15e, original_name='Health', from_json=HealthInfo.from_json, to_json=HealthInfo.to_json
        ),
    })
    puddle_speed: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc6c16427, original_name='PuddleSpeed'
        ),
    })
    blob_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x2367f689, original_name='BlobEffect'
        ),
    })
    part_0xe8a6e174: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xe8a6e174, original_name='PART'
        ),
    })
    part_0x1ab2b090: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x1ab2b090, original_name='PART'
        ),
    })
    puddle_death: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x1ccfa4ba, original_name='PuddleDeath'
        ),
    })
    sound_ing_spot_idle: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x4cab30a9, original_name='Sound_IngSpotIdle'
        ),
    })
    sound_ing_spot_move: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x8f83be73, original_name='Sound_IngSpotMove'
        ),
    })
    sound_0xb392943a: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0xb392943a, original_name='Sound'
        ),
    })
    sound_0x24ecc1e9: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x24ecc1e9, original_name='Sound'
        ),
    })
    sound_ing_spot_death: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x4489935e, original_name='Sound_IngSpotDeath'
        ),
    })
    vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0x7b71ae90, original_name='Vulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
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
        if property_count != 13:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x55744160
        state_machine = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcf90d15e
        health = HealthInfo.from_stream(data, property_size, default_override={'hi_knock_back_resistance': 2.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc6c16427
        puddle_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2367f689
        blob_effect = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe8a6e174
        part_0xe8a6e174 = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1ab2b090
        part_0x1ab2b090 = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1ccfa4ba
        puddle_death = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4cab30a9
        sound_ing_spot_idle = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8f83be73
        sound_ing_spot_move = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb392943a
        sound_0xb392943a = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x24ecc1e9
        sound_0x24ecc1e9 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4489935e
        sound_ing_spot_death = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7b71ae90
        vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        return cls(state_machine, health, puddle_speed, blob_effect, part_0xe8a6e174, part_0x1ab2b090, puddle_death, sound_ing_spot_idle, sound_ing_spot_move, sound_0xb392943a, sound_0x24ecc1e9, sound_ing_spot_death, vulnerability)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\r')  # 13 properties

        data.write(b'UtA`')  # 0x55744160
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.state_machine))

        data.write(b'\xcf\x90\xd1^')  # 0xcf90d15e
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.health.to_stream(data, default_override={'hi_knock_back_resistance': 2.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b"\xc6\xc1d'")  # 0xc6c16427
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.puddle_speed))

        data.write(b'#g\xf6\x89')  # 0x2367f689
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.blob_effect))

        data.write(b'\xe8\xa6\xe1t')  # 0xe8a6e174
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.part_0xe8a6e174))

        data.write(b'\x1a\xb2\xb0\x90')  # 0x1ab2b090
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.part_0x1ab2b090))

        data.write(b'\x1c\xcf\xa4\xba')  # 0x1ccfa4ba
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.puddle_death))

        data.write(b'L\xab0\xa9')  # 0x4cab30a9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_ing_spot_idle))

        data.write(b'\x8f\x83\xbes')  # 0x8f83be73
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_ing_spot_move))

        data.write(b'\xb3\x92\x94:')  # 0xb392943a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_0xb392943a))

        data.write(b'$\xec\xc1\xe9')  # 0x24ecc1e9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_0x24ecc1e9))

        data.write(b'D\x89\x93^')  # 0x4489935e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_ing_spot_death))

        data.write(b'{q\xae\x90')  # 0x7b71ae90
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct30Json", data)
        return cls(
            state_machine=json_data['state_machine'],
            health=HealthInfo.from_json(json_data['health']),
            puddle_speed=json_data['puddle_speed'],
            blob_effect=json_data['blob_effect'],
            part_0xe8a6e174=json_data['part_0xe8a6e174'],
            part_0x1ab2b090=json_data['part_0x1ab2b090'],
            puddle_death=json_data['puddle_death'],
            sound_ing_spot_idle=json_data['sound_ing_spot_idle'],
            sound_ing_spot_move=json_data['sound_ing_spot_move'],
            sound_0xb392943a=json_data['sound_0xb392943a'],
            sound_0x24ecc1e9=json_data['sound_0x24ecc1e9'],
            sound_ing_spot_death=json_data['sound_ing_spot_death'],
            vulnerability=DamageVulnerability.from_json(json_data['vulnerability']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'state_machine': self.state_machine,
            'health': self.health.to_json(),
            'puddle_speed': self.puddle_speed,
            'blob_effect': self.blob_effect,
            'part_0xe8a6e174': self.part_0xe8a6e174,
            'part_0x1ab2b090': self.part_0x1ab2b090,
            'puddle_death': self.puddle_death,
            'sound_ing_spot_idle': self.sound_ing_spot_idle,
            'sound_ing_spot_move': self.sound_ing_spot_move,
            'sound_0xb392943a': self.sound_0xb392943a,
            'sound_0x24ecc1e9': self.sound_0x24ecc1e9,
            'sound_ing_spot_death': self.sound_ing_spot_death,
            'vulnerability': self.vulnerability.to_json(),
        }

    def _dependencies_for_state_machine(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.state_machine)

    def _dependencies_for_blob_effect(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.blob_effect)

    def _dependencies_for_part_0xe8a6e174(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.part_0xe8a6e174)

    def _dependencies_for_part_0x1ab2b090(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.part_0x1ab2b090)

    def _dependencies_for_puddle_death(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.puddle_death)

    def _dependencies_for_sound_ing_spot_idle(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_ing_spot_idle)

    def _dependencies_for_sound_ing_spot_move(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_ing_spot_move)

    def _dependencies_for_sound_0xb392943a(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_0xb392943a)

    def _dependencies_for_sound_0x24ecc1e9(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_0x24ecc1e9)

    def _dependencies_for_sound_ing_spot_death(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_ing_spot_death)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self._dependencies_for_state_machine, "state_machine", "AssetId"),
            (self.health.dependencies_for, "health", "HealthInfo"),
            (self._dependencies_for_blob_effect, "blob_effect", "AssetId"),
            (self._dependencies_for_part_0xe8a6e174, "part_0xe8a6e174", "AssetId"),
            (self._dependencies_for_part_0x1ab2b090, "part_0x1ab2b090", "AssetId"),
            (self._dependencies_for_puddle_death, "puddle_death", "AssetId"),
            (self._dependencies_for_sound_ing_spot_idle, "sound_ing_spot_idle", "int"),
            (self._dependencies_for_sound_ing_spot_move, "sound_ing_spot_move", "int"),
            (self._dependencies_for_sound_0xb392943a, "sound_0xb392943a", "int"),
            (self._dependencies_for_sound_0x24ecc1e9, "sound_0x24ecc1e9", "int"),
            (self._dependencies_for_sound_ing_spot_death, "sound_ing_spot_death", "int"),
            (self.vulnerability.dependencies_for, "vulnerability", "DamageVulnerability"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for UnknownStruct30.{field_name} ({field_type}): {e}"
                )


def _decode_state_machine(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_health(data: typing.BinaryIO, property_size: int) -> HealthInfo:
    return HealthInfo.from_stream(data, property_size, default_override={'hi_knock_back_resistance': 2.0})


def _decode_puddle_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_blob_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_part_0xe8a6e174(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_part_0x1ab2b090(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_puddle_death(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_sound_ing_spot_idle(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_sound_ing_spot_move(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_sound_0xb392943a(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_sound_0x24ecc1e9(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_sound_ing_spot_death(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x55744160: ('state_machine', _decode_state_machine),
    0xcf90d15e: ('health', _decode_health),
    0xc6c16427: ('puddle_speed', _decode_puddle_speed),
    0x2367f689: ('blob_effect', _decode_blob_effect),
    0xe8a6e174: ('part_0xe8a6e174', _decode_part_0xe8a6e174),
    0x1ab2b090: ('part_0x1ab2b090', _decode_part_0x1ab2b090),
    0x1ccfa4ba: ('puddle_death', _decode_puddle_death),
    0x4cab30a9: ('sound_ing_spot_idle', _decode_sound_ing_spot_idle),
    0x8f83be73: ('sound_ing_spot_move', _decode_sound_ing_spot_move),
    0xb392943a: ('sound_0xb392943a', _decode_sound_0xb392943a),
    0x24ecc1e9: ('sound_0x24ecc1e9', _decode_sound_0x24ecc1e9),
    0x4489935e: ('sound_ing_spot_death', _decode_sound_ing_spot_death),
    0x7b71ae90: ('vulnerability', DamageVulnerability.from_stream),
}
