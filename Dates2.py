import re
import numpy as np
from datetime import datetime as dt 
import re
from functools import reduce

__all__ = ["enrich_time", "AutoReplacer", "collision_fix_1", "dater"]

days = ["понедельник"
        , "вторник"
        , "среда"
        , "четверг"
        , "пятница"
        , "суббота"
        , "восресенье"]

weekday = re.compile("(?:{}) (?=(0?1\d)|(2[0-3]))".format("|".join(["(?<={})"] * 7).format(*days)))
collision_fix_1 = lambda text: weekday.sub(string=text, repl = " в ")


TD = re.compile("(в|на| ){,4}(((0?1\d)|(2[0-3]))[: \.]([0-5][05])?)(на| ){,4}((2\d)|(3[01])|([01]?\d))?[\. /]?(1[0-2]|0?[1-9])?[\. /]?(((2\d{3})|(1[89]\d{2})))?")
DT = re.compile("((((2\d)|([3][01])|[01]?\d)))[\. /]((1[012])|(0?[1-9]))[\. /]?((19\d{2})|([2-9]\d{3}))?(в|на| ){,4}(((0?1\d)|(2[0-3]))[: \.]?([0-5][05])?)?")
digitize = re.compile("\d+")

def enclose(t,b,s,g='minute'):
    return {'dim': 'time',  'body': b, 'end': s[1], 'start': s[0], 'value': {'type': 'value', 'value': t, 'grain': g}}

def isLeap(y):
        if not y % 4 == 0:
            return False
        elif not y % 100 == 0:
            return True
        elif not y % 400 == 0:
            return False
        else:
            return True

def modify(y = 0, m = 0, d = 0, h = 0, mm = 0):
    today = dt.today()
    y = binarize(y or today.year)
    m = binarize(m or today.month)
    d = binarize(d or today.day)
    h = binarize(h)
    mm = binarize(mm)
    
    return f"{y}-{m}-{d}T{h}:{mm}:00.00000+3:00"

padList = lambda l, n: l + [0] * (n - (len(l)))
mapper = lambda l: dict(zip(["d", "m", "y", "h", "mm"], map(stringize,l)))
stringize = lambda i: str(i).zfill(2)
datify = lambda l: "{y}-{m}-{d}T{h}:{mm}:00.000+3:00".format(**mapper(l))
monthEnds = (31,28,31,30,31,30,31,31,30,31,30,31)

