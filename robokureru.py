#!/usr/bin/env python

# Enters steamgifts, synchronises the wishlist, enters wishlist giveaways.  

# TODO
# 1. Check if we ever accidentally enter the 'featured' GA. listcropper should
# avoid this, but it seemed to fail the first time. You can test it with
# listcropper2.py

# 2. We could use cron instead, just like we run the finance updater. 
# THIS. The loop might be fucked up in some way. Sometimes it outputs instances 
# like crazy. Cron is probably much more reliable. We should make a proper loop though.
# Add it to the bash starting commands, with some delay, so it effectively runs at 
# startup. 
# Check if we can decouple this behaviour of the console from the actual terminal. 
# Having the screen 'cleared' is counterproductive when we can't log into the DE.

# 3. Move the log files (blist, WonGA) to a different folder. So it isn't so cluttered. 
# Actually, leave 'WonGA', as it's better if it's visible. Simply reorganise the 
# folders to hide all the 'development' clutter and the actually useful files. 

from splinter import Browser
import re
import os
import time
import mqgift as mq

wishlisturl = "http://www.steamgifts.com/giveaways/search?type=wishlist"
iwbegbot = Browser('firefox', 
                   profile='/home/tachibana/.mozilla/firefox/guu1k45t.begbot')
strike = 0  # Counts 'Not enough points' scenarios. Exits upon reaching '3'. 

# Sync Steam's wishlist with Steamgifts.
mq.syncwl(iwbegbot)

# Get all links from the wishlist page and store them.
manylinks = mq.getlinks(wishlisturl, iwbegbot)

# Find all links corresponding to giveaways.
regex = r'http://www.steamgifts.com/giveaway/[\d\w]{5}/[\d\w]*-?[\d\w]*-?[\d\w]*'
pattern = re.compile(regex)
foundall = re.findall(pattern, manylinks)

# Remove the spurious GA links. 
foundall = mq.listcropper(foundall)

# Creates a blacklist file, if there isn't one already. 
if os.path.exists('blist.txt'):
    blacklist = [line.rstrip('\n') for line in open('blist.txt')]
else:
    blacklist = [line.rstrip('\n') for line in open('blist.txt', 'w+')]

# Remove from 'foundall' the elements of 'blacklist'. 
foundall = [x for x in foundall if x not in blacklist]

# Enter the giveaways.
for i in foundall:
    if strike <3:
        strike, enteredga = mq.enterga(i, iwbegbot, strike)
        # Blacklist the link if we entered it, or if it ended. 
        if enteredga == True:
            blacklist.append(i)
        # TODO Fine tune the seconds that takes to enter. Try 1?
        time.sleep(2)
    else:
        break  # Exits the loop if we, apparently, don't have enough points. 

iwbegbot.quit()

# Overwrites blist.txt with the updated blacklist. 
blistobject = open('blist.txt', 'w')

for item in blacklist:
  blistobject.write("%s\n" % item)
blistobject.close() 

mq.giftreminder()  # Notifies us if there's unclaimed won games. 
print 'Process finished.'
