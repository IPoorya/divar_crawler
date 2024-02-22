import json, os
from modules.last_post_date import last_post_date as date
from modules.crawler import Crawler

def load_json(state=False):
    if not state:
        with open('modules/cities.json') as file:
            return json.load(file)
    if state['category'] == 'extract tokens':
        with open(f"states/{state['mode']}-state.json", "r") as file:
            return file
    elif state['category'] == 'extract data':
        with open(f"states/{state['mode']}-state.json", "r") as file:
            return file


if __name__ == '__main__':

    # loads supported cities from cities.json
    try:
        cities = load_json()
    except Exception as e:
        print(e)
        exit

    state = {}
    print('-- DIVAR CRAWLER v1.0 --')
    print('')


    # selecting crawling mode
    while True:
        print('select a mode number:')
        print('1. extract tokens')
        print('2. extract data')
        print('press enter to exit')
        ans = input()
        if ans == '1':
            state['mode'] = 'extract tokens'
            break

        elif ans == '2':
            state['mode'] = 'extract data'
            break

        elif ans == '':
            print('exiting...')
            exit()
        else:
            print('invalid input, try again')
            print('- - - - - - - - - - - -')
            continue


    # selecting duration
    while state['mode'] == 'extract tokens':
        print('select a duration')
        print('continue last process or extract tokens until ....... before')
        print('0. continue last process')
        print('1. 1 week')
        print('2. 2 weeks')
        print('3. 3 weeks')
        print('4. 4 weeks')
        print('5. 5 weeks')
        print('press enter to exit')
        ans = input()
        persian_number = {
            '1': '۱',
            '2': '۲',
            '3': '۳',
            '4': '۴',
            '5': '۵',
        }

        if ans == '0':       # continue last process
            state['duration'] = '0'
            break

        elif ans == '1' or ans == '2' or ans == '3' or ans == '4' or ans == '5':
            state['duration'] = persian_number[ans]
            break

        elif ans == '':
            print('exiting...')
            exit()
        else:
            print('invalid input, try again')
            print('- - - - - - - - - - - -')
            continue


    # extract tokens
    if state['mode'] == 'extract tokens' and state['duration'] == '0': # continue last process
        if os.path.isfile(f"states/{state['mode']}-state.json"):
            last_state = load_json(state)[-1]
            state = {
                "id": last_state['id'],
                "category": last_state['category'],
                "page": last_state['page'], 
                "last_post_date": last_state['last_post_date'], 
                "city": last_state[cities], 
                "request_count": 50, 
                "duration": last_state['duration'],
                "status": True
                }
            Crawler.extract_tokens(state)
        else:
            print("process didn't found")

        exit()

    elif state['mode'] == 'extract tokens': # selected a new duration

        # selecting category
        while True:
            print('select a category number:')
            print('1. apartment sell')
            print('2. apartment rent')
            print('3. house and villa sell')
            print('4. house and villa rent')
            print('press enter to exit')
            ans = input()
            if ans == '1':
                state['category'] = 'apartment-sell'
                break

            elif ans == '2':
                state['category'] = 'apartment-rent'
                break

            elif ans == '3':
                state['category'] = 'house-villa-sell'
                break

            elif ans == '4':
                state['category'] = 'house-villa-rent'
                break

            elif ans == '':
                print('exiting...')
                exit()
            else:
                print('invalid input, try again')
                print('- - - - - - - - - - - -')
                continue

        # selecting cities
        while True:
            choices = {
                "1": "tehran",
                "2": "karaj",
                "3": "shiraz",
                "4": "isfahan",
                "5": "rasht",
                "6": "ahvaz",
                "7": "mashahd",
                "8": "qom"
            }

            print('select one or more city numbers separated by space:')
            for key, value in choices.items():
                print(f"{key}. {value}")
            print('press enter to exit')

            ans = input()
            if ans == '':
                print('exiting...')
                exit()
            ans = ans.split()
            selected_cities = []
            for number in ans:
                if choices[number] not in cities.keys():
                    selected_cities.clear()
                    print('invalid input, try again')
                    print('- - - - - - - - - - - -')
                    continue
                selected_cities.append(cities[choices[number]])
            
            state["cities"] = selected_cities
            break

    
    # new process for extracting tokens
    if state['mode'] == 'extract tokens' and state['duration'] in persian_number.values(): 
        state = {
                "category": state['category'],
                "page": 0, 
                "last_post_date": date(), 
                "city": state['cities'], 
                "request_count": 50, 
                "duration": state['duration'],
                "status": True
                }
        

    elif state['mode'] == 'extract data':
        if os.path.isfile(f"states/{state['mode']}-state.json"):
                last_state = load_json(state)[-1]
                state = {
                    "category": last_state['category'],
                    "file": last_state['file'],
                    "window": last_state['window'], 
                    "city": last_state['cities'],
                    "p": last_state['p']
                    }
        else:
            state = {
                "category": '',
                # "category": state['category'],
                "file": '', 
                "window": 0, 
                "city": '',
                # "city": state['cities'],
                "p": 0
                }

    
    Crawler.extract_data(state)