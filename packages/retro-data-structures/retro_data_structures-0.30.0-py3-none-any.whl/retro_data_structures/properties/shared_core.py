# Generated File
import typing

import retro_data_structures.properties.prime.core.AnimationParameters as _AnimationParameters_Prime
import retro_data_structures.properties.echoes.core.AnimationParameters as _AnimationParameters_Echoes
import retro_data_structures.properties.corruption.core.AnimationParameters as _AnimationParameters_Corruption
import retro_data_structures.properties.prime.core.AssetId as _AssetId_Prime
import retro_data_structures.properties.echoes.core.AssetId as _AssetId_Echoes
import retro_data_structures.properties.corruption.core.AssetId as _AssetId_Corruption
import retro_data_structures.properties.prime.core.Color as _Color_Prime
import retro_data_structures.properties.echoes.core.Color as _Color_Echoes
import retro_data_structures.properties.corruption.core.Color as _Color_Corruption
import retro_data_structures.properties.prime.core.Spline as _Spline_Prime
import retro_data_structures.properties.echoes.core.Spline as _Spline_Echoes
import retro_data_structures.properties.corruption.core.Spline as _Spline_Corruption
import retro_data_structures.properties.prime.core.Vector as _Vector_Prime
import retro_data_structures.properties.echoes.core.Vector as _Vector_Echoes
import retro_data_structures.properties.corruption.core.Vector as _Vector_Corruption

AnimationParameters = typing.Union[
    _AnimationParameters_Prime.AnimationParameters,
    _AnimationParameters_Echoes.AnimationParameters,
    _AnimationParameters_Corruption.AnimationParameters
]
AssetId = typing.Union[
    _AssetId_Prime.AssetId,
    _AssetId_Echoes.AssetId,
    _AssetId_Corruption.AssetId
]
Color = typing.Union[
    _Color_Prime.Color,
    _Color_Echoes.Color,
    _Color_Corruption.Color
]
Spline = typing.Union[
    _Spline_Prime.Spline,
    _Spline_Echoes.Spline,
    _Spline_Corruption.Spline
]
Vector = typing.Union[
    _Vector_Prime.Vector,
    _Vector_Echoes.Vector,
    _Vector_Corruption.Vector
]
