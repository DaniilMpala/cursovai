from http.client import HTTPResponse
from urllib import response
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.core import serializers
import json
import re
from pymongo import MongoClient
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.decorators import parser_classes
from parser.functions import percentFromString, brandFromString, weightFromString, translateString, CursorIntoList
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


sortedBy = {
    1: [("shops.tovar.value", -1), "Подешевле"],
    2: [("shops.tovar.value", 1), "Подороже"],
    3: [("countBuyMonth", -1), "По спросу"],
    4: [("shops.tovar.valueSymbol", 1), "Подешевле за еденицу"],
    5: [("shops.tovar.valueSymbol", -1), "Подороже за еденицу"]
}


@api_view(['POST'])
@parser_classes((JSONParser,))
def getAllProduct(request):
    body = json.loads(request.body.decode('utf-8'))

    skip = 0
    query = {}
    query2 = {}
    sortedList = [("countBuyMonth", -1)]
    if("search" in body):
        if(body['search'].strip() != ""):

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
            if symbolaGr:
                weight = float(
                    re.search("[0-9.,]{1,}", symbolaGr[0])[0]) / 1000
            if symbolaKg:
                weight = float(re.search("[0-9.,]{1,}", symbolaKg[0])[0])
            if symbolaL:
                weight = float(re.search("[0-9.,]{1,}", symbolaL[0])[0])

            d = Brand.find_one({"$text": {"$search": translateString(body['search'])}}, {
                               "score": {"$meta": "textScore"}}, sort=[("score", {"$meta": "textScore"})])

            print(translateString(body['search']))
            if d != None:
                if d["score"] >= 1:
                    query.update({"brandSearch": d["title"]})
            if weight != 0:
                query.update({"weight": weight})

            percent = percentFromString(body['search'])
            if percent:
                query.update({"percent": {"$in": percent}})

            query.update({"$text": {"$search": body['search']}})
            query2.update({"score": {"$meta": "textScore"}})
            sortedList.append(("score", {"$meta": "textScore"}))
    if("category" in body):
        if len(body['category']) > 0:
            query.update({"categoryShort": {"$regex": "|".join(
                [f'({word})' for word in body['category']])}})
    if("skip" in body):
        skip = body["skip"]
    if("brand" in body):
        query.update({"brandSearch": body["brand"]})
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
        sortedList[0] = sortedBy[int(body["sortedBy"])][0]

    query2.update({"titleProduct": 0, "categoryShort": 0, "countBuyMonth": 0, "brandSearch": 0,
                  "brand": 0, "categoryFull": 0, "percent": 0, "searchText": 0, "weight": 0})

    # TODO близкие магазины выбрать
    #     #если магазин не выбран то выбираем по место положению
    if(not "shops" in body):
        body['shops'] = ["Лента", "Дикси"]
    elif(type(body['shops']) != type([])):
        body['shops'] = [body['shops']]

    data = {}
    print(skip, query, query2)
    for shop in body['shops']:
        query.update({"shops.Shop.title": shop})
        tmpData = CursorIntoList(Catalog.find(
            query, query2, limit=15, skip=skip, sort=sortedList))

        for i in range(len(tmpData)):
            tmpReplaceData = []
            for item in tmpData[i]['shops']:
                tmp = {"_id": tmpData[i]["_id"],
                       "symbol": tmpData[i]["symbol"]}
                tmp.update(item["tovar"])
                tmp.update(
                    {"shopsImg": item["Shop"]["img"], "titleShops": item["Shop"]["title"]})
                tmpReplaceData.append(tmp)
            tmpData[i] = tmpReplaceData

        data.update({shop: tmpData})

    return JsonResponse(data, safe=False)


@api_view(['POST'])
def getOptionsFilter(request):
    bd = CursorIntoList(FilterOptions.find({}, {"_id": 0}))[0]
    ip = request.META.get('REMOTE_ADDR', None)
    # city = g.city(ip)['city']
    # print(city)
    #desc - описание
    bd['shops'].sort()
    bd['brand'].sort()
    bd['category'].sort()

    bd['shops'] = [{"v": shop} for shop in bd['shops']]
    bd['brand'] = [{"v": brand} for brand in bd['brand']]
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
