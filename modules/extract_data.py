from modules.post import Post



def extract_data(state, tokens, data):
    post = Post()
    state['p'] = 0
    while tokens:
        token = tokens.pop(0)
        post.get(token)
        if post.exists(token):
            try:
                postData = post.data(token)
            except Exception as e:
                print(e)
                continue
            if not postData:
                    print(str(state['p']))
                    print("didn't have price")
                    state['p'] += 1
                    continue
            for record in postData:
                data.append(record)
                print(str(state['p']))
                print(record)
            state['p'] += 1
        else:
            print(str(state['p']) + ' - ' + '404')
            state['p'] += 1
        
    post.driverQuit()
    return data