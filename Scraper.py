import sys
import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select


class Scraper:
    def __init__(self, args):
        self.browser = webdriver.Chrome(os.getcwd() + '/chromedriver')
        self.args = args
        load_dotenv()

    def login(self):
        self.browser.get(
            'https://sso.immobilienscout24.de/sso/login?appName=is24main')
        self.browser.find_element_by_id(
            'username').send_keys(os.getenv('EMAIL'))
        self.browser.find_element_by_id('submit').click()
        time.sleep(3)
        self.browser.find_element_by_id(
            'password').send_keys(os.getenv('PASSWORD'))
        self.browser.find_element_by_id('loginOrRegistration').click()

    def search(self):
        self.browser.get('https://www.immobilienscout24.de/')
        # rent
        self.browser.find_element_by_id('oss-price').send_keys(self.args.rent)
        # the minimum space of the flat
        self.browser.find_element_by_id('oss-area').send_keys(self.args.space)
        # own or shared flat
        typeSelect = Select(self.browser.find_element_by_id(
            'oss-real-estate-type-rent'))
        if self.args.own:
            typeSelect.select_by_value('APARTMENT_RENT')
        else:
            typeSelect.select_by_value('FLAT_SHARE_ROOM')
        # city
        cityInput = self.browser.find_element_by_id('oss-location')
        cityInput.send_keys(self.args.city)
        time.sleep(1)
        cityInput.send_keys(Keys.ENTER)
        time.sleep(1)

        # area/radius to search for
        searchAreaSelect = Select(
            self.browser.find_element_by_id('oss-radius'))
        searchAreaSelect.select_by_value('Km' + str(self.args.area))
        time.sleep(2)

        self.browser.find_element_by_xpath(
            '//button[contains(@class, "oss-main-criterion oss-button button-primary one-whole")]').click()

    def get_expose_links(self):
        def find_exposes():  # find all expose links on a single page
            time.sleep(3)
            link_tags = self.browser.find_elements_by_xpath('//a[@href]')
            links = map(lambda link: link.get_attribute('href'), link_tags)
            expose_links = list(filter(lambda href: '/expose' in href, links))
            return expose_links

        expose_links = []
        expose_links.extend(find_exposes())
        while True:  # loop through all result pages
            time.sleep(2)
            try:
                self.browser.find_element_by_xpath(
                    '//span[contains(text(), "nächste Seite")]').click()
                expose_links.extend(find_exposes())
            except:  # no next page button found
                break

        # eliminate duplicates
        expose_links = list(dict.fromkeys(expose_links))
        return expose_links

    def save_expose_to_log(self, file):
        title = self.browser.find_element_by_id('expose-title').text
        address = self.browser.find_element_by_xpath(
            '//span[contains(@class, "zip-region-and-country")]').text
        owner = self.browser.find_element_by_css_selector(
            'div[data-qa="contactName"]').text
        net_rent = self.browser.find_element_by_xpath(
            '//div[contains(@class, "is24qa-kaltmiete is24-value font-semibold is24-preis-value")]').text
        total_rent = self.browser.find_element_by_xpath(
            '//dd[contains(@class, "is24qa-gesamtmiete grid-item three-fifths font-bold")]').text
        rooms = self.browser.find_element_by_xpath(
            '//div[contains(@class, "is24qa-zi is24-value font-semibold")]').text
        area = self.browser.find_element_by_xpath(
            '//div[contains(@class, "is24qa-flaeche is24-value font-semibold")]').text
        try:
            object_description = self.browser.find_element_by_xpath(
                '//pre[contains(@class, "is24qa-objektbeschreibung text-content full-text")]').text
        except:
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

    def fill_out_contact_form(self, owner):
        self.browser.find_element_by_css_selector(
            'a[data-qa="sendButton"]').click()
        time.sleep(2)
        self.browser.find_element_by_id(
            'contactForm-Message').send_keys(owner + ',\n\n' + self.args.text
                                             + '\n\nMit freundlichen Grüßen\n'
                                             + os.getenv('FIRSTNAME')
                                             + ' ' + os.getenv('LASTNAME'))
        Select(self.browser.find_element_by_id('contactForm-salutation')
               ).select_by_value(os.getenv('GENDER'))
        self.browser.find_element_by_id(
            'contactForm-firstName').send_keys(os.getenv('FIRSTNAME'))
        self.browser.find_element_by_id(
            'contactForm-lastName').send_keys(os.getenv('LASTNAME'))
        self.browser.find_element_by_id(
            'contactForm-emailAddress').send_keys(os.getenv('EMAIL'))
        self.browser.find_element_by_id(
            'contactForm-street').send_keys(os.getenv('STREET'))
        self.browser.find_element_by_id(
            'contactForm-houseNumber').send_keys(os.getenv('NR'))
        self.browser.find_element_by_id(
            'contactForm-postcode').send_keys(os.getenv('ZIP'))
        self.browser.find_element_by_id(
            'contactForm-city').send_keys(os.getenv('CITY'))

    def start(self):
        try:
            name = 'log_' + str(int(time.time())) + '.txt'
            log_file = open('logs/' + name, 'a+')

            self.login()
            self.search()
            expose_links = self.get_expose_links()

            for link in expose_links:
                self.browser.get(link)
                time.sleep(2)
                try:
                    # <3-button is unset: have not yet written to that expose
                    self.browser.find_element_by_xpath(
                        '//*[@title="Exposé merken"]')
                except:
                    continue  # <3-button is set: don't write to that expose again
                owner = self.save_expose_to_log(log_file)
                self.fill_out_contact_form(owner)
        except:
            print('\nProgram terminated.')
        finally:
            log_file.close()
            self.browser.quit()
