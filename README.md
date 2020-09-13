# Club Luv Webscraper
Scraper to get all the power rankings info off IMLeagues and into our spreadsheet yay!!

Details:
 - In python 3.7
 - It uses webdriver to handle the javascript rendering and setting the view to the whole season (god such a pain in my ass) and BeautifulSoup to parse the html (more annoying that with just webdriver, but faster). 
 - It uses pyinstaller to package everything into a single executable

Setup:\
`pip install selenium`\
`pip install bs4`\
`pip install pyinstaller`\
download chrome webdriver (http://chromedriver.chromium.org/downloads) and move the executable into a folder on your $PATH (preferably /usr/local/bin/ if not then update the spec binaries line with its location)

Exporting details:
 - Needs the spec file (Imleagues_Webscraper.spec)
 - F flag puts it in a single file\
`pyinstaller -F Imleagues_Webscraper.spec Imleagues_Webscraper.py`\
`cp dist/web_scraper .; zip web_scraper.zip web_scraper`
