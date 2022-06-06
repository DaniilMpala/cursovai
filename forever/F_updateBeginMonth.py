from pymongo import MongoClient
import datetime
import math

import os
import sys
sys.path.append(os.path.abspath('../globale'))
from functions import setInterval

client = MongoClient(
    'mongodb+srv://testSait:test123Q@cluster0.obuew.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
db = client.catalog
Catalog = db["Catalog"]


def updateCountBuyMonth():
    skip = 0
    numberDay = datetime.date.today().day
    numberHour = datetime.datetime.now().hour
    if numberDay == 1 and numberHour == 0:
        # Значит начало месяца и удалим у всех кол-во покупок на 50%
        while True:
            data = Catalog.find_one(
                {},
                limit=1,
                skip=skip,
                sort=[("countBuyMonth", -1)]
            )
            if not data is None:
                if data["countBuyMonth"] > 0:
                    countBuyMonth = math.floor(data["countBuyMonth"]*0.5)
                    Catalog.update_one({
                        "_id": data["_id"]
                    }, {
                        "$set": {"countBuyMonth": countBuyMonth}
                    })
                    print(f'Обновили id: {data["_id"]}, поставили кол-во покупок в месяц: {countBuyMonth}')
                    skip=+1
                else:
                    break
            else:
                break


setInterval(1*60*60,updateCountBuyMonth)
