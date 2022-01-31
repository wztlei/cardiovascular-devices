from collections import defaultdict, Counter
from re import T
import matplotlib.pyplot as plt
import numpy as np

JOINED_DATA_FILE = 'joined_data.txt'

with open(JOINED_DATA_FILE) as file:
    read_header = False
    manufacturers = defaultdict(int)
    for line in file:
        if not read_header:
            read_header = True
            columns = line.strip().split('|')
            manufacturer_name_index = columns.index('MANUFACTURER_D_NAME')
        row = line.strip().split('|')
        manufacturers[row[manufacturer_name_index]] += 1

with open('manufacturers.txt', 'w') as file:

    total = sum(manufacturers.values())
    sorted_counts = sorted(manufacturers.items(), key=lambda kvp: kvp[1], reverse=True)

    for s in sorted_counts:
        file.write(f'{s[0]}|{s[1]}|{str(s[1]*100/total)[:5]}\n')
    # top_10_sum = sum([kvp[1] for kvp in sorted_counts[:1]])
    # print(top_10_sum / total)
