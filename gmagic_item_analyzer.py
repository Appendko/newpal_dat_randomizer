#Python Script to randomize talk8.dat
#Author: Append Huang (append@gmail.com)
#Reference: https://www.ptt.cc/bbs/pal/M.1461154467.A.F26.html
#Reference: https://goo.gl/VypRfq

#read binary file as bytearray to make modification

import random
from common import item_lst, full_item_lst
from gFile import gFile

item_dict = dict(item_lst)
full_item_dict = dict(full_item_lst)

def test_gmagic(gmagic):
    res_lst = []
    for magic_script in gmagic.items:
        magic_id = magic_script[0].value(1)
        magic_gitem_lst = magic_script.search_dtype(0x7F202041)
        for magic_gitem in magic_gitem_lst:
            item_id = magic_gitem.value(1)
            if item_id in item_dict:
                item_name = item_dict[item_id]
                item_num = int.from_bytes(magic_gitem[8:12], byteorder="little",signed=True)
                res_lst.append((magic_id, item_name, item_num))
    return res_lst

if __name__ == "__main__":
    gmagic = gFile("dat/gmagic.dat")    
                
