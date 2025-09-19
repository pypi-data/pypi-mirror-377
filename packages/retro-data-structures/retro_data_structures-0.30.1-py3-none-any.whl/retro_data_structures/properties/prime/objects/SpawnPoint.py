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
from retro_data_structures.properties.prime.core.Vector import Vector

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class SpawnPointJson(typing_extensions.TypedDict):
        name: str
        position: json_util.JsonValue
        rotation: json_util.JsonValue
        power_beam: int
        ice_beam: int
        wave_beam: int
        plasma_beam: int
        missiles: int
        scan_visor: int
        morph_ball_bomb: int
        power_bombs: int
        flamethrower: int
        thermal_visor: int
        charge_beam: int
        super_missile: int
        grapple_beam: int
        x_ray_visor: int
        ice_spreader: int
        space_jump_boots: int
        morph_ball: int
        combat_visor: int
        boost_ball: int
        spider_ball: int
        power_suit: int
        gravity_suit: int
        varia_suit: int
        phazon_suit: int
        energy_tanks: int
        unknown_item_1: int
        health_refill: int
        unknown_item_2: int
        wavebuster: int
        default_spawn: bool
        active: bool
        morphed: bool
    

@dataclasses.dataclass()
class SpawnPoint(BaseObjectType):
    name: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x00000000, original_name='Name'
        ),
    })
    position: Vector = dataclasses.field(default_factory=Vector, metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x00000001, original_name='Position', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    rotation: Vector = dataclasses.field(default_factory=Vector, metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x00000002, original_name='Rotation', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    power_beam: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000003, original_name='Power Beam'
        ),
    })
    ice_beam: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000004, original_name='Ice Beam'
        ),
    })
    wave_beam: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000005, original_name='Wave Beam'
        ),
    })
    plasma_beam: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000006, original_name='Plasma Beam'
        ),
    })
    missiles: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000007, original_name='Missiles'
        ),
    })
    scan_visor: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000008, original_name='Scan Visor'
        ),
    })
    morph_ball_bomb: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000009, original_name='Morph Ball Bomb'
        ),
    })
    power_bombs: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x0000000a, original_name='Power Bombs'
        ),
    })
    flamethrower: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x0000000b, original_name='Flamethrower'
        ),
    })
    thermal_visor: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x0000000c, original_name='Thermal Visor'
        ),
    })
    charge_beam: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x0000000d, original_name='Charge Beam'
        ),
    })
    super_missile: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x0000000e, original_name='Super Missile'
        ),
    })
    grapple_beam: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x0000000f, original_name='Grapple Beam'
        ),
    })
    x_ray_visor: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000010, original_name='X-Ray Visor'
        ),
    })
    ice_spreader: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000011, original_name='Ice Spreader'
        ),
    })
    space_jump_boots: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000012, original_name='Space Jump Boots'
        ),
    })
    morph_ball: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000013, original_name='Morph Ball'
        ),
    })
    combat_visor: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000014, original_name='Combat Visor'
        ),
    })
    boost_ball: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000015, original_name='Boost Ball'
        ),
    })
    spider_ball: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000016, original_name='Spider Ball'
        ),
    })
    power_suit: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000017, original_name='Power Suit?'
        ),
    })
    gravity_suit: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000018, original_name='Gravity Suit'
        ),
    })
    varia_suit: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000019, original_name='Varia Suit'
        ),
    })
    phazon_suit: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x0000001a, original_name='Phazon Suit'
        ),
    })
    energy_tanks: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x0000001b, original_name='Energy Tanks'
        ),
    })
    unknown_item_1: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x0000001c, original_name='Unknown Item 1'
        ),
    })
    health_refill: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x0000001d, original_name='Health Refill'
        ),
    })
    unknown_item_2: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x0000001e, original_name='Unknown Item 2'
        ),
    })
    wavebuster: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x0000001f, original_name='Wavebuster'
        ),
    })
    default_spawn: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000020, original_name='Default Spawn'
        ),
    })
    active: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000021, original_name='Active'
        ),
    })
    morphed: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000022, original_name='Morphed'
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.PRIME

    def get_name(self) -> str | None:
        return self.name

    def set_name(self, name: str) -> None:
        self.name = name

    @classmethod
    def object_type(cls) -> int:
        return 0xF

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        property_count = struct.unpack(">L", data.read(4))[0]
        name = b"".join(iter(lambda: data.read(1), b'\x00')).decode("utf-8")
        position = Vector.from_stream(data)
        rotation = Vector.from_stream(data)
        power_beam = struct.unpack('>l', data.read(4))[0]
        ice_beam = struct.unpack('>l', data.read(4))[0]
        wave_beam = struct.unpack('>l', data.read(4))[0]
        plasma_beam = struct.unpack('>l', data.read(4))[0]
        missiles = struct.unpack('>l', data.read(4))[0]
        scan_visor = struct.unpack('>l', data.read(4))[0]
        morph_ball_bomb = struct.unpack('>l', data.read(4))[0]
        power_bombs = struct.unpack('>l', data.read(4))[0]
        flamethrower = struct.unpack('>l', data.read(4))[0]
        thermal_visor = struct.unpack('>l', data.read(4))[0]
        charge_beam = struct.unpack('>l', data.read(4))[0]
        super_missile = struct.unpack('>l', data.read(4))[0]
        grapple_beam = struct.unpack('>l', data.read(4))[0]
        x_ray_visor = struct.unpack('>l', data.read(4))[0]
        ice_spreader = struct.unpack('>l', data.read(4))[0]
        space_jump_boots = struct.unpack('>l', data.read(4))[0]
        morph_ball = struct.unpack('>l', data.read(4))[0]
        combat_visor = struct.unpack('>l', data.read(4))[0]
        boost_ball = struct.unpack('>l', data.read(4))[0]
        spider_ball = struct.unpack('>l', data.read(4))[0]
        power_suit = struct.unpack('>l', data.read(4))[0]
        gravity_suit = struct.unpack('>l', data.read(4))[0]
        varia_suit = struct.unpack('>l', data.read(4))[0]
        phazon_suit = struct.unpack('>l', data.read(4))[0]
        energy_tanks = struct.unpack('>l', data.read(4))[0]
        unknown_item_1 = struct.unpack('>l', data.read(4))[0]
        health_refill = struct.unpack('>l', data.read(4))[0]
        unknown_item_2 = struct.unpack('>l', data.read(4))[0]
        wavebuster = struct.unpack('>l', data.read(4))[0]
        default_spawn = struct.unpack('>?', data.read(1))[0]
        active = struct.unpack('>?', data.read(1))[0]
        morphed = struct.unpack('>?', data.read(1))[0]
        return cls(name, position, rotation, power_beam, ice_beam, wave_beam, plasma_beam, missiles, scan_visor, morph_ball_bomb, power_bombs, flamethrower, thermal_visor, charge_beam, super_missile, grapple_beam, x_ray_visor, ice_spreader, space_jump_boots, morph_ball, combat_visor, boost_ball, spider_ball, power_suit, gravity_suit, varia_suit, phazon_suit, energy_tanks, unknown_item_1, health_refill, unknown_item_2, wavebuster, default_spawn, active, morphed)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x00\x00#')  # 35 properties
        data.write(self.name.encode("utf-8"))
        data.write(b'\x00')
        self.position.to_stream(data)
        self.rotation.to_stream(data)
        data.write(struct.pack('>l', self.power_beam))
        data.write(struct.pack('>l', self.ice_beam))
        data.write(struct.pack('>l', self.wave_beam))
        data.write(struct.pack('>l', self.plasma_beam))
        data.write(struct.pack('>l', self.missiles))
        data.write(struct.pack('>l', self.scan_visor))
        data.write(struct.pack('>l', self.morph_ball_bomb))
        data.write(struct.pack('>l', self.power_bombs))
        data.write(struct.pack('>l', self.flamethrower))
        data.write(struct.pack('>l', self.thermal_visor))
        data.write(struct.pack('>l', self.charge_beam))
        data.write(struct.pack('>l', self.super_missile))
        data.write(struct.pack('>l', self.grapple_beam))
        data.write(struct.pack('>l', self.x_ray_visor))
        data.write(struct.pack('>l', self.ice_spreader))
        data.write(struct.pack('>l', self.space_jump_boots))
        data.write(struct.pack('>l', self.morph_ball))
        data.write(struct.pack('>l', self.combat_visor))
        data.write(struct.pack('>l', self.boost_ball))
        data.write(struct.pack('>l', self.spider_ball))
        data.write(struct.pack('>l', self.power_suit))
        data.write(struct.pack('>l', self.gravity_suit))
        data.write(struct.pack('>l', self.varia_suit))
        data.write(struct.pack('>l', self.phazon_suit))
        data.write(struct.pack('>l', self.energy_tanks))
        data.write(struct.pack('>l', self.unknown_item_1))
        data.write(struct.pack('>l', self.health_refill))
        data.write(struct.pack('>l', self.unknown_item_2))
        data.write(struct.pack('>l', self.wavebuster))
        data.write(struct.pack('>?', self.default_spawn))
        data.write(struct.pack('>?', self.active))
        data.write(struct.pack('>?', self.morphed))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("SpawnPointJson", data)
        return cls(
            name=json_data['name'],
            position=Vector.from_json(json_data['position']),
            rotation=Vector.from_json(json_data['rotation']),
            power_beam=json_data['power_beam'],
            ice_beam=json_data['ice_beam'],
            wave_beam=json_data['wave_beam'],
            plasma_beam=json_data['plasma_beam'],
            missiles=json_data['missiles'],
            scan_visor=json_data['scan_visor'],
            morph_ball_bomb=json_data['morph_ball_bomb'],
            power_bombs=json_data['power_bombs'],
            flamethrower=json_data['flamethrower'],
            thermal_visor=json_data['thermal_visor'],
            charge_beam=json_data['charge_beam'],
            super_missile=json_data['super_missile'],
            grapple_beam=json_data['grapple_beam'],
            x_ray_visor=json_data['x_ray_visor'],
            ice_spreader=json_data['ice_spreader'],
            space_jump_boots=json_data['space_jump_boots'],
            morph_ball=json_data['morph_ball'],
            combat_visor=json_data['combat_visor'],
            boost_ball=json_data['boost_ball'],
            spider_ball=json_data['spider_ball'],
            power_suit=json_data['power_suit'],
            gravity_suit=json_data['gravity_suit'],
            varia_suit=json_data['varia_suit'],
            phazon_suit=json_data['phazon_suit'],
            energy_tanks=json_data['energy_tanks'],
            unknown_item_1=json_data['unknown_item_1'],
            health_refill=json_data['health_refill'],
            unknown_item_2=json_data['unknown_item_2'],
            wavebuster=json_data['wavebuster'],
            default_spawn=json_data['default_spawn'],
            active=json_data['active'],
            morphed=json_data['morphed'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'name': self.name,
            'position': self.position.to_json(),
            'rotation': self.rotation.to_json(),
            'power_beam': self.power_beam,
            'ice_beam': self.ice_beam,
            'wave_beam': self.wave_beam,
            'plasma_beam': self.plasma_beam,
            'missiles': self.missiles,
            'scan_visor': self.scan_visor,
            'morph_ball_bomb': self.morph_ball_bomb,
            'power_bombs': self.power_bombs,
            'flamethrower': self.flamethrower,
            'thermal_visor': self.thermal_visor,
            'charge_beam': self.charge_beam,
            'super_missile': self.super_missile,
            'grapple_beam': self.grapple_beam,
            'x_ray_visor': self.x_ray_visor,
            'ice_spreader': self.ice_spreader,
            'space_jump_boots': self.space_jump_boots,
            'morph_ball': self.morph_ball,
            'combat_visor': self.combat_visor,
            'boost_ball': self.boost_ball,
            'spider_ball': self.spider_ball,
            'power_suit': self.power_suit,
            'gravity_suit': self.gravity_suit,
            'varia_suit': self.varia_suit,
            'phazon_suit': self.phazon_suit,
            'energy_tanks': self.energy_tanks,
            'unknown_item_1': self.unknown_item_1,
            'health_refill': self.health_refill,
            'unknown_item_2': self.unknown_item_2,
            'wavebuster': self.wavebuster,
            'default_spawn': self.default_spawn,
            'active': self.active,
            'morphed': self.morphed,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []
