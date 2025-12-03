import tapi_mod
import oauth


token = oauth.gen()

print(token.displayname, token.loginname)

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

#print(result)