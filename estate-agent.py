#!/usr/bin/python
# -*- coding:utf-8 -*-
import argparse
import sys
import os
from subprocess import call
import time
from dotenv import load_dotenv


def get_arguments():
    parser = argparse.ArgumentParser(
        description='This program automatically searches for new flats and writes to the respective owners.')

    # add command line arguments
    parser.add_argument(
        'city', type=str, help='specify where to search for a flat')
    parser.add_argument(
        '-t', dest='text', type=str, help='set the text to write to the owners')
    parser.add_argument('-r', dest='rent', type=int,
                        help='set the maximum net rent')
    parser.add_argument('-s', dest='space', type=int,
                        help='set the minimum living space')
    parser.add_argument('--shared', action='store_true',
                        help='search for a shared flat')
    parser.add_argument('--own', action='store_true',
                        help='search for your own flat')

    args = parser.parse_args()

    # check input
    if args.own and args.shared:
        print("\n\t[-] You can either look for own or shared flats.\n")
        sys.exit()
    if not args.own and not args.shared:
        args.own = True  # if nothing provided, set own as default

    if args.text:
        # save provided text to file
        file = open('message.txt', 'w')
        file.write(args.text)
        file.close()
    elif os.path.isfile('message.txt') and os.path.getsize('message.txt') != 0:
        # when argument is not provided, take the saved text in the file
        file = open('message.txt', 'r')
        args.text = file.read()
    else:
        print(
            '\n\t[-] Please provide the text to write to the owners using the -t argument.\n')
        sys.exit()

    if not args.space:
        args.space = 0
    if not args.rent:
        args.rent = 0  # treated as infinity

    return args


def clear():
    _ = call('clear' if os.name == 'posix' else 'cls')


def print_start_message():
    clear()
    print('\nWelcome to')
    print('''  
  ___        _          _____    _        _          ___                   _   
 / _ \      | |        |  ___|  | |      | |        / _ \                 | |  
/ /_\ \_   _| |_ ___   | |__ ___| |_ __ _| |_ ___  / /_\ \ __ _  ___ _ __ | |_ 
|  _  | | | | __/ _ \  |  __/ __| __/ _` | __/ _ \ |  _  |/ _` |/ _ \ '_ \| __|
| | | | |_| | || (_) | | |__\__ \ || (_| | ||  __/ | | | | (_| |  __/ | | | |_ 
\_| |_/\__,_|\__\___/  \____/___/\__\__,_|\__\___| \_| |_/\__, |\___|_| |_|\__|
                                                           __/ |               
                                                          |___/                
    ''')
    print('\t\t\t\t\t\t\t\tby Henry Helm')

    time.sleep(2)

    print('''
        __   __                     ___      _
       |  | |  |      /|           |   |   _/ \_
       |  | |  |  _  | |__         |   |_-/     \-_     _
     __|  | |  |_| | | |  |/\_     |   |  \     /  |___|
    |  |  | |  | | __| |  |   |_   |   |   |___|   |   |
    |  |  |^|  | ||  | |  |   | |__|   |   |   |   |   |
    |  |  |||  | ||  | |  |   | /\ |   |   |   |   |   |
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~/  \~~~~~~~~~~~~~~~~~~~~~~~
   ~ ~~  ~ ~~ ~~~ ~ ~ ~~ ~~ ~~ \   \__   ~  ~  ~~~~ ~~~ ~~
 ~~ ~ ~ ~~~ ~~  ~~ ~~~~~~~~~~ ~ \   \o\  ~~ ~ ~~~~ ~ ~ ~~~
   ~ ~~~~~~~~ ~ ~ ~~ ~ ~ ~ ~ ~~~ \   \o\=   ~~ ~~  ~~ ~ ~~
~ ~ ~ ~~~~~~~ ~  ~~ ~~ ~ ~~ ~ ~ ~~ ~ ~ ~~ ~~~ ~ ~ ~ ~ ~~~~
    ''')
    time.sleep(5)
    clear()  # clears the console


def print_query(args):
    print('What you are looking for:')
    print('=====================================\n')
    if args.shared:
        print('Type:\t\t\tShared flat')
    else:
        print('Type:\t\t\tOwn flat')
    print('City:\t\t\t%s' % args.city)

    if args.rent == 0:
        print('Maximum rent:\t\t-')
    else:
        print('Maximum rent:\t\t%d€' % args.rent)

    if args.space == 0:
        print('Minimum living space:\t-')
    else:
        print(u'Minimum living space:\t%dm\u00b2\n' % args.space)

    time.sleep(2)

    print('\n\nWhat you write to the owners:')
    print('=====================================\n')
    print('Sehr geehrter Herr/Frau...\n')
    print(args.text)
    print('\nMit freundlichen Grüßen')
    print(os.getenv('NAME'))


load_dotenv()
args = get_arguments()
print_start_message()
print_query(args)
