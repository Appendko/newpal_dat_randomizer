#Python Script to randomize talk8.dat
#Author: Append Huang (append@gmail.com)
#Reference: https://www.ptt.cc/bbs/pal/M.1461154467.A.F26.html
#Reference: https://goo.gl/VypRfq

#read binary file as bytearray to make modification
import os
import random
from common import item_lst, full_item_lst, magic_obtainitem_lst
from tFile import tFile
from gFile import gFile
item_dict = dict(item_lst)

    
# def randomize_talkitem(tfile, gmagic):
#     global multi_item_dict
#     global multi_magicitem_dict    
#     multi_item_dict = generate_multi_item_dict(item_lst, 2, 5)
#     multi_magicitem_dict = generate_multi_item_dict(magic_obtainitem_lst, 1, 1)    
#     res_lst = randomize_titem(tfile)
#     res_lst.extend(randomize_titem_gmagic(tfile,gmagic))
#     return res_lst


# def print_talkitem_lst(res_item_lst):
#     for tup_print in res_item_lst:
#         print("%s -> %s"%tup_print[4:])
#     return 

def fix_luggage(gmagic, gitem, talk1):
    # gmagic.search_id(0x107A)
    # In [43]: [item_dict.get(a.value(1), "") for a in gmagic.search_id(0x107A)[1].items]
    # Out[43]: ['', '', '玉鐲', '繡花鞋', '生鏽鐵劍', '還神丹', '金創藥', '', '', '']
    luggage_item_lst = [magic_item for magic_item in gmagic.search_id(0x107A)[1].items 
                                   if magic_item.value(1) in item_dict] # 包袱
    replace_item_lst = [0x0F77,0x0F3D,0x0D7C,0x0F40,0x0F3F] # 金蠶王,引路蜂,生鏽鐵劍,驅魔香,十里香

    for magic_item in luggage_item_lst: #5 items
        # print(magic_item)
        item_id = magic_item.value(1)
        item_name = item_dict[item_id]

        replace_id = replace_item_lst.pop()
        magic_item.set_value(replace_id, 1)
        magic_item.set_value(0x01, 2)
        replace_name = item_dict[replace_id]
        # print(item_name, "->", replace_name)
        # print(magic_item)

    orig_desc = "一些療傷藥、一雙繡花鞋、玉鐲子"
    replace_desc = "一隻引路蜂、一個驅魔香、十里香"
    talk_item = [x for x in talk1.items if x.findall(orig_desc)][1]
    ind_str = talk_item.findstr_r(orig_desc, 0)
    talk_item[ind_str] = replace_desc

    # Infinite Use: [(0x0F3F, '十里香%%'), (0x0F40, '驅魔香%%')]
    obj_lst = [0x0F3F, 0x0F40]
    for obj_id in obj_lst: 
        obj_item = gitem.search_id(obj_id)[1]
        obj_gitem = obj_item.search_initial(b"\x01\x00\x20\x7F\x06")[0] #是否消耗: 0x7F200001, 0x06
        obj_gitem.set_value(-1,2,offset=2,signed=True) #不消耗: FFFF (-1)
    return

if __name__ == "__main__":   
    gmagic = gFile("dat/gmagic.dat")
    gitem = gFile("dat/gitem.dat")
    talk1 = tFile("dat/talk1.dat")
    fix_luggage(gmagic, gitem, talk1)

    # talk1 = tFile("dat/talk1.dat")
    # talk2 = tFile("dat/talk2.dat")
    # talk3 = tFile("dat/talk3.dat")
    # talk4 = tFile("dat/talk4.dat")       
    # talk8 = tFile("dat/talk8.dat")