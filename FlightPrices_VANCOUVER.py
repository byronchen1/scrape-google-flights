import pandas as pd
import numpy as np
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class Flightbot:
    def __init__(self, DEPARTURE_LOCATION, DEPARTURE_DATE, ONE_WAY=False):
        self.driver = webdriver.Chrome()
        self.DEPARTURE_LOCATION = DEPARTURE_LOCATION
        self.DEPARTURE_DATE = DEPARTURE_DATE
        self.driver.get("https://www.google.com/flights?hl=en")
        self.driver.set_page_load_timeout(5)
        self.driver.maximize_window()
        self.driver.implicitly_wait(5)
        time.sleep(2)
        if ONE_WAY:
            self.driver.find_element_by_xpath("//span[contains(text(), 'Round trip')]").click()
            self.driver.find_element_by_xpath("//span[contains(text(), 'One-way')]").click()
        # Departing Location
        Dep_Loc_XPATH = r'//*[@id="flt-app"]/div[2]/main[1]/div[4]/div/div[3]/div/div[2]/div[1]'
        self.driver.find_element_by_xpath(Dep_Loc_XPATH).click()
        self.driver.find_element_by_xpath("//input[@placeholder=\"Where from?\"]").clear()
        time.sleep(2)
        self.driver.find_element_by_xpath("//input[@placeholder=\"Where from?\"]").send_keys(DEPARTURE_LOCATION)
        time.sleep(2)
        # First Option
        self.driver.find_element_by_xpath("//div[@id=\"sbse0\"]").click()

    def arriving(self, ARRIVAL_LOCATION):
        # Arriving Location
        Arv_Loc_XPATH = r'//*[@id="flt-app"]/div[2]/main[1]/div[4]/div/div[3]/div/div[2]/div[2]'
        self.driver.find_element_by_xpath(Arv_Loc_XPATH).click()
        self.driver.find_element_by_xpath("//input[@placeholder=\"Where to?\"]").clear()
        time.sleep(2)
        self.driver.find_element_by_xpath("//input[@placeholder=\"Where to?\"]").send_keys(ARRIVAL_LOCATION)
        time.sleep(1)
        # First Option
        self.driver.find_element_by_xpath("//div[@id=\"sbse0\"]").click()
        time.sleep(2)

    def departure_date(self, DEPARTURE_DATE):
        # Departing date
        Dep_Date_XPATH = r'//*[@id="flt-app"]/div[2]/main[1]/div[4]/div/div[3]/div/div[2]/div[4]/div[1]'
        self.driver.find_element_by_xpath(Dep_Date_XPATH).click()
        self.driver.find_element_by_xpath("//input[@placeholder=\"Departure date\"]").clear()
        time.sleep(1)
        self.driver.find_element_by_xpath("//input[@placeholder=\"Departure date\"]").send_keys(DEPARTURE_DATE)
        self.driver.find_element_by_xpath("//input[@placeholder=\"Departure date\"]").send_keys(Keys.ENTER)
        time.sleep(3)

    def view_specific_month(self, CURR_MONTH_NUM, ARRIVAL_LOCATION):
        data = []
        Inc_Days_Btn = r'//*[@id="flt-modaldialog"]/div/div[5]/div[2]/div[1]/jsl[3]/span[4]'
        Dec_days_Btn = r'//*[@id="flt-modaldialog"]/div/div[5]/div[2]/div[1]/jsl[3]/span[2]'
        self.driver.find_element_by_xpath(Dec_days_Btn).click()
        time.sleep(2)
        #3 to 5 day trip
        for h in range(3):
            # Maximum of 5 weeks per month
            for i in range(5):
                # Maximum of 7 days per week
                for j in range(7):
                    try:
                        the_date = fr'//*[@id="flt-modaldialog"]/div/two-month-calendar/div/div/calendar-month[{CURR_MONTH_NUM - 2}]/calendar-week[{i + 1}]/calendar-day[{j + 1}]/div[3]'
                        the_price = fr'//*[@id="flt-modaldialog"]/div/two-month-calendar/div/div/calendar-month[{CURR_MONTH_NUM - 2}]/calendar-week[{i + 1}]/calendar-day[{j + 1}]/div[4]/span[1]'
                        date_num = self.driver.find_element_by_xpath(the_date).text
                        price_num = self.driver.find_element_by_xpath(the_price).text
                        data.append([ARRIVAL_LOCATION, CURR_MONTH_NUM, date_num, price_num, h+3])
                    except:
                        pass
            self.driver.find_element_by_xpath(Inc_Days_Btn).click()
            time.sleep(2)

        return data

    def close_browser(self):
        # Close Chrome
        self.driver.quit()


if __name__ == "__main__":
    ### VARIABLES ###

    # Desired month to view
    CURR_MONTH_NUM = 4  # Apr = 4, July = 7 , Dec = 12 , Jan = 13, Feb = 2

    DESTINATIONS = 'VANCOUVER'
    DEPARTURE_LOCATION = 'TORONTO'

    ### NO CHANGE REQ ###
    DEPARTURE_DATE = pd.datetime(2020, CURR_MONTH_NUM, 11).strftime('%a, %d %b')
    CurrDate = pd.datetime.today().strftime('%Y%m%d')
    appended_data = []
    #####################

    MY_BOT = Flightbot(DEPARTURE_LOCATION=DEPARTURE_LOCATION,
                       DEPARTURE_DATE=DEPARTURE_DATE,
                       ONE_WAY=False)
    try:
        MY_BOT.arriving(ARRIVAL_LOCATION=DESTINATIONS)
        MY_BOT.departure_date(DEPARTURE_DATE=DEPARTURE_DATE)

        # Returns DF
        myData = MY_BOT.view_specific_month(CURR_MONTH_NUM=CURR_MONTH_NUM,
                                            ARRIVAL_LOCATION=DESTINATIONS)

        data = pd.DataFrame(np.array(myData), columns=['Location', 'Month', 'Day', 'Price', 'TotalDays'])
        appended_data.append(data)
    except:
        pass
    # Finished
    appended_data = pd.concat(appended_data)
    appended_data.to_csv(fr'{DESTINATIONS}PricesAsAt{CurrDate}.csv', index=False)

    MY_BOT.close_browser()
