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
os.makedirs('qr_log', exist_ok=True)


def main(input_name, current_data):
    sent_qr_data = DataFrame({'name':'dummy'}, index=[0])
    if os.path.exists('sent_qr_list.csv'):
        sent_qr_data = pandas.read_csv('sent_qr_list.csv', header=0, encoding='utf-8')

    if current_data.loc[current_data['name'] == input_name].shape[0]>=1:
        name_lists = []
        for row in current_data.loc[current_data['name'] == input_name].to_dict('records'):
            if row['status'] in ['확정','완료']:
                name_lists.append(row)

        if len(name_lists) > 0:
            for idx, row in enumerate(name_lists):
                name = row['name']
                phone = row['phone']

                # # click
                # try:
                #     element = driver.find_element(By.XPATH, f"//*[contains(text(), {name})]")
                #     element = driver.find_elements(By.CLASS_NAME,
                #                                    'align-self-center BookingListView__cell__10Lyz BookingListView__book-number__pJ808')
                #     the_one_you_want = [x for x in fc_day_contents if "15" == x.text][0]
                #     element.click()
                #     element = driver.find_element(By.XPATH,
                #                         '//*[@id="app"]/div[1]/div[2]/div[2]/div/div[3]/div[2]/div/div[2]/div/div/div[2]/div/a[3]')
                #     element.click()
                # except Exception as e:
                #     print(e)
                #     pass

                print(f'{idx + 1}. 이름:{name}, 휴대폰 번호: {phone}\n')
            right_idx = int(input("해당하는 올바른 정보의 번호 를 입력하십시오: \n"))

            st = True
            if (right_idx - 1) in range(len(name_lists)):
                send_qr_api(name_lists[right_idx-1])
                st = False
            else:
                print('올바르지 않은 인덱스 입니다. 다시 입력하십시오: \n')

        else:
            print('취소한 예매자 입니다. 예약 페이지를 확인해주십시오 \n')

    else:
        # already_sents = sent_qr_data.loc[sent_qr_data['name']==input_name]
        # if already_sents.shape[0]>=1:
        #     print('이미 발송한 내역에 같은 이름이 있습니다 : \n')
        #     for already_sent in already_sents:
        #         name = already_sent['name']
        #         phone = already_sent['phone']
        #         print(f'\t 이름: {name} , 핸드폰번호:{phone}')
        #     answer = str(input('위 리스트 중에 중복되는 내역이 있습니까? (Y/N) : \n'))
        #     if answer in ['Y', 'y']:
        #         print('이미 qr 보냈습니다. \n')
        #     else:
        #         print('예약 페이지를 확인하십시오. \n')

        # Retry Crawling
        # else:
        print('예약 내역에 없어서 재확인하는 중... 기다려주십시오 \n')
        current_data = get_guest_list(driver)
        if current_data.loc[current_data['name'] == input_name].shape[0] >= 1:
            name_lists = []
            for row in current_data.loc[current_data['name'] == input_name].to_dict('records'):
                if row['status'] == '확정':
                    name_lists.append(row)

            if len(name_lists) > 0:
                for idx, row in enumerate(name_lists):
                    name = row['name']
                    phone = row['phone']
                    print(f'{idx + 1}. 이름:{name}, 휴대폰 번호: {phone}\n')
                right_idx = int(input("해당하는 올바른 정보의 번호 를 입력하십시오: \n"))

                if (right_idx - 1) in range(len(name_lists)):
                    send_qr_api(name_lists[right_idx - 1])
                else:
                    print('올바르지 않은 인덱스 입니다. 다시 입력하십시오: \n')
            else:
                print('취소한 예매자 입니다. 예약 페이지를 확인해주십시오 \n')
        else:
            print('예약 내역에 없습니다. 네이버 홈페이지를 확인해주세요 \n')

    return current_data
        # if input_name not in current_data.to_dict['list']['name']:
        #     if input_name in sent_qr_names:
        #         print(f'이미 발송한 내역에 이름이 있습니다. 발송한 예약 이름')
        #     current_data = get_guest_list(driver)
        #     currents = current_data.to_dict('records')
        #     currents = [current for current in currents if current not in sent_qr_list]
        #     if input_name not in currents
        #
        #     current
        # send_qr_api(currents)





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
    element = driver.find_element(By.ID, 'pw')
    element.send_keys(pw)
    element = driver.find_element(By.ID, 'log.login')
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


