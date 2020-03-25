#!/usr/bin/env python3

# Sneakernet/users.py

"""
  if no my_feed.json exists:
    create? n -> exit
    create
  if no log dir exists:
    create dir
  if no log file 0 exists:
    create pcap file
  read pcap file
  if unequal to feedID:
    abort

  if 'display_name' option:
    ask for name
    append about event
  else:
    loop over all logs
      scan log, record latest 'about'
      display feed and display_name
"""

import base64
import json
import os
import platform
import sys
import time
from datetime import datetime
import random
# from consolemenu import *

import lib.gg     as gg
import lib.pcap   as log
# from consolemenu.items import *

import lib.crypto as crypto
import lib.gg     as gg
import lib.pcap   as log
import curses
import udp_peer

MY_SECRET_FILE = 'MyFeedID.json'
LOGS_DIR = 'logs'
MY_LOG_FILE = '1.pcap'  # inside logs dir

# ----------------------------------------------------------------------

menu = ['Import', 'Export', 'Write', 'Read', 'About', 'Exit']

submenu = ["USB", "UDP"]


def print_sneaker(stdscr):
    curses.echo()
    # Just don't change the try catch or else it will fail
    try:
        stdscr.addstr("""


                                  ,/((//*,.                                                                           
                                 (#%%##%%%%%##/                                                                       
                               .#%%%%#%&&&&&&&%%#(,                                                                   
                               #%%&&&%(&&&&&&&&&&%%%#/.                                                               
                              (%%&&&%&%%&&&&&&&&&&&&&%%##/                                                             
                             (%%&&&&&&&&&&&@&&&&&&&&&&&&%%%#(*                                                         
                           /%&%&&&&&&&&%&%@@@@@&&&&&&&&&&&&&%%#(*                                                     
                          *%%&%&&&&&&&&&&%@@@@@@&&&&&&&&&&&&&%%%(*                                                   
                          #%&&&&&&&&&&&&&&&&&&%&&@@@@&&&&&&&&&&&&%%%%#/                                               
                        #%%&&&&&&&&&&&&&&&&&&&&%@@@@@&&&&&&&&&&%#/#%%#(/                                             
                      .#%&&&&&&&&&&&&&&&&&&&&&&&%%&&      ........... *.                                         
                      #%&&&/&&&&&&&&&&&&&&&&&&&&%&&%&&*    ,..,/,...... /*#/                                       
                     #%&&&&&,&&&&&&&&(&&&&&&&&&&&&&&&&&&&%&.  .(*((.,/(*... %%%%(                                     
                   #&&/&&&&&&%&&&&&&&&&(&&&&&&&&&%&&&&&&&%&(.  *,((,,*(((*.. %&%%(                                     
                 (&&&&&&&&&&&&&%&&&&&&&&%&&&&&&&&&&&&&&,%.....**/(.////..%&&%%/                                   
               (%&&&&&&&%&&&&&&&/&&&&&&&&&&&&&&&&&&&/  &&&(%.......//((*,..%&&%%#                                   
              %&&&&&&&&&&/&&&&&&&&*&&&&&&&&&&&.&&/&&&.&@%*#&&.... ...**....%%&&%#                                   
            /#& &&&&&&&&&&&&&&&&&&.&&&&&&&&&&&&*&&&/.*,/&&&&%..............%%&&%(                                   
           #(&  .&&&&&&&&&&&&&&&&&&&%&&&&&&&&&&&&&&&&&&&&&&&%/*/*/*.,**,,..&&&%%*                                   
         /%&&    .&&&&&&&&&&&/&&&&&&&&&&.&&&&&&&&&&&&&&&&&&&&&&.. ... .......&%&%#                                     
       .%&&%.      %&&&&&&&&&&&&&&&&&&&&.&&&&&&&@@&&&&&&&&&&&&&&&&&&&&&&&&&&%&%(                                     
     . &&&%&.       .&&&&&&&&&&&%&&&&&&&&&&&%&&&,&@&&&%  .(&&&&&&&&&&&&&&&&&&&%&%*                                     
    , ,&&&@&&.        /&&&&&&&&&&&(&&&&&&&&&&&&&%@&&&&          /%&&&&&&&&&&&&%##                                     
    #  &&&&&&&*         (&&&&&&&&&&&(&&&&&&&&&&@&&&@&@&&             ,#&&&%(.                                         
    #. &&&&&&&&&          *&&&&&&&&&&&&&&&&&&&&&@&@&&&&&&&&(                                                         
    .%  &&&&&&(//,           &&&&&&&&&&&*&&&&&&/@&&&@@@&&&&&,&,......          ..                                     
     #(  &&&&&%*../,           .&&&&&&&&&/&&&/&@&&&&/(%&&&*&....  .#&&.    (/                                     
      %#  &&&&&*./// .          *&&&&&&&&&&,&*&@&@&%        *%&&&&&&&&&&%%/.                                         
       *%  %&&&&&/(&&&,           #&&&&&&&&&&&&&&&&&*              .,..                                             
         %. /&&&&&&&&&&&&&&          &&&&&&&&&&(@&&&@&&&&&&&&(               /%%(                                     
          %(  &&&&&&&&&&&&&&&&       .&&&&&&&&&*&&&&@&&&&&&&&%...... ./,      .%#                                     
           (%  %&&&&&&&&&&&&&&&.      *#*&&&&&&,&&&&&&&%%#%&&%,..,&&&&&&&&%%%/.                                       
            .%  %&&&&&&&&&&&&&&&       &&&&&&&&&@&@&&&              ./###.                                             
    ...       %/ .&&&&&&&&&&&&%#.      (&&&&&&&&@&&&&&.                        *##                                     
               ..  ,,,,,,,,......       ,,,,,,,,,,,,,,,,,,,,.....                ..                                   

       @@@   @@@   @@@  @@@@@@@(  @@,       #@@@@@@   .@@@@@@.   /@@@    @@@   @@@@@@@(      @@@@@@@@@   @@@@@@*       
       .@@  /@@@(  @@.  @@#       @@,      @@@    %  @@@    @@@  /@@@@  @@@@   @@@              @@&    &@@    @@@      
        @@@ @@ @@ @@@   @@@@@@@   @@,     &@@       .@@.    .@@. /@@/@&@@ @@   @@@@@@@          @@&    @@&     @@(     
         @@#@& @@(@@    @@#       @@,     %@@        @@/    /@@  /@@ &@@  @@   @@@              @@&    @@@    .@@,     
         @@@@   @@@@    @@@@@@@(  @@@@@@@  @@@@**@@  *@@@**@@@*  /@@      @@   @@@@@@@(         @@&     @@@(,@@@%      
                                              *#/       ,((,                                               /#,         



        @@@@@@@&  @@@@   @@   @@@@@@@@    @@@@     @@@  .@@@  @@@@@@@@  @@@@@@@@   @@@@   @@&  &@@@@@@@ @@@@@@@@@      
       @@@        @@@@@  @@   @@@        (@@@@@    @@@ @@@    @@@       @@#   @@*  @@@@@  @@&  &@@         @@@         
        @@@@@@@   @@ (@@ @@   @@@@@@@    @@  @@/   @@@@@&     @@@@@@@   @@@@@@@%   @@*.@@#@@&  &@@@@@@*    @@@         
             @@@  @@   @@@@   @@@       @@@@@@@@   @@@ @@@    @@@       @@# @@@    @@*  @@@@&  &@@         @@@         
       @@@@@@@@,  @@    @@@   @@@@@@@@ @@@    @@@  @@@  (@@@  @@@@@@@@  @@#  .@@@  @@*   @@@&  &@@@@@@@    @@@         

                                             .................,,,,,,,,,          .,,,,,,,,,,,,...                      
                                         ##.  #&&&&&&&&&&&&&&&&@@@@@@&&*. ./&%&&@@@@@@@&&&&&&@&&%                      
                               .          #%%   &&@@@@@@@@@@@@@@@@@@@@@@@&&@&&@&@@@@@@@@&&&&&&&&                     
                                .           %%%   &&&@&@@@@@@@@@@@@@@@@@@@@&@&&&@@@@@@&&&&&&&&&&&&(                    
                                 ..           %%%   &&@@@@@@@@@@@@@@@@&&,&@@@*@&@@@@@@&&&&&&&&&&&%%.                   
                                  ...  .        %%%   &&@@@@@@@@@@@@@(&&@&&*@#&@@@&&&&&&&&&&&&&&&&%/                   
                                   .... . .       %%#   #&&@@@@@@@@@@@@@,&&&.*&&@@@&&&@&&&&&&&&&&&%%*                  
                                    ..... .         %%%.  .&@@@@@@@@@@@@&@&@@@#&@@&@&&@&&&&&&&&&&%%,                 
                                     .....   .        (%%%   (&&@@@@@@@&@*@@@@@@@&@#&@@&&&&@&&&&&&&&&%,*               
                                      ... .  .           %%%/   &&@@@&&%@&@@@(@@@@@@&@#&&@@@&&&&&&&&&&&*#              
                                        ..... ...          *%%%   .&(&&&&@@@@@@&.@@@@@@@&&*&&@&&&&&&&&&%,            
                                         .......  ...         %%%#   (&@@@@@@@@@@@@#@&@@@@&&@&%&&&&&&&&& &%(,          
                                          ...... ...  . .       ,%%%    &&@@@@@@@@@@@@@,&@@@&@@@&&,#&&&,%&&&(#         
                                            .......  ....          %&&%    &&@@@@@@@@@@@@@@&&@@@&&@@&&&&&&&&&*%,       
                                              .........   .  .        %&%%    &@@@@@@@@@@@@@@@&/@&&&@@&&&&&&&*&%#      
                                                ......    .....          %&&%    &@@@@@@@@@@@@@@@@@&&(.&.#&&&&%%     
                                                  ............. ..          %&&%/   .&@@@@@@@@@@@@@@@@@&&&&&&&&&&&%    
                                                     ..........  ... ..        ,%&&%.   ,&&@@@@@@@@@@@@@&&&&&&&&&&&(   
                                                       .........  .. ..  .         /&&&%*    &@@@@@@@@@@@@@@@&&&&&&&   
                                                         ......... .  . ....   ..      *&&&   .,&&@@@@@@@@@@&&&&&   .
                                                            .......... .  ...  .            #%&&%%.    . .,(#/,     *#.
                                                               ........... ..  ..      .         #%%%%%%%(*,...*(%%%%  
                                                                  ....... .. .......    .. .            ,/#%%%#/.      
                                                                      ............. ...     ..                         
                                                                         ............ ......    ...                    
                                                                             ...................           .           
                                                                                 ...................... .   ..         
                                                                                      ...................   .          
                                                                                             .....                     



   """)
    except:
        stdscr.refresh()
        time.sleep(3)
        return


