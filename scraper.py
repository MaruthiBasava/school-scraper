from bs4 import BeautifulSoup
import requests
import json


class GroupJSONTemplate:

    @classmethod
    def return_group_template(cls, group_name, address, city, state, zipcode, country):
        return {
             "group": {
                "group_name": group_name,
                "school_code": 2
             },
             "group_visibility": {
                  "is_local": True,
                  "is_private": False,
                  "is_mature": False
             },
             "location": {
                "address": address,
                "city": city,
                "state": state,
                "zipcode": zipcode,
                "country": country
               }
             }


class SchoolDirectoryScrape:

    @classmethod
    def scrape(cls, url):
        result = requests.get(url)
        return BeautifulSoup(result.text, "html.parser")


def get_between(s, start, end):
        return s.split(start)[1].split(end)[0]


def associate(school):

    school_title = school.find('strong')

    if 'High School' in school_title.text:
        group_name = school_title.text.replace('High School', 'HS')
    else:
        return None

    inner_text = get_between(str(school), '</strong>', 'Phone:')

    if 'P.O.' in inner_text:
        return None

    big_block = inner_text.split('<br/>')

    if len(big_block) == 4:
        semi_blocks = big_block[2].split(',')
    else:
        return None

    if len(semi_blocks) == 2:
        micro_blocks = (semi_blocks[1].split())
        if len(micro_blocks) != 2:
            return None
    else:
        return None



    address = big_block[1]
    city = semi_blocks[0]
    state = micro_blocks[0]
    zipcode = micro_blocks[1]

    template = GroupJSONTemplate.return_group_template(group_name=group_name,
                                                       address=address,
                                                       city=city,
                                                       state=state,
                                                       zipcode=zipcode,
                                                       country='US')

    return template


def write_data_to_json(data):
    with open('schools.json', 'w') as outfile:
        json.dump(data, outfile)


big_array = []
states_long_text = ' '
states = ['alabama', 'alaska', 'arizona', 'arkansas', 'california', 'colorado', 'connecticut', 'delaware', 'florida', 'georgia', 'hawaii', 'idaho', 'illinois', 'indiana', 'iowa', 'kansas', 'kentucky', 'louisiana', 'maine', 'maryland', 'massachusetts', 'michigan', 'minnesota', 'mississippi', 'missouri', 'montana', 'nebraska', 'nevada', 'new-hampshire', 'new jersey', 'new mexico', 'new york', 'north carolina', 'north dakota', 'ohio', 'oklahoma', 'oregon', 'pennsylvania', 'rhode island', 'south carolina', 'south dakota', 'tennessee', 'texas', 'utah', 'vermont', 'virginia', 'washington', 'west virginia', 'wisconsin', 'wyoming']
further_pages = '-High-Schools-'
current_index = 1
base_url = 'http://www.directoryofschools.com/high-schools/'
ending = '.html'

home_label = 'Education Search for 1500 + Online Degrees, Colleges & Universities'


def is_not_home_page(soup):
    shit = soup.find('div', id='shortdesc')
    if shit is None:
        return None
    return home_label not in shit.text


for state in states:
    for current_index in range(1, 15):

        if current_index == 1:
            url = base_url + state.replace(' ', '-') + ending
            print(url)
            soup = SchoolDirectoryScrape.scrape(url)
            schools = soup.find_all('font')
            for school in schools:
                jsondat = associate(school)
                if jsondat is not None:
                    big_array.append(jsondat)
                else:
                    continue

            current_index += 1
            continue

        if current_index > 1:
            url = base_url + (state.title()).replace(' ', '-') + further_pages + str(current_index) + ending
            print(url)
            soup = SchoolDirectoryScrape.scrape(url)

            bool = is_not_home_page(soup)

            if bool is None:
                print("NONE FOUND")
                continue

            if is_not_home_page(soup):
                schools = soup.find_all('font')
                for school in schools:
                    jsondat = associate(school)
                    if jsondat is not None:
                        big_array.append(jsondat)
                    else:
                        continue

                current_index += 1
            else:
                print('')
            continue


write_data_to_json(big_array)
