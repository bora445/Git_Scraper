import unittest
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import requests
from pymongo import MongoClient
from selenium.webdriver.common.keys import Keys
from pprint import pprint


num_of_pages = 5         ###num of pages to scan
mong = 'my_mongo'        ### mongoDB container name


# mongoDB initialisation
client = MongoClient(mong, 27017)
db = client['pymongo_test']
posts = db.posts


class MyTest(unittest.TestCase):

    def check_exists_by_xpath(self, xpath):  ###check if xpath exists (for optional elements)
        try:
            self.driver.find_element_by_xpath(xpath)
        except NoSuchElementException:
            return False
        return True
        pass


    def setUp(self):
        """Start web driver"""
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.set_window_size(3840, 2160)
        self.driver.implicitly_wait(10)

    def tearDown(self):
        """Stop web driver"""
        self.driver.quit()

    def test_case_1(self):
        """Scraper Running"""

        try:
            # Open github page
            self.driver.get('https://github.com/search?')
            search_input = self.driver.find_element_by_xpath('//*[@id="search_form"]/div/div/input[1]')

            # Run search for selenium
            search_input.send_keys("selenium")
            search_input.submit()
            time.sleep(5)
            # self.driver.save_screenshot('/usr/share/Selenium/data/after_selenium_search.png') ##Optional for debugging

            res = 0   ###Results counter

            for i in range(num_of_pages):
                for x in range(1, 11):

                    # Link and Title search
                    result = self.driver.find_element_by_xpath('//*[@id="js-pjax-container"]/div/div[3]/div/ul/div[%s]/div[1]/h3/a'%x)
                    rep = (result.get_attribute('href'))
                    headline = result.text

                    # Description tag search
                    elm_p = '//*[@id="js-pjax-container"]/div/div[3]/div/ul/div[%s]/div[1]/p'%x
                    if self.check_exists_by_xpath(elm_p):
                        description_result = self.driver.find_element_by_xpath(elm_p)
                        desc = description_result.text
                    else:
                        desc = ' '

                    # Tags search
                    tags_result = self.driver.find_element_by_xpath('//*[@id="js-pjax-container"]/div/div[3]/div/ul/div[%s]/div[1]/div[1]'%(x))
                    tagtag = tags_result.find_elements_by_tag_name("a")
                    tags = [j.text for j in tagtag]

                    # Time tag search
                    update_time = self.driver.find_elements_by_xpath("//div/*[contains(text(), 'Updated')]")
                    tm = []
                    for u in update_time:
                        tm.append(u.text)
                    updated = tm[x - 1]

                    # Language tag search
                    language_result = self.driver.find_element_by_xpath('//*[@id="js-pjax-container"]/div/div[3]/div/ul/div[%s]/div[2]/div[1]'%x)
                    language = language_result.text

                    # Score tag search
                    stars_result = self.driver.find_element_by_xpath('//*[@id="js-pjax-container"]/div/div[3]/div/ul/div[%s]/div[2]/div[2]/a'%x)
                    stars = stars_result.text

                    # Insert to mongoDB
                    results_dict = {'Title': headline, 'Repo_link': rep, 'Description': desc, 'Tags': tags, 'Language': language, 'Update_Time': updated, 'Ranking': stars}
                    posts.insert_one(results_dict)

                    res += 1
                    print('Result %s scanned, Title: %s' % (res, headline))
                self.driver.find_element_by_class_name('next_page').click()
                time.sleep(5)
                # self.driver.save_screenshot('/usr/share/Selenium/data/after_click.png') ###Optional for debugging

            # Print collection content
            cursor = posts.find()
            print('\n\n')
            print('Printing collected results from DB:')
            print('\n')
            for k in cursor:
                pprint(k)
                print('\n\n')

        except NoSuchElementException as ex:
            self.fail(ex.msg)

    def test_case_2(self):
        """Navigation timing test"""

        try:
            for post in posts.distinct("Repo_link"):
                self.driver.get(post)
                navigationstart = self.driver.execute_script("return window.performance.timing.navigationStart")
                responsestart = self.driver.execute_script("return window.performance.timing.responseStart")
                domcomplete = self.driver.execute_script("return window.performance.timing.domComplete")
                query_time = responsestart - navigationstart
                pageload_time = domcomplete - responsestart
                r = requests.get(post)
                pprint("For link %s: Search query time:%sms| Page load time:%sms| Response code is %s" % (post, query_time, pageload_time, r.status_code))
                # print('\n')
                time.sleep(1)

        except NoSuchElementException as ex:
                        self.fail(ex.msg)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(MyTest)
    unittest.main(verbosity=2).run(suite)