def send_qr_api(current):
    print('QR 코드를 보내는 중입니다. \n')
    from dateutil.parser import parse
    now = datetime.datetime.now()
    url = "https://museumx.kr/api/management/create-qrcode"
    # current_list = current_list.to_dict('records')
    # for current in current_list:
    if current['status'] in ['확정', '완료']:
        phone_number = current['phone']
        products = current['quantity'].split(',')
        for product_ in products:
            product = re.findall('(\D+)\s(\d)', product_)[0]
            quant = 0
            pp = product[0].strip()
            if pp in ['입장권 대인+AI패키지','뮤지엄+AI패키지 대인','입장권 소인+AI패키지','뮤지엄+AI패키지 소인']:
                user_level = 1
                quant = product[1]
            elif pp in ['입장권 소인','뮤지엄 패스권 소인','입장권 대인','뮤지엄 패스권 대인']:
                user_level = 0
                quant = product[1]

            # reservation_time = parse(convert_time(current['time']))
            # start = reservation_time - datetime.timedelta(minutes=10)

            # end = reservation_time + datetime.timedelta(minutes=10)
            # if time_in_range(start, end, now):
            headers = {
                "serviceKey": "test123",
                # "phoneNumber": re.sub('-','',phone_number),
                "phoneNumber": '01096376103',
                "requiredQrCodeCount": str(quant),
                "userLevel": str(user_level)
            }
            try:
                response = requests.post(url, headers=headers, verify=False).json()
                print(f"API response: {response} \n")
                new = DataFrame(current, index=[0])
                new.to_csv('sent_qr_list.csv', mode='a', index=False, encoding='utf-8')
                today = str(datetime.datetime.today()).split(' ')[0]
                logfile_path = f'qr_log/{today}.txt'
                A = [headers]
                A.extend(new.to_dict('records')[0])

                create_log(logfile_path, A)
                print('성공적으로 QR코드를 보냈습니다. \n')
            except:
                print('Error: could not send api')
                today = str(datetime.datetime.today()).split(' ')[0]
                logfile_path = f'qr_log/{today}.txt'
                create_log(logfile_path, current['appointment'])

    elif current['status'] == '완료':
        print('이미 이용 완료한 고객 입니다. \n')
    else:
        print("네이버 예약이 확정되지 않았습니다. 예약 페이지를 참고해주세요. \n")


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
    div_list = table[0].find_all('div', attrs={'class': 'BookingListView__contents-inner__2lnqC d-flex flex-nowrap'})
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
        status.append(div.find('div', {
            'class': 'align-self-center BookingListView__cell__10Lyz BookingListView__state__2mcaw'}).get_text())
        name.append(div.find('div', {
            'class': 'align-self-center BookingListView__cell__10Lyz BookingListView__name__16_zV'}).get_text())
        phone.append(div.find('div', {
            'class': 'align-self-center BookingListView__cell__10Lyz BookingListView__phone__2IoIp'}).get_text())
        appointment.append(div.find('div', {
            'class': 'align-self-center BookingListView__cell__10Lyz BookingListView__book-number__pJ808'}).get_text())
        time.append(div.find('div', {
            'class': 'BookingListView__cell__10Lyz BookingListView__book-date__uvr59 align-self-center'}).get_text())
        product.append(div.find('div', {
            'class': 'BookingListView__cell__10Lyz BookingListView__host__2GgAn align-self-center'}).get_text())
        quantity.append(div.find('div', {
            'class': 'align-self-center BookingListView__cell__10Lyz BookingListView__option__2vC1Q'}).get_text())
        payment_info.append(div.find('div', {
            'class': 'align-self-center BookingListView__cell__10Lyz BookingListView__payment-state__2py52'}).get_text())
        howmuch.append(div.find('div', {
            'class': 'BookingListView__cell__10Lyz BookingListView__total-price__1_-_I align-self-center'}).get_text())
        payment_data.append(div.find('div', {
            'class': 'align-self-center BookingListView__cell__10Lyz BookingListView__order-date__2ARr_'}).get_text())
        confirmation_time.append(div.find('div', {
            'class': 'align-self-center BookingListView__cell__10Lyz BookingListView__order-success-date__1RvPL'}).get_text())
        cancel_date.append(div.find('div', {
            'class': 'align-self-center BookingListView__cell__10Lyz BookingListView__order-cancel-date__3JOfl'}).get_text())

    INFO['status'] = status
    INFO['name'] = name
    INFO['phone'] = phone
    INFO['appointment'] = appointment
    INFO['time'] = time
    INFO['product'] = product
    INFO['quantity'] = quantity
    INFO['payment_info'] = payment_info
    INFO['confirmation_time'] = confirmation_time
    INFO['cancel_date'] = cancel_date

    data = DataFrame(INFO)

    return data


def convert_time(old_time):
    if old_time == '-':
        return old_time
    else:
        # 23. 7. 30.(일) 오후 2:43
        # 2023 - 07 - 31 19: 31
        year, month, date = re.findall('(\d+)\.', old_time)
        hour, min = re.findall('(\d+)\:(\d+)', old_time)[0]
        if re.compile('\) ([가-힣]+)').findall(old_time)[0] == '오후':
            hour = str(int(hour) + 12)

        year = str(int(year) + 2000)
        if len(month) == 1:
            month = '0' + month
        if len(date) == 1:
            date = '0' + date
        if len(hour) == 1:
            hour = '0' + hour
        if len(min) == 1:
            min = '0' + min

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




# schedule.every().hour.do(main)

# while True:
#     schedule.run_pending()


chrome_options = Options()
chrome_options.headless = False
driver = webdriver.Chrome(options=chrome_options)
driver.get(URL)

config = get_config()

login_naver_with_execute_script(driver, config['userId'], config['userPw'])
time.sleep(2)
current_data = get_guest_list(driver)

while 1:
    try:
        mode = int(input('예약자 명을 입력하려면 1, 핸드폰 번호로 바로 QR 을 보내시려면 2를 누르세요'))
        if mode==1:
            name = str(input('예약자 명을 입력하십시오: \n'))
            current_data = main(name, current_data)
        elif mode==2:
            url = "https://museumx.kr/api/management/create-test-qrcode"
            phone = str(input('휴대폰 번호를 입력하세요: \n'))
            headers = {
                "serviceKey": "test123",
                "phoneNumber": re.sub('\s', '', phone),
            }
            response = requests.post(url, headers=headers, verify=False).json()
            print(response)
            print('\n')
    except Exception as e:
        print(e)
        pass