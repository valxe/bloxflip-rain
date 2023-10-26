import os
import json
import time
import requests
import cloudscraper
from webserver import keep_alive
from discord_webhook import DiscordWebhook, DiscordEmbed

webhook_enable = True
webhookurl = os.environ['webhookurl']
minimum = 10
ping = os.environ['ping']
refresh = 150

if webhook_enable == True:
    webhook = DiscordWebhook(url=webhookurl, content=f"{ping}")

keep_alive()
time.sleep(5)
os.system('clear')
rain_end = 0

while True:
    try:
        scraper = cloudscraper.create_scraper()
        r = scraper.get('https://api.bloxflip.com/chat/history').json()
        check = r['rain']
        if check['active'] == True:
            if check['prize'] >= minimum:
                grabprize = str(check['prize'])[:-2]
                prize = (format(int(grabprize), ","))
                host = check['host']
                getduration = check['duration']
                created = check['created']
                umduration = getduration + created
                eduration = umduration / 1000
                duration = round(eduration)
                convert = (getduration / (1000 * 60)) % 60
                waiting = (convert * 60 + 10)
                sent = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(int(time.time())))

                if time.time() > rain_end:
                    print("Bloxflip Rain!")
                    print(f"Rain amount: {prize} R$")
                    print(f"Expiration: {duration} minutes")
                    print(f"Host: {host}")
                    print(f"Timestamp: {sent}\n")
                    
                    print("Sending request to users.roblox.com API...")
                    userid = requests.post(f"https://users.roblox.com/v1/usernames/users",
                                           json={"usernames": [host]}).json()['data'][0]['id']
                    print("Request success!")

                    print("Sending request to thumbnails.roblox.com API...")
                    thumburl = requests.get(
                        f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={userid}&size=50x50&format=Png&isCircular=false").json()[
                        'data'][0]['imageUrl']
                    print("Request success!")

                    if webhook_enable == True:
                        embed = DiscordEmbed(title=f"{host} is hosting a chat rain!", url="https://bloxflip.com",
                                             color=0xFFC800)
                        embed.add_embed_field(name="Rain Amount", value=f"{prize} R$")
                        embed.add_embed_field(name="Expiration", value=f"<t:{duration}:R>")
                        embed.add_embed_field(name="Host",
                                              value=f"[{host}](https://www.roblox.com/users/{userid}/profile)")
                        embed.set_timestamp()
                        embed.set_thumbnail(url=thumburl)
                        webhook.add_embed(embed)
                        print("Executing webhook...")
                        webhook.execute()
                        print("Webhook executed!")
                        webhook.remove_embed(0)
                        print("All Done!")
                        rain_end = time.time() + duration * 60
                        
                    time.sleep(duration * 60 + 10)

            else:
                print("Rain amount does not meet the minimum requirement")
                time.sleep(130)
        elif check['active'] == False:
            time.sleep(refresh)
    except Exception as e:
        error_message = str(e)
        if webhook_enable == True:
            webhook_error = DiscordWebhook(url=webhookurl, content=f"An error occurred: {error_message}")
            webhook_error.execute()
        print(error_message)
        time.sleep(refresh)
