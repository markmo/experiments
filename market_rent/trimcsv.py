import csv
import sys

f = sys.argv[1]
n = int(sys.argv[2])

reader = csv.DictReader(open(f))
writer = csv.DictWriter(open('trim_' + f, 'wb'), reader.fieldnames, quoting=csv.QUOTE_MINIMAL)
writer.writeheader()
for i in range(0, n):
    writer.writerow(reader.next())
