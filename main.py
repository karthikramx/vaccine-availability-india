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
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    hostipal_names_result = soup.find_all('h5', attrs={'class': 'center-name-title'})
    hostipal_address_result = soup.find_all('p', attrs={'class': 'center-name-text'})

    hostipal_names = []
    hostipal_addresses = []

    for hospital in hostipal_names_result:
        hostipal_names.append(hospital.text)

    for hospital_address in hostipal_address_result:
        hostipal_addresses.append(hospital_address.text)

    print(hostipal_names, "\n", "SIZE:{}".format(len(hostipal_names)))
    print(hostipal_addresses, "\n", "SIZE:{}".format(len(hostipal_addresses)))



    print("check")

    # try:
    #     print("Clicking on: {}".format(sector))
    #     element = driver.find_element_by_link_text(sector)
    #     driver.execute_script("arguments[0].scrollIntoView();", element)
    #     driver.find_element_by_link_text(sector).click()
    #     WebDriverWait(driver, 30)
    #
    #     page_df = pd.read_html(driver.current_url)
    #     table_df = page_df[1]
    #     table_df["Company Name"] = table_df["Company Name"].apply(lambda x: x.split(" Add to Watchlist")[0])
    #     print(table_df)
    #     ltp_data = ltp_data.append(table_df)
    #     print("---------------------------------------------------------------------------------------------------")
    #     print(ltp_data)
    #     print("---------------------------------------------------------------------------------------------------")
    #
    #
    # except Exception as e:
    #     print("Failed to retrieve:{}".format(sector))
    #     print("Exception:{}".format(e))

    driver.quit()


check_availability(122001)
