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
from retro_data_structures.properties.corruption.archetypes.ElectricBeamInfo import ElectricBeamInfo
from retro_data_structures.properties.corruption.archetypes.FlyerMovementMode import FlyerMovementMode
from retro_data_structures.properties.corruption.archetypes.GrappleData import GrappleData
from retro_data_structures.properties.corruption.archetypes.LaunchProjectileData import LaunchProjectileData
from retro_data_structures.properties.corruption.archetypes.ModIncaData import ModIncaData
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.corruption.core.Vector import Vector

if typing.TYPE_CHECKING:
    class GragnolFlyerDataJson(typing_extensions.TypedDict):
        shooter: bool
        projectile: json_util.JsonObject
        missile_deflection_offset: json_util.JsonValue
        missile_deflection_radius: float
        missile_deflection_rate: float
        beam_weapon_info: json_util.JsonObject
        deflection_particle: int
        beam_deflection_sound: int
        unknown_0xf10ee8e2: float
        unknown_0x7171bfc2: float
        electric_beam_info: json_util.JsonObject
        patrol: json_util.JsonObject
        attack_path: json_util.JsonObject
        attack: json_util.JsonObject
        grapple_pull_distance: float
        min_idle_delay: float
        max_idle_delay: float
        recheck_path_time: float
        recheck_path_distance: float
        unknown_0xdff6c19b: bool
        unknown_0xf7381a24: bool
        unknown_0xb2c2928e: float
        grapple_data: json_util.JsonObject
        mod_inca_data: json_util.JsonObject
    

