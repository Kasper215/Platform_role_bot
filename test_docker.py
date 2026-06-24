import urllib.request, urllib.parse, json

BASE = 'http://localhost:8001/api'

# 1. Регистрация
print('=== 1. Signup ===')
data = json.dumps({'email':'test2@test.com','username':'testuser2','display_name':'Тест','password':'test123456'}).encode()
r = urllib.request.Request(BASE+'/auth/signup', data=data, method='POST')
r.add_header('Content-Type','application/json')
try:
    resp = json.loads(urllib.request.urlopen(r).read())
    print('OK:', resp.get('email',''))
except Exception as e:
    print('Signup:', e)

# 2. Login
print()
print('=== 2. Login ===')
data = urllib.parse.urlencode({'username':'test2@test.com','password':'test123456'}).encode()
r = urllib.request.Request(BASE+'/auth/login', data=data, method='POST')
r.add_header('Content-Type','application/x-www-form-urlencoded')
resp = json.loads(urllib.request.urlopen(r).read())
token = resp['access_token']
print('Token OK:', token[:20]+'...')

# 3. Profile
print()
print('=== 3. Profile ===')
r = urllib.request.Request(BASE+'/auth/me')
r.add_header('Authorization','Bearer '+token)
me = json.loads(urllib.request.urlopen(r).read())
print('User:', me.get('display_name',''), '-', me.get('email',''))

# 4. Characters
print()
print('=== 4. Characters ===')
r = urllib.request.Request(BASE+'/characters/')
r.add_header('Authorization','Bearer '+token)
chars = json.loads(urllib.request.urlopen(r).read())
print('Total:', len(chars))
for c in chars[:8]:
    print('  [' + str(c['id']) + '] ' + c['name'])

# 5. Featured
print()
print('=== 5. Featured ===')
r = urllib.request.Request(BASE+'/characters/featured')
r.add_header('Authorization','Bearer '+token)
feat = json.loads(urllib.request.urlopen(r).read())
print('Featured:', len(feat))
for c in feat:
    print('  [' + str(c['id']) + '] ' + c['name'])

# 6. Tags
print()
print('=== 6. Tags ===')
r = urllib.request.Request(BASE+'/characters/tags')
r.add_header('Authorization','Bearer '+token)
tags = json.loads(urllib.request.urlopen(r).read())
print('Tags:', [t['name'] for t in tags])

# 7. Chat create
print()
print('=== 7. Create Chat ===')
if chars:
    cid = chars[0]['id']
    r = urllib.request.Request(BASE+'/chats/'+str(cid), data=b'{}', method='POST')
    r.add_header('Authorization','Bearer '+token)
    r.add_header('Content-Type','application/json')
    chat = json.loads(urllib.request.urlopen(r).read())
    print('Chat created, messages:', len(chat['messages']))
    if chat['messages']:
        m = chat['messages'][0]
        print('  First message:', m['role'], ':', m['content'][:60]+'...')

# 8. Chats list
print()
print('=== 8. Chats List ===')
r = urllib.request.Request(BASE+'/chats/')
r.add_header('Authorization','Bearer '+token)
chats = json.loads(urllib.request.urlopen(r).read())
print('Chats:', len(chats))
for ch in chats:
    print('  [' + str(ch['character_id']) + '] ' + ch.get('character_name','?'))
