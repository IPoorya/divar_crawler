from playwright.sync_api import sync_playwright
import json


# end_points = {
#     "isfahan": "https://divar.ir/s/isfahan/real-estate",
#     "karaj": "https://divar.ir/s/karaj/real-estate",
#     "tehran": "https://divar.ir/s/tehran/real-estate",
#     "mashahd": "https://divar.ir/s/mashhad/real-estate",
#     "ahvaz": "https://divar.ir/s/ahvaz/real-estate",
#     "shiraz": "https://divar.ir/s/shiraz/real-estate",
#     "qom": "https://divar.ir/s/qom/real-estate",
#     "rasht": "https://divar.ir/s/rasht/real-estate"
# }



lpd = ''
def last_post_date(state=None):
    def handle_route(route):
        global lpd
        request = route.request
        post_data = request.post_data
        if post_data:
            request_data = json.loads(post_data)
            lpd = request_data.get("last-post-date")

        route.continue_()


    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()

        global lpd

        page = context.new_page()
        page.goto("https://divar.ir/s/tehran-province/rent-residential")

        # Enable request interception
        page.route('https://api.divar.ir/v8/web-search/undefined/residential-rent', lambda route: handle_route(route))

        # Scroll down to trigger API calls
        for _ in range(1):  # You may need to adjust the number of times to scroll
            page.keyboard.press('End')
            page.wait_for_timeout(2000)  # Adjust as needed

        browser.close()
        return lpd
    

    