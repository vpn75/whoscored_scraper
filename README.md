# WhoScored Scraper
This python package allows you to scrape football player-ratings from [WhoScored.com](https://whoscored.com)

## Dependencies
* [Selenium](https://selenium-python.readthedocs.io/getting-started.html) package used to simulate opening site in browser to avoid getting flagged as a bot
* BeautifulSoup used for actual web-scraping
* Pandas used to write resulting DataFrame to csv file.

You will also need to install the [Chrome driver](http://chromedriver.storage.googleapis.com/index.html) and place it in same PATH as your python executable.

Full dependencies documented in `requirements.txt` file. To install required dependencies, run the following command from a virtual environment created to run the package:

```pip install -r requirements.txt```