def dateTimeMap(li):
    li = padList(li,5)
    today = dt.today()
    a0, a1, a2, a3, a4 = li
    
    maxMonLen = monthEnds[a1-1 if a1 <= 12 else 11] + isLeap(today.year)
    return datify([a0 if a0 <= maxMonLen else maxMonLen     #d
                 , a1 if a1 <  12 else 12        #m
                 , a2 if a2 > 1000 else today.year  #y
                 , a3 if a2 > 1000 else a2          #hh
                 , ((a4 // 5) * 5) if a2 > 1000  else ((a3 // 5) * 5)] #mm
                 )


def timeDateMap(li):
    li = padList(li,5)
    today = dt.today()
    a0, a1, a2, a3, a4 = li
    
    hh = a0 if 0 <= a0 <= 23 else 0
    mm = a1 if 0 <= a1 <= 59 and (a1 % 5 == 0) else (a1 // 5) * 5
    d = a1 if (mm == 0) and (1 <= a1 <= 31) and (1 <= a2 <= 31) else a2
    m = a2 if (mm == 0) and (a2 <= 12 and a3 <= 12) else a3 if 1 <= a3 <= 12 else 12
    y = a3 if (mm == 0) and (a3 > 1000 or a4 > 1000) else (today.year if a4 == 0  else a4)
    return datify([d,m,y,hh,mm])


def dater(text):
    dfound = DT.search(text)
    tfound = TD.search(text)
    
    d_t = digitize.findall(dfound[0]) if dfound else []                          
    
    t_d = digitize.findall(tfound[0]) if tfound else []
   
    if len(d_t) == len(t_d) and d_t != t_d:
        return None
    elif len(d_t) and len(d_t) >= len(t_d):
        s = dfound.span()
        b = dfound[0]
        #print(s,b)
        d_t = list(map(int,d_t))
        
        if len(d_t) > 2:
            t = dateTimeMap(d_t)
            return enclose(t,b,s)
        elif len(d_t) == 2:
            t = dateTimeMap(d_t)
            return enclose(t,b,s, "day")
        else: 
            return None
    elif len(t_d) and len(d_t) < len(t_d):
        s = tfound.span()
        b = tfound[0]
        #print(s,b)
        t_d = list(map(int,t_d))
        if len(t_d) >= 2:
            t = timeDateMap(t_d)
            return enclose(t,b,s)            
        else: 
            return None   
    else:
        return None
             
def enrich_time(item):
    if item["dim"] != "time":
        return item
    else:    
        val = item["value"]
        if val["type"] == 'interval':
            item["grain"] = val.get("from",val.get("to"))["grain"]
            item["type"] = val["type"]
        elif val["type"] == 'value':
            item["grain"] = val["grain"]
            item["type"] = val["type"]
        else:
            pass
    return item  
    
    



compose = lambda f, g: lambda x: f(g(x))
enabler = lambda tup: lambda x: tup[0].sub(tup[1],x)


import re
from functools import reduce

def enclose(t,b,s,g='minute'):
    return {'dim': 'time',  'body': b, 'end': s[1], 'start': s[0], 'value': {'type': 'value', 'value': t, 'grain': g}}

compose = lambda f, g: lambda x: f(g(x))
enabler = lambda tup: lambda x: tup[0].sub(tup[1],x)
binarize = lambda x: str(x) if int(x) // 10 else "0"+str(x)



class AutoReplacer:
    def __init__(self):
        
        self.date = re.compile("\d\d[ \.][а-я]{,8}[ \.]?(\d\d){0,2}")
        self.digits = re.compile("\d+")
        
        
        self.reStrings = (
          "январ(е|я|ю|ь)|янв\.?"
        , "феврал(е|я|ю|ь)|фев\.?"
        , "март(а|у|е)?|мар\.?"
        , "апрел(е|я|ю|ь)|апр\.?"
        , "ма(е|й|я)"
        , "июн(е|я|ю|ь)|июн\.?"
        , "июл(е|я|ю|ь)|июл\.?"
        , "август(е|а)|авг\.?"
        , "сентябр(е|я|ю|ь)|сент?\.?"
        , "октябр(е|я|ю|ь)|окт\.?"
        , "ноябр(е|я|ю|ь)|ноя\.?"
        ,  "декабр(е|я|ю|ь)|дек\.?"
        )
           
        self.replacers = (
                  "1"
                , "2"
                , "3" 
                , "4"
                , "5"
                , "6"
                , "7"
                , "8"
                , "9"
                , "10"
                , "11"
                , "12"
                )
        #self.process = lambda x: reduce(compose, map(enabler,zip(map(re.compile,self.reStrings),self.replacers)), lambda I: I)(x.lower())
        self.process = lambda x: reduce(compose, map(enabler,zip(map(re.compile,self.reStrings),self.replacers)), lambda I: I)(x.lower())
    
    def bad_date(self, text):
        
        txt = self.date.search(text)
        if not txt: 
            return None
        else: 
            s = txt.span()
            b = txt[0]
        txt = list(map(lambda x: x, self.digits.findall(self.process(b))))
        if len(txt) == 3:
            d,m,y = txt
            y = (len(y) == 4 and y) or "20" + y
            return enclose(modify(y = y, m = m, d = d), b, s)
        elif len(txt) == 2:
            d,m = txt
            return enclose(modify(m = m, d = d), b, s)

    
