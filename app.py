import os, re
from typing import List
import pytz
import pickle
from duckling import Language, Duckling
from flask import Flask, request, json, Response, jsonify
from flask_httpauth import HTTPBasicAuth
from flask_restful import Api
from Extractors.name.Name import *
from Extractors.city.City import *
from datetime import datetime as dt
from Dates2 import *


exyear = re.compile(pattern="(?<=\b\d{4}) ?года?")

cropTime = lambda x: x["dim"] == "time"
filterTime = lambda x: x["dim"] != "time"
a = AutoReplacer()

def splitTime(arr):
    timeblock = list(filter(cropTime, arr))
    
    if not timeblock or len(timeblock) < 2:
        #print("\n\n**************\n\n")
        return arr
    else: 
        sortedArr = sorted(timeblock, key = lambda x: len(x["body"]), reverse=True)
        #print(sortedArr)
        
        if len(sortedArr[0]["body"]) == len(sortedArr[1]["body"]):
            return arr
        else:
            return list(filter(filterTime, arr)) + sortedArr[:1]
              
    
USER = os.environ.get('U_NAME', 'username')
PASSWORD = os.environ.get('U_PASS', 'password')

app = Flask(__name__)
api = Api(app)
auth = HTTPBasicAuth()

users = {
    # USER: generate_password_hash(PASSWORD),
    USER: PASSWORD,
}


 
zoneSuffix = {}
for z in pytz.all_timezones:
    tz = pytz.timezone(z).localize(dt.today()).strftime('%z')
    zoneSuffix[z] = f"{tz[:3]}:{tz[3:]}"

@auth.verify_password
def verify_password(username, password):
    if username in users:
        return users[username] == password
        # return check_password_hash(users.get(username), password)
    return False


d = Duckling()
d.load(['ru'])

ne = NameExtractor()
ce = CityExtractor() 


tz_regex = re.compile("\+\d{,2}:\d\d")
TZ = lambda s, repl: tz_regex.sub(repl=repl, string = s)

def extract(text):
    acc = []
    matches = ne.extract(text.replace(".", ","))
    
    for N in matches:
        name, (start, end) = N
        tmp = {
            "body": "",
            "dim": "names",
            "end": end,
            "start": start,
            "value": {"type": "value", "value": name}
        }
        if tmp["value"]["value"]:
            acc.append(tmp)
    
    matches = ce.extract(text)
    for A in matches:

        tmp = {
            "body": "",
            "dim": "city",
            "end": 0,
            "start": 0,
            "value": {"type": "value", "value": A}}
        if tmp["value"]["value"]:
            acc.append(tmp) 
    
    return acc


def unic_dict(data: List) -> List:
    """
    Убирает повторяющиеся словари из списка.
    :param data: Список словарей
    :return: Список унмкальных словарей
    """
    set_of_dicts = set()
    for item in data:
        set_of_dicts.add(json.dumps(item))
    return [json.loads(item) for item in set_of_dicts]


@app.route('/actuator/health', methods=['GET'])
def health():
    return jsonify({"status": "UP"})


@app.route('/parse', methods=['POST'])
@auth.login_required
def parse():
    text = request.form.get("text", "")
    zn = request.form.get('zone', "Europe/Moscow")
    localZone = pytz.timezone(zn)
    text = collision_fix_1(text)
    
    k = dater(text)
    k = eval(TZ(str(k), zoneSuffix[zn]))
    bad = a.bad_date(text)
    bad = eval(TZ(str(bad), zoneSuffix[zn]))
    

    if not text:
        return Response([], content_type="application/json; charset=utf-8")
      
    ref = dt.now().strftime("%Y-%m-%dT%H:%M:%S.%f" + zoneSuffix[zn])
    out = d.parse(exyear.sub(string = text.lower(), repl = " "), language=Language.RUSSIAN, reference_time=ref) or []#, dim_filter=[Dim.DURATION, Dim.TIME] )

        
    if k:
        out.append(k)
    if bad:
        out.append(bad)
    
    acc = extract(text)
    if acc:
        out.extend(acc)
    out = [*map(enrich_time, out)]
    
    #res = rec_replace(str(splitTime(unic_dict(out))))
    res = splitTime(unic_dict(out))
    json_string = json.dumps(res, ensure_ascii=False).replace("00000", "000").encode('utf8')
    #print(str(splitTime(unic_dict(out))))
    return Response(json_string, content_type="application/json; charset=utf-8")


if __name__ == '__main__':
    app.run(port=8080, host="0.0.0.0")
