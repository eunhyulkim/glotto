from models import Wcode
from random import choices, choice
from sqlalchemy import desc



def convert_ranges(wcode):
    ranges = [0, 0, 0, 0, 0]
    for number in wcode.numbers:
        if number.value >= 40:
            ranges[4] += 1
        elif number.value >= 30:
            ranges[3] += 1
        elif number.value >= 20:
            ranges[2] += 1
        elif number.value >= 10:
            ranges[1] += 1
        else:
            ranges[0] += 1
    return ranges


def get_wseed(base=10, pattern_cnt=30,
              of_five=1, of_ten=1, over_ten=1,
              over_twenty=1, perfect=100, lucky_standard=12,
              lucky_zero_weight=0,lucky_one_weight=77
    ):
    wseed = {
        'base': base,
        'pattern_cnt': pattern_cnt,
        'of_five': of_five,
        'of_ten': of_ten,
        'over_ten': over_ten,
        'over_twenty': over_twenty,
        'perfect': perfect,
        'lucky_standard': lucky_standard,
        'lucky_zero_weight': lucky_zero_weight,
        'lucky_one_weight': lucky_one_weight
    }
    return wseed


def get_raw_weight_data(pattern_cnt):
    raw_result = []
    for i in range(45):
        raw_result += [[]]
    wcodes = Wcode.query.order_by(desc("no")).all()[:pattern_cnt]
    for wcode in wcodes:
        numbers = list(map(lambda x: x.value, wcode.numbers))
        numbers.append(wcode.bonus.value)
        for i in range(1, 46):
            if i in numbers:
                raw_result[i - 1].append(1)
            else:
                raw_result[i - 1].append(0)
    for i in range(45):
        raw_result[i].reverse()
    return raw_result


def get_mid_weight_data(raw_weight_data):
    ret_lists = []
    for number, rawdata in enumerate(raw_weight_data):
        result = []
        present = None
        index = None
        cnt = 0
        for i, data in enumerate(rawdata):
            if index is None:
                index = data
                cnt = 1
            elif i == len(rawdata) - 1:
                if index == data:
                    present = str(index) + "-" + str(cnt + 1)
                else:
                    result.append(str(index) + "-" + str(cnt))
                    present = str(data) + "-" + str(1)
            elif index == data:
                cnt += 1
            else:
                result.append(str(index) + "-" + str(cnt))
                index = data
                cnt = 1
        rlist = []
        ret_dict = {}
        if result:
            for j in sorted(list(set(result))):
                rlist.append(j + "-" + str(result.count(j)))
        ret_dict['number'] = number + 1
        ret_dict['present'] = present
        ret_dict['data'] = rlist
        ret_lists.append(ret_dict)
    return ret_lists


def ptow(output_percent):
    standard_percent = 14.28571
    weight = output_percent / standard_percent
    return weight


def get_high_weight_data(mid_weight_data, wseed):
    high_weight_data = []
    sp = 14.28571
    for weight_data in mid_weight_data:
        present = weight_data['present']
        datas = weight_data['data']
        # ret = None
        # print(weight_data['number'], weight_data['present'], weight_data['data'])
        # number = weight_data['number']
        ps = list(map(lambda x: int(x), present.split('-')))
        if datas:
            cnt = [0, 0]
            for data in datas:
                ds = list(map(lambda x: int(x), data.split('-')))
                if ps[0] == ds[0]:
                    if ps[1] <= ds[1]:
                        cnt[ps[0]] += (ds[1] - ps[1]) * ds[2]
                else:
                    cnt[(ps[0] + 1) % 2] += ds[2]
            if ps[1] >= wseed['lucky_standard'] or cnt[0] + cnt[1] == 0:
                if ps[0] == 0:
                    ret = ptow(wseed['lucky_zero_weight'])
                else:
                    ret = ptow(wseed['lucky_one_weight'])
            elif cnt[0] + cnt[1] <= 5:
                ret = ptow((round(cnt[1] / (cnt[0] + cnt[1]), 2) * wseed['of_five'])
                           + sp * (100 - wseed['of_five']) / 100)
            elif cnt[0] + cnt[1] <= 10:
                ret = ptow((round(cnt[1] / (cnt[0] + cnt[1]), 2) * wseed['of_ten'])
                           + sp * (100 - wseed['of_ten']) / 100)
            elif cnt[0] + cnt[1] <= 20:
                ret = ptow((round(cnt[1] / (cnt[0] + cnt[1]), 2) * wseed['over_ten'])
                           + sp * (100 - wseed['over_ten']) / 100)
            else:
                ret = ptow((round(cnt[1] / (cnt[0] + cnt[1]), 2) * wseed['over_twenty'])
                           + sp * (100 - wseed['over_twenty']) / 100)
        elif ps[0] == 1:
            ret = ptow(wseed['perfect'])
        else:
            ret = 0
        high_weight_data.append(round(ret * 100 + wseed['base'], 2))
    return high_weight_data


