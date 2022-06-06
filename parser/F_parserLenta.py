from ast import Try
from fnmatch import translate
import json
import re
import time
import requests
from pymongo import MongoClient
from bs4 import BeautifulSoup
from pymongo import ReturnDocument
import os
import sys
sys.path.append(os.path.abspath('../globale'))
from functions import percentFromString, brandFromString, weightFromString, translateString, deleteAdd, weightFromStringMany, updateOption
client = MongoClient(
    'mongodb+srv://testSait:test123Q@cluster0.obuew.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
db = client.catalog
Catalog = db["Catalog"]
Shops = db["ShopsName"].find_one({"title": "Лента"})
Brand = db["Brand"]


'''
Выделяем :
    Бренд
    Массу
    Кол-во пакетиков
    Категорию

'''


def getAvailability(url):
    time.sleep(1)
    r = requests.get(url, headers={
        "user-agent": "node-fetch"
    })

    if r.status_code != 200:
        return None
    h = BeautifulSoup(r.text, 'lxml')
    retJson = {}
    # у них хранятся все магазины в атрибуте в одном блоке поэтмоу этот блок распарсиваю
    for js in json.loads(h.find_all("div", {"class": "sku-page-control-container sku-page__control"})[0]["data-model"])["storesWithSku"]:
        retJson.update({js['storeName']: js["stockBalance"]})

    return retJson

# Это сам парсер


def parserLenta():

    # это каталоги в ленте где есть какие то товары продукты/для дома и тд
    allCat = ("g604e486481b04594c32002c67a2b459a", "g301007c55a37d7ff8539f1f169a4b8ae", "g68552e15008531b8ae99799a1d9391df", "g7cc5c7251a3e5503dc4122139d606465", "geee7643ec01603a5db2cf4819de1a033", "g0a4c6ef96090b5b3db5f6aa0f2c20563", "g0a4c6ef96090b5b3db5f6aa0f2c20563", "gaaa3a99413aa9e3963f7f07ed7a75ec0", "g523853c00788bbb520b022c130d1ae92", "gce3c6ce98ad51e02445da35b93d2c7b7", "gd152557d86db1829c25705de4db3cf66",
              "g4258530b46e66c5ac62f88a56ee8bce1", "g36505197bc9614e24d1020b3cfb38ee5", "gd6dd9b5e854cf23f28aa622863dd6913", "ga4638d8e16b266a51b9906c290531afb", "g4477ab807af5fd53f280b1aac7816659", "g81ed6bb4ec3cd75cbf9117a7e9722a1d", "g6b6be260dbddd6da54dcc3ca020bf380", "g1d79df330af0458391dd6307863d333e", "g1baf1ddaa150137098383967c9a8e732", "g9290c81c23578165223ca2befe178b47", "g7886175ed64de08827c4fb2a9ad914f3", "ge638b7ffc736e21c16b21710b4086220", "g6f4a2d852409e5804606d640dc97a2b1", "gb57865aeafbfc5aa8e086b86d3000a27", "g648e6f3e83892dabd3f63281dab529fd")
    for cat in allCat:
        offsetLast = 0
        totalCount = 1

        while (totalCount > offsetLast):
            # запросы делаем к ленте с разным началом offset
            print("Запрос")
            translate = False
            try:
                r = requests.post("https://lenta.com/api/v1/skus/list",
                                  headers={
                                      "content-type": "application/json",
                                      "user-agent": "node-fetch"
                                  },
                                  json={"nodeCode": cat, "filters": [], "typeSearch": 1,
                                        "sortingType": "ByCardPriceAsc", "offset": offsetLast, "limit": 24, "updateFilters": True},
                                  )
            except (TimeoutError, json.decoder.JSONDecodeError):
                print("Ошибка TimeoutError или json.decoder.JSONDecodeError")
                r.status_code = 500

            status_code = r.status_code
            r = r.json()

            if not "totalCount" in r:
                offsetLast += 25
                continue

            totalCount = r["totalCount"]
            print(status_code, totalCount, offsetLast)

            if status_code != 200 or r["totalCount"] == 0:
                time.sleep(3)
                continue
            if totalCount <= offsetLast or len(r["skus"]) == 0:
                break

            print("Всего ", totalCount, "В разделе твоаров: ",
                  len(r["skus"]))

            for v in r["skus"]:
                # переводим все в русские символы
                v['title'] = re.sub('\s*\-\s*', '-', v["title"])

                #title = weightFromStringMany(v['title'])
                weightSymbol = weightFromStringMany(v['title'])
                if not weightSymbol:
                    weightSymbol = [[None]]

                valueSymbol = v["cardPrice"]["value"] if len(
                    v["weightOptionsMax"]) > 0 and v["weightOptionsMax"] else None

                symbol = "кг" if len(
                    v["weightOptionsMax"]) > 0 and v["weightOptionsMax"] else None
                decimal = None
                for i in range(len(weightSymbol[0])):
                    if weightSymbol[0][i]:
                        try:
                            decimal = weightSymbol[0][i]
                            symbol = weightSymbol[1]
                            valueSymbol = v["cardPrice"]["value"] / decimal
                        except:
                            print(v['title'], decimal, symbol, weightSymbol[0])
                            break

                    brand = brandFromString(v["title"])

                    brandSearch = translateString(brandFromString(v["title"]))
                    if brandSearch != "" and not brandSearch.isnumeric():
                        d = Brand.find_one({"$text": {"$search": translateString(v['title'])}},
                                           {"score": {"$meta": "textScore"}},
                                           sort=[
                                               ("score", {"$meta": "textScore"})]
                                           ) or {"score": 0}
                    else:
                        d = {"score": 0}

                    print(brandSearch, d["score"], brandSearch != "")
                    if d["score"] >= 1:
                        brandSearch = d["value"]
                    elif brandSearch != "":
                        Brand.insert_one({
                            "value": brandSearch,
                            "label": brand,
                            "categoryFull": v["gaCategory"],
                            "categoryShort": v["gaCategory"].split("/")[1]
                        })


                    d = Catalog.find_one(
                        {"shops.tovar.description": v["title"]})

                    # Если ласт символ не буква удалить
                    # if len(re.findall("[^a-zA-ZА-Я]", v["title"][-1])) > 0:
                    #     v["title"] = v["title"][:-1].strip()
                    infoProduct = {
                        "Shop": {
                            "img": Shops["img"],
                            "title": Shops["title"]
                        },
                        "tovar": {
                            "description": v["title"],
                            "value": v["cardPrice"]["value"],
                            "oldValue": v["regularPrice"]['value'],
                            "valueSymbol": round(valueSymbol, 2) if valueSymbol != None else None,
                            "stockValue": v["stockValue"],
                            "img": v["imageUrl"],
                            "promoPercent": v["promoPercent"],
                            "promoEnd": v["promoEnd"].split("T")[0],
                            "promoStart": v["promoStart"].split("T")[0],
                            "productUrl": ("http://lenta.com" + v["skuUrl"]) if not v["skuUrl"] is None else None,
                            # getAvailability("http://lenta.com" + v["skuUrl"]),
                            "availabilityShop": None
                        }}

                    print(
                        f'Бренд: {brand} ({brandSearch}) | %: {percentFromString(v["title"])[1]} | вес и symbol: {decimal} {symbol} | Полный текст: {v["title"]}')

                    if d == None:
                        Catalog.insert_one({
                            "countBuyMonth": 0,
                            # Русский перевод добавляется
                            "searchText": v["title"] + " " + v["gaCategory"].replace("/", " ") + " " + deleteAdd(translateString(v["title"]), v["title"]),
                            "titleProduct": v["gaCategory"].split("/")[2],
                            "categoryFull": v["gaCategory"],
                            "categoryShort": v["gaCategory"].split("/")[1],
                            "brandSearch": brandSearch,
                            "brand": brand if brand != "" else brandSearch,
                            "weight": decimal,
                            "percent": percentFromString(v["title"])[1],
                            "symbol": symbol,
                            "shops": [infoProduct]
                        })
                    else:
                        reloaded = False
                        for i in range(len(d["shops"])):
                            if d["shops"][i]["Shop"]["title"] == "Лента":
                                d["shops"][i] = infoProduct
                                reloaded = True
                        if not reloaded:
                            d["shops"].append(infoProduct)
                        #print(list(sorted(d["shops"], key=lambda x: x["tovar"]["value"])))
                        d["shops"] = list(
                            sorted(d["shops"], key=lambda x: x["tovar"]["value"]))

                        Catalog.update_one({
                            "_id": d["_id"]
                        }, {
                            "$set": {"shops": d["shops"]}
                        })

                    # Обновим фильтр
                    updateOption()
                    ####################
            offsetLast += len(r["skus"])

            print(totalCount, offsetLast)


parserLenta()
