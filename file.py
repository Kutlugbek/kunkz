"""
teachers_list = {
    "Nadiratashpulatova": "Tn1981@5",
    "mirkholikova": "Ss123456+",
    "isakzhanova": "Kk12345+",
    "umidatashalieva": "Uu12345!",
    "nigoraabdiraimova": "777Sayram@",
    "adolat": "Aa12345+"
}
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import easyocr
from sql_db import *

driver = webdriver.Firefox()
driver.maximize_window()

def captcha(driver):
    try:
        captcha_element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//img[@class='captcha__image']")))
        driver.execute_script("arguments[0].scrollIntoView();", captcha_element)
        time.sleep(1)
        captcha_element.screenshot("/home/kutlugbek/Desktop/kunkz/captcha.png")
        reader = easyocr.Reader(['en'])
        result = reader.readtext("/home/kutlugbek/Desktop/kunkz/captcha.png", detail=0, allowlist='0123456789')
        print(result[0])
        driver.find_element(By.NAME, "Captcha.Input").send_keys(result[0])
        driver.find_element(By.XPATH, "//input[@type='submit']").click()
    except Exception as e:
        print(f"Error occurred during captcha solving: {e}")
        raise e

def log_in(username, password):
    try:
        time.sleep(2)
        driver.get("https://login.kundelik.kz/login")
        driver.find_element(By.NAME, "login").send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.XPATH, "//input[@type='submit']").click()

        try:
            WebDriverWait(driver, 1).until(EC.visibility_of_element_located((By.NAME, "Captcha.Input")))
            captcha(driver)
        except Exception as e:
            print(f"User logged in successfully: {username}, {password}")
            print(f"Error occurred: {e}")
    except Exception as e:
        print(f"Error occurred during login: {e}")

def log_out(driver):
    try:
        time.sleep(2)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[@onclick='document.logout.submit();']"))).click()
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//a[@class='blue action button']")))
    except Exception as e:
        print(f"Error occurred during logout: {e}")

def new_users(teacher):
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

def main(teacher, teacher_password):
    try:
        log_in(teacher, teacher_password)

        try:
            WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//a[@href='https://kundelik.kz/workplace/teacher']"))).click()
        except:
            main(teacher, teacher_password)

        classes = driver.find_elements(By.XPATH, "//tr[@class='class-leading-row']")
        for _class in classes:
            links = []

            links.append(_class.find_element(By.XPATH, "//span[@class='class-leading-link__name class-leading-link__name_students']//..").get_attribute('href'))
            links.append(_class.find_element(By.XPATH, "//span[@class='class-leading-link__name class-leading-link__name_parents']//..").get_attribute('href'))

            for link in links:
                try:
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
                                password = driver.find_elementsсв(By.CLASS_NAME, "bold")[1].text
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
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        log_out(driver)

if __name__ == "__main__":
    try:
        new_users("isakzhanova")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        driver.quit()