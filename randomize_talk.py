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
magic_obtainitem_dict = dict(magic_obtainitem_lst)

def rand_helper_titem(n):
    global multi_item_dict
    return random.choice(multi_item_dict[n])

Max_Occurence = 10

def randomize_titem(tfile):    
    res_lst = []
    for i, item in enumerate(tfile.items):
        lst_8000 = item.findall(b"\x80\x00")
        if lst_8000:
            if len(lst_8000) > 1:
                if len(lst_8000) > Max_Occurence: 
                    continue
                # print(lst_8000)
            else: pass

            for ind in lst_8000:
                item_id = item.value(ind+2, 2)
                item_num = item.value(ind+4, 2, signed=True)  
                item_name = item_dict.get(item_id, "0x%04X"%item_id)                

                if item_num < 0: continue
                if item_id not in item_dict: continue

                length = len(item_name)
                if length == 1: continue

                if item_id == 0x0F3D: #[0x0F3D, "引路蜂"],
                    id_pair = [item.value(x+2,2) for x in lst_8000]
                    if id_pair == [0x0BFF, 0x0F3D]: # talk1                        
                        continue

                rand_id, rand_num, rand_name = rand_helper_titem(length)

                # 搜尋這個事件內有沒有這個物件名稱                
                str_found = item.findall(item_name)
                for ind_str in str_found: # 叫這個名字的String存在，預設可以替換，但要確認是在一個字串內
                    ind_suffix = item.findstr_r("\x25\x51", ind_str) # 字串幾乎都是由 \x25\x51 結束
                    if ind_suffix == -1: continue
                    else:
                        res_str = item.check_str(ind_str, ind_suffix) # ind_str 到 \x25\x51 中間能否翻譯成字串
                        if res_str: # 確認在同一個字串裡面，可以安全替換
                            item[ind+2] = rand_id
                            item[ind_str] = rand_name
                            replaced_str = item.check_str(ind_str, ind_suffix)
                            # print("%s 0x%06X 0x%04X 0x%04X % 4d"%(tfile.filename, i, ind, ind_str, ind_suffix-ind_str))
                            # print(res_str, "->", replaced_str, "\n")
                if str_found:
                    res_lst.append((item_name, item_num, rand_name, rand_num, res_str, replaced_str))

    return res_lst

def rand_helper_magicitem(n):
    global multi_magicitem_dict  
    return random.choice(multi_magicitem_dict[n])

def randomize_titem_gmagic(tfile, gmagic):
    res_lst = []
    for i, item in enumerate(tfile.items):
        lst_0903 = item.findall(b"\x09\x03")
        if lst_0903:
            if len(lst_0903) > 1:
                if len(lst_0903) > Max_Occurence: 
                    continue
                # print(lst_0903)
            else: pass

            item_id = None
            for ind in lst_0903:                
                magic_id = item.value(ind+2, 2)
                try:
                    magic_script = gmagic.search_id(magic_id)[1]
                except TypeError:
                    continue
                magic_gitem_lst = magic_script.search_dtype(0x7F202041)
                for magic_gitem in magic_gitem_lst:
                    item_id = magic_gitem.value(1)
                    if item_id in item_dict:
                        item_name = item_dict[item_id]
                        item_num = magic_gitem.value(2)                        

                        length = len(item_name)
                        if length == 1:
                            continue
                        # this magic_id should be randomized
                        rand_magic_id, _, rand_name = rand_helper_magicitem(length)
                        # item.arr[ind+2:ind+4] = rand_magic_id.to_bytes(2,byteorder="little")
                        # find string

                        # 搜尋這個事件內有沒有這個物件名稱                
                        str_found = item.findall(item_name)
                        for ind_str in str_found: # 叫這個名字的String存在，預設可以替換，但要確認是在一個字串內
                            ind_suffix = item.findstr_r("\x25\x51", ind_str) # 字串幾乎都是由 \x25\x51 結束
                            if ind_suffix == -1: continue
                            else:
                                res_str = item.check_str(ind_str, ind_suffix) # ind_str 到 \x25\x51 中間能否翻譯成字串
                                if res_str: # 確認在同一個字串裡面，可以安全替換
                                    item[ind+2] = rand_magic_id
                                    item[ind_str] = rand_name
                                    replaced_str = item.check_str(ind_str, ind_suffix)
                                    # print("%s 0x%06X 0x%04X 0x%04X % 4d"%(tfile.filename, i, ind, ind_str, ind_suffix-ind_str))
                                    # print(res_str, "->", replaced_str, "\n")
                        if str_found:
                            res_lst.append((item_name, item_num, rand_name, 1, res_str, replaced_str))
    return res_lst

