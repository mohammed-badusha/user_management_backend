import httpx

def fetch_location(ip: str) -> dict | None:
    url = f"http://ip-api.com/json/{ip}"

    try:
        response = httpx.get(url, timeout=5)

        if response.status_code != 200:
            return None

        data = response.json()

        if data.get("status") != "success":
            return None

        return data

    except Exception:
        return None
