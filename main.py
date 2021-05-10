import time
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver


HEADLESS_MODE = False
BROWSER_X_POS = 750
BROWSER_Y_POS = 0
BROWSER_X_SIZE = 800
BROWSER_Y_SIZE = 900

weeks = 5
pin_code = 403711
url = "https://www.cowin.gov.in/home"
push_bullet_token = "you push bullet token goes here"


class cowin_ckeck:
    def __init__(self):
        self.notification = ""
        self.service = webdriver.chrome.service.Service('./chromedriver')
        self.service.start()
        options = webdriver.ChromeOptions()
        if HEADLESS_MODE:
            options.add_argument('--headless')
        options = options.to_capabilities()
        print("\t\tLaunching Chrome Driver")
        self.driver = webdriver.Remote(self.service.service_url, options)
        self.driver.set_window_position(BROWSER_X_POS, BROWSER_Y_POS)
        self.driver.set_window_size(BROWSER_X_SIZE, BROWSER_Y_SIZE)
        self.driver.get(url)
        self.driver.implicitly_wait(10)
        page_source = self.driver.page_source

    def check_availability(self, pin_code, weeks):
        search_element = self.driver.find_element_by_id("mat-input-0")
        search_element.send_keys(pin_code)
        button = self.driver.find_element_by_class_name("pin-search-btn")
        button.click()
        time.sleep(2)
        self.driver.execute_script("window.scrollTo(0, 700)")

        master_vaccine_dataframe = pd.DataFrame()
        for i in range(weeks):
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            date_result = soup.find_all('li', attrs={'class': 'availability-date'})

            hostipal_names_result = soup.find_all('h5', attrs={'class': 'center-name-title'})
            hostipal_address_result = soup.find_all('p', attrs={'class': 'center-name-text'})
            row_result = soup.find_all('ul', attrs={'class': 'slot-available-wrap'})

            hostipal_names = []
            hostipal_addresses = []
            current_dates = []

            for date in date_result:
                current_dates.append(date.text)

            for hospital in hostipal_names_result:
                hostipal_names.append(hospital.text)

            for hospital_address in hostipal_address_result:
                hostipal_addresses.append(hospital_address.text)

            all_tag_list = []

            for row in row_result:
                als = row.find_all('li')
                row_wise_list = []
                for al in als:
                    row_wise_list.append(al.div.text)
                all_tag_list.append(row_wise_list)

            print("\n**********************************************************************************\n")

            print(hostipal_names, "\n", "SIZE:{}".format(len(hostipal_names)))
            print(hostipal_addresses, "\n", "SIZE:{}".format(len(hostipal_addresses)))
            print(all_tag_list, "\n", "SIZE:{}".format(len(all_tag_list)))

            columns_list = current_dates[i * 6: (i * 6) + 6]
            vaccine_data = pd.DataFrame(index=hostipal_names, columns=columns_list)

            for x in range(len(hostipal_names)):
                vaccine_data.loc[hostipal_names[x]] = all_tag_list[x]

            master_vaccine_dataframe = pd.concat([master_vaccine_dataframe, vaccine_data], axis=1)

            print(vaccine_data)
            print(master_vaccine_dataframe)

            next_button = self.driver.find_element_by_class_name("right.carousel-control.carousel-control-next")
            next_button.click()
            time.sleep(0.5)

        print("check")
        master_vaccine_dataframe.index.name = "Hospital"
        master_vaccine_dataframe.to_csv('Vaccine_Data_{}week_pin{}.csv'.format(weeks, pin_code))
        for i in range(weeks):
            next_button = self.driver.find_element_by_class_name("left.carousel-control.carousel-control-prev")
            next_button.click()
        self.driver.execute_script("window.scrollTo(0, 0)")

    def close_browser(self):
        self.driver.quit()

    def extract_vaccine_avail_info(self):
        df2 = pd.read_csv('Vaccine_Data_{}week_pin{}.csv'.format(weeks, pin_code))
        dates = df2.columns
        dates = dates[1:len(dates)]
        available_df = pd.DataFrame()

        for date in dates:
            newdf2 = df2[df2[date].astype(str).str.contains("Booked|NA", na=True) == False][["Hospital", date]]
            newdf2.set_index("Hospital", inplace=True)
            available_df = pd.concat([available_df, newdf2], axis=1)

        available_df.dropna(axis=1, how='all', inplace=True)
        dates = available_df.columns

        data = [str(available_df[dates[j]][i]) + " available at " + str(available_df.index[i] + " on " + dates[j])
                for i in range(len(available_df.index))
                for j in range(len(dates))
                if str(available_df[dates[j]][i]) != "nan"]

        self.notification = ""
        for i in range(len(data)):
            self.notification = self.notification + "-->" + data[i] + "\n\n"

        print(self.notification)

    def send_bullet_notification(self):

        if len(self.notification) > 0:
            self.notification = "Vaccine availaibility - PIN:{}\n\n".format(
                pin_code) + self.notification + "\n\n" + "BOOK NOW, thank me later - karthik ram"
            self.pushbullet_message("COWIN WEBSCAPPER", self.notification)
        else:
            self.notification = "Vaccine availaibility - PIN:{}\n\n".format(pin_code) + "No vaccines found :/"
            print(self.notification)

    def pushbullet_message(self, title, body):
        msg = {"type": "note", "title": title, "body": body}
        TOKEN = push_bullet_token
        resp = requests.post('https://api.pushbullet.com/v2/pushes',
                             data=json.dumps(msg),
                             headers={'Authorization': 'Bearer ' + TOKEN,
                                      'Content-Type': 'application/json'})
        if resp.status_code != 200:
            raise Exception('Error', resp.status_code)
        else:
            print('Message sent')


CA = cowin_ckeck()

while True:
    # extracts all data and stores it as a csv
    CA.check_availability(pin_code, weeks)

    # extracts only avialble vaccine info and stores it in a string variable
    CA.extract_vaccine_avail_info()

    # sends notification as a buttle notification to all registered devices, requires an app
    CA.send_bullet_notification()

    # checks every 5 minutes
    time.sleep(300)

print("stop")
