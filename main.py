import os
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

console_links = {
    'cpc': 'https://edgeemu.net/browse-cpc.htm',
    'atari5200': 'https://edgeemu.net/browse-5200.htm',
    'jaguar': 'https://edgeemu.net/browse-jaguar.htm',
    'c64': 'https://edgeemu.net/browse-c64.htm',
    'wsx': 'https://edgeemu.net/browse-wsx.htm',
    'pce': 'https://edgeemu.net/browse-pce.htm',
    'n64': 'https://edgeemu.net/browse-n64.htm',
    'nes': 'https://edgeemu.net/browse-nes.htm',
    'gbc': 'https://edgeemu.net/browse-gbc.htm',
    'snes': 'https://edgeemu.net/browse-snes.htm',
    '3do': 'https://edgeemu.net/browse-3do.htm',
    '32x': 'https://edgeemu.net/browse-32x.htm',
    'dc': 'https://edgeemu.net/browse-dc.htm',
    'md': 'https://edgeemu.net/browse-md.htm',
    'saturn': 'https://edgeemu.net/browse-saturn.htm',
    'ngcd': 'https://edgeemu.net/browse-ngcd.htm',
    'gba': 'https://edgeemu.net/browse-gba.htm'
}

def get_rom_links(console, game):
    if console not in console_links:
        print(f"Console {console} not supported.")
        return []
    
    url = console_links[console]
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    time.sleep(3)

    first_letter = game[0].upper()
    try:
        letter_link = driver.find_element(By.LINK_TEXT, first_letter)
        letter_link.click()
        time.sleep(3)
    except Exception as e:
        print(f"Failed to navigate to letter {first_letter}: {e}")
        driver.quit()
        return []

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    driver.quit()

    links = []
    table = soup.find('table', class_='roms')
    if table:
        for row in table.find_all('tr')[1:]:
            columns = row.find_all('td')
            if len(columns) > 0:
                game_name = columns[0].text.strip()
                if game.lower() in game_name.lower() and '(USA)' in game_name:
                    download_link = row.find('a')['href']
                    links.append("https://edgeemu.net/" + download_link)
                    break 
    return links


def download_roms(links, console, game):
    base_dir = os.path.join(os.getcwd(), 'roms', console, game)
    os.makedirs(base_dir, exist_ok=True)
    
    for link in links:
        response = requests.get(link, stream=True)
        filename = link.split('id=')[-1] + '.zip'
        filepath = os.path.join(base_dir, filename)
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f'Downloaded: {filename} to {filepath}')


def main():
    games = input("Enter games separated by commas (console:game): ")
    game_list = [g.strip() for g in games.split(',') if ':' in g]
    
    if not game_list:
        print("Invalid input format.")
        return

    for entry in game_list:
        console, game = entry.split(':')
        console = console.strip()
        game = game.strip()

        print(f"Searching for {game} on {console}...")
        links = get_rom_links(console, game)
        if links:
            print(f"Found {len(links)} ROM(s) for {game}. Downloading...")
            download_roms(links, console, game)
        else:
            print(f"No ROMs found for {game} on {console}.")

    print("All downloads complete!")


if __name__ == '__main__':
    main()
