from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
from datetime import datetime
import pandas as pd


errors = []  #save all the errors along the way
season = []


#create a list of every match id fron the past 4 years
season_18_19_games = list(range(38308, 38688))
season_19_20_games = list(range(46605, 46985))
season_20_21_games = list(range(58896, 59276))
season_21_22_games = list(range(66342, 66372))
past_4_years_games_id = season_18_19_games + season_19_20_games + season_20_21_games + season_21_22_games


#extracting the stasitics from the web
for id in past_4_years_games_id:
    # Opening the connection and grabbing the page
    my_url = f'https://www.premierleague.com/match/{id}'

    #modify google chrome security options
    option = Options()
    option.headless = True


    driver = webdriver.Chrome(options=option)
    driver.get(my_url)
    driver.maximize_window()
    sleep(5)

    # Scraping the data
    try:
        cookies = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/section/div/div')))
        webdriver.ActionChains(driver).move_to_element(cookies).click(cookies).perform()
        sleep(1)
        date = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((
                By.XPATH, '//*[@id="mainContent"]/div/section/div[2]/section/div[1]/div/div[1]/div[1]'))).text
        date = datetime.strptime(date, '%a %d %b %Y').strftime('%m/%d/%Y')
        home_team = driver.find_element_by_xpath(
                '//*[@id="mainContent"]/div/section/div[2]/section/div[3]/div/div/div[1]/div[1]/a[2]/span[1]').text
        away_team = driver.find_element_by_xpath(
                '//*[@id="mainContent"]/div/section/div[2]/section/div[3]/div/div/div[1]/div[3]/a[2]/span[1]').text

        scores = driver.find_element_by_xpath(
                '//*[@id="mainContent"]/div/section/div[2]/section/div[3]/div/div/div[1]/div[2]/div/div').text

        home_score = scores.split('-')[0]
        away_score = scores.split('-')[1]

        elem = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="mainContent"]/div/section[2]/div[2]/div[2]/div[1]/div/div/ul/li[3]')))
        webdriver.ActionChains(driver).move_to_element(elem).click(elem).perform()
        sleep(5)

        dfs = pd.read_html(driver.page_source) #r_h : This function returns a list with all tables on the page stored as DataFrames
        stats = dfs[-1] #select the last element in the list

        driver.quit() #scraping is now over, we dont need the driver


    except:
        driver.quit()
        errors.append(id) #save the match id of that made an error
        continue

    # Handling the stats
    home_stats = {}
    away_stats = {}

    home_series = stats[home_team]
    away_series = stats[away_team]
    stats_series = stats['Unnamed: 1']
    #print(stats)


    for row in zip(home_series, stats_series, away_series):
        stat = row[1].replace(' ', '_').lower()
        home_stats[stat] = row[0]
        away_stats[stat] = row[2]

    stats_check = ['possession_%', 'shots_on_target', 'shots', 'touches', 'passes',
                   'tackles', 'clearances', 'corners', 'offsides', 'yellow_cards',
                   'red_cards', 'fouls_conceded']

    for stat in stats_check:
        if stat not in home_stats.keys():
            home_stats[stat] = 0
            away_stats[stat] = 0

    # Storing the data
    match = [date, home_team, away_team, home_score, away_score, home_stats['possession_%'], away_stats['possession_%'],
             home_stats['shots_on_target'], away_stats['shots_on_target'], home_stats['shots'], away_stats['shots'],
             home_stats['touches'], away_stats['touches'], home_stats['passes'], away_stats['passes'],
             home_stats['tackles'], away_stats['tackles'], home_stats['clearances'], away_stats['clearances'],
             home_stats['corners'], away_stats['corners'], home_stats['offsides'], away_stats['offsides'],
             home_stats['yellow_cards'], away_stats['yellow_cards'], home_stats['red_cards'], away_stats['red_cards'],
             home_stats['fouls_conceded'], away_stats['fouls_conceded']]

    season.append(match)
    #print(match)
    print(f'ID {id} scraped.')

# Exporting the data
columns = ['date', 'home_team', 'away_team', 'home_score', 'away_score']
#print(stats_check)
for stat in stats_check:
    columns.append(f'home_{stat}')
    columns.append(f'away_{stat}')

#print(columns)
dataset = pd.DataFrame(season, columns=columns)
dataset.to_csv('Full_statistics.csv', index=False)
print('.csv file exported.')
print(f'Number of errors: {len(errors)}')
print('Errors:\n')
print(errors)
