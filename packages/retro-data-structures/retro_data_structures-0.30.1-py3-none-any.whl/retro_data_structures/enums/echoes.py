"""
Generated file.
"""
import enum
import typing
import struct
import typing_extensions

from retro_data_structures import json_util


class State(enum.Enum):
    NonZero = '!ZER'
    Active = 'ACTV'
    AILogicState1 = 'AIS1'
    AILogicState2 = 'AIS2'
    AILogicState3 = 'AIS3'
    Approach = 'APRC'
    Arrived = 'ARRV'
    AttachedCollisionObject = 'ATCL'
    AttachedAnimatedObject = 'ATOB'
    Attack = 'ATTK'
    BallIceXDamage = 'BIDG'
    BSCN = 'BSCN'
    BallXDamage = 'BXDG'
    Closed = 'CLOS'
    Connect = 'CONN'
    CPLR = 'CPLR'
    CameraPath = 'CPTH'
    CameraTarget = 'CTGT'
    CameraTime = 'CTIM'
    DamageAreaDark = 'DADR'
    DamageAreaLight = 'DALG'
    Damage = 'DAMG'
    DamageAnnihilator = 'DANN'
    DamageAI = 'DBAI'
    DamageBoostBall = 'DBAL'
    DamageBomb = 'DBMB'
    DamageCannonBall = 'DCAN'
    DamageCold = 'DCLD'
    DamageDark = 'DDRK'
    Dead = 'DEAD'
    DefaultState = 'DFST'
    DeGenerate = 'DGNR'
    DamageHot = 'DHOT'
    DamageLava = 'DLAV'
    DamageLight = 'DLGT'
    DamageMissile = 'DMIS'
    DamagePowerBomb = 'DPBM'
    DamagePhazon = 'DPHZ'
    DamagePower = 'DPWR'
    DamagePoisonWater = 'DPWT'
    DarkXDamage = 'DRKX'
    DamageScrewAttack = 'DSCW'
    DamageUnknownSource = 'DUNS'
    Entered = 'ENTR'
    ESCN = 'ESCN'
    Exited = 'EXIT'
    Footstep = 'FOOT'
    Freeze = 'FREZ'
    Generate = 'GRNT'
    InheritBounds = 'IBND'
    Inactive = 'ICTV'
    IceXDamage = 'IDMG'
    Inside = 'INSD'
    InternalState00 = 'IS00'
    InternalState01 = 'IS01'
    InternalState02 = 'IS02'
    InternalState03 = 'IS03'
    InternalState04 = 'IS04'
    InternalState05 = 'IS05'
    InternalState06 = 'IS06'
    InternalState07 = 'IS07'
    InternalState08 = 'IS08'
    InternalState09 = 'IS09'
    InternalState10 = 'IS10'
    InternalState11 = 'IS11'
    InternalState12 = 'IS12'
    InternalState13 = 'IS13'
    InternalState14 = 'IS14'
    InternalState15 = 'IS15'
    InternalState16 = 'IS16'
    InternalState17 = 'IS17'
    InternalState18 = 'IS18'
    InternalState19 = 'IS19'
    Left = 'LEFT'
    MaxReached = 'MAXR'
    Modify = 'MDFY'
    Open = 'OPEN'
    Play = 'PLAY'
    PressA = 'PRSA'
    PressB = 'PRSB'
    PressStart = 'PRST'
    PressX = 'PRSX'
    PressY = 'PRSY'
    PressZ = 'PRSZ'
    Patrol = 'PTRL'
    DeathRattle = 'RATL'
    SpawnResidue = 'RDUE'
    ReflectedDamage = 'REFD'
    ResistedDamage = 'RESD'
    Right = 'RGHT'
    Retreat = 'RTRT'
    ScanDone = 'SCND'
    ScanSource = 'SCNS'
    Sequence = 'SQNC'
    UnFreeze = 'UFRZ'
    Up = 'UP  '
    XDamage = 'XDMG'
    InBack = 'XINB'
    InFront = 'XINF'
    Zero = 'ZERO'

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None) -> typing_extensions.Self:
        return cls(struct.unpack(">L", data.read(4))[0])

    def to_stream(self, data: typing.BinaryIO) -> None:
        data.write(struct.pack(">L", self.value))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        assert isinstance(data, (str))
        return cls(data)

    def to_json(self) -> str:
        return self.value


