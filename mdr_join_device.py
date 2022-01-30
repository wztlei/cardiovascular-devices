from collections import defaultdict
from os import listdir
from os.path import isfile, join


# Open the file
MDR_FILENAME = 'data/mdrfoiThru2020.txt'
DEVICE_FILENAMES = [f for f in listdir('data/device-data') if isfile(join('data/device-data', f))]
DEVICE_FILENAMES.sort()
assert len(DEVICE_FILENAMES) == 23, "Missing device file"

DEVICE_COLUMNS_OF_INTEREST = [
	# In device files
	'MDR_REPORT_KEY',
	'DEVICE_REPORT_PRODUCT_CODE',
	'DATE_RECEIVED',
	'BRAND_NAME',
	'GENERIC_NAME',
	'MANUFACTURER_D_NAME',
]
DEVICE_REPORT_PRODUCT_CODE_OUTPUT_COLUMN = DEVICE_COLUMNS_OF_INTEREST.index('DEVICE_REPORT_PRODUCT_CODE')

MDR_COLUMNS_OF_INTEREST = [
	# In MDR file
	'MDR_REPORT_KEY',
	'DATE_RECEIVED',
	'DATE_REPORT',
	'DATE_OF_EVENT',
	'DEVICE_DATE_OF_MANUFACTURE',
	'EVENT_TYPE',
]
joined_data = defaultdict(lambda: [None,[]])

DEVICE_REPORT_PRODUCT_CODES = set([
	'MAF',
	'NIQ',
	'PNY',
	'NIV'
])
ROWS_OUTPUT_FILE = 'filtered_rows.txt'
GROUPS_OUTPUT_FILE = 'count_by_group.txt'

# Iterate through all device files
num_device_mismatch = 0
num_device_match = 0

for filename in DEVICE_FILENAMES:
	print('Parsing', filename)
	with open(f'data/device-data/{filename}', encoding="latin-1") as devicefile:
		num_device_lines_parsed = 0
		read_header = False

		# Go through each line in the device file
		for line in devicefile:
			num_device_lines_parsed += 1
			row = line.strip().split('|')

			if num_device_lines_parsed % 100000 == 0:
				print('num_device_lines_parsed =', num_device_lines_parsed)

			if not read_header:
				read_header = True
				device_column_indexes = [row.index(c) for c in DEVICE_COLUMNS_OF_INTEREST]
				device_report_product_code_column = device_column_indexes[DEVICE_REPORT_PRODUCT_CODE_OUTPUT_COLUMN]
				continue

			mdr_report_key = row[0]

			# If the DEVICE_REPORT_PRODUCT_CODE column doesn't exist for the row
			if device_report_product_code_column >= len(row):
				num_device_mismatch += 1
				continue

			device = row[device_report_product_code_column]

			# We only want rows where the device is in the set DEVICE_REPORT_PRODUCT_CODES
			if device in DEVICE_REPORT_PRODUCT_CODES:
				selected_columns = [row[i] if i < len(row) else None for i in device_column_indexes]
				joined_data[mdr_report_key][1].append(selected_columns)
				num_device_match += 1
			else:
				num_device_mismatch += 1

print('num_device_match =', num_device_match)
print('num_device_mismatch =', num_device_mismatch)
# Open the MDR file
num_only_in_mdr = 0
num_missing_date_received = 0

with open(MDR_FILENAME, encoding="latin-1") as mdrfile:
	# Iterate through each line of the file
	num_mdr_lines_parsed = 0
	read_header = False

	for line in mdrfile:
		num_mdr_lines_parsed += 1
		row = line.strip().split('|') # Split each row by the | symbol

		if num_mdr_lines_parsed % 1000000 == 0:
			print('num_mdr_lines_parsed =', num_mdr_lines_parsed)

		if not read_header:
			read_header = True
			mdr_column_indexes = [row.index(c) for c in MDR_COLUMNS_OF_INTEREST]
			continue
		
		mdr_report_key = row[0] # Get the MDR Report Key (first column)

		if mdr_report_key in joined_data:
			if joined_data[mdr_report_key][0]:
				print(mdr_report_key, 'mdr_report_key appears twice in', mdrfile)
			else:
				selected_columns = [row[i] if i < len(row) else '' for i in mdr_column_indexes]
				joined_data[mdr_report_key][0] = selected_columns # Add the row to the end of the list
		else:
			num_only_in_mdr += 1

print('num_only_in_mdr =', num_only_in_mdr)
print('num_missing_date_received =', num_missing_date_received)
''''
mdr row device 1
mdr row device 2
...
'''
num_only_in_device = 0
num_rows_written = 0

groups = defaultdict(int)

with open(ROWS_OUTPUT_FILE, 'w') as file:
	file.write('|'.join(MDR_COLUMNS_OF_INTEREST + DEVICE_COLUMNS_OF_INTEREST))
	file.write('\n')
	date_of_event_index = MDR_COLUMNS_OF_INTEREST.index('DATE_OF_EVENT')
	product_code_index = DEVICE_COLUMNS_OF_INTEREST.index('DEVICE_REPORT_PRODUCT_CODE')
	event_type_index = MDR_COLUMNS_OF_INTEREST.index('EVENT_TYPE')

	for mdr_report_key in joined_data:
		mdr_row, device_rows = joined_data[mdr_report_key]

		if mdr_row is None:
			num_only_in_device += 1
			continue

		date_of_event = mdr_row[date_of_event_index].split('/')
		if len(date_of_event) == 3:
			month, day, year = date_of_event
			assert len(month) == 2
			assert len(day) == 2
			assert len(year) == 4
		else:
			month, day, year = 'Unknown', 'Unknown', 'Unknown'
		
		product_code = device_rows[0][product_code_index]
		event_type = mdr_row[event_type_index]
		group = (f'{year}/{month}', product_code, event_type)
		groups[group] += len(device_rows)
		
		for device_row in device_rows:
			num_rows_written += 1
			file.write('|'.join(mdr_row + device_row))
			file.write('\n')
print('num_only_in_device =', num_only_in_device)
print('num_rows_written =', num_rows_written)

with open(GROUPS_OUTPUT_FILE, 'w') as file:
	file.write('YEAR/MONTH|DEVICE_REPORT_PRODUCT_CODE|EVENT_TYPE\n')

	for group in sorted(groups.keys()):
		count = groups[group]
		file.write('|'.join(group))
		file.write('|' + str(count) + '\n')

