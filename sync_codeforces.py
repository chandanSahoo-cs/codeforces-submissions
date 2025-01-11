import requests
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from time import sleep

# Function to get submission info for Codeforces
def get_submission_info(username):
    submissions = json.loads(requests.get(f'https://codeforces.com/api/user.status?handle={username}').text)['result']

    for submission in submissions:
        if submission['verdict'] == 'OK':
            try:
                if len(str(submission["problem"]["contestId"])) <= 4 and len(submission["author"]["members"]) == 1:
                    yield {
                        'language': submission['programmingLanguage'],
                        'problem_code': f'{submission["problem"]["contestId"]}{submission["problem"]["index"]}',
                        'solution_id': submission['id'],
                        'problem_name': submission['problem']['name'] if 'name' in submission['problem'] else '',
                        'problem_link': f'https://codeforces.com/contest/{submission["problem"]["contestId"]}/problem/{submission["problem"]["index"]}',
                        'link': f'https://codeforces.com/contest/{submission["contestId"]}/submission/{submission["id"]}?f0a28=2',
                    }
            except KeyError:
                pass

# Function to get code for each submission
def get_code(driver):
    lines = driver.find_elements(By.CSS_SELECTOR, '#program-source-text > ol > li')
    return '\n'.join(line.text for line in lines)

# Function to get and save all Codeforces submissions
def get_solutions(username):
    all_info = list(get_submission_info(username))

    sub_id_info = {info['solution_id']: info for info in all_info}
    for info in all_info:
        sub_id_info[info['solution_id']] = info

    options = Options()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument('disable-gpu')

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.get(f'https://codeforces.com/submissions/{username}')
    sleep(1)

    select = Select(driver.find_element(By.ID, 'verdictName'))
    select.select_by_value('OK')

    driver.find_element(By.CSS_SELECTOR, 'input[value=Apply]').click()

    sub_ids = [info['solution_id'] for info in all_info]

    try:
        pages = int(driver.find_elements(By.CSS_SELECTOR, '#pageContent > div > ul > li > span')[-1].text)
    except IndexError:
        pages = 1

    index = 1
    driver.get(f'https://codeforces.com/submissions/{username}/page/{index}')
    prev = {}

    for sub_id in sub_ids:
        if index > pages:
            break

        try:
            element = driver.find_element(By.PARTIAL_LINK_TEXT, str(sub_id))
            driver.execute_script("arguments[0].click();", element)
            sleep(0.3)

            code = get_code(driver)
            sub_id_info[sub_id]['solution'] = code.replace('\u00a0', '\n')

            yield sub_id_info[sub_id]

        except NoSuchElementException:
            index += 1
            driver.get(f'https://codeforces.com/submissions/{username}/page/{index}')

        except StaleElementReferenceException:
            driver.execute_script("location.reload(true);")
            sleep(2)

    driver.quit()

# Save the Codeforces solutions to a folder
def save_submissions(submissions, folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    for submission in submissions:
        file_path = os.path.join(folder_name, f"{submission['solution_id']}.json")
        with open(file_path, 'w') as file:
            json.dump(submission, file, indent=4)

def main():
    username = 'Realmchan'  # Replace with your Codeforces username
    solutions = list(get_solutions(username))
    save_submissions(solutions, 'codeforces_submissions')  # Save in a folder

if __name__ == '__main__':
    main()
