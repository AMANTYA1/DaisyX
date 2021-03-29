import os


from pyrogram import filters
from DaisyX.services.pyrogram import Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from DaisyX.db.mongo_helpers.connections_mdb import add_connection, all_connections, if_active, delete_connection



@Client.on_message((filters.private | filters.group) & filters.command("connect"))
async def addconnection(client,message):
    userid = message.from_user.id
    chat_type = message.chat.type

    if chat_type == "private":
        try:
            cmd, group_id = message.text.split(" ", 1)
        except:
            return

    elif (chat_type == "group") or (chat_type == "supergroup"):
        group_id = message.chat.id

    try:
        st = await client.get_chat_member(group_id, userid)
        if (st.status == "administrator") or (st.status == "creator"):
            pass
        else:
            await message.reply_text("You should be an admin in Given group!", quote=True)
            return
    except Exception as e:
        print(e)
        await message.reply_text(
            "Invalid Group ID!\n\nIf correct, Make sure I'm present in your group!!",
            quote=True
        )
        return

    try:
        st = await client.get_chat_member(group_id, "me")
        if st.status == "administrator":
            ttl = await client.get_chat(group_id)
            title = ttl.title

            addcon = await add_connection(str(group_id), str(userid))
            if addcon:
                await message.reply_text(
                    f"Sucessfully connected to **{title}**\nNow manage your group from my pm !",
                    quote=True,
                    parse_mode="md"
                )
                if (chat_type == "group") or (chat_type == "supergroup"):
                    await message.reply_text(
                        f"Connected to **{title}** !",
                        quote=True,
                        parse_mode="md"
                    )
            else:
                await message.reply_text(
                    "You're already connected to this chat!",
                    quote=True
                )
        else:
            await message.reply_text("Add me as an admin in group", quote=True)
    except Exception as e:
        print(e)
        await message.reply_text(
            "Some error occured! Try again later.",
            quote=True
        )
        return


@Client.on_message((filters.private | filters.group) & filters.command("disconnect"))
async def deleteconnection(client,message):
    userid = message.from_user.id
    chat_type = message.chat.type

    if chat_type == "private":
        await message.reply_text("Run /connections to view or disconnect from groups!", quote=True)

    elif (chat_type == "group") or (chat_type == "supergroup"):
        group_id = message.chat.id

        st = await client.get_chat_member(group_id, userid)
        if not ((st.status == "administrator") or (st.status == "creator")):
            return

        delcon = await delete_connection(str(userid), str(group_id))
        if delcon:
            await message.reply_text("Successfully disconnected from this chat", quote=True)



@Client.on_message(filters.private & filters.command(["connections"]))
async def connections(client,message):
    userid = message.from_user.id

    groupids = await all_connections(str(userid))
    if groupids is None:
        return
    buttons = []
    for groupid in groupids:
        try:
            ttl = await client.get_chat(int(groupid))
            title = ttl.title
            active = await if_active(str(userid), str(groupid))
            if active:
                act = " - ACTIVE \n Remember you can only /filter or stop filters in multiple groups. other connections only support one group"
            else:
                act = ""
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{title}:{act}"
                    )
                ]
            )
        except:
            pass
    if buttons:
        await message.reply_text(
            "Your connected group details ;\n\n",
            reply_markup=InlineKeyboardMarkup(buttons),
            quote=True
        )