def print_menu(stdscr, selected_row_idx):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    for idx, row in enumerate(menu):
        x = w // 2 - len(row) // 2
        y = h // 2 - len(menu) // 2 + idx
        if idx == selected_row_idx:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, x, row)
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(y, x, row)
    stdscr.refresh()


def print_submenu(stdscr, selected_row_idx):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    for idx, row in enumerate(submenu):
        x = w // 2 - len(row) // 2
        y = h // 2 - len(submenu) // 2 + idx
        if idx == selected_row_idx:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, x, row)
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(y, x, row)
    stdscr.refresh()


def print_center(stdscr, text):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    x = 10
    y = h // 2
    stdscr.addstr(y, x, text)
    stdscr.refresh()


def main(stdscr):
    # turn off cursor blinking
    curses.curs_set(0)

    # color scheme for selected row
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    # specify the current selected row
    current_row = 0

    print_sneaker(stdscr)

    # print the menu
    print_menu(stdscr, current_row)

    while 1:
        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu) - 1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            # print_center(stdscr, "You selected '{}'".format(menu[current_row]))
            menu_selection = menu[current_row]
            stdscr.clear()
            stdscr.refresh()
            if menu_selection == "Write":

                write_message(stdscr)

            elif menu_selection == "Import":
                sub_menu(stdscr, current_row, menu_selection)
            elif menu_selection == "Export":
                sub_menu(stdscr, current_row, menu_selection)
            elif menu_selection == "Read":
                output_chat(stdscr)
                if key == 27:
                    print_menu(stdscr, 0)
            elif menu_selection == "About":
                print_sneaker(stdscr)
                if key == 27:
                    print_menu(stdscr, 0)
            elif menu_selection == "Exit":
                exit_selection = c_input(stdscr, "Are you sure you want to exit? [Yes|No]")
                if exit_selection in ["No", "N", "no", "n"]:
                    print_menu(stdscr, 0)
                else:
                    print("shutdown..")
                    for i in range(300):
                        time.sleep(0.009)
                        print(".")
                    sys.exit()
            stdscr.getch()
            # if user selected last row, exit the program

        print_menu(stdscr, current_row)


