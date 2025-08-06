from typing import Any

from chara.onebot.api.onebot import OneBotAPI


class NapCatAPI(OneBotAPI):
    '''
    ## NapCat 协议API
    '''

    ## 账号相关
    @staticmethod
    async def set_qq_profile(*, nickname: str, personal_note: str = ..., sex: str = ...) -> dict[str, Any]:
        '''
        ## 设置账号信息

        ---
        ### 参数
        - nickname: 昵称
        - personal_note: 个性签名
        - sex: 性别
            - 0: 未知
            - 1: 男
            - 2: 女
        ---
        ### 响应数据
        - result
        - errMsg
        '''

'''
ArkSharePeer
ArkShareGroup
set_online_status
get_friends_with_category
set_qq_avatar
send_like
create_collection
set_friend_add_request
set_self_longnick
get_stranger_info
get_friend_list
get_profile_like
fetch_custom_face
upload_private_file
delete_friend
nc_get_user_status
send_private_msg
send_private_forward_msg
forward_friend_single_msg
group_poke
send_group_msg
send_group_forward_msg
forward_group_single_msg
mark_msg_as_read
mark_group_msg_as_read
mark_private_msg_as_read
_mark_all_as_read
delete_msg
get_msg
get_image
get_record
get_file
get_group_msg_history
set_msg_emoji_like
get_friend_msg_history
get_recent_contact
fetch_emoji_like
get_forward_msg
send_forward_msg
set_group_kick
set_group_ban
get_group_system_msg
get_essence_msg_list
set_group_whole_ban
set_group_portrait
set_group_admin
set_essence_msg
set_group_card
delete_essence_msg
set_group_name
set_group_leave
_send_group_notice
_get_group_notice
set_group_special_title
upload_group_file
set_group_add_request
get_group_info
get_group_info_ex
create_group_file_folder
delete_group_file
delete_group_folder
get_group_file_system_info
get_group_root_files
get_group_files_by_folder
get_group_file_url
get_group_list
get_group_member_info
get_group_member_list
get_group_honor_info
get_group_at_all_remain
get_group_ignored_notifies
set_group_sign
send_group_sign
get_ai_characters
send_group_ai_record
get_ai_record
get_online_clients
get_robot_uin_range
ocr_image
get_login_info
set_input_status
download_file
get_cookies
get_csrf_token
_del_group_notice
get_credentials
_get_model_show
_set_model_show
can_send_image
nc_get_packet_status
can_send_record
get_status
nc_get_rkey
get_version_info
get_group_shut_list
'''