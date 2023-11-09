import schedule
from bs4 import BeautifulSoup
import json
from selenium import webdriver
from selenium.common.exceptions import SessionNotCreatedException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_auto_update.webdriver_auto_update import WebdriverAutoUpdate
from dateutil.parser import parse
import pandas
import os
import json
import time
from pandas import DataFrame
import requests
import re
import os
import datetime
from slack_api_send import send_error_message

os.makedirs('data_log', exist_ok=True)
os.makedirs('api_log', exist_ok=True)

def main():
    try:
        today = str(datetime.datetime.today()).split(' ')[0]
        chrome_options = Options()
        # chrome_options.add_argument('--incognito')
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--no-sandbox')
        # chrome_options.add_argument('--disable-setuid-sandbox')
        # chrome_options.add_argument('--disable-dev-shm-usage')
        # chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        # driver = webdriver.Chrome(options=chrome_options)

        driver = webdriver.Chrome()
        config = get_config()
        driver.get(config['url'])

        try:
            login_naver_with_execute_script(driver, config['userId'], config['userPw'])
        except Exception as e:
            print(e)
        time.sleep(2)

        # driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")

        # driver.find_elements()
        current_data = get_guest_list(driver)
        currents = current_data.to_dict('records')

        if os.path.exists(f'guests.csv'):
            past_data = get_past_data(f'guests.csv')
            pasts = past_data.to_dict('list')
            updated = []
            for current in currents:
                if int(current['appointment']) not in pasts['appointment']:
                    updated.append(current)

            success_list = send_api(updated, config['api_path'])
            new = DataFrame(success_list)
            pandas.concat([past_data,new]).to_csv(f'guests.csv', header=True, index=False, encoding='utf-8')

        else:
            # for current in currents:
            #     updated.append(current)
            success_list = send_api(currents, config['api_path'])
            # current_data.to_csv(f'data_log/guests.csv', header=True, index=False, encoding='utf-8')
            DataFrame(success_list).to_csv(f'guests.csv', header=True, index=False, encoding='utf-8')

        driver.quit()


    except SessionNotCreatedException as e:
        send_error_message(f"Error Occured: {e}")
        logfile_path = f'api_log/{today}.txt'
        try:
            driver_manager = WebdriverAutoUpdate(r'C:\Users\xorbis\PycharmProjects\NaverWebCrawl\chromedriver.exe')
            driver_manager.main()
            send_error_message('Successfully downloaded new chrome driver')
            create_log(logfile_path, 'ChromeDriverUpdated')

        except Exception as e:
            send_error_message(f'Error while downloading chrome driver: {e}')
            create_log(logfile_path, 'ChromeDriverUpdateFailure')

    except Exception as e:
        driver_manager = WebdriverAutoUpdate(r'C:\Users\xorbis\PycharmProjects\NaverWebCrawl\chromedriver.exe')
        driver_manager.main()
        logfile_path = f'api_log/{today}.txt'
        create_log(logfile_path, f'Error: {e}')
        send_error_message(f"Error Occured: {e}")


def check_existance(dict_of_values, df):
    v = df.iloc[:, 0] == df.iloc[:, 0]
    for key, value in dict_of_values.items():
        v &= (df[key] == value)
    return v.any()

def get_config():
    try:
        with open('config.json') as json_file:
            json_data = json.load(json_file)
    except Exception as e:
        print('Error in reading config file, {}'.format(e))
        return None
    else:
        return json_data


# def login_naver(driver, id, pw):
#     # element = driver.find_element_by_css_selector('#id')
#     element = driver.find_element(By.ID, 'id')
#     element.send_keys(id)
#     element = driver.find_element(By.ID,'pw')
#     element.send_keys(pw)
#     element = driver.find_element(By.ID,'log.login')
#     element.click()
#
#     print('login succeeded')
#
#     return


def login_naver_with_execute_script(driver, id, pw):
    script = "                                      \
    (function execute(){                            \
        document.querySelector('#id').value = '" + id + "'; \
        document.querySelector('#pw').value = '" + pw + "'; \
    })();"
    driver.execute_script(script)

    # element = WebDriverWait(driver, 10).until(
    #     EC.presence_of_element_located((By.CSS_SELECTOR, "input.btn_global"))
    # )
    element = driver.find_element(By.ID, 'log.login')
    element.click()
    print('login success')

    return

