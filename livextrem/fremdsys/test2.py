import tapi_mod
import oauth


token = oauth.gen()

#print(token.displayname, token.loginname)

#result = tapi_mod.get_messages(token)
#result = tapi_mod.test_irc_connection(token)
# result = tapi_mod.get_vod_chat(token)



# +++ Chat laden Funktionen ++
# all_messages, vod_with_chat, ec = tapi_mod.get_vod_chat(token)
# print(all_messages)
# print("+++++")
# print(vod_with_chat)
# print("+++++")
# print(ec)


#result = tapi_mod.get_mod_history(token)

# result = tapi_mod.ban_or_timeout_user(token, "dieFlaavina", 0, "War unanständig")
# result = tapi_mod.unban_user(token, "dieFlaavina")

# print(result)