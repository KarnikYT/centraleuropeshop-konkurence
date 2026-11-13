import json
import os
import urllib.request

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
STATE_FILE = "state.json"

# Definice sledovaných konkurentů a jejich produktů (zde si budeš upravovat data/scrapovat weby)
# V reálném provozu sem můžeš doplnit vlastní parsování stránek (např. pomocí BeautifulSoup)
current_data = {
    "Kladenské Dílny": {
        "Karosa C 954": {"price": 149, "currency": "CZK", "available": True},
        "SOR NB 12": {"price": 199, "currency": "CZK", "available": True}
    },
    "DevyBus": {
        "Citybus 12M Pack": {"price": 250, "currency": "CZK", "available": True}
    },
    "Western European Shop": {
        "German City Station": {"price": 15, "currency": "EUR", "available": True}
    },
    "CentralEurope Roblox Shop": {
        "Prague Tram Infrastructure": {"price": 300, "currency": "CZK", "available": True}
    }
}

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=4)

def send_discord_notification(html_content):
    if not DISCORD_WEBHOOK_URL:
        print("Chybí DISCORD_WEBHOOK_URL!")
        return
    
    # Discord webhook pro zprávy (můžeme poslat čistý text nebo embed v JSON)
    payload = {
        "content": "🔔 **Den ní hlášení: Sledování konkurence Roblox assetů**\n" + html_content
    }
    
    req = urllib.request.Request(
        DISCORD_WEBHOOK_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "RobloxTrackerBot"}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            print(f"Odesláno na Discord, status: {response.status}")
    except Exception as e:
        print(f"Chyba při odesílání na Discord: {e}")

def main():
    old_state = load_state()
    changes_detected = []
    
    if not old_state:
        print("První spuštění: Inicializuji výchozí stav.")
        save_state(current_data)
        send_discord_notification("✅ Sledování konkurence bylo úspěšně inicializováno. První srovnávací data byla uložena.")
        return

    # Porovnání cen a produktů
    for competitor, products in current_data.items():
        if competitor not in old_state:
            changes_detected.append(f"✨ **Nový konkurent:** {competitor} byl přidán do sledování.")
            continue
            
        for prod_name, details in products.items():
            if prod_name not in old_state[competitor]:
            
                changes_detected.append(f"🚀 **Nový produkt:** `{competitor}` vydal novou položku **{prod_name}** za `{details['price']} {details['currency']}`.")
                continue
                
            old_details = old_state[competitor][prod_name]
            old_price = old_details["price"]
            new_price = details["price"]
            
            if old_price != new_price:
                diff = new_price - old_price
                percent = (diff / old_price) * 100 if old_price > 0 else 0
                direction = "zvýšena" if diff > 0 else "snížena"
                changes_detected.append(
                    f"💰 **Změna ceny u `{competitor}` ({prod_name}):**\n"
                    f"• Stará cena: `{old_price} {details['currency']}`\n"
                    f"• Nová cena: `{new_price} {details['currency']}`\n"
                    f"• Změna: Cena byla **{direction}** o `{abs(diff)} {details['currency']}` (`{percent:.1f}%`)."
                )

    # Uložení nového stavu
    save_state(current_data)

    # Odeslání notifikace, pokud se něco změny
    if changes_detected:
        message = "\n\n".join(changes_detected)
        send_discord_notification(message)
    else:
        print("Za posledních 24 hodin nebyly zaznamenány žádné změny cen ani nové produkty.")

if __name__ == "__main__":
    main()
