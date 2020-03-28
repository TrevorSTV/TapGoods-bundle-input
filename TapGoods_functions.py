import openpyxl
import time
import datetime

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains


"""
This is function I made just so I would have an easy way to make consistant wait time
without needing a global variable.

"""


def wait(sec=0):
    time.sleep(3 + sec)


"""
Input:
bundles_sheet_name = string of the name of an xlsx file.
items_sheet_name = string of the name of an xlsx file.

bundles_sheet_name refers to a spreadsheet formatted like bundles_sheet.xlsx

items_sheet_name refers to a spreadsheet formatted like items_sheet.xlsx

This function takes 2 excel spreadsheets and makes a data structure out of the data in them.
The data structure is:
{ 'bundle name': {'flat_price': 'price as string'
                   'tags': [tag1, tag2, ...]
                   'items': {inventory: quantity}
                 }
}

I had intended to similarly get all of the rest of the data from the spreadsheets.
However, since I no longer have access to TapGoods I couldn't determine the html
elements to input the rest of the data so I left it as how I did it when initially
putting in the bundles for Event Rentals. This is the minimal info necessary and 
assumes the the bundle will be price locked.

I think dealing accounting for non-price locked bundles will require more steps in
this function and the bundle_form_fill function.

Something I didn't consider until recently is that using a library like Pandas could
make this function unnecessary and could potentially make the code simpler.
"""


def bundle_data_structure_format(bundles_sheet_name, items_sheet_name):

    # data structure that will be returned
    bundles = {}

    bundles_wb = openpyxl.load_workbook(bundles_sheet_name)
    items_wb = openpyxl.load_workbook(items_sheet_name)

    # These are the sheets in the spreadsheet containing the data.
    bundles_sheet = bundles_wb.active
    items_sheet = items_wb.active

    for row in bundles_sheet.values:
        # dict that will be the entry for the bundle name in bundles
        bundle_entry = {}

        bundle_entry['flat_price'] = str(row[12])

        bundle_entry['tags'] = row[2].split(',')

        bundle_entry['items'] = {}

        bundles[row[0]] = bundle_entry

    for row in items_sheet.values:
        bundle_name = row[0]
        if bundle_name in bundles:
            item = row[1]
            qty = row[2]
            bundles[bundle_name]['items'][item] = qty

    return bundles


"""
This function will add inventory to the bundle. I believe this should work from
any bundles page, so it could potentially be used to mass update bundles that
already exist. The find_element_by_css_selector methods may need to be changed
to find_element_by_xpath for that to work though.

Input:
driver = selenium web driver object
current_bundle =  dict of the form {'flat_price': 'price as string'
                                          'tags': [tag1, tag2, ...]
                                         'items': {inventory: quantity}

The function opens the inventory adding popup menu, and then once finished closes it.

The process of finding the correct item and then adding the correct quantity gave me the most difficulty.
Initially I was using different methods for finding the html elements for the correct item. The early
methods failed to find the correct html objects somewhat frequently. The method used in this function
appeared to me to be fairly stable. I don't think I had any issues once I started using it.
"""


def bundle_items_add(driver, current_bundle):

    wait()

    # Push button to link inventory
    # scrolls down to make sure link inventory button is visible
    driver.execute_script(
        "window.scrollTo(0, document.body.scrollHeight);")

    link_inventory_button = driver.find_element_by_xpath(
        '//a[text()="Link Inventory"]')
    link_inventory_button.click()

    # loop through inventory and add it to bundle
    for item in current_bundle['items']:
        current_item = current_bundle['items'][item]

        wait(-2)
        # Search for item
        item_search = driver.find_element_by_css_selector(
            '.filter > input:nth-child(1)')
        item_search.send_keys(item)

        wait(-1)
        # Input quantity of item
        item_qty_xpath = f'//label[text()="{item}"]//parent::td[1]//following-sibling::td//child::input'
        try:
            item_qty = driver.find_element_by_xpath(item_qty_xpath)
            item_qty.clear()
            item_qty.send_keys(current_item)
        except:
            item_search.clear()
            wait()

    # Clear search bar
        item_search.clear()
        wait()

    # Click add inventory button. Note that this is outside of the loop.
    wait()
    add_inventory_button = driver.find_element_by_css_selector(
        'button.btn:nth-child(1)')
    add_inventory_button.click()


