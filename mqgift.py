"""This module allows to automatically enter giveaways from 'Steamgifts.com for 
games that are on your wishlist."""

from splinter import Browser
import re
import os
import time
import subprocess
from colorama import init, Fore, Back, Style
init()  # Allows it to be used on Windows OSs.

def getlinks(url, browser):
    """Gets all the links from the input url. Returns them as a single string, each 
    one in a newline."""
    
    # Load new profile. No clutter, just signed up on steamgifts. 
    browser.visit(url)
    
    # Get all links in this page
    # TODO: I don't know how this works. Research it!
    links = [a['href'] for a in browser.find_by_tag('a')]

    # Writes the link list directly to a string. 
    # http://stackoverflow.com/questions/4435169/good-way-to-append-to-a-string
    string = ''
    for item in links:
        string += str(item) + '\n'

    return string


def enterga(url, browser, failcounter):
#def enterga(url, browser):
    """Loads the giveaway url and clicks the button, entering it."""
    
    entered = False  # Records if the GA has already been entered. 
    browser.visit(url)  # Loads the page.

    print
    print 'Game:', (Fore.CYAN + Style.DIM + browser.title + Fore.RESET)
    print 'URL:', browser.url

    # 'Entry giveaway' button visible. 
    c1 = browser.find_by_css('div.sidebar__entry-insert')
    # 'Not enough points' button visible.
    c2 = browser.find_by_css('div.sidebar__error.is-disabled')

    if c1:
        # Find and click the 'Enter giveaway' button via CSS. 
        # TODO How to handle the error of 'element not visible' exception?
        #http://stackoverflow.com/questions/4990718/python-about-catching-any-exception
        try:
            c1.click()
            print (Fore.GREEN + Style.DIM + 'Entered the giveaway.' + Fore.RESET)
            entered = True
        #except ElementNotVisibleException:
        # NOTE: this doesn't work. It stops the program. 
        except:
            #print 'Couldn\'t enter the giveaway. Already entered, perhaps.'
            print (Fore.YELLOW + Style.DIM + 'Couldn\'t enter the giveaway. Already entered, perhaps.' + Fore.RESET)
            # TODO
            # Remove said links from the link list. (Better, add it to the black list).
            entered = True
    elif c2:
        #print 'Not enough points!'
        print (Fore.YELLOW + Style.DIM + 'Not enough points.' + Fore.RESET)

        failcounter += 1
        #print 'The fail counter is', failcounter
    else:
        #print
        #print 'Apparently, the giveaway ended.'
        print (Fore.YELLOW + Style.DIM + 'The giveaway ended or you\'re not signed in Steamgifts.' + Fore.RESET)
        # Url to be removed/blacklisted, despite not having 'entered', it's impossible now. 
        entered = True
    return (failcounter, entered)


def rmdual(seq):
    """Removes duplciates from list, keeping the order."""
    # http://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-in-python-whilst-preserving-order
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

def syncwl(browser):
    """Syncs Steam's account with Steamgifts, updating the wishlist."""
    syncurl = "http://www.steamgifts.com/account/profile/sync"
    browser.visit(syncurl)
    csync = browser.find_by_css('div.form__sync-default')
    try:
        csync.click()
        time.sleep(2)  # TODO Test 1 second instead. 
        print
        print 'Wishlist synchronised.'
        print
    except:
        print
        print (Fore.RED + Style.DIM + 'Couldn\'t synchronise wishlist.' + Fore.RESET)
        print
    return


def listcropper(list0):
    """Shortens a list to a certain length trimming the beginning. Used to avoid 
    the 'featured' GAs that appear also in the wishlist page of steamigifts."""
    
    # Remove first the spurious giveaway. The wishlist page always features 
    # the giveaway that's going to end sooner, we want to remove that. 
    del list0[0:2]  # It's duplicated (image and text). 
    # TODO If we use del after removing the duplicates we would only need to 
    # remove one! Test that!
    
    # NOTE The second one should be enough. 
    # Strip removes the characters from the beginning or the end of the string. 
    # re.sub simply replaces them, but it's slower than "string.replace('\n','')" 
    list0 = [line.strip('\n') for line in list0]
    list0 = [re.sub('\n', '', line) for line in list0]
    #list0 = mq.rmdual(list0)  # Removes duplicates, keeps the original order. 
    list0 = rmdual(list0)  # Removes duplicates, keeps the original order. 

    # Remove the 'Featured Giveaways', since there's only 50 GAs per wishlist page.
    # NOTE It worked. Maybe it only works sometimes. Only time and testing will tell.
    # It works well, except when the game you're after belongs to both groups. i.e.
    # 'Featured' and 'wishlist'.
    # You can test with listcropper2.py
    # TODO Make another function out of this. 
    while len(list0)>50:
        del list0[0]
    return list0


