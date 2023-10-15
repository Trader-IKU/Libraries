# -*- coding: utf-8 -*-
"""
Created: 2023/01/04 22:24:47
Revised: 2023/07/28 08:27
@author: IKU-Trader
"""

class Const:
    TIME = 'time'
    OPEN = 'open'
    HIGH = 'high'
    LOW = 'low'
    CLOSE = 'close'
    VOLUME = 'volume'
    PRICE = 'price'
    MID = 'mid'
    POLARITY = 'polarity'
    
    TimeUnit = str
    UNIT_MINUTE:TimeUnit = 'MINUTE'
    UNIT_HOUR:TimeUnit = 'HOUR'
    UNIT_DAY:TimeUnit = 'DAY'
    
    @staticmethod
    def timeSymbol2elements(symbol: str):
        u = symbol[0].upper()
        unit = None
        if u == 'D':
            unit = Const.UNIT_DAY
        elif u == 'H':
            unit = Const.UNIT_HOUR
        elif u == 'M':
            unit = Const.UNIT_MINUTE
        else:
            raise Exception('Bad time unit symbol ...'  + symbol)
            
        try:
            n = int(symbol[1:])
            return (n, unit)            
        except:
            raise Exception('Bad time unit symbol ...'  + symbol)