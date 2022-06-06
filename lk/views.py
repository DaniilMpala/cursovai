from datetime import timedelta, datetime
import math
from django.http import HttpResponse, JsonResponse
import json
import re
from pymongo import MongoClient
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from bson.objectid import ObjectId
from rest_framework.decorators import parser_classes
from globale.functions import validAuth, percentFromString, brandFromString, weightFromString, translateString, CursorIntoList, get_client_ip
import pendulum
import hashlib
from django.contrib import auth
import jwt
from discountsite.settings import SECRET_KEY
client = MongoClient(
    'mongodb+srv://testSait:test123Q@cluster0.obuew.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
db = client.catalog
User = db["User"]
Catalog = db["Catalog"]
ShopsName = db["ShopsName"]


@api_view(['POST'])
@parser_classes((JSONParser,))
def deleteSaveBasket(request):
    auth = validAuth(request.META["HTTP_AUTHORIZATION"])
    if not auth["auth"]:
        return JsonResponse({"auth": False, "result": False}, status=403)

    body = json.loads(request.body.decode('utf-8'))
    #костыль удаление по индуксу в массиве
    User.update_one({
        "login": auth['payload']['login']
    }, {
        "$unset": {f'historyBasket.{body["index"]}': 1}
    })

    User.update_one({
        "login": auth['payload']['login']
    }, {
        "$pull": {'historyBasket': None}
    })

    return JsonResponse({"auth": True, "result": True})


@api_view(['POST'])
@parser_classes((JSONParser,))
def getDataSaveBasket(request):
    auth = validAuth(request.META["HTTP_AUTHORIZATION"])
    if not auth["auth"]:
        return JsonResponse({"auth": False}, status=403)

    user = User.find_one({"login": auth['payload']['login']})
    body = json.loads(request.body.decode('utf-8'))

    data = []
    query2 = {
        "titleProduct": 0,
        "categoryShort": 0,
        "countBuyMonth": 0,
        "brandSearch": 0,
        "brand": 0,
        "categoryFull": 0,
        "percent": 0,
        "searchText": 0,
        "weight": 0,
        "symbol": 0,
        "shops.tovar.oldValue": 0,
        "shops.tovar.valueSymbol": 0,
        "shops.tovar.stockValue": 0,
        "shops.tovar.promoPercent": 0,
        "shops.tovar.productUrl": 0,
        "shops.tovar.availabilityShop": 0
    }

    listItemIds = []
    for basket in user["historyBasket"][body["skip"]:body["skip"]+30]:
        for shopTitle in basket:
            for _ids in basket[shopTitle]:
                if not _ids in listItemIds:
                    listItemIds.append(ObjectId(_ids))

    dataItem = CursorIntoList(Catalog.find(
        {"_id": {"$in": listItemIds}}, query2))

    for basket in user["historyBasket"][body["skip"]:body["skip"]+30]:
        for shopTitle in basket:
            for i in range(len(basket[shopTitle])):
                item = next(
                    (item for item in dataItem if item["_id"] == basket[shopTitle][i]), None)
                if item is None:
                    basket[shopTitle][i] = {
                        "description": "Товара больше нет в Базе!",
                        "img": "",
                        "promoEnd": "",
                        "promoStart": "",
                        "shopsImg": "",
                        "titleShops": shopTitle,
                        "value": 0,
                        "_id": basket[shopTitle][i]
                    }
                    continue

                itemInShop = next(
                    (itemInShop for itemInShop in item["shops"] if itemInShop["Shop"]["title"] == shopTitle), None)
                if itemInShop is None:
                    basket[shopTitle][i] = {
                        "description": "Товара больше нет в Базе этого магазина!",
                        "img": "",
                        "promoEnd": "",
                        "promoStart": "",
                        "shopsImg": "",
                        "titleShops": shopTitle,
                        "value": 0,
                        "_id": basket[shopTitle][i]
                    }
                    continue

                basket[shopTitle][i] = {
                    "description": itemInShop['tovar']["description"],
                    "img": itemInShop['tovar']["img"],
                    "promoEnd": itemInShop['tovar']["promoEnd"],
                    "promoStart": itemInShop['tovar']["promoStart"],
                    "shopsImg": itemInShop['Shop']["img"],
                    "titleShops": shopTitle,
                    "value": itemInShop['tovar']["value"],
                    "_id": basket[shopTitle][i]
                }

        data.append(basket)

    return JsonResponse({"auth": True, "data": data})


@api_view(['POST'])
@parser_classes((JSONParser,))
def saveBasket(request):
    auth = validAuth(request.META["HTTP_AUTHORIZATION"])
    if not auth["auth"]:
        return JsonResponse({"result": False, "textMessage": "Вы не авторизованы"}, status=403)

    body = json.loads(request.body.decode('utf-8'))

    # найдем все магазины которые пришли в запросе
    shopData = CursorIntoList(ShopsName.find({
        "title": {"$in": [shopTitle for shopTitle in body]}
    }, {
        "img": 0,
        "_id": 0
    }))

    saveBasket = {}

    for shopTitle in shopData:
        shopTitle = shopTitle["title"]

        # Проверим что все пришедшие объекты явялются _id в монго
        tmp = []
        for _idItem in body[shopTitle]:
            if ObjectId.is_valid(_idItem):
                tmp.append(_idItem)

        if len(tmp) > 0:
            saveBasket.update({shopTitle: tmp})

    data = User.find_one({
        "login": auth['payload']['login'],
        "historyBasket": {"$in": [saveBasket]}
    })

    if not data is None:
        return JsonResponse({"result": False, "textMessage": "Вы уже сохранили эту корзину"})

    User.update_one({
        "login": auth['payload']['login']
    }, {
        "$push": {"historyBasket": {"$each": [saveBasket], "$position": 0}}
    })

    return JsonResponse({"result": True, "textMessage": "Корзина сохранена в профиле"})


@api_view(['POST'])
@parser_classes((JSONParser,))
def getDataUserFavoriteProducts(request):
    auth = validAuth(request.META["HTTP_AUTHORIZATION"])
    if not auth["auth"]:
        return JsonResponse({"auth": False}, status=403)

    user = User.find_one({"login": auth['payload']['login']})
    print(request.body)
    body = json.loads(request.body.decode('utf-8'))

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
    data = []
    tmpData = CursorIntoList(Catalog.find({"_id": {"$in": [ObjectId(
        user) for user in user["favoriteProducts"]]}}, query2, limit=30, skip=body["skip"], sort=[("countBuyMonth", -1)]))
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
        data.append(tmpReplaceData)
    return JsonResponse({"auth": True, "data": data}, safe=False)


@api_view(['POST'])
@parser_classes((JSONParser,))
def getDataUserSetting(request):
    auth = validAuth(request.META["HTTP_AUTHORIZATION"])
    if not auth["auth"]:
        return JsonResponse({"auth": False}, status=403)

    user = User.find_one({"login": auth['payload']['login']})
    return JsonResponse({
        "auth": True,
        "geolocation": user["geolocation"],
        "notifyFavoriteProducts": user["setting"]["notifyFavoriteProductsPromoAction"]
    }, status=200)


@ api_view(['POST'])
@ parser_classes((JSONParser,))
def changeNotifyUser(request):
    body = json.loads(request.body.decode('utf-8'))
    auth = validAuth(request.META["HTTP_AUTHORIZATION"])
    if not auth["auth"]:
        return JsonResponse({"auth": False}, status=403)

    if "notifyFavoriteProductsPromoAction" in body["type"]:
        User.update_one({
            "login": auth['payload']['login']
        }, {
            "$set": {"setting.notifyFavoriteProductsPromoAction": body["value"]}
        })
    return JsonResponse({
        "auth": True,
        "status": True,
    }, status=200)


@ api_view(['POST'])
@ parser_classes((JSONParser,))
def loginOrRegistration(request):
    body = json.loads(request.body.decode('utf-8'))

    if not "login" in body:
        return JsonResponse(status=400)
    if not "password" in body:
        return JsonResponse(status=400)
    if body["login"].strip() == "":
        return JsonResponse({"error": "Логин не может быть пустым"}, status=400)
    if body["password"].strip() == "":
        return JsonResponse({"error": "Пароль не может быть пустым"}, status=400)
    if len(body["password"].strip()) < 4:
        return JsonResponse({"error": "Пароль должен собдержать минимум 4 символа"}, status=400)
    if re.match("([A-zА-я])+([0-9\-_\+\.])*([A-zА-я0-9\-_\+\.])*@([A-zА-я])+([0-9\-_\+\.])*([A-zА-я0-9\-_\+\.])*[\.]([A-zА-я])+", body["login"].strip()) is None:
        return JsonResponse({"error": "Не похоже на почту :)"}, status=400)

    login = str(body["login"].strip())
    password = str(body["password"].strip())

    user = User.find_one({"login": login})

    if user is None:
        # Юзера нет в ьд, регистрируем
        # TODO геолакаци.
        user = {
            "login": login,
            "password": hashlib.md5(password.encode('utf-8')).hexdigest(),
            "dateRegistration": datetime.now().isoformat(),
            "favoriteProducts": [],
            "historyBasket": [],
            "geolocation": None,
            "setting": {
                "notifyFavoriteProductsPromoAction": False,
            }
        }
        User.insert_one(user)
    else:
        if user["password"] != hashlib.md5(password.encode('utf-8')).hexdigest():
            return JsonResponse({"error": "Не верный пароль от аккаунта :("}, status=400)
    encoded_jwt = jwt.encode(
        {
            "login": login,
            "exp": round((datetime.now() + timedelta(hours=48)).timestamp()*1000)
        }, SECRET_KEY, algorithm="HS256")

    return JsonResponse({
        "accessToken": encoded_jwt
    }, status=200)
