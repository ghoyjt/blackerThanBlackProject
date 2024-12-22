import aiohttp
from config import GEOCODING_URL, OPENWEATHER_TOKEN, OPENWEATHER_URL


async def get_coords(city):
    async with aiohttp.ClientSession() as session:
        url = f"{GEOCODING_URL}/direct"
        params = {
            "q": city,
            "limit": 1,
            "appid": OPENWEATHER_TOKEN
        }
        async with session.get(url, params=params) as resp:
            data = await resp.json()
            if data:
                return data[0]["lat"], data[0]["lon"]
            return None


async def get_weather(city, days):
    coords = await get_coords(city)
    if not coords:
        return None

    lat, lon = coords
    async with aiohttp.ClientSession() as session:
        url = f"{OPENWEATHER_URL}/forecast"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": OPENWEATHER_TOKEN,
            "units": "metric"
        }
        async with session.get(url, params=params) as resp:
            data = await resp.json()
            if resp.status != 200:
                return None

            forecasts = []
            seen_dates = set()

            for item in data["list"]:
                date = item["dt_txt"].split()[0]
                if date not in seen_dates and len(seen_dates) < days:
                    seen_dates.add(date)
                    forecasts.append({
                        "date": date,
                        "temp": round(item["main"]["temp"]),
                        "wind": round(item["wind"]["speed"]),
                        "rain": round(item.get("rain", {}).get("3h", 0), 1)
                    })

            return {
                "city": data["city"]["name"],
                "forecasts": forecasts
            }
