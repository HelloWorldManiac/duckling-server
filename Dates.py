import re
import numpy as np
from datetime import datetime as dt 
import re
from functools import reduce

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
binarize = lambda x: x if x // 10 else "0"+str(x)
def enclose(t,b,s,g='minute'):
    return {'dim': 'time',  'body': b, 'end': s[1], 'start': s[0], 'value': {'type': 'value', 'value': t, 'grain': g}}

def stringize(y = 0, m = 0, d = 0, h = 0, mm = 0):
    today = dt.today()
    y = binarize(y or today.year)
    m = binarize(m or today.month)
    d = binarize(d or today.day)
    h = binarize(h)
    mm = binarize(mm)
    
    return f"{y}-{m}-{d}T{h}:{mm}:00.00000+3:00"


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
        if len(d_t) == 5:
            d,m,y,h,mm = d_t
            if h <=23 and m<=12 and d<=31 and mm<=59:
                t = stringize(y,m,d,h,mm)
                return enclose(t,b,s)
        elif len(d_t) == 4 and max(d_t) > 1000:
            d,m,y,h = d_t
            if h <=23 and m<=12 and d<=31:
                t = stringize(y,m,d,h,0)
                return enclose(t,b,s)
        elif len(d_t) == 4 and max(d_t) < 1000:
            d,m,h, mm = d_t
            if h <=23 and mm < 60 and d<=31 and mm<=59:
                t = stringize(0,m,d,h,mm)
                return enclose(t,b,s)
        elif len(d_t) == 3 and max(d_t) > 1000:
            d,m,y = d_t
            if d<=31 and m<=12:
                t = stringize(y,m,d,0,0)
                return enclose(t,b,s)
        elif len(d_t) == 3 and max(d_t) < 1000:
            d,m,h = d_t
            if h <=23 and m<=12 and d<=31:
                t = stringize(0,m,d,h,0)
                return enclose(t,b,s)
        elif len(d_t) == 3 and max(d_t) > 1000:
            d,m,y = d_t
            if m<=12 and d<=31:
                t = stringize(y,m,d,0,0)
                return enclose(t,b,s)
        elif len(d_t) == 2:
            d,m = d_t
            if m<=12 and d<=31:
                t = stringize(0,m,d,0,0)
                return enclose(t,b,s, "day")
        else: 
            return None
    elif len(t_d) and len(d_t) < len(t_d):
        s = tfound.span()
        b = tfound[0]
        #print(s,b)
        t_d = list(map(int,t_d))
        if len(t_d) == 5:
            h,mm,d,m,y = t_d
            if h <=23 and m<=12 and d<=31 and mm<=59:
                
                t = stringize(y,m,d,h,mm)
                return enclose(t,b,s)
        elif len(t_d) == 4 and max(t_d) > 1000:
            h,d,m,y = t_d
            t = t = stringize(y,m,d,h,0)
            return enclose(t,b,s)
        elif len(t_d) == 4 and max(t_d) < 1000:
            h,mm,d,m = t_d
            t = t = stringize(0,m,d,h,mm)
            return enclose(t,b,s)
        elif len(t_d) == 3 and max(t_d) < 1000:
            h,mm,d = t_d
            if h <=23 and mm < 60:
                t = stringize(0,0,d,h,mm)
                return enclose(t,b,s)
        elif len(t_d) == 2:
            h, mm = t_d
            if h <=23 and mm < 60:
                t = stringize(0,0,0,h,mm)
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
            return enclose(stringize(y = y, m = m, d = d), b, s)
        elif len(txt) == 2:
            d,m = txt
            return enclose(stringize(m = m, d = d), b, s)

    
