from django.http import HttpResponse, JsonResponse
import json
import re
from pymongo import MongoClient
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from bson.objectid import ObjectId
from rest_framework.decorators import parser_classes

from globale.functions import percentFromString, brandFromString, validAuth, weightFromString, translateString, CursorIntoList, get_client_ip
import pendulum
from datetime import timedelta, datetime
# from django.contrib.gis.utils import GeoIP
# g = GeoIP()

client = MongoClient(
    'mongodb+srv://testSait:test123Q@cluster0.obuew.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
db = client.catalog
Catalog = db["Catalog"]
FilterOptions = db["FilterOptions"]
Category = db["Category"]
ShopsName = db["ShopsName"]
Brand = db["Brand"]
User = db["User"]

sortedBy = {
    3: [("countBuyMonth", -1), "По спросу"],
    1: [("shops.tovar.value", -1), "Подороже"],
    2: [("shops.tovar.value", 1), "Подешевле"],
    4: [("shops.tovar.valueSymbol", 1), "Подороже за еденицу"],
    5: [("shops.tovar.valueSymbol", -1), "Подешевле за еденицу"]
}

banIpDemandItem = []


@api_view(['POST'])
@parser_classes((JSONParser,))
def makeFavorite(request):
    auth = validAuth(request.META["HTTP_AUTHORIZATION"])
    if not auth["auth"]:
        return JsonResponse({"result": False})

    body = json.loads(request.body.decode('utf-8'))

    if not body["now"]:
        req = {"$addToSet": {"favoriteProducts": body["_id"]}}
    else:
        req = {"$pull": {"favoriteProducts": body["_id"]}}

    User.update_one({"login": auth['payload']['login']}, req)

    return JsonResponse({"result": True})


@api_view(['POST'])
@parser_classes((JSONParser,))
def updateDemandItem(request):
    ip = get_client_ip(request)
    if not ip:
        return HttpResponse(status=400)

    # Добавим бан на запрос в 5 сек после каждого запроса
    findIpIndex = next((index for (index, person) in enumerate(
        banIpDemandItem) if person["ip"] == ip), None)

    if not findIpIndex is None:
        if banIpDemandItem[findIpIndex]["ip"] == ip and banIpDemandItem[findIpIndex]["date"] < datetime.now():
            del banIpDemandItem[findIpIndex]
        else:
            return HttpResponse(status=403)

    banIpDemandItem.append({
        "ip": ip,
        "date": datetime.now() + timedelta(seconds=5)
    })

    body = json.loads(request.body.decode('utf-8'))
    print("Пытаемся обновить item -", body, ip)
    if not "_id" in body:
        return HttpResponse(status=400)

    _id = re.match("[0-9a-z]*", body["_id"])
    if not _id:
        return HttpResponse(status=400)

    print("Обновим спрос у айтема -", body, ip)
    Catalog.update_one({
        "_id":  ObjectId(_id[0]),
    }, {
        "$inc": {"countBuyMonth": 1}
    })

    return HttpResponse(status=200)


@api_view(['POST'])
@parser_classes((JSONParser,))
def getChoiceBuyers(request):
    auth = validAuth(request.META["HTTP_AUTHORIZATION"])
    if not auth["auth"]:
        return JsonResponse({"auth": False}, status=403)

    user = {"favoriteProducts":[]}
    if auth['auth']:
        user = User.find_one({"login": auth['payload']['login']})

    query2 = {
        "titleProduct": 0,
        "categoryShort": 0,
        "countBuyMonth": 0,
        "brandSearch": 0,
        "brand": 0,
        "categoryFull": 0,
        "percent": 0,
        "searchText": 0,
        "weight": 0
    }
    tmpData = CursorIntoList(Catalog.find(
        {}, query2, limit=5, sort=[("countBuyMonth", -1)]))
    for i in range(len(tmpData)):
        tmpReplaceData = []
        for item in tmpData[i]['shops']:
            tmpReplaceData.append({
                "_id": tmpData[i]["_id"],
                "symbol": tmpData[i]["symbol"],
                "shopsImg": item["Shop"]["img"],
                "titleShops": item["Shop"]["title"],
                "favorit": tmpData[i]["_id"] in user["favoriteProducts"],
                **item["tovar"]
            })
        tmpData[i] = tmpReplaceData
    return JsonResponse(tmpData, safe=False)


@api_view(['POST'])
@parser_classes((JSONParser,))
def getAllProduct(request):
    try:
        auth = validAuth(request.META["HTTP_AUTHORIZATION"])
        body = json.loads(request.body.decode('utf-8'))

        skip = 0
        query = {}
        query2 = {}
        sortedList = [("countBuyMonth", -1), ("_id", 1)]
        if("search" in body):
            body['search'] = body['search'][0].strip()
            if(body['search'] != ""):

                symbolaMl = re.search(
                    "[0-9]{1,}[ ]?((мл)|(миллитров)|(милитров)|(миллилитрами))", body['search'])
                symbolaGr = re.search(
                    "[0-9]{1,}[ ]?((г)|(гр)|(грам)|(грамм)|(граммами)|(граммов))", body['search'])
                symbolaKg = re.search(
                    "[0-9]{1,}[ ]?((кг)|(кило)|(килограм)|(килограмм)|(килограммов)|(килограммами))", body['search'])
                symbolaL = re.search(
                    "[0-9]{1,}[ ]?((л)|(литр)|(литров)|(литрам))", body['search'])
                weight = 0
                if symbolaMl:
                    weight = float(
                        re.search("[0-9.,]{1,}", symbolaMl[0])[0]) / 1000
                    body['search'] = body['search'].replace(symbolaMl[0], "")
                if symbolaGr:
                    weight = float(
                        re.search("[0-9.,]{1,}", symbolaGr[0])[0]) / 1000
                    body['search'] = body['search'].replace(symbolaGr[0], "")
                if symbolaKg:
                    weight = float(re.search("[0-9.,]{1,}", symbolaKg[0])[0])
                    body['search'] = body['search'].replace(symbolaKg[0], "")
                if symbolaL:
                    weight = float(re.search("[0-9.,]{1,}", symbolaL[0])[0])
                    body['search'] = body['search'].replace(symbolaL[0], "")

                # d = Brand.find_one({"$text": {"$search": translateString(body['search'])}}, {
                #                 "score": {"$meta": "textScore"}}, sort=[("score", {"$meta": "textScore"})])

                # if d != None:
                #     print(d)
                #     if d["score"] >= 1:
                #         query.update({"brandSearch": d["title"]})
                if weight != 0:
                    query.update({"weight": weight})

                percent = percentFromString(body['search'])
                if percent[1]:
                    query.update({"percent": {"$in": percent[1]}})
                    body['search'] = body['search'].replace(percent[0][0], "")

                query.update({"shops.tovar.description": {
                             "$regex": body['search'].strip().replace(" ", "|"), "$options": "i"}})
                # Поиск по совпадениям
                # query.update({"$text": {"$search": body['search']}})
                # query2.update({"score": {"$meta": "textScore"}})
                # sortedList.append(("score", {"$meta": "textScore"}))
        if("category" in body):
            if len(body['category']) > 0:
                query.update({"categoryShort": {"$regex": "|".join(
                    [f'({word})' for word in body['category']])}})
        if("skip" in body):
            skip = body["skip"]
        if("price" in body):
            query.update({"shops.tovar.value": {"$gte": float(
                body["price"][0]), "$lte": float(body["price"][1])}})
        if("brand" in body):
            query.update({"brandSearch": {"$in": body["brand"]}})
        # if("shops" in body):
        #     if(len(body['shops']) > 0):
        #         query.update({"shops": {"$elemMatch": {
        #                      "$or": [{"Shop.title": shop} for shop in body['shops']]}}})

        if("sortedBy" in body):
            # 1 - от большего к меньшему (цена)
            # 2 - от меньшего к большему (цена)
            # default  3 - по спросу ( от большего к меньшему)
            # 4 - от меньшего к большему (цена за кг)
            # 5 - от большего к меньшему (цена за кг)
            sortedList[0] = sortedBy[int(body["sortedBy"][0])][0]

        query2.update({
            "titleProduct": 0,
            "categoryShort": 0,
            "countBuyMonth": 0,
            "brandSearch": 0,
            "brand": 0,
            "categoryFull": 0,
            "percent": 0,
            "searchText": 0,
            "weight": 0
        })

        # TODO близкие магазины выбрать
        #     #если магазин не выбран то выбираем по место положению
        if(not "shops" in body):
            body['shops'] = ["Лента", "Дикси"]
        elif(type(body['shops']) != type([])):
            body['shops'] = [body['shops']]

        data = {}

        user = {"favoriteProducts":[]}
        if auth['auth']:
            user = User.find_one({"login": auth['payload']['login']})

        for shop in body['shops']:
            query.update({"shops.Shop.title": shop})
            print(skip, query, query2, sortedList)
            tmpData = CursorIntoList(Catalog.find(
                query, query2, limit=15, skip=skip, sort=sortedList))
            for i in range(len(tmpData)):
                tmpReplaceData = []
                for item in tmpData[i]['shops']:
                    tmpReplaceData.append({
                        "_id": tmpData[i]["_id"],
                        "symbol": tmpData[i]["symbol"],
                        "shopsImg": item["Shop"]["img"],
                        "titleShops": item["Shop"]["title"],
                        "favorit": tmpData[i]["_id"] in user["favoriteProducts"],
                        **item["tovar"]
                    })
                tmpData[i] = tmpReplaceData

            data.update({shop: tmpData})

        return JsonResponse(data, safe=False)
    except Exception as err:
        print(pendulum.now(), "getAllProduct | Ошибка", err)


@api_view(['POST'])
def getOptionsFilter(request):
    bd = CursorIntoList(FilterOptions.find({}, {"_id": 0}))[0]
    ip = request.META.get('REMOTE_ADDR', None)
    # city = g.city(ip)['city']
    # print(city)
    #desc - описание
    bd['shops'].sort()
    bd['brand'] = sorted(bd['brand'], key=lambda d: d['label'])
    bd['category'].sort()

    bd['shops'] = [{"v": shop} for shop in bd['shops']]
    bd['brand'] = [{"v": brand["value"], "label": brand["label"]}
                   for brand in bd['brand']]
    bd['category'] = [{"v": category} for category in bd['category']]

    tmpDict = []
    for sort in sortedBy:
        tmpDict.append({"v": sort, "label": sortedBy[sort][1]})
    bd.update({"sortedBy": tmpDict})

    return JsonResponse(bd, safe=False)


# @api_view(['POST'])
# @parser_classes((JSONParser,))
# def getCategory(request):
#     body = json.loads(request.body.decode('utf-8'))
#     shops = [str(shop) for shop in body["shops"]]
#     return JsonResponse(CursorIntoList(Catalog.find({"shops.Shop.title": {"$or": shops}}).distinct("categoryShort")), safe=False)
