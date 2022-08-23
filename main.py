from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
import datetime
import pymssql
from pymssql import _mssql

options = webdriver.ChromeOptions()
options.add_argument('lang=ru_RU.UTF-8')
options.add_argument("--incognito")
driver = webdriver.Chrome('C://chromedriver', options=options)


BD_KWARGS = dict(
    server='MSK-MNH-DB01T.gmlogic.ru',
    database='ils',
    user='manh',
    password='DEsaw123456', )

sql = "INSERT INTO ab_test_history_log VALUES (%s, %s, %s,%s)"

driver.get('https://msk-mnh-app01t.gmlogic.ru/RF/SignonMenuRF.aspx')

#Авторизация
user_log_seash = driver.find_element("xpath", '//*[@id="userNameInput"]')
user_log_seash.send_keys('myway\evgenij.dubodelov')
pass_log_seash = driver.find_element("xpath", '//*[@id="passwordInput"]')
pass_log_seash.send_keys('3dwJ4HXm')
aut_log_pass_seash = driver.find_element("xpath", '//*[@id="submitButton"]').click()
cont_l = driver.find_element("xpath", '/html/body/center/center/form/table/tbody/tr/td[1]/input').click()
#cont_2 = driver.find_element("xpath", '//*[@id="FORM1"]/table/tbody/tr[4]/td/a[1]').click()
#cont_3 = driver.find_element("xpath", '//*[@id="proRfWrapper"]/form/table/tbody/tr[3]/td/a[3]').click()

time.sleep(5.5)
a = 1;
while a < 5:
    #Экран с ячейкой
    if driver.title == 'Выбор рабочей единицы':
        work_1_1 = driver.find_element("xpath", '//*[@id="wrapper"]/table/tbody/tr[2]/td/input[1]').click()
        time.sleep(1)

    #Экран принтера
    elif driver.title == 'Печать этикеток':
        work_2_1 = driver.find_element("xpath", '//*[@id="wrapper"]/table/tbody/tr[1]/td[2]/input').send_keys('test')
        work_2_2 = driver.find_element("xpath", '//*[@id="wrapper"]/table/tbody/tr[2]/td/input[1]').click()
        time.sleep(1)
        
    #Экран тары - получаем РЕ записываем её в переменную
    elif driver.title == 'Планируемая тара':
        work_3_1 = driver.find_element("xpath", '//*[@id="wrapper"]/table/tbody/tr[1]/td') 
        work_3_3 = work_3_1.text
        work_3_2 = driver.find_element("xpath", '//*[@id="wrapper"]/table/tbody/tr[5]/td/input[1]').click()
        print(work_3_3)
        time.sleep(1)

    #экран ввода родительской LPN - смотрим в БД пишем в поле ввода
    elif driver.title == 'ИД контейнера':
        with _mssql.connect(**BD_KWARGS) as conn_MSK:
            conn_MSK.execute_query(
            f"""
            select top 1 container_id
            from KC_STATISTICS_SHIPPING_CONTAINER
            where user_def4 =  replace(replace(%s,N'Рабочая единица ',''),':','')
            and container_type = 'EUR'""", work_3_3
            )
            work_4_3 = ''
            for line_MSK in conn_MSK:
                work_4_3 = f"{line_MSK['container_id']} "
        work_4_1 = driver.find_element("xpath", '//*[@id="wrapper"]/table/tbody/tr[2]/td[2]/input') 
        work_4_1.send_keys(work_4_3)
        work_4_2 = driver.find_element("xpath", '//*[@id="wrapper"]/table/tbody/tr[3]/td/input[1]').click()
        time.sleep(5)

    elif driver.title == 'Отбор':
        dt_now = datetime.datetime.now()
        print(dt_now)
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, "proRfWrapper"))).get_attribute("value")

        work_unit = driver.find_element("xpath", "//input[@name='HIDDENWORK_UNIT']")
        work_unit_sql = work_unit.get_attribute("value")

        text1 = driver.find_element("xpath", '//*[@id="wrapper"]') 

        text2 = text1.text
        
        print(work_unit_sql)
        with _mssql.connect(**BD_KWARGS) as conn_MSK:
            conn_MSK.execute_query(
            f"""
                select top 1 container_id
                from KC_STATISTICS_SHIPPING_CONTAINER
                where internal_ship_alloc_num = (
                select top 1 internal_ship_alloc_num
                from shipment_alloc_request
                where internal_shipment_line_num = ( 
                select top 1 internal_line_num
                from WORK_INSTRUCTION
                where WORK_UNIT = %s and from_qty != '0' and instruction_type = 'detail' and hold_code is null
                order by sequence)
                ) and isnull(container_type,'1') != 'EUR' and user_def4 = %s""", (work_unit_sql, work_unit_sql)

            )
            cont_id = ''
            for line_MSK in conn_MSK:
                cont_id = f"{line_MSK['container_id']} "
        lpn_inpt = driver.find_element("xpath", '//*[@id="trContainerId"]/td[2]/input')
        lpn_inpt.send_keys(cont_id)
        time.sleep(1)
        print(cont_id)
        pick_but = driver.find_element("xpath", '//*[@id="btnOK"]')
        pick_but.click()
        val = (work_unit_sql,cont_id,dt_now,text2)
        with _mssql.connect(**BD_KWARGS) as conn_MSK2:
            conn_MSK2.execute_query(sql,val)

    elif driver.title == 'Размещение':
        work_5_1 = driver.find_element("xpath", '//*[@id="btnOK"]').click()
        
        
    else:    
        time.sleep(10)

   


# !страница загрузилась - посмотрели в БД взяли LPN - ввели LPN! 
# Логирования
# ПОнимание какую LPN вводить
     
