#!/usr/bin/env python3
import os
import requests
import sys

from collections import defaultdict
from datetime import datetime, timedelta
from lxml import etree, html
from orjson import loads, dumps
from re import search

#from utils.going import get_surface
from utils.header import RandomHeader
#from utils.lxml_funcs import find
#from utils.region import get_region

import time
from bs4 import BeautifulSoup
import pandas as pd
import shutil
import datetime

random_header = RandomHeader()

date_ext = "tomorrow"
date = "-"

def get_text(element):  #  this is copied from RC_menu_V03_RTV.py
    try:
        text = element.text.strip()
    except:
        text = None
    
    return text

def menu(): #Top Menu   this is copied from RC_menu_V03_RTV.py
    os.system('cls')
    print('Please select option below:\n')
    print('\t1. Race Cards\n')
    print('\t2. Odds\n')
    print('\t3. Results\n')
    print('\t4. Non Runners, Aids etc.\n')
    print('\t5. Going \n')
    print('\t6. Exit\n')
    print()
    return 

def sub_menu_1(): #Scrape Race Cards        this is copied from RC_menu_V03_RTV.py
    os.system('cls')
    print('\t\t1) Tomorrow’s Cards\n')
    print('\t\t2) Today’s Cards\n')
    print('\t\t3) Choose date\n')
    print('\t\tm) Main menu')
    print()
    return

def sub_menu_2(): #Scrape Odds      this is copied from RC_menu_V03_RTV.py
    os.system('cls')
    print('\t\t1) Tomorrow’s Odds\n')
    print('\t\t2) Today’s Odds\n')
    print('\t\tm) Main menu')
    print()
    return

def sub_menu_3(): #Scrape Race Results      this is copied from RC_menu_V03_RTV.py
    os.system('cls')
    print('\t\t1) Today’s Results\n')
    print('\t\t2) Yesterday’s Results\n')
    print('\t\t3) Choose date\n')
    print('\t\tm) Main menu')
    print()
    return

def sub_menu_4(): #Non Runners, Aids etc.       this is copied from RC_menu_V03_RTV.py
    os.system('cls')
    print('\t\t1) Non Runners\n')
    print('\t\t2) Travellers\n')
    print('\t\t3) Aids\n')
    print('\t\tm) Main menu')
    print()
    return

def sub_menu_5(): #Scrape Going     this is copied from RC_menu_V03_RTV.py
    os.system('cls')
    print('\t\t1) Tomorrow’s Going\n')
    print('\t\t2) Today’s Going\n')
    print('\t\tm) Main menu')
    print()
    return

def clear_odd_nr():
    src="Racecards/RacecardsOdds_Blank.xlsx"
    dst="Racecards/RacecardsOdds.xlsx"
    shutil.copy(src,dst)

    print("File %s is replaced successfully" % dst)

    # renamed the file f.txt to d.txt
    src1="Racecards/NonRunners_Blank.xlsx"
    dst1="Racecards/NonRunners.xlsx"
    shutil.copy(src1,dst1)

    print("File %s is replaced successfully" % dst1)
    #time.sleep(2)
    return

def get_going():
    global date
    global date_ext
    odds_date = date_ext
    
    url = f'https://www.racingtv.com/racecards/{date_ext}'
    
    try:
        res = requests.get(url, headers = headersrtv)
    except:
        print('Date or Connection error occured! \nTry again!!')
        return
    
    soup = BeautifulSoup(res.text, 'html.parser')
    main_row = soup.select('.race-selector__title')
    comments =  soup.select('.race-selector__conditions')
    
    race_data = []
    for row, cmt in zip(main_row, comments):
        course = row.text
        going = cmt.text
        
        race_data.append({
            'Course': course, 'Going': going
        })
    
    df_race = pd.DataFrame(race_data)
    df_race['Course'] = df_race['Course'].str.replace('Hamilton Park', 'Hamilton')    #Replace Course names
    
    df = df_race
    
    return df

def get_nr(date=None):
    
    url = f'https://www.sportinglife.com/racing/non-runners'
    resp = requests.get(url,headers=headers)

    soup = BeautifulSoup(resp.text,'html.parser')

    nr_horse = soup.find_all('span', class_='NonRunners__Horse-o6sh1j-4 cSiKAk')
    
    rows = []

    for nr in nr_horse:
        horsename = get_text(nr).split(maxsplit=1)[1]
        #horsename = nr.split(maxsplit=1)[1]
        item = {'HorseName':horsename}
        rows.append(item)
        continue

    df = pd.DataFrame(rows)
    df['HorseName'] = df['HorseName'].str.upper()
    df['HorseName'] = df['HorseName'].str.replace("'",'')
    
    #save_excel(df, main_word = r'Racecards\NonRunners', date=date)

    return df

