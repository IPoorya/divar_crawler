import requests
from modules.post import Post
import time, random


def apiRequest(page, city, last_post_date, category, max_retries=10, timeout=3):
    url = f"https://api.divar.ir/v8/web-search/12/{category}"

    
    data = {
        "page": 0,
        "json_schema": {
            "cities": city,
            "category": {"value": f"{category}"},
            "sort": {"value": "sort_date"}
        },
        "last-post-date": int(last_post_date)
    }

    headers = {"Content-Type": "application/json"}
    retries = 0
    while retries < max_retries:
        try:
            response = requests.post(url, json=data, headers=headers, timeout=timeout)
            response.raise_for_status()  # Raise an exception if the response status code is not 200
            return response
        except requests.Timeout:
            print(f"Request timed out after {timeout} seconds. Retrying...")
            retries += 1
            time.sleep(2)
        except Exception as e:
            print(f"Error: {e}")
            break 


def dateCheck(tokens, state, post):
    if not tokens:
        return True

    while True:
        try:
            post.get(tokens[random.randint(0, 23)])
            while not post.exists():
                post.get(tokens[random.randint(0, 23)])

            date = post.date()
            if date == 0:
                print('waiting for date check')
                time.sleep(2)
                continue
            # ۵, ۴, ۳ , ۲, ۱
            elif date[1] == "هفته" and date[0] == state["duration"]:
                state["status"] = False
                print('end of duration')
                return False
            else:
                return True

        except Exception as e:
            print('getting date error')
            print(e)
            post = Post()
            continue

        

def extract_tokens(state, tokens):
    last_post_date = None
    post = Post()
    start = state["page"]
    page = state['page']
    posts = []
    while dateCheck(tokens, state, post) and page - start != state["request_count"]:
        page += 1
        response = apiRequest(state["page"], state["city"], state["last_post_date"], state["category"])                

        if response.status_code != 200:
            page -= 1
            print("status: " + str(response.status_code))
            time.sleep(5)
            continue

        response = response.json()
        last_post_date = response["last_post_date"]
        state["last_post_date"] = last_post_date
        print(page)

        posts = response["web_widgets"]["post_list"]
        while posts:
            p = posts.pop()
            if p["widget_type"] == "POST_ROW":
                tokens.append(p["data"]["token"])


    print('tokens found in this process: ' + str(len(tokens)))
    state["last_post_date"] = last_post_date
    post.driverQuit()