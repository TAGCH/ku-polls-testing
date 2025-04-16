import time
import unittest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class PollTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        chrome_options = Options()
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("--start-maximized")
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.implicitly_wait(2)
        cls.base_url = "http://127.0.0.1:8000/polls/"

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def setUp(self):
        self.driver.get(self.base_url)

    def test_vote_without_login(self):
        """Test voting without login in should redirect to the login page."""
        try:
            self.logout_if_logged_in()

            question_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href="/polls/3/"]'))
            )
            question_link.click()
            time.sleep(1)

            choice_radio = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "choice-label"))

            )
            choice_radio.click()
            time.sleep(1)

            vote_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Vote")]'))
            )
            vote_button.click()
            time.sleep(1)

            login_header = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, '//h2[text()="Login"]'))
            )
            self.assertEqual(login_header.text, "Login", f"Test failed: Expected 'Login' header but got '{login_header.text}'")
            self.assertTrue("accounts/login" in self.driver.current_url, "Test failed: URL did not contain accounts/login") # Add URL check

        except Exception as e:
            self.fail(f"Test failed: {e}")

    def test_user_vote_with_login(self):
        """Test voting with login in should record user's vote."""
        try:
            #login
            login_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'btnLogin-popup'))
            )
            login_button.click()
            time.sleep(1)
            username_field = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, 'id_username'))
            )
            username_field.clear()
            username_to_enter = "Test01"
            username_field.send_keys(username_to_enter)
            password_field = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, 'id_password'))
            )
            password_field.clear()
            password_to_enter = "Test01"
            password_field.send_keys(password_to_enter)
            submit_button = self.driver.find_element(By.XPATH, '//button[@type="submit"]')
            submit_button.click()

            #try enter expired poll
            ex_question_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href="/polls/4/"]'))
            )
            ex_question_link.click()
            time.sleep(2)
            ex_vote_header = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH,
                                                  "//li[text()=\"This poll is not allowed for voting.\"]"))
            )
            self.assertEqual(ex_vote_header.text, "This poll is not allowed for voting.")
            close_button = self.driver.find_element(By.CLASS_NAME, 'close-button')
            close_button.click()
            time.sleep(1)

            #enter poll #2 to try empty vote
            pre_question_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href="/polls/2/"]'))
            )
            pre_question_link.click()
            time.sleep(1)
            vote_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//button[contains(text(), "Vote")]'))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", vote_button)
            time.sleep(0.3)
            self.driver.execute_script("arguments[0].click();", vote_button)
            self.driver.execute_script("window.scrollTo({top: 0, behavior: 'smooth'});")
            time.sleep(3)
            no_vote_header = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH,
                                                  "//li[text()=\"You didn't select a valid choice.\"]"))
            )
            self.assertEqual(no_vote_header.text, "You didn't select a valid choice.")

            #back to home
            home = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'a'))
            )
            home.click()
            time.sleep(2)

            #voting on right conditiom
            question_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href="/polls/3/"]'))
            )
            question_link.click()
            time.sleep(1)
            choice_radio = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "choice-label"))

            )
            choice_radio.click()
            time.sleep(1)
            vote_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Vote")]'))
            )
            vote_button.click()
            time.sleep(1)
            question_header = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, '//h1[text()="What is the most important factor when choosing a software development framework?"]'))
            )
            self.assertEqual(question_header.text, "What is the most important factor when choosing a software development framework?")
            choice_header = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH,
                                                  "//li[text()=\"Your vote was changed to 'Performance'\"]"))
            )
            self.assertEqual(choice_header.text, "Your vote was changed to 'Performance'")


        except Exception as e:
            self.fail(f"Test failed: {e}")

    def test_user_login_logout(self):
        """Test user login with both correct and incorrect field and logout"""
        try:
            #click on login button
            login_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'btnLogin-popup'))
            )
            login_button.click()
            time.sleep(1)

            #wrong username
            wrong_username_field = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, 'id_username'))
            )
            wrong_username_field.clear()
            wrong_username_to_enter = "Wrong name"
            time.sleep(1)
            wrong_username_field.send_keys(wrong_username_to_enter)
            password_field = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, 'id_password'))
            )
            password_field.clear()
            password_to_enter = "Test01"
            time.sleep(1)
            password_field.send_keys(password_to_enter)
            submit_button = self.driver.find_element(By.XPATH, '//button[@type="submit"]')
            submit_button.click()
            time.sleep(2)

            #wrong password
            username_field = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, 'id_username'))
            )
            username_field.clear()
            username_to_enter = "Test01"
            time.sleep(1)
            username_field.send_keys(username_to_enter)
            wrong_password_field = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, 'id_password'))
            )
            wrong_password_field.clear()
            wrong_password_to_enter = "Test02"
            time.sleep(1)
            wrong_password_field.send_keys(wrong_password_to_enter)
            submit_button = self.driver.find_element(By.XPATH, '//button[@type="submit"]')
            submit_button.click()
            time.sleep(2)

            #fill right password
            password_field = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, 'id_password'))
            )
            password_field.clear()
            password_to_enter = "Test01"
            time.sleep(1)
            password_field.send_keys(password_to_enter)
            submit_button = self.driver.find_element(By.XPATH, '//button[@type="submit"]')
            submit_button.click()
            time.sleep(5)

            #logout
            logout_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[text()="Logout"]'))
            )
            logout_button.click()
            time.sleep(2)
            alert = WebDriverWait(self.driver, 5).until(EC.alert_is_present())
            self.assertEqual(alert.text, "You're already logged out!")
            alert.accept()
            login_button_after_logout = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'btnLogin-popup'))
            )
            self.assertTrue(login_button_after_logout.is_displayed(),
                            "Logout failed: Login button not found after logout")

        except Exception as e:
            self.fail(f"Test failed: {e}")

    def logout_if_logged_in(self):
        try:
            logout_button = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, '//button[text()="Logout"]'))
            )
            logout_button.click()
            time.sleep(1)
            alert = WebDriverWait(self.driver, 3).until(EC.alert_is_present())
            alert.accept()
            time.sleep(1)
        except Exception:
            pass

if __name__ == "__main__":
    unittest.main()