def get_travel(date=None):
    
    travel_list = []
    url = "https://www.skysports.com/racing/hints-and-pointers/longest-travellers"
    res = requests.get(url, headers = headers)
    #soup = BeautifulSoup(res.content, 'lxml')
    soup = BeautifulSoup(res.content, "html.parser")
    rows = soup.find_all('tr')[1:]
    
    for row in rows:
        travel_dict = {}
        travel_dict['Horse'] = get_text(row.td).split('(')[0].strip()
        
        travel_dict['Wins'] = get_text(row.find_all('td')[1])
        travel_dict['WinPct'] = get_text(row.find_all('td')[3])
        travel_dict['Places'] = get_text(row.find_all('td')[4])
        travel_dict['PlacePct'] = get_text(row.find_all('td')[5])
        travel_dict['Race'] = get_text(row.find_all('td')[7])
        #travel_dict['Course'] = str(travel_dict['Course']).split(' ')[0].strip()
        travel_dict['Date'] = date

        travel_list.append(travel_dict)
        
    return travel_list

def get_aids(date=None):
    
    aids_list = []
    url = "https://www.skysports.com/racing/hints-and-pointers/first-time-blinkers"
    res = requests.get(url, headers = headers)
    #soup = BeautifulSoup(res.content, 'lxml')
    soup = BeautifulSoup(res.content, "html.parser")
    rows = soup.find_all('tr')[1:]
    
    for row in rows:
        aids_dict = {}
        aids_dict['Horse'] = get_text(row.td).split('(')[0].strip()
        
        aids_dict['Wins'] = get_text(row.find_all('td')[1])
        aids_dict['WinPct'] = get_text(row.find_all('td')[3])
        aids_dict['Places'] = get_text(row.find_all('td')[4])
        aids_dict['PlacePct'] = get_text(row.find_all('td')[5])
        aids_dict['Race'] = get_text(row.find_all('td')[6])
        #aids_dict['Course'] = str(aids_dict['Course']).split(' ')[0].strip()
        aids_dict['Date'] = date

        aids_list.append(aids_dict)
        
    return aids_list

def get_rtv_odds(ext = ''):
    global date
    global date_ext
    global race_cnt
    odds_date = date_ext
    
    url = f'https://www.racingtv.com/racecards/{date_ext}'
    
    try:
        res = requests.get(url, headers = headersrtv)
    except:
        print('Date or Connection error occured! \nTry again!!')
        return
    
    soup = BeautifulSoup(res.text, 'html.parser')
    meetings = soup.select('.race-selector__times__race')

    meetings1 = [a['href'] for a in soup.select('.race-selector__times__race')]
    
    if race_cnt == 0:
        course_num = len(meetings1)
    else:
        course_num = race_cnt

    cnt01 = 0
    n = 0

    if course_num == 0:
      print('Provide a upcoming valid date')
      return
    
    for track in meetings1[:course_num]:
        cnt01 = cnt01 + 1
        trackref = track.split("/")[2]
        print(cnt01, ": ", trackref)

    if race_cnt == 0:
        need = input(f'{course_num} courses found \nHow many courses to scrape? Press \'a\' for all :\n')
        if need == 'a':
            n = course_num
        else:
            try:
                n = int(need)
            except:
                print('Invalid input !')
                return
        
    else:
        n = race_cnt
    
    cnt01 = 0
    race_data = []
    for mtm in meetings[:course_num]:
        cnt01 = cnt01 + 1
        racetime = mtm.text
        href = mtm.attrs
        htxt = Text(href)
        url_race = htxt.partition("/")[2]
        url_race = "/" + url_race.rpartition("'")[0]
        print(cnt01, racetime, url_race)
        time.sleep(1)
        race_data.extend(get_rtv_data(url_race, date, racetime))
        print(f"Meeting {url_race.split('/')[2]} scraping completed")
        if cnt01 == n:
            break
    
    df_race = pd.DataFrame(race_data)
    df_race['Horse'] = df_race['Horse'].str.title()
    df_race = df_race[df_race.Odds != ""] #remove rows where odds = blank
    
   
    print(df_race)
    
    df = df_race

    save_excel(df, main_word='Racecards\RacecardsOdds', date=date)
    
    return race_data