def generate_cate_item_dict(item_lst):
    def cate_helper(item_lst, n):
        return [[item[0], 1, item[1]] for item in item_lst if len(item[1]) == n]

    dict_item = {2: cate_helper(item_lst, 2), 
                3: cate_helper(item_lst, 3), 
                4: cate_helper(item_lst, 4), 
                5: cate_helper(item_lst, 5),}
    return dict_item

def generate_multi_item_dict(item_lst, MinN, MaxN):
    dict_item = generate_cate_item_dict(item_lst)   
    def rand_helper(item):
        text_lst = ["零個", "一個", "兩個", "三個", "四個", "五個", "六個", "七個", "八個", "九個", "十個"]
        n_out = random.randint(MinN, MaxN)
        return item[0], n_out, text_lst[n_out]+item[2]

    dict_item[4].extend([rand_helper(item) for item in dict_item[2]])
    dict_item[5].extend([rand_helper(item) for item in dict_item[3]])
    return dict_item

def randomize_talkitem(tfile, gmagic):
    global multi_item_dict
    global multi_magicitem_dict    
    multi_item_dict = generate_multi_item_dict(item_lst, 2, 5)
    multi_magicitem_dict = generate_multi_item_dict(magic_obtainitem_lst, 1, 1)    
    res_lst = randomize_titem(tfile)
    res_lst.extend(randomize_titem_gmagic(tfile,gmagic))
    return res_lst

def randomize_talk1_specific(talk1):    
    # 越女劍 0x0D80
    obtain_bytes = b"\x80\x00\x80\x0D\x01\x00"
    msg_bytes = "拾得地上的寶劍".encode("big5")
    item = [x for i,x in enumerate(talk1.items) if x.findall(msg_bytes)][0]
    ind_str = item.findstr_r(msg_bytes, 0)
    ind_item = item.findstr_r(obtain_bytes, 0)
    rand_id, _, rand_name = rand_helper_titem(2)
    item[ind_item+2] = rand_id
    item[ind_str+10] = rand_name
    # print(rand_id)
    return

def print_talkitem_lst(res_item_lst):
    for tup_print in res_item_lst:
        print("%s -> %s"%tup_print[4:])
    return 


if __name__ == "__main__":   
    gmagic = gFile("dat/gmagic.dat")
    talk1 = tFile("dat/talk1.dat")
    talk2 = tFile("dat/talk2.dat")
    talk3 = tFile("dat/talk3.dat")
    talk4 = tFile("dat/talk4.dat")       
    talk8 = tFile("dat/talk8.dat")

    res_lst = []
    _ = [res_lst.extend(randomize_talkitem(t, gmagic)) for t in [talk1, talk2, talk3, talk4, talk8]]
    print_talkitem_lst(res_lst)
    # [t.export(t.filename+".randomized") for t in [talk1, talk2, talk3, talk4, talk8]]

# 包袱
# gmagic.search_id(0x107A)
# In [43]: [item_dict.get(a.value(1), "") for a in gmagic.search_id(0x107A)[1].items]
# Out[43]: ['', '', '玉鐲', '繡花鞋', '生鏽鐵劍', '還神丹', '金創藥', '', '', '']
    
