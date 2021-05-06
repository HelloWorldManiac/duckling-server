from datetime import datetime as dtm
import pytz, re


__all__ = ["rec_replace"]

Zones = ["Kaliningrad"
        , "Moscow"
        ,"Samara"
        ,"Yekaterinburg"
        ,"Omsk"
        ,"Krasnoyarsk"
        ,"Irkutsk"
        ,"Yakutsk"
        ,"Vladivostok"
        ,"Magadan"
        ,"Kamchatka"
        ]

ZZZ = []
for z in Zones:
    for tz in pytz.all_timezones:
        if z in tz:
            ZZZ.append(tz)



zones = [*map(pytz.timezone,ZZZ)]
BASE = pytz.timezone('Europe/Moscow')
timeReg = re.compile("\d{4}\-\d{2}\-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}\+\d{2}:\d{2}")
inFormat = "%Y-%m-%dT%H:%M:%S.%f"
outFormat = "%Y-%m-%dT%H:%M:%S.000"


enrich_tz = lambda duckDate: dict(map(lambda zone: (zone.zone, BASE.localize(
                                                               dtm.strptime(duckDate[:-6],inFormat)
                                                             ).astimezone(zone)
                                                              .strftime(outFormat)
                                                   ), zones)
                                 )

def rec_replace(js):
    f = (timeReg.search(js) or [None])[0]
    if not f:
        return js
    else:
        return rec_replace(js.replace(f, str(enrich_tz(f))))