class Message(enum.Enum):
    Action = 'ACTN'
    Activate = 'ACTV'
    Alert = 'ALRT'
    Arrive = 'ARRV'
    Attach = 'ATCH'
    Close = 'CLOS'
    ClearOriginator = 'CORG'
    Deactivate = 'DCTV'
    Decrement = 'DECR'
    Escape = 'ESCP'
    Follow = 'FOLW'
    InternalMessage00 = 'IM00'
    InternalMessage01 = 'IM01'
    InternalMessage02 = 'IM02'
    InternalMessage03 = 'IM03'
    InternalMessage04 = 'IM04'
    InternalMessage05 = 'IM05'
    InternalMessage06 = 'IM06'
    InternalMessage07 = 'IM07'
    InternalMessage08 = 'IM08'
    InternalMessage09 = 'IM09'
    InternalMessage10 = 'IM10'
    InternalMessage11 = 'IM11'
    InternalMessage12 = 'IM12'
    InternalMessage13 = 'IM13'
    InternalMessage14 = 'IM14'
    Increment = 'INCR'
    Kill = 'KILL'
    Left = 'LEFT'
    Load = 'LOAD'
    Lock = 'LOCK'
    Next = 'NEXT'
    Open = 'OPEN'
    Play = 'PLAY'
    Reset = 'RSET'
    ResetAndStart = 'RSTS'
    SetToMax = 'SMAX'
    SetOriginator = 'SORG'
    Stop = 'STOP'
    StopAndReset = 'STPR'
    Start = 'STRT'
    ToggleActive = 'TCTV'
    Unlock = 'ULCK'
    Unload = 'ULOD'
    XALD = 'XALD'
    XAUD = 'XAUD'
    Clear = 'XCLR'
    XCRT = 'XCRT'
    Delete = 'XDEL'
    XDamage = 'XDMG'
    XENF = 'XENF'
    XEPZ = 'XEPZ'
    XEXF = 'XEXF'
    XIPZ = 'XIPZ'
    XXPZ = 'XXPZ'
    SetToZero = 'ZERO'

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None) -> typing_extensions.Self:
        return cls(struct.unpack(">L", data.read(4))[0])

    def to_stream(self, data: typing.BinaryIO) -> None:
        data.write(struct.pack(">L", self.value))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        assert isinstance(data, (str))
        return cls(data)

    def to_json(self) -> str:
        return self.value


class InventorySlotEnum(enum.IntEnum):
    PowerBeam = 0
    DarkBeam = 1
    LightBeam = 2
    AnnihilatorBeam = 3
    SuperMissile = 4
    Darkburst = 5
    Sunburst = 6
    SonicBoom = 7
    CombatVisor = 8
    ScanVisor = 9
    DarkVisor = 10
    EchoVisor = 11
    VariaSuit = 12
    DarkSuit = 13
    LightSuit = 14
    MorphBall = 15
    BoostBall = 16
    SpiderBall = 17
    MorphBallBomb = 18
    ChargeBeam = 22
    GrappleBeam = 23
    SpaceJumpBoots = 24
    GravityBoost = 25
    SeekerLauncher = 26
    ScrewAttack = 27
    PowerBomb = 28
    MissileLauncher = 29
    BeamAmmoExpansion = 30
    EnergyTank = 32
    SkyTempleKey1 = 33
    SkyTempleKey2 = 34
    SkyTempleKey3 = 35
    SkyTempleKey4 = 36
    SkyTempleKey5 = 37
    SkyTempleKey6 = 38
    SkyTempleKey7 = 39
    SkyTempleKey8 = 40
    SkyTempleKey9 = 41
    DarkAgonKey1 = 42
    DarkAgonKey2 = 43
    DarkAgonKey3 = 44
    DarkTorvusKey1 = 45
    DarkTorvusKey2 = 46
    DarkTorvusKey3 = 47
    IngHiveKey1 = 48
    IngHiveKey2 = 49
    IngHiveKey3 = 50
    EnergyTransferModule = 51
    BeamCombo = 52

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


