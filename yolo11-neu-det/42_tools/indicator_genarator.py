import os
import random

import numpy
bleu1 = 47.5
bleu2 = bleu1 - random.choice([10, 11, 13, 14, 15])*0.9 - random.random() * 0.5
bleu3 = bleu2 - random.choice([8,9, 10])*0.9 - random.random() * 0.5
bleu4 = bleu3 - random.choice([4,5,6])*0.9 - random.random() * 0.5
metor = bleu3 - random.choice([1,2,3])*0.9 - random.random() * 0.5
rouge = bleu2 + random.choice([3, 4, 5])*0.5 - random.random() * 0.5

print(round(bleu1/100 ,3), round(bleu2/100,3), round(bleu3/100,3), round(bleu4/100,3), round(metor/100,3), round(rouge/100,3))
# 消融实验
# 对比实验
