#!/usr/bin/env python
"""Checks for won giveaways. Run it at a different frequency than robokureru.
e.g. once a day"""

from splinter import Browser
import mqgift as mq

# TODO Can't we define iwbegbot inside the mqgift?
iwbegbot = Browser('firefox', 
                   profile='/home/tachibana/.mozilla/firefox/guu1k45t.begbot')

mq.giftchecker(iwbegbot)
