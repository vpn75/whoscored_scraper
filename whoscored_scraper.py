from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from pandas import DataFrame, Series
from bs4 import BeautifulSoup
from datetime import datetime as dt
from urllib.parse import unquote

class WhoScored_scraper(object):
	def __init__(self, team, league):
		self.base_url = 'https://whoscored.com/'
		self.team_url = ''
		
		self.team = team #Specify team whose player ratings are being scrape
		
		self.league_urls = {
								'EPL': 'https://www.whoscored.com/Regions/252/Tournaments/2/England-Premier-League',
								'LaLiga': 'https://www.whoscored.com/Regions/206/Tournaments/4/Spain-LaLiga',
								'Bundesliga': 'https://www.whoscored.com/Regions/81/Tournaments/3/Germany-Bundesliga',
								'SerieA': 'https://www.whoscored.com/Regions/108/Tournaments/5/Italy-Serie-A',
								'Ligue1': 'https://www.whoscored.com/Regions/74/Tournaments/22/France-Ligue-1'
							}

		self.comps = {
						'EPL': 'EPL',
						'LaLiga': 'SLL',
						'Bundesliga': 'GB',
						'SerieA': 'ISA',
						'Ligue1': 'FL1'
					}

		self.colnames = [
							'name',
							'competition',
							'match_date',
							'opponent',
							'match_location',
							'home_goals',
							'away_goals',
							'result',
							'minutes_played',
							'rating'
						]

		#self.teams_to_scrape = ['Liverpool','Arsenal','Manchester City','Manchester United','Chelsea','Tottenham']
		if league not in self.league_urls.keys():
			raise KeyError('Class called with invalid league-name!')
		else:
			self.url = self.league_urls[league]
			self.comp = self.comps[league]

		self.player_urls = []
		self.player_names = []

		chrome_options = webdriver.ChromeOptions()
		chrome_options.add_argument('--incognito') #Open Chrome browser in 'incognito' mode
		chrome_options.add_argument('--headless')
		self.driver = webdriver.Chrome(chrome_options=chrome_options)

		self.team_url_xpath = '//*[@id="standings-17590-content"]/tr[*]/td[2]/a'
		self.player_url_xpath = '//*[@id="player-table-statistics-body"]/tr[*]/td[3]/a'
		self.result_xpath = '//*[@id="player-fixture"]/tbody//tr[*]/td[4]/a'
		self.comp_xpath = '//*[@id="player-fixture"]/tbody/tr[*]/td[1]/span/a'
		self.match_date_xpath = '//*[@id="player-fixture"]/tbody/tr[*]/td[2]'
		self.away_team_xpath = '//*[@id="player-fixture"]/tbody/tr[*]/td[5]/a'
		self.home_team_xpath = '//*[@id="player-fixture"]/tbody/tr[*]/td[3]/a'
		self.mins_played_xpath = '//*[@id="player-fixture"]/tbody/tr[*]/td[8]'
		self.rating_xpath = '//*[@id="player-fixture"]/tbody/tr[*]/td[9]'
		self.all_matches = []

	
	def get_team_urls(self):
		driver = self.driver
		try:
			driver.get(self.url)
			soup = BeautifulSoup(driver.page_source, 'lxml')
			tables = soup.find_all('table')
			links = tables[5].find_all('a', {'class': 'team-link'})
			for link in links:
				if link.text.strip() == self.team:
					self.team_url = self.base_url + link['href']

		except TimeoutException:
			print('Connection to WhoScoredcom timed out. Please try running the script again.')
		finally:
			print('Found Team URL for ', self.team)



	def get_player_urls(self, **kwargs):
		driver = self.driver
		driver.get(self.team_url)
		soup = BeautifulSoup(driver.page_source, 'lxml')
		table = soup.find_all('table')
		links = table[3].find_all('a', {'class': 'player-link'})

		p_urls = [self.base_url + link['href'].replace('Show','Fixtures') for link in links]
		
		if len(p_urls) > 0:
			self.player_urls = Series(p_urls).unique()
			print('Successfuly scraped player URLs for {}!'.format(self.team))

	def set_player_names(self, **kwargs):
		"""Parses out player-name from scraped player-urls"""
		for url in self.player_urls:
			pname = url.split('/')[7].replace('-', ' ')
			self.player_names.append(unquote(pname))
		#print(self.player_names)

	def set_match_location(self, home_team, **kwargs):
		match_location = 'Home' if home_team == self.team else 'Away'
		return match_location

	def set_match_opponent(self, home_team, away_team, player_team, **kwargs):
		opponent = away_team if home_team == player_team else home_team
		return opponent

	def set_match_score(self, result, **kwargs):
		home_goals, away_goals = result.split(':')
		home_goals = int(home_goals.strip())
		away_goals = int(away_goals.strip())

		return home_goals, away_goals

	def set_match_result(self, home_team, away_team, home_goals, away_goals, **kwargs):
		home_goals = int(home_goals)
		away_goals = int(away_goals)
		if home_team == self.team:
			if home_goals > away_goals: 
				result = 'W'
			elif home_goals == away_goals:
				result = 'D'
			else: result = 'L'
		else:
			if away_goals > home_goals: 
				result = 'W'
			elif away_goals < home_goals: 
				result = 'L'
			else: result = 'D'
		return result

	def scrape_player_info(self, **kwargs):
		driver = self.driver
		
		for i, url in enumerate(self.player_urls):
			driver.get(url)
			print('Scraping ratings for player {} from {}'.format(self.player_names[i], self.team))
			comps = driver.find_elements_by_xpath(self.comp_xpath)
			match_dates = driver.find_elements_by_xpath(self.match_date_xpath)
			home_teams = driver.find_elements_by_xpath(self.home_team_xpath)
			away_teams = driver.find_elements_by_xpath(self.away_team_xpath)
			results = driver.find_elements_by_xpath(self.result_xpath)
			mins_played = driver.find_elements_by_xpath(self.mins_played_xpath)
			ratings = driver.find_elements_by_xpath(self.rating_xpath)
			
			player_detail = []
			player_detail.append(self.player_names[i])

			for comp, match_date, home_team, away_team, result, min_played, rating in zip(comps, match_dates, home_teams, away_teams, results, mins_played, ratings):
				r = result.get_attribute('text')
				c = comp.get_attribute('text')
				ht = home_team.get_attribute('text')
				awt = away_team.get_attribute('text')
				md = match_date.get_attribute('innerHTML')
				mp = min_played.get_attribute('innerHTML').strip().replace("'", "")
				rt = rating.get_attribute('innerHTML')
				
				if c == self.comp: #Filter ratings to specified competition
					#name = self.set_player_name(url)
					match_location = self.set_match_location(ht)
					home_goals, away_goals = self.set_match_score(r)
					opponent = self.set_match_opponent(ht,awt, self.team)
					outcome = self.set_match_result(ht, awt, home_goals, away_goals)                      
					rt = float(rt.strip())

					self.all_matches.append(player_detail + [c, md, opponent, match_location, home_goals, away_goals, mp, outcome, rt])         

		print('Finished scraping player-URLs for {}!'.format(self.team))
		print('Total matches scraped: {}'.format(len(self.all_matches)))
		

	def do_work(self):
		self.get_team_urls()

		if self.team_url == '':
			raise Exception('No valid team URL found for:', self.team)
			self.driver.quit()
		
		self.get_player_urls()

		if len(self.player_urls) == 0:
			raise Exception('No valid player URLs were found for:', self.team)
			self.driver.quit()

		self.set_player_names()
		self.scrape_player_info()	
	
		if len(self.all_matches) > 0:
			self.write_to_csv()
			self.driver.quit()
		else:
			raise Exception("There was an issue scraping player-ratings!")
			self.driver.quit()

	def write_to_csv(self):
		today = dt.strftime(dt.today(), '%Y%m%d')
		csv_filename = '{}_{}_player_ratings_{}.csv'.format(self.team, self.comp, today)
		df = DataFrame(self.all_matches)
		df.columns = self.colnames
		df.to_csv(csv_filename, index=False)
		print('Player ratings for {} successfully written to filename: {}'.format(self.team, csv_filename))