@dataclasses.dataclass()
class GragnolFlyerData(BaseProperty):
    shooter: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x8acc7d20, original_name='Shooter'
        ),
    })
    projectile: LaunchProjectileData = dataclasses.field(default_factory=LaunchProjectileData, metadata={
        'reflection': FieldReflection[LaunchProjectileData](
            LaunchProjectileData, id=0x2c83c012, original_name='Projectile', from_json=LaunchProjectileData.from_json, to_json=LaunchProjectileData.to_json
        ),
    })
    missile_deflection_offset: Vector = dataclasses.field(default_factory=lambda: Vector(x=0.0, y=0.0, z=0.0), metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x7ab4ab98, original_name='MissileDeflectionOffset', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    missile_deflection_radius: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x88fa2acf, original_name='MissileDeflectionRadius'
        ),
    })
    missile_deflection_rate: float = dataclasses.field(default=120.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1d159832, original_name='MissileDeflectionRate'
        ),
    })
    beam_weapon_info: ElectricBeamInfo = dataclasses.field(default_factory=ElectricBeamInfo, metadata={
        'reflection': FieldReflection[ElectricBeamInfo](
            ElectricBeamInfo, id=0x05015775, original_name='BeamWeaponInfo', from_json=ElectricBeamInfo.from_json, to_json=ElectricBeamInfo.to_json
        ),
    })
    deflection_particle: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x8f1ded1b, original_name='DeflectionParticle'
        ),
    })
    beam_deflection_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0b339fac, original_name='BeamDeflectionSound'
        ),
    })
    unknown_0xf10ee8e2: float = dataclasses.field(default=-1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf10ee8e2, original_name='Unknown'
        ),
    })
    unknown_0x7171bfc2: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7171bfc2, original_name='Unknown'
        ),
    })
    electric_beam_info: ElectricBeamInfo = dataclasses.field(default_factory=ElectricBeamInfo, metadata={
        'reflection': FieldReflection[ElectricBeamInfo](
            ElectricBeamInfo, id=0x24265839, original_name='ElectricBeamInfo', from_json=ElectricBeamInfo.from_json, to_json=ElectricBeamInfo.to_json
        ),
    })
    patrol: FlyerMovementMode = dataclasses.field(default_factory=FlyerMovementMode, metadata={
        'reflection': FieldReflection[FlyerMovementMode](
            FlyerMovementMode, id=0xccdd3aca, original_name='Patrol', from_json=FlyerMovementMode.from_json, to_json=FlyerMovementMode.to_json
        ),
    })
    attack_path: FlyerMovementMode = dataclasses.field(default_factory=FlyerMovementMode, metadata={
        'reflection': FieldReflection[FlyerMovementMode](
            FlyerMovementMode, id=0xc845d3c0, original_name='AttackPath', from_json=FlyerMovementMode.from_json, to_json=FlyerMovementMode.to_json
        ),
    })
    attack: FlyerMovementMode = dataclasses.field(default_factory=FlyerMovementMode, metadata={
        'reflection': FieldReflection[FlyerMovementMode](
            FlyerMovementMode, id=0xfa2a173f, original_name='Attack', from_json=FlyerMovementMode.from_json, to_json=FlyerMovementMode.to_json
        ),
    })
    grapple_pull_distance: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe74cf583, original_name='GrapplePullDistance'
        ),
    })
    min_idle_delay: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x176bd1f4, original_name='MinIdleDelay'
        ),
    })
    max_idle_delay: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x02e00506, original_name='MaxIdleDelay'
        ),
    })
    recheck_path_time: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9aa90b6b, original_name='RecheckPathTime'
        ),
    })
    recheck_path_distance: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7626ec89, original_name='RecheckPathDistance'
        ),
    })
    unknown_0xdff6c19b: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xdff6c19b, original_name='Unknown'
        ),
    })
    unknown_0xf7381a24: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xf7381a24, original_name='Unknown'
        ),
    })
    unknown_0xb2c2928e: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb2c2928e, original_name='Unknown'
        ),
    })
    grapple_data: GrappleData = dataclasses.field(default_factory=GrappleData, metadata={
        'reflection': FieldReflection[GrappleData](
            GrappleData, id=0xf609c637, original_name='GrappleData', from_json=GrappleData.from_json, to_json=GrappleData.to_json
        ),
    })
    mod_inca_data: ModIncaData = dataclasses.field(default_factory=ModIncaData, metadata={
        'reflection': FieldReflection[ModIncaData](
            ModIncaData, id=0xb4c02854, original_name='ModIncaData', from_json=ModIncaData.from_json, to_json=ModIncaData.to_json
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
        if property_count != 24:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8acc7d20
        shooter = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2c83c012
        projectile = LaunchProjectileData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7ab4ab98
        missile_deflection_offset = Vector.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x88fa2acf
        missile_deflection_radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1d159832
        missile_deflection_rate = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x05015775
        beam_weapon_info = ElectricBeamInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8f1ded1b
        deflection_particle = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0b339fac
        beam_deflection_sound = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf10ee8e2
        unknown_0xf10ee8e2 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7171bfc2
        unknown_0x7171bfc2 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x24265839
        electric_beam_info = ElectricBeamInfo.from_stream(data, property_size, default_override={'length': 50.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xccdd3aca
        patrol = FlyerMovementMode.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc845d3c0
        attack_path = FlyerMovementMode.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfa2a173f
        attack = FlyerMovementMode.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe74cf583
        grapple_pull_distance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x176bd1f4
        min_idle_delay = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x02e00506
        max_idle_delay = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9aa90b6b
        recheck_path_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7626ec89
        recheck_path_distance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdff6c19b
        unknown_0xdff6c19b = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf7381a24
        unknown_0xf7381a24 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb2c2928e
        unknown_0xb2c2928e = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf609c637
        grapple_data = GrappleData.from_stream(data, property_size, default_override={'grapple_type': 1})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb4c02854
        mod_inca_data = ModIncaData.from_stream(data, property_size)
    
        return cls(shooter, projectile, missile_deflection_offset, missile_deflection_radius, missile_deflection_rate, beam_weapon_info, deflection_particle, beam_deflection_sound, unknown_0xf10ee8e2, unknown_0x7171bfc2, electric_beam_info, patrol, attack_path, attack, grapple_pull_distance, min_idle_delay, max_idle_delay, recheck_path_time, recheck_path_distance, unknown_0xdff6c19b, unknown_0xf7381a24, unknown_0xb2c2928e, grapple_data, mod_inca_data)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        num_properties_offset = data.tell()
        data.write(b'\x00\x10')  # 16 properties
        num_properties_written = 16

        data.write(b'\x8a\xcc} ')  # 0x8acc7d20
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.shooter))

        if self.projectile != default_override.get('projectile', LaunchProjectileData()):
            num_properties_written += 1
            data.write(b',\x83\xc0\x12')  # 0x2c83c012
            before = data.tell()
            data.write(b'\x00\x00')  # size placeholder
            self.projectile.to_stream(data)
            after = data.tell()
            data.seek(before)
            data.write(struct.pack(">H", after - before - 2))
            data.seek(after)

        data.write(b'z\xb4\xab\x98')  # 0x7ab4ab98
        data.write(b'\x00\x0c')  # size
        self.missile_deflection_offset.to_stream(data)

        if self.missile_deflection_radius != default_override.get('missile_deflection_radius', 20.0):
            num_properties_written += 1
            data.write(b'\x88\xfa*\xcf')  # 0x88fa2acf
            data.write(b'\x00\x04')  # size
            data.write(struct.pack('>f', self.missile_deflection_radius))

        if self.missile_deflection_rate != default_override.get('missile_deflection_rate', 120.0):
            num_properties_written += 1
            data.write(b'\x1d\x15\x982')  # 0x1d159832
            data.write(b'\x00\x04')  # size
            data.write(struct.pack('>f', self.missile_deflection_rate))

        if self.beam_weapon_info != default_override.get('beam_weapon_info', ElectricBeamInfo()):
            num_properties_written += 1
            data.write(b'\x05\x01Wu')  # 0x5015775
            before = data.tell()
            data.write(b'\x00\x00')  # size placeholder
            self.beam_weapon_info.to_stream(data)
            after = data.tell()
            data.seek(before)
            data.write(struct.pack(">H", after - before - 2))
            data.seek(after)

        if self.deflection_particle != default_override.get('deflection_particle', default_asset_id):
            num_properties_written += 1
            data.write(b'\x8f\x1d\xed\x1b')  # 0x8f1ded1b
            data.write(b'\x00\x08')  # size
            data.write(struct.pack(">Q", self.deflection_particle))

        if self.beam_deflection_sound != default_override.get('beam_deflection_sound', default_asset_id):
            num_properties_written += 1
            data.write(b'\x0b3\x9f\xac')  # 0xb339fac
            data.write(b'\x00\x08')  # size
            data.write(struct.pack(">Q", self.beam_deflection_sound))

        data.write(b'\xf1\x0e\xe8\xe2')  # 0xf10ee8e2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xf10ee8e2))

        data.write(b'qq\xbf\xc2')  # 0x7171bfc2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x7171bfc2))

        if self.electric_beam_info != default_override.get('electric_beam_info', ElectricBeamInfo()):
            num_properties_written += 1
            data.write(b'$&X9')  # 0x24265839
            before = data.tell()
            data.write(b'\x00\x00')  # size placeholder
            self.electric_beam_info.to_stream(data, default_override={'length': 50.0})
            after = data.tell()
            data.seek(before)
            data.write(struct.pack(">H", after - before - 2))
            data.seek(after)

        data.write(b'\xcc\xdd:\xca')  # 0xccdd3aca
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.patrol.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc8E\xd3\xc0')  # 0xc845d3c0
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.attack_path.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xfa*\x17?')  # 0xfa2a173f
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.attack.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xe7L\xf5\x83')  # 0xe74cf583
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.grapple_pull_distance))

        data.write(b'\x17k\xd1\xf4')  # 0x176bd1f4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_idle_delay))

        data.write(b'\x02\xe0\x05\x06')  # 0x2e00506
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_idle_delay))

        data.write(b'\x9a\xa9\x0bk')  # 0x9aa90b6b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.recheck_path_time))

        data.write(b'v&\xec\x89')  # 0x7626ec89
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.recheck_path_distance))

        data.write(b'\xdf\xf6\xc1\x9b')  # 0xdff6c19b
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xdff6c19b))

        data.write(b'\xf78\x1a$')  # 0xf7381a24
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xf7381a24))

        data.write(b'\xb2\xc2\x92\x8e')  # 0xb2c2928e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xb2c2928e))

        if self.grapple_data != default_override.get('grapple_data', GrappleData()):
            num_properties_written += 1
            data.write(b'\xf6\t\xc67')  # 0xf609c637
            before = data.tell()
            data.write(b'\x00\x00')  # size placeholder
            self.grapple_data.to_stream(data, default_override={'grapple_type': 1})
            after = data.tell()
            data.seek(before)
            data.write(struct.pack(">H", after - before - 2))
            data.seek(after)

        data.write(b'\xb4\xc0(T')  # 0xb4c02854
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.mod_inca_data.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        if num_properties_written != 16:
            struct_end_offset = data.tell()
            data.seek(num_properties_offset)
            data.write(struct.pack(">H", num_properties_written))
            data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("GragnolFlyerDataJson", data)
        return cls(
            shooter=json_data['shooter'],
            projectile=LaunchProjectileData.from_json(json_data['projectile']),
            missile_deflection_offset=Vector.from_json(json_data['missile_deflection_offset']),
            missile_deflection_radius=json_data['missile_deflection_radius'],
            missile_deflection_rate=json_data['missile_deflection_rate'],
            beam_weapon_info=ElectricBeamInfo.from_json(json_data['beam_weapon_info']),
            deflection_particle=json_data['deflection_particle'],
            beam_deflection_sound=json_data['beam_deflection_sound'],
            unknown_0xf10ee8e2=json_data['unknown_0xf10ee8e2'],
            unknown_0x7171bfc2=json_data['unknown_0x7171bfc2'],
            electric_beam_info=ElectricBeamInfo.from_json(json_data['electric_beam_info']),
            patrol=FlyerMovementMode.from_json(json_data['patrol']),
            attack_path=FlyerMovementMode.from_json(json_data['attack_path']),
            attack=FlyerMovementMode.from_json(json_data['attack']),
            grapple_pull_distance=json_data['grapple_pull_distance'],
            min_idle_delay=json_data['min_idle_delay'],
            max_idle_delay=json_data['max_idle_delay'],
            recheck_path_time=json_data['recheck_path_time'],
            recheck_path_distance=json_data['recheck_path_distance'],
            unknown_0xdff6c19b=json_data['unknown_0xdff6c19b'],
            unknown_0xf7381a24=json_data['unknown_0xf7381a24'],
            unknown_0xb2c2928e=json_data['unknown_0xb2c2928e'],
            grapple_data=GrappleData.from_json(json_data['grapple_data']),
            mod_inca_data=ModIncaData.from_json(json_data['mod_inca_data']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'shooter': self.shooter,
            'projectile': self.projectile.to_json(),
            'missile_deflection_offset': self.missile_deflection_offset.to_json(),
            'missile_deflection_radius': self.missile_deflection_radius,
            'missile_deflection_rate': self.missile_deflection_rate,
            'beam_weapon_info': self.beam_weapon_info.to_json(),
            'deflection_particle': self.deflection_particle,
            'beam_deflection_sound': self.beam_deflection_sound,
            'unknown_0xf10ee8e2': self.unknown_0xf10ee8e2,
            'unknown_0x7171bfc2': self.unknown_0x7171bfc2,
            'electric_beam_info': self.electric_beam_info.to_json(),
            'patrol': self.patrol.to_json(),
            'attack_path': self.attack_path.to_json(),
            'attack': self.attack.to_json(),
            'grapple_pull_distance': self.grapple_pull_distance,
            'min_idle_delay': self.min_idle_delay,
            'max_idle_delay': self.max_idle_delay,
            'recheck_path_time': self.recheck_path_time,
            'recheck_path_distance': self.recheck_path_distance,
            'unknown_0xdff6c19b': self.unknown_0xdff6c19b,
            'unknown_0xf7381a24': self.unknown_0xf7381a24,
            'unknown_0xb2c2928e': self.unknown_0xb2c2928e,
            'grapple_data': self.grapple_data.to_json(),
            'mod_inca_data': self.mod_inca_data.to_json(),
        }


def _decode_shooter(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_missile_deflection_offset(data: typing.BinaryIO, property_size: int) -> Vector:
    return Vector.from_stream(data)


def _decode_missile_deflection_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_missile_deflection_rate(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_deflection_particle(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_beam_deflection_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_unknown_0xf10ee8e2(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x7171bfc2(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_electric_beam_info(data: typing.BinaryIO, property_size: int) -> ElectricBeamInfo:
    return ElectricBeamInfo.from_stream(data, property_size, default_override={'length': 50.0})


def _decode_grapple_pull_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_min_idle_delay(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_idle_delay(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_recheck_path_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_recheck_path_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xdff6c19b(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xf7381a24(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xb2c2928e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_grapple_data(data: typing.BinaryIO, property_size: int) -> GrappleData:
    return GrappleData.from_stream(data, property_size, default_override={'grapple_type': 1})


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x8acc7d20: ('shooter', _decode_shooter),
    0x2c83c012: ('projectile', LaunchProjectileData.from_stream),
    0x7ab4ab98: ('missile_deflection_offset', _decode_missile_deflection_offset),
    0x88fa2acf: ('missile_deflection_radius', _decode_missile_deflection_radius),
    0x1d159832: ('missile_deflection_rate', _decode_missile_deflection_rate),
    0x5015775: ('beam_weapon_info', ElectricBeamInfo.from_stream),
    0x8f1ded1b: ('deflection_particle', _decode_deflection_particle),
    0xb339fac: ('beam_deflection_sound', _decode_beam_deflection_sound),
    0xf10ee8e2: ('unknown_0xf10ee8e2', _decode_unknown_0xf10ee8e2),
    0x7171bfc2: ('unknown_0x7171bfc2', _decode_unknown_0x7171bfc2),
    0x24265839: ('electric_beam_info', _decode_electric_beam_info),
    0xccdd3aca: ('patrol', FlyerMovementMode.from_stream),
    0xc845d3c0: ('attack_path', FlyerMovementMode.from_stream),
    0xfa2a173f: ('attack', FlyerMovementMode.from_stream),
    0xe74cf583: ('grapple_pull_distance', _decode_grapple_pull_distance),
    0x176bd1f4: ('min_idle_delay', _decode_min_idle_delay),
    0x2e00506: ('max_idle_delay', _decode_max_idle_delay),
    0x9aa90b6b: ('recheck_path_time', _decode_recheck_path_time),
    0x7626ec89: ('recheck_path_distance', _decode_recheck_path_distance),
    0xdff6c19b: ('unknown_0xdff6c19b', _decode_unknown_0xdff6c19b),
    0xf7381a24: ('unknown_0xf7381a24', _decode_unknown_0xf7381a24),
    0xb2c2928e: ('unknown_0xb2c2928e', _decode_unknown_0xb2c2928e),
    0xf609c637: ('grapple_data', _decode_grapple_data),
    0xb4c02854: ('mod_inca_data', ModIncaData.from_stream),
}
