from selenium import webdriver
from config.settings import BASE_URL, USERNAME, PASSWORD, DOWNLOAD_FOLDER_LOCATION, BROWSER_DRIVER_PATH
from config.untils import setup_logger
from automation.visit_automation import VisitAutomation
from automation.patient_service_automation import PatientServiceAutomation
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


if __name__ == '__main__':

    driver_path = BROWSER_DRIVER_PATH
    service = Service(executable_path=driver_path)

    download_folder = DOWNLOAD_FOLDER_LOCATION
    chrome_options = Options()
    chrome_options.headless = True
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox") 
    prefs = {"download.default_directory": download_folder}
    chrome_options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    logger = setup_logger("logs/automation.log", log_level="INFO")
    try:
        # visit_automation  = VisitAutomation(driver, BASE_URL, USERNAME, PASSWORD, logger, DOWNLOAD_FOLDER_LOCATION)
        visit_automation  = PatientServiceAutomation(driver, BASE_URL, USERNAME, PASSWORD, logger, DOWNLOAD_FOLDER_LOCATION)
        visit_automation.login()
        visit_automation.navigate_to_visits()
        visit_automation.automate_monthly_export(2023, 2024)
        # print("berhasill...")
    finally:
        driver.quit()