import scraperwiki
import requests
from bs4 import BeautifulSoup
import re


def add_operator(mcc, mnc, brand, operator, status, country, country_code, db):
    assert re.match('^\d{3}$', mcc)
    assert re.match('^\d{2,3}$', mnc)
    assert re.match('^[A-Z/-]*$', country_code)
    assert status.lower() in ['discontinued', 'inactive', 'not operational', 'operational', 'planned', 'planning', 'reserved', 'returned spare', 'temporary operational', 'unknown', 'suspended', 'test network', '']
    db.append({
        'mccmnc': mcc + mnc,
        'brand': brand,
        'operator': operator,
        'country': country,
        'status': status,
        'countryCode': country_code
    })


def scan_table(table, country, country_code, db):
    rows = table.find_all('tr')
    hdr = rows.pop(0).find_all('th')
    assert hdr[0].text == u'MCC'
    assert hdr[1].text == u'MNC'
    assert hdr[2].text == u'Brand'
    assert hdr[3].text == u'Operator'
    assert hdr[4].text == u'Status'
    for row in rows:
        td = row.find_all('td')
        mcc = td[0].text
        mnc = td[1].text
        brand = td[2].text.replace('[citation needed]', '')
        operator = td[3].text.replace('[citation needed]', '')
        status = re.sub(r'\([^)]*\)', '', td[4].text.replace('[citation needed]', '')).strip()
        if mcc and mnc and '?' not in mnc:
            if '-' in mnc:
                # TODO: mnc range
                pass
            else:
                add_operator(mcc, mnc, brand, operator, status.lower(), country, country_code, db)


def contains_headline(tag):
    return tag.find(class_='mw-headline') is not None


def main():
    db = []
    soup = BeautifulSoup(requests.get('https://en.wikipedia.org/wiki/Mobile_country_code').text, 'xml')
    for th in soup.find_all('th', text='MCC'):
        table = th.find_parent('table')
        tab_title = table.find_previous_sibling(contains_headline).find(class_='mw-headline').findAll(text=True)
        tab_title = ''.join(tab_title).split(' - ')
        assert (len(tab_title) == 1) or (len(tab_title) == 2)
        country = tab_title.pop(0)
        country_code = ''.join(tab_title)
        scan_table(table, country, country_code, db)

    scraperwiki.sqlite.save(unique_keys=['mccmnc'], data=db)


main()