def sub_menu(stdscr, current_row, selecter):
    print_submenu(stdscr, current_row)
    while 1:
        key = stdscr.getch()
        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(submenu) - 1:
            current_row += 1
        elif key in [27, curses.KEY_LEFT]:
            print_menu(stdscr, 0)
            break
        elif key == curses.KEY_ENTER or key in [10, 13]:
            sub_selection = submenu[current_row]
            stdscr.clear()
            stdscr.refresh()
            if selecter == "Import":
                if sub_selection == "USB":
                    import_log(stdscr)
                    if key == 27:
                        print_menu(stdscr, 0)
                else:
                    udp_peer.udp_start(stdscr)
                    if key == 27:
                        print_menu(stdscr, 0)
            else:
                if sub_selection == "USB":
                    export(stdscr)
                    if key == 27:
                        print_menu(stdscr, 0)
                else:
                    ip = c_input(stdscr, "IP: ")
                    udp_peer.udp_start(stdscr, ip)
        print_submenu(stdscr, current_row)
        if key == 27:
            print_menu(stdscr, 0)


def c_input(stdscr, prompt_str):
    curses.echo()
    stdscr.addstr(prompt_str)
    stdscr.refresh()
    input = stdscr.getstr()
    return input.decode("utf-8")


def my_log_append(log_fn, body):
    lg = log.PCAP()
    lg.open(log_fn, 'r')
    prev = None
    feed = None
    seq = 0
    t = gg.TRANSFER()
    # find last event
    for block in lg:
        t.from_cbor(block)
        prev = t.event.prev
        feed = t.event.feed
        seq = t.event.seq
    lg.close()

    lg.open(log_fn, 'a')
    e = gg.EVENT(
        prev=prev,
        feed=keypair.public,
        seq=seq + 1,
        time=int(time.time()),
        content=bytes(json.dumps(body), 'utf-8'),
        content_enc=gg.GG_CONTENT_ENCODING_JSON
    )
    e.signature = keypair.sign(e.event_to_cbor())
    t = gg.TRANSFER(e)
    lg.write(t.to_cbor())
    lg.close()


