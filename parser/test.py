from functions import percentFromString, brandFromString, weightFromString, translateString, deleteAdd
def similarity(src, dst):
    src = src.lower()
    dst = dst.lower()
    #ищем самое длинное слово
    wordLenMax = max([max(src.split(), key=len), max(dst.split(), key=len)], key=len) 
    maxstr = max([src, dst], key=len) 

    #Максимальная погрешность определяется по самому длинному слову
    maxLossWord = 100 -int(len(wordLenMax)/len(maxstr)*100)


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
    #str1 рсавниваем с str2
    str1 = str1.replace(weightFromString(str1)[0] if weightFromString(str1) else "", "")
    str2 = str2.replace(weightFromString(str1)[0] if weightFromString(str1) else "", "")

    str1 = str1.lower().split(" ")
    str2 = str2.lower()
    count = 0
    for word in str1:
        if str2.find(word) > -1:
            count += 1
    #Процент совпадения, кол-во ошибок
    return [count / len(str1), len(str1)-count]

a = "Молоко Простоквашино топленое 3,2%, 930 мл"
b = "Кефир Простоквашино классический 3,2%, 930 г"

c = "Молоко топленое ПРОСТОКВАШИНО 3,2%, без змж, 930мл"
print(similarityText(a,c))
print(similarityText(c,a))
# print(similarityText("Чай черный AZERCAY с ароматом бергамота, 25пак"))
# import translators as ts
# print(ts.baidu("со вкусом винограда MENTOS Pure fresh со вкусом винограда, 54г", to_language='ru', from_language='en'))