from flask import Flask, jsonify
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from pymongo import MongoClient
import json
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import requests
import time
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv('MONGO_URL'))
db = client['twitter_trends']
collection = db['trends_data']

proxy_list = ['proxy1', 'proxy2', 'proxy3'] 



def generate_unique_id():
    return str(random.randint(100000000, 999999999))

def fetch_trending_topics():
    proxy = random.choice(proxy_list)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(f'--proxy-server=http://{proxy}')
    
    driver = webdriver.Chrome(service=Service(r"C:\\Users\\HP\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe"))
    try:
        driver.get("https://twitter.com/login")
        time.sleep(2)

        driver.implicitly_wait(3)
        username = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input"))
         )
        username.send_keys(os.getenv('TWITTER_USERNAME')) 
        username.send_keys(Keys.RETURN)
        time.sleep(2)
        
        password = driver.find_element(By.NAME, "password")
        password.send_keys(os.getenv('TWITTER_PASSWORD'))  
        password.send_keys(Keys.RETURN)
        time.sleep(5)

        driver.get("https://twitter.com/explore/tabs/trending")
        time.sleep(5)

        trends = driver.find_elements(By.XPATH, "//div//span[@dir=\"ltr\"]")[:5]

        trend_names = [trend.text for trend in trends]

        current_time = time.strftime('%Y-%m-%d %H:%M:%S')
        ip_address = requests.get('https://api.ipify.org').text
        unique_id = generate_unique_id()
        record = {
            "_id": unique_id,
            "trend1": trend_names[0],
            "trend2": trend_names[1],
            "trend3": trend_names[2],
            "trend4": trend_names[3],
            "trend5": trend_names[4],
            "timestamp": current_time,
            "ip_address": ip_address
        }
        collection.insert_one(record)

        return trend_names, current_time, ip_address

    finally:
        driver.quit()


app = Flask(__name__) 
cors = CORS(app, resources={r"*": {"origins": "*"}})

@app.route('/run_script')
def run_script():
    result = fetch_trending_topics()
   
    trend_names, timestamp, ip_address = result
    response = {
        "timestamp": timestamp,
        "trend1": trend_names[0],
        "trend2": trend_names[1],
        "trend3": trend_names[2],
        "trend4": trend_names[3],
        "trend5": trend_names[4],
        "ip_address": ip_address
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