def feed_get_display_name(log_fn):
    # returns a <feedID,display_name> tuple
    feed = None
    name = None
    lg = log.PCAP()
    lg.open(log_fn, 'r')
    t = gg.TRANSFER()
    for block in lg:
        t.from_cbor(block)
        if not feed:
            feed = t.event.feed
        c = t.event.content
        if not c:
            continue
        m = json.loads(c)
        if 'app' in m and m['app'] == 'feed/about' and 'display_name' in m:
            name = m['display_name']
    lg.close()
    return (feed, name)


def write_message(stdscr):
    message = c_input(stdscr, "\nPlease insert your message: ")
    body = {"app": "feed/message",
            "feed": my_secret['public_key'],
            "text": message}
    scr_print(stdscr, "\n** successfuly created body\n")
    my_log_append(os.path.join(LOGS_DIR, MY_LOG_FILE), body)
    scr_print(stdscr, f"** successfuly appended to {os.path.join(LOGS_DIR, MY_LOG_FILE)}")


def output_chat(stdscr):
    t = gg.TRANSFER()
    lg = log.PCAP()
    pp_list = []
    name_list = {}
    for file in os.listdir(LOGS_DIR):
        lg.open(os.path.join(LOGS_DIR, file), "r")
        nick_name = []
        for block in lg:
            t.from_cbor(block)
            c = t.event.content
            if c != None:
                # print(f"** {base64.b64encode(t.event.feed).decode('utf8')}/{t.event.seq}")
                # print(str(c, 'utf8'))
                m = json.loads(c)
                if m['app'] == "feed/message":
                    pp_list.append([t.event.time, m])
                if m['app'] == "feed/about":
                    name_list[m['feed']] = m['display_name']
                # print(m)
            else:
                scr_print(stdscr, f"** {n}: no content")
        lg.close()
    pp(pp_list, name_list, stdscr)


def pp(list, name_list, stdscr):
    sorted(list)
    output = ""
    if list:
        for item in list:
            timestamp = str(datetime.fromtimestamp(item[0]))
            feed = item[1]['feed']
            name = name_list.get(feed)
            content = item[1]['text']
            curses.echo()
            output += f"({timestamp}) {name}:\t{content}\n\n"


        height, width = stdscr.getmaxyx()

        # Create a curses pad (pad size is height + 10)
        mypad_height = len(list) * 4

        mypad = curses.newpad(mypad_height, width)
        mypad.scrollok(True)
        mypad_pos = -2
        mypad_refresh = lambda: mypad.refresh(mypad_pos + 2, 0, 0, 0, height - 1, width)
        mypad_refresh()
        try:
            mypad.addstr(output)
        except:
            pass
        finally:
            mypad_refresh()

        while 1:
            key = stdscr.getch()
            if key == curses.KEY_DOWN and mypad_pos < mypad.getyx()[0] - height - 1:
                mypad_pos += 1
                mypad_refresh()
            elif key == curses.KEY_UP and mypad_pos > -2:
                mypad_pos -= 1
                mypad_refresh()
            elif key == 27:  # ESC
                print_menu(stdscr, 0)
                break
            elif key == curses.KEY_RESIZE:
                height, width = stdscr.getmaxyx()
                # while mypad_pos > mypad.getyx()[0] - height - 1:
                #     mypad_pos -= 1
                mypad.refresh(mypad_pos + 2, 0, 0, 0, height - 1, width - 1)
    else:
        scr_print(stdscr, "No logs to show")

