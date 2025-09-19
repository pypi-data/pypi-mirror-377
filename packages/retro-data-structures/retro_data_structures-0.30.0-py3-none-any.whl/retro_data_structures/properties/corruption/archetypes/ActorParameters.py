# Generated File
from __future__ import annotations

import dataclasses
import enum
import struct
import typing
import typing_extensions

from retro_data_structures import json_util
from retro_data_structures.game_check import Game
from retro_data_structures.properties.base_property import BaseProperty
from retro_data_structures.properties.field_reflection import FieldReflection
from retro_data_structures.properties.corruption.archetypes.LightParameters import LightParameters
from retro_data_structures.properties.corruption.archetypes.ScannableParameters import ScannableParameters
from retro_data_structures.properties.corruption.archetypes.VisorParameters import VisorParameters
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    class ActorParametersJson(typing_extensions.TypedDict):
        lighting: json_util.JsonObject
        scannable: json_util.JsonObject
        x_ray_model: int
        x_ray_skin: int
        use_global_render_time: bool
        fade_in_time: float
        fade_out_time: float
        visor: json_util.JsonObject
        force_render_unsorted: bool
        takes_projected_shadow: bool
        unknown_0xf07981e8: bool
        unknown_0x4d55f7d4: bool
        actor_material_type: int
        actor_collision_response: int
        max_volume: int
        is_hostile: bool
    

class ActorMaterialType(enum.IntEnum):
    kMT_Unknown = 3498468170
    kMT_Stone = 1104775585
    kMT_Metal = 2560325698
    kMT_Grass = 4042527608
    kMT_Ice = 173689903
    kMT_MetaGrating = 35715264
    kMT_Phazon = 687970960
    kMT_Dirt = 114101165
    kMT_SP_Metal = 520586891
    kMT_Glass = 1077031892
    kMT_Snow = 2821279656
    kMT_Shield = 3064176193
    kMT_Sand = 1053849610
    kMT_SeedOrganics = 3543027614
    kMT_Web = 3571249264
    kMT_Wood = 2721575702
    kMT_Organic = 1369290280
    kMT_Rubber = 316113227

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None) -> typing_extensions.Self:
        return cls(struct.unpack(">L", data.read(4))[0])

    def to_stream(self, data: typing.BinaryIO) -> None:
        data.write(struct.pack(">L", self.value))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        assert isinstance(data, (int))
        return cls(data)

    def to_json(self) -> int:
        return self.value


class ActorCollisionResponse(enum.IntEnum):
    kACR_Default = 3733775805
    Unknown2 = 652573799
    Unknown3 = 1071627662

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None) -> typing_extensions.Self:
        return cls(struct.unpack(">L", data.read(4))[0])

    def to_stream(self, data: typing.BinaryIO) -> None:
        data.write(struct.pack(">L", self.value))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        assert isinstance(data, (int))
        return cls(data)

    def to_json(self) -> int:
        return self.value


