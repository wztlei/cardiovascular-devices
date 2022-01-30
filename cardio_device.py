from collections import defaultdict

joined_data = defaultdict(list)

# Open the file
MDR_FILENAME = 'end100mdrfoiThru2020.txt'
DEVICE_FILENAMES = [
	('end100device2020.txt', False)
]
MDR_HEADER_FILENAME = 'headingmdrfoiThru2020.txt'
DEVICE_HEADER_FILENAME = 'headingdevice.txt'
# DEVICE_NAMES = set([
# 	'STENT, CORONARY',
# 	'CORONARY DRUG-ELUTING STENT',
# 	'ABSORBABLE CORONARY DRUG-ELUTING STENT',
# 	'CORONARY COVERED STENT'
# ])
DEVICE_REPORT_PRODUCT_CODES = set([
	'MAF',
	'NIQ',
	'PNY',
	'NIV'
])
ROWS_OUTPUT_FILE = 'rows_output.txt'
GROUPS_OUTPUT_FILE = 'groups_output.txt'

with open(MDR_HEADER_FILENAME) as header_file:
	for row in header_file:
		mdr_column_names = row.strip().split('|')
		event_type_column = mdr_column_names.index('EVENT_TYPE')
		break

with open(DEVICE_HEADER_FILENAME) as header_file:
	for row in header_file:
		device_column_names = row.strip().split('|')
		product_code_column = device_column_names.index('DEVICE_REPORT_PRODUCT_CODE')
		date_received_column = device_column_names.index('DATE_RECEIVED')

		break

# print(mdr_column_names)
# print(device_column_names)


# Iterate through all device files
num_device_mismatch = 0
num_device_match = 0

for device_filename in DEVICE_FILENAMES:
	filename, has_header = device_filename
	print('parsing', filename)
	with open(filename) as devicefile:
		read_header = False
		num_device_lines_parsed = 0

		for line in devicefile:
			if has_header and not read_header:
				read_header = True
				continue
			num_device_lines_parsed += 1
			if num_device_lines_parsed % 100000 == 0:
				print('num_device_lines_parsed =', num_device_lines_parsed)
			row = line.strip().split('|')
			mdr_report_key = row[0]

			if mdr_report_key in joined_data:
				print(mdr_report_key, 'mdr_report_key appears twice in', filename)
				continue

			if product_code_column >= len(row):
				num_device_mismatch += 1
				continue
			device = row[product_code_column]

			if device in DEVICE_REPORT_PRODUCT_CODES:
				# mdr_report_keys in both
				joined_data[mdr_report_key].append(row)
				num_device_match += 1
			else:
				num_device_mismatch += 1

print('num_device_match =', num_device_match)
print('num_device_mismatch =', num_device_mismatch)
# Open the MDR file
num_only_in_mdr = 0
num_missing_date_received = 0
with open(MDR_FILENAME) as mdrfile:
	# Iterate through each line of the file
	num_mdr_lines_parsed = 0
	
	for line in mdrfile:
		# >= Jan 1 2011
		num_mdr_lines_parsed += 1

		if num_mdr_lines_parsed % 1000000 == 0:
			print('num_mdr_lines_parsed =', num_mdr_lines_parsed)
		row = line.strip().split('|') # Split each row by the | symbol
		
		# if date_received_column >= len(row):
		# 	num_missing_date_received += 1
		# 	continue
		# if row[date_received_column] < '2011/01/01':
		# 	continue
		
		mdr_report_key = row[0] # Get the MDR Report Key (first column)
		if mdr_report_key in joined_data:
			if len(joined_data[mdr_report_key]) >= 2:
				print(mdr_report_key, 'mdr_report_key appears twice in', mdrfile)
			else:
				joined_data[mdr_report_key].append(row) # Add the row to the end of the list
		else:
			num_only_in_mdr += 1
print('num_only_in_mdr =', num_only_in_mdr)
print('num_missing_date_received =', num_missing_date_received)

num_only_in_device = 0
num_rows_written = 0

groups = defaultdict(int)

with open(ROWS_OUTPUT_FILE, 'w') as file:
	file.write('|'.join(device_column_names + mdr_column_names))
	file.write('\n')

	for mdr_report_key in joined_data:
		rows = joined_data[mdr_report_key]

		if len(rows) == 1:
			num_only_in_device += 1
			continue

		device_row, mdr_row = rows[:2]
		num_rows_written += 1
		year_month = device_row[date_received_column][:-3] if date_received_column < len(device_row) else 'NULL'
		product_code = device_row[product_code_column] if product_code_column < len(device_row) else 'NULL'
		event_type = mdr_row[event_type_column] if event_type_column < len(mdr_row) else 'NULL'
		group = (year_month, product_code, event_type)
		groups[group] += 1
		

		file.write('|'.join(rows[0] + rows[1]))
		file.write('\n')
print('num_only_in_device =', num_only_in_device)
print('num_rows_written =', num_rows_written)

with open(GROUPS_OUTPUT_FILE, 'w') as file:
	file.write('YEAR/MONTH|PRODUCT_CODE|EVENT_TYPE\n')

	for group in sorted(groups.keys()):
		count = groups[group]
		file.write('|'.join(group))
		file.write('|' + str(count) + '\n')

