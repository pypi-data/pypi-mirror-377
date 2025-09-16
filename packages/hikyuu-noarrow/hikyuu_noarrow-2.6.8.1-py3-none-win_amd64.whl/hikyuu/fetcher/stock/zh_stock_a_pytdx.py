# coding:utf-8
#
# The MIT License (MIT)
#
# Created on: 2020-11-29
#     Author: fasiondog

import datetime
from concurrent import futures
from pytdx.hq import TdxHq_API
from hikyuu.data.common_pytdx import search_best_tdx
from hikyuu import get_stock, constant
from hikyuu.util import *


@hku_catch(ret=None, callback=lambda quotes: hku_warn(quotes))
def parse_one_result(quotes):
    result = {}
    hku_check_ignore(quotes, "Invalid input param!")
    try:
        result['datetime'] = datetime.datetime.combine(
            datetime.date.today(), datetime.time.fromisoformat(quotes['servertime'])
        )
    except:
        return None

    result['market'] = 'SH' if quotes['market'] == 1 else 'SZ'
    result['code'] = quotes['code']
    result['name'] = ''
    result['open'] = quotes['open']  # 今日开盘价
    result['yesterday_close'] = quotes['last_close']  # 昨日收盘价
    result['close'] = quotes['price']  # 当前价格
    result['high'] = quotes['high']  # 今日最高价
    result['low'] = quotes['low']  # 今日最低价
    result['bid'] = float(quotes['bid1'])  # 竞买价，即“买一”报价
    result['ask'] = float(quotes['ask1'])  # 竞卖价，即“卖一”报价
    # 指数 volumn 需要乘以 0.01
    stk = get_stock(f"{result['market']}{result['code']}")
    if not stk.is_null() and stk.type == constant.STOCKTYPE_INDEX:
        result['volume'] = float(quotes['vol']) * 0.01
    else:
        result['volume'] = float(quotes['vol'])  # 成交的股票手数
    result['amount'] = round(quotes['amount'] * 0.0001, 2)  # 成交金额，单位为“元”，若要以“万元”为成交金额的单位，需要把该值除以一万

    result['bid'] = [float(quotes['bid1']), float(quotes['bid2']), float(
        quotes['bid3']), float(quotes['bid4']), float(quotes['bid5'])]
    result['bid_amount'] = [float(quotes['bid_vol1']), float(quotes['bid_vol2']), float(
        quotes['bid_vol3']), float(quotes['bid_vol4']), float(quotes['bid_vol5'])]
    result['ask'] = [float(quotes['ask1']), float(quotes['ask2']), float(
        quotes['ask3']), float(quotes['ask4']), float(quotes['ask5'])]
    result['ask_amount'] = [float(quotes['ask_vol1']), float(quotes['ask_vol2']), float(
        quotes['ask_vol3']), float(quotes['ask_vol4']), float(quotes['ask_vol5'])]
    return result


@hku_catch(ret=[], trace=True)
def request_data(api, stklist, parse_one_result):
    """请求失败将抛出异常"""
    quotes_list = api.get_security_quotes(stklist)
    result = [parse_one_result(q) for q in quotes_list] if quotes_list is not None else []
    return [r for r in result if r is not None]


@hku_catch(ret=([], []))
def inner_get_spot(stocklist, ip, port, batch_func=None):
    api = TdxHq_API()
    hku_check(api.connect(ip, port), 'Failed connect tdx ({}:{})!'.format(ip, port))

    count = 0
    tmplist = []
    result = []
    max_size = 80
    err_list = []
    for stk in stocklist:
        tmplist.append((1 if stk.market == 'SH' else 0, stk.code))
        count += 1
        if count >= max_size:
            phase_result = request_data(api, tmplist, parse_one_result)
            if phase_result:
                result.extend(phase_result)
                if batch_func:
                    batch_func(phase_result)
            else:
                err_list.extend(tmplist)
            count = 0
            tmplist = []
    if tmplist:
        phase_result = request_data(api, tmplist, parse_one_result)
        if phase_result:
            result.extend(phase_result)
            if batch_func:
                batch_func(phase_result)
        else:
            err_list.extend(tmplist)
    api.disconnect()
    return result, err_list


@spend_time
def get_spot(stocklist, ip, port, batch_func=None):
    hosts = search_best_tdx()
    hosts_cnt = len(hosts)
    num = len(stocklist) // hosts_cnt
    batchslist = []
    for i in range(hosts_cnt):
        batchslist.append([[stk for stk in stocklist[i*num: (i+1)*num]], hosts[i][2], hosts[i][3], batch_func])
    if len(stocklist) % hosts_cnt != 0:
        pos = num * hosts_cnt
        for i in range(hosts_cnt):
            batchslist[i][0].append(stocklist[pos])
            pos += 1
            if pos >= len(stocklist):
                break

    def do_inner(param):
        ret = inner_get_spot(param[0], param[1], param[2], param[3])
        return ret

    with futures.ThreadPoolExecutor() as executor:
        res = executor.map(do_inner, batchslist, timeout=10)

    result = []
    errors = []
    for batch_result in res:
        if batch_result[0]:
            result.extend(batch_result[0])
        if batch_result[1]:
            errors.extend(batch_result[1])
    return result, errors