def get_side_calc_weight_data():
    wcodes = Wcode.query.order_by(desc("no")).all()[:10]
    last_numbers = list(map(lambda x: x.value, wcodes[0].numbers))
    total_numbers = []
    high_weight_data = []
    for wcode in wcodes:
        total_numbers += list(map(lambda x: x.value, wcode.numbers))
    for i in range(1, 46):
        if total_numbers.count(i) >= 3:
            if i in last_numbers:
                high_weight_data.append(1)
            else:
                high_weight_data.append(2)
        elif total_numbers.count(i) == 2:
            if i in last_numbers:
                high_weight_data.append(1.5)
            else:
                high_weight_data.append(2.5)
        elif total_numbers.count(i) == 1:
            if i in last_numbers:
                high_weight_data.append(2)
            else:
                high_weight_data.append(3)
        else:
            high_weight_data.append(5)
    return high_weight_data


def get_side_lucky_weight_data():
    wcodes = Wcode.query.order_by(desc("no")).all()[:10]
    last_numbers = list(map(lambda x: x.value, wcodes[0].numbers))
    total_numbers = []
    high_weight_data = []
    for wcode in wcodes:
        total_numbers += list(map(lambda x: x.value, wcode.numbers))
    for i in range(1, 46):
        if total_numbers.count(i) >= 3:
            if i in last_numbers:
                high_weight_data.append(1)
            else:
                high_weight_data.append(2)
        elif total_numbers.count(i) == 2:
            if i in last_numbers:
                high_weight_data.append(1.5)
            else:
                high_weight_data.append(3)
        elif total_numbers.count(i) == 1:
            if i in last_numbers:
                high_weight_data.append(2)
            else:
                high_weight_data.append(5)
        else:
            high_weight_data.append(1)
    return high_weight_data


def get_random_weight_data():
    wcode = Wcode.query.order_by(desc("no")).first()
    numbers = list(map(lambda x: x.value, wcode.numbers))
    numbers.append(wcode.bonus.value)
    high_weight_data = []
    for i in range(1, 46):
        if i in numbers:
            high_weight_data.append(1)
        else:
            high_weight_data.append(5)
    return high_weight_data


def get_weight(wseed, mode="default"):
    if mode == "default":
        raw_weight_data = get_raw_weight_data(wseed['pattern_cnt'])
        mid_weight_data = get_mid_weight_data(raw_weight_data)
        high_weight_data = get_high_weight_data(mid_weight_data, wseed)
    elif mode == "side-calc":
        high_weight_data = get_side_calc_weight_data()
    elif mode == "side-lucky":
        high_weight_data = get_side_lucky_weight_data()
    else:
        high_weight_data = get_random_weight_data()
    return high_weight_data


def get_games(ticket, wseed, mode):
    weight = get_weight(wseed, mode)
    games = []
    for i in range(ticket):
        numbers = list(range(1, 46))
        weights = weight.copy()
        game = []
        for j in range(6):
            index = choices(list(range(len(numbers))), weights, k=1)[0]
            game.append(numbers.pop(index))
            del weights[index]
        game.sort()
        games.append(game)
    return games


def init_seeds():
    """
    ret = base + percent
    :base: default 100
    :pattern_cnt: 30
    :of_five: * 1 ~ 100
    :of_ten: * 1 ~ 100
    :over_ten: * 1 ~ 100
    :over_twenty: * 1 ~ 100
    :perfect: * 100
    :lucky_standard: 5 ~
    :lucky_zero_weight: percent (default 14.28%)
    :lucky_one_weight: percent (default 14.28%)
    :return: dictonary
    """
    seeds = {}
    seeds['base_list'] = [40]
    seeds['pattern_cnt_list'] = [30]
    # seeds['pattern_cnt_list'] = [20, 30, 50]
    seeds['of_five_list'] = [50]
    # seeds['of_five_list'] = [10, 30, 50]
    seeds['of_ten_list'] = [70]
    # seeds['of_ten_list'] = [30, 50, 70]
    seeds['over_ten_list'] = [85]
    # seeds['over_ten_list'] = [50, 75, 100]
    seeds['over_twenty_list'] = [100]
    # seeds['over_twenty_list'] = [80, 100]
    seeds['perfect_list'] = [300]
    # seeds['perfect_list'] = [100, 200, 300, 500]
    seeds['lucky_standard_list'] = [10]
    # seeds['lucky_standard_list'] = [8, 10, 12]
    seeds['lucky_zero_weight_list'] = [0]
    # seeds['lucky_zero_weight_list'] = [0, 1, 3, 7]
    seeds['lucky_one_weight_list'] = [100]
    # seeds['lucky_one_weight_list'] = [50, 100, 200, 300]
    return seeds


def get_lotto(ticket, mode):
    seeds = init_seeds()
    # seed
    wseed = get_wseed(
        base=choice(seeds['base_list']),
        pattern_cnt=choice(seeds['pattern_cnt_list']),
        of_five=choice(seeds['of_five_list']),
        of_ten=choice(seeds['of_ten_list']),
        over_ten=choice(seeds['over_ten_list']),
        over_twenty=choice(seeds['over_twenty_list']),
        perfect=choice(seeds['perfect_list']),
        lucky_standard=choice(seeds['lucky_standard_list']),
        lucky_zero_weight=choice(seeds['lucky_zero_weight_list']),
        lucky_one_weight=choice(seeds['lucky_one_weight_list'])
    )
    # result
    games = get_games(ticket, wseed, mode)
    return games


def lotto():
    tickets = get_lotto(ticket=1, mode="default")
    tickets += get_lotto(ticket=1, mode="side-calc")
    tickets += get_lotto(ticket=1, mode="side-lucky")
    tickets += get_lotto(ticket=1, mode="random")
    return tickets