import httpx
import json
url='http://127.0.0.1:8000/api/auth/register'
for payload in [
    {'email':'testuser_name@example.com','name':'Test Name','password':'TestPass123'},
    {'email':'testuser_full@example.com','full_name':'Test Full','password':'TestPass123'}
]:
    try:
        r=httpx.post(url,json=payload,timeout=10.0)
        print('Payload:', json.dumps(payload))
        print('Status:', r.status_code)
        print('Response:', r.text)
    except Exception as e:
        print('Error:', e)
