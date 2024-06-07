#Python Script to randomize talk8.dat
#Author: Append Huang (append@gmail.com)
#Reference: https://www.ptt.cc/bbs/pal/M.1461154467.A.F26.html
#Reference: https://goo.gl/VypRfq

#read binary file as bytearray to make modification
import os, operator
import random
from common import item_lst, egg_lst
# from tFile import tFile
from gFile import gFile
item_dict = dict(item_lst)

def randomize_syn_egg(gitem):
    syn_item = gitem.search_id(0x012FD1)[1] #煉蠱規則ID
    synegg_gitem_lst = syn_item.search_dtype(0x7F20204F)

    def item_lst_remove_egg():
        res_lst = item_lst.copy()
        [res_lst.remove(item) for item in egg_lst]
        return res_lst
    avail_item_lst = item_lst_remove_egg()

    def item_rand_helper(item, offset=2):
        item_id = item.value(offset)
        rand_id = random.choice(avail_item_lst)[0]
        item.set_value(rand_id, offset)
        return [item.loc, item_id, rand_id]
    res_lst = []
    for synegg_gitem in synegg_gitem_lst:
        [item_loc, item_id, rand_id] = item_rand_helper(synegg_gitem)
        item_name = item_dict[item_id] + "卵"
        rand_name = item_dict[rand_id] + "卵"
        res_lst.append((item_loc, item_name, rand_name))
    return res_lst

def randomize_syn_order(gitem):
    syn_item = gitem.search_id(0x012FD1)[1] #煉蠱規則ID
    synorder_gitem_lst = syn_item.search_dtype(0x7F40204D)

    fix_item = [0x0F3D, 0x0F3E, 0x0F3F, 0x0F40, 0x0F77]
    # gold_index = [i for i,x in enumerate(synorder_gitem_lst) if x.value(2) == 0x0F77][0]
    # gold_gitem = synorder_gitem_lst.pop(gold_index)
    fix_gitem_lst = [x for x in synorder_gitem_lst if x.value(2) in fix_item]    
    for fix_item in fix_gitem_lst:
        _ = synorder_gitem_lst.remove(fix_item)



    synorder_id_lst = [x.value(2) for x in synorder_gitem_lst]
    fix_id_lst = [x.value(2) for x in fix_gitem_lst]
    random.shuffle(synorder_id_lst)
    #synorder_gitem_lst = [gold_gitem] + synorder_gitem_lst
    synorder_gitem_lst = fix_gitem_lst + synorder_gitem_lst
    synorder_id_lst = fix_id_lst + synorder_id_lst

    res_lst = []
    for x, rand_id in zip(synorder_gitem_lst, synorder_id_lst):
        item_loc = x.loc
        item_id = x.value(2)
        item_type = x.value(1)
        item_rank = x.value(3)
        item_level = x.value(4)
        x.set_value(rand_id, 2)
        res_lst.append([item_loc, item_type, item_rank, item_level, item_id, rand_id])
    res_lst = sorted(res_lst, key=operator.itemgetter(1, 2, 3))
    return res_lst

def print_syn_order(synorder_lst):
    item_type_dict = {0: "生命", 1: "真氣", 2: "雙補", 3: "復活", 
                      4: "解毒", 5: "能力", 6: "引路蜂", 7: "傀儡蟲", 
                      8: "十里香", 9: "驅魔香", 10: "毒蠱"} 

    for res_i in synorder_lst:
        item_loc, item_type, item_rank, item_level, item_id, rand_id = res_i
        item_name = item_dict[item_id]
        rand_name = item_dict[rand_id]
        item_type_name = item_type_dict[item_type]
        tup = (item_loc, item_type_name, item_rank, item_level, item_name, rand_name)
        print("0x%04X, %s, % 2d, % 2d, %s -> %s"%tup)

    return

def print_syn_egg(res_lst):
    for tup in res_lst:
        print("0x%04X, %s -> %s"%tup)

    return

def randomize_syn(gitem):
    syn_egg_lst = randomize_syn_egg(gitem)
    syn_order_lst = randomize_syn_order(gitem)
    return syn_egg_lst, syn_order_lst

if __name__ == "__main__":   
    gitem = gFile("dat/gitem.dat")
    syn_egg_lst, syn_order_lst = randomize_syn(gitem) 
    print_syn_egg(syn_egg_lst)
    print_syn_order(syn_order_lst)