def save_excel(df, main_word, date=None):
    print('Saving data in excel files')

    try:
        df.to_excel(f'{main_word}.xlsx', index = False)
    except:
        print(f'{main_word}.xlsx saving failed. You may need to remove or close the existing {main_word}.xlsx')
    
    print(main_word, ": ",'Saved')
    time.sleep(3)
    menu()
    return


def get_racecards_data(base_url):    # , date):  # this is copied from RC_menu_V03_RTV.py 
    racecards_list = []
    res = requests.get(base_url, headers=random_header.header())
    soup = BeautifulSoup(res.content, "html.parser")
    #race_id = base_url.split('/')[7]
    course = get_text(soup.find('h1',class_='ui-h1 RC-courseHeader__name')).strip()
    inforow = soup.find_all('div', class_='RC-headerBox__infoRow__content')
    value = get_text(inforow[0]).strip()
    runner_num = get_text(inforow[1]).split(' ')[0].strip()
    going = get_text(inforow[2]).strip()
    stalls = get_text(inforow[3]).strip()
    hrs, mnt = get_text(soup.find('span',class_='RC-courseHeader__time')).split(':')
    if int(hrs) == 12 or int(hrs) == 11:
        hrs = str(int(hrs) - 12)
    time = f'{int(hrs)+12}:{mnt}'

    dist = get_text(soup.find('strong',class_='RC-cardHeader__distance')).strip()
    desc = get_text(soup.find('span', {'data-test-selector':'RC-header__raceInstanceTitle'})).strip()
    
    try:
        klass = get_text(soup.find('span', {'data-test-selector':'RC-header__raceClass'})).strip()
    except:
        klass = 'not provided'

    try:
        agelimit = get_text(soup.find('span', {'data-test-selector':'RC-header__rpAges'})).strip()
    except:
        agelimit = 'not provided'
        
    runners = soup.find_all('div', class_='RC-runnerCardWrapper')
    
    for run in runners:
        no = get_text(run.select_one('.RC-runnerNumber__no'))
        draw = get_text(run.select_one('.RC-runnerNumber__draw'))[1:-1]
        form = get_text(run.select_one('.RC-runnerInfo__form'))
        horse = get_text(run.select_one('.js-bestOddsRunnerHorseName'))
        age = get_text(run.select_one('.RC-runnerAge'))
        weight = '-'.join(get_text(run.select_one('.RC-runnerWgt__carried')).split())
        or_ = get_text(run.select_one('.RC-runnerOr'))
        jockey = get_text(run.select_one('.RC-runnerInfo_jockey .js-popupLink'))
        trainer = get_text(run.select_one('.RC-runnerInfo_trainer .js-popupLink'))
        allow = get_text(run.select_one('.RC-runnerInfo_jockey .RC-runnerInfo__count'))
        rtf = get_text(run.select_one('.js-RC-runnerInfo_rtf')) # trainer horses on form in 16days
        ts = get_text(run.select_one('.RC-runnerTs'))
        rpr = get_text(run.select_one('.RC-runnerRpr'))
        days = get_text(run.select_one('.RC-runnerStats__lastRun'))
        aid = get_text(run.select_one('.RC-runnerHeadgearCode'))
        cdb = ' '.join([get_text(e) for e in run.select('.RC-runnerStats__cdbf')])
        tips = ' '.join([get_text(e) for e in run.select('.RC-runnerStats__tips')])

       #CANNOT SEEM TO GET odds = get_text(run.select_one('.RC-runnerPriceWrapper .js-PC-subscribed'))
        
        try:
            st, lb = weight.split('-')
            wtlbs = int(st) * 14 + int(lb)
        except:
            wtlbs = None
        
        racecards_list.append({'Course': course, 'Going': going, 'Time': time, 'RaceDesc': desc, 'Dist':dist,
                                'Class': klass, 'AgeLimit': agelimit, 'Value': value, 'Run': runner_num, 
                                'StallPos': stalls, 'Tips': tips,
                                'No': no, 'Draw': draw, 'Form': form, 'Horse': horse, 'Age': age, 'Weight': weight,
                                'OR': or_, 'Jockey': jockey, 'Trainer': trainer, 'Allow': allow, 'RTF': rtf, 'TS': ts,
                                'RPR': rpr, 'Days': days, 'Aid': aid, 'WtLbs': wtlbs, 'CDB': cdb, 'RaceURL': base_url}) # 'Date': date, 'Odds': odds
        
        
    return racecards_list