def get_past_data(file_path):
    data = pandas.read_csv(file_path, header=0, encoding='utf-8')
    return data

def time_in_range(start, end, x):
    """Return true if x is in the range [start, end]"""
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end

def get_guest_list(driver):
    driver.execute_script("document.body.style.zoom='25%'")
    import time
    for _ in range(20):
        item = driver.find_elements(By.XPATH,"//*[contains(@class, 'BookingListView__list-contents__')]")

        # item = driver.find_elements(By.CLASS_NAME, 'BookingListView__list-contents__g037Y')  #BookingListView__list-contents__g037Y
        # item = driver.find_elements(By.XPATH, '//*[@id="app"]/div[1]/div[2]/div[2]/div/div[2]/div[4]/div[2]')
        # item = driver.find_elements(By.CLASS_NAME, re.compile('BookingListView__list-contents__.*')) #3pFPD

        try:
            driver.execute_script("return arguments[0].scrollTo(0,100000);", item[0])
            time.sleep(1)
        except Exception as e:
            print(e)


    soup = BeautifulSoup(driver.page_source, "html.parser")
    table = soup.find_all("div", {"class" : re.compile('.*BookingListView__list-contents__.*')})
    div_list =table[0].find_all('div', attrs={'class': re.compile('BookingListView__contents-inner__.* d-flex flex-nowrap')})
    # app > div.BaseLayout__root__2-HIX > div.BaseLayout__container__2nc4I > div.BaseLayout__contents__3w55v > div > div.BookingListView__root__3eW0M > div.BookingListView__list__3dEpl.BookingListView__table__2DWDa > div.BookingListView__list-contents__1mfa8
    INFO = {}
    status = []
    name = []
    phone = []
    appointment = []
    time = []
    product = []
    quantity = []
    payment_info = []
    howmuch = []
    payment_data = []
    confirmation_time = []
    cancel_date = []
    for div in div_list:
        status.append(div.find('div',{'class':re.compile('BookingListView__cell__.* BookingListView__state__.*')}).get_text())
        name.append(div.find('div',{'class':re.compile('BookingListView__cell__.* BookingListView__name__.*')}).get_text())
        phone.append(div.find('div',{'class':re.compile('BookingListView__cell__.* BookingListView__phone__.*')}).get_text())
        appointment.append(div.find('div',{'class':re.compile('BookingListView__cell__.* BookingListView__book-number__.*')}).get_text())
        time.append(div.find('div',{'class':re.compile('BookingListView__cell__.* BookingListView__book-date__.* align-self-center')}).get_text())
        product.append(div.find('div',{'class':re.compile('BookingListView__cell__.* BookingListView__host__.* align-self-center')}).get_text())
        quantity.append(div.find('div',{'class':re.compile('BookingListView__cell__.* BookingListView__option__.*')}).get_text())
        payment_info.append(div.find('div',{'class':re.compile('BookingListView__cell__.* BookingListView__payment-state__.*')}).get_text())
        howmuch.append( div.find('div',{'class':re.compile('BookingListView__cell__.* BookingListView__total-price__.* align-self-center')}).get_text())
        payment_data.append(div.find('div',{'class':re.compile('BookingListView__cell__.* BookingListView__order-date__.*')}).get_text())
        confirmation_time.append(div.find('div',{'class':re.compile('BookingListView__cell__.* BookingListView__order-success-date__.*')}).get_text())
        cancel_date.append(div.find('div',{'class':re.compile('BookingListView__cell__.* BookingListView__order-cancel-date__.*')}).get_text())


    INFO['status'] = status
    INFO['name'] = name
    INFO['phone']=phone
    INFO['appointment']=appointment
    INFO['time']=time
    INFO['product']=product
    INFO['quantity']=quantity
    INFO['payment_info']=payment_info
    INFO['confirmation_time']=confirmation_time
    INFO['cancel_date']=cancel_date

    data = DataFrame(INFO)

    return data

