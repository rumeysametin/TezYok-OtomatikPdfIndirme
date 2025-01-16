import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import re
import time
import csv
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def pdf_download(term="veri madenciliği"):
    # Selenium başlatılıyor
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    try:
        # Tez arama sayfasına giriş
        base_url = "https://tez.yok.gov.tr/UlusalTezMerkezi/"
        driver.get(base_url)

        search_box = driver.find_element(By.ID, "neden")
        search_box.send_keys(term)

        find_button = driver.find_element(By.XPATH, "//input[@value='     Bul      ']")
        find_button.click()

        time.sleep(5)

        tez_listesi = []

        # Sayfanın kaynağını alınıyor
        while True:
            page_source = driver.page_source
            var_doc_matches = re.findall(r"var doc = {.*?};", page_source, re.DOTALL)

            if var_doc_matches:
                for idx, doc in enumerate(var_doc_matches, start=1):
                    tez_data = {
                        'Tez No': '',
                        'Yazar': '',
                        'Yıl': '',
                        'Tez Adı': '',
                        'Üniversite': '',
                        'Dil': '',
                        'Tez Türü': '',
                        'Konu': '',
                        'Tez Detayı': ''
                    }

                    # Tez detayına gidip PDF'yi indirme
                    try:
                        detail_button = driver.find_element(By.XPATH, f"//*[@id='div1']/table/tbody/tr[{idx}]/td[2]/span")
                        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(detail_button))
                        ActionChains(driver).move_to_element(detail_button).click().perform()

                        time.sleep(2)  # Detay pop-up'ının yüklenmesi için bekle

                        # PDF indirme
                        try:
                            pdf_link = driver.find_element(By.XPATH, "//*[@id='dialog-modal']/p/table/tbody/tr[2]/td[2]/a")
                            pdf_url = pdf_link.get_attribute("href")
                            driver.get(pdf_url)
                        except Exception as e:
                            print(f"PDF indirme yapılamadı: {tez_data['Tez No']}, Hata: {e}")

                        # Detay kutusunu kapat
                        close_button = driver.find_element(By.XPATH, "/html/body/div[3]/div[1]/a")
                        close_button.click()
                    except Exception as e:
                        print(f"Tez detayına tıklanırken hata oluştu: {e}")

                    tez_listesi.append(tez_data)

            # "İleri" butonuna tıklama işlemi
            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//*[@id='div1']/table/tfoot/tr/td/div/div[1]/div/ul/li[7]/a"))
                )
                next_button.click()
                time.sleep(5)  # Yeni sayfanın yüklenmesi için bekle
                
            except Exception as e:
                print("Sonraki sayfa bulunamadı veya işlem yapılamadı.")
                break  # Eğer ileri butonu yoksa veya tıklanamıyorsa, döngüden çık

    except Exception as e:
        print(f"Bir hata oluştu: {e}")

    finally:
        driver.quit()
        cursor.close()
        connection.close()

if __name__ == "__main__":
    pdf_download()