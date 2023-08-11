# -*- coding: utf-8 -*-
"""
Created on Sun Apr 2023/04/02 17:44:54
Revised date : 2023/07/28 08:22
@author: IKU-Trader
"""

import numpy as np
import polars as pl
from polars import DataFrame
from datetime import datetime, timedelta
from const import Const
from time_utils import TimeUtils


class Converter:
    @staticmethod
    def candles2tohlc(candles):
        is_volume = (len(candles[0]) > 5)
        times = []
        op = []
        hi = []
        lo = []
        cl = []
        vol = []
        for candle in candles:
            times.append(candle[0])
            op.append(candle[1])
            hi.append(candle[2])
            lo.append(candle[3])
            cl.append(candle[4])
            if is_volume:
                vol.append(candle[5])
        if is_volume:
            return [times, op, hi, lo, cl, vol]
        else:
            return [times, op, hi, lo, cl]
    
    @staticmethod
    def df2Candles(df: DataFrame):
        df2 = df[[Const.OPEN, Const.HIGH, Const.LOW, Const.CLOSE]]
        return df2.to_list()
    
    @staticmethod
    def df2dic(df: DataFrame) ->dict:
        t = df[Const.TIME].to_list()
        o = df[Const.OPEN].to_numpy()
        h = df[Const.HIGH].to_numpy()
        l = df[Const.LOW].to_numpy()
        c = df[Const.CLOSE].to_numpy()
        dic = {Const.TIME: t, Const.OPEN: o, Const.HIGH: h, Const.LOW: l, Const.CLOSE: c}
        if Const.VOLUME in df.columns:
            v = df[Const.VOLUME].to_numpy()
            dic[Const.VOUME] = v
        return dic
    
    @staticmethod
    def df2tohlcv(df: DataFrame) ->dict:
        t = df[Const.TIME].to_list()
        o = df[Const.OPEN].to_numpy()
        h = df[Const.HIGH].to_numpy()
        l = df[Const.LOW].to_numpy()
        c = df[Const.CLOSE].to_numpy()
        tohlcv = [t,  o, h, l, c]
        if Const.VOLUME in df.columns:
            v = df[Const.VOLUME].to_numpy()
            tohlcv.append(v)
        return tohlcv
    
    @staticmethod
    def tohlcv2Candles(tohlcv):
        op = tohlcv[1]
        hi = tohlcv[2]
        lo = tohlcv[3]
        cl = tohlcv[4]
        candles = []
        for o, h, l, c in zip(op, hi, lo, cl):
            candles.append([o, h, l, c])
        return candles
    
    @staticmethod
    def tohlcvArrays2dic(tohlcv: list, is_last_invalid):
        dic = {}
        if is_last_invalid:
            dic[Const.TIME] = tohlcv[0][:-1]
            dic[Const.OPEN] = tohlcv[1][:-1]
            dic[Const.HIGH] = tohlcv[2][:-1]
            dic[Const.LOW] = tohlcv[3][:-1]
            dic[Const.CLOSE] = tohlcv[4][:-1]
            if len(tohlcv) > 5:
                dic[Const.VOLUME] = tohlcv[5][:-1]
            candle = [tohlcv[0][-1], tohlcv[1][-1], tohlcv[2][-1],tohlcv[3][-1], tohlcv[4][-1]]
            if len(tohlcv) > 5:
                candle.append(tohlcv[5][-1])
            return dic, candle
        else:
            dic = Converter.arrays2Dic(tohlcv)
            return dic, []

    @staticmethod        
    def dic2Arrays(dic: dict):
        arrays = [dic[Const.TIME], dic[Const.OPEN], dic[Const.HIGH], dic[Const.LOW], dic[Const.CLOSE]]
        if Const.VOLUME in dic.keys():
            arrays.append(dic[Const.VOLUME])
        return arrays 
    
    @staticmethod        
    def arrays2Dic(tohlcvArrays: list):
        dic = {}
        dic[Const.TIME] = tohlcvArrays[0]
        dic[Const.OPEN] = tohlcvArrays[1]
        dic[Const.HIGH] = tohlcvArrays[2]
        dic[Const.LOW] = tohlcvArrays[3]
        dic[Const.CLOSE] = tohlcvArrays[4]
        if len(tohlcvArrays) > 5:
            dic[Const.VOLUME] = tohlcvArrays[5]
        return dic    
    
    @staticmethod
    def arrays2Candles(tohlcvArrays: list):
        out = []
        n = len(tohlcvArrays[0])
        for i in range(n):
            d = [array[i] for array in tohlcvArrays]
            out.append(d)
        return out

    @staticmethod
    def candles2dic(candles: list):
        n = len(candles)
        m = len(candles[0])
        arrays = []
        for i in range(m):
            array = [candles[j][i] for j in range(n)]
            arrays.append(array)
            
        dic = {Const.TIME: arrays[0], Const.OPEN: arrays[1], Const.HIGH: arrays[2], Const.LOW: arrays[3], Const.CLOSE: arrays[4]}
        if m > 5:
            dic[Const.VOLUME] = arrays[5]
        return dic

    @staticmethod
    def dic2Candles(dic: dict):
        arrays = [dic[Const.TIME], dic[Const.OPEN], dic[Const.HIGH], dic[Const.LOW], dic[Const.CLOSE]]
        try:
            arrays.append(dic[Const.VOLUME])
        except:
            pass
        out = []
        for i in range(len(arrays[0])):
            d = [] 
            for array in arrays:
                d.append(array[i])
            out.append(d)
        return out
    
    # tohlcv: tohlcv arrays
    @staticmethod
    def resample(dic: dict, interval: int, unit: Const.TimeUnit):        
        time = dic[Const.TIME]
        n = len(time)
        op = dic[Const.OPEN]
        hi = dic[Const.HIGH]
        lo = dic[Const.LOW]
        cl = dic[Const.CLOSE]
        if Const.VOLUME in dic.keys():
            vo = dic[Const.VOLUME]
            is_volume = True
        else:
            is_volume = False
        tmp_candles = []
        candles = []
        for i in range(n):
            if is_volume:
                values = [time[i], op[i], hi[i], lo[i], cl[i], vo[i]]
            else:
                values = [time[i], op[i], hi[i], lo[i], cl[i]]
            t_round = Converter.roundTime(time[i], interval, unit)
            if time[i] == t_round:
                tmp_candles.append(values)
                candle = Converter.candlePrice(time[i], tmp_candles)
                candles.append(candle)
                tmp_candles = []
            elif time[i] < t_round:
                tmp_candles.append(values)
            elif time[i] > t_round:
                tmp_candles = []
        return Converter.candles2dic(candles), candles, tmp_candles
    
    @staticmethod
    def tick_to_candle(dic: dict):
        def update(tohlc, price):
            if np.isnan(tohlc[2]):
                tohlc[2] = price
            else:
                if tohlc[2] < price:
                    tohlc[2] = price
            if np.isnan(tohlc[3]):
                tohlc[3] = price
            else:
                if tohlc[3] > price:
                    tohlc[3] = price           
        time = dic[Const.TIME]
        price = dic[Const.PRICE]    
        candles = []
        tohlc = None
        last_price = None
        t_current = None
        for t, p in zip(time, price):
            t_round = datetime(t.year, t.month, t.day, t.hour, t.minute, 0)
            if tohlc is None:
                t_current = t_round
                tohlc = [t_current, p, np.nan, np.nan, np.nan]
                update(tohlc, p)
            else:
                if t_round > t_current:
                    tohlc[4] = last_price
                    candles.append(tohlc)
                    t_current = t_round
                    tohlc = [t_current, p, np.nan, np.nan, np.nan]
                    update(tohlc, p)
                else:
                    update(tohlc, p)
            last_price = p
        if tohlc is not None:
            tohlc[4] = last_price
            update(tohlc, last_price)
            candles.append(tohlc)
        return Converter.candles2dic(candles), candles
    
    @staticmethod
    def roundTime(time: datetime, interval: int, unit: Const.TimeUnit):
        zone = time.tzinfo
        if unit == Const.UNIT_MINUTE:
            t = datetime(time.year, time.month, time.day, time.hour, 0, 0, tzinfo=zone)
        elif unit == Const.UNIT_HOUR:
            t = datetime(time.year, time.month, time.day, 0, 0, 0, tzinfo=zone)
        elif unit == Const.UNIT_DAY:
            if TimeUtils.isSummerTime(time):
                hour = 6
            else:
                hour = 7
            if time.hour <= hour:    
                return datetime(time.year, time.month, time.day, hour, 0, 0, tzinfo=zone)
            else:
                t = datetime(time.year, time.month, time.day, hour, 0, 0, tzinfo=zone)
                t += timedelta(days=1)
                return t
                
        if t == time:
            return t
        while t < time:
            if unit == Const.UNIT_MINUTE:
                t += timedelta(minutes=interval)
            elif unit == Const.UNIT_HOUR:
                t += timedelta(hours=interval)
        return t

    @staticmethod
    def candlePrice(time:datetime, tohlcv_list:[]):
        m = len(tohlcv_list[0])
        n = len(tohlcv_list)
        o = tohlcv_list[0][1]
        c = tohlcv_list[-1][4]
        h_array = [tohlcv_list[i][2] for i in range(n)]
        h = max(h_array)
        l_array = [tohlcv_list[i][3] for i in range(n)]
        l = min(l_array)
        if m > 5:
            v_array = [tohlcv_list[i][5] for i in range(n)]
            v = sum(v_array)
            return [time, o, h, l, c, v]
        else:
            return [time, o, h, l, c]    