def clean_name(name):
    if name:
        return name.strip().replace("'", '').lower().title()
    else:
        return ''


def distance_to_furlongs(distance):
    dist = distance.strip().replace('¼', '.25').replace('½', '.5').replace('¾', '.75')

    if 'm' in dist:
        if len(dist) > 2:
            dist = int(dist.split('m')[0]) * 8 + float(dist.split('m')[1].strip('f'))
        else:
            dist = int(dist.split('m')[0]) * 8
    else:
        dist = dist.strip('f')

    return float(dist)


def get_going_info(session, date):
    r = session.get(f'https://www.racingpost.com/non-runners/{date}', headers=random_header.header())
    doc = html.fromstring(r.content.decode())

    json_str = doc.xpath('//body/script')[0].text.replace('var __PRELOADED_STATE__ = ', '').strip().strip(';')

    going_info = defaultdict(dict)

    for course in loads(json_str):
        going, rail_movements = parse_going(course['going'])

        course_id = 0
        course_name = ''

        if course['courseName'] == 'Belmont At The Big A':
            course_id = 255
            course_name = 'Aqueduct'
        else:
            course_id = int(course['raceCardsCourseMeetingsUrl'].split('/')[2])
            course_name = course['courseName']

        going_info[course_id]['course'] = course_name
        going_info[course_id]['going'] = going
        going_info[course_id]['stalls'] = course['stallsPosition']
        going_info[course_id]['rail_movements'] = rail_movements
        going_info[course_id]['weather'] = course['weather']

    return going_info


def get_pattern(race_name):
    regex_group = '(\(|\s)((G|g)rade|(G|g)roup) (\d|[A-Ca-c]|I*)(\)|\s)'
    match = search(regex_group, race_name)

    if match:
        pattern = f'{match.groups()[1]} {match.groups()[4]}'.title()
        return pattern.title()

    if any(x in race_name.lower() for x in {'listed race', '(listed'}):
        return 'Listed'

    return ''


def get_race_type(doc, race, distance):
        race_type = ''
        fences = find(doc, 'div', 'RC-headerBox__stalls')

        if 'hurdle' in fences.lower():
            race_type = 'Hurdle'
        elif 'fence' in fences.lower():
            race_type = 'Chase'
        else:
            if distance >= 12:
                if any(x in race for x in {'national hunt flat', 'nh flat race', 'mares flat race'}):
                    race_type = 'NH Flat'
                if any(x in race for x in {'inh bumper', ' sales bumper', 'kepak flat race', 'i.n.h. flat race'}):
                    race_type = 'NH Flat'
                if any(x in race for x in {' hurdle', '(hurdle)'}):
                    race_type = 'Hurdle'
                if any(x in race for x in {' chase', '(chase)', 'steeplechase', 'steeple-chase', 'steeplchase', 'steepl-chase'}):
                    race_type = 'Chase'

        if race_type == '':
            race_type = 'Flat'

        return race_type


def get_race_urls_old(session, racecard_url):
    r = session.get(racecard_url, headers=random_header.header())
    doc = html.fromstring(r.content)

    race_urls = []

    for meeting in doc.xpath("//section[@data-accordion-row]"):
        course = meeting.xpath(".//span[contains(@class, 'RC-accordion__courseName')]")[0]
        if valid_course(course.text_content().strip().lower()):
            for race in meeting.xpath(".//a[@class='RC-meetingItem__link js-navigate-url']"):
                race_urls.append('https://www.racingpost.com' + race.attrib['href'])

    return sorted(list(set(race_urls)))


def get_meetings(session):       # was def get_race_urls(session, racecard_url):
    racecard_url = f'https://www.racingpost.com/racecards/{date_ext}'
    r = session.get(racecard_url, headers=random_header.header())
    doc = html.fromstring(r.content)

    #race_urls = []
    race_data = []  # RC_menu_V03_RTV.py

    for meeting in doc.xpath("//section[@data-accordion-row]"):
        course = meeting.xpath(".//span[contains(@class, 'RC-accordion__courseName')]")[0]
        if valid_course(course.text_content().strip().lower()):
            for race in meeting.xpath(".//a[@class='RC-meetingItem__link js-navigate-url']"):
                #race_urls.append('https://www.racingpost.com' + race.attrib['href'])
                race_data.extend(get_racecards_data('https://www.racingpost.com' + race.attrib['href']))
                #time.sleep(1)
            #print(f"Meeting {race_urls.split('/')[3]} scraping completed") #try to print when each course if scraped
    
    df_race = pd.DataFrame(race_data)
    df_race = df_race[df_race.No != "NR"] #remove rows where No = NR
    df_race.drop_duplicates(subset="Horse", keep="first", inplace=True)
    df_race.set_index('Horse')


    # if not os.path.exists('../racecards'):
    #     os.makedirs(f'../racecards')

    # with open(f'../racecards/{date}.json', 'w', encoding='utf-8') as f:
    #     f.write(dumps(races).decode('utf-8'))

    df_race.to_excel(r'C:\Users\chris\Documents\UKHR\PythonSand\df_race_data.xlsx')

    return


