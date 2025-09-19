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
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.corruption.core.Spline import Spline

if typing.TYPE_CHECKING:
    class UnknownStruct41Json(typing_extensions.TypedDict):
        unknown_0xea4b88c8: float
        unknown_0xaa04f0be: float
        unknown_0x59f8b6d0: float
        unknown_0x460020aa: float
        unknown_0x353abf40: float
        caud_0x2822a8fa: int
        caud_0x95d26130: int
        unknown_0xbfb8336b: json_util.JsonObject
        unknown_0xf79adca8: json_util.JsonObject
        unknown_0x68454cb4: float
        beam_sweep: json_util.JsonObject
        beam_sweep2: json_util.JsonObject
        unknown_0xb2671c2a: int
        beam_track_speed: float
        beam_cancel_range: float
        beam_cancel_time: float
        jump_min_range: float
        jump_max_range: float
        unknown_0xb619c33a: float
        missile_min_range: float
        unknown_0x041abba6: float
        melee_attack_min_range: float
        unknown_0x625f214b: float
        melee_attack_range: float
        unknown_0x3e618127: float
        melee_collide_sound: int
        collision_damage: json_util.JsonObject
        hypermode_effect: str
        hypermode_cycle_time: float
        unknown_0xe64bd01e: float
        unknown_0xd8255983: float
    

