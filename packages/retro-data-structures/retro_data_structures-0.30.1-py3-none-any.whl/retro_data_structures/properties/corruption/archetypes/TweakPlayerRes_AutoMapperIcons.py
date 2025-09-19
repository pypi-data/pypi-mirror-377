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

if typing.TYPE_CHECKING:
    class TweakPlayerRes_AutoMapperIconsJson(typing_extensions.TypedDict):
        landing_site: str
        unknown_0xdd1b0445: str
        warp_portal: str
        save_station: str
        map_station: str
        unknown_0xdfac0db1: str
        unknown_0xb838c9c0: str
        unknown_0x5096bfa5: str
        unknown_0x5291eb5f: str
        unknown_0xf4e6e0eb: str
        unknown_0x65700ccc: str
        unknown_0xa0d73242: str
    

@dataclasses.dataclass()
class TweakPlayerRes_AutoMapperIcons(BaseProperty):
    landing_site: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x1eba4bd8, original_name='LandingSite'
        ),
    })
    unknown_0xdd1b0445: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0xdd1b0445, original_name='Unknown'
        ),
    })
    warp_portal: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0xb35b7bec, original_name='WarpPortal'
        ),
    })
    save_station: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x64667637, original_name='SaveStation'
        ),
    })
    map_station: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0xd5d00133, original_name='MapStation'
        ),
    })
    unknown_0xdfac0db1: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0xdfac0db1, original_name='Unknown'
        ),
    })
    unknown_0xb838c9c0: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0xb838c9c0, original_name='Unknown'
        ),
    })
    unknown_0x5096bfa5: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x5096bfa5, original_name='Unknown'
        ),
    })
    unknown_0x5291eb5f: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x5291eb5f, original_name='Unknown'
        ),
    })
    unknown_0xf4e6e0eb: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0xf4e6e0eb, original_name='Unknown'
        ),
    })
    unknown_0x65700ccc: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x65700ccc, original_name='Unknown'
        ),
    })
    unknown_0xa0d73242: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0xa0d73242, original_name='Unknown'
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
        if property_count != 12:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1eba4bd8
        landing_site = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdd1b0445
        unknown_0xdd1b0445 = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb35b7bec
        warp_portal = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x64667637
        save_station = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd5d00133
        map_station = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdfac0db1
        unknown_0xdfac0db1 = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb838c9c0
        unknown_0xb838c9c0 = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5096bfa5
        unknown_0x5096bfa5 = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5291eb5f
        unknown_0x5291eb5f = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf4e6e0eb
        unknown_0xf4e6e0eb = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x65700ccc
        unknown_0x65700ccc = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa0d73242
        unknown_0xa0d73242 = data.read(property_size)[:-1].decode("utf-8")
    
        return cls(landing_site, unknown_0xdd1b0445, warp_portal, save_station, map_station, unknown_0xdfac0db1, unknown_0xb838c9c0, unknown_0x5096bfa5, unknown_0x5291eb5f, unknown_0xf4e6e0eb, unknown_0x65700ccc, unknown_0xa0d73242)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x0c')  # 12 properties

        data.write(b'\x1e\xbaK\xd8')  # 0x1eba4bd8
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.landing_site.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xdd\x1b\x04E')  # 0xdd1b0445
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.unknown_0xdd1b0445.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xb3[{\xec')  # 0xb35b7bec
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.warp_portal.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'dfv7')  # 0x64667637
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.save_station.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xd5\xd0\x013')  # 0xd5d00133
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.map_station.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xdf\xac\r\xb1')  # 0xdfac0db1
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.unknown_0xdfac0db1.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xb88\xc9\xc0')  # 0xb838c9c0
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.unknown_0xb838c9c0.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'P\x96\xbf\xa5')  # 0x5096bfa5
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.unknown_0x5096bfa5.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'R\x91\xeb_')  # 0x5291eb5f
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.unknown_0x5291eb5f.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xf4\xe6\xe0\xeb')  # 0xf4e6e0eb
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.unknown_0xf4e6e0eb.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'ep\x0c\xcc')  # 0x65700ccc
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.unknown_0x65700ccc.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xa0\xd72B')  # 0xa0d73242
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.unknown_0xa0d73242.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("TweakPlayerRes_AutoMapperIconsJson", data)
        return cls(
            landing_site=json_data['landing_site'],
            unknown_0xdd1b0445=json_data['unknown_0xdd1b0445'],
            warp_portal=json_data['warp_portal'],
            save_station=json_data['save_station'],
            map_station=json_data['map_station'],
            unknown_0xdfac0db1=json_data['unknown_0xdfac0db1'],
            unknown_0xb838c9c0=json_data['unknown_0xb838c9c0'],
            unknown_0x5096bfa5=json_data['unknown_0x5096bfa5'],
            unknown_0x5291eb5f=json_data['unknown_0x5291eb5f'],
            unknown_0xf4e6e0eb=json_data['unknown_0xf4e6e0eb'],
            unknown_0x65700ccc=json_data['unknown_0x65700ccc'],
            unknown_0xa0d73242=json_data['unknown_0xa0d73242'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'landing_site': self.landing_site,
            'unknown_0xdd1b0445': self.unknown_0xdd1b0445,
            'warp_portal': self.warp_portal,
            'save_station': self.save_station,
            'map_station': self.map_station,
            'unknown_0xdfac0db1': self.unknown_0xdfac0db1,
            'unknown_0xb838c9c0': self.unknown_0xb838c9c0,
            'unknown_0x5096bfa5': self.unknown_0x5096bfa5,
            'unknown_0x5291eb5f': self.unknown_0x5291eb5f,
            'unknown_0xf4e6e0eb': self.unknown_0xf4e6e0eb,
            'unknown_0x65700ccc': self.unknown_0x65700ccc,
            'unknown_0xa0d73242': self.unknown_0xa0d73242,
        }


def _decode_landing_site(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_unknown_0xdd1b0445(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_warp_portal(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_save_station(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_map_station(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_unknown_0xdfac0db1(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_unknown_0xb838c9c0(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_unknown_0x5096bfa5(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_unknown_0x5291eb5f(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_unknown_0xf4e6e0eb(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_unknown_0x65700ccc(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_unknown_0xa0d73242(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x1eba4bd8: ('landing_site', _decode_landing_site),
    0xdd1b0445: ('unknown_0xdd1b0445', _decode_unknown_0xdd1b0445),
    0xb35b7bec: ('warp_portal', _decode_warp_portal),
    0x64667637: ('save_station', _decode_save_station),
    0xd5d00133: ('map_station', _decode_map_station),
    0xdfac0db1: ('unknown_0xdfac0db1', _decode_unknown_0xdfac0db1),
    0xb838c9c0: ('unknown_0xb838c9c0', _decode_unknown_0xb838c9c0),
    0x5096bfa5: ('unknown_0x5096bfa5', _decode_unknown_0x5096bfa5),
    0x5291eb5f: ('unknown_0x5291eb5f', _decode_unknown_0x5291eb5f),
    0xf4e6e0eb: ('unknown_0xf4e6e0eb', _decode_unknown_0xf4e6e0eb),
    0x65700ccc: ('unknown_0x65700ccc', _decode_unknown_0x65700ccc),
    0xa0d73242: ('unknown_0xa0d73242', _decode_unknown_0xa0d73242),
}