def get_runners(session, profile_urls):
    runners = {}

    for url in profile_urls:
        r = session.get(url, headers=random_header.header())
        doc = html.fromstring(r.content)

        runner = {}

        try:
            json_str = doc.xpath('//body/script')[0].text.split('window.PRELOADED_STATE =')[1].split('\n')[0].strip().strip(';')
            js = loads(json_str)
        except IndexError:
            split = url.split('/')
            runner['horse_id'] = int(split[5])
            runner['name'] = split[6].replace('-', ' ').title()
            runner['broken_url'] = url
            runners[runner['horse_id']] = runner
            continue

        runner['horse_id'] = js['profile']['horseUid']
        runner['name'] = clean_name(js['profile']['horseName'])
        runner['dob'] = js['profile']['horseDateOfBirth'].split('T')[0]
        runner['age'] = int(js['profile']['age'].split('-')[0])
        runner['sex'] = js['profile']['horseSex']
        runner['sex_code'] = js['profile']['horseSexCode']
        runner['colour'] = js['profile']['horseColour']
        runner['region'] = js['profile']['horseCountryOriginCode']

        runner['breeder'] = js['profile']['breederName']
        runner['dam'] = clean_name(js['profile']['damHorseName'])
        runner['dam_region'] = js['profile']['damCountryOriginCode']
        runner['sire'] = clean_name(js['profile']['sireHorseName'])
        runner['sire_region'] = js['profile']['sireCountryOriginCode']
        runner['grandsire'] = clean_name(js['profile']['siresSireName'])
        runner['damsire'] = clean_name(js['profile']['damSireHorseName'])
        runner['damsire_region'] = js['profile']['damSireCountryOriginCode']

        runner['trainer'] = clean_name(js['profile']['trainerName'])
        runner['trainer_id'] = js['profile']['trainerUid']
        runner['trainer_location'] = js['profile']['trainerLocation']
        runner['trainer_14_days'] = js['profile']['trainerLast14Days']

        runner['owner'] = clean_name(js['profile']['ownerName'])

        runner['prev_trainers'] = js['profile']['previousTrainers']

        if runner['prev_trainers']:
            prev_trainers = []

            for trainer in runner['prev_trainers']:
                prev_trainer = {}
                prev_trainer['trainer'] = trainer['trainerStyleName']
                prev_trainer['trainer_id'] = trainer['trainerUid']
                prev_trainer['change_date'] = trainer['trainerChangeDate'].split('T')[0]
                prev_trainers.append(prev_trainer)

            runner['prev_trainers'] = prev_trainers

        runner['prev_owners'] = js['profile']['previousOwners']

        if runner['prev_owners']:
            prev_owners = []

            for owner in runner['prev_owners']:
                prev_owner = {}
                prev_owner['owner'] = owner['ownerStyleName']
                prev_owner['owner_id'] = owner['ownerUid']
                prev_owner['change_date'] = owner['ownerChangeDate'].split('T')[0]
                prev_owners.append(prev_owner)

            runner['prev_owners'] = prev_owners

        if js['profile']['comments']:
            runner['comment'] = js['profile']['comments'][0]['individualComment']
            runner['spotlight'] = js['profile']['comments'][0]['individualSpotlight']
        else:
            runner['comment'] = None
            runner['spotlight'] = None

        if js['profile']['medical']:
            medicals = []

            for med in js['profile']['medical']:
                medical = {}
                medical['date'] = med['medicalDate'].split('T')[0]
                medical['type'] = med['medicalType']
                medicals.append(medical)

            runner['medical'] = medicals

        runner['quotes'] = None

        if js['quotes']:
            quotes = []

            for q in js['quotes']:
                quote = {}
                quote['date'] = q['raceDate'].split('T')[0]
                quote['horse'] = q['horseStyleName']
                quote['horse_id'] = q['horseUid']
                quote['race'] = q['raceTitle']
                quote['race_id'] = q['raceId']
                quote['course'] = q['courseStyleName']
                quote['course_id'] = q['courseUid']
                quote['distance_f'] = q['distanceFurlong']
                quote['distance_y'] = q['distanceYard']
                quote['quote'] = q['notes']
                quotes.append(quote)

            runner['quotes'] = quotes

        runner['stable_tour'] = None

        if js['stableTourQuotes']:
            quotes = []

            for q in js['stableTourQuotes']:
                quote = {}
                quote['horse'] = q['horseName']
                quote['horse_id'] = q['horseUid']
                quote['quote'] = q['notes']
                quotes.append(quote)

            runner['stable_tour'] = quotes

        runners[runner['horse_id']] = runner

    return runners


