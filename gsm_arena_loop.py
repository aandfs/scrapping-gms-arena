import requests
import re
import time
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

# Fungsi membaca URL dari file
def read_links_from_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines() if line.strip()]

# Header untuk menyamar sebagai browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

# Fungsi mengambil halaman HTML
def fetch_page(url):
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"Gagal mengambil data dari {url}: {e}")
        return None

# Fungsi scraping spesifikasi dan ulasan
def scrape_data(specs_url):
    base_url = "https://www.gsmarena.com/"
    filename = specs_url.split("/")[-1].replace(".php", "") + ".md"

    specs_soup = fetch_page(specs_url)

    if not specs_soup:
        print(f"Gagal mengambil halaman spesifikasi: {specs_url}")
        return

    # Ambil link review dari halaman spesifikasi
    review_link_element = specs_soup.find("li", class_="article-info-meta-link-review")
    review_url = base_url + review_link_element.find("a")["href"] if review_link_element else None

    # Ambil spesifikasi
    specs_text = specs_soup.find('div', id='specs-list').get_text("\n", strip=True) if specs_soup.find('div', id='specs-list') else "Spesifikasi tidak ditemukan."

    # Ambil ulasan jika ada
    reviews_text = "Ulasan tidak ditemukan."
    if review_url:
        reviews_soup = fetch_page(review_url)
        if reviews_soup and reviews_soup.find('div', id='review-body'):
            reviews_text = reviews_soup.find('div', id='review-body').get_text("\n", strip=True)

    # Gabungkan data
    combined_data = f"Spec:\n{specs_text}\n\nReview:\n{reviews_text}"

    # Simpan ke file
    with open(filename, "w", encoding="utf-8") as f:
        f.write(combined_data)

    print(f"Scraping selesai! Data telah disimpan ke {filename}")

    # Delay 5 detik untuk menghindari blokir
    time.sleep(4)

# Baca daftar link dari file
links = read_links_from_file("links_apple.txt")

# Loop melalui setiap link secara berurutan (tanpa multi-threading agar delay bekerja)
for link in links:
    scrape_data(link)

print("\nSemua scraping selesai!")
