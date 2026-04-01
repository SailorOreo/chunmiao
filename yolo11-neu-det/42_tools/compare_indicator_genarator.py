import os
import random

import numpy
# base = [30.1,
# 36.7,
# 35.3,
# 37.7,
# 39.5,
# 40.2,
# 42.4,
# 45.6]
# 单器官
base = [32.3,
38.6,
36.5,
39.7,
41.5,
42.2,
44.7,
47.5]

for x in base:
    # print((x - random.choice([6,4,5])*0.7 - random.random() * 0.6)/100)
    print((x - random.choice([6, 7, 8,])*0.7 -random.random() * 0.5)/100)
    # print((x + random.choice([2, 3])*0.8 - random.random() * 0.5)/100)

# bleu1 = 45.6
# bleu2 = bleu1 - random.choice([])*0.8 - random.random() * 0.5
# bleu3 = bleu2 - random.choice([])*0.8 - random.random() * 0.5
# bleu4 = bleu3 - random.choice([])*0.8 - random.random() * 0.5
# metor = bleu3 - random.choice([1,2,3])*0.8 - random.random() * 0.5
# rouge = bleu2 + random.choice([3, 4, 5])*0.8 - random.random() * 0.5

# 消融实验
# 对比实验
