#!/usr/bin/env python3
import os
import requests
import sys

from collections import defaultdict
from datetime import datetime, timedelta
from lxml import html
from orjson import loads, dumps
from re import search

from utils.going import get_surface
from utils.header import RandomHeader
from utils.lxml_funcs import find
from utils.region import get_region

import time
from bs4 import BeautifulSoup
import pandas as pd
import shutil
import datetime
from typing import Text

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
    print('\t\t1) Tomorrow Cards\n')
    print('\t\t2) Today Cards\n')
    print('\t\t3) Choose date\n')
    print('\t\tm) Main menu')
    print()
    return

def sub_menu_2(): #Scrape Odds      this is copied from RC_menu_V03_RTV.py
    os.system('cls')
    print('\t\t1) \n')  #Tomorrow’s Odds\n')
    print('\t\t2) Today Odds\n')
    print('\t\tm) Main menu')
    print()
    return

def sub_menu_3(): #Scrape Race Results      this is copied from RC_menu_V03_RTV.py
    os.system('cls')
    print('\t\t1) Today Results\n')
    print('\t\t2) Yesterday Results\n')
    print('\t\t3) Choose date\n')
    print('\t\tm) Main menu')
    print()
    return

def sub_menu_4(): #Non Runners, Aids etc.       this is copied from RC_menu_V03_RTV.py
    os.system('cls')
    print('\t\t1) Today Non Runners\n')
    print('\t\t2) \n') # Travellers\n')
    print('\t\t3) \n') # Aids\n')
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

def update_odds():
    df_racecard = pd.read_excel(file_loc + r'\racecards\Racecards.xlsx')
    del df_racecard['odds']
    df_odds = pd.read_excel(file_loc + r'\racecards\RacecardsOdds.xlsx')

    df_racecard = df_racecard.merge(df_odds, on = ['horse'], how='left')
    save_excel(df_racecard, main_word = file_loc + r'\racecards\Racecards', date=date)

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

def make_old_df(df_race):
    df_old = df_race[['course', 'date', 'going', 'off_time', 'race_name', 'race_class', 'age_band', 'prize',
                        'field_size', 'distance', 'number', 'draw', 'form', 'horse', 'age', 'tips', 'ofr',
                        'jockey', 'trainer', 'claim', 'trainer_rtf', 'ts', 'rpr', 'last_run', 'headgear',
                        'lbs', 'cd', 'odds']].copy()
    #df_old = df_race.copy()   # Create copy of DataFrame for use with old python files etc
    df_old = df_old.rename(columns = {'date' : 'Date',  
                                    'course' : 'Course', 
                                    'off_time' : 'Time', 
                                    'race_name' : 'RaceDesc', 
                                    'distance' : 'Dist', 
                                    'race_class' : 'Class', 
                                    'age_band' : 'AgeLimit',  
                                    'prize' : 'Value', 
                                    'field_size' : 'Run', 
                                    'going' : 'Going', 
                                    'horse' : 'Horse',
                                    'age' : 'Age', 
                                    'number' : 'No', 
                                    'draw' : 'Draw', 
                                    'last_run' : 'Days', 
                                    'form' : 'Form', 
                                    'cd' : 'CDB', 
                                    'headgear' : 'Aid', 
                                    'lbs' : 'WtLbs', 
                                    'tips' : 'Weight',
                                    'claim' : 'Allow', 
                                    'ofr' : 'OR', 
                                    'rpr' : 'RPR', 
                                    'ts' : 'TS', 
                                    'jockey' : 'Jockey', 
                                    'trainer' : 'Trainer', 
                                    'trainer_rtf' : 'RTF',
                                    'odds' : 'Odds'
                                    })

    save_excel(df_old, main_word = r'C:\Users\chris\Documents\UKHR\Python\Racecards\RacecardsOld', date=date)
    #save_excel_date(df_old, main_word = r'C:\Users\chris\Documents\UKHR\Python\Racecards\RacecardsOld', date=date)
      
    return                                    


