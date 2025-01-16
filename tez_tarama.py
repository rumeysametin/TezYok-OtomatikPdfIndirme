import mysql.connector
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import re
import time
import csv

def scrape_theses_and_store_in_mysql(term="veri madenciliği"):
    # Burada Selenium başlatılıyor
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    # MySQL bağlantısını kuruluyor
    connection = mysql.connector.connect(
        host="localhost",  
        user="tez_user",
        password="tez_password",
        database="tezler"
    )
    cursor = connection.cursor()

    try:
        #Taramaların yapıldığı kısım
        base_url = "https://tez.yok.gov.tr/UlusalTezMerkezi/"
        driver.get(base_url)

        search_box = driver.find_element(By.ID, "neden")
        search_box.send_keys(term)

        find_button = driver.find_element(By.XPATH, "//input[@value='     Bul      ']")
        find_button.click()

        time.sleep(5)

        # Sayfanın kaynağını alınıyor
        page_source = driver.page_source
        var_doc_matches = re.findall(r"var doc = {.*?};", page_source, re.DOTALL)

        if var_doc_matches:
            tez_listesi = []
            for idx, doc in enumerate(var_doc_matches, start=1):
                # Doc içeriğindeki verileri çıkarılıyor
                doc_data = {
                    'Tez No': re.search(r"userId: .*?>(\d+)<", doc).group(1) if re.search(r"userId: .*?>(\d+)<", doc) else '',
                    'Yazar': re.search(r"name: \"(.*?)\"", doc).group(1) if re.search(r"name: \"(.*?)\"", doc) else '',
                    'Yıl': re.search(r"age: \"(\d{4})\"", doc).group(1) if re.search(r"age: \"(\d{4})\"", doc) else '',
                    'Tez Adı': re.search(r"weight: \"(.*?)<", doc).group(1) if re.search(r"weight: \"(.*?)<", doc) else '',
                    'Üniversite': re.search(r"uni:\"(.*?)\"", doc).group(1) if re.search(r"uni:\"(.*?)\"", doc) else '',
                    'Dil': re.search(r"height:\"(.*?)\"", doc).group(1) if re.search(r"height:\"(.*?)\"", doc) else '',
                    'Tez Türü': re.search(r"important: \"(.*?)\"", doc).group(1) if re.search(r"important: \"(.*?)\"", doc) else '',
                    'Konu': re.search(r"someDate: \"(.*?)\"", doc).group(1) if re.search(r"someDate: \"(.*?)\"", doc) else ''
                }
                tez_listesi.append(doc_data)

            # Verileri MySQL'e ekliyor
            sql_insert_query = """
            INSERT INTO tezler (tez_no, yazar, yil, tez_adi, universite, dil, tez_turu, konu)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """

            for tez in tez_listesi:
                values = (
                    tez['Tez No'],
                    tez['Yazar'],
                    tez['Yıl'],
                    tez['Tez Adı'],
                    tez['Üniversite'],
                    tez['Dil'],
                    tez['Tez Türü'],
                    tez['Konu']
                )
                cursor.execute(sql_insert_query, values)

            connection.commit()
            print(f"{len(tez_listesi)} tez bilgisi başarıyla MySQL'e kaydedildi.")
            
            # CSV dosyasına yazma
            with open('tezler.csv', mode="w", encoding="utf-8", newline='') as file:
             writer = csv.DictWriter(file, fieldnames=['Tez No', 'Yazar', 'Yıl', 'Tez Adı', 'Üniversite', 'Dil', 'Tez Türü', 'Konu'])
             writer.writeheader()
             writer.writerows(tez_listesi)
            print("Tez bilgileri CSV dosyasına kaydedildi.")

        else:
            print("var doc elemanları bulunamadı.")

    except Exception as e:
        print(f"Bir hata oluştu: {e}")

    finally:
        driver.quit()
        cursor.close()
        connection.close()

if __name__ == "__main__":
    scrape_theses_and_store_in_mysql()