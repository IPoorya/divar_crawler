import json, os
from modules.last_post_date import last_post_date as date
from modules.crawler import Crawler

def load_json(state=False):
    if not state:
        with open('modules/cities.json') as file:
            return json.load(file)
    if state['mode'] == 'extract-tokens':
        with open(f"states/{state['category']}-{state['mode']}-state.json", "r") as file:
            return json.load(file)
    elif state['mode'] == 'extract-data':
        with open(f"states/{state['category']}-{state['mode']}-state.json", "r") as file:
            return json.load(file)


if __name__ == '__main__':

    my_crawler = Crawler()

    # loads supported cities from cities.json
    try:
        cities = load_json()
    except Exception as e:
        print(e)
        exit

    state = {}
    print('-- DIVAR CRAWLER --')
    print('')


    # selecting crawling mode
    while True:
        print('select a mode number:')
        print('1. extract tokens')
        print('2. extract data')
        print('press enter to exit')
        ans = input()
        if ans == '1':
            state['mode'] = 'extract-tokens'
            break

        elif ans == '2':
            state['mode'] = 'extract-data'
            break

        elif ans == '':
            print('exiting...')
            exit()
        else:
            print('invalid input, try again')
            print('- - - - - - - - - - - -')
            continue

    print('')
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


    print('')
    # selecting duration
    while state['mode'] == 'extract-tokens':
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
            state['duration'] = ans
            break

        elif ans == '':
            print('exiting...')
            exit()
        else:
            print('invalid input, try again')
            print('- - - - - - - - - - - -')
            continue


    print('')
    # extract tokens
    if state['mode'] == 'extract-tokens' and state['duration'] == '0': # continue last process
        if os.path.isfile(f"states/{state['category']}-{state['mode']}-state.json"):
            last_state = load_json(state)[-1]
            state = {
                "category": last_state['category'],
                "mode": last_state['mode'],
                "page": last_state['page'], 
                "last_post_date": last_state['last_post_date'], 
                "city": last_state['city'], 
                "request_count": last_state['request_count'], 
                "duration": last_state['duration'],
                "status": last_state['status']
                }
            my_crawler.extract_tokens(state)
        else:
            print("process didn't found")

        exit()

    elif state['mode'] == 'extract-tokens': # selected a new duration

        print('')
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
    if state['mode'] == 'extract-tokens' and state['duration'] in persian_number.keys(): 
        state = {
                "category": state['category'],
                "mode": state['mode'],
                "page": 0, 
                "last_post_date": date(), 
                "city": state['cities'], 
                "request_count": 50, 
                "duration": state['duration'],
                "status": True
                }
        
        my_crawler.extract_tokens(st=state)

    elif state['mode'] == 'extract-data':
        if os.path.isfile(f"states/{state['category']}-{state['mode']}-state.json"):
                last_state = load_json(state)[-1]
                state = {
                    "mode": last_state['mode'],
                    "category": last_state['category'],
                    "file": last_state['file'],
                    "window": last_state['window'], 
                    "index": last_state['index']
                    }
        else:
            state = {
                "mode": state['mode'],
                "category": state['category'],
                "file": '', # next file to process 
                "window": 0, 
                "index": 0
                }

    
        my_crawler.extract_data(st=state)

    print('END!')