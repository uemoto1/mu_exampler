#!/usr/bin/env python


def _trim_ast(kw):
    nkw = len(kw)
    for i in range(nkw):
        if kw[i] != '*':
            nast_l = i
            break
    for i in range(nkw):
        if kw[nkw - i - 1] != '*':
            nast_r = i
            break
    kw_t = kw[nast_l:nkw - nast_r]
    return nast_l, nast_r, kw_t


def _match_rec(kw, data, pos):
    if len(kw) == 0:
        flag, endpos = True, pos
    elif kw[0] == '*':
        flag, endpos = _match_rec(kw[1:], data, pos + 1)
        if not flag:  # Retry matching with skipping current word.
            flag, endpos = _match_rec(kw[1:], data, pos)
    elif pos < len(data) and kw[0] == data[pos]:
        flag, endpos = _match_rec(kw[1:], data, pos + 1)
    else:
        flag, endpos = False, None
    return flag, endpos


def search(kw, data, pos=0):
    nast_l, nast_r, kw_t = _trim_ast(kw)
    # Main loop
    flag, pos_m, endpos_m = False, None, None
    for pos_t in range(pos, len(data)):
        flag, endpos_t = _match_rec(kw_t, data, pos_t)
        if flag:
            pos_m = max(0, pos_t - nast_l)
            endpos_m = min(len(data), endpos_t + nast_r)
            break
    return flag, pos_m, endpos_m


def findall(kw, data):
    result = []
    pos = 0
    while pos < len(data):
        flag, pos, endpos = search(kw, data, pos)
        if flag:
            result += [(pos, endpos)]
            pos = endpos
        else:
            break
    return result
