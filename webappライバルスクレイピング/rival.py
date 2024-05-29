from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

app = Flask(__name__)

def scrape_asin(product_url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    driver.get(product_url)
    time.sleep(3)  # ページの読み込みを待つ
    
    try:
        asin_element = driver.find_element(By.XPATH, "//th[text()=' ASIN ']/following-sibling::td")
        asin = asin_element.text
    except:
        asin = "No data"
    
    driver.quit()
    return asin

def scrape_rival_seller(seller_url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    driver.get(seller_url)
    time.sleep(3)  # ページの読み込みを待つ

    products = []
    while True:
        items = driver.find_elements(By.CSS_SELECTOR, '.s-main-slot .s-result-item')
        for item in items:
            try:
                title = item.find_element(By.CSS_SELECTOR, 'h2').text
                price_whole = item.find_element(By.CSS_SELECTOR, '.a-price-whole').text
                price_fraction = item.find_element(By.CSS_SELECTOR, '.a-price-fraction').text
                price = f"{price_whole}.{price_fraction}"
                link = item.find_element(By.CSS_SELECTOR, 'h2 a').get_attribute('href')
                try:
                    demand_element = item.find_element(By.CSS_SELECTOR, '.a-row.a-size-base .a-size-base.a-color-secondary')
                    demand_text = demand_element.text
                    if 'bought in past month' in demand_text:
                        demand = demand_text
                    else:
                        demand = "No data"
                except:
                    demand = "No data"
                
                # 商品詳細ページからASINを取得
                asin = scrape_asin(link)
                
                products.append({
                    'title': title,
                    'price': price,
                    'link': link,
                    'demand': demand,
                    'asin': asin
                })
            except Exception as e:
                print(f"Error: {e}")
                continue
        
        # 次のページへのリンクを探す
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, 'a.s-pagination-item.s-pagination-next.s-pagination-button.s-pagination-separator')
            next_button.click()
            time.sleep(3)  # 次のページの読み込みを待つ
        except Exception as e:
            print(f"Error: {e}")
            break  # 次のページがない場合はループを終了

    driver.quit()
    return products

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        seller_url = request.form['seller_url']
        products = scrape_rival_seller(seller_url)
        return render_template('index.html', products=products)
    return render_template('index.html', products=[])

if __name__ == '__main__':
    app.run(debug=True)

#hello