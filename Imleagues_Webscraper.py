import datetime
import os
import sys

from bs4 import BeautifulSoup
from bs4.element import Tag
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


# get a tag with the given class name from a list of children
def get_tag(tag, className=None):
    if className is None:
        return next((x for x in tag.contents if isinstance(x, Tag)))
    else:
        return next((x for x in tag.contents if isinstance(x, Tag) and className in x.attrs['class']))


if __name__ == '__main__':
    # gets date to check if games have been played yet
    now = datetime.datetime.now()

    # launches webdriver in chrome
    chrome_options = Options()
    # makes it so the window doesn't actually open
    chrome_options.add_argument('--headless')
    if getattr(sys, 'frozen', False):
        # if executed as a bundled exe, fetch the driver is in the extracted folder
        chromedriver_path = os.path.join(sys._MEIPASS, 'chromedriver')
        driver = webdriver.Chrome(chromedriver_path, options=chrome_options)

        # get current directory
        filename = os.path.dirname(sys.executable)
    else:
        # if executed as a simple script, the driver should be in `PATH`
        driver = webdriver.Chrome(options=chrome_options)

        # get current directory
        filename = os.path.dirname(__file__)

    try:
        # get url if saved else ask for it
        filename += os.path.sep + 'url.txt'
        if os.path.isfile(filename):
            with open(filename, 'r') as f:
                url = f.readline()

            print('\n\n---------------------------- IMLeagues Webscraper ----------------------------')
            print('Loading (sorry IMLeagues is slow) ...')
        else:
            url = input('\nIMLeagues Link: ')

            print('\n\n---------------------------- IMLeagues Webscraper ----------------------------')
            print('Loading (sorry IMLeagues is slow) ...')

            # get the URL the user gave
            driver.get(url)
            # wait until page has loaded
            WebDriverWait(driver, 5).until_not(
                expected_conditions.visibility_of_element_located((By.ID, 'loadingScreen')))

            # parse html
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            divisions = soup.find_all('div', class_='iml-panel-1', attrs={'ng-repeat-start': 'division in initData.divisionTeams'})
            if not divisions:
                raise NoSuchElementException
            else:
                print('\n\n----------------------- TEAMS TO COPY TO THE EXCEL DOC -----------------------')
                for division in divisions:
                    name = division.find('a', attrs={'ng-bind': 'division.name'}).text
                    for team in division.find('table', class_='team-list').find_all('a', class_='iml-team-name'):
                        print(name + '\t' + team.text)
            print('\n\nLoading (sorry IMLeagues is so very slow) ...')

            # reset url
            url = url.rsplit('/', 1)[0] + '/managegames'

        # get the URL the user gave
        driver.get(url)

        # select the whole season
        # wait until page has loaded
        WebDriverWait(driver, 5).until_not(
            expected_conditions.visibility_of_element_located((By.ID, 'loadingScreen')))
        # click the dropdown
        driver.find_element_by_xpath('//button[@data-id=\'selectView\']').click()
        # click whole season
        driver.find_element_by_xpath('//li[@data-original-index=\"4\"]/a').click()
        # wait for it to reload
        WebDriverWait(driver, 30).until_not(
            expected_conditions.presence_of_element_located((By.CLASS_NAME, 'blockPage')))

        # parse html
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()

        games_complete = []
        # games to do manually
        games_incomplete = []

        # get all game elements
        games = soup.find_all('div', {'class': 'iml-game-info'})

        for game in games:
            try:
                # get school on the left
                school1Body = get_tag(get_tag(game, 'iml-team-left'), 'media-body')
                school1 = get_tag(school1Body, 'media-heading').text
                # get school on the right
                school2Body = get_tag(get_tag(game, 'iml-team-right'), 'media-body')
                school2 = get_tag(school2Body, 'media-heading').text

                if 'Forfeit' in school1Body.text:
                    # school1 forfeited
                    games_complete.append(f'{school1},F,,{school2}')
                    continue
                elif 'Forfeit' in school2Body.text:
                    # school2 forfeited
                    games_complete.append(f'{school1},,F,{school2}')
                    continue

                result_tag = get_tag(get_tag(game, 'iml-game-result'))
                if 'status' in result_tag.attrs['class']:
                    # game doesn't have a result
                    if result_tag.text != 'FINAL':
                        # fetch the date from parent elements
                        dateSplit = get_tag(get_tag(game.parent.parent, 'searchSportLeagueDivision'),
                                            'tdGameDay').text.split('/')
                        if int(dateSplit[0]) < now.month or (
                                int(dateSplit[0]) == now.month and int(dateSplit[1]) < now.day):
                            # date has passed
                            games_incomplete.append(f'NO SCORE: {school1} vs {school2}')
                        continue
                else:
                    # get the score from the result
                    score1 = get_tag(get_tag(result_tag), 'match-team1Score').text
                    score2 = get_tag(get_tag(result_tag), 'match-team2Score').text
                    if score1.isdigit() and score2.isdigit():
                        games_complete.append(f'{school1},{score1},{score2},{school2}')
                        continue

                games_incomplete.append(f'IDK MATE: {school1} vs {school2}')
            except StopIteration:
                # such a whack result, it couldn't be parsed
                games_incomplete.append('IDK MATE: {}'.format(game.text.replace('\n', ' ')))

        print('\n\n----------------------- GAMES TO COPY TO THE EXCEL DOC -----------------------')
        print('School 1\tScore 1\tScore 2\tSchool 2')
        print('\n'.join(games_complete))
        print('\n\n-------------------------- GAMES TO REVIEW MANUALLY --------------------------')
        print('\n'.join(games_incomplete))

        # save url
        with open(filename, 'w') as f:
            f.write(url)

    except (NoSuchElementException, WebDriverException) as e:
        print('URL not working. Double check it\'s the right one and rerun.')
