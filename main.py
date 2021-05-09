import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
from selenium import webdriver

HEADLESS_MODE = False
BROWSER_X_POS = 750
BROWSER_Y_POS = 0
BROWSER_X_SIZE = 800
BROWSER_Y_SIZE = 900

url = "https://www.cowin.gov.in/home"


def check_availability(pin_code):
    service = webdriver.chrome.service.Service('./chromedriver')
    service.start()
    options = webdriver.ChromeOptions()
    if HEADLESS_MODE:
        options.add_argument('--headless')
    options = options.to_capabilities()
    print("\t\tLaunching Chrome Driver")
    driver = webdriver.Remote(service.service_url, options)
    driver.set_window_position(BROWSER_X_POS, BROWSER_Y_POS)
    driver.set_window_size(BROWSER_X_SIZE, BROWSER_Y_SIZE)
    driver.get(url)
    driver.implicitly_wait(10)
    page_source = driver.page_source
    search_element = driver.find_element_by_id("mat-input-0")
    search_element.send_keys(pin_code)
    button = driver.find_element_by_class_name("pin-search-btn")
    button.click()
    time.sleep(2)
    driver.execute_script("window.scrollTo(0, 700)")

    master_vaccine_dataframe = pd.DataFrame()
    weeks = 5
    for i in range(weeks):
        page_source = driver.page_source
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

        next_button = driver.find_element_by_class_name("right.carousel-control.carousel-control-next")
        next_button.click()
        time.sleep(2)

    print("check")
    master_vaccine_dataframe.to_csv('Vaccine_Data_{}week_pin{}.csv'.format(weeks, pin_code))
    driver.quit()


check_availability(122001)
