import json
import re
import time
import requests
from pymongo import MongoClient
from bs4 import BeautifulSoup
from pymongo import ReturnDocument
from bson.objectid import ObjectId
from datetime import datetime
from functions import percentFromString, brandFromString, weightFromString, translateString, deleteAdd, similarity, similarityText, CursorIntoList, weightFromStringMany, updateOption
from bson.objectid import ObjectId
client = MongoClient(
    'mongodb+srv://testSait:test123Q@cluster0.obuew.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
db = client.catalog
Catalog = db["Catalog"]
Shops = db["ShopsName"].find_one({"title": "Дикси"})
Brand = db["Brand"]



def parserDixy():
    maxLen = 0

    for obj in CursorIntoList(Catalog.find({"shops.Shop.title": "Дикси"})):
        tmp = []
        searchTextDel = ""
        for shop in obj["shops"]:
            if shop['Shop']['title'] != 'Дикси':
                tmp.append(shop)
            else:
                searchTextDel = shop['tovar']['description']
        if len(tmp) > -1:
            d = Catalog.update_one({
                    "_id": ObjectId(obj["_id"])
                }, {
                    "$set": {"shops": tmp, "searchText": obj["searchText"].replace(searchTextDel, "")}
            })
        else:
            d = Catalog.delete_one({
                    "_id": ObjectId(obj["_id"])
                })
        print("удалеяем дикси", obj["_id"],)



    for i in range(1, 50):
        r = requests.post("https://dixy.ru/catalog/?PAGEN_1="+str(i),
                          headers={
            "content-type": "application/json",
                            "user-agent": "node-fetch"
        },
            json={"AJAX_SHOW_MORE": "Y", "FILTER_NAME": "catalogFilter", "FILTER[PROPERTY_DEPARTMENT]": "6",
                              "FILTER[!DETAIL_PICTURE]": False, "FILTER[=PROPERTY_ADULT]": False, },
        )
        html = BeautifulSoup(r.text, 'lxml')

        if maxLen < len(html.findAll("div", {"class": "item"})):
            maxLen = len(html.findAll("div", {"class": "item"}))

        # dixyCatalogItem
        for block in html.findAll("div", {"class": "item"}):
            if len(block.select("div.dixyCatalogItemPrice__new")) == 0:
                continue

            title = ""

            if(block.select("div.dixyCatalogItem__title")[0].text.find("...") == -1):
                title = block.select("div.dixyCatalogItem__title")[
                    0].text.strip()
            else:
                title = block.select("div.dixyCatalogItem__hover")[
                    0].text.strip()
            #title = ts.yandex(title, to_language='ru',from_language='en')
            price = float(
                f'{block.select("div.dixyCatalogItemPrice__new")[0].text.strip()}.{block.select("div.dixyCatalogItemPrice__kopeck")[0].text.strip()}')
            promoPercent = block.select("div.dixyCatalogItemPrice__discount")[
                0].text.strip().replace("-", "").replace("%", "")
            promoEnd = datetime.strptime(block.select("div.dixyCatalogItem__term")[
                                         0].text.strip().split("-")[1].strip(), "%d.%m.%Y")
            promoStart = datetime.strptime(block.select("div.dixyCatalogItem__term")[
                                           0].text.strip().split("-")[0].strip(), "%d.%m.%Y")

            weightSymbol = weightFromStringMany(title) 
            if not weightSymbol:
                weightSymbol = [[None]]

            decimal = None
            symbol = None
            valueSymbol = None
            
            for i in range(len(weightSymbol[0])):
                if weightSymbol[0][i]:
                    decimal = weightSymbol[0][i]
                    symbol = weightSymbol[1]
                    title = re.sub(" +", " ", title.replace("упак.", "").replace(
                        "с/к", "").replace("ст/б", "").replace("в/у", "").strip())
                    # title = re.sub(", ", "", title)
                    valueSymbol = price / decimal

                infoProduct = {
                    "Shop": {
                        "img": Shops["img"],
                        "title": Shops["title"]
                    },
                    "tovar": {
                        "description": title,
                        "value": price,
                        "oldValue": None,
                        "img": block.find("img", class_="")["src"],
                        "valueSymbol": round(valueSymbol, 2) if valueSymbol != None else None,
                        "stockValue": None,
                        "promoPercent": promoPercent,
                        "promoEnd": promoEnd.strftime("%Y-%m-%d"),
                        "promoStart": promoStart.strftime("%Y-%m-%d"),
                        "productUrl": None,
                        "availabilityShop": None,
                    }}
                d = Brand.find_one({"$text": {"$search": translateString(title)}}, {
                                "score": {"$meta": "textScore"}}, sort=[("score", {"$meta": "textScore"})])
                
                percent = percentFromString(title)
                if d != None:
                    if d["score"] >= 1:
                        brand = d
                        query = {"$text": {"$search": title}, "brand": {"$regex": d["title"]}}  # regex ДОБАВИЛ!
                        if weightSymbol:
                            query.update({"weight": decimal})
                        if percent:
                            query.update({"percent": percent})
                        
                        #Поиск схожего 
                        d = Catalog.find_one(query, {"score": {"$meta": "textScore"}}, sort=[("score", {"$meta": "textScore"})])
                        if d != None:
                            # 3 условия совпадение товаров
                            # 1 - по score 2.5 +
                            # 2 - Есть точное совпадение между предложениями
                            okeySimilarityText = False
                            for shop in d["shops"]:
                                if similarityText(shop["tovar"]["description"], title)[0] == 1:
                                    okeySimilarityText = True
                                    break
                                if similarityText(title, shop["tovar"]["description"])[0] == 1:
                                    okeySimilarityText = True
                                    break
                            if d["score"] >= 2.5 or okeySimilarityText:
                                print(f'{d["score"]}    weight: {decimal} {symbol}, percent: {percent} | {title} ')
                                # Добавляем к найденному товар

                                finded = False
                                for i in range(len(d["shops"])):
                                    if d["shops"][i]["Shop"]["title"] == "Дикси":
                                        finded = d["shops"][i]["tovar"]["description"]
                                maximum = 0
                                maximum2 = 0
                                if finded:
                                    for i in range(len(d["shops"])):
                                        if d["shops"][i]["Shop"]["title"] == "Дикси":
                                            continue

                                        v1 = similarity(title,  d["shops"][i]["tovar"]["description"])[0]
                                        v2 = similarity(d["shops"][i]["tovar"]["description"],  title)[0]
                                        if maximum < v2:
                                            maximum = v2
                                        if maximum < v1:
                                            maximum = v1
                                    print(f'Схожесть нового товара с товаром из других магазов: {maximum}  | {title}')

                                
                                    for i in range(len(d["shops"])):
                                        if d["shops"][i]["Shop"]["title"] == "Дикси":
                                            continue

                                        v1 = similarity(finded,  d["shops"][i]["tovar"]["description"])[0]
                                        v2 = similarity(d["shops"][i]["tovar"]["description"],  finded)[0]
                                        if maximum2 < v2:
                                            maximum2 = v2
                                        if maximum2 < v1:
                                            maximum2 = v1
                                    print(maximum, maximum2)
                                    if maximum > maximum2:
                                        for i in range(len(d["shops"])):
                                            if d["shops"][i]["Shop"]["title"] == "Дикси":
                                                d["shops"][i] = infoProduct 
                                    
                                    print(f'Схожесть старого товара с товаром из других магазов: {maximum2} | {finded}')

                                else:
                                    print("append", d["searchText"])
                                    d["shops"].append(infoProduct)

                                d["shops"] = list(sorted(d["shops"], key=lambda x: x["tovar"]["value"]))

                                Catalog.update_one({
                                    "_id": d["_id"]
                                }, {
                                    "$set": {"shops": d["shops"], "searchText": d["searchText"]+" "+(title if d["searchText"].find(title) > -1 else "")}
                                })
                            else:
                                print(f'НОВЫЙ {d["score"]} - weight: {decimal} {symbol}, percent: {percent} | {title} ')
                                # Если есть бренд но нету товара
                                Catalog.insert_one({
                                    "countBuyMonth": 0,
                                    # Русский перевод добавляется
                                    "searchText": title + " " + brand["categoryFull"].replace("/", " ") + deleteAdd(translateString(title), title),
                                    "titleProduct": brand["categoryFull"].split("/")[2],
                                    "categoryFull": brand["categoryFull"],
                                    "categoryShort": brand["categoryShort"],
                                    "brandSearch": translateString(brand["title"]),
                                    "brand": brand["title"],
                                    "weight": decimal,
                                    "percent": percentFromString(title),
                                    "symbol": symbol,
                                    "shops": [infoProduct]
                                })
                        else:
                            print(f'НОВЫЙ - weight: {decimal} {symbol}, percent: {percent} | {title} ')
                            # Если есть бренд но нету товара
                            Catalog.insert_one({
                                "countBuyMonth": 0,
                                # Русский перевод добавляется
                                "searchText": title + " " + brand["categoryFull"].replace("/", " ") + deleteAdd(translateString(title), title),
                                "titleProduct": brand["categoryFull"].split("/")[2],
                                "categoryFull": brand["categoryFull"],
                                "categoryShort": brand["categoryShort"],
                                "brandSearch": translateString(brand["title"]),
                                "brand": brand["title"],
                                "weight": decimal,
                                "percent": percentFromString(title),
                                "symbol": symbol,
                                "shops": [infoProduct]
                            })
                            pass
                else:
                    pass
                
                #Обновим фильтр
                updateOption()
                ####################
        print(i, "|", len(html.findAll("div", {"class": "item"})))
        if maxLen > len(html.findAll("div", {"class": "item"})):
            print("Товары закончились на странице: ", i)
            break


# while True:
parserDixy()
