from collections import defaultdict
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
JOINED_DATA_FILE = 'joined_data.txt'
TOP_X = 10
MOVING_AVERAGE_MONTHS = 12

def parse_mmddyyy(date):
    parts = date.strip().split('/')
    if len(parts) != 3:
        return None
    month, day, year = parts

    if len(month) != 2 or len(day) != 2 or len(year) != 4:
        return None
    return datetime(int(year), int(month), 1)
def moving_average(a, n=MOVING_AVERAGE_MONTHS) :
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n

manufacturer_groups = defaultdict(lambda: defaultdict(int))

with open(JOINED_DATA_FILE) as file:
    read_header = False
    manufacturer_count = defaultdict(int)
    for line in file:
        if not read_header:
            read_header = True
            columns = line.strip().split('|')
            manufacturer_name_index = columns.index('MANUFACTURER_D_NAME')
            date_of_event_index = columns.index('DATE_OF_EVENT')
        row = line.strip().split('|')
        
        manufacturer_name = row[manufacturer_name_index]
        date_of_event = parse_mmddyyy(row[date_of_event_index])

        manufacturer_count[manufacturer_name] += 1
        if date_of_event and date_of_event >= datetime(2000, 1, 1):
            manufacturer_groups[manufacturer_name][date_of_event] += 1

sorted_counts = sorted(manufacturer_count.items(), key=lambda kvp: kvp[1], reverse=True)
top_x_manufacturers = [m[0] for m in sorted_counts[:TOP_X]]
for m in top_x_manufacturers:
    data = sorted(manufacturer_groups[m].items(), key=lambda kvp: kvp[0])
    x = [kvp[0] for kvp in data]
    y = [kvp[1] for kvp in data]
    y = moving_average(y)
    print(y.shape)
    x = x[:len(y)]
    plt.plot(x, y, label=m)
plt.legend()
plt.show()
# with open('manufacturers.txt', 'w') as file:

#     total = sum(manufacturers.values())
#     sorted_counts = sorted(manufacturers.items(), key=lambda kvp: kvp[1], reverse=True)

#     for s in sorted_counts:
#         file.write(f'{s[0]}|{s[1]}|{str(s[1]*100/total)[:5]}\n')
    # top_10_sum = sum([kvp[1] for kvp in sorted_counts[:1]])
    # print(top_10_sum / total)
