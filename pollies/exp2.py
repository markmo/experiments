# -*- coding: utf-8 -*-

import sys
import time
import cPickle as pickle
import twitter
from twitter.oauth_dance import oauth_dance

# Run python exp2.py johnkeypm from the command line

consumer_key = 'UkmiRFjbevouUfXh36sVg'
consumer_secret = '7bMMc3nBhHI7JjIMep3Xf7Dkl6w8ImIH7WsskgogY'

SCREEN_NAME = sys.argv[1]
friends_limit = 10000

(oauth_token, oauth_token_secret) = oauth_dance('Experiment1', consumer_key, consumer_secret)
t = twitter.Twitter(domain='api.twitter.com', api_version='1',
                    auth=twitter.oauth.OAuth(oauth_token, oauth_token_secret,
                    consumer_key, consumer_secret))

ids = []
wait_period = 2 # secs
cursor = -1

while cursor != 0:
    if wait_period > 3600: # 1 hour
        print 'Too many retries. Saving partial data to disk and exiting'
        f = file('%s.friend_ids' % str(cursor), 'wb')
        pickle.dump(ids, f)
        f.close()
        exit()
        
    try:
        response = t.friends.ids(screen_name=SCREEN_NAME, cursor=cursor)
        ids.extend(response['ids'])
        print ids
        wait_period = 2
    except twitter.api.TwitterHTTPError, e:
        if e.e.code == 401:
            print 'Encountered 401 Error (Not Authorized)'
            print 'User %s is protecting their tweets' % (SCREEN_NAME, )
        elif e.e.code in (502, 503):
            print 'Encountered %i Error. Trying again in %i seconds' % (e.e.code,
                    wait_period)
            time.sleep(wait_period)
            wait_period *= 1.5
            continue
        elif t.account.rate_limit_status()['remaining_hits'] == 0:
            status = t.account.rate_limit_status()
            now = time.time() # UTC
            when_rate_limit_resets = status['reset_time_in_seconds'] # UTC
            sleep_time = when_rate_limit_resets - now
            print 'Rate limit reached. Trying again in %i seconds' % (sleep_time, )
            time.sleep(sleep_time)
            continue
            
    cursor = response['next_cursor']
    print 'Fetched %i ids for %s' % (len(ids), SCREEN_NAME)
    if len(ids) >= friends_limit:
        break

print ids
