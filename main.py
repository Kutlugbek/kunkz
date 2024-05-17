from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from sql_db import *

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")

driver = webdriver.Chrome()
driver.get("https://login.kundelik.kz/")
driver.set_window_size(1920, 1080)

def captcha(driver):
    return driver, False

def log_in(driver, username, password):
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, 'login'))).send_keys(username)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, 'password'))).send_keys(password)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//input[@type="submit"]'))).click()

    try:
        WebDriverWait(driver, 10).until(EC.url_contains("https://kundelik.kz/"))
    except:
        return captcha(driver)
    
    return driver, True

def log_out(driver):
    try:
        time.sleep(2)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[@onclick='document.logout.submit();']"))).click()
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//a[@class='blue action button']")))
    except Exception as e:
        print(f"Error occurred during logout: {e}")

def get_users_list(driver, link, teacher):
    try:
        print("Trying to get users list...")
        driver.get(link)
        edits = driver.find_elements(By.XPATH, "//li[@class='iE']")

        edits_list = [_.find_element(By.TAG_NAME, "a").get_attribute('href') for _ in edits]

        for edit in edits_list:
            try:
                driver.get(edit)
                driver.get(driver.find_element(By.ID, "TabPassword").get_attribute('href'))

                username = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "bold"))).text
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@type='submit']"))).click()
                try:
                    password = driver.find_elements(By.CLASS_NAME, "bold")[1].text
                except:
                    driver.back()

                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@type='submit']"))).click()
                    password = driver.find_elements(By.CLASS_NAME, "bold")[1].text

                print(f"{username} {password}")

                driver.get(link)

                sql_insert(teacher, username, password)
            except Exception as e:
                print(f"Error occurred: {e}")
    except Exception as e:
        print(f"Error occurred: {e}")

    return driver

def getUsers(driver, teacher, password):
    driver, result = log_in(driver, teacher, password)

    driver.get("https://schools.kundelik.kz/v2/myclasses")

    href_students = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@id="ContentPanelMyClasses"]'))).find_elements(By.TAG_NAME, "a")[0].get_attribute("href") + "&view=members"

    get_users_list(driver, href_students, teacher)
    
def newUsers(teacher):
    for user in sql_select(teacher):
        try:
            username, password = user
            log_in(username, password)
            if '.' in username:
                username = username.replace('.', '')

            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "Password"))).send_keys(username + password)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "RepeatedPassword"))).send_keys(username + password)
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@type='submit']"))).click()

            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//a[@href='https://kundelik.kz/']"))).click()

            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//a[@class='header-submenu__link']"))).click()
            log_out(driver)

            print(f"{username} {password} Done")
        except Exception as e:
            print(f"Error occurred: {e}")

def users(teacher):
    for user in sql_select(teacher):
        try:
            student_u, password = user
            if '.' in student_u:
                username = student_u.replace('.', '')
            else:
                username = student_u

            log_in(student_u, username + password)

            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//a[@class='header-submenu__link']"))).click()

            log_out(driver)

            print(f"{student_u} {username + password} Done")
        except Exception as e:
            print(f"Error occurred: {e}")

if __name__ == '__main__':
    getUsers(driver, "isakzhanova", "Kk12345+")