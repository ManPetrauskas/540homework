import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
chrome_options = Options()

driver.get("https://www.fly540.com/flights/mombasa-to-nairobi?isoneway=0&currency=KES&depairportcode=MBA&arrvairportcode=NBO&date_from=Wed%2C+12+Jan+2022&date_to=Wed%2C+23+Feb+2022&adult_no=1&children_no=0&infant_no=0&searchFlight=&change_flight=")

button_results = []
prev_value = "0000"
depart_context_opener = driver.find_elements(By.XPATH,
                                             "//div[contains(concat(' ', @class, ' '), 'fly5-flights fly5-depart "
                                             "th')]//tbody/tr/td[1]/span[@class='fltime ftop']")
return_context_opener = driver.find_elements(By.XPATH, "//div[contains(concat(' ', @class, ' '), 'fly5-flights "
                                                       "fly5-return th')]//tbody/tr/td[1]/span[@class='fltime ftop']")
depart_button_id = driver.find_elements(By.XPATH, "//button[@data-direction='outbound']")
return_button_id = driver.find_elements(By.XPATH, "//button[@data-direction='inbound']")

result_array = []

# Looping through Depart flight options
for i in range(len(depart_context_opener)):
    depart_temp = {'Depart Button ID': depart_button_id[i].get_attribute("data-package-id")}
    # Make make button visible before clicking it
    depart_context_opener[i].click()
    if prev_value != depart_button_id[i].get_attribute("data-package-id"):
        prev_value = depart_button_id[i].get_attribute("data-package-id")
        # Wait until button loads up and click it
        WebDriverWait(driver, 5).until(ec.element_to_be_clickable(
            (By.XPATH, f"//button[@data-direction='outbound'][contains(@data-package-id, '{prev_value}')]"))).click()

        # Looping through Return flight options
        for x in range(len(return_context_opener)):
            # Make make button visible before clicking it
            time.sleep(2)
            return_context_opener[x].click()
            arrive_temp = {'Return Button ID': return_button_id[x].get_attribute("data-package-id")}

            if prev_value != return_button_id[x].get_attribute("data-package-id"):
                prev_value = return_button_id[x].get_attribute("data-package-id")
                # Wait until button loads up and click it
                WebDriverWait(driver, 5).until(ec.element_to_be_clickable(
                    (By.XPATH,
                     f"//button[@data-direction='inbound'][contains(@data-package-id, '{prev_value}')]"))).click()
                # Animations
                time.sleep(3)
                WebDriverWait(driver, 5).until(ec.element_to_be_clickable(
                    (By.XPATH,
                     "//div[contains(concat(' ', @class, ' '), 'fly5-fltotal')]//button[@id='continue-btn']"))).click()

                # Expand tax info
                WebDriverWait(driver, 5).until(ec.element_to_be_clickable(
                    (By.XPATH,
                     "//div[contains(concat(' ', @class, ' '), 'fly5-totalprice')]//a[@data-toggle='collapse']"))).click()

                # Declaring at top of file results in not finding elements
                depart_airport = driver.find_elements(By.XPATH,
                                                      "//div[contains(concat(' ', @class, ' '), 'col-4 fly5-frshort')]")
                arrival_airport = driver.find_elements(By.XPATH,
                                                       "//div[contains(concat(' ', @class, ' '), 'col-4 fly5-toshort')]")
                depart_date = driver.find_elements(By.XPATH,
                                                   "//div[contains(concat(' ', @class, ' '), 'col-5 fly5-timeout')]//span[@class='fly5-fdate']")
                depart_time = driver.find_elements(By.XPATH,
                                                   "//div[contains(concat(' ', @class, ' '), 'col-5 fly5-timeout')]//span[@class='fly5-ftime']")
                arrival_date = driver.find_elements(By.XPATH,
                                                    "//div[contains(concat(' ', @class, ' '), 'col-5 fly5-timein')]//span[@class='fly5-fdate']")
                arrival_time = driver.find_elements(By.XPATH,
                                                    "//div[contains(concat(' ', @class, ' '), 'col-5 fly5-timein')]//span[@class='fly5-ftime']")
                individual_tax = driver.find_elements(By.XPATH,
                                                      "//div[contains(concat(' ', @class, ' '), 'fly5-bkdown')]//div[contains(string(), 'Tax')]//span[@class='num']")
                subtotal = driver.find_elements(By.XPATH,
                                                "//div[contains(concat(' ', @class, ' '), 'fly5-bkdown')]//div[contains(concat(' ', @class, ' '), 'subtotal')]//span[@class='num']")
                total_price = driver.find_elements(By.XPATH,
                                                   "//div[contains(concat(' ', @class, ' '), 'total')]//strong[contains(string(), 'Total:')]//span[@class='num']")

                for a in range(2):  # Range is 2 because outbound and inbound flights
                    print(depart_airport[0])
                    temp_data = {
                        'Departure Airport': depart_airport[a].text,
                        'Arrival Airport': arrival_airport[a].text,
                        'Depart date': depart_date[a].text + " " + depart_time[a].text,
                        'Arrival date': arrival_date[a].text + " " + arrival_time[a].text,
                        'Cheapest fare price': subtotal[a].text,
                        'Individual tax': individual_tax[a].text,
                        'Total price': total_price[0].text  # Using the same sum for both entries
                    }
                    result_array.append(temp_data)
                driver.back()
                time.sleep(2)
    else:
        prev_value = "0000"

df_data = pd.DataFrame(result_array)
df_data.to_csv('results2.csv', index=False)
