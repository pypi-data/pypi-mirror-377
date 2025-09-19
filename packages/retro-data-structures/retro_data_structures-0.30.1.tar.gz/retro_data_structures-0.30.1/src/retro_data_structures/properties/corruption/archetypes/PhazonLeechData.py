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
from retro_data_structures.properties.corruption.archetypes.ModIncaData import ModIncaData

if typing.TYPE_CHECKING:
    class PhazonLeechDataJson(typing_extensions.TypedDict):
        energy_loss: float
        min_hunger_energy: float
        hunger_threshold: float
        bored_threshold: float
        unknown_0xa822c334: float
        alert_time: float
        unknown_0x61634792: float
        unknown_0xc657c7eb: float
        min_attach_time: float
        max_attach_time: float
        jump_position_offset: float
        attach_position_offset: float
        unknown_0x4f547915: float
        unknown_0xa934d6f4: float
        normal_jump_apex: float
        normal_jump_speed: float
        attack_jump_apex: float
        attack_jump_speed: float
        detach_jump_apex: float
        detach_jump_speed: float
        hurl_distance: float
        attach_damage: json_util.JsonObject
        attach_damage_delay: float
        unknown_0x57fee02a: float
        mod_inca_data: json_util.JsonObject
        use_terrain_alignment: bool
    

