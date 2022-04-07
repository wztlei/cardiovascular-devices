from calendar import c
from collections import defaultdict
from os import listdir
from os.path import isfile, join
import pdb
from datetime import datetime

DEVICE_REPORT_PRODUCT_CODES = set([
	'MAF',
	'NIQ',
	'PNY',
])
JOINED_COLUMNS = [
    # 'DATE_OF_EVENT',
    'EVENT_TYPE',
    # 'DEVICE_REPORT_PRODUCT_CODE',
    # 'FOI_TEXT'
]
JOINED_COLUMN_INDEXES = {c: JOINED_COLUMNS.index(c) for c in JOINED_COLUMNS}
PRINT_INTERVAL = 100000
FOI_TEXT_SEARCH_STRINGS = [
    # 'PATIENT EXPIRED',
    # 'PATIENT DIED',
    # 'SUBSEQUENTLY EXPIRED',
    # 'DECEDENT',
    # 'TIME OF DEATH'
    # 'PATIENTS EXPIRED',
    # 'PATIENTS DIED',
    # 'TIME OF DEATH',
    # 'PATIENT LATER EXPIRED'
]
EVENT_TYPES = set([
    # 'M', 'IN'
    'D'
])

DEVICE_FILENAMES = [join('data/device-data', f) for f in listdir('data/device-data') if isfile(join('data/device-data', f))]
FOI_FILENAMES = [join('data/foi-data', f) for f in listdir('data/foi-data') if isfile(join('data/foi-data', f))]
MDR_FILENAMES = ['data/mdrfoiThru2020.txt']
OUTPUT_FILE = 'all-reports.txt'
OUTPUT_LOG = 'misreports_stats.txt'
DEVICE_FILENAMES.sort()
FOI_FILENAMES.sort()

joined_data = defaultdict(lambda: ['' for _ in range(len(JOINED_COLUMNS))])
stats = {
    'num_foi_text_mismatch': 0
}

def read_from_files(filenames, row_function, initial_read=False):
    for filename in filenames:
        print(f'Begin reading {filename}')

        with open(filename, encoding="latin-1") as file:
            read_header = False
            num_rows_parsed = 0

            for line in file:
                num_rows_parsed += 1
                should_print = num_rows_parsed % PRINT_INTERVAL == 0

                if should_print:
                    print(f'Read {num_rows_parsed} from {filename}')
                    print(f'Joined data length = {len(joined_data)}')

                row = line.strip().split('|')
                if not read_header:
                    column_indexes = {c: row.index(c) for c in row}
                    read_header = True
                    continue
                # if row[0] == '2737751':
                #     pdb.set_trace()
                row_function(row, column_indexes, initial_read)

def parse_device_row(row, column_indexes, initial_read):
    mdr_report_key = row[column_indexes['MDR_REPORT_KEY']]

    if (mdr_report_key in joined_data) == initial_read:
        return

    product_code_index = column_indexes['DEVICE_REPORT_PRODUCT_CODE']
    joined_product_code_index = JOINED_COLUMN_INDEXES['DEVICE_REPORT_PRODUCT_CODE']

    if product_code_index >= len(row):
        return

    device_report_product_code = row[product_code_index]

    if device_report_product_code in DEVICE_REPORT_PRODUCT_CODES:
        joined_data[mdr_report_key][joined_product_code_index] = device_report_product_code

def parse_foi_row(row, column_indexes, initial_read):
    mdr_report_key = row[column_indexes['MDR_REPORT_KEY']]

    # both true means key exists AND initial_read, so we skip since we already read key
    if (mdr_report_key in joined_data) == initial_read:
        return

    foi_text_index = column_indexes['FOI_TEXT']
    joined_foi_text_index = JOINED_COLUMN_INDEXES['FOI_TEXT']

    if foi_text_index >= len(row):
        return

    foi_text = row[foi_text_index].upper()
    joined_data[mdr_report_key][joined_foi_text_index] = foi_text   
    
    # for search_text in FOI_TEXT_SEARCH_STRINGS:
    #     if search_text in foi_text:
    #     if True:
    #         print(mdr_report_key)
    #         joined_data[mdr_report_key][joined_foi_text_index] = foi_text
    #         return

    # stats['num_foi_text_mismatch'] += 1
def parse_date(s, keep_month=False):
    month, day, year = s.split('/')
    if keep_month:
        return datetime(int(year), int(month), 1)
    return datetime(int(year), 1, 1)

def parse_mdr_row(row, column_indexes, initial_read):
    mdr_report_key = row[column_indexes['MDR_REPORT_KEY']]

    if (mdr_report_key in joined_data) == initial_read:
        return

    date_of_event_index = column_indexes['DATE_OF_EVENT']
    event_type_index = column_indexes['EVENT_TYPE']

    if date_of_event_index >= len(row):
        return
    if  event_type_index >= len(row):
        return

    event_type = row[event_type_index]
    date_of_event = row[date_of_event_index]
    if not date_of_event:
        return
    # date_of_event = parse_date(date_of_event, True)

    if event_type in EVENT_TYPES :
        joined_event_type_index = JOINED_COLUMN_INDEXES['EVENT_TYPE']
        # joined_date_of_event_index = JOINED_COLUMN_INDEXES['DATE_OF_EVENT']

        joined_data[mdr_report_key][joined_event_type_index] = event_type
        # joined_data[mdr_report_key][joined_date_of_event_index] = date_of_event

if __name__ == '__main__':
    read_from_files(MDR_FILENAMES, parse_mdr_row, True)
    # read_from_files(['test.txt'], parse_foi_row, True)
    # read_from_files(FOI_FILENAMES, parse_foi_row, False)

    # read_from_files(DEVICE_FILENAMES, parse_device_row, False)
    
    # read_from_files(DEVICE_FILENAMES, parse_device_row, True)

    # read_from_files(FOI_FILENAMES, parse_foi_row, False)
    
    for key in list(joined_data.keys()):
        if '' in joined_data[key]:
            del joined_data[key]
    
    print(f'Joined row count = {len(joined_data)}')

    # with open(OUTPUT_FILE, 'w') as file:
    #     file.write('|'.join(['MDR_REPORT_KEY'] + JOINED_COLUMNS))
    #     file.write('\n')
    #     for key in sorted(joined_data.keys()):
    #         row = [key] + joined_data[key]
    #         file.write(f'{"|".join(row)}\n')
# 









