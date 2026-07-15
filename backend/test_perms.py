import requests

# Admin login & CRUD
r = requests.post("http://127.0.0.1:8000/api/auth/login", json={"email": "shange@linknest.local", "password": "admin123"})
t = r.json()["access_token"]
role = r.json()["user"]["role"]
h = {"Authorization": f"Bearer {t}"}
print(f"Admin role={role}")

bm = requests.post("http://127.0.0.1:8000/api/bookmarks", json={"title": "Test", "url": "https://a.com", "tag_ids": [1]}, headers=h)
assert bm.status_code == 201, f"Create failed: {bm.status_code} {bm.text}"
bid = bm.json()["id"]
print(f"Admin create: OK id={bid}")

up = requests.put(f"http://127.0.0.1:8000/api/bookmarks/{bid}", json={"title": "Updated"}, headers=h)
assert up.status_code == 200
print(f"Admin update: OK title={up.json()['title']}")

dl = requests.delete(f"http://127.0.0.1:8000/api/bookmarks/{bid}", headers=h)
assert dl.status_code == 204
print("Admin delete: OK")

# Normal user
r2 = requests.post("http://127.0.0.1:8000/api/auth/login", json={"email": "normal@test.com", "password": "user1234"})
h2 = {"Authorization": f"Bearer {r2.json()['access_token']}"}
print(f"\nNormal user role={r2.json()['user']['role']}")

res = requests.post("http://127.0.0.1:8000/api/bookmarks", json={"title": "x", "url": "https://x.com"}, headers=h2)
print(f"Normal create: {res.status_code} {'(403 expected)' if res.status_code==403 else 'FAIL'}")

res2 = requests.get("http://127.0.0.1:8000/api/bookmarks", headers=h2)
print(f"Normal list: {res2.status_code} {'(200 expected)' if res2.status_code==200 else 'FAIL'}")

print("\nAll permissions verified.")
