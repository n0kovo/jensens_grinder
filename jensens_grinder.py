# -*- coding: utf-8 -*-
"""
Dette script plejede at kunne optjene point på clubjensens.dk
hvilket man kunne bruge til at betale for mad,
ved at referere brugere fra en central konto,
og oprette disse falske refererede profiler med falske
oplysninger for point.

Jensens har ændret systemet nu, så scriptet er forældet.
We had a good run.
"""


import requests
from bs4 import BeautifulSoup, SoupStrainer
from guerrillamail import GuerrillaMailSession
from time import sleep
from faker import *
import random
import simplejson as json

#Ændr dette
EMAIL = 'enelleranden@sharklasers.com'
PASSWORD = 'lolololololololol'


faker = Factory.create('dk_DK')

# Make sessions
s = requests.session() # Session til login
s2 = requests.session() # Session til registrering
gmsession = GuerrillaMailSession()


def get_form_key():
    """Get token for use in login POST"""
    key_req = s.get('http://www.clubjensens.dk/customer/account/login/')
    html = key_req.text
    soup = BeautifulSoup(html, 'lxml')
    value = soup.find('input', {'name': 'form_key'}).get('value')
    print "[+] CSRF TOKEN: %s" % value

    return value


def login():
    """Send login POST"""

    print '[+] LOGGER IND'

    post_data = {'form_key': get_form_key(),
                 'login[username]': EMAIL,
                 'login[password]': PASSWORD,
                 'send': ''}
    headers = {'Referer': 'https://www.clubjensens.dk/customer/account/login/',
    			'Conrent-Type': 'application/x-www-form-urlencoded'}

    req = s.post('http://www.clubjensens.dk/customer/account/loginPost/', data=post_data)
    print req.text


def send_invite(email):
    """Send Club Jensens referral email"""

    print '[+] Sender invitation til %s' % email

    url = 'http://www.clubjensens.dk/points/invitation/sendinvitation/'
    post_data = {'email[]': email,
                 'msg': ''}

    headers = {'Content-Type': 'application/x-www-form-urlencoded',
    			'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1)",
    			'Referer': 'https://www.clubjensens.dk/referrer/'}

    invite_reply = s.post(url, data=post_data, headers=headers)



def get_register_link(email):
    """Query Guerillamail server for email containing the referral link and return it when found"""
    while True:
        try:
            print '[+] Venter på referral-link'
            session = GuerrillaMailSession()
            session.set_email_address(email)
            mail = session.get_email_list()[0].guid
        except IndexError:
            sleep(4)
            continue
        else:
            emailbody = session.get_email(mail).body

            for link in BeautifulSoup(emailbody, 'lxml', parse_only=SoupStrainer('a')):
                if link.has_attr('href') and link['href'].endswith('club'):
                    return link['href']


def get_confirm_link(email):
    """Query Guerillamail server for email containing the account confirmation link and return it when found"""
    while True:
        try:

            print '[+] Venter på confirmation-link'

            session = GuerrillaMailSession()
            session.set_email_address(email)
            mail = session.get_email_list()[0].guid
        except IndexError:
            sleep(4)
            continue
        else:
            sleep(4)
            emailbody = session.get_email(mail).body

            for link in BeautifulSoup(emailbody, 'lxml', parse_only=SoupStrainer('a')):
                if link.has_attr('href') and link['href'].startswith('http://www.clubjensens.dk/customer'):
                    return link['href']


def random_user():
    """Returner fake navn med tilsvarende email-adresse"""

    # Liste med de forskellige guerillamail-domains
    domain = ['guerrillamail.com', 'guerrillamail.info', 'grr.la', 'guerrillamail.biz',
              'guerrillamail.net', 'guerrillamail.org', 'pokemail.net']

    # Fjern titler fra navnene, som Faker insisterer på at medtage
    name = faker.name().replace('Univ.Prof. ', '').replace('Prof. ', '').replace('Dr. ', '').replace('Fru ',
                                                                                                     '').replace('Hr ',
                                                                                                                 '')

    # Lav shortname uden mellemrum og convert til lowercase
    shortname = name.replace(' ', '').lower()

    # Hvis navnet uden tegn eller mellemrum er under 15 karakterer, tilføj et tal mellem 50 og 99
    if len(shortname) < 15:
        shortname += str(random.randint(50, 99))

    # Erstat danske bogstaver
    shortname = shortname.replace(u'æ', 'ae').replace(u'ø', 'o').replace(u'å', 'aa')

    # Fjern alt andet end bogstaver og tal
    emailname = filter(lambda x: x in 'abcdefghijklmnopqrstuvwxyz0123456789.', shortname)
    emailname = emailname.replace('univ.prof.', '').replace('prof.', '').replace('dr.', '')

    user = {'name': name,
            'email': emailname + '@' + (random.choice(domain))}

    return user


