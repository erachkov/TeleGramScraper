import configparser
import csv

from telethon import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty

# Reading Configs
config = configparser.ConfigParser()
config.read("src/config/config.ini")

# Setting configuration values
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']
chunk_group_size = int(config['Telegram']['chunk_group_size'])
chunk_user_size = int(config['Telegram']['chunk_user_size'])
api_hash = str(api_hash)
myphone = config['Telegram']['phone']
username = config['Telegram']['username']

last_date = None

client = TelegramClient(username, api_id, api_hash)


async def get_all_groups():
    chats = []
    groups = []

    result = await client(GetDialogsRequest(
        offset_date=last_date,
        offset_id=0,
        offset_peer=InputPeerEmpty(),
        limit=chunk_group_size,
        hash=0
    ))
    chats.extend(result.chats)

    for chat in chats:
        try:
            if chat.megagroup:
                groups.append(chat)
        except:
            continue
    return groups

async def get_participants_in_group(group):
    users = client.get_participants(group, aggressive=True)
    return users

async def main():
    while True:
        groups = await get_all_groups()
        for id, group in enumerate(groups):
            print(id + 1, group.title)

        print(0, "Exit")
        g_index = input("Enter a Number: ")

        if not g_index.isdigit():
            print(f"Enter a Number!  Not {g_index}")
            continue

        target_group = groups[int(g_index)-1]

        print()
        print('You choose group {}'.format(target_group.title))
        print()

        if not int(g_index):
            break

        print('Fetching Members...')
        print()

        all_participants = await client.get_participants(target_group, aggressive=True)

        file  = f"src/data/{str(target_group.title).replace(' ','_')}.csv"
        with open(file,"w",encoding='UTF-8') as f:
            writer = csv.writer(f,delimiter=",", lineterminator="\n")
            writer.writerow(['id', 'name', 'username', 'phone'])
            for user in all_participants:
                if user.username:
                    username = user.username
                else:
                    username = ""
                if user.first_name:
                    first_name = user.first_name
                else:
                    first_name = ""
                if user.last_name:
                    last_name = user.last_name
                else:
                    last_name= ""
                name= (first_name + ' ' + last_name).strip()

                writer.writerow([user.id, name, username, user.phone])
            print(f'Members scraped successfully to file {file}')

if __name__ == "__main__":
    client.start(phone=myphone, max_attempts=3)
    with client as cln:
        cln.loop.run_until_complete(main())