def get_nr(date=None):
    
    url = f'https://www.sportinglife.com/racing/non-runners'
    resp = requests.get(url,headers=random_header.header())

    soup = BeautifulSoup(resp.text,'html.parser')

    nr_horse = soup.find_all('span', class_='NonRunners__Horse-o6sh1j-4 cSiKAk')
    
    rows = []

    for nr in nr_horse:
        horsename = get_text(nr).split(maxsplit=1)[1]
        horsename = clean_name(horsename)
        #horse = clean_name(horse)
        #horsename = nr.split(maxsplit=1)[1]
        item = {'horse':horsename}
        rows.append(item)
        continue

    df = pd.DataFrame(rows)
    #df['horse'] = clean_name(df['horse'])
    
    #save_excel(df, main_word = r'Racecards\NonRunners', date=date)

    return df


def get_sl_odds(ext):
    odd_list = []
    url =  'https://www.sportinglife.com/racing/abc-guide/'  + ext
    #   url = 'https://www.skysports.com/racing/abc-entries-guide/' + ext
    res = requests.get(url, headers=random_header.header())
    soup = BeautifulSoup(res.content, "html.parser")
    rows = soup.find_all('tr')[1:]
    
    for row in rows:
        odd_dict = {}
        odd_dict['horse'] = get_text(row.td).split('(')[0].strip()
        odd_dict['horse'] = clean_name(odd_dict['horse'])
        
        odd_dict['odds'] = get_text(row.find_all('th')[0])

        odd_list.append(odd_dict)

        #print(odd_dict)
        
    return odd_list


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


def save_excel_date(df, main_word, date=None):
    print('Saving data in excel files')

    try:
        df.to_excel(f'{main_word} {date}.xlsx', index = False)
    except:
        print(f'{main_word} {date}.xlsx saving failed. You may need to remove or close the existing {main_word} {date}.xlsx')
    
    try:
        df.to_excel(f'{main_word}.xlsx', index = False)
    except:
        print(f'{main_word}.xlsx saving failed. You may need to remove or close the existing {main_word}.xlsx')
    
    print(main_word, ": ",'Saved')
    time.sleep(3)
    menu()
    return


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


def distance_to_yards(dist):
    #dist = distance.strip().replace('¼', '.25').replace('½', '.5').replace('¾', '.75')
    yards = 0
    mf = 0
    flgs = 0
    mls = 0
    if 'm' in dist:
        if len(dist) > 2:
            if 'y' in dist:
                dist = dist[:-1]
                if 'f' in dist:
                    yards = float(dist.split('f')[1].strip('f'))
                    mf = dist.split('f')[0].strip('f')
                    flgs = float(mf.split('m')[1].strip('m'))
                    mls = float(mf.split('m')[0].strip('m'))
                else:
                    yards = float(dist.split('m')[1].strip('m'))
                    mls = float(dist.split('m')[0].strip('m'))
            else:
                dist = dist[:-1]
                flgs = float(dist.split('m')[1].strip('m'))
                mls = float(dist.split('m')[0].strip('m'))
        else:
            mls = int(dist.split('m')[0]) * 8

    else:
        if 'y' in dist:
            dist = dist[:-1]
            yards = float(dist.split('f')[1].strip('f'))
            flgs = float(dist.split('f')[0].strip('f'))
        else:
            flgs = float(dist.strip('f'))

    yards = (mls * 8 + flgs) * 220 + yards
    return float(yards)


def get_going_info(session, date):
    r = session.get(f'https://www.racingpost.com/non-runners/{date}', headers=random_header.header())
    doc = html.fromstring(r.content.decode())

    json_str = doc.xpath('//body/script')[0].text.replace('var __PRELOADED_STATE__ = ', '').strip().strip(';')

    going_info = defaultdict(dict)

    for course in loads(json_str):
        going, rail_movements = parse_going(course['going'])
        course_id = int(course['raceCardsCourseMeetingsUrl'].split('/')[2])
        going_info[course_id]['course'] = course['courseName']
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


