from selenium import webdriver
from selenium.webdriver.support.ui import Select
from requests_html import HTMLSession, AsyncHTMLSession
from bs4 import BeautifulSoup
import pandas as pd
import time

import config

base_url = "https://uk.trapstarlondon.com/"

def get_product_link():
    base_shop = base_url + "/collections/drop"#the exact url 
    session = HTMLSession()#idk but this gets the website i think
    r = session.get(base_shop)#opens the url 
    items = r.html.find("#grid grid--uniform grid--view-items", first=True).find("li")#finding the product using f12 element
    return items, session

def get_product_wanted(target_name):
    target_name_list = [x.lower() for x in target_name.split(" ")]
    potential_urls = []
    items, session = get_product_link()
    for item in items:
        target_url = base_url + item.find("a", first = True).attrs["href"]
        r = session.get(target_url)
        product_name = r.html.find("h1[class=name]", first=True).text.lower()
        found = True
        for q in target_name_list:
            if q not in product_name:
                found = False
                break
        print("************************")
        if found:
            print("Found a match: {product_name}")
            if check_can_buy(r):
                print("Still here bitch")
                potential_urls.append(target_url)
            else:
                print("You snooze you lose")
        else:
            print(f'Not a match: {product_name}')
    return potential_urls

def check_can_buy(r):
    buy_btn = r.html.find('input[value = "add to cart"]', first = True)
    return(buy_btn is not None)

def perform_purchase(url):

    driver = webdriver.Chrome()
    driver.get(url)
    btn = driver.find_element_by_id('AddToCart-product-template').find_elements_by_tag_name('button')#this is to add item to cart
    if len(btn) == 0:
        print('not available, DONE')
        return

    btn[0].click()#for cart
    time.sleep(1)

    btn_check = driver.find_element_by_id('checkout').find_elements_by_tag_name('input')#trapstar goes straight to checkout when adding one thing to cart therefore this is to click CHECK OUT
    if len(btn_check) == 0:
        print('not available, DONE')
        return

    btn_check[0].click()#for checkout
    time.sleep(1)
   

    driver.find_element_by_id('checkout_email').send_keys(config.EMAIL) #afinding autofill
    driver.find_element_by_id('checkout_shipping_address_first_name').send_keys(config.FIRSTNAME)
    driver.find_element_by_id('checkout_shipping_address_last_name').send_keys(config.LASTNAME)
    driver.find_element_by_id('checkout_shipping_address_address1').send_keys(config.ADDRESS)
    driver.find_element_by_id('checkout_shipping_address_city').send_keys(config.CITY)
    driver.find_element_by_id('order_billing_city').send_keys(config.BCITY)
    driver.find_element_by_id('checkout_shipping_address_zip').send_keys(config.ZIP)
    driver.find_element_by_id('checkout_shipping_address_phone').send_keys(config.PHONE)

    btn_check2 = driver.find_element_by_id('continue_button').find_elements_by_tag_name('button')#continue to shipping
    if len(btn_check2) == 0:
        print('not available, DONE')
        return

    btn_check2[0].click()#shipping
    time.sleep(1)

    btn_check3 = driver.find_element_by_id('continue_button').find_elements_by_tag_name('button')#continue 
    if len(btn_check3) == 0:
        print('not available, DONE')
        return

    btn_check3[0].click()#continue
    time.sleep(1)

    #driver.find_element_by_id('number').send_keys(config.CC_NUMBER)
    #driver.find_element_by_id('name').send_keys(config.CC_NAME)
    #driver.find_element_by_id('expiry').send_keys(config.CC_YEAR)
    #driver.find_element_by_id('verification_value').send_keys(config.CC_CCV)

    select = Select(driver.find_element_by_id('number'))
    select.select_by_value(config.CC_NUMBER)
    select = Select(driver.find_element_by_id('name'))
    select.select_by_value(config.CC_NAME)
    select = Select(driver.find_element_by_id('expiry'))
    select.select_by_value(config.CC_YEAR)
    select = Select(driver.find_element_by_id('verification_value'))
    select.select_by_value(config.CC_CCV)

    time.sleep(2)

    btn_check4 = driver.find_element_by_id('continue_button').find_elements_by_tag_name('button')#REVIEW ORDER
    if len(btn_check4) == 0:
        print('not available, DONE')
        return

    btn_check4[0].click()#continue
    time.sleep(1)

    pay_btn = driver.find_element_by_id('continue_button').find_elements_by_tag_name('button') #complete order
    pay_btn[0].click()


def main(target_product):
    urls = get_product_wanted(target_product)
    print(f'Found {len(urls)} matches.')
    if len(urls) == 0:
        print('No match found - checking again')
        return
    print(f'Processing first url: {urls[0]}')
    # just buy the first match
    url = urls[0]
    perform_purchase(url)
    print('Done.')


# define main
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Trappybot main parser')
    parser.add_argument('--name', required=True,
                        help='Specify product name to find and purchase')
    args = parser.parse_args()
    main(target_product=args.name)