def import_log(stdscr):
    import_dir = c_input(stdscr, "enter path: ")

    if not os.path.isdir(import_dir):
        scr_print(stdscr, "directory not found, press ENTER to go back\n")
        return

    new_db = {}
    new_cnt = 0
    lg = log.PCAP()
    t = gg.TRANSFER()
    for fn in os.listdir(import_dir):
        fn = os.path.join(import_dir, fn)
        lg.open(fn, 'r')
        for block in lg:
            t.from_cbor(block)
            feed = t.event.feed
            seq = t.event.seq
            if not feed in new_db:
                new_db[feed] = {}
            if not seq in new_db[feed]:
                new_db[feed][seq] = []
            new_db[feed][seq].append(block)
            new_cnt += 1
        lg.close()
    scr_print(stdscr, f"** found {new_cnt} event(s) in '{import_dir}'\n")

    have_fn = {}
    have_max = {}
    have_cnt = 0
    max_fn_number = 1
    for fn in os.listdir(LOGS_DIR):
        # remember highest file number, if we have to create a new file
        i = int(fn.split('.')[0])
        if max_fn_number < i:
            max_fn_number = i

        lg.open(os.path.join(LOGS_DIR, fn), 'r')
        for block in lg:
            have_cnt += 1
            t.from_cbor(block)
            feed = t.event.feed
            if not feed in have_fn:
                have_fn[feed] = fn
            seq = t.event.seq
            if not feed in have_max:
                have_max[feed] = -1
            if seq > have_max[feed]:
                have_max[feed] = seq
        lg.close()
    scr_print(stdscr, f"** found {have_cnt} event(s) in '{LOGS_DIR}'\n")

    update_cnt = 0
    for feed in new_db:
        if not feed in have_fn:
            max_fn_number += 1
            have_fn[feed] = os.path.join(LOGS_DIR, str(max_fn_number) + '.pcap')
            have_max[feed] = 0
            if update_cnt == 0:
                print()
            scr_print(stdscr, f"** creating {have_fn[feed]} for {base64.b64encode(feed).decode('utf8')}\n")
            lg.open(have_fn[feed], 'w')
            lg.close()
            max_fn_number += 1
            update_cnt += 1

    update_cnt = 0
    for feed in have_fn:
        if not feed in new_db:
            continue
        lg.open(have_fn[feed], 'a')
        # print(f"** testing {have_fn[feed]}, seq={have_max[feed]}")
        while have_max[feed] + 1 in new_db[feed]:
            have_max[feed] += 1
            if update_cnt == 0:
                print()
            scr_print(stdscr, f"** import {base64.b64encode(feed).decode('utf8')}/{have_max[feed]}\n")
            lg.write(new_db[feed][have_max[feed]][0])
            update_cnt += 1
        lg.close()

    scr_print(stdscr, f"** imported {update_cnt} event(s) to the '{LOGS_DIR}' directory\n")


