# Club Luv Webscraper
Scraper to get all the power rankings info off IMLeagues and into our spreadsheet yay!!

Details:
 - In python 3.7
 - It uses webdriver to handle the javascript rendering and setting the view to the whole season (god such a pain in my ass) and BeautifulSoup to parse the html (more annoying that with just webdriver, but faster). 

Setup:
`pip install selenium`
`pip install bs4`
download chrome webdriver (http://chromedriver.chromium.org/downloads) and move the executable into a folder on your $PATH

Exporting details:
 - Used pyinstaller to package into a single file with a spec file (Imleagues_Webscraper.spec)
 - F flag puts it in a single file
`pip install pyinstaller`
`pyinstaller -F Imleagues_Webscraper.spec Imleagues_Webscraper.py`  
