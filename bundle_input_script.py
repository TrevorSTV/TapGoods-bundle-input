import TapGoods_functions as tg

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains

bundles = tg.bundle_data_structure_format(
    'bundles_sheet.xlsx', 'items_sheet.xlsx')

driver = webdriver.Chrome()
driver.implicitly_wait(10)

tg.login(driver)

tg.loc_selection(driver)

"""
The next few lines is how I navigated to the add bundle page.
It's better to do this with driver.get(url) if possible.

I didn't think to do that when I was originally inputting our bundles, and I can no longer access TapGoods to get the url, so this is what I've got.
"""
############################################
# non-optimal navigation to add bundle page

tg.wait()

# Find and click the inventory button on the toolbar.
inventory_button = driver.find_element_by_css_selector(
    '.inventoryMenu > a:nth-child(1)')
inventory_button.click()

tg.wait()

# Find and click on add bundle button in inventory menu.
add_bundle_button = driver.find_element_by_css_selector(
    '.content > div:nth-child(1) > section:nth-child(1) > ul:nth-child(2) > li:nth-child(4) > a:nth-child(1)')
add_bundle_button.click()

# end of navigation to add bundle page
############################################

for bundle in bundles:
    current_bundle = bundles[bundle]

    tg.bundle_form_fill(driver, current_bundle, bundle)
    tg.bundle_items_add(driver, current_bundle)
    tg.bundle_tags_add(driver, current_bundle)
    driver.back()
