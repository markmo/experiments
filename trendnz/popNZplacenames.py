# -*- coding: utf-8 -*-

import csv

reader = csv.reader(open('namedata.txt', 'rb'), delimiter="`")
writer = csv.writer(open('/Users/markmo/Dev/data/nltk_data/corpora/gazetteers/nzplacenames.txt', 'wb'), quoting=csv.QUOTE_MINIMAL)
reader.next()
for line in reader:
    for p in line[1].split('/'):
        writer.writerow([' '.join([w.capitalize() for w in p.split()])])