def convert_time(old_time):
    if old_time=='-':
        return old_time
    else:
        #23. 7. 30.(일) 오후 2:43
        #2023 - 07 - 31 19: 31
        year, month, date = re.findall('(\d+)\.', old_time)
        hour, min = re.findall('(\d+)\:(\d+)', old_time)[0]
        if re.compile('\) ([가-힣]+)').findall(old_time)[0] == '오후':
            if hour!='12':
                hour = str(int(hour)+12)

        year = str(int(year)+2000)
        if len(month)==1:
            month = '0'+month
        if len(date)==1:
            date = '0'+date
        if len(hour)==1:
            hour = '0'+hour
        if len(min)==1:
            min = '0'+min

        final_str = f'{year}-{month}-{date} {hour}:{min}'
        return final_str

def create_log(logfile_path, json_message):
    now = datetime.datetime.now()
    now = str(now).split('.')[0]
    A = []
    A.append(f'{now}\t')
    A.append(f'{str(json_message)}\n')

    with open(logfile_path, 'a', encoding='utf-8') as f:
        f.writelines(A)


def send_api(updated_list, api_path):
    success = []
    fail = []
    for updates in updated_list:
        cancel = "false"
        if updates['status'] == '취소':
            cancel = "true"

        products = []
        product_all = updates['quantity'].split(',')
        for product_ in product_all:
            product = re.findall('(\D+)\s(\d)', product_)[0]
            pp = product[0].strip()

            hook_word = re.findall('AI', pp)
            ticketType = 1
            #AI는 1, 아니면 0
            # if pp== '입장권 대인' or '뮤지엄 패스권 대인':
            #     ticketType = 1
            # elif pp == '입장권 소인' or '뮤지엄 패스권 소인':
            #     ticketType = 2
            # elif pp == '입장권 대인+AI패키지' or '뮤지엄+AI패키지 대인':
            #     ticketType = 3
            # elif pp == '입장권 소인+AI패키지' or '뮤지엄+AI패키지 소인':
            #     ticketType = 4

            if len(hook_word)>0:
                ticketType = 3
            else:
                ticketType = 1

            products.append({
                "ticketType": ticketType,
                "ticketName": pp,
                "ticketCount": int(product[1])
            })
        reservation_time = convert_time(updates['time'])
        confirmation_time = convert_time(updates['confirmation_time'])
        cancel_date = convert_time(updates['cancel_date'])

        json_message = \
            [{
                "status": updates['status'],
                "name": updates['name'],
                # "mobileNumber": '010-9637-6103',
                "mobileNumber": updates['phone'],
                "appointmentNumber": updates['appointment'],
                "reservationTime": reservation_time,
                "productName": updates['product'],
                "paymentState": updates['payment_info'],
                "confirmationTime": confirmation_time,
                "canceled": cancel,
                "cancellationTime": cancel_date,
                "quantity": products
            }]
        headers = {'serviceKey': 'test123'}
        try:
            response = requests.post(api_path, json=json_message, headers=headers, verify=False).json()
            if response['message'] == '정상 처리':
                success.append(updates)
            else:
                print('Failed')
                fail.append(updates)
            print(f'Name: {updates["name"]}, Phone Number: {updates["phone"]}, Response: {response}')
            # print(f'Name: {updates["name"]}, Phone Number: {updates["phone"]}')
        except Exception as e:
            print(e)

        today = str(datetime.datetime.today()).split(' ')[0]
        logfile_path = f'api_log/{today}.txt'
        text = f'Sent Message: {json_message} \n Response: {response}'
        create_log(logfile_path, text)
        # time.sleep(2)

    return success

def delete_past_data(file_path):
    if os.path.exists(file_path):
        guest_data = get_past_data(file_path)
        new = []
        old = []
        for guest in guest_data.to_dict('records'):
            reservation_time = parse(convert_time(guest['time']))
            start = datetime.datetime.today() - datetime.timedelta(days=10)
            if start<reservation_time:
                new.append(guest)
            else:
                old.append(guest)
        pandas.DataFrame(new).to_csv(file_path, mode='w', header=True, index=False, encoding='utf-8')
        print(f"Deleted {len(old)} data older than past 10 days")

# delete_past_data('guests.csv')
# schedule.every(5).minutes.do(main)
# while True:
#     schedule.run_pending()

if __name__=='__main__':
    while True:
        main()
#         time.sleep(3)
    # delete_past_data('guests.csv')