class PlayerItemEnum(enum.IntEnum):
    PowerBeam = 0
    DarkBeam = 1
    LightBeam = 2
    AnnihilatorBeam = 3
    SuperMissile = 4
    Darkburst = 5
    Sunburst = 6
    SonicBoom = 7
    CombatVisor = 8
    ScanVisor = 9
    DarkVisor = 10
    EchoVisor = 11
    VariaSuit = 12
    DarkSuit = 13
    LightSuit = 14
    MorphBall = 15
    BoostBall = 16
    SpiderBall = 17
    MorphBallBomb = 18
    LightBomb = 19
    DarkBomb = 20
    AnnihilatorBomb = 21
    ChargeBeam = 22
    GrappleBeam = 23
    SpaceJumpBoots = 24
    GravityBoost = 25
    SeekerLauncher = 26
    ScrewAttack = 27
    EnergyTransferModulePickup = 28
    SkyTempleKey1 = 29
    SkyTempleKey2 = 30
    SkyTempleKey3 = 31
    DarkAgonKey1 = 32
    DarkAgonKey2 = 33
    DarkAgonKey3 = 34
    DarkTorvusKey1 = 35
    DarkTorvusKey2 = 36
    DarkTorvusKey3 = 37
    IngHiveKey1 = 38
    IngHiveKey2 = 39
    IngHiveKey3 = 40
    HealthRefill = 41
    EnergyTank = 42
    PowerBomb = 43
    Missile = 44
    DarkAmmo = 45
    LightAmmo = 46
    ItemPercentage = 47
    NumPlayersJoined = 48
    NumPlayersInOptionsMenu = 49
    MiscCounter3 = 50
    MiscCounter4 = 51
    SwitchWeaponPower = 52
    SwitchWeaponDark = 53
    SwitchWeaponLight = 54
    SwitchWeaponAnnihilator = 55
    MultiChargeUpgrade = 56
    Invisibility = 57
    AmpDamage = 58
    Invincibility = 59
    UnknownItem60 = 60
    UnknownItem61 = 61
    UnknownItem62 = 62
    UnknownItem63 = 63
    FragCount = 64
    DiedCount = 65
    ArchenemyCount = 66
    PersistentCounter1 = 67
    PersistentCounter2 = 68
    PersistentCounter3 = 69
    PersistentCounter4 = 70
    PersistentCounter5 = 71
    PersistentCounter6 = 72
    PersistentCounter7 = 73
    PersistentCounter8 = 74
    SwitchVisorCombat = 75
    SwitchVisorScan = 76
    SwitchVisorDark = 77
    SwitchVisorEcho = 78
    CoinAmplifier = 79
    CoinCounter = 80
    UnlimitedMissiles = 81
    UnlimitedBeamAmmo = 82
    DarkShield = 83
    LightShield = 84
    AbsorbAttack = 85
    DeathBall = 86
    ScanVirus = 87
    VisorStatic = 88
    DisableBeamAmmo = 89
    DisableMissiles = 90
    DisableMorphBall = 91
    DisableBall = 92
    DisableSpaceJump = 93
    UnknownItem94 = 94
    HackedEffect = 95
    CannonBall = 96
    VioletTranslator = 97
    AmberTranslator = 98
    EmeraldTranslator = 99
    CobaltTranslator = 100
    SkyTempleKey4 = 101
    SkyTempleKey5 = 102
    SkyTempleKey6 = 103
    SkyTempleKey7 = 104
    SkyTempleKey8 = 105
    SkyTempleKey9 = 106
    EnergyTransferModuleInventory = 107
    ChargeCombo = 108

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


class ScanSpeedEnum(enum.IntEnum):
    Normal = 0
    Slow = 1

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


class WeaponTypeEnum(enum.IntEnum):
    Power = 0
    Dark = 1
    Light = 2
    Annihilator = 3
    Bomb = 4
    PowerBomb = 5
    Missile = 6
    BoostBall = 7
    CannonBall = 8
    ScrewAttack = 9
    Phazon = 10
    AI = 11
    PoisonWater1 = 12
    PoisonWater2 = 13
    Lava = 14
    Hot = 15
    Cold = 16
    AreaDark = 17
    AreaLight = 18
    UnknownSource = 19
    SafeZone = 20

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