def get_race_urls(session, racecard_url):
    r = session.get(racecard_url, headers=random_header.header())
    doc = html.fromstring(r.content)

    race_urls = []

    for meeting in doc.xpath("//section[@data-accordion-row]"):
        course = meeting.xpath(".//span[contains(@class, 'RC-accordion__courseName')]")[0]
        if valid_course(course.text_content().strip().lower()):
            for race in meeting.xpath(".//a[@class='RC-meetingItem__link js-navigate-url']"):
                race_urls.append('https://www.racingpost.com' + race.attrib['href'])

    return sorted(list(set(race_urls)))


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
                runner['distance_f'] = q['distanceFurlong']
                runner['distance_y'] = q['distanceYard']
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

    racecards_list = []

    for url in race_urls:
        r = session.get(url, headers=random_header.header())
        doc = html.fromstring(r.content)
    #    df_doc = pd.DataFrame(r)
    #    save_excel_date(df_doc, main_word=r'C:\Users\chris\Documents\UKHR\PythonSand\racecards\RC_doc', date=date)
                
        race = {}

        url_split = url.split('/')

        race['course_id'] = int(url_split[4])
        race['region'] = get_region(str(race['course_id']))

        if (race['region'] != 'GB' and race['region'] != 'IRE'):
            continue

        race['race_id'] = int(url_split[7])
        race['date'] = url_split[6]
        
        race['course'] = find(doc, 'h1', 'RC-courseHeader__name')

        race['off_time'] = find(doc, 'span', 'RC-courseHeader__time')
        hrs, mnt = race['off_time'].split(':')  # convert time to 24hr
        if (int(hrs) == 12 or int(hrs) == 11):
            hrs = str(int(hrs) - 12)
        race['off_time'] = f'{int(hrs)+12}:{mnt}'

        race['race_name'] = find(doc, 'span', 'RC-header__raceInstanceTitle')

        # create a Handicap/Maiden/Amateur/Novice column for use with lookups etc
        race['race_name_up'] = race['race_name'].upper()
        if 'HANDICAP' in race['race_name_up']: 
            race['hc'] = "HCap"
        else:
            race['hc'] = None

        if 'MAIDEN' in race['race_name_up']: 
            race['maid'] = "Mdn"
        else:
            race['maid'] = None

        if 'AMATEUR' in race['race_name_up']: 
            race['am'] = "Am"
        else:
            race['am'] = None

        if 'NOVICE' in race['race_name_up']: 
            race['nov'] = "Nov"
        else:
            race['nov'] = None

        race['distance_round'] = find(doc, 'strong', 'RC-header__raceDistanceRound')
        race['distance'] = find(doc, 'span', 'RC-header__raceDistance')
        race['distance'] = race['distance_round'] if not race['distance'] else race['distance'].strip('()')
        race['distance_f'] = distance_to_furlongs(race['distance_round'])
        race['yards'] = distance_to_yards(race['distance'])
        
        race['pattern'] = get_pattern(race['race_name'].lower())
        race['race_class'] = find(doc, 'span', 'RC-header__raceClass')
        race['race_class'] = race['race_class'].strip('()') if race['race_class'] else '0'
        race['type'] = get_race_type(doc, race['race_name'].lower(), race['distance_f'])

        if not race['race_class']:
            if race['pattern']:
                race['race_class'] = was = 'Class 1'

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
        if (('£' in race['prize']) | ('€' in race['prize'])) :
            race['prize'] = race['prize'][1:].strip()
        else:
            None

        race['prize'] = race['prize'].replace(',', '')

        if ('lass' in race['race_class']) :
            race['race_class'] = race['race_class'][6:].strip()
        else:
            None
        
        if int(race['race_class']) == 0:   # assign a Class to IRE based on prize value if no class
            if int(race['prize']) > 13000:
                race['race_class'] = "1"
            elif int(race['prize']) > 10000:
                race['race_class'] = "2"
            elif int(race['prize']) > 8000:
                race['race_class'] = "3"
            elif int(race['prize']) > 5000:
                race['race_class'] = "4"
            elif int(race['prize']) > 2000:
                race['race_class'] = "5"
            else:
                race['race_class'] = "6"

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
                runners[horse_id]['trainer'] = clean_name(runners[horse_id]['trainer'])

            runners[horse_id]['number'] = int(find(horse, 'span', 'RC-cardPage-runnerNumber-no', attrib='data-order-no'))

            try:
                runners[horse_id]['draw'] = int(find(horse, 'span', 'RC-cardPage-runnerNumber-draw', attrib='data-order-draw'))
            except ValueError:
                runners[horse_id]['draw'] = None

            runners[horse_id]['headgear'] = find(horse, 'span', 'RC-cardPage-runnerHeadGear')
            runners[horse_id]['headgear_first'] = find(horse, 'span', 'RC-cardPage-runnerHeadGear-first')

            try:
                runners[horse_id]['odds'] = find('div', class_='RC-runnerRowPriceWrapper').find('a').text.strip()
                
            except TypeError:
                runners[horse_id]['odds'] = None

            try:
                runners[horse_id]['odds'] = find(horse, 'div', 'data-diffusion-next-price')
            except TypeError:
                runners[horse_id]['odds'] = None

            try: 
                runners[horse_id]['tips'] = find(horse, 'div', 'RC-cardPage-runnerStats-tips').split(' ')[0].strip()
            except TypeError:
                runners[horse_id]['tips'] = None

            try:
                runners[horse_id]['cd'] = find(horse, 'div', 'RC-cardPage-runnerStats-cd')
            except TypeError:
                runners[horse_id]['cd'] = None

            try:
                runners[horse_id]['d'] = find(horse, 'div', 'RC-cardPage-runnerStats-d')
            except TypeError:
                runners[horse_id]['d'] = None

            try:
                runners[horse_id]['bf'] = find(horse, 'div', 'RC-cardPage-runnerStats-bf')
            except TypeError:
                runners[horse_id]['bf'] = None

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
            jockey = find(horse, 'a', 'RC-cardPage-runnerJockey-name', attrib='data-order-jockey')

            if jockey:
                runners[horse_id]['jockey'] = jockey # no need to add claim here... if not claim else jockey + f'({claim})'
            else:
                runners[horse_id]['jockey'] = None

            runners[horse_id]['jockey'] = clean_name(runners[horse_id]['jockey'])

            try:
                runners[horse_id]['last_run'] = find(horse, 'div', 'RC-cardPage-runnerStats-lastRun')
            except TypeError:
                runners[horse_id]['last_run'] = None

            try: 
                runners[horse_id]['last_run'] = runners[horse_id]['last_run'].split('(')[0].strip()
            except TypeError:
                runners[horse_id]['last_run'] = runners[horse_id]['last_run']

            runners[horse_id]['form'] = find(horse, 'span', 'RC-cardPage-runnerForm')

            try:
                runners[horse_id]['trainer_rtf'] = find(horse, 'span', 'RC-cardPage-runnerTrainer-rtf')
            except TypeError:
                runners[horse_id]['trainer_rtf'] = None

            race['runners'] = [runner for runner in runners.values()]
            races[race['region']][race['course']][race['off_time']] = race

            racecards_list.append({'url': url, 
                'race_id' : race['race_id'], 
                'date' : race['date'], 
                'course_id' : race['course_id'], 
                'course' : race['course'], 
                'region' : race['region'], 
                'off_time' : race['off_time'], 
                'race_name' : race['race_name'], 
                'distance_f' : race['distance_f'], 
                'distance' : race['distance'],
                'yards' : race['yards'], 
                'surface' : race['surface'], 
                'type' : race['type'], 
                'race_class' : race['race_class'], 
                'hc' : race['hc'],
                'maid' : race['maid'],
                'am' : race['am'],
                'nov' : race['nov'],
                'age_band' : race['age_band'], 
                'rating_band' : race['rating_band'], 
                'prize' : race['prize'], 
                'field_size' : race['field_size'], 
                'going' : race['going'], 
                'weather' : race['weather'], 
                'stalls' : race['stalls'], 
                'horse_id' : horse_id, 
                'horse' : runners[horse_id]['name'],
                'sire' : runners[horse_id]['sire'], 
                'dam' : runners[horse_id]['dam'], 
                'age' : runners[horse_id]['age'], 
                'sex_colour' : runners[horse_id]['colour'], 
                'sex_code' : runners[horse_id]['sex_code'], 
                'number' : runners[horse_id]['number'], 
                'draw' : runners[horse_id]['draw'], 
                'last_run' : runners[horse_id]['last_run'], 
                'form' : runners[horse_id]['form'], 
                'd' : runners[horse_id]['d'], 
                'cd' : runners[horse_id]['cd'], 
                'bf' : runners[horse_id]['bf'], 
                'tips' : runners[horse_id]['tips'],
                'headgear' : runners[horse_id]['headgear'], 
                'headgear_first' : runners[horse_id]['headgear_first'], 
                'lbs' : runners[horse_id]['lbs'], 
                'claim' : claim, 
                'ofr' : runners[horse_id]['ofr'], 
                'rpr' : runners[horse_id]['rpr'], 
                'ts' : runners[horse_id]['ts'], 
                'jockey' : runners[horse_id]['jockey'], 
                'trainer' : runners[horse_id]['trainer'], 
                'trainer_rtf' : runners[horse_id]['trainer_rtf']
                })
        
    return racecards_list


