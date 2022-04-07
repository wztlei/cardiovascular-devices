from collections import defaultdict
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

JOINED_DATA_FILE = 'joined_data.txt'
TOP_X = 10
MOVING_AVERAGE_NUMBER = 365
START_DATE_CUTOFF = datetime(2011, 1, 1)
AGGREGATE_INTERVAL = 'month'
def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

def parse_mmddyyy(date, erase_day=False):
    parts = date.strip().split('/')
    if len(parts) != 3:
        return None
    month, day, year = parts

    if len(month) != 2 or len(day) != 2 or len(year) != 4:
        return None
    return datetime(int(year), int(month), 1 if erase_day else int(day))
def moving_average(a, n=MOVING_AVERAGE_NUMBER) :
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n

def moving_sum(a, n=MOVING_AVERAGE_NUMBER) :
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:]

manufacturer_groups = defaultdict(lambda: defaultdict(int))
total = 0 

with open(JOINED_DATA_FILE) as file:
    read_header = False
    manufacturer_count = defaultdict(int)
    for line in file:
        if not read_header:
            read_header = True
            columns = line.strip().split('|')
            manufacturer_name_index = columns.index('EVENT_TYPE')
            product_code_index = columns.index('DEVICE_REPORT_PRODUCT_CODE')
            date_of_event_index = columns.index('DATE_OF_EVENT')
            continue
        row = line.strip().split('|')
        
        product_code = row[product_code_index]
        manufacturer_name = row[manufacturer_name_index]
        criteria = ', '.join([manufacturer_name, product_code])

        date_of_event = parse_mmddyyy(row[date_of_event_index], erase_day=True)
        total += 1
        if date_of_event and date_of_event >= START_DATE_CUTOFF and product_code in ('NIQ') :
            manufacturer_count[criteria] += 1
            manufacturer_groups[criteria][date_of_event] += 1
sorted_counts = sorted(manufacturer_count.items(), key=lambda kvp: kvp[1], reverse=True)
top_x_manufacturers = [m[0] for m in sorted_counts[:10]]

for m in top_x_manufacturers:
    dates = manufacturer_groups[m].keys()
    category_count = manufacturer_count[m]
    first_date = max(START_DATE_CUTOFF, min(dates))
    last_date = max(dates)
    
    # for date in daterange(first_date, last_date):
    #     if date not in manufacturer_groups[m]:
    #         manufacturer_groups[m][date] = 0

    data = sorted(manufacturer_groups[m].items(), key=lambda kvp: kvp[0])
    
    # x = [kvp[0].toordinal()-START_DATE_CUTOFF.toordinal() for kvp in data]
    x = [kvp[0] for kvp in data]

    y = [kvp[1] for kvp in data]
    print(x)
    # print(m, sum(y))    
    # y = moving_sum(y, 7)
    # max_y = max(y)
    # y = [val/max_y*100 for val in y]
    # percent_change = np.diff(y) / y[:-1] * 100
    # percent_change = moving_sum(percent_change, 30)
    # slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
    # predict_y = intercept + slope * np.array(x)

    # plt.scatter(x[:len(y)], y, label=f'{m}, {category_count}')
    plt.plot(x[:len(y)], y, label=m)
    # plt.plot(x, predict_y, label=f'{m}, r={r_value:.2f}, m={slope:.2f}, b={intercept:.2f}')

    # plt.plot(x[:len(percent_change)], percent_change, label=f'{m}, % change')
plt.legend()
plt.show()
# with open('manufacturers.txt', 'w') as file:

#     total = sum(manufacturers.values())
#     sorted_counts = sorted(manufacturers.items(), key=lambda kvp: kvp[1], reverse=True)

#     for s in sorted_counts:
#         file.write(f'{s[0]}|{s[1]}|{str(s[1]*100/total)[:5]}\n')
    # top_10_sum = sum([kvp[1] for kvp in sorted_counts[:1]])
    # print(top_10_sum / total)
