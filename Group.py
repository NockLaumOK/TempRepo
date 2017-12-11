#!/usr/bin/env python3
'''

'''

import itertools 

ZERO = "ɛ"
Rules = {("ss","tt"), ("tttt",""), ("tst","s")}
#Rules = {("ssss",""), ("ttttt",""), ("ts","stt")}
#Rules = []
Al = sorted(set("".join(a+b for a,b in Rules)))
Alp = Al+[""]
MAXLEN=max(max(len(a),len(b)) for a,b in Rules)*(len(Alp))
#MAXLEN = 15

def lookup(e, table):
    return {table[e[:i],e[i:]] for i in range(1,len(e)) if (e[:i],e[i:]) in table}

def allnabers(res,maxlen=MAXLEN):
    '''Множество всех элементов, получаемых из множества res
    однократным применением каждогог правила в каждом возможном месте'''
    ret = set()
    for e in res:                       # для каждого элемента
        for c,d in Rules:               # применяем правило…
            for a,b in ((c,d),(d,c)):   # …а также и обратное правило
                # Если шаблон не содержится в элементе или результат слишком длинный, ничего не делать
                if not a in e or len(b)>=len(a) and len(e)-len(a)+len(b)>maxlen: continue
                # XXX: не работает, когда ss→что-то для ssss (получится ['', '', ''], а надо ещё ['s','','s']
                # Разобьём элемент на части, удалив из него все вхождения a
                # Если a — пустая строка (правило вида ""→"что-то"),
                # то элемент "tss" превращается в ["", "t", "s", "s", "" ]
                chain = e.split(a) if a else [""]+list(e)+[""]
                # Соберём обратно, заменив последовательно по одному вхождению a на b
                ret |= {a.join(chain[:i+1])+b+a.join(chain[i+1:]) for i in range(len(chain)-1)}
    return ret

Cache = {"":""}
def simplify(e,verbose=True):
    if e in Cache:
        if verbose: print(".",end="")
        return Cache[e]
    if(verbose): print("simplify <<",e,">>",end=" ")
    l, res, nab = -1, set(), {e}
    while nab:
        new = allnabers(nab)
        nab = new-res
        res |= nab
    ret = min(res, key=lambda w: (len(w),w))
    Cache.update(dict(zip(res,(ret,)*len(res))))
    print("{",ret,"}",len(Cache))
    return ret

lookers = "⁰¹²³⁴⁶⁷⁸⁹"
lookers *= 1+(MAXLEN//len(lookers))
def look(s,alp):
    for c in alp:
        for i in range(s.count(c),1,-1):
            s = s.replace(c*i,c+lookers[i])
    return s

def look1(s,alp):
    return look(s,alp) or ZERO

def outtable(T):
    print()
    skeys = sorted({a for a,b in T}|set(T.values()))
    fmt = "{{:{}}}".format((max(len(look(t,Al)) for t in skeys)))
    print("|",fmt.format(len(skeys))," ".join(fmt.format(look1(e,Al)) for e in skeys),"|")
    for a in skeys:
        print("|",fmt.format(look1(a,Al)), " ".join(fmt.format(look1(T.get((a,b),"."),Al)) for b in skeys),"|")

table = {(simplify(a[:i]),simplify(a[i:])):simplify(b) for a,b in Rules for i in range(1,len(a))}
table.update({(simplify(a[:i]),simplify(a[i:])):simplify(b) for b,a in Rules for i in range(1,len(a))})

l = 0
while len(table)!=l:
    outtable(table)
    l = len(table)
    skeys = {a for a,b in table} | set(table.values())
    for a in skeys:
        for b in skeys:
            table[a,b] = simplify(a+b)
            #print("{}*{}={}".format(look(a,Al),look(b,Al),look(table[a,b],Al)), end=" ")
    #print(l,len(table))
outtable(table)

inverts = { a:b for a,b in table if not table[a,b] }
#print("Inverts:", " ".join("{}*{}".format(a or 1,b or 1) for a,b in inverts.items()))

def closure(group, table):
    l, g = 0, set(group)
    while len(g) != l:
        l = len(g)
        g |= {inverts[a] for a in g} | {table[a,b] for a in g for b in g}
    return g

subcache = set()
def subgroups(table,group=set("")):
    els = {a for a,b in table.keys()}
    for e in els - group:
        sub = frozenset(closure(group|{e},table))
        if sub not in subcache:
            subcache.add(sub)
            subgroups(table, sub)

def outgroup(group):
    print("<",*[look1(g,Al) for g in sorted(group)],">")

subgroups(table)
print("\n\tSubgroups:",len(subcache))
for g in sorted(subcache, key=lambda s: (len(s),"".join(s))):
    outgroup(g)

import readline
e = "s"
while e:
    e = input("simplify({})> ".format(MAXLEN)).replace("*","")
    print(look(simplify(e,False),Al))
