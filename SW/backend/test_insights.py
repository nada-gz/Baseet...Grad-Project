import requests

def test():
    resp = requests.post("http://127.0.0.1:8000/auth/login", json={"email":"nada.super@gmail.com","password":"password"})
    if resp.status_code == 200:
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        r = requests.get("http://127.0.0.1:8000/parent/child/1/insights", headers=headers)
        print(r.status_code)
        print(r.text[:200])
    else:
        print("Login failed")

test()
