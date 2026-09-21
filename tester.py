import requests

APP_ID = "01a0b45b-2b66-7d27-b86a-dc163bcfce00"        # from the app you just registered
PAT_TOKEN = "pat_9e9d988710e9b09cac39396028f5c999bdd6569b73d3e94f3c3ce1e672baa79f"

resp = requests.get(
    "https://api.derivws.com/trading/v1/options/accounts",
    headers={
        "Authorization": f"Bearer {PAT_TOKEN}",
        "Deriv-App-ID": APP_ID,
    },
)

print(resp.status_code)
print(resp.json())