@dataclasses.dataclass()
class ActorParameters(BaseProperty):
    lighting: LightParameters = dataclasses.field(default_factory=LightParameters, metadata={
        'reflection': FieldReflection[LightParameters](
            LightParameters, id=0xb028db0e, original_name='Lighting', from_json=LightParameters.from_json, to_json=LightParameters.to_json
        ),
    })
    scannable: ScannableParameters = dataclasses.field(default_factory=ScannableParameters, metadata={
        'reflection': FieldReflection[ScannableParameters](
            ScannableParameters, id=0x375bfd7c, original_name='Scannable', from_json=ScannableParameters.from_json, to_json=ScannableParameters.to_json
        ),
    })
    x_ray_model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xbb52f0be, original_name='XRayModel'
        ),
    })
    x_ray_skin: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': [], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xc647755b, original_name='XRaySkin'
        ),
    })
    use_global_render_time: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x1499803c, original_name='UseGlobalRenderTime'
        ),
    })
    fade_in_time: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x90aa341f, original_name='FadeInTime'
        ),
    })
    fade_out_time: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7c269ebc, original_name='FadeOutTime'
        ),
    })
    visor: VisorParameters = dataclasses.field(default_factory=VisorParameters, metadata={
        'reflection': FieldReflection[VisorParameters](
            VisorParameters, id=0x05ad250e, original_name='Visor', from_json=VisorParameters.from_json, to_json=VisorParameters.to_json
        ),
    })
    force_render_unsorted: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x799263f1, original_name='ForceRenderUnsorted'
        ),
    })
    takes_projected_shadow: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xed3a6e87, original_name='TakesProjectedShadow'
        ),
    })
    unknown_0xf07981e8: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xf07981e8, original_name='Unknown'
        ),
    })
    unknown_0x4d55f7d4: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x4d55f7d4, original_name='Unknown'
        ),
    })
    actor_material_type: ActorMaterialType = dataclasses.field(default=ActorMaterialType.kMT_Unknown, metadata={
        'reflection': FieldReflection[ActorMaterialType](
            ActorMaterialType, id=0xe315ee72, original_name='ActorMaterialType', from_json=ActorMaterialType.from_json, to_json=ActorMaterialType.to_json
        ),
    })
    actor_collision_response: ActorCollisionResponse = dataclasses.field(default=ActorCollisionResponse.kACR_Default, metadata={
        'reflection': FieldReflection[ActorCollisionResponse](
            ActorCollisionResponse, id=0x583895fa, original_name='ActorCollisionResponse', from_json=ActorCollisionResponse.from_json, to_json=ActorCollisionResponse.to_json
        ),
    })
    max_volume: int = dataclasses.field(default=127, metadata={
        'reflection': FieldReflection[int](
            int, id=0xc712847c, original_name='MaxVolume'
        ),
    })
    is_hostile: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x701b61b3, original_name='IsHostile'
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
        if property_count != 16:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb028db0e
        lighting = LightParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x375bfd7c
        scannable = ScannableParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbb52f0be
        x_ray_model = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc647755b
        x_ray_skin = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1499803c
        use_global_render_time = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x90aa341f
        fade_in_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7c269ebc
        fade_out_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x05ad250e
        visor = VisorParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x799263f1
        force_render_unsorted = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xed3a6e87
        takes_projected_shadow = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf07981e8
        unknown_0xf07981e8 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4d55f7d4
        unknown_0x4d55f7d4 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe315ee72
        actor_material_type = ActorMaterialType.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x583895fa
        actor_collision_response = ActorCollisionResponse.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc712847c
        max_volume = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x701b61b3
        is_hostile = struct.unpack('>?', data.read(1))[0]
    
        return cls(lighting, scannable, x_ray_model, x_ray_skin, use_global_render_time, fade_in_time, fade_out_time, visor, force_render_unsorted, takes_projected_shadow, unknown_0xf07981e8, unknown_0x4d55f7d4, actor_material_type, actor_collision_response, max_volume, is_hostile)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x10')  # 16 properties

        data.write(b'\xb0(\xdb\x0e')  # 0xb028db0e
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.lighting.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'7[\xfd|')  # 0x375bfd7c
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.scannable.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xbbR\xf0\xbe')  # 0xbb52f0be
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.x_ray_model))

        data.write(b'\xc6Gu[')  # 0xc647755b
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.x_ray_skin))

        data.write(b'\x14\x99\x80<')  # 0x1499803c
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.use_global_render_time))

        data.write(b'\x90\xaa4\x1f')  # 0x90aa341f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.fade_in_time))

        data.write(b'|&\x9e\xbc')  # 0x7c269ebc
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.fade_out_time))

        data.write(b'\x05\xad%\x0e')  # 0x5ad250e
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.visor.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'y\x92c\xf1')  # 0x799263f1
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.force_render_unsorted))

        data.write(b'\xed:n\x87')  # 0xed3a6e87
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.takes_projected_shadow))

        data.write(b'\xf0y\x81\xe8')  # 0xf07981e8
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xf07981e8))

        data.write(b'MU\xf7\xd4')  # 0x4d55f7d4
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x4d55f7d4))

        data.write(b'\xe3\x15\xeer')  # 0xe315ee72
        data.write(b'\x00\x04')  # size
        self.actor_material_type.to_stream(data)

        data.write(b'X8\x95\xfa')  # 0x583895fa
        data.write(b'\x00\x04')  # size
        self.actor_collision_response.to_stream(data)

        data.write(b'\xc7\x12\x84|')  # 0xc712847c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.max_volume))

        data.write(b'p\x1ba\xb3')  # 0x701b61b3
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.is_hostile))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("ActorParametersJson", data)
        return cls(
            lighting=LightParameters.from_json(json_data['lighting']),
            scannable=ScannableParameters.from_json(json_data['scannable']),
            x_ray_model=json_data['x_ray_model'],
            x_ray_skin=json_data['x_ray_skin'],
            use_global_render_time=json_data['use_global_render_time'],
            fade_in_time=json_data['fade_in_time'],
            fade_out_time=json_data['fade_out_time'],
            visor=VisorParameters.from_json(json_data['visor']),
            force_render_unsorted=json_data['force_render_unsorted'],
            takes_projected_shadow=json_data['takes_projected_shadow'],
            unknown_0xf07981e8=json_data['unknown_0xf07981e8'],
            unknown_0x4d55f7d4=json_data['unknown_0x4d55f7d4'],
            actor_material_type=ActorMaterialType.from_json(json_data['actor_material_type']),
            actor_collision_response=ActorCollisionResponse.from_json(json_data['actor_collision_response']),
            max_volume=json_data['max_volume'],
            is_hostile=json_data['is_hostile'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'lighting': self.lighting.to_json(),
            'scannable': self.scannable.to_json(),
            'x_ray_model': self.x_ray_model,
            'x_ray_skin': self.x_ray_skin,
            'use_global_render_time': self.use_global_render_time,
            'fade_in_time': self.fade_in_time,
            'fade_out_time': self.fade_out_time,
            'visor': self.visor.to_json(),
            'force_render_unsorted': self.force_render_unsorted,
            'takes_projected_shadow': self.takes_projected_shadow,
            'unknown_0xf07981e8': self.unknown_0xf07981e8,
            'unknown_0x4d55f7d4': self.unknown_0x4d55f7d4,
            'actor_material_type': self.actor_material_type.to_json(),
            'actor_collision_response': self.actor_collision_response.to_json(),
            'max_volume': self.max_volume,
            'is_hostile': self.is_hostile,
        }


def _decode_x_ray_model(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_x_ray_skin(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_use_global_render_time(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_fade_in_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_fade_out_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_force_render_unsorted(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_takes_projected_shadow(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xf07981e8(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x4d55f7d4(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_actor_material_type(data: typing.BinaryIO, property_size: int) -> ActorMaterialType:
    return ActorMaterialType.from_stream(data)


def _decode_actor_collision_response(data: typing.BinaryIO, property_size: int) -> ActorCollisionResponse:
    return ActorCollisionResponse.from_stream(data)


def _decode_max_volume(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_is_hostile(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xb028db0e: ('lighting', LightParameters.from_stream),
    0x375bfd7c: ('scannable', ScannableParameters.from_stream),
    0xbb52f0be: ('x_ray_model', _decode_x_ray_model),
    0xc647755b: ('x_ray_skin', _decode_x_ray_skin),
    0x1499803c: ('use_global_render_time', _decode_use_global_render_time),
    0x90aa341f: ('fade_in_time', _decode_fade_in_time),
    0x7c269ebc: ('fade_out_time', _decode_fade_out_time),
    0x5ad250e: ('visor', VisorParameters.from_stream),
    0x799263f1: ('force_render_unsorted', _decode_force_render_unsorted),
    0xed3a6e87: ('takes_projected_shadow', _decode_takes_projected_shadow),
    0xf07981e8: ('unknown_0xf07981e8', _decode_unknown_0xf07981e8),
    0x4d55f7d4: ('unknown_0x4d55f7d4', _decode_unknown_0x4d55f7d4),
    0xe315ee72: ('actor_material_type', _decode_actor_material_type),
    0x583895fa: ('actor_collision_response', _decode_actor_collision_response),
    0xc712847c: ('max_volume', _decode_max_volume),
    0x701b61b3: ('is_hostile', _decode_is_hostile),
}