def random_address():
    """Returner dictionary med adresseinfo fra semitilfældig dansk adresse"""

    kommunekoder = [101, 147, 151, 153, 155, 157, 159, 161, 163, 165, 167, 169, 173, 175, 183, 185, 187, 190, 201, 210,
                    217, 219, 223, 230, 240, 250, 253, 259, 260, 265, 269, 270, 306, 316, 320, 326, 329, 330, 336, 340,
                    350, 360, 370, 376, 390, 400, 410, 411, 420, 430, 440, 450, 461, 479, 480, 482, 492, 510, 530, 540,
                    550, 561, 563, 573, 575, 580, 607, 615, 621, 630, 657, 661, 665, 671, 706, 707, 710, 727, 730, 740,
                    741, 746, 751, 756, 760, 766, 773, 779, 787, 791, 810, 813, 820, 825, 840, 846, 849, 851, 860]
    while True:
        url = 'https://dawa.aws.dk/adresser?kommunekode=%s&husnr=%s&struktur=mini&side=%s&per_side=1' % \
              (random.choice(kommunekoder), str(random.randint(1, 100)), str(random.randint(1, 100)))
        req = requests.get(url)
        if 'vejnavn' in req.text:
            break

    return json.loads(req.text)[0]


def get_register_form_key():
    """Get token for use in register POST"""

    key_req = s2.get('http://www.clubjensens.dk/')
    html = key_req.text
    soup = BeautifulSoup(html, 'lxml')
    value = soup.find('input', {'name': 'form_key'}).get('value')
    return value


def register_and_activate(**user_data):
    """Registrer ny konto og åbn aktiveringslink. Kaldes med random_user()-data som args"""

    print '[+] Registrerer bruger: %s' % user_data['name']

    fornavn = user_data['name'].split(' ', 1)[0]
    efternavn = user_data['name'].split(' ', 1)[-1]

    adresse = random_address()

    restauranter = [55, 54, 53, 52, 51, 50, 49, 48,
                    47, 46, 45, 44, 43, 42, 41, 40,
                    39, 38, 37, 36, 35, 33, 65, 64,
                    63, 62, 61, 60, 59, 58, 57, 56]

    birthday_day = str(random.choice(range(1, 30)))
    birthday_month = str(random.choice(range(1, 12)))
    birthday_year = str(random.choice(range(1950, 2000)))

    data = {"form_key": (None, get_register_form_key()),
            "success_url": (None, "http://www.clubjensens.dk/tak/"),
            "error_url": (None, ""),
            "auto_assign_card_number": (None, "1"),
            "facebook_id": (None, ""),
            "firstname": (None, fornavn),
            "lastname": (None, efternavn),
            "create_address": (None, "1"),
            "telephone": (None, "-"),
            "street[]": (None, adresse["vejnavn"] + " " + str(adresse["husnr"])),
            "postcode": (None, str(adresse["postnr"])),
            "city": (None, adresse["postnrnavn"]),
            "aw_ca_mobile": (None, str(random.randint(20000000, 89999999))),
            "country_id": (None, "DK"),
            "email": (None, user_data["email"]),
            "confirm_email": (None, user_data["email"]),
            "password": (None, "qazwsxedcrfvtgbyhnujm"),
            "confirmation": (None, "qazwsxedcrfvtgbyhnujm"),
            "aw_ca_fav_store": (None, str(random.choice(restauranter))),
            "region": (None, ""),
            "aw_ca_gender": (None, str(random.choice(list([1, 2])))),
            "aw_ca_birthday_day": (None, birthday_day),
            "aw_ca_birthday_month": (None, birthday_month),
            "aw_ca_birthday_year": (None, birthday_year),
            "aw_ca_birthday": (None, "%s/%s/%s" % (birthday_day, birthday_month, birthday_year)),
            "default_billing": (None, "1"),
            "default_shipping": (None, "1"),
            "checkbox": (None, "value")}

    headers = {"Pragma": "no-cache",
               "Origin": "http://www.clubjensens.dk",
               "Upgrade-Insecure-Requests": "1",
               "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/59.0.3071.115 Safari/537.3",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
               "Referer": "http://www.clubjensens.dk/",
               "Accept-Encoding": "gzip, deflate",
               "Content-Type": "application/x-www-form-urlencoded",
               "DNT": "1"}

    print "[+] Sender account create request"

    req = s2.post("http://www.clubjensens.dk/customer/account/createpost/",
                  files=data, headers=headers)

    req = s2.get(get_confirm_link(user_data["email"]))
    print "[+] KONTO AKTIVERET: %s (%s)" % (user_data["name"], user_data["email"])
    print


for i in range(50):
    login()
    user = random_user()

    send_invite(user["email"])

    req = s2.get(get_register_link(user["email"]))

    register_and_activate(**user)
    s.cookies.clear()
    s2.cookies.clear()
pass
