import os, json, time, csv
from modules.extract_tokens import extract_tokens as phase_1
from modules.extract_data import extract_data as phase_2
from multiprocessing import Process, Manager


class Crawler:

    @classmethod
    def __init__(self):
        self.tokens = []
        self.records = []

    @classmethod
    def extract_tokens(self, st):

        def save_tokens(tokens):
            # Write the data back to the file
            name = 0
            if state['page'] < state['request_count']:
                name = "0"
            else:
                name = str(state['page'] - state['request_count'])

            with open(f"tokens/{state['category']}/{name}-{state['page']}.json", "w") as file:
                json.dump(tokens, file)

        def save_state(state):
            data = []

            # If the file exists, load the existing data
            if os.path.isfile(f"states/{state['category']}-state.json"):
                with open(f"states/{state['category']}-state.json", "r") as file:
                    data = json.load(file)

            # Add the new state to the data
            data.append(dict(state))

            # Write the data back to the file
            with open(f"states/{state['category']}-state.json", "w") as file:
                json.dump(data, file)

        manager = Manager()
        state = manager.dict()

        state["category"] = st["category"]
        state["mode"] = st["mode"]
        state["page"] = st["page"]
        state["last_post_date"] = st["last_post_date"]
        state["city"] = st["city"]
        state["request_count"] = st["request_count"]
        state["duration"] = st["duration"]
        state["status"] = st["status"]

        while state["status"]:
            scraped_tokens = manager.list()
            print(state["last_post_date"])
            process = Process(target=phase_1, args=(state, scraped_tokens))
            process.start()

            process.join(timeout=(state["request_count"]*10) + 60)
            if process.is_alive():
                print('process got stuck!')
                process.kill()
                time.sleep(30)
                continue
            state['page'] += state['request_count']
            print(state["last_post_date"])
            print(scraped_tokens[-1])
            self.tokens.extend(scraped_tokens)
            save_tokens(self.tokens)
            save_state(state)
            self.tokens.clear()


    @classmethod
    def extract_data(self, st):

        def save_to_csv(data):
            csv_file = f"{st['category']}/records.csv"
            file_exists = os.path.isfile(csv_file)

            # Writing to csv file
            with open(csv_file, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames = data[0].keys())
                # If the file didn't exist before we opened it, write a header
                if not file_exists:
                    writer.writeheader()
                # Write the data rows
                writer.writerows(data)


        def save_state(state):
            data = []

            # If the file exists, load the existing data
            if os.path.isfile(f"{state['mode']}-state.json"):
                with open(f"{state['mode']}-state.json") as file:
                    data = json.load(file)

            # Add the new state to the data
            data.append(dict(state))

            # Write the data back to the file
            with open(f"{state['mode']}-state.json", "w") as file:
                json.dump(data, file)


        manager = Manager()
        state = manager.dict()
        state['category'] = st['category']
        state['file'] = st['file']
        state['window'] = st['window']
        state['city'] = st['city']
        state['p'] = st['p']

        # request count on one selenium browser,
        # when its reached, we would open another browser
        # to not reach the request limit
        window_range = 70 


        json_files = [f for f in os.listdir(f'tokens/{state["mdoe"]}') if f.endswith('.json')]
        if not json_files:
            print('not found: json file')
            exit()

        # loading last processing file
        json_file = json_files.pop(0)
        while state['file'] and json_file != state['file']:
            json_file = json_files.pop(0)

        # Loop through the files and load the data
        while True:            

            state['file'] = json_file
            with open(os.path.join(f'tokens/{st["mode"]}', json_file), 'r') as f:
                # Load the data from the file and append it to the list
                all_tokens = json.load(f) # all the tokens in a json file
                wait_time = len(all_tokens)

            while True: # loop through tokens
                tokens = [] # selected tokens to scrape in a process
                all = [] # all the tokens sliced for window number to the end
                print('window: ' + str(state["window"]))
                if state['window'] != 0:
                    all = all_tokens[state["window"]:]
                    if not all:
                        state['window'] = 0
                        break
                else:
                    all = all_tokens.copy()

                for i in range(len(all)):
                    tokens.append(all[i])
                    if len(tokens) >= window_range:
                        break

                scraped_data = manager.list()
                print(json_file)
                process = Process(target=phase_2, args=(state, tokens, scraped_data))
                process.start()

                process.join(timeout=(wait_time*10) + 60)
                if process.is_alive():
                    print('process got stuck!')
                    process.kill()
                    time.sleep(30)
                    continue
                else:
                    state['window'] += state['p']
                    save_to_csv(scraped_data)
                    save_state(state)
                    os.remove(f'tokens/{state["category"]}/{state["file"]}')

            if not json_files:
                break
            json_file = json_files.pop(0)