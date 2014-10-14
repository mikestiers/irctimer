# History:
# 10-03-2014
#  v0.1 development start
# 10-11-2014
#  v0.5 initial release
# 10-14-2014
#  v0.6
#   bugfix, check if already connected upon plugin load (discovered infolist_get.  neat)
#   bugfix, use HOME environment variable for timer path
# 10-14-2014
#  v0.7
#   bar now displays friendly timer in days (write_value_friendly)
#
# Todo - high priority:
#  make bar item appear automatically (/set weechat.bar.status.items irctimer)
#  timer still counts if you go into standby
#
# Todo - low priority:
#  if connected to multiple servers and then disconnect from one, the timer stops.  really need an isConnected() or += connectedState
#  maybe check irctimer.txt for correct formatting.  probably not worth it.
#  find out why i lose a few seconds every disconnect
#  with an isConnected() i could probably eliminate serverConnected, serverDisconnected, and move a lot into calculateTimer()
#  last_reset_posix = time.mktime(last_reset_ctime)
#
# Learning Opportunities:
#  do i need global in front of all these things?
#  how to get dot completion support for weechat
#  figure out what "data, cals" or "data, buffer, args" is doing
#  find out what a "callback" is for
#  understand the infolist iteration / while loop a bit better please.  by understand i mean read the documentation and understand it from there
#  infolist_get(irc_server) or hdata()
#  Find a better way to debug than outputting data to a channel
#
# Debug help
#  weechat.command(weechat.buffer_search("irc", "freenode.#jf8hadfiadsf"), "The value of connectedState is " + str(connectedState))
#  session_start_time = time.time()

import os
import time
import datetime
import weechat

SCRIPT_NAME    = "IRC_Timer"
SCRIPT_AUTHOR  = "Mike Stiers <mike.stiers@gmail.com>"
SCRIPT_VERSION = "0.6"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC    = "Script to display how much of your life has been wasted on IRC"

filename = os.getenv("HOME")+'/irctimer.txt'
write_value_paused = str
write_value = 0

def readTimer():
    counter_file = open(filename, 'r')
    # Read the date and time the counter was last reset in C time. Using C time so I can force myself to learn to convert to POSIX time properly
    global last_reset_ctime
    last_reset_ctime = counter_file.readline()
    # Read the last counter value from counter stats file as seconds spent online
    global start_time_sec
    start_time_sec = float(counter_file.readline())
    counter_file.close()
    return start_time_sec

def calculateTimer(data, buffer, args):
    # Condition to check if connected.  If connected, increase seconds connected (write_value)), otherwise write_value_paused is returned to "pause" never ending hook timer
    if connectedState == 1:
        # count_value is the counter for the session
        # session_start_time is the start time of the current connection
        # write_value is the sum that outputs on the bar and written to the timer file
        count_value = time.time() - session_start_time
        global write_value
        write_value = count_value + start_time_sec
        write_value_friendly = str(write_value / 60 / 60 / 24) + " days"
        global write_value_paused
        write_value_paused = write_value
        return str(write_value_friendly)
    else:
        return str(write_value_paused)

def updateTimer(data, cals):
    # Write out time spent online to file, first the last reset time and then the number of seconds spent connected
    counter_file = open(filename, 'w')
    counter_file.writelines([last_reset_ctime, str(write_value), '\n'])
    counter_file.close()
    # Update weechat bar
    weechat.bar_item_update('irctimer')
    return weechat.WEECHAT_RC_OK

def serverConnected(data, buffer, args):
    global start_time_sec
    start_time_sec = readTimer()
    global connectedState
    connectedState = 1
    # POSIX of the start of the session
    global session_start_time
    session_start_time = time.time()
    weechat.hook_timer(1000,1,0,'updateTimer','')
    return weechat.WEECHAT_RC_OK

def serverDisconnected(data, buffer, args):
    global connectedState
    connectedState = 0
    return weechat.WEECHAT_RC_OK

# Check if counter stats file exists and create it if it does not
if os.path.isfile(filename):
    readTimer()
else:
    start_time_sec = 0.0
    last_reset_ctime = time.ctime()
    counter_file = open(filename, 'w')
    counter_file.writelines([last_reset_ctime, '\n', str(start_time_sec), '\n'])
    counter_file.close()

# Register plugin

if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, '', ''):
    weechat.bar_item_new('irctimer', 'calculateTimer', '')
    weechat.hook_signal('irc_server_connected', 'serverConnected', '')
    weechat.hook_signal('irc_server_disconnected', 'serverDisconnected', '')

# Check if connected already and start the party

infolist = weechat.infolist_get('irc_server', '', '')
while weechat.infolist_next(infolist):
    connectedState = weechat.infolist_integer(infolist, 'is_connected')

if connectedState == 1:
    serverConnected('', '', '')
