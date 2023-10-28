import os
import time

import cloudscraper
import requests
from discord_webhook import DiscordEmbed, DiscordWebhook

from webserver import keep_alive

webhook_enable = True
webhookurl = os.environ.get('webhookurl')
ping = os.environ.get('ping')
minimum = 10
refresh = 150

def send_webhook_message(content):
    if webhook_enable:
        webhook = DiscordWebhook(url=webhookurl, content=content)
        webhook.execute()

def get_user_id(username):
    try:
        response = requests.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [username]})
        response.raise_for_status()
        user_id = response.json()['data'][0]['id']
        return user_id
    except Exception as e:
        raise Exception(f"Error getting user ID: {e}")

def get_thumbnail_url(user_id):
    try:
        response = requests.get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={user_id}&size=50x50&format=Png&isCircular=false")
        response.raise_for_status()
        thumbnail_url = response.json()['data'][0]['imageUrl']
        return thumbnail_url
    except Exception as e:
        raise Exception(f"Error getting thumbnail URL: {e}")

def main():
    while True:
        try:
            scraper = cloudscraper.create_scraper()
            r = scraper.get('https://api.bloxflip.com/chat/history').json()
            check = r.get('rain')

            if check and check.get('active'):
                if check.get('prize', 0) >= minimum:
                    grabprize = str(check['prize'])[:-2]
                    prize = format(int(grabprize), ",")
                    host = check['host']
                    getduration = check['duration']
                    created = check['created']
                    umduration = getduration + created
                    eduration = umduration / 1000
                    duration = round(eduration)
                    convert = (getduration / (1000 * 60)) % 60
                    (convert * 60 + 10)
                    sent = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(int(time.time())))

                    if time.time() > rain_end:
                        print("Bloxflip Rain!")
                        print(f"Rain amount: {prize} R$")
                        print(f"Expiration: {duration} minutes")
                        print(f"Host: {host}")
                        print(f"Timestamp: {sent}\n")

                        print("Sending request to users.roblox.com API...")
                        userid = get_user_id(host)
                        print("Request success!")

                        print("Sending request to thumbnails.roblox.com API...")
                        thumburl = get_thumbnail_url(userid)
                        print("Request success!")

                        if webhook_enable:
                            embed = DiscordEmbed(title=f"{host} is hosting a chat rain!", url="https://bloxflip.com", color=0xFFC800)
                            embed.add_embed_field(name="Rain Amount", value=f"{prize} R$")
                            embed.add_embed_field(name="Expiration", value=f"<t:{duration}:R>")
                            embed.add_embed_field(name="Host", value=f"[{host}](https://www.roblox.com/users/{userid}/profile)")
                            embed.set_timestamp()
                            embed.set_thumbnail(url=thumburl)
                            webhook = DiscordWebhook(url=webhookurl, content=f"{ping}")
                            webhook.add_embed(embed)
                            print("Executing webhook...")
                            webhook.execute()
                            print("Webhook executed!")
                            webhook.remove_embed(0)
                            print("All Done!")
                            time.time() + duration * 60

                        time.sleep(duration * 60 + 10)

                else:
                    print("Rain amount does not meet the minimum requirement")
                    time.sleep(130)

            elif check and not check.get('active'):
                time.sleep(refresh)

        except Exception as e:
            error_message = str(e)
            send_webhook_message(f"An error occurred: {error_message}")
            print(error_message)
            time.sleep(refresh)

if __name__ == '__main__':
    keep_alive()
    time.sleep(5)
    os.system('clear')
    rain_end = 0
    main()