def giftchecker(browser):
    """Checks if we have won any giveaways, then creates 'WonGA.txt', containing 
    the won game's name. It doesn't notify the user (that's 'giftreminder's job)
    ."""
    wongaurl = "http://www.steamgifts.com/giveaways/won"
    soundpath = '-q /media/01/06-KoEC/Programming/python/OwnProjects/Scrapping/roboshinobu/sounds/'
    soundsystem = soundpath + 'YMHTTPG.ogg'

    # Get all links from the won GAs page and store them.
    manylinks = getlinks(wongaurl, browser)
    browser.quit()

    # Find all links corresponding to giveaways.
    regex = r'http://www.steamgifts.com/giveaway/[\d\w]{5}/[\d\w]*-?[\d\w]*-?[\d\w]*'
    pattern = re.compile(regex)
    foundall = re.findall(pattern, manylinks)

    # NOTE The second one should be enough. 
    # Strip removes the characters from the beginning or the end of the string. 
    # re.sub simply replaces them, but it's slower than "string.replace('\n','')"
    foundall = [line.strip('\n') for line in foundall]  # Comment this one out. 
    foundall = [re.sub('\n', '', line) for line in foundall]

    foundall = rmdual(foundall)  # Removes duplicates, keeps original order.

    # Creates a blacklist file, if there isn't one already. 
    if os.path.exists('wonblist.txt'):
        blacklist = [line.rstrip('\n') for line in open('wonblist.txt')]
    else:
        blacklist = [line.rstrip('\n') for line in open('wonblist.txt', 'w+')]

    # Remove from 'foundall' the elements of 'blacklist'. 
    foundall = [x for x in foundall if x not in blacklist]

    # Detects if a new game has been won.
    if foundall:
        fileobject = open('WonGa.txt', 'w')
        for item in foundall:
            fileobject.write("%s\n" % item)  
        fileobject.close()
        # Check if the list comprehension works well. It should. 
        """
        for i in foundall:
            blacklist.append(i)
        """
        [blacklist.append(i) for i in foundall]

    # Overwrites wonblist.txt with the updated blacklist. 
    blistobject = open('wonblist.txt', 'w')
    for item in blacklist:
        blistobject.write("%s\n" % item)
    blistobject.close()
    return

def giftreminder():
    """Checks if we have unclaimed won giveaways. It simply checks for 
    'WonGA.txt's existence, then reminds you with text and sound. Delete the
    'WonGA.txt' file once you've claimed your gift."""

    regexshort = r'http://www.steamgifts.com/giveaway/[\d\w]{5}/'
    soundpath = '-q /media/01/06-KoEC/Programming/python/OwnProjects/Scrapping/roboshinobu/sounds/'
    soundsystem = soundpath + 'YMHTTPG.ogg'  # Kerrigan: You may have time to play games. 

    if os.path.exists('WonGa.txt'):    
        # http://stackoverflow.com/questions/8369219/how-do-i-read-a-text-file-into-a-string-variable-in-python
        with open ("WonGa.txt", "r") as myfile:
            game = myfile.read()
            game = re.sub(regexshort, '', game)  # Extracts name from the url. 
            game = re.sub('-', ' ', game)
            #print 'You\'ve won a game! %s' %game.title()  # Capitalises name.
            print(Fore.GREEN + "You " + Fore.BLACK + Back.GREEN + "won" + Style.RESET_ALL + Fore.GREEN + " a game!" + Style.RESET_ALL  + Fore.CYAN + " %s" + Fore.RESET) %game.title()
            subprocess.check_output("play " + soundsystem, shell=True)
    return
