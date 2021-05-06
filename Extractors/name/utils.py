import re
from pyrsistent import plist, pvector
ex = re.compile("[,;!?]| и | а | но ")

#to_repl = {'Льв':'Лев','Льву':'Лев','Рассказов':'Рассказова','Юлию':'Юлия','Чупину':'Чупина'}

to_repl = {'Льв':'Лев','Льву':'Лев','Рассказов':'Рассказова','Юлию':'Юлия','Чупину':'Чупина','Оксана':'Оксан', 'Климов':'Климову'} # added
def _group(matches):
    matches = plist(matches)
    if matches:
        def helper(matches, shift, group, acc):
            if len(shift) == 0:
                return acc.append(group)
            elif shift.first[1] - matches.first[2] < 3:
                return helper(matches.rest, shift.rest, group.append(shift.first[0]), acc)
            else:
                return helper(matches.rest, shift.rest, pvector([shift.first[0]]), acc.append(group))

        return helper(matches, matches.rest, pvector([matches.first[0]]), pvector([]))
    else: return []

def _match(text, extracts):
    text = ex.sub('<*****>',text)

    def helper(ext, txt, acc):
        if len(ext) == 0:
            return acc
        else:
            head = ext.first
            if len(head) >2:
                del_ch = 2
            else:
                del_ch = 1
            acc = acc.append(plist((head, txt.find(head[:-del_ch]), txt.find(head[:-del_ch]) + len(head))))
            return helper(ext.rest, txt.replace(head,"*" * len(head[:-del_ch]),1), acc)        
    return helper(extracts, text, pvector())

def replace_text(text):
    text = text.replace('ё','е')
    for i in to_repl.keys():
        text = text.replace(i,to_repl[i])
    return text