@dataclasses.dataclass()
class UnknownStruct41(BaseProperty):
    unknown_0xea4b88c8: float = dataclasses.field(default=12.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xea4b88c8, original_name='Unknown'
        ),
    })
    unknown_0xaa04f0be: float = dataclasses.field(default=40.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xaa04f0be, original_name='Unknown'
        ),
    })
    unknown_0x59f8b6d0: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x59f8b6d0, original_name='Unknown'
        ),
    })
    unknown_0x460020aa: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x460020aa, original_name='Unknown'
        ),
    })
    unknown_0x353abf40: float = dataclasses.field(default=8.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x353abf40, original_name='Unknown'
        ),
    })
    caud_0x2822a8fa: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x2822a8fa, original_name='CAUD'
        ),
    })
    caud_0x95d26130: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x95d26130, original_name='CAUD'
        ),
    })
    unknown_0xbfb8336b: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0xbfb8336b, original_name='Unknown', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    unknown_0xf79adca8: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0xf79adca8, original_name='Unknown', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    unknown_0x68454cb4: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x68454cb4, original_name='Unknown'
        ),
    })
    beam_sweep: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x34ddd21c, original_name='BeamSweep', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    beam_sweep2: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x39705dd6, original_name='BeamSweep2', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    unknown_0xb2671c2a: int = dataclasses.field(default=3, metadata={
        'reflection': FieldReflection[int](
            int, id=0xb2671c2a, original_name='Unknown'
        ),
    })
    beam_track_speed: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x546dab4c, original_name='BeamTrackSpeed'
        ),
    })
    beam_cancel_range: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xfbdcb40f, original_name='BeamCancelRange'
        ),
    })
    beam_cancel_time: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0d225e0a, original_name='BeamCancelTime'
        ),
    })
    jump_min_range: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xcfd57029, original_name='JumpMinRange'
        ),
    })
    jump_max_range: float = dataclasses.field(default=25.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8f9a085f, original_name='JumpMaxRange'
        ),
    })
    unknown_0xb619c33a: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb619c33a, original_name='Unknown'
        ),
    })
    missile_min_range: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x5eccb98c, original_name='MissileMinRange'
        ),
    })
    unknown_0x041abba6: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x041abba6, original_name='Unknown'
        ),
    })
    melee_attack_min_range: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xbeadf2e0, original_name='MeleeAttackMinRange'
        ),
    })
    unknown_0x625f214b: float = dataclasses.field(default=25.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x625f214b, original_name='Unknown'
        ),
    })
    melee_attack_range: float = dataclasses.field(default=40.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc3e43d0e, original_name='MeleeAttackRange'
        ),
    })
    unknown_0x3e618127: float = dataclasses.field(default=12.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3e618127, original_name='Unknown'
        ),
    })
    melee_collide_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x095080d9, original_name='MeleeCollideSound'
        ),
    })
    collision_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x0cfd3139, original_name='CollisionDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    hypermode_effect: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x8062d2f8, original_name='HypermodeEffect'
        ),
    })
    hypermode_cycle_time: float = dataclasses.field(default=40.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xbf26fcfb, original_name='HypermodeCycleTime'
        ),
    })
    unknown_0xe64bd01e: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe64bd01e, original_name='Unknown'
        ),
    })
    unknown_0xd8255983: float = dataclasses.field(default=8.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd8255983, original_name='Unknown'
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
        if property_count != 31:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xea4b88c8
        unknown_0xea4b88c8 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xaa04f0be
        unknown_0xaa04f0be = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x59f8b6d0
        unknown_0x59f8b6d0 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x460020aa
        unknown_0x460020aa = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x353abf40
        unknown_0x353abf40 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2822a8fa
        caud_0x2822a8fa = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x95d26130
        caud_0x95d26130 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbfb8336b
        unknown_0xbfb8336b = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf79adca8
        unknown_0xf79adca8 = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x68454cb4
        unknown_0x68454cb4 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x34ddd21c
        beam_sweep = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x39705dd6
        beam_sweep2 = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb2671c2a
        unknown_0xb2671c2a = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x546dab4c
        beam_track_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfbdcb40f
        beam_cancel_range = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0d225e0a
        beam_cancel_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcfd57029
        jump_min_range = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8f9a085f
        jump_max_range = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb619c33a
        unknown_0xb619c33a = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5eccb98c
        missile_min_range = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x041abba6
        unknown_0x041abba6 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbeadf2e0
        melee_attack_min_range = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x625f214b
        unknown_0x625f214b = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc3e43d0e
        melee_attack_range = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3e618127
        unknown_0x3e618127 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x095080d9
        melee_collide_sound = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0cfd3139
        collision_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8062d2f8
        hypermode_effect = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbf26fcfb
        hypermode_cycle_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe64bd01e
        unknown_0xe64bd01e = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd8255983
        unknown_0xd8255983 = struct.unpack('>f', data.read(4))[0]
    
        return cls(unknown_0xea4b88c8, unknown_0xaa04f0be, unknown_0x59f8b6d0, unknown_0x460020aa, unknown_0x353abf40, caud_0x2822a8fa, caud_0x95d26130, unknown_0xbfb8336b, unknown_0xf79adca8, unknown_0x68454cb4, beam_sweep, beam_sweep2, unknown_0xb2671c2a, beam_track_speed, beam_cancel_range, beam_cancel_time, jump_min_range, jump_max_range, unknown_0xb619c33a, missile_min_range, unknown_0x041abba6, melee_attack_min_range, unknown_0x625f214b, melee_attack_range, unknown_0x3e618127, melee_collide_sound, collision_damage, hypermode_effect, hypermode_cycle_time, unknown_0xe64bd01e, unknown_0xd8255983)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x1f')  # 31 properties

        data.write(b'\xeaK\x88\xc8')  # 0xea4b88c8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xea4b88c8))

        data.write(b'\xaa\x04\xf0\xbe')  # 0xaa04f0be
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xaa04f0be))

        data.write(b'Y\xf8\xb6\xd0')  # 0x59f8b6d0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x59f8b6d0))

        data.write(b'F\x00 \xaa')  # 0x460020aa
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x460020aa))

        data.write(b'5:\xbf@')  # 0x353abf40
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x353abf40))

        data.write(b'("\xa8\xfa')  # 0x2822a8fa
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.caud_0x2822a8fa))

        data.write(b'\x95\xd2a0')  # 0x95d26130
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.caud_0x95d26130))

        data.write(b'\xbf\xb83k')  # 0xbfb8336b
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0xbfb8336b.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xf7\x9a\xdc\xa8')  # 0xf79adca8
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0xf79adca8.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'hEL\xb4')  # 0x68454cb4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x68454cb4))

        data.write(b'4\xdd\xd2\x1c')  # 0x34ddd21c
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.beam_sweep.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'9p]\xd6')  # 0x39705dd6
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.beam_sweep2.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xb2g\x1c*')  # 0xb2671c2a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xb2671c2a))

        data.write(b'Tm\xabL')  # 0x546dab4c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.beam_track_speed))

        data.write(b'\xfb\xdc\xb4\x0f')  # 0xfbdcb40f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.beam_cancel_range))

        data.write(b'\r"^\n')  # 0xd225e0a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.beam_cancel_time))

        data.write(b'\xcf\xd5p)')  # 0xcfd57029
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.jump_min_range))

        data.write(b'\x8f\x9a\x08_')  # 0x8f9a085f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.jump_max_range))

        data.write(b'\xb6\x19\xc3:')  # 0xb619c33a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xb619c33a))

        data.write(b'^\xcc\xb9\x8c')  # 0x5eccb98c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.missile_min_range))

        data.write(b'\x04\x1a\xbb\xa6')  # 0x41abba6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x041abba6))

        data.write(b'\xbe\xad\xf2\xe0')  # 0xbeadf2e0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.melee_attack_min_range))

        data.write(b'b_!K')  # 0x625f214b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x625f214b))

        data.write(b'\xc3\xe4=\x0e')  # 0xc3e43d0e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.melee_attack_range))

        data.write(b">a\x81'")  # 0x3e618127
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x3e618127))

        data.write(b'\tP\x80\xd9')  # 0x95080d9
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.melee_collide_sound))

        data.write(b'\x0c\xfd19')  # 0xcfd3139
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.collision_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x80b\xd2\xf8')  # 0x8062d2f8
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.hypermode_effect.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xbf&\xfc\xfb')  # 0xbf26fcfb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.hypermode_cycle_time))

        data.write(b'\xe6K\xd0\x1e')  # 0xe64bd01e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xe64bd01e))

        data.write(b'\xd8%Y\x83')  # 0xd8255983
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xd8255983))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct41Json", data)
        return cls(
            unknown_0xea4b88c8=json_data['unknown_0xea4b88c8'],
            unknown_0xaa04f0be=json_data['unknown_0xaa04f0be'],
            unknown_0x59f8b6d0=json_data['unknown_0x59f8b6d0'],
            unknown_0x460020aa=json_data['unknown_0x460020aa'],
            unknown_0x353abf40=json_data['unknown_0x353abf40'],
            caud_0x2822a8fa=json_data['caud_0x2822a8fa'],
            caud_0x95d26130=json_data['caud_0x95d26130'],
            unknown_0xbfb8336b=Spline.from_json(json_data['unknown_0xbfb8336b']),
            unknown_0xf79adca8=Spline.from_json(json_data['unknown_0xf79adca8']),
            unknown_0x68454cb4=json_data['unknown_0x68454cb4'],
            beam_sweep=Spline.from_json(json_data['beam_sweep']),
            beam_sweep2=Spline.from_json(json_data['beam_sweep2']),
            unknown_0xb2671c2a=json_data['unknown_0xb2671c2a'],
            beam_track_speed=json_data['beam_track_speed'],
            beam_cancel_range=json_data['beam_cancel_range'],
            beam_cancel_time=json_data['beam_cancel_time'],
            jump_min_range=json_data['jump_min_range'],
            jump_max_range=json_data['jump_max_range'],
            unknown_0xb619c33a=json_data['unknown_0xb619c33a'],
            missile_min_range=json_data['missile_min_range'],
            unknown_0x041abba6=json_data['unknown_0x041abba6'],
            melee_attack_min_range=json_data['melee_attack_min_range'],
            unknown_0x625f214b=json_data['unknown_0x625f214b'],
            melee_attack_range=json_data['melee_attack_range'],
            unknown_0x3e618127=json_data['unknown_0x3e618127'],
            melee_collide_sound=json_data['melee_collide_sound'],
            collision_damage=DamageInfo.from_json(json_data['collision_damage']),
            hypermode_effect=json_data['hypermode_effect'],
            hypermode_cycle_time=json_data['hypermode_cycle_time'],
            unknown_0xe64bd01e=json_data['unknown_0xe64bd01e'],
            unknown_0xd8255983=json_data['unknown_0xd8255983'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unknown_0xea4b88c8': self.unknown_0xea4b88c8,
            'unknown_0xaa04f0be': self.unknown_0xaa04f0be,
            'unknown_0x59f8b6d0': self.unknown_0x59f8b6d0,
            'unknown_0x460020aa': self.unknown_0x460020aa,
            'unknown_0x353abf40': self.unknown_0x353abf40,
            'caud_0x2822a8fa': self.caud_0x2822a8fa,
            'caud_0x95d26130': self.caud_0x95d26130,
            'unknown_0xbfb8336b': self.unknown_0xbfb8336b.to_json(),
            'unknown_0xf79adca8': self.unknown_0xf79adca8.to_json(),
            'unknown_0x68454cb4': self.unknown_0x68454cb4,
            'beam_sweep': self.beam_sweep.to_json(),
            'beam_sweep2': self.beam_sweep2.to_json(),
            'unknown_0xb2671c2a': self.unknown_0xb2671c2a,
            'beam_track_speed': self.beam_track_speed,
            'beam_cancel_range': self.beam_cancel_range,
            'beam_cancel_time': self.beam_cancel_time,
            'jump_min_range': self.jump_min_range,
            'jump_max_range': self.jump_max_range,
            'unknown_0xb619c33a': self.unknown_0xb619c33a,
            'missile_min_range': self.missile_min_range,
            'unknown_0x041abba6': self.unknown_0x041abba6,
            'melee_attack_min_range': self.melee_attack_min_range,
            'unknown_0x625f214b': self.unknown_0x625f214b,
            'melee_attack_range': self.melee_attack_range,
            'unknown_0x3e618127': self.unknown_0x3e618127,
            'melee_collide_sound': self.melee_collide_sound,
            'collision_damage': self.collision_damage.to_json(),
            'hypermode_effect': self.hypermode_effect,
            'hypermode_cycle_time': self.hypermode_cycle_time,
            'unknown_0xe64bd01e': self.unknown_0xe64bd01e,
            'unknown_0xd8255983': self.unknown_0xd8255983,
        }


def _decode_unknown_0xea4b88c8(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xaa04f0be(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x59f8b6d0(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x460020aa(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x353abf40(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_caud_0x2822a8fa(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_caud_0x95d26130(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_unknown_0x68454cb4(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xb2671c2a(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_beam_track_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_beam_cancel_range(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_beam_cancel_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_jump_min_range(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_jump_max_range(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xb619c33a(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_missile_min_range(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x041abba6(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_melee_attack_min_range(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x625f214b(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_melee_attack_range(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x3e618127(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_melee_collide_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_hypermode_effect(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_hypermode_cycle_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xe64bd01e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xd8255983(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xea4b88c8: ('unknown_0xea4b88c8', _decode_unknown_0xea4b88c8),
    0xaa04f0be: ('unknown_0xaa04f0be', _decode_unknown_0xaa04f0be),
    0x59f8b6d0: ('unknown_0x59f8b6d0', _decode_unknown_0x59f8b6d0),
    0x460020aa: ('unknown_0x460020aa', _decode_unknown_0x460020aa),
    0x353abf40: ('unknown_0x353abf40', _decode_unknown_0x353abf40),
    0x2822a8fa: ('caud_0x2822a8fa', _decode_caud_0x2822a8fa),
    0x95d26130: ('caud_0x95d26130', _decode_caud_0x95d26130),
    0xbfb8336b: ('unknown_0xbfb8336b', Spline.from_stream),
    0xf79adca8: ('unknown_0xf79adca8', Spline.from_stream),
    0x68454cb4: ('unknown_0x68454cb4', _decode_unknown_0x68454cb4),
    0x34ddd21c: ('beam_sweep', Spline.from_stream),
    0x39705dd6: ('beam_sweep2', Spline.from_stream),
    0xb2671c2a: ('unknown_0xb2671c2a', _decode_unknown_0xb2671c2a),
    0x546dab4c: ('beam_track_speed', _decode_beam_track_speed),
    0xfbdcb40f: ('beam_cancel_range', _decode_beam_cancel_range),
    0xd225e0a: ('beam_cancel_time', _decode_beam_cancel_time),
    0xcfd57029: ('jump_min_range', _decode_jump_min_range),
    0x8f9a085f: ('jump_max_range', _decode_jump_max_range),
    0xb619c33a: ('unknown_0xb619c33a', _decode_unknown_0xb619c33a),
    0x5eccb98c: ('missile_min_range', _decode_missile_min_range),
    0x41abba6: ('unknown_0x041abba6', _decode_unknown_0x041abba6),
    0xbeadf2e0: ('melee_attack_min_range', _decode_melee_attack_min_range),
    0x625f214b: ('unknown_0x625f214b', _decode_unknown_0x625f214b),
    0xc3e43d0e: ('melee_attack_range', _decode_melee_attack_range),
    0x3e618127: ('unknown_0x3e618127', _decode_unknown_0x3e618127),
    0x95080d9: ('melee_collide_sound', _decode_melee_collide_sound),
    0xcfd3139: ('collision_damage', DamageInfo.from_stream),
    0x8062d2f8: ('hypermode_effect', _decode_hypermode_effect),
    0xbf26fcfb: ('hypermode_cycle_time', _decode_hypermode_cycle_time),
    0xe64bd01e: ('unknown_0xe64bd01e', _decode_unknown_0xe64bd01e),
    0xd8255983: ('unknown_0xd8255983', _decode_unknown_0xd8255983),
}
