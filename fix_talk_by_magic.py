#Python Script to randomize talk8.dat
#Author: Append Huang (append@gmail.com)
#Reference: https://www.ptt.cc/bbs/pal/M.1461154467.A.F26.html
#Reference: https://goo.gl/VypRfq

#read binary file as bytearray to make modification
import os
import random
from common import magic_lst, user_lst
from tFile import tFile
from gFile import gFile
magic_dict = dict(magic_lst)
user_dict = dict(user_lst)

def find_learn_gitem_id(gmagic):
    # 00 20 10 7f 3b 11 00 00               # 3B 11
    # 45 20 20 7f d0 07 00 00 5f 1a 00 00   # D0 07 李逍遙 5F 1A 冰心訣 
    # 45 20 20 7f d0 07 00 00 6c 18 00 00   # D0 07 李逍遙 6C 18 飛龍探雲手
    # id_pattern = b"\x00\x20\x10\x7F"
    res_lst = []
    type_pattern = b"\x45\x20\x20\x7F"
    for item in gmagic.items:
        gitem_id = item[0].value(1)        
        item_learn_magic_lst = item.search_initial(type_pattern)
        for item_learn_magic in item_learn_magic_lst:
            user_id = item_learn_magic.value(1)
            magic_id = item_learn_magic.value(2)
            username = user_dict[user_id]
            print("0x%06X, %s, 0x%04X, %s"%(gitem_id, username, magic_id, magic_dict[magic_id]))

    return #res_lst

# 0x00113B, 手卷, 0x1A5F, 冰心訣, 0x186C, 飛龍探雲手
# 0x00170F, 學御劍術, 0x1901, 御劍術 
# 0x001712, 還魂咒, 0x1AC3, 還魂咒
# 0x001713, 靈葫咒, 0x186B, 靈葫咒
# 0x001388, 酒劍仙蜀山教學, 0x186D, 酒神, 0x1839, 仙風雲體術, 0x183B, 醉仙望月步
# 0x001468, 逍遙試煉窟山神, 0x1969, 山神
# 0x001469, 阿奴試煉窟火神, 0x199B, 火神
# 0x00146A, 逍遙試煉窟雷神, 0x19CD, 雷神
# 0x00146B, 阿奴試煉窟風神, 0x19FE, 風神
# 0x00146F, 阿奴試煉窟雪妖, 0x1936, 雪妖
# 0x001471, 靈兒試煉窟火神, 0x199B, 火神
# 0x001473, 靈兒鎖妖塔夢蛇, 0x1B27, 夢蛇
# 0x001474, 阿奴贖魂, 0x1AC4, 贖魂


if __name__ == "__main__":   
    gmagic = gFile("dat/gmagic.dat")
    talk1 = tFile("dat/talk1.dat")
    talk2 = tFile("dat/talk2.dat")
    talk3 = tFile("dat/talk3.dat")
    talk4 = tFile("dat/talk4.dat")       
    talk8 = tFile("dat/talk8.dat")
    find_learn_gitem_id(gmagic)


# 包袱
# gmagic.search_id(0x107A)
# In [43]: [item_dict.get(a.value(1), "") for a in gmagic.search_id(0x107A)[1].items]
# Out[43]: ['', '', '玉鐲', '繡花鞋', '生鏽鐵劍', '還神丹', '金創藥', '', '', '']
    
