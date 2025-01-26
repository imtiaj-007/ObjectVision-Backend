import httpx

class SessionService:
    @staticmethod
    def detect_device_type(user_agent: str) -> str:
        device_types = {
            "mobile": ["android", "iphone", "ipad", "mobile"],
            "tablet": ["ipad", "tablet"],
            "desktop": ["windows", "macintosh", "linux"],
        }

        user_agent = user_agent.lower()
        for key, patterns in device_types.items():
            if any(pattern in user_agent for pattern in patterns):
                return key
        return "desktop"

    @staticmethod
    async def get_location_by_ip(ip: str) -> dict:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"https://ipapi.co/{ip}/json/")
                data = response.json()
                return {
                    "ip": ip,
                    "city": data.get("city", "Unknown"),
                    "country": data.get("country_name", "Unknown"),
                    "latitude": data.get("latitude"),
                    "longitude": data.get("longitude"),
                }
            except Exception:
                return {
                    "ip": ip,
                    "city": "Unknown",
                    "country": "Unknown",
                    "latitude": None,
                    "longitude": None,
                }    

