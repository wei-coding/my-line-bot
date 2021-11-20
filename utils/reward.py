import random

REWARD_LIST = [
    ("憑此木牌，購一送一", 0.01),
    ("一日往生體驗服務（一次）", 0.02),
    ("往生堂品牌桃級棺材七九折", 0.04),
    ("往生堂品牌木級棺材一個", 0.08),
    ("往生堂整套服務九五折（限一人）", 0.16),
    ("往生堂服務預約免手續費（一次）", 0.32),
    ("萬民堂蝦餃五折折價卷（請至往生堂領取）", 0.37)
]

def random_choice():
    val = random.random()
    cumulative_prob = [REWARD_LIST[0][1]]
    for r in REWARD_LIST[1:]:
        cumulative_prob.append(cumulative_prob[-1] + r[1])
    print(cumulative_prob)
    for i in range(len(cumulative_prob)-1):
        if val >= cumulative_prob[i] and val <= cumulative_prob[i+1]:
            return REWARD_LIST[i], i