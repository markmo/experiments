# -*- coding: utf-8 =*-

import codecs
# import json
import sys
import twitter

HASHTAG = sys.argv[1]
PAGES = int(sys.argv[2])
RPP = int(sys.argv[3])

# http://search.twitter.com/search.json?pages=15&rpp=100&q=%23webstock&show_user=true
# Twitter will only return a max of approx. 1500 results (rpp * pages),
# showing a mix of recent and popular results
t = twitter.Twitter(domain='search.twitter.com')

search_results = []
for page in range(1, PAGES):
    search_results.append(t.search(q=HASHTAG, rpp=RPP, show_user=False))

# print json.dumps(tweets, sort_keys=True, indent=1)
f = codecs.open('./output/tweets', 'w', encoding="UTF-8")

count = 0
for result in search_results:
    for t in result['results']:
        count += 1
        f.write(''.join([
                t['from_user_id_str'], '\t',
                t['from_user'], '\t',
                ' '.join(t['text'].splitlines()), '\n' # creates a list from text breaking at line boundaries, and joins them back up using the object of the join method as the delimiter
                ]))

print "Wrote %i records." % (count)
f.close()