def parse_going(going_info):
    going = going_info
    rail_movements = ''

    if 'Rail movements' in going_info:
        going_info = going_info.replace('movements:', 'movements')
        rail_movements = [x.strip() for x in going_info.split('Rail movements')[1].strip().strip(')').split(',')]
        going = going_info.split('(Rail movements')[0].strip()

    return going, rail_movements


def parse_races(session, race_urls, date):
    races = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))

    going_info = get_going_info(session, date)

    for url in race_urls:
        r = session.get(url, headers=random_header.header(), allow_redirects=False)

        if r.status_code != 200:
            print('Failed to get racecard.')
            print(f'URL: {url}')
            print(f'Response: {r.status_code}')
            continue

        try:
            doc = html.fromstring(r.content)
        except etree.ParserError:
            continue

        race = {}

        url_split = url.split('/')

        race['course'] = find(doc, 'h1', 'RC-courseHeader__name')

        if race['course'] == 'Belmont At The Big A':
            race['course_id'] = 255
            race['course'] = 'Aqueduct'
        else:
            race['course_id'] = int(url_split[4])

        race['race_id'] = int(url_split[7])
        race['date'] = url_split[6]
        race['off_time'] = find(doc, 'span', 'RC-courseHeader__time')
        race['race_name'] = find(doc, 'span', 'RC-header__raceInstanceTitle')
        race['distance_round'] = find(doc, 'strong', 'RC-header__raceDistanceRound')
        race['distance'] = find(doc, 'span', 'RC-header__raceDistance')
        race['distance'] = race['distance_round'] if not race['distance'] else race['distance'].strip('()')
        race['distance_f'] = distance_to_furlongs(race['distance_round'])
        race['region'] = get_region(str(race['course_id']))
        race['pattern'] = get_pattern(race['race_name'].lower())
        race['race_class'] = find(doc, 'span', 'RC-header__raceClass')
        race['race_class'] = race['race_class'].strip('()') if race['race_class'] else ''
        race['type'] = get_race_type(doc, race['race_name'].lower(), race['distance_f'])

        if not race['race_class']:
            if race['pattern']:
                race['race_class'] = 'Class 1'

        try:
            band = find(doc, 'span', 'RC-header__rpAges').strip('()').split()
            if band:
                race['age_band'] = band[0]
                race['rating_band'] = band[1] if len(band) > 1 else None
            else:
                race['age_band'] = None
                race['rating_band'] = None
        except AttributeError:
            race['age_band'] = None
            race['rating_band'] = None

        prize = find(doc, 'div', 'RC-headerBox__winner').lower()
        race['prize'] = prize.split('winner:')[1].strip() if 'winner:' in prize else None
        field_size = find(doc, 'div', 'RC-headerBox__runners').lower()
        if field_size:
            race['field_size'] = int(field_size.split('runners:')[1].split('(')[0].strip())
        else:
            race['field_size'] = ''

        try:
            race['going_detailed'] = going_info[race['course_id']]['going']
            race['rail_movements'] = going_info[race['course_id']]['rail_movements']
            race['stalls'] = going_info[race['course_id']]['stalls']
            race['weather'] = going_info[race['course_id']]['weather']
        except KeyError:
            race['going'] = None
            race['rail_movements'] = None
            race['stalls'] = None
            race['weather'] = None

        going = find(doc, 'div', 'RC-headerBox__going').lower()
        race['going'] = going.split('going:')[1].strip().title() if 'going:' in going else ''

        race['surface'] = get_surface(race['going'])

        profile_hrefs = doc.xpath("//a[@data-test-selector='RC-cardPage-runnerName']/@href")
        profile_urls = ['https://www.racingpost.com' + a.split('#')[0] + '/form' for a in profile_hrefs]

        runners = get_runners(session, profile_urls)

        for horse in doc.xpath("//div[contains(@class, ' js-PC-runnerRow')]"):
            horse_id = int(find(horse, 'a', 'RC-cardPage-runnerName', attrib='href').split('/')[3])

            if 'broken_url' in runners[horse_id]:
                sire = find(horse, 'a', 'RC-pedigree__sire').split('(')
                dam = find(horse, 'a', 'RC-pedigree__dam').split('(')
                damsire = find(horse, 'a', 'RC-pedigree__damsire').lstrip('(').rstrip(')').split('(')

                runners[horse_id]['sire'] = clean_name(sire[0])
                runners[horse_id]['dam'] = clean_name(dam[0])
                runners[horse_id]['damsire'] = clean_name(damsire[0])

                runners[horse_id]['sire_region'] = sire[1].replace(')', '').strip()
                runners[horse_id]['dam_region'] = dam[1].replace(')', '').strip()
                runners[horse_id]['damsire_region'] = damsire[1].replace(')', '').strip()

                runners[horse_id]['age'] = find(horse, 'span', 'RC-cardPage-runnerAge', attrib='data-order-age')

                sex = find(horse, 'span', 'RC-pedigree__color-sex').split()

                runners[horse_id]['colour'] = sex[0]
                runners[horse_id]['sex_code'] = sex[1].capitalize()

                runners[horse_id]['trainer'] = find(horse, 'a', 'RC-cardPage-runnerTrainer-name', attrib='data-order-trainer')

            runners[horse_id]['number'] = int(find(horse, 'span', 'RC-cardPage-runnerNumber-no', attrib='data-order-no'))

            try:
                runners[horse_id]['draw'] = int(find(horse, 'span', 'RC-cardPage-runnerNumber-draw', attrib='data-order-draw'))
            except ValueError:
                runners[horse_id]['draw'] = None

            runners[horse_id]['headgear'] = find(horse, 'span', 'RC-cardPage-runnerHeadGear')
            runners[horse_id]['headgear_first'] = find(horse, 'span', 'RC-cardPage-runnerHeadGear-first')

            try:
                runners[horse_id]['lbs'] = int(find(horse, 'span', 'RC-cardPage-runnerWgt-carried', attrib='data-order-wgt'))
            except ValueError:
                runners[horse_id]['lbs'] = None

            try:
                runners[horse_id]['ofr'] = int(find(horse, 'span', 'RC-cardPage-runnerOr', attrib='data-order-or'))
            except ValueError:
                runners[horse_id]['ofr'] = None

            try:
                runners[horse_id]['rpr'] = int(find(horse, 'span', 'RC-cardPage-runnerRpr', attrib='data-order-rpr'))
            except ValueError:
                runners[horse_id]['rpr'] = None

            try:
                runners[horse_id]['ts'] = int(find(horse, 'span', 'RC-cardPage-runnerTs', attrib='data-order-ts'))
            except ValueError:
                runners[horse_id]['ts'] = None

            claim = find(horse, 'span', 'RC-cardPage-runnerJockey-allowance')
            jockey = horse.find('.//a[@data-test-selector="RC-cardPage-runnerJockey-name"]')

            if jockey is not None:
                jock = jockey.attrib['data-order-jockey']
                runners[horse_id]['jockey'] = jock if not claim else jock + f'({claim})'
                runners[horse_id]['jockey_id'] = int(jockey.attrib['href'].split('/')[3])
            else:
                runners[horse_id]['jockey'] = None
                runners[horse_id]['jockey_id'] = None

            try:
                runners[horse_id]['last_run'] = find(horse, 'div', 'RC-cardPage-runnerStats-lastRun')
            except TypeError:
                runners[horse_id]['last_run'] = None

            runners[horse_id]['form'] = find(horse, 'span', 'RC-cardPage-runnerForm')

            try:
                runners[horse_id]['trainer_rtf'] = find(horse, 'span', 'RC-cardPage-runnerTrainer-rtf')
            except TypeError:
                runners[horse_id]['trainer_rtf'] = None

        race['runners'] = [runner for runner in runners.values()]
        races[race['region']][race['course']][race['off_time']] = race

    return races