def valid_course(course):
    invalid = ['free to air', 'worldwide stakes', '(arab)']
    return all([x not in course for x in invalid])


def main():
    global date
    global date_ext
    global race_cnt
    global file_loc
    file_loc = r'C:\Users\chris\Documents\UKHR\Python\git'
    
    print('UKHR 2022 RATINGS\n')
    print('Please change python script for future years\n\n')

    racecard_url = 'https://www.racingpost.com/racecards'

    session = requests.Session()        # Requests.session object allows you to persist specific parameters across requests to the same site.

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
                    
                elif sub_choice == '2': #Today’s Cards
                    date_ext = ""
                    df_nr = pd.DataFrame(get_nr(date=date))                                        
                    save_excel(df_nr, main_word = file_loc + r'\racecards\RacecardsNR', date=date)
                    
                elif sub_choice == '3': #Choose date for Cards
                    date = input('Please Provide Date (YYYY-MM-DD):\n')
                    date_ext = date
                    
                elif sub_choice == 'm': #Return to Main menu
                    break

                else:
                    print('\t\tInvalid choice\n\n')

  #              clear_odd_nr()
                odds_date = date_ext
                racecard_url = f'https://www.racingpost.com/racecards/{date_ext}'
                #racecard_url = 'https://www.racingpost.com/racecards'

                race_urls = get_race_urls(session, racecard_url)
                races = parse_races(session, race_urls, date)

                df_race = pd.DataFrame(races)
                df_race = df_race[df_race.jockey != "Non-Runner"] #remove rows where jockey = NR

                #race_cnt = df_race[['course'],['off_time']].nunique()                
                race_cnt = len(set(zip(df_race['course'],df_race['off_time'])))
                
                if ((odds_date == '')|(odds_date == 'tomorrow')):
                    df_odd = pd.DataFrame(get_sl_odds(odds_date))
                    df_odd.set_index('horse')
                    df_race = df_race.merge(df_odd, on = ['horse'], how='left')

                else:
                    print('Odds were not scraped \nSelect td (for today) or tm (for tomorrow) odds scraping')
                                                
                #df_race = df_race[df_race.No != "NR"] #remove rows where No = NR
                #df_race.drop_duplicates(subset="Horse", keep="first", inplace=True)
                #df_race.set_index('Horse')

                # if not os.path.exists('../racecards'):
                #     os.makedirs(f'../racecards')

                # with open(f'../racecards/{date}.json', 'w', encoding='utf-8') as f:
                #     f.write(dumps(races).decode('utf-8'))
                make_old_df(df_race)
                save_excel(df_race, main_word = file_loc + r'\racecards\Racecards', date=date)
                
                #save_excel(df_race, main_word=r'C:\Users\chris\Documents\UKHR\PythonSand\racecards\Racecards', date=date)
                # C:\Users\chris\Documents\UKHR\PythonSand\racecards
                
                break
        
        elif choice == '2': #Odds update
            while(True):
                sub_menu_2()
                sub_choice = input()

                if sub_choice == '1': #Tomorrow’s Cards
                    print('\tInvalid choice - Odds update only available on Raceday\n\n')                    
                    date_ext = "tomorrow"
                    #break
                    
                elif sub_choice == '2': #Today’s Cards
                    date_ext = ""
                    
                elif sub_choice == 'm': #Return to Main menu
                    break

                else:
                    print('\tInvalid choice\n\n')

                df_nr = pd.DataFrame(get_nr(date=date))                                    
                df_nr.drop_duplicates(subset="horse", keep="first", inplace=True)
                save_excel(df_nr, main_word = file_loc + r'\racecards\RacecardsNR', date=date)
                
                df_odds = pd.DataFrame(get_sl_odds(date_ext))                
                df_odds.drop_duplicates(subset="horse", keep="first", inplace=True)
                save_excel(df_odds, main_word = file_loc + r'\racecards\RacecardsOdds', date=date)
                #save_excel(df, main_word=r'C:\Users\chris\Documents\UKHR\PythonSand\racecards\RacecardsOdds', date=date)
                
                df_racecard = pd.read_excel(file_loc + r'\racecards\Racecards.xlsx')
                del df_racecard['odds']
                df_racecard = df_racecard.merge(df_odds, on = ['horse'], how='left')

                make_old_df(df_race)
                save_excel(df_racecard, main_word = file_loc + r'\racecards\Racecards', date=date)

                print("Odds File Saved and Racecard updated\n\n")
                time.sleep(0.5) #pause for x sec
                break
                
        elif choice == '3': #Scrape Race Results
            while(True):
                sub_menu_3()
                sub_choice = input()

                if sub_choice == '1': #Today’s Results
                    date_ext = ""
                                        
                elif sub_choice == '2': #Yesterday’s Results
                    date_ext = ydate
                    date = ydate
                    
                elif sub_choice == '3': #Choose date for Results
                    date = input('Please Provide Date (YYYY-MM-DD) :\n')
                    date_ext = date                   

                elif sub_choice == 'm': #Return to Main menu
                    break

                else:
                    print('\t\tInvalid choice\n\n')
  #              get_results()
                break
        
        elif choice == '4': #Non Runners etc
            while(True):
                #sub_menu_4()
                sub_choice = '1'    #input()

                if sub_choice == '1': #Non Runners
                    df = pd.DataFrame(get_nr(date=date))                                                          
                    save_excel(df, main_word = file_loc + r'\racecards\RacecardsNR', date=date)
                    
                    df = pd.DataFrame(get_sl_odds(date_ext))                    
                    save_excel(df, main_word = file_loc + r'\racecards\RacecardsOdds', date=date)
                    
                elif sub_choice == '2': #Travellers
                    print('\t\tNot Used\n\n')
                    time.sleep(2) #pause for x sec
                    continue
                    df = pd.DataFrame(get_travel(date=date))
                    #save_excel(df, main_word='Racecards\RC_Travellers', date=date)
                    save_excel(df, main_word=r'C:\Users\chris\Documents\UKHR\PythonSand\racecards\RacecardsTrvl', date=date)
                    
                elif sub_choice == '3': #Aids
                    print('\t\tNot Used\n\n')
                    time.sleep(2) #pause for x sec
                    continue
                    df = pd.DataFrame(get_aids(date=date))
                    #save_excel(df, main_word='Racecards\RC_Aids', date=date)
                    save_excel(df, main_word=r'C:\Users\chris\Documents\UKHR\PythonSand\racecards\RacecardsAids', date=date)
                    
                elif sub_choice == 'm': #Return to Main menu
                    break

                else:
                    print('\t\tInvalid choice\n\n')
                    
                break
        
        elif choice == '5': #Going update
            print('\t\tNot Used\n\n')
            time.sleep(2) #pause for x sec
            continue
            while(True):
                sub_menu_5()
                sub_choice = input()

                if sub_choice == '1': #Tomorrow’s Cards
                    date_ext = "tomorrow"
                    #date = tdate
                    
                elif sub_choice == '2': #Today’s Cards
                    date_ext = ""
                    
                elif sub_choice == 'm': #Return to Main menu
                    break

                else:
                    print('\tInvalid choice\n\n')

                df = pd.DataFrame(get_going())
                #save_excel(df, main_word='Racecards\RacecardsGng', date=date)
                save_excel(df, main_word=r'C:\Users\chris\Documents\UKHR\PythonSand\racecards\RacecardsGoing', date=date)
                break
        
        elif choice == '6': #Exit
            break

        else:
            print('\tInvalid choice\n\n')

    return



    if not os.path.exists('../racecards'):
        os.makedirs(f'../racecards')

    with open(f'../racecards/{date}.json', 'w', encoding='utf-8') as f:
        f.write(dumps(races).decode('utf-8'))


if __name__ == '__main__':
    main()
