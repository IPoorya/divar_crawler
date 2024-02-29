from modules.post import Post



def extract_data(state, tokens, data):
    post = Post()
    state['index'] = 0
    while tokens:
        token = tokens.pop(0)
        post.get(token, 1)

        if not post.exists():
            post.get(token, 1)

        if post.exists():
            try:
                postData = post.data()

            except Exception as e:
                print(e)
                continue

            if not postData:
                print(str(state['index']))
                print("didn't have price")
                state['index'] += 1
                continue

            for record in postData:
                rec = {'token': token}
                rec.update(record)
                data.append(rec)
                print(str(state['index']))
                print(rec)
            state['index'] += 1
        else:
            print(str(state['index']) + ' - ' + '404')
            state['index'] += 1
        
    
    post.driverQuit()
    return data