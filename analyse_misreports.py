

from cProfile import label
from collections import defaultdict
from datetime import datetime
import matplotlib.pyplot as plt

def read_from_files(filenames, row_function, reports_by_group, group_columns=None):
    for filename in filenames:
        print(f'Begin reading {filename}')

        with open(filename, encoding="latin-1") as file:
            read_header = False
            num_rows_parsed = 0

            for line in file:
                num_rows_parsed += 1
                # should_print = num_rows_parsed % PRINT_INTERVAL == 0

                # if should_print:
                #     print(f'Read {num_rows_parsed} from {filename}')
                    # print(f'Joined data length = {len(joined_data)}')

                row = line.strip().split('|')
                if not read_header:
                    column_indexes = {c: row.index(c) for c in row}
                    read_header = True
                    continue
                # if row[0] == '2737751':
                #     pdb.set_trace()
                row_function(row, column_indexes, reports_by_group, group_columns)

def generate_datetimes(include_month=False):
    datetimes = []

    for year in range(2011, 2021):
        datetimes.append(datetime(year, 1, 1))

        if include_month:
            for month in range(2, 13):
                datetimes.append(datetime(year, month, 1))

    return datetimes

def parse_date(s, keep_month=False):
    month, day, year = s.split('/')
    if keep_month:
        return datetime(int(year), int(month), 1)
    return datetime(int(year), 1, 1)


def parse_report_row(row, column_indexes, reports_by_group, group_columns=None):
    date_of_event = row[column_indexes['DATE_OF_EVENT']]
    date_of_event = parse_date(date_of_event)
    if not group_columns:
        group = 'All Reports'
    else:
        group = ', '.join([row[column_indexes[c]] for c in group_columns])

    if date_of_event >= datetime(2010, 1, 1):
        reports_by_group[group][date_of_event] += 1


def add_graph(reports_by_group):
    for group in reports_by_group:
        dates = generate_datetimes()
        reports_by_date = reports_by_group[group]
        for d in dates:
            if d not in reports_by_date:
                reports_by_date[d] = 0
            
        # reports_by_date = sorted(reports_by_date.items(), key=lambda kvp: kvp[0])
        
        
        x, y = zip(*sorted(reports_by_date.items()))
        plt.plot(x, y, label=group)

def add_percentage_graph(subset_reports_by_group, reports_by_group):
    percent_by_group = defaultdict(lambda: defaultdict(int))
    dates = generate_datetimes()

    for group in subset_reports_by_group:
        subset_reports_by_date = subset_reports_by_group[group]
        reports_by_date = reports_by_group[group]

        for d in dates:
            if d in subset_reports_by_date and d in reports_by_date:
                percent_by_group[group][d] = subset_reports_by_date[d] / reports_by_date[d] * 100
            else:
                percent_by_group[group][d] = 0
            
        # reports_by_date = sorted(reports_by_date.items(), key=lambda kvp: kvp[0])
        
        print(percent_by_group[group])
        x, y = zip(*percent_by_group[group].items())
        plt.plot(x, y, label=f'% Misreports of {group}')

misreports_by_group = defaultdict(lambda: defaultdict(int))
reports_by_group = defaultdict(lambda: defaultdict(int))
read_from_files(['misreports.txt'], parse_report_row, misreports_by_group)
# read_from_files(['misreports.txt'], parse_report_row, misreports_by_group, ['EVENT_TYPE'])
# read_from_files(['misreports.txt'], parse_report_row, misreports_by_group, ['DEVICE_REPORT_PRODUCT_CODE'])

read_from_files(['all-reports.txt'], parse_report_row, reports_by_group)

# add_graph(misreports_by_group)
add_percentage_graph(misreports_by_group, reports_by_group)
print(sum(misreports_by_group['All Reports'].values()))
print(sum(reports_by_group['All Reports'].values()))
plt.legend()
plt.show()


