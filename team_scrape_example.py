from whoscored_scraper import *

team = 'Arsenal'
league = 'EPL' #Supported leagues: EPL, Bundesliga, Ligue1, LaLiga, SerieA

scraper = WhoScored_scraper(team, league)
scraper.do_work()

