from bs4 import BeautifulSoup
import requests


url = 'https://finance.yahoo.com/quote/AAPL?p=AAPL&.tsrc=fin-srch'
page = requests.get(url)


soup = BeautifulSoup(page.content, 'html.parser')
ressultappl = soup.find('table', class_='W(100%)').find(
    'td', class_="Ta(end)").find('span').text

resultamazon = soup.find(
    'div', class_='Pos(a) W(300px) End(0) T(0) tablet_D(n)--noRightRail').find()
# .find('td', class_="Fz(14px) Py(6px)").find('span').text

print(resultamazon)
