import requests

# Admin
r = requests.post("http://127.0.0.1:8000/api/auth/login", json={"email": "shange@linknest.local", "password": "admin123"})
h = {"Authorization": "Bearer " + r.json()["access_token"]}

# Create
tag = requests.post("http://127.0.0.1:8000/api/tags", json={"name": "test", "slug": "test-tag", "level": 1}, headers=h)
assert tag.status_code == 201, f"Create failed: {tag.status_code} {tag.text}"
tid = tag.json()["id"]
print(f"Create: OK id={tid}")

# Update
up = requests.put(f"http://127.0.0.1:8000/api/tags/{tid}", json={"name": "Modified"}, headers=h)
assert up.status_code == 200
print("Update: OK")

# Delete
dl = requests.delete(f"http://127.0.0.1:8000/api/tags/{tid}", headers=h)
assert dl.status_code == 204
print("Delete: OK")

# Normal user denied
r2 = requests.post("http://127.0.0.1:8000/api/auth/login", json={"email": "normal@test.com", "password": "user1234"})
h2 = {"Authorization": "Bearer " + r2.json()["access_token"]}
res = requests.post("http://127.0.0.1:8000/api/tags", json={"name": "x", "slug": "x"}, headers=h2)
assert res.status_code == 403
print("Normal create: 403 (correct)")

print("\nAll tag CRUD tests passed.")