@dataclasses.dataclass()
class PhazonLeechData(BaseProperty):
    energy_loss: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x50d4e6dd, original_name='EnergyLoss'
        ),
    })
    min_hunger_energy: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4638014f, original_name='MinHungerEnergy'
        ),
    })
    hunger_threshold: float = dataclasses.field(default=0.699999988079071, metadata={
        'reflection': FieldReflection[float](
            float, id=0xfe41f1ab, original_name='HungerThreshold'
        ),
    })
    bored_threshold: float = dataclasses.field(default=0.8999999761581421, metadata={
        'reflection': FieldReflection[float](
            float, id=0x96729b15, original_name='BoredThreshold'
        ),
    })
    unknown_0xa822c334: float = dataclasses.field(default=0.15000000596046448, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa822c334, original_name='Unknown'
        ),
    })
    alert_time: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd263977c, original_name='AlertTime'
        ),
    })
    unknown_0x61634792: float = dataclasses.field(default=35.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x61634792, original_name='Unknown'
        ),
    })
    unknown_0xc657c7eb: float = dataclasses.field(default=55.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc657c7eb, original_name='Unknown'
        ),
    })
    min_attach_time: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc5e8886b, original_name='MinAttachTime'
        ),
    })
    max_attach_time: float = dataclasses.field(default=4.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x964e908f, original_name='MaxAttachTime'
        ),
    })
    jump_position_offset: float = dataclasses.field(default=-1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc9db43b2, original_name='JumpPositionOffset'
        ),
    })
    attach_position_offset: float = dataclasses.field(default=-1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x371594cd, original_name='AttachPositionOffset'
        ),
    })
    unknown_0x4f547915: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4f547915, original_name='Unknown'
        ),
    })
    unknown_0xa934d6f4: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa934d6f4, original_name='Unknown'
        ),
    })
    normal_jump_apex: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x32ab2d0f, original_name='NormalJumpApex'
        ),
    })
    normal_jump_speed: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xca517218, original_name='NormalJumpSpeed'
        ),
    })
    attack_jump_apex: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6f1deb26, original_name='AttackJumpApex'
        ),
    })
    attack_jump_speed: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x88be5cb2, original_name='AttackJumpSpeed'
        ),
    })
    detach_jump_apex: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xec07a9be, original_name='DetachJumpApex'
        ),
    })
    detach_jump_speed: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x76e95d86, original_name='DetachJumpSpeed'
        ),
    })
    hurl_distance: float = dataclasses.field(default=7.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x13bfc5dd, original_name='HurlDistance'
        ),
    })
    attach_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x3546f14f, original_name='AttachDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    attach_damage_delay: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8976d3f6, original_name='AttachDamageDelay'
        ),
    })
    unknown_0x57fee02a: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0x57fee02a, original_name='Unknown'
        ),
    })
    mod_inca_data: ModIncaData = dataclasses.field(default_factory=ModIncaData, metadata={
        'reflection': FieldReflection[ModIncaData](
            ModIncaData, id=0xb4c02854, original_name='ModIncaData', from_json=ModIncaData.from_json, to_json=ModIncaData.to_json
        ),
    })
    use_terrain_alignment: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x6117e78f, original_name='UseTerrainAlignment'
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
        if property_count != 26:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x50d4e6dd
        energy_loss = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4638014f
        min_hunger_energy = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfe41f1ab
        hunger_threshold = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x96729b15
        bored_threshold = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa822c334
        unknown_0xa822c334 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd263977c
        alert_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x61634792
        unknown_0x61634792 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc657c7eb
        unknown_0xc657c7eb = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc5e8886b
        min_attach_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x964e908f
        max_attach_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc9db43b2
        jump_position_offset = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x371594cd
        attach_position_offset = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4f547915
        unknown_0x4f547915 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa934d6f4
        unknown_0xa934d6f4 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x32ab2d0f
        normal_jump_apex = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xca517218
        normal_jump_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6f1deb26
        attack_jump_apex = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x88be5cb2
        attack_jump_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xec07a9be
        detach_jump_apex = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x76e95d86
        detach_jump_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x13bfc5dd
        hurl_distance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3546f14f
        attach_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8976d3f6
        attach_damage_delay = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x57fee02a
        unknown_0x57fee02a = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb4c02854
        mod_inca_data = ModIncaData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6117e78f
        use_terrain_alignment = struct.unpack('>?', data.read(1))[0]
    
        return cls(energy_loss, min_hunger_energy, hunger_threshold, bored_threshold, unknown_0xa822c334, alert_time, unknown_0x61634792, unknown_0xc657c7eb, min_attach_time, max_attach_time, jump_position_offset, attach_position_offset, unknown_0x4f547915, unknown_0xa934d6f4, normal_jump_apex, normal_jump_speed, attack_jump_apex, attack_jump_speed, detach_jump_apex, detach_jump_speed, hurl_distance, attach_damage, attach_damage_delay, unknown_0x57fee02a, mod_inca_data, use_terrain_alignment)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x1a')  # 26 properties

        data.write(b'P\xd4\xe6\xdd')  # 0x50d4e6dd
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.energy_loss))

        data.write(b'F8\x01O')  # 0x4638014f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_hunger_energy))

        data.write(b'\xfeA\xf1\xab')  # 0xfe41f1ab
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.hunger_threshold))

        data.write(b'\x96r\x9b\x15')  # 0x96729b15
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.bored_threshold))

        data.write(b'\xa8"\xc34')  # 0xa822c334
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xa822c334))

        data.write(b'\xd2c\x97|')  # 0xd263977c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.alert_time))

        data.write(b'acG\x92')  # 0x61634792
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x61634792))

        data.write(b'\xc6W\xc7\xeb')  # 0xc657c7eb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xc657c7eb))

        data.write(b'\xc5\xe8\x88k')  # 0xc5e8886b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_attach_time))

        data.write(b'\x96N\x90\x8f')  # 0x964e908f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_attach_time))

        data.write(b'\xc9\xdbC\xb2')  # 0xc9db43b2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.jump_position_offset))

        data.write(b'7\x15\x94\xcd')  # 0x371594cd
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.attach_position_offset))

        data.write(b'OTy\x15')  # 0x4f547915
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x4f547915))

        data.write(b'\xa94\xd6\xf4')  # 0xa934d6f4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xa934d6f4))

        data.write(b'2\xab-\x0f')  # 0x32ab2d0f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.normal_jump_apex))

        data.write(b'\xcaQr\x18')  # 0xca517218
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.normal_jump_speed))

        data.write(b'o\x1d\xeb&')  # 0x6f1deb26
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.attack_jump_apex))

        data.write(b'\x88\xbe\\\xb2')  # 0x88be5cb2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.attack_jump_speed))

        data.write(b'\xec\x07\xa9\xbe')  # 0xec07a9be
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.detach_jump_apex))

        data.write(b'v\xe9]\x86')  # 0x76e95d86
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.detach_jump_speed))

        data.write(b'\x13\xbf\xc5\xdd')  # 0x13bfc5dd
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.hurl_distance))

        data.write(b'5F\xf1O')  # 0x3546f14f
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.attach_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x89v\xd3\xf6')  # 0x8976d3f6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.attach_damage_delay))

        data.write(b'W\xfe\xe0*')  # 0x57fee02a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x57fee02a))

        data.write(b'\xb4\xc0(T')  # 0xb4c02854
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.mod_inca_data.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'a\x17\xe7\x8f')  # 0x6117e78f
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.use_terrain_alignment))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("PhazonLeechDataJson", data)
        return cls(
            energy_loss=json_data['energy_loss'],
            min_hunger_energy=json_data['min_hunger_energy'],
            hunger_threshold=json_data['hunger_threshold'],
            bored_threshold=json_data['bored_threshold'],
            unknown_0xa822c334=json_data['unknown_0xa822c334'],
            alert_time=json_data['alert_time'],
            unknown_0x61634792=json_data['unknown_0x61634792'],
            unknown_0xc657c7eb=json_data['unknown_0xc657c7eb'],
            min_attach_time=json_data['min_attach_time'],
            max_attach_time=json_data['max_attach_time'],
            jump_position_offset=json_data['jump_position_offset'],
            attach_position_offset=json_data['attach_position_offset'],
            unknown_0x4f547915=json_data['unknown_0x4f547915'],
            unknown_0xa934d6f4=json_data['unknown_0xa934d6f4'],
            normal_jump_apex=json_data['normal_jump_apex'],
            normal_jump_speed=json_data['normal_jump_speed'],
            attack_jump_apex=json_data['attack_jump_apex'],
            attack_jump_speed=json_data['attack_jump_speed'],
            detach_jump_apex=json_data['detach_jump_apex'],
            detach_jump_speed=json_data['detach_jump_speed'],
            hurl_distance=json_data['hurl_distance'],
            attach_damage=DamageInfo.from_json(json_data['attach_damage']),
            attach_damage_delay=json_data['attach_damage_delay'],
            unknown_0x57fee02a=json_data['unknown_0x57fee02a'],
            mod_inca_data=ModIncaData.from_json(json_data['mod_inca_data']),
            use_terrain_alignment=json_data['use_terrain_alignment'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'energy_loss': self.energy_loss,
            'min_hunger_energy': self.min_hunger_energy,
            'hunger_threshold': self.hunger_threshold,
            'bored_threshold': self.bored_threshold,
            'unknown_0xa822c334': self.unknown_0xa822c334,
            'alert_time': self.alert_time,
            'unknown_0x61634792': self.unknown_0x61634792,
            'unknown_0xc657c7eb': self.unknown_0xc657c7eb,
            'min_attach_time': self.min_attach_time,
            'max_attach_time': self.max_attach_time,
            'jump_position_offset': self.jump_position_offset,
            'attach_position_offset': self.attach_position_offset,
            'unknown_0x4f547915': self.unknown_0x4f547915,
            'unknown_0xa934d6f4': self.unknown_0xa934d6f4,
            'normal_jump_apex': self.normal_jump_apex,
            'normal_jump_speed': self.normal_jump_speed,
            'attack_jump_apex': self.attack_jump_apex,
            'attack_jump_speed': self.attack_jump_speed,
            'detach_jump_apex': self.detach_jump_apex,
            'detach_jump_speed': self.detach_jump_speed,
            'hurl_distance': self.hurl_distance,
            'attach_damage': self.attach_damage.to_json(),
            'attach_damage_delay': self.attach_damage_delay,
            'unknown_0x57fee02a': self.unknown_0x57fee02a,
            'mod_inca_data': self.mod_inca_data.to_json(),
            'use_terrain_alignment': self.use_terrain_alignment,
        }


def _decode_energy_loss(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_min_hunger_energy(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_hunger_threshold(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_bored_threshold(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xa822c334(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_alert_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x61634792(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xc657c7eb(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_min_attach_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_attach_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_jump_position_offset(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_attach_position_offset(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x4f547915(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xa934d6f4(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_normal_jump_apex(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_normal_jump_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_attack_jump_apex(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_attack_jump_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_detach_jump_apex(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_detach_jump_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_hurl_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_attach_damage_delay(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x57fee02a(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_use_terrain_alignment(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x50d4e6dd: ('energy_loss', _decode_energy_loss),
    0x4638014f: ('min_hunger_energy', _decode_min_hunger_energy),
    0xfe41f1ab: ('hunger_threshold', _decode_hunger_threshold),
    0x96729b15: ('bored_threshold', _decode_bored_threshold),
    0xa822c334: ('unknown_0xa822c334', _decode_unknown_0xa822c334),
    0xd263977c: ('alert_time', _decode_alert_time),
    0x61634792: ('unknown_0x61634792', _decode_unknown_0x61634792),
    0xc657c7eb: ('unknown_0xc657c7eb', _decode_unknown_0xc657c7eb),
    0xc5e8886b: ('min_attach_time', _decode_min_attach_time),
    0x964e908f: ('max_attach_time', _decode_max_attach_time),
    0xc9db43b2: ('jump_position_offset', _decode_jump_position_offset),
    0x371594cd: ('attach_position_offset', _decode_attach_position_offset),
    0x4f547915: ('unknown_0x4f547915', _decode_unknown_0x4f547915),
    0xa934d6f4: ('unknown_0xa934d6f4', _decode_unknown_0xa934d6f4),
    0x32ab2d0f: ('normal_jump_apex', _decode_normal_jump_apex),
    0xca517218: ('normal_jump_speed', _decode_normal_jump_speed),
    0x6f1deb26: ('attack_jump_apex', _decode_attack_jump_apex),
    0x88be5cb2: ('attack_jump_speed', _decode_attack_jump_speed),
    0xec07a9be: ('detach_jump_apex', _decode_detach_jump_apex),
    0x76e95d86: ('detach_jump_speed', _decode_detach_jump_speed),
    0x13bfc5dd: ('hurl_distance', _decode_hurl_distance),
    0x3546f14f: ('attach_damage', DamageInfo.from_stream),
    0x8976d3f6: ('attach_damage_delay', _decode_attach_damage_delay),
    0x57fee02a: ('unknown_0x57fee02a', _decode_unknown_0x57fee02a),
    0xb4c02854: ('mod_inca_data', ModIncaData.from_stream),
    0x6117e78f: ('use_terrain_alignment', _decode_use_terrain_alignment),
}
