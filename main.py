import schedule
from bs4 import BeautifulSoup
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

import pandas
import os
import json
import time
from pandas import DataFrame
import requests
import re
import os
import datetime

URL = 'https://nid.naver.com/nidlogin.login?svctype=1&locale=ko_KR&url=https%3A%2F%2Fpartner.booking.naver.com%2Fbizes%2F947442%2Fbooking-list-view'
os.makedirs('log', exist_ok=True)

def main():
    try:
        chrome_options = Options()
        chrome_options.headless = False
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(URL)

        config = get_config()

        login_naver_with_execute_script(driver, config['userId'], config['userPw'])
        time.sleep(2)

        # driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")

        # driver.find_elements()
        current_data = get_guest_list(driver)
        currents = current_data.to_dict('records')

        if os.path.exists('guest.csv'):
            past_data = get_past_data('guest.csv')
            pasts = past_data.to_dict('list')
            updated = []
            for current in currents:
                if int(current['appointment']) not in pasts['appointment']:
                    updated.append(current)

            send_api(updated, 'https://museumx.kr/api/management/save/reservation-info')
            new = DataFrame(updated)
            pandas.concat([past_data,new]).to_csv('guest.csv', header=True, index=False, encoding='utf-8')
        else:
            # for current in currents:
            #     updated.append(current)
            send_api(currents, 'https://museumx.kr/api/management/save/reservation-info')
            current_data.to_csv('guest.csv', header=True, index=False, encoding='utf-8')


    except Exception as e:
        print(str(e))
        today = str(datetime.datetime.today()).split(' ')[0]
        logfile_path = f'log/{today}.txt'
        create_log(logfile_path, 'ERROR\n')


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


def login_naver(driver, id, pw):
    # element = driver.find_element_by_css_selector('#id')
    element = driver.find_element(By.ID, 'id')
    element.send_keys(id)
    element = driver.find_element(By.ID,'pw')
    element.send_keys(pw)
    element = driver.find_element(By.ID,'log.login')
    element.click()

    print('login succeeded')
    return


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
    for _ in range(10):
        item = driver.find_elements(By.CLASS_NAME, 'BookingListView__list-contents__1mfa8')
        driver.execute_script("return arguments[0].scrollTo(0,100000);", item[0])
        time.sleep(1)
    # desired_y = (element.size['height'] / 2) + element.location['y']
    # window_h = driver.execute_script('return window.innerHeight')
    # window_y = driver.execute_script('return window.pageYOffset')
    # current_y = (window_h / 2) + window_y
    # scroll_y_by = desired_y - current_y
    #
    # driver.execute_script("window.scrollBy(0, arguments[0]);", 1000000)
    # driver.execute_script("return arguments[0].scrollTo(0,100);", item[0])
    # driver.execute_script("return arguments[0].scrollIntoView();", item[-1])
    # try:
    #     driver.execute_script("return arguments[0].scrollIntoView();", item)
    # except Exception as e:
    #     pass
    # item = driver.find_element_by_class_name('BookingListView__list-contents__1mfa8')
    # item.location_once_scrolled_into_view

    soup = BeautifulSoup(driver.page_source, "html.parser")
    table = soup.find_all("div", {"class": "BookingListView__table__2DWDa"})
    div_list =table[0].find_all('div', attrs={'class': 'BookingListView__contents-inner__2lnqC d-flex flex-nowrap'})
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
        status.append(div.find('div',{'class':'align-self-center BookingListView__cell__10Lyz BookingListView__state__2mcaw'}).get_text())
        name.append(div.find('div',{'class':'align-self-center BookingListView__cell__10Lyz BookingListView__name__16_zV'}).get_text())
        phone.append(div.find('div',{'class':'align-self-center BookingListView__cell__10Lyz BookingListView__phone__2IoIp'}).get_text())
        appointment.append(div.find('div',{'class':'align-self-center BookingListView__cell__10Lyz BookingListView__book-number__pJ808'}).get_text())
        time.append(div.find('div',{'class':'BookingListView__cell__10Lyz BookingListView__book-date__uvr59 align-self-center'}).get_text())
        product.append(div.find('div',{'class':'BookingListView__cell__10Lyz BookingListView__host__2GgAn align-self-center'}).get_text())
        quantity.append(div.find('div',{'class':'align-self-center BookingListView__cell__10Lyz BookingListView__option__2vC1Q'}).get_text())
        payment_info.append(div.find('div',{'class':'align-self-center BookingListView__cell__10Lyz BookingListView__payment-state__2py52'}).get_text())
        howmuch.append( div.find('div',{'class':'BookingListView__cell__10Lyz BookingListView__total-price__1_-_I align-self-center'}).get_text())
        payment_data.append(div.find('div',{'class':'align-self-center BookingListView__cell__10Lyz BookingListView__order-date__2ARr_'}).get_text())
        confirmation_time.append(div.find('div',{'class':'align-self-center BookingListView__cell__10Lyz BookingListView__order-success-date__1RvPL'}).get_text())
        cancel_date.append(div.find('div',{'class':'align-self-center BookingListView__cell__10Lyz BookingListView__order-cancel-date__3JOfl'}).get_text())


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



def send_api(updated_list, url):
    for updates in updated_list:
        cancel = "false"
        if updates['status'] == '취소':
            cancel = "true"

        products = []
        product_all = updates['quantity'].split(',')
        for product_ in product_all:
            product = re.findall('(\D+)\s(\d)', product_)[0]
            pp = product[0].strip()
            if pp== '입장권 대인' or '뮤지엄 패스권 대인':
                ticketType = 1
            elif pp == '입장권 소인' or '뮤지엄 패스권 소인':
                ticketType = 2
            elif pp == '입장권 대인+AI패키지' or '뮤지엄+AI패키지 대인':
                ticketType = 3
            elif pp == '입장권 소인+AI패키지' or '뮤지엄+AI패키지 소인':
                ticketType = 4

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
        response = requests.post('https://museumx.kr/api/management/save/reservation-info', json=json_message, headers=headers, verify=False).json()
        print(response)

        today = str(datetime.datetime.today()).split(' ')[0]
        logfile_path = f'log/{today}.txt'
        create_log(logfile_path, json_message)


schedule.every(5).minutes.do(main)

while True:
    schedule.run_pending()
#
# if __name__=='__main__':
#     main()