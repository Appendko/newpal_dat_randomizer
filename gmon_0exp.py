import random
from common import item_lst
from gFile import gFile, cmp

def gmon_0exp(gmon):
    res_lst = []     
    exp_pattern = b"\x01\x10\x20\x7F\xBE"
    res_lst = []
    for item in gmon.items:
        gmon_item_id = item[0].value(1)        
        gmon_item_name = item.str()
        lst_exp = item.search_initial(exp_pattern)
        if lst_exp:
            orig_exp = lst_exp[0].value(2)
            lst_exp[0].arr[8:10] = b"\x00\x00"
        res_lst.append((gmon_item_id, gmon_item_name, orig_exp, 0))
    return res_lst

def print_exp_lst(res_exp_lst):
    for gmon_item_id, gmon_item_name, orig_exp, curr_exp in res_exp_lst:
        tup = gmon_item_id, gmon_item_name, orig_exp, curr_exp
        print("0x%06X, %s, %d -> %d"%tup)
    return 
     
if __name__ == "__main__":    
    gmon = gFile("dat/gmon.dat")
    res_exp_lst = gmon_0exp(gmon)
    print_exp_lst(res_exp_lst)
    gmon.export(gmon.filename+".randomized")    