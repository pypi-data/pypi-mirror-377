
  
from dataclasses import dataclass
from typing import Optional, Union, Literal, TypedDict, Any, Tuple, List
from datetime import datetime
from qpace import Ctx, Backtest
from qpace_content import _lib
  
  


def accdist(ctx: Ctx, ) -> List[float]:
    """
Total money flowing in and out (Accumulation/Distribution)

`accdist() -> float`
    """
    return _lib.Incr_fn_accdist_ee1631(ctx=ctx, ).collect()

class AccdistLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Accdist:
    """
Total money flowing in and out (Accumulation/Distribution)

`accdist() -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_accdist_ee1631(ctx, )
        self.locals = AccdistLocals(self.inner)

    def next(self, ) -> Optional[float]:
        return self.inner.next()
    



def cum(ctx: Ctx, src: List[float], ) -> List[float]:
    """
Adds up the values so far (running total)

`cum(series<float> src) -> float`
    """
    return _lib.Incr_fn_cum_e4a473(ctx=ctx, ).collect(_11985_src=src)

class CumLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Cum:
    """
Adds up the values so far (running total)

`cum(series<float> src) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_cum_e4a473(ctx, )
        self.locals = CumLocals(self.inner)

    def next(self, src: float) -> Optional[float]:
        return self.inner.next(_11985_src=src)
    



def change(ctx: Ctx, src: List[float], ) -> List[float]:
    """
How much it moved from the previous bar

`change(series<float> src) -> series<float>`
    """
    return _lib.Incr_fn_change_235ff2(ctx=ctx, ).collect(_11987_src=src)

class ChangeLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Change:
    """
How much it moved from the previous bar

`change(series<float> src) -> series<float>`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_change_235ff2(ctx, )
        self.locals = ChangeLocals(self.inner)

    def next(self, src: float) -> Optional[float]:
        return self.inner.next(_11987_src=src)
    



def barssince(ctx: Ctx, condition: List[bool], ) -> List[int]:
    """
Number of bars since something happened

`barssince(series<bool> condition) -> int`
    """
    return _lib.Incr_fn_barssince_2c58cb(ctx=ctx, ).collect(_11989_condition=condition)

class BarssinceLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Barssince:
    """
Number of bars since something happened

`barssince(series<bool> condition) -> int`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_barssince_2c58cb(ctx, )
        self.locals = BarssinceLocals(self.inner)

    def next(self, condition: bool) -> Optional[int]:
        return self.inner.next(_11989_condition=condition)
    



def roc(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Speed of change over given bars

`roc(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_roc_e80701(ctx=ctx, ).collect(_11991_src=src, _11992_length=length)

class RocLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Roc:
    """
Speed of change over given bars

`roc(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_roc_e80701(ctx, )
        self.locals = RocLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_11991_src=src, _11992_length=length)
    



def crossover(ctx: Ctx, source1: List[float], source2: List[float], ) -> List[bool]:
    """
When line1 moves above line2

`crossover(series<float> source1, series<float> source2) -> bool`
    """
    return _lib.Incr_fn_crossover_ecb5d5(ctx=ctx, ).collect(_11994_source1=source1, _11995_source2=source2)

class CrossoverLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Crossover:
    """
When line1 moves above line2

`crossover(series<float> source1, series<float> source2) -> bool`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_crossover_ecb5d5(ctx, )
        self.locals = CrossoverLocals(self.inner)

    def next(self, source1: float, source2: float) -> Optional[bool]:
        return self.inner.next(_11994_source1=source1, _11995_source2=source2)
    



def crossunder(ctx: Ctx, source1: List[float], source2: List[float], ) -> List[bool]:
    """
When line1 drops below line2

`crossunder(series<float> source1, series<float> source2) -> bool`
    """
    return _lib.Incr_fn_crossunder_012839(ctx=ctx, ).collect(_11997_source1=source1, _11998_source2=source2)

class CrossunderLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Crossunder:
    """
When line1 drops below line2

`crossunder(series<float> source1, series<float> source2) -> bool`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_crossunder_012839(ctx, )
        self.locals = CrossunderLocals(self.inner)

    def next(self, source1: float, source2: float) -> Optional[bool]:
        return self.inner.next(_11997_source1=source1, _11998_source2=source2)
    



def cross(ctx: Ctx, source1: List[float], source2: List[float], ) -> List[bool]:
    """
When two lines meet

`cross(series<float> source1, series<float> source2) -> bool`
    """
    return _lib.Incr_fn_cross_1457b8(ctx=ctx, ).collect(_12000_source1=source1, _12001_source2=source2)

class CrossLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Cross:
    """
When two lines meet

`cross(series<float> source1, series<float> source2) -> bool`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_cross_1457b8(ctx, )
        self.locals = CrossLocals(self.inner)

    def next(self, source1: float, source2: float) -> Optional[bool]:
        return self.inner.next(_12000_source1=source1, _12001_source2=source2)
    



def highestbars(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[int]:
    """
Bar index with highest value in period

`highestbars(series<float> src, int length = 14) -> int`
    """
    return _lib.Incr_fn_highestbars_e1623f(ctx=ctx, ).collect(_12003_src=src, _12004_length=length)

class HighestbarsLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Highestbars:
    """
Bar index with highest value in period

`highestbars(series<float> src, int length = 14) -> int`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_highestbars_e1623f(ctx, )
        self.locals = HighestbarsLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[int]:
        return self.inner.next(_12003_src=src, _12004_length=length)
    



def lowestbars(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[int]:
    """
Bar index with lowest value in period

`lowestbars(series<float> src, int length = 14) -> int`
    """
    return _lib.Incr_fn_lowestbars_097e57(ctx=ctx, ).collect(_12006_src=src, _12007_length=length)

class LowestbarsLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Lowestbars:
    """
Bar index with lowest value in period

`lowestbars(series<float> src, int length = 14) -> int`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_lowestbars_097e57(ctx, )
        self.locals = LowestbarsLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[int]:
        return self.inner.next(_12006_src=src, _12007_length=length)
    



def highest(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Highest value in period

`highest(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_highest_3bdd5e(ctx=ctx, ).collect(_12009_src=src, _12010_length=length)

class HighestLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Highest:
    """
Highest value in period

`highest(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_highest_3bdd5e(ctx, )
        self.locals = HighestLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_12009_src=src, _12010_length=length)
    



def lowest(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Lowest value in period

`lowest(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_lowest_d99e1b(ctx=ctx, ).collect(_12012_src=src, _12013_length=length)

class LowestLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Lowest:
    """
Lowest value in period

`lowest(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_lowest_d99e1b(ctx, )
        self.locals = LowestLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_12012_src=src, _12013_length=length)
    



def swma(ctx: Ctx, src: List[float], ) -> List[float]:
    """
Smoothed weighted moving average line

`swma(series<float> src) -> float`
    """
    return _lib.Incr_fn_swma_722a9c(ctx=ctx, ).collect(_12015_src=src)

class SwmaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Swma:
    """
Smoothed weighted moving average line

`swma(series<float> src) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_swma_722a9c(ctx, )
        self.locals = SwmaLocals(self.inner)

    def next(self, src: float) -> Optional[float]:
        return self.inner.next(_12015_src=src)
    



def sma(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Simple moving average (plain average)

`sma(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_sma_3cea78(ctx=ctx, ).collect(_12017_src=src, _12018_length=length)

class SmaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Sma:
    """
Simple moving average (plain average)

`sma(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_sma_3cea78(ctx, )
        self.locals = SmaLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_12017_src=src, _12018_length=length)
    



def ema(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Exponential moving average (reacts faster)

`ema(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_ema_b5abdc(ctx=ctx, ).collect(_12020_src=src, _12021_length=length)

class EmaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Ema:
    """
Exponential moving average (reacts faster)

`ema(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_ema_b5abdc(ctx, )
        self.locals = EmaLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_12020_src=src, _12021_length=length)
    



def rma(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
RMA used inside RSI

`rma(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_rma_5d6fbb(ctx=ctx, ).collect(_12023_src=src, _12024_length=length)

class RmaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Rma:
    """
RMA used inside RSI

`rma(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_rma_5d6fbb(ctx, )
        self.locals = RmaLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_12023_src=src, _12024_length=length)
    



def wma(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Weighted moving average (recent bars matter more)

`wma(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_wma_061f9b(ctx=ctx, ).collect(_12026_src=src, _12027_length=length)

class WmaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Wma:
    """
Weighted moving average (recent bars matter more)

`wma(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_wma_061f9b(ctx, )
        self.locals = WmaLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_12026_src=src, _12027_length=length)
    



def lwma(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Linear weighted moving average

`lwma(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_lwma_f9cf8c(ctx=ctx, ).collect(_12029_src=src, _12030_length=length)

class LwmaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Lwma:
    """
Linear weighted moving average

`lwma(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_lwma_f9cf8c(ctx, )
        self.locals = LwmaLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_12029_src=src, _12030_length=length)
    



def hma(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Hull moving average (smooth and fast)

`hma(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_hma_3a551b(ctx=ctx, ).collect(_12032_src=src, _12033_length=length)

class HmaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Hma:
    """
Hull moving average (smooth and fast)

`hma(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_hma_3a551b(ctx, )
        self.locals = HmaLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_12032_src=src, _12033_length=length)
    



def vwma(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Volume‑weighted moving average

`vwma(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_vwma_cff731(ctx=ctx, ).collect(_12035_src=src, _12036_length=length)

class VwmaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Vwma:
    """
Volume‑weighted moving average

`vwma(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_vwma_cff731(ctx, )
        self.locals = VwmaLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_12035_src=src, _12036_length=length)
    



def dev(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Standard deviation (how much it varies)

`dev(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_dev_8a7813(ctx=ctx, ).collect(_12038_src=src, _12039_length=length)

class DevLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Dev:
    """
Standard deviation (how much it varies)

`dev(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_dev_8a7813(ctx, )
        self.locals = DevLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_12038_src=src, _12039_length=length)
    



def tr(ctx: Ctx, handle_na: Optional[bool] = None, ) -> List[float]:
    """
True range (how much price moved in bar)

`tr(bool handle_na = true) -> series<float>`
    """
    return _lib.Incr_fn_tr_2b51fb(ctx=ctx, ).collect(_12041_handle_na=handle_na)

class TrLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Tr:
    """
True range (how much price moved in bar)

`tr(bool handle_na = true) -> series<float>`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_tr_2b51fb(ctx, )
        self.locals = TrLocals(self.inner)

    def next(self, handle_na: Optional[bool] = None) -> Optional[float]:
        return self.inner.next(_12041_handle_na=handle_na)
    



def atr(ctx: Ctx, length: Optional[int] = None, ) -> List[float]:
    """
Average true range (typical move size)

`atr(int length = 14) -> float`
    """
    return _lib.Incr_fn_atr_01291b(ctx=ctx, ).collect(_12043_length=length)

class AtrLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Atr:
    """
Average true range (typical move size)

`atr(int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_atr_01291b(ctx, )
        self.locals = AtrLocals(self.inner)

    def next(self, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_12043_length=length)
    



def rsi(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Relative Strength Index (momentum strength)

`rsi(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_rsi_eda785(ctx=ctx, ).collect(_12045_src=src, _12046_length=length)

class RsiLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Rsi:
    """
Relative Strength Index (momentum strength)

`rsi(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_rsi_eda785(ctx, )
        self.locals = RsiLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_12045_src=src, _12046_length=length)
    



def cci(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Commodity Channel Index (price vs average)

`cci(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_cci_93a869(ctx=ctx, ).collect(_12048_src=src, _12049_length=length)

class CciLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Cci:
    """
Commodity Channel Index (price vs average)

`cci(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_cci_93a869(ctx, )
        self.locals = CciLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_12048_src=src, _12049_length=length)
    



def stdev(ctx: Ctx, src: List[float], length: int, biased: Optional[bool] = None, ) -> List[float]:
    """
Standard deviation over period

`stdev(series<float> src, int length, bool biased = true) -> float`
    """
    return _lib.Incr_fn_stdev_3cce2f(ctx=ctx, ).collect(_12051_src=src, _12052_length=length, _12053_biased=biased)

class StdevLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Stdev:
    """
Standard deviation over period

`stdev(series<float> src, int length, bool biased = true) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_stdev_3cce2f(ctx, )
        self.locals = StdevLocals(self.inner)

    def next(self, src: float, length: int, biased: Optional[bool] = None) -> Optional[float]:
        return self.inner.next(_12051_src=src, _12052_length=length, _12053_biased=biased)
    



def aroon(ctx: Ctx, length: Optional[int] = None, ) -> Tuple[float, float]:
    """
Aroon indicator (time since highs/lows)

`aroon(int length = 14) -> [float, float]`
    """
    return _lib.Incr_fn_aroon_3ae133(ctx=ctx, ).collect(_12055_length=length)

class AroonLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Aroon:
    """
Aroon indicator (time since highs/lows)

`aroon(int length = 14) -> [float, float]`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_aroon_3ae133(ctx, )
        self.locals = AroonLocals(self.inner)

    def next(self, length: Optional[int] = None) -> Optional[Tuple[float, float]]:
        return self.inner.next(_12055_length=length)
    



def supertrend(ctx: Ctx, src: List[float], factor: float, atr_period: int, ) -> Tuple[float, int]:
    """
Supertrend line for direction

`supertrend(series<float> src, float factor, int atr_period) -> [float, int]`
    """
    return _lib.Incr_fn_supertrend_09c2f0(ctx=ctx, ).collect(_12057_src=src, _12058_factor=factor, _12059_atr_period=atr_period)

class SupertrendLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Supertrend:
    """
Supertrend line for direction

`supertrend(series<float> src, float factor, int atr_period) -> [float, int]`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_supertrend_09c2f0(ctx, )
        self.locals = SupertrendLocals(self.inner)

    def next(self, src: float, factor: float, atr_period: int) -> Optional[Tuple[float, int]]:
        return self.inner.next(_12057_src=src, _12058_factor=factor, _12059_atr_period=atr_period)
    



def awesome_oscillator(ctx: Ctx, src: List[float], slow_length: Optional[int] = None, fast_length: Optional[int] = None, ) -> List[float]:
    """
Awesome Oscillator (momentum)

`awesome_oscillator(series<float> src, int slow_length = 5, int fast_length = 34) -> float`
    """
    return _lib.Incr_fn_awesome_oscillator_3e9e68(ctx=ctx, ).collect(_12061_src=src, _12062_slow_length=slow_length, _12063_fast_length=fast_length)

class AwesomeOscillatorLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class AwesomeOscillator:
    """
Awesome Oscillator (momentum)

`awesome_oscillator(series<float> src, int slow_length = 5, int fast_length = 34) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_awesome_oscillator_3e9e68(ctx, )
        self.locals = AwesomeOscillatorLocals(self.inner)

    def next(self, src: float, slow_length: Optional[int] = None, fast_length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_12061_src=src, _12062_slow_length=slow_length, _12063_fast_length=fast_length)
    



def balance_of_power(ctx: Ctx, ) -> List[float]:
    """
Balance of power between buyers and sellers

`balance_of_power() -> float`
    """
    return _lib.Incr_fn_balance_of_power_eabb74(ctx=ctx, ).collect()

class BalanceOfPowerLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class BalanceOfPower:
    """
Balance of power between buyers and sellers

`balance_of_power() -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_balance_of_power_eabb74(ctx, )
        self.locals = BalanceOfPowerLocals(self.inner)

    def next(self, ) -> Optional[float]:
        return self.inner.next()
    



def bollinger_bands_pct_b(ctx: Ctx, src: List[float], length: Optional[int] = None, mult: Optional[float] = None, ) -> List[float]:
    """
%B – where price is inside Bollinger Bands (0‑1)

`bollinger_bands_pct_b(series<float> src, int length = 20, float mult = 2.0) -> float`
    """
    return _lib.Incr_fn_bollinger_bands_pct_b_151264(ctx=ctx, ).collect(_12068_src=src, _12069_length=length, _12070_mult=mult)

class BollingerBandsPctBLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class BollingerBandsPctB:
    """
%B – where price is inside Bollinger Bands (0‑1)

`bollinger_bands_pct_b(series<float> src, int length = 20, float mult = 2.0) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_bollinger_bands_pct_b_151264(ctx, )
        self.locals = BollingerBandsPctBLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None, mult: Optional[float] = None) -> Optional[float]:
        return self.inner.next(_12068_src=src, _12069_length=length, _12070_mult=mult)
    



def bollinger_bands_width(ctx: Ctx, src: List[float], length: Optional[int] = None, mult: Optional[float] = None, ) -> List[float]:
    """
Band width – how wide Bollinger Bands are

`bollinger_bands_width(series<float> src, int length = 20, float mult = 2.0) -> float`
    """
    return _lib.Incr_fn_bollinger_bands_width_2147be(ctx=ctx, ).collect(_12077_src=src, _12078_length=length, _12079_mult=mult)

class BollingerBandsWidthLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class BollingerBandsWidth:
    """
Band width – how wide Bollinger Bands are

`bollinger_bands_width(series<float> src, int length = 20, float mult = 2.0) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_bollinger_bands_width_2147be(ctx, )
        self.locals = BollingerBandsWidthLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None, mult: Optional[float] = None) -> Optional[float]:
        return self.inner.next(_12077_src=src, _12078_length=length, _12079_mult=mult)
    



def bollinger_bands(ctx: Ctx, src: List[float], length: Optional[int] = None, mult: Optional[float] = None, ) -> Tuple[float, float]:
    """
Gives upper and lower Bollinger Bands

`bollinger_bands(series<float> src, int length = 20, float mult = 2.0) -> [float, float]`
    """
    return _lib.Incr_fn_bollinger_bands_004dd9(ctx=ctx, ).collect(_12086_src=src, _12087_length=length, _12088_mult=mult)

class BollingerBandsLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class BollingerBands:
    """
Gives upper and lower Bollinger Bands

`bollinger_bands(series<float> src, int length = 20, float mult = 2.0) -> [float, float]`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_bollinger_bands_004dd9(ctx, )
        self.locals = BollingerBandsLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None, mult: Optional[float] = None) -> Optional[Tuple[float, float]]:
        return self.inner.next(_12086_src=src, _12087_length=length, _12088_mult=mult)
    



def chaikin_money_flow(ctx: Ctx, length: Optional[int] = None, ) -> List[float]:
    """
Chaikin Money Flow – volume weighted flow

`chaikin_money_flow(int length = 20) -> float`
    """
    return _lib.Incr_fn_chaikin_money_flow_40ae1b(ctx=ctx, ).collect(_12094_length=length)

class ChaikinMoneyFlowLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def cumVol(self) -> float:
        return self.__inner._12095_cumVol()
  
      

class ChaikinMoneyFlow:
    """
Chaikin Money Flow – volume weighted flow

`chaikin_money_flow(int length = 20) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_chaikin_money_flow_40ae1b(ctx, )
        self.locals = ChaikinMoneyFlowLocals(self.inner)

    def next(self, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_12094_length=length)
    



def chande_kroll_stop(ctx: Ctx, atr_length: Optional[int] = None, atr_coeff: Optional[float] = None, stop_length: Optional[int] = None, ) -> Tuple[float, float]:
    """
Chande‑Kroll stop lines

`chande_kroll_stop(int atr_length = 10, float atr_coeff = 1.0, int stop_length = 9) -> [float, float]`
    """
    return _lib.Incr_fn_chande_kroll_stop_d1f11e(ctx=ctx, ).collect(_12099_atr_length=atr_length, _12100_atr_coeff=atr_coeff, _12101_stop_length=stop_length)

class ChandeKrollStopLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class ChandeKrollStop:
    """
Chande‑Kroll stop lines

`chande_kroll_stop(int atr_length = 10, float atr_coeff = 1.0, int stop_length = 9) -> [float, float]`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_chande_kroll_stop_d1f11e(ctx, )
        self.locals = ChandeKrollStopLocals(self.inner)

    def next(self, atr_length: Optional[int] = None, atr_coeff: Optional[float] = None, stop_length: Optional[int] = None) -> Optional[Tuple[float, float]]:
        return self.inner.next(_12099_atr_length=atr_length, _12100_atr_coeff=atr_coeff, _12101_stop_length=stop_length)
    



def choppiness_index(ctx: Ctx, length: Optional[int] = None, ) -> List[float]:
    """
Choppiness Index – tells if market is sideways or trending

`choppiness_index(int length = 14) -> float`
    """
    return _lib.Incr_fn_choppiness_index_de13d0(ctx=ctx, ).collect(_12110_length=length)

class ChoppinessIndexLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class ChoppinessIndex:
    """
Choppiness Index – tells if market is sideways or trending

`choppiness_index(int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_choppiness_index_de13d0(ctx, )
        self.locals = ChoppinessIndexLocals(self.inner)

    def next(self, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_12110_length=length)
    



def connors_rsi(ctx: Ctx, src: List[float], rsi_length: Optional[int] = None, up_down_length: Optional[int] = None, roc_length: Optional[int] = None, ) -> List[float]:
    """
`connors_rsi(series<float> src, int rsi_length = 3, int up_down_length = 2, int roc_length = 100) -> float`
    """
    return _lib.Incr_fn_connors_rsi_1e1ad2(ctx=ctx, ).collect(_12117_src=src, _12118_rsi_length=rsi_length, _12119_up_down_length=up_down_length, _12120_roc_length=roc_length)

class ConnorsRsiLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class ConnorsRsi:
    """
`connors_rsi(series<float> src, int rsi_length = 3, int up_down_length = 2, int roc_length = 100) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_connors_rsi_1e1ad2(ctx, )
        self.locals = ConnorsRsiLocals(self.inner)

    def next(self, src: float, rsi_length: Optional[int] = None, up_down_length: Optional[int] = None, roc_length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_12117_src=src, _12118_rsi_length=rsi_length, _12119_up_down_length=up_down_length, _12120_roc_length=roc_length)
    



def coppock_curve(ctx: Ctx, src: List[float], wma_length: Optional[int] = None, long_roc_length: Optional[int] = None, short_roc_length: Optional[int] = None, ) -> List[float]:
    """
Coppock Curve – long‑term momentum

`coppock_curve(series<float> src, int wma_length = 10, int long_roc_length = 14, int short_roc_length = 11) -> float`
    """
    return _lib.Incr_fn_coppock_curve_db643d(ctx=ctx, ).collect(_12126_src=src, _12127_wma_length=wma_length, _12128_long_roc_length=long_roc_length, _12129_short_roc_length=short_roc_length)

class CoppockCurveLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class CoppockCurve:
    """
Coppock Curve – long‑term momentum

`coppock_curve(series<float> src, int wma_length = 10, int long_roc_length = 14, int short_roc_length = 11) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_coppock_curve_db643d(ctx, )
        self.locals = CoppockCurveLocals(self.inner)

    def next(self, src: float, wma_length: Optional[int] = None, long_roc_length: Optional[int] = None, short_roc_length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_12126_src=src, _12127_wma_length=wma_length, _12128_long_roc_length=long_roc_length, _12129_short_roc_length=short_roc_length)
    



def donchian_channel(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> Tuple[float, float, float]:
    """
Donchian Channel highs/lows

`donchian_channel(series<float> src, int length = 20) -> [float, float, float]`
    """
    return _lib.Incr_fn_donchian_channel_313036(ctx=ctx, ).collect(_12131_src=src, _12132_length=length)

class DonchianChannelLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class DonchianChannel:
    """
Donchian Channel highs/lows

`donchian_channel(series<float> src, int length = 20) -> [float, float, float]`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_donchian_channel_313036(ctx, )
        self.locals = DonchianChannelLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[Tuple[float, float, float]]:
        return self.inner.next(_12131_src=src, _12132_length=length)
    



def macd(ctx: Ctx, src: List[float], short_length: Optional[int] = None, long_length: Optional[int] = None, ) -> List[float]:
    """
MACD line (fast trend vs slow)

`macd(series<float> src, int short_length = 12, int long_length = 26) -> float`
    """
    return _lib.Incr_fn_macd_383d22(ctx=ctx, ).collect(_12137_src=src, _12138_short_length=short_length, _12139_long_length=long_length)

class MacdLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Macd:
    """
MACD line (fast trend vs slow)

`macd(series<float> src, int short_length = 12, int long_length = 26) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_macd_383d22(ctx, )
        self.locals = MacdLocals(self.inner)

    def next(self, src: float, short_length: Optional[int] = None, long_length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_12137_src=src, _12138_short_length=short_length, _12139_long_length=long_length)
    



def price_oscillator(ctx: Ctx, src: List[float], short_length: Optional[int] = None, long_length: Optional[int] = None, ) -> List[float]:
    """
Price oscillator in percent

`price_oscillator(series<float> src, int short_length = 12, int long_length = 26) -> float`
    """
    return _lib.Incr_fn_price_oscillator_7f5886(ctx=ctx, ).collect(_12142_src=src, _12143_short_length=short_length, _12144_long_length=long_length)

class PriceOscillatorLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class PriceOscillator:
    """
Price oscillator in percent

`price_oscillator(series<float> src, int short_length = 12, int long_length = 26) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_price_oscillator_7f5886(ctx, )
        self.locals = PriceOscillatorLocals(self.inner)

    def next(self, src: float, short_length: Optional[int] = None, long_length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_12142_src=src, _12143_short_length=short_length, _12144_long_length=long_length)
    



def relative_vigor_index(ctx: Ctx, length: Optional[int] = None, ) -> List[float]:
    """
Relative Vigor Index – strength of close vs range

`relative_vigor_index(int length = 14) -> float`
    """
    return _lib.Incr_fn_relative_vigor_index_2e5d9e(ctx=ctx, ).collect(_12149_length=length)

class RelativeVigorIndexLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class RelativeVigorIndex:
    """
Relative Vigor Index – strength of close vs range

`relative_vigor_index(int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_relative_vigor_index_2e5d9e(ctx, )
        self.locals = RelativeVigorIndexLocals(self.inner)

    def next(self, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_12149_length=length)
    



def relative_volatility_index(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Relative Volatility Index – like RSI but for volatility

`relative_volatility_index(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_relative_volatility_index_f00e2d(ctx=ctx, ).collect(_12151_src=src, _12152_length=length)

class RelativeVolatilityIndexLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class RelativeVolatilityIndex:
    """
Relative Volatility Index – like RSI but for volatility

`relative_volatility_index(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_relative_volatility_index_f00e2d(ctx, )
        self.locals = RelativeVolatilityIndexLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_12151_src=src, _12152_length=length)
    



def stochastic_rsi(ctx: Ctx, src: List[float], stoch_length: Optional[int] = None, rsi_length: Optional[int] = None, k: Optional[int] = None, d: Optional[int] = None, ) -> Tuple[float, float]:
    """
Stochastic RSI

`stochastic_rsi(series<float> src, int stoch_length = 14, int rsi_length = 14, int k = 3, int d = 3) -> [float, float]`
    """
    return _lib.Incr_fn_stochastic_rsi_6f5187(ctx=ctx, ).collect(_12158_src=src, _12159_stoch_length=stoch_length, _12160_rsi_length=rsi_length, _12161_k=k, _12162_d=d)

class StochasticRsiLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class StochasticRsi:
    """
Stochastic RSI

`stochastic_rsi(series<float> src, int stoch_length = 14, int rsi_length = 14, int k = 3, int d = 3) -> [float, float]`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_stochastic_rsi_6f5187(ctx, )
        self.locals = StochasticRsiLocals(self.inner)

    def next(self, src: float, stoch_length: Optional[int] = None, rsi_length: Optional[int] = None, k: Optional[int] = None, d: Optional[int] = None) -> Optional[Tuple[float, float]]:
        return self.inner.next(_12158_src=src, _12159_stoch_length=stoch_length, _12160_rsi_length=rsi_length, _12161_k=k, _12162_d=d)
    



def ultimate_oscillator(ctx: Ctx, fast_length: Optional[int] = None, medium_length: Optional[int] = None, slow_length: Optional[int] = None, ) -> List[float]:
    """
Ultimate Oscillator – combines 3 speeds

`ultimate_oscillator(int fast_length = 7, int medium_length = 14, int slow_length = 28) -> float`
    """
    return _lib.Incr_fn_ultimate_oscillator_625268(ctx=ctx, ).collect(_12171_fast_length=fast_length, _12172_medium_length=medium_length, _12173_slow_length=slow_length)

class UltimateOscillatorLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class UltimateOscillator:
    """
Ultimate Oscillator – combines 3 speeds

`ultimate_oscillator(int fast_length = 7, int medium_length = 14, int slow_length = 28) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_ultimate_oscillator_625268(ctx, )
        self.locals = UltimateOscillatorLocals(self.inner)

    def next(self, fast_length: Optional[int] = None, medium_length: Optional[int] = None, slow_length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_12171_fast_length=fast_length, _12172_medium_length=medium_length, _12173_slow_length=slow_length)
    



def volume_oscillator(ctx: Ctx, short_length: Optional[int] = None, long_length: Optional[int] = None, ) -> List[float]:
    """
Volume Oscillator – volume momentum

`volume_oscillator(int short_length = 5, int long_length = 10) -> float`
    """
    return _lib.Incr_fn_volume_oscillator_ecf803(ctx=ctx, ).collect(_12183_short_length=short_length, _12184_long_length=long_length)

class VolumeOscillatorLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class VolumeOscillator:
    """
Volume Oscillator – volume momentum

`volume_oscillator(int short_length = 5, int long_length = 10) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_volume_oscillator_ecf803(ctx, )
        self.locals = VolumeOscillatorLocals(self.inner)

    def next(self, short_length: Optional[int] = None, long_length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_12183_short_length=short_length, _12184_long_length=long_length)
    



def vortex_indicator(ctx: Ctx, length: Optional[int] = None, ) -> Tuple[float, float]:
    """
Vortex Indicator – shows trend direction

`vortex_indicator(int length = 14) -> [float, float]`
    """
    return _lib.Incr_fn_vortex_indicator_2e67e9(ctx=ctx, ).collect(_12189_length=length)

class VortexIndicatorLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class VortexIndicator:
    """
Vortex Indicator – shows trend direction

`vortex_indicator(int length = 14) -> [float, float]`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_vortex_indicator_2e67e9(ctx, )
        self.locals = VortexIndicatorLocals(self.inner)

    def next(self, length: Optional[int] = None) -> Optional[Tuple[float, float]]:
        return self.inner.next(_12189_length=length)
    



def williams_pct_r(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Williams %R – overbought/oversold

`williams_pct_r(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_williams_pct_r_5998c2(ctx=ctx, ).collect(_12196_src=src, _12197_length=length)

class WilliamsPctRLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class WilliamsPctR:
    """
Williams %R – overbought/oversold

`williams_pct_r(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_williams_pct_r_5998c2(ctx, )
        self.locals = WilliamsPctRLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_12196_src=src, _12197_length=length)
    



def advance_decline_ratio(ctx: Ctx, length: Optional[int] = None, ) -> List[float]:
    """
Advance/Decline Ratio (Bars)

`advance_decline_ratio(int length = 9) -> float`
    """
    return _lib.Incr_fn_advance_decline_ratio_bcafc0(ctx=ctx, ).collect(_12202_length=length)

class AdvanceDeclineRatioLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class AdvanceDeclineRatio:
    """
Advance/Decline Ratio (Bars)

`advance_decline_ratio(int length = 9) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_advance_decline_ratio_bcafc0(ctx, )
        self.locals = AdvanceDeclineRatioLocals(self.inner)

    def next(self, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_12202_length=length)
    



def detrended_price_oscillator(ctx: Ctx, length: Optional[int] = None, centered: Optional[bool] = None, ) -> List[float]:
    """
Detrended Price Oscillator (DPO)

`detrended_price_oscillator(int length = 21, bool centered = false) -> series<float>`
    """
    return _lib.Incr_fn_detrended_price_oscillator_04afac(ctx=ctx, ).collect(_12208_length=length, _12209_centered=centered)

class DetrendedPriceOscillatorLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class DetrendedPriceOscillator:
    """
Detrended Price Oscillator (DPO)

`detrended_price_oscillator(int length = 21, bool centered = false) -> series<float>`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_detrended_price_oscillator_04afac(ctx, )
        self.locals = DetrendedPriceOscillatorLocals(self.inner)

    def next(self, length: Optional[int] = None, centered: Optional[bool] = None) -> Optional[float]:
        return self.inner.next(_12208_length=length, _12209_centered=centered)
    



def bull_bear_power(ctx: Ctx, length: Optional[int] = None, ) -> List[float]:
    """
Bull Bear Power (BBP)

`bull_bear_power(int length = 13) -> series<float>`
    """
    return _lib.Incr_fn_bull_bear_power_60d923(ctx=ctx, ).collect(_12214_length=length)

class BullBearPowerLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class BullBearPower:
    """
Bull Bear Power (BBP)

`bull_bear_power(int length = 13) -> series<float>`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_bull_bear_power_60d923(ctx, )
        self.locals = BullBearPowerLocals(self.inner)

    def next(self, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_12214_length=length)
    



def absolute_price_oscillator(ctx: Ctx, src: List[float], fast_length: Optional[int] = None, slow_length: Optional[int] = None, ) -> List[float]:
    """
Absolute Price Oscillator (APO)

`absolute_price_oscillator(series<float> src, int fast_length = 12, int slow_length = 26) -> float`
    """
    return _lib.Incr_fn_absolute_price_oscillator_3791bf(ctx=ctx, ).collect(_12220_src=src, _12221_fast_length=fast_length, _12222_slow_length=slow_length)

class AbsolutePriceOscillatorLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class AbsolutePriceOscillator:
    """
Absolute Price Oscillator (APO)

`absolute_price_oscillator(series<float> src, int fast_length = 12, int slow_length = 26) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_absolute_price_oscillator_3791bf(ctx, )
        self.locals = AbsolutePriceOscillatorLocals(self.inner)

    def next(self, src: float, fast_length: Optional[int] = None, slow_length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_12220_src=src, _12221_fast_length=fast_length, _12222_slow_length=slow_length)
    



def know_sure_thing(ctx: Ctx, src: List[float], roc_length1: Optional[int] = None, roc_length2: Optional[int] = None, roc_length3: Optional[int] = None, roc_length4: Optional[int] = None, sma_length1: Optional[int] = None, sma_length2: Optional[int] = None, sma_length3: Optional[int] = None, sma_length4: Optional[int] = None, sig_length: Optional[int] = None, ) -> Tuple[float, float]:
    """
Know Sure Thing (KST)

`know_sure_thing(series<float> src, int roc_length1 = 10, int roc_length2 = 15, int roc_length3 = 20, int roc_length4 = 30, int sma_length1 = 10, int sma_length2 = 10, int sma_length3 = 10, int sma_length4 = 15, int sig_length = 9) -> [float, float]`
    """
    return _lib.Incr_fn_know_sure_thing_557f99(ctx=ctx, ).collect(_12226_src=src, _12227_roc_length1=roc_length1, _12228_roc_length2=roc_length2, _12229_roc_length3=roc_length3, _12230_roc_length4=roc_length4, _12231_sma_length1=sma_length1, _12232_sma_length2=sma_length2, _12233_sma_length3=sma_length3, _12234_sma_length4=sma_length4, _12235_sig_length=sig_length)

class KnowSureThingLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class KnowSureThing:
    """
Know Sure Thing (KST)

`know_sure_thing(series<float> src, int roc_length1 = 10, int roc_length2 = 15, int roc_length3 = 20, int roc_length4 = 30, int sma_length1 = 10, int sma_length2 = 10, int sma_length3 = 10, int sma_length4 = 15, int sig_length = 9) -> [float, float]`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_know_sure_thing_557f99(ctx, )
        self.locals = KnowSureThingLocals(self.inner)

    def next(self, src: float, roc_length1: Optional[int] = None, roc_length2: Optional[int] = None, roc_length3: Optional[int] = None, roc_length4: Optional[int] = None, sma_length1: Optional[int] = None, sma_length2: Optional[int] = None, sma_length3: Optional[int] = None, sma_length4: Optional[int] = None, sig_length: Optional[int] = None) -> Optional[Tuple[float, float]]:
        return self.inner.next(_12226_src=src, _12227_roc_length1=roc_length1, _12228_roc_length2=roc_length2, _12229_roc_length3=roc_length3, _12230_roc_length4=roc_length4, _12231_sma_length1=sma_length1, _12232_sma_length2=sma_length2, _12233_sma_length3=sma_length3, _12234_sma_length4=sma_length4, _12235_sig_length=sig_length)
    



def momentum(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Momentum (MOM)

`momentum(series<float> src, int length = 10) -> series<float>`
    """
    return _lib.Incr_fn_momentum_256b0a(ctx=ctx, ).collect(_12243_src=src, _12244_length=length)

class MomentumLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Momentum:
    """
Momentum (MOM)

`momentum(series<float> src, int length = 10) -> series<float>`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_momentum_256b0a(ctx, )
        self.locals = MomentumLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_12243_src=src, _12244_length=length)
    



def trix(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Trix

`trix(series<float> src, int length = 18) -> series<float>`
    """
    return _lib.Incr_fn_trix_3a18a1(ctx=ctx, ).collect(_12246_src=src, _12247_length=length)

class TrixLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Trix:
    """
Trix

`trix(series<float> src, int length = 18) -> series<float>`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_trix_3a18a1(ctx, )
        self.locals = TrixLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_12246_src=src, _12247_length=length)
    



def true_strength_index(ctx: Ctx, src: List[float], long_length: Optional[int] = None, short_length: Optional[int] = None, ) -> List[float]:
    """
True Strength Index (TSI)

`true_strength_index(series<float> src, int long_length = 25, int short_length = 13) -> float`
    """
    return _lib.Incr_fn_true_strength_index_623031(ctx=ctx, ).collect(_12249_src=src, _12250_long_length=long_length, _12251_short_length=short_length)

class TrueStrengthIndexLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class TrueStrengthIndex:
    """
True Strength Index (TSI)

`true_strength_index(series<float> src, int long_length = 25, int short_length = 13) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_true_strength_index_623031(ctx, )
        self.locals = TrueStrengthIndexLocals(self.inner)

    def next(self, src: float, long_length: Optional[int] = None, short_length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_12249_src=src, _12250_long_length=long_length, _12251_short_length=short_length)
    



def dema(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Double Exponential Moving Average (DEMA)

`dema(series<float> src, int length = 9) -> float`
    """
    return _lib.Incr_fn_dema_db6ad8(ctx=ctx, ).collect(_12257_src=src, _12258_length=length)

class DemaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Dema:
    """
Double Exponential Moving Average (DEMA)

`dema(series<float> src, int length = 9) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_dema_db6ad8(ctx, )
        self.locals = DemaLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_12257_src=src, _12258_length=length)
    



def fwma(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Fibonacci Weighted Moving Average (FWMA)

`fwma(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_fwma_ba8e5a(ctx=ctx, ).collect(_12267_src=src, _12268_length=length)

class FwmaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Fwma:
    """
Fibonacci Weighted Moving Average (FWMA)

`fwma(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_fwma_ba8e5a(ctx, )
        self.locals = FwmaLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_12267_src=src, _12268_length=length)
    



def money_flow_index(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Money Flow Index (MFI)

`money_flow_index(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_money_flow_index_b4e12a(ctx=ctx, ).collect(_12274_src=src, _12275_length=length)

class MoneyFlowIndexLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class MoneyFlowIndex:
    """
Money Flow Index (MFI)

`money_flow_index(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_money_flow_index_b4e12a(ctx, )
        self.locals = MoneyFlowIndexLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_12274_src=src, _12275_length=length)
    



def ease_of_movement(ctx: Ctx, length: Optional[int] = None, divisor: Optional[int] = None, ) -> List[float]:
    """
Ease of Movement (EOM)

`ease_of_movement(int length = 14, int divisor = 10000) -> float`
    """
    return _lib.Incr_fn_ease_of_movement_65c4ec(ctx=ctx, ).collect(_12277_length=length, _12278_divisor=divisor)

class EaseOfMovementLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class EaseOfMovement:
    """
Ease of Movement (EOM)

`ease_of_movement(int length = 14, int divisor = 10000) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_ease_of_movement_65c4ec(ctx, )
        self.locals = EaseOfMovementLocals(self.inner)

    def next(self, length: Optional[int] = None, divisor: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_12277_length=length, _12278_divisor=divisor)
    



def elder_force_index(ctx: Ctx, length: Optional[int] = None, ) -> List[float]:
    """
Elder Force Index (EFI)

`elder_force_index(int length = 13) -> float`
    """
    return _lib.Incr_fn_elder_force_index_5d4cb8(ctx=ctx, ).collect(_12280_length=length)

class ElderForceIndexLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class ElderForceIndex:
    """
Elder Force Index (EFI)

`elder_force_index(int length = 13) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_elder_force_index_5d4cb8(ctx, )
        self.locals = ElderForceIndexLocals(self.inner)

    def next(self, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_12280_length=length)
    



def tema(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Tripple Exponential Moving Average (TEMA)

`tema(series<float> src, int length = 9) -> float`
    """
    return _lib.Incr_fn_tema_ab96ac(ctx=ctx, ).collect(_12282_src=src, _12283_length=length)

class TemaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Tema:
    """
Tripple Exponential Moving Average (TEMA)

`tema(series<float> src, int length = 9) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_tema_ab96ac(ctx, )
        self.locals = TemaLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_12282_src=src, _12283_length=length)
    


class MainAlert(TypedDict):
    time: datetime
    bar_index: int
    title: Optional[str]
    message: Optional[str]

class MainResultLocals(TypedDict):

    pass

class MainResult(TypedDict):
    alerts: List[MainAlert]
    locals: MainResultLocals


def main(ctx: Ctx, ) -> MainResult:
    """
`main() -> void`
    """
    return _lib.Incr_fn_main_8b2430(ctx=ctx, ).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_8b2430(ctx, )
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          