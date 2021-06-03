from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import csv

def sort_groups_csv(file):
    group_dict = {}
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)
        for row in csv_reader:
            group = row[4]
            fullname = row[6]
            if group in group_dict:
                group_dict[group].append(fullname)
            else:
                group_dict[group] = [fullname]
    
    return group_dict

def edit_default_question_block(driver):
    wait = WebDriverWait(driver, 30)
    survey_title = driver.find_element_by_xpath("//textarea[contains(@class, 'SurveyNameInput')]").text
    default_question_block = driver.find_element_by_xpath("//button[contains(@class, 'BlockExpander')]")
    try:
        default_question_block.click()
    except:
        default_question_block.click()
    
    wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='QuestionText']")))
    q1_text_box = driver.find_element_by_xpath("//div[@class='QuestionText']")
    q1_text_box.click()
    text_box = driver.find_element_by_id('InlineEditorElement')
    text_box.clear()
    text_box.send_keys(f'Teammate Evaluation for {survey_title}\n\nPlease provide an honest evaluation to your teammates.')
    default_question_block.click()

    return survey_title

def delete_extra_blocks(driver, group_dict):
    wait = WebDriverWait(driver, 30)
    standard_blocks = driver.find_elements_by_xpath("//div[div[@class='BlockHeader StandardBlock']]")
    for i in range(len(standard_blocks) - len(group_dict.keys())):
        standard_blocks = driver.find_elements_by_xpath("//div[div[@class='BlockHeader StandardBlock']]")
        try:
            standard_blocks[-1].click()
        except:
            standard_blocks[-1].click()

        menu_buttons = driver.find_elements_by_xpath("//button[contains(@class, 'BlockMenuButton')]")
        menu_buttons[-1].click()
        wait.until(EC.element_to_be_clickable((By.ID, "block-menu-delete")))
        delete_option = driver.find_element_by_id("block-menu-delete")
        delete_option.click()
        delete_button = driver.find_element_by_xpath("//a[@class='btn btn-danger']")
        delete_button.click()
        wait.until(EC.invisibility_of_element_located((By.XPATH, "//a[@class='btn btn-hover']")))
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'BlockExpander')]")))

def edit_group_blocks(driver, group_dict):
    wait = WebDriverWait(driver, 30)
    standard_blocks = driver.find_elements_by_xpath("//div[div[@class='BlockHeader StandardBlock']]")
    edit_names = driver.find_elements_by_xpath("//span[@class='BlockTitle Editable']")
    group_names = list(group_dict.keys())
    original_num_blocks = len(standard_blocks)
    arrow_buttons = driver.find_elements_by_xpath("//button[contains(@class, 'BlockExpander')]")

    if original_num_blocks < len(group_names):
        raise Exception("More groups than available blocks")

    for i in range(len(group_names)):
        try:
            arrow_buttons[i + 1].click()
        except:
            arrow_buttons[i + 1].click()
        
        edit_names[i + 1].click()
        wait.until(EC.presence_of_element_located((By.ID, "InlineEditorElement")))
        text_box = driver.find_element_by_id("InlineEditorElement")
        text_box.clear()
        text_box.send_keys(str(group_names[i]))
        names_entry = driver.find_elements_by_xpath("//span[@class='LabelWrapper']")
        try:
            names_entry[-1].click()
        except:
            names_entry[-1].click()

        group_members = group_dict[group_names[i]]
        for j in range(len(group_members)):
            new_option = driver.find_element_by_id("InlineEditorElement")
            new_option.clear()
            new_option.send_keys(group_members[j])
            if j < len(group_members) - 1:
                new_option.send_keys(Keys.RETURN)
            
        # Clicks off of the question
        driver.find_element_by_xpath("//body").click()
        try:
            arrow_buttons[i + 1].click()
        except:
            arrow_buttons[i + 1].click()

def edit_survey_flow(driver, group_dict):
    wait = WebDriverWait(driver, 30)
    group_names = list(group_dict.keys())
    survey_flow_tab = driver.find_element_by_id("toolbar-survey-editor-toolbar-tab-1")
    survey_flow_tab.click()
    wait.until(EC.element_to_be_clickable((By.XPATH, "//a[text()='Edit Condition']")))
    edit_condition_buttons = driver.find_elements_by_xpath("//a[text()='Edit Condition']")
    ok_buttons = driver.find_elements_by_xpath("//a[@class='btn btn-success logic-done']")
    
    if len(edit_condition_buttons) - 1 < len(group_names):
        raise Exception("More groups than available blocks")

    for i in range(1, len(edit_condition_buttons)):
        if i <= len(group_names):
            wait.until(EC.element_to_be_clickable((By.XPATH, "//a[text()='Edit Condition']")))
            try:
                edit_condition_buttons[i].click()
            except:
                edit_condition_buttons[i].click()
            text_boxes = driver.find_elements_by_xpath("//input[@class='TextBox Multiline ExpressionField']")
            text_boxes[-1].clear()
            text_boxes[-1].send_keys(group_names[i - 1])
            if i > 2:
                try:
                    ok_buttons[i - 1].click()
                except:
                    ok_buttons[i - 1].click()
        else:
            # Deletes extra blocks
            delete_buttons = driver.find_elements_by_xpath("//a[@class='Delete']")
            try:
                delete_buttons[-1].click()
            except:
                delete_buttons[-1].click()
            yes_button = driver.find_element_by_xpath("//a[@class='btn positive']")
            yes_button.click()

    # This statement is to get the last ok button in view
    if len(group_names) == len(edit_condition_buttons) - 1:
        add_new_element_buttons = driver.find_elements_by_xpath("//a[//span[@class='add-element-label']]")
        add_new_element_buttons[-1].click()
    
    ok_buttons = driver.find_elements_by_xpath("//a[@class='btn btn-success logic-done']")
    try:
        ok_buttons[-1].click()
    except:
        ok_buttons[-1].click()

    buttons = driver.find_elements_by_xpath("//button[@type='button']")
    buttons[-1].click()

if __name__ == "__main__":
    # Change the file below according to which CSV file is used
    group_dict = sort_groups_csv("examplemailinglist.csv")

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    abs_driver_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chromedriver")
    driver = webdriver.Chrome(options=options, executable_path=abs_driver_path)
    driver.get("https://uiuc.qualtrics.com")

    input(
        f"Please select the correct template with more than {len(group_dict.keys())} groups.\n"\
        "Then rename the project in the pop-up window and navigate to the project.\n"\
        "Remember: The title should be 'Peer Evaluation for Course Title (semester year).'\n"\
        "Ex. Peer Evaluation for Program Capstone (Fall 2017).\n\n"\
        "Once you are done, please press ENTER in this window.\n"
    )
    
    edit_default_question_block(driver)
    delete_extra_blocks(driver, group_dict)
    edit_group_blocks(driver, group_dict)
    edit_survey_flow(driver, group_dict)

    input("Please complete the rest of the survey manually. Then press ENTER to quit")
    driver.quit()
