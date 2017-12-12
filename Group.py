#!/usr/bin/env python3
'''
CСоздание конечной группы
Элементы группы — строки
Операция умножения — склейка строк (s+t)
Единичный элемент — пустая строка (при выводе обозначается ɛ)
'''

import itertools 

# Как выводить единичный элемент
ZERO = "ɛ"
#Rules = {("ss","tt"), ("tttt",""), ("tst","s")}
Rules = {("ssss",""), ("ttttt",""), ("ts","stt")}
# Алфавит
Al = sorted(set("".join(a+b for a,b in Rules)))
# Алфавит с единичным элементом (пустой строкой)
Alp = Al+[""]
# WARNING: взятая от фонаря оценка наибольшей длины слова
MAXLEN=max(max(len(a),len(b)) for a,b in Rules)*(len(Alp))

def allnabers(res,maxlen=MAXLEN):
    '''Множество всех выражений не длиннее MAXLEN, получаемых из множества res
    однократным применением каждого правила каждому элементу в каждом возможном месте'''
    ret = set()
    for el in res:                      # для каждого элемента
        for c,d in Rules:               # применяем правило…
            for a,b in ((c,d),(d,c)):   # …а также и обратное правило
                # Если шаблон не содержится в элементе или результат слишком длинный, ничего не делать
                if not a in el or len(b)>=len(a) and len(el)-len(a)+len(b)>maxlen: continue
                # Применим правило один раз во всех возможных местах
                ret |= {el[:i]+el[i:].replace(a,b,1) for i in range(len(el)-len(a)+1) if el[i:].startswith(a)}
    return ret

# Кеш упрощённых выражений
Cache = {"":""}

def simplify(el,verbose=True):
    '''Упростить выражение el, вернуть наименьший возможный результат'''
    if el in Cache:                      # Если есть в кеше, хорошо
        if verbose: print(".",end="")
        return Cache[el]
    if(verbose): print("simplify <<",el,">>",end=" ")
    res, nab = set(), {el}
    # Создадим множество выражений, получаемых из el всевозможными подстановками правил
    # Предполагается, что выражения длиннее MAXLEN рассматривать не надо
    while nab:                          # выражения, которые мы ещё не рассмотрели         
        new = allnabers(nab)            # все «соседи» наших выражений
        nab = new-res                   # оставим только новые
        res |= nab                      # добавим в общее множество
    # ответ — наименьшая строка среди самых коротких
    ret = min(res, key=lambda w: (len(w),w))
    # Добавим в кеш все ответы
    Cache.update(dict(zip(res,(ret,)*len(res))))
    if verbose: print("{",ret,"}",len(Cache))
    return ret

lookers = "⁰¹²³⁴⁶⁷⁸⁹"                   # Красивые степени (только до 9)
lookers *= 1+(MAXLEN//len(lookers))     # на всякий случай (для степеней больше 9)
def look(s,alp):
    '''Украсить слово (например sssssttt → s⁵t³) в алфавите alp'''
    for c in alp:
        for i in range(s.count(c),1,-1):
            s = s.replace(c*i,c+lookers[i])
    return s

def look1(s,alp):
    '''Украсить слово, а если оно пустое — вернуть единичный символ'''
    return look(s,alp) or ZERO

def outtable(T):
    '''Красиво вывести таблицу'''
    print()
    skeys = sorted({a for a,b in T}|set(T.values()))
    fmt = "{{:{}}}".format((max(len(look(t,Al)) for t in skeys)))
    print("|",fmt.format(len(skeys))," ".join(fmt.format(look1(el,Al)) for el in skeys),"|")
    for a in skeys:
        print("|",fmt.format(look1(a,Al)), " ".join(fmt.format(look1(T.get((a,b),"."),Al)) for b in skeys),"|")

# Таблица умножения состоит из произведений алфавита на ɛ
table = { ("",el):el for el in Alp }
table.update( { (el,""):el for el in Alp } )

l = 0
while len(table)!=l:                    # Пока меняется объём таблицы
    outtable(table)
    l = len(table)
    skeys = {a for a,b in table} | set(table.values())
    for a in skeys:                     # По всем известным
        for b in skeys:                 # парам элементов
            table[a,b] = simplify(a+b)  # Вычислим их произведение
            #print("{}*{}={}".format(look(a,Al),look(b,Al),look(table[a,b],Al)), end=" ")
    #print(l,len(table))
outtable(table)

# Словарь обратных элементов (их проихведение == "" )
inverts = { a:b for a,b in table if table[a,b]=="" }

def closure(group, table):
    '''Замыкание множества group по обратным элементам и умножению с помощью table'''
    l, g = 0, set(group)
    while len(g) != l:                  # пока меняется объём группы
        l = len(g)
        # Добавляем в неё все обратные элементы и все произведения
        g |= {inverts[a] for a in g} | {table[a,b] for a in g for b in g}
    return g

subcache = set()                        # Множество всех подгрупп
def subgroups(table,group=set("")):
    '''Поиск всех подгрупп, определяемых таблицей table и содержащих все элементы из group'''
    els = {a for a,b in table.keys()}   # Элементы группы
    for el in els - group:              # По всемэлементам не из группы
        # Добавим элемент в множество и сделаем из него группу
        sub = frozenset(closure(group|{el},table))
        if sub not in subcache:         # Если такой подгруппы не было
            subcache.add(sub)           # добавим её
            subgroups(table, sub)       # найдём все подгруппы, содержащие её элементы

def outgroup(group):
    '''Вывод группы'''
    print("<",*[look1(g,Al) for g in sorted(group)],">")

subgroups(table)
print("\n\tSubgroups:",len(subcache))
for g in sorted(subcache, key=lambda s: (len(s),"".join(s))):
    outgroup(g)

import readline
el = "s"
while el:
    el = input("simplify({})> ".format(MAXLEN)).replace("*","")
    print(look(simplify(el,False),Al))
