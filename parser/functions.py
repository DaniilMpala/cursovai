import math
import re
from pymongo import MongoClient
from bson.objectid import ObjectId
client = MongoClient(
    'mongodb+srv://testSait:test123Q@cluster0.obuew.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
FilterOptions = client.catalog["FilterOptions"]



'''Выделяем проценты в продукте'''
# 3.4-4.5   3.4/4.5    3.5    5


def percentFromString(string):
    try:
        if len(re.findall("[0-9]{1,}[0-9,.]*[\/][0-9,.]*%", string)) > 0:
            percent = [float(re.sub("[ %\-\–\/]", "", word.replace(",", ".")))
                       for word in re.findall("[0-9]{1,}[0-9,.]*[\/][0-9,.]*%", string)[0].split("/")]
        else:
            percent = [float(re.sub("[ %\-\–\/]", "", word.replace(",", "."))) if string.find(
                "%") > -1 else None for word in re.findall("[0-9]{1,}[0-9,.]*[%\-\–]", string)]  # *%
    except:
        percent = []

    # if len(percent) == 1:
    #     if(percent[0].find("/") > -1):
    #         percent = [percent[0].split("/")[0], percent[0].split("/")[1]]
    #     else:
    #         percent = [percent[0]]
    # elif len(percent) > 1:
    #     percent = [percent[0], percent[1]]
    # else:
    #     percent = [None]

    # if rounde and percent[0]:
    #     if float(percent[0]) > 10:
    #         # Округляем в меньшую
    #         return [math.floor(float(percent[0])), percent[0]]
    #     else:
    #         return [percent[0]]
    return list(filter(None, percent))


'''Выделяем бренды для поиска'''


def brandFromString(string):
    brand = re.search("[ \"'][.0-9 ]*[a-zA-ZА-Я0-9 \-\-'.!`]{2,}[ \"',]", string) \
        or re.search("[ \"'][.0-9 ]*[.a-zA-ZА-Я0-9 \-\-'.!`]{2,}[ \"',]*$", string) \
        or [""]
    if brand:
        return brand[0].replace("\"", "").replace(",", "").strip()
    else:
        return None


'''Выделяем вес товара'''
# вывод в формате 400г


def weightFromStringMany(string):
    tmp = re.search("[.,0-9]{2,}.?((пакетиков)|(пак)|(п))", string) \
        or re.search("([0-9][,.\/]?[0-9]?){1,}.?л{1}", string) \
        or re.search("([0-9][,.\/]?[0-9]?){1,}.?мл{1}", string) \
        or re.search("([0-9][,.\/]?[0-9]?){1,}.?[гГ]{1}", string) \
        or re.search("([0-9][,.\/]?[0-9]?){1,}.?кг{1}", string) \
        or re.search("([0-9][,.\/]?[0-9]?){1,}.?шт{1}", string)
    if tmp:
        print(tmp, string)
        weight = filter(None, re.findall("[0-9,.]*", tmp[0]))
        symbolDefault = re.search(
            "[млгркМЛГРКГпакПАКшт]{1,}", tmp[0])[0].lower()
        tmp = []
        symbolNew = symbolDefault
        for dec in weight:
            if re.search("[0-9,.]", dec):
                dec = float(dec.replace(",", "."))
                if symbolDefault == "мл":
                    symbolNew = "л"
                    dec = dec / 1000
                if symbolDefault == "г" or symbolDefault == "гр":
                    symbolNew = "кг"
                    dec = dec / 1000

                tmp.append(dec)
        #[[], г]
        return [tmp, symbolNew]
    else:
        return None


def weightFromString(string):
    for i in range(5):
        tmp = re.search("[.,0-9]{1,}.?((пакетиков)|(пак)|(п))", string) \
            or re.search("([0-9][,.]?[0-9]?){1,}.?л{1}", string) \
            or re.search("([0-9][,.]?[0-9]?){1,}.?мл{1}", string) \
            or re.search("([0-9][,.]?[0-9]?){1,}.?[гГ]{1}", string) \
            or re.search("([0-9][,.]?[0-9]?){1,}.?кг{1}", string) \
            or re.search("([0-9][,.]?[0-9]?){1,}.?шт{1}", string)

        if tmp:
            if re.search("[0-9]", tmp[0]):
                return tmp
        else:
            return None


"""Перевод слов в русский язык"""
dic = {'ь': '', 'ъ': '', 'а': 'a', 'б': 'b', 'в': 'v',
       'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'zh',
       'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l',
       'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
       'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h',
       'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ы': 'yi',
       'э': 'e', 'ю': 'yu', 'я': 'ya'}


def get_key(d, value):
    for k, v in d.items():
        if v == value:
            return k


def translateString(string, toRussia=True):
    t = ''
    if not toRussia:
        for i in string:
            t += dic.get(i.lower(), i.lower()
                         ).upper() if i.isupper() else dic.get(i, i)
    else:
        for i in string:
            t += (get_key(dic, i.lower()) if not get_key(dic, i.lower()) is None else i) if i.islower(
            ) else (get_key(dic, i.lower()) if not get_key(dic, i.lower()) is None else i).upper()

    return t


def get_existing_values(d, keys):
    return filter(None, map(d.get, keys))


def deleteAdd(string, string2):
    tmp = ""
    for word in string.split():
        if string2.find(word) == -1:
            tmp += " " + word
    return tmp.strip()

# Погрешность


def similarity(src, dst):
    src = src.lower()
    dst = dst.lower()
    # ищем самое длинное слово
    wordLenMax = max([max(src.split(), key=len),
                     max(dst.split(), key=len)], key=len)
    maxstr = max([src, dst], key=len)

    # Максимальная погрешность определяется по самому длинному слову
    maxLossWord = 100 - int(len(wordLenMax)/len(maxstr)*100)

    dst_buf = dst
    result = 0
    for char in src:
        if char in dst_buf:
            dst_buf = dst_buf.replace(char, '', 1)
            result += 1
    r1 = int(result / len(src) * 100)
    r2 = int(result / len(dst) * 100)
    return [r1 if r1 < r2 else r2, maxLossWord <= r1 if r1 < r2 else r2]


def similarityText(str1, str2):

    str1 = str1.replace(weightFromString(
        str1)[0] if weightFromString(str1) else "", "")
    str2 = str2.replace(weightFromString(
        str1)[0] if weightFromString(str1) else "", "")

    str1 = str1.lower().split(" ")
    str2 = str2.lower()
    count = 0
    for word in str1:
        if str2.find(word) > -1:
            count += 1
    # Процент совпадения, кол-во ошибок
    return [count / len(str1), len(str1)-count]

# f = translate("Кофе растворимый BUSHIDO Original сублимированный, ст/б, 100г, Швейцария, 100 г")
# print(deleteAdd(f, "Кофе растворимый BUSHIDO Original сублимированный, ст/б, 100г, Швейцария, 100 г"))
# БУСХИДО Оригинал
# Выводит слова которые не повторидлись во 2-ой строке из ПЕРВОЙ


def CursorIntoList(res, deleteParams=[]):
    tmp = []
    for doc in res:
        if doc is None:
            continue
        if "_id" in doc:
            doc["_id"] = str(doc['_id'])
        if len(deleteParams) > 0:
            for param in deleteParams:
                if(param in doc):
                    del doc[param]

        tmp.append(doc)
    return tmp

'''Обновляем опции фильтра'''


def updateOption():
    options = {
        "maxPrice": client.catalog['Catalog'].find({}, sort=[("shops.tovar.value", -1)]).limit(1)[0]["shops"][0]["tovar"]["value"],
        "minPrice": client.catalog['Catalog'].find({'shops.tovar': {"$exists": True}}, sort=[("shops.tovar.value", 1)]).limit(1)[0]["shops"][0]["tovar"]["value"],
        "shops": [item["title"] for item in client.catalog['ShopsName'].find({})],
        "brand": [item["title"] for item in client.catalog['Brand'].find({})],
        "category": list(set([item["categoryShort"] for item in client.catalog['Brand'].find({})])),
    }
    FilterOptions.update_one({"_id": ObjectId("626c0db9acde4a80808c3b07")}, {
        "$set": options
    })