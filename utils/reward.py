import random

REWARD_LIST = [("一折", 0.1), ("第二件半價", 0.2), ("買一送一", 0.2), ("兩件77折", 0.5)]

def random_choice():
    val = random.random()
    cumulative_prob = [REWARD_LIST[0][1]]
    for r in REWARD_LIST[1:]:
        cumulative_prob.append(cumulative_prob[-1] + r[1])
    print(cumulative_prob)
    for i in range(len(cumulative_prob)-1):
        if val >= cumulative_prob[i] and val <= cumulative_prob[i+1]:
            return REWARD_LIST[i], i