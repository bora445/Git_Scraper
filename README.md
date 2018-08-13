# Git_Scraper
Scraper exersize
This project runs scraper on GitHub pages, searches for "selenium", saves corresponding results and conducts link verification
------------------------------------------------------------------------------------------------------------------------------
Installation and run instructions:

Run Selenium Docker with following parameters:
***Befoure running this replace mapped folder path [c:/dev/selenium] in docker run command with folder path to you host***

	Run on host: docker run --name seleniumContainer --shm-size=2g -it -v c:/dev/selenium:/usr/share/Selenium/data joyzoursky/python-chromedriver:3.6-alpine3.7-selenium

	Install following packages with pip install: pymongo, requests

Run mongoDB docker with following parameters:

	docker run -d --name my_mongo mongo
	run mongoDB on mongo console with command: mongo


Create user-defined bridge ->run on your host: 

	docker network create mynet

Map your containers to the bridge:

	On selenium docker run: docker network connect mynet seleniumContainer
	On mongoDB  docker run: docker network connect mynet my_mongo

To run the scraper:

	Place scraper.py file in your mapped folder
	
	Run from selenium console: python /usr/share/Selenium/data/scraper.py
	
View results in selenium console

Have FUN!