def valid_course(course):
    invalid = ['free to air', 'worldwide stakes', '(arab)']
    return all([x not in course for x in invalid])


def main():

    global date
    global date_ext

    print('UKHR 2022 RATINGS\n')
    print('Please change python script for future years\n\n')

    racecard_url = 'https://www.racingpost.com/racecards'

    session = requests.Session()

    system_time = datetime.datetime.now()
    tom = datetime.date.today() + datetime.timedelta(days=1)
    yest = datetime.date.today() + datetime.timedelta(days=-1)

    year = str(system_time.strftime("%Y"))
    month = str(system_time.strftime("%m"))
    day = str(system_time.strftime("%d"))
    
    date =  year + "-" + month + "-" + day

    tyear = str(tom.strftime("%Y"))
    tmonth = str(tom.strftime("%m"))
    tday = str(tom.strftime("%d"))
    
    tdate =  tyear + "-" + tmonth + "-" + tday

    yyear = str(yest.strftime("%Y"))
    ymonth = str(yest.strftime("%m"))
    yday = str(yest.strftime("%d"))
    
    ydate =  yyear + "-" + ymonth + "-" + yday
    
    while(True): #Top menu
        menu()
        choice = input()

        if choice == '1': #Scrape Race Cards
            while(True):
                sub_menu_1()
                sub_choice = input()

                if sub_choice == '1': #Tomorrow’s Cards
                    date_ext = "tomorrow"
                    date = tdate
                    #pass

                elif sub_choice == '2': #Today’s Cards
                    date_ext = ""
                    #pass

                elif sub_choice == '3': #Choose date for Cards
                    date = input('Please Provide Date (YYYY-MM-DD) :\n')
                    date_ext = date
                    #pass

                elif sub_choice == 'm': #Return to Main menu
                    break

                else:
                    print('\t\tInvalid choice\n\n')

  #              clear_odd_nr()
                get_meetings(session)
                
                break
        
        elif choice == '2': #Odds update
            while(True):
                sub_menu_2()
                sub_choice = input()

                if sub_choice == '1': #Tomorrow’s Cards
                    date_ext = "tomorrow"
                    #pass

                elif sub_choice == '2': #Today’s Cards
                    date_ext = ""
                    #pass

                elif sub_choice == 'm': #Return to Main menu
                    break

                else:
                    print('\tInvalid choice\n\n')

                df = pd.DataFrame(get_rtv_odds())
                save_excel(df, main_word='Racecards\RacecardsOdds', date=date)

                print("Odds File Saved\n\n")
                time.sleep(2) #pause for 1 sec
                break
                
        elif choice == '3': #Scrape Race Results
            while(True):
                sub_menu_3()
                sub_choice = input()

                if sub_choice == '1': #Today’s Results
                    date_ext = ""
                    
                    #pass

                elif sub_choice == '2': #Yesterday’s Results
                    date_ext = ydate
                    date = ydate
                    #pass

                elif sub_choice == '3': #Choose date for Results
                    date = input('Please Provide Date (YYYY-MM-DD) :\n')
                    date_ext = date
                    #pass

                elif sub_choice == 'm': #Return to Main menu
                    break

                else:
                    print('\t\tInvalid choice\n\n')
  #              get_results()
                break
        
        elif choice == '4': #Non Runners etc
            while(True):
                sub_menu_4()
                sub_choice = input()

                if sub_choice == '1': #Non Runners
                    df = pd.DataFrame(get_nr(date=date))
                    save_excel(df, main_word = r'Racecards\NonRunners', date=date)
                    #pass

                elif sub_choice == '2': #Travellers
                    df = pd.DataFrame(get_travel(date=date))
                    save_excel(df, main_word='Racecards\RC_Travellers', date=date)
                    #pass

                elif sub_choice == '3': #Aids
                    df = pd.DataFrame(get_aids(date=date))
                    save_excel(df, main_word='Racecards\RC_Aids', date=date)
                    #pass

                elif sub_choice == 'm': #Return to Main menu
                    break

                else:
                    print('\t\tInvalid choice\n\n')
                    #pass
                break
        
        elif choice == '5': #Going update
            while(True):
                sub_menu_5()
                sub_choice = input()

                if sub_choice == '1': #Tomorrow’s Cards
                    date_ext = "tomorrow"
                    #date = tdate
                    #pass

                elif sub_choice == '2': #Today’s Cards
                    date_ext = ""
                    #pass

                elif sub_choice == 'm': #Return to Main menu
                    break

                else:
                    print('\tInvalid choice\n\n')

                df = pd.DataFrame(get_going())
                save_excel(df, main_word='Racecards\RacecardsGng', date=date)
                break
        
        elif choice == '6': #Exit
            break

        else:
            print('\tInvalid choice\n\n')

    return


if __name__ == '__main__':
    main()
