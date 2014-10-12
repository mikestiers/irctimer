import os
import time
import datetime
import weechat

SCRIPT_NAME    = "IRC_Timer"
SCRIPT_AUTHOR  = "Mike Stiers <mike.stiers@gmail.com>"
SCRIPT_VERSION = "0.5"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC    = "Script to display how much of your life has been wasted on IRC"

filename = '/home/mayonaise/irctimer.txt'
connectedState = 0
write_value_paused = str

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
        write_value = count_value + start_time_sec
        global write_value_paused
        write_value_paused = write_value
        return str(write_value)
    else:
        return str(write_value_paused)

def updateTimer(data, cals):
    # Write out time spent online to file, first the last reset time and then the number of seconds spent connected
    counter_file = open(filename, 'w')
    counter_file.writelines([last_reset_ctime, str(calculateTimer('', '', '')), '\n'])
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

if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, '', ''):
    weechat.bar_item_new('irctimer', 'calculateTimer', '')
    weechat.hook_signal('irc_server_connected', 'serverConnected', '')
    weechat.hook_signal('irc_server_disconnected', 'serverDisconnected', '')

# last_reset_posix = time.mktime(last_reset_ctime)
# path = os.path.join('~/')
# timer still counts if you go into standby
# what happens when there are multiple server connections?
# find out why i lose a few seconds every disconnect
# maybe check irctimer.txt for correct formatting.  probably not worth it.
# does not start counting if plugin is loaded after connected

# do i need global in front of all these things?
# how to get dot completion support for weechat
# there has to be a way to get the value of things like "irc_server_connected" or the count of servers connected...tuple of info?
# figure out what "data, cals" or "data, buffer, args" is doing
# find out what a "callback" is for


# return str(days_value)  + " days"
# weechat.command(weechat.buffer_search("irc", "freenode.#jf8hadfiadsf"), "The value of connectedState is " + str(connectedState))
# session_start_time = time.time()

#if os.path.isfile(filename):
    #counter_file = open(filename, 'r')
    # Read the date and time the counter was last reset in C time. Using C time so I can force myself to learn to convert to POSIX time properly
    #last_reset_ctime = counter_file.readline()
    # Read the last counter value from counter stats file as seconds spent online
#    start_time_sec = float(counter_file.readline())
    #counter_file.close()

#infolist.py
#infolist_get(irc_server) or hdata()
