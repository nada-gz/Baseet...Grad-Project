import requests

def test():
    # Attempt to login as supervisor
    resp = requests.post("http://127.0.0.1:8000/auth/login", data={"username":"supervisor_user","password":"password"})
    print("Login:", resp.status_code, resp.text)
    
    if resp.status_code == 200:
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        for ep in ["/supervisor/students/all", "/supervisor/teachers", "/supervisor/students/flagged"]:
            r = requests.get(f"http://127.0.0.1:8000{ep}", headers=headers)
            print(f"{ep}:", r.status_code)
            if r.status_code != 200:
                print(r.text)

test()
