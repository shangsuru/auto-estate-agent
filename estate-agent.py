#!/usr/bin/python
# -*- coding:utf-8 -*-
import argparse
import sys
import os
from subprocess import call
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select


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
    parser.add_argument('-a', dest='area', type=int,
                        help='set the search area in km')
    parser.add_argument('--shared', action='store_true',
                        help='search for a shared flat')
    parser.add_argument('--own', action='store_true',
                        help='search for your own flat (default)')

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

    # set defaults for space and rent
    if not args.space:
        args.space = 0
    if not args.rent:
        args.rent = 0  # treated as infinity

    # change chosen area to closest available option
    options = [1, 2, 3, 4, 5, 10, 15, 20, 50]
    distances = list(map(lambda option: abs(args.area - option), options))
    args.area = options[distances.index(
        min(distances))]

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
    time.sleep(4)
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

    print('Search area:\t\t%d' % args.area)
    time.sleep(1)

    print('\n\nWhat you write to the owners:')
    print('=====================================\n')
    print('<Name des Vermieters>,\n')
    print(args.text)
    print('\nMit freundlichen Grüßen')
    print(os.getenv('FIRSTNAME') + ' ' + os.getenv('LASTNAME') + '\n')

    while True:
        choice = input('Do you want to start searching? [y/N]\t')
        if choice.lower() == 'y' or choice.lower() == 'yes':
            break
        else:
            sys.exit()


def login():
    global browser
    browser.get('https://sso.immobilienscout24.de/sso/login?appName=is24main')
    browser.find_element_by_id('username').send_keys(os.getenv('EMAIL'))
    browser.find_element_by_id('submit').click()
    time.sleep(3)
    browser.find_element_by_id('password').send_keys(os.getenv('PASSWORD'))
    browser.find_element_by_id('loginOrRegistration').click()


def search():
    global browser, args
    browser.get('https://www.immobilienscout24.de/')
    # rent
    browser.find_element_by_id('oss-price').send_keys(args.rent)
    # the minimum space of the flat
    browser.find_element_by_id('oss-area').send_keys(args.space)
    # own or shared flat
    typeSelect = Select(browser.find_element_by_id(
        'oss-real-estate-type-rent'))
    if args.own:
        typeSelect.select_by_value('APARTMENT_RENT')
    else:
        typeSelect.select_by_value('FLAT_SHARE_ROOM')
    # city
    cityInput = browser.find_element_by_id('oss-location')
    cityInput.send_keys(args.city)
    time.sleep(1)
    cityInput.send_keys(Keys.ENTER)
    time.sleep(1)

    # area/radius to search for
    searchAreaSelect = Select(browser.find_element_by_id('oss-radius'))
    searchAreaSelect.select_by_value('Km' + str(args.area))
    time.sleep(2)

    browser.find_element_by_xpath(
        '//button[contains(@class, "oss-main-criterion oss-button button-primary one-whole")]').click()


def get_expose_links():
    global browser

    def find_exposes():  # find all expose links on a single page
        global browser
        time.sleep(3)
        link_tags = browser.find_elements_by_xpath('//a[@href]')
        links = map(lambda link: link.get_attribute('href'), link_tags)
        expose_links = list(filter(lambda href: '/expose' in href, links))
        return expose_links

    expose_links = []
    expose_links.extend(find_exposes())
    while True:  # loop through all result pages
        time.sleep(2)
        try:
            browser.find_element_by_xpath(
                '//span[contains(text(), "nächste Seite")]').click()
            expose_links.extend(find_exposes())
        except Exception:  # if there is no next page button to be found
            break

    # eliminate duplicates
    expose_links = list(dict.fromkeys(expose_links))
    return expose_links


def save_expose_info(link, file):
    global browser
    browser.get(link)
    time.sleep(2)
    title = browser.find_element_by_id('expose-title').text
    address = browser.find_element_by_xpath(
        '//span[contains(@class, "zip-region-and-country")]').text
    owner = browser.find_element_by_css_selector(
        'div[data-qa="contactName"]').text
    net_rent = browser.find_element_by_xpath(
        '//div[contains(@class, "is24qa-kaltmiete is24-value font-semibold is24-preis-value")]').text
    total_rent = browser.find_element_by_xpath(
        '//dd[contains(@class, "is24qa-gesamtmiete grid-item three-fifths font-bold")]').text
    rooms = browser.find_element_by_xpath(
        '//div[contains(@class, "is24qa-zi is24-value font-semibold")]').text
    area = browser.find_element_by_xpath(
        '//div[contains(@class, "is24qa-flaeche is24-value font-semibold")]').text
    try:
        object_description = browser.find_element_by_xpath(
            '//pre[contains(@class, "is24qa-objektbeschreibung text-content full-text")]').text
    except Exception:
        object_description = 'Object description is missing.'

    file.write(title + '\n')
    file.write('==============================================\n')
    file.write('Address:\t\t' + address + '\n')
    file.write('Owner:\t\t' + owner + '\n')
    file.write('Net rent:\t\t' + net_rent + '\n')
    file.write('Total rent:\t\t' + total_rent + '\n')
    file.write('Rooms:\t\t' + rooms + '\n')
    file.write('Area:\t\t' + area + '\n')
    file.write('Object Description:\n' + object_description + '\n\n')

    return owner


load_dotenv()
args = get_arguments()

print_start_message()
print_query(args)

browser = webdriver.Chrome(os.getcwd() + '/chromedriver')

login()
search()
expose_links = get_expose_links()

# log file to save retrieved exposes
log_file = 'log_' + str(int(time.time())) + '.txt'
file = open('logs/' + log_file, 'a+')

for link in expose_links:
    owner = save_expose_info(link, file)

    # fill out the contact form
    browser.find_element_by_css_selector('a[data-qa="sendButton"]').click()
    time.sleep(2)
    browser.find_element_by_id(
        'contactForm-Message').send_keys(owner + ',\n\n' + args.text
                                         + '\n\nMit freundlichen Grüßen\n'
                                         + os.getenv('FIRSTNAME')
                                         + ' ' + os.getenv('LASTNAME'))
    Select(browser.find_element_by_id('contactForm-salutation')
           ).select_by_value(os.getenv('GENDER'))
    browser.find_element_by_id(
        'contactForm-firstName').send_keys(os.getenv('FIRSTNAME'))
    browser.find_element_by_id(
        'contactForm-lastName').send_keys(os.getenv('LASTNAME'))
    browser.find_element_by_id(
        'contactForm-emailAddress').send_keys(os.getenv('EMAIL'))
    browser.find_element_by_id(
        'contactForm-street').send_keys(os.getenv('STREET'))
    browser.find_element_by_id(
        'contactForm-houseNumber').send_keys(os.getenv('NR'))
    browser.find_element_by_id(
        'contactForm-postcode').send_keys(os.getenv('ZIP'))
    browser.find_element_by_id('contactForm-city').send_keys(os.getenv('CITY'))


file.close()
browser.quit()
