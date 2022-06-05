import asyncio
from pulitzers import get_all


all_members = asyncio.get_event_loop().run_until_complete(get_all())
all_members.to_csv("pulitzer_members.csv")