def export(stdscr):
    export_dir = c_input(stdscr, "enter path: ")

    scr_print(stdscr, f"** exporting new events to '{export_dir}'\n")
    print()

    if not os.path.isdir(export_dir):
        scr_print(stdscr, "directory not found, press ENTER to go back\n")
        return

    lg = log.PCAP()
    t = gg.TRANSFER()

    have_db = {}
    have_max = {}
    have_cnt = 0
    for fn in os.listdir(LOGS_DIR):
        lg.open(os.path.join(LOGS_DIR, fn), 'r')
        for block in lg:
            t.from_cbor(block)
            feed = t.event.feed
            seq = t.event.seq
            if not feed in have_db:
                have_db[feed] = {}
                have_max[feed] = 0
            have_db[feed][seq] = block
            if seq > have_max[feed]:
                have_max[feed] = seq
            have_cnt += 1
        lg.close()
    scr_print(stdscr, f"** found {have_cnt} event(s) in directory '{LOGS_DIR}'\n")

    target_db = {}
    target_cnt = 0
    for fn in os.listdir(export_dir):
        fn = os.path.join(export_dir, fn)
        lg.open(fn, 'r')
        for block in lg:
            t.from_cbor(block)
            feed = t.event.feed
            seq = t.event.seq
            if not feed in target_db:
                target_db[feed] = {}
            if not seq in target_db[feed]:
                target_db[feed][seq] = []
            # target_db[feed][seq].append(block)
            target_cnt += 1
        lg.close()
    scr_print(stdscr, f"** found {target_cnt} event(s) in target directory '{export_dir}'\n")

    # create file with unique file name
    log_fn = None
    while True:
        log_fn = 'x' + str(random.randint(10000000, 19999999))[1:] + '.pcap'
        log_fn = os.path.join(export_dir, log_fn)
        if not os.path.isfile(log_fn):
            break

    lg.open(log_fn, 'w')
    update_cnt = 0
    for feed in have_db:
        for i in range(0, have_max[feed]):
            if not feed in target_db or not i + 1 in target_db[feed]:
                if update_cnt == 0:
                    print()
                scr_print(stdscr, f"** exporting {base64.b64encode(feed).decode('utf8')}/{i + 1}\n")
                lg.write(have_db[feed][i + 1])
                update_cnt += 1
    lg.close()

    print()
    if update_cnt == 0:
        os.unlink(log_fn)
        scr_print(stdscr, "** no events exported\n")
    else:
        stdscr.addstr(f"** exported {update_cnt} event(s) to '{log_fn}'\n")

    # eof

def scr_print(stdscr, content):
    stdscr.addstr(f"{content}\n")
    stdscr.refresh()

# ----------------------------------------------------------------------
if __name__ == '__main__':

    set_new_name = False
    message_mode = False
    output_mode = False

    print("\nWelcome to SneakerNet\n")
    # print("** starting the user directory app")

    keypair = crypto.ED25519()
    if not os.path.isfile(MY_SECRET_FILE):
        yn = input('>> create personal feed ID? (y/N) ')
        if yn != 'y':
            print("** aborted")
            sys.exit()
        keypair.create()
        my_secret = {'public_key':
                         base64.b64encode(keypair.public).decode('utf8'),
                     'private_key':
                         base64.b64encode(keypair.private).decode('utf8'),
                     'create_context': platform.uname(),
                     'create_time': time.ctime()
                     }
        with open(MY_SECRET_FILE, 'w') as f:
            f.write(json.dumps(my_secret, indent=2))
    else:
        with open(MY_SECRET_FILE, 'r') as f:
            my_secret = json.loads(f.read())
        keypair.public = base64.b64decode(my_secret['public_key'])
        keypair.private = base64.b64decode(my_secret['private_key'])
        # print(keypair.public, keypair.private)
        print(f"** loaded my feed ID: @{base64.b64encode(keypair.public).decode('utf8')}")

    if not os.path.isdir(LOGS_DIR):
        os.mkdir(LOGS_DIR)
        print(f"** created {LOGS_DIR} directory")

    log_fn = os.path.join(LOGS_DIR, MY_LOG_FILE)
    if not os.path.isfile(log_fn):
        lg = log.PCAP()
        lg.open(log_fn, 'w')
        lg.close()
        print(f"** created my log at {log_fn}")

    # find my name
    feed, name = feed_get_display_name(log_fn)
    if feed and feed != keypair.public:
        print(f"** {log_fn} does not match feed ID (MyFeedID.json), aborting")
        sys.exit()
    if set_new_name or not feed or not name:
        if not feed or not name:
            print("** no name for this feed found")
        name = input(">> enter a display name for yourself: ")
        about = {'app': 'feed/about',
                 'feed': my_secret['public_key'],
                 'display_name': name}
        my_log_append(log_fn, about)
        print(f"** defined display name '{name}'")
    else:
        print(f"** loaded my name: '{name}'")

    print("\n** list of known users:")
    feeds = {}
    for fn in os.listdir(LOGS_DIR):
        log_fn = os.path.join(LOGS_DIR, fn)
        feed, name = feed_get_display_name(log_fn)
        feeds[feed] = name
    for feed, name in sorted(feeds.items(), key=lambda x: x[1]):
        print(f"- @{base64.b64encode(feed).decode('utf8')}   {name}")

    os.environ.setdefault('ESCDELAY', '0')
    curses.wrapper(main)



# eof