############################################################
# selects tags for a new or old bundle

"""
Inputs are the same as the bundle_items_add function.

The function will open the sidebar for adding tags. Once it's finished it will not close it.

Tags were the trickiest part and I never found a solution I was really confident in.

I had a lot of issues with finding the correct html elements for tags. In particular when the tag
has the subtag in parentheses.
"""


def bundle_tags_add(driver, current_bundle):

    wait()

    # scroll to the bottom of the page so the add tag button is visible
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Push button to add tags.
    add_tag_button = driver.find_element_by_xpath('//a[text()="Add Tags"]')
    add_tag_button.click()

    # tag search field
    tag_search = driver.find_element_by_xpath('//input[@type="search"]')

    for tag in current_bundle['tags']:
        tag = tag.strip()

        tag_search.clear()
        tag_search.send_keys(tag)

        wait()
        tag_xpath = f'//span[./text()="{tag}"]'
        tag_select = driver.find_element_by_xpath(tag_xpath)
        tag_select.click()


############################################################
# Requests username and password to login.
# Need to have fail case for incorrect username or password

"""
Input is the web driver.

Requests username and password to login, and logs into TapGoods.

Note there are no fail cases/safeguards against entering incorrect usernames or passwords.

All of the html elements are found with CSS selectors, but xpath would be better.
"""


def login(driver):
    # navigate to tg
    driver.get('https://business.tapgoods.com/login')
    driver.maximize_window()

    # enter username
    print('Enter username: ')
    username = input()
    driver.find_element_by_css_selector(
        '#root > div > main > div > div > form > input[type=text]:nth-child(1)').send_keys(username)

    # enter password
    print('Enter password: ')
    password = input()
    driver.find_element_by_css_selector(
        '#root > div > main > div > div > form > input[type=password]:nth-child(2)').send_keys(password)

    # press login button
    driver.find_element_by_css_selector(
        '#root > div > main > div > div > form > input.btn').click()

    wait()


"""
Input is the web driver and optionally the location. Specifically this only really works for Event Rentals.

Asks which location to log into if none is specified, and then chooses that location.

There's probably a more general way to do it by finding the html elements using xpaths.
"""


def loc_selection(driver, loc_arg='none'):
    # navigate to location selection page
    driver.get('https://business.tapgoods.com/selectBusiness')
    wait()

    location = loc_arg

    if location == 'none':

        while location != 'asr' and location != 'csr' and location != 'ssr':
            location = print('Select location - asr, csr, ssr: ')

    if location == 'asr':
        driver.find_element_by_css_selector(
            '#root > div > main > div > div > section:nth-child(2) > button').click()

    elif location == 'csr':
        driver.find_element_by_css_selector(
            '#root > div > main > div > div > section:nth-child(3) > button').click()

    elif location == 'ssr':
        driver.find_element_by_css_selector(
            '#root > div > main > div > div > section:nth-child(4) > button').click()

    else:
        print('Something went wrong in the location selection function')


"""
Input:
driver = selenium web driver object
current_bundle =  dict of the form {'flat_price': 'price as string'
                                          'tags': [tag1, tag2, ...]
                                         'items': {inventory: quantity}
bundle = bundle name as a string

This only fills in the name and either the flat price or the weekly price (I forget).
I meant to expand it to include all other info.
"""


def bundle_form_fill(driver, current_bundle, bundle):
    # driver.get(url for add bundle page) would be optimal
    current_bundle = current_bundle

    # enter bundle name
    bundle_name_field = driver.find_element_by_css_selector(
        '.content > div:nth-child(1) > section:nth-child(1) > ul:nth-child(2) > li:nth-child(4) > a:nth-child(1)')
    bundle_name_field.send_keys(bundle)

    # enter price
    # this is either the weekly or flat price, I forget which
    price_field = driver.find_element_by_css_selector('input.sm:nth-child(10)')
    price_field.send_keys(current_bundle['price'])
