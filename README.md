# TapGoods-bundle-input
Script I made to input Event Rentals bundles into TapGoods.

This isn't the script I actually used when I was inputting our bundles.
In theory, this one should work better because it doesn't have some flaws
that the one I actually used did.

Note that since I no longer have access to TapGoods that I didn't actually test
this script. It's possible there are some problems I missed that wouldn't show up
to me as an error in my editor, but could keep it from working.

The program works by first combining the data in the 2 excel spreadsheets in the
repository. bundles_sheet.xlsx has the name of the bundle plus all other info about
the bundle in a row. items_sheet.xlsx contains all of the data about which inventory
goes into each bundle. I did it this way because I happened to have both of those
spreadsheets, so I didn't need to reformat anything. The program combines the data
into a dictionary.

After the data is consolidated, the program uses Selenium to launch a browser and navigate to TapGoods,
log in, and then choose a location. From there it navigates to the add bundle page.
It then loops through the dictionary of the bundle data filling out the information for
the bundle, and submitting it. After submition, the back button on the browser is pressed.
This will return you to the bundle add page with nothing filled in.

I think a better way than pushing the back button is to use driver.get('url for add bundle page')
either at the beginning of the loop, or at the beginning of the bundle_form_fill function.
However, I didn't think of that until after I no longer had access to TapGoods to get the url.

bundle_input_script.py is the file that contains the script that performs everything. It
essentially just launches the Selenium webdriver and calls functions in TapGoods_functions.py.

TapGoods_functions.py contains the bulk of the code that actually does anything.

Some notes:
1. My original script required a lot of babysitting. Basically, since it requires
   finding html elements that load dynamically, it can randomly have issues finding
   an element because the page took too long to load. I assume with some error handling
   hat can be fixed, but I was pretty crunched on time and don't have much experience with
   that so I just rolled with it. I put pauses in the places where there were the most
   issues, and set an implicit wait of 10 seconds which helped.
   
2. It still takes a decent amount of time to run. I was running it almost nonstop for a
   a good week to week and a half. This script should work faster than the one I used
   because I changed the method for finding the html element for the quantity input box
   of the inventory items.
   
3. I had a lot of issues with tags. In my original implementation I couldn't get it to
   find some specific tags, and actually ended up tagging a lot of things as "Flooring"
   or something just because I knew I could get that to work. I also didn't bother
   attempting to give multiple tags. The bundle_tags_add is the function I have the least
   confidence in.

Things I wanted to implement but didn't:
1. Error handling. Especially for the errors that arise when html elements can be found,
   which currently will crash the program.
   
2. A good way to log what was done/missed. In my orinal implementation I had some janky
   methods of logging the items that were missed in a bunddle to a spreadsheet, but they
   didn't work well so I removed them.
   
3. The bundle_form_fill function filling in all information for the bundle except the
   inventory and tags. I wanted to at least add this functionality before I sent it to
   you, but I no longer have access so I can't find the xpaths for the html elements.
   
4. Change the method for finding html elements from CSS selectors to xpaths. When I first
   started the project I didn't know how xpaths worked, and so for a lot of things I just
   copied the CSS selector from the developer tools.


