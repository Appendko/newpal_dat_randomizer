import random
from common import item_lst
from gFile import gFile, cmp
item_dict = dict(item_lst)
gmon_item_lst = item_lst.copy()
gmon_item_lst.remove([0x0F77, "金蠶王"])

bool_fix_fox = True
def fix_fox(gmon):
    # ## 不管怎麼樣總之先修正狐妖 選擇ric版數據
    # 00 10 10 7F 3A 06 00 00  //  代號 3A 06 00 00 
    # 00 F0 F2 7F  //  string 小狐狸精%%    
    # 01 10 20 7f ce 00 00 00 01 00 00 00 -> 17 0E   [0x0E17, "忘魂花"],
    # 01 10 20 7f cd 00 00 00 17 0e 00 00 -> 01 00
    # 01 10 20 7f d1 00 00 00 02 00 00 00 -> 17 0E   [0x0E17, "忘魂花"],
    # 01 10 20 7f d0 00 00 00 00 00 00 00 -> 01 00    
    fox = gmon.search_id(0x0000063A)[1]
    base_pattern = b"\x01\x10\x20\x7F"
    item1_pattern = b"\xCE\x00", b"\xCD\x00", b"\xCC\x00"
    item2_pattern = b"\xD1\x00", b"\xD0\x00", b"\xCF\x00"
    fox.search_initial(base_pattern+item1_pattern[0])[0].arr[8:10] = b"\x17\x0E"
    fox.search_initial(base_pattern+item1_pattern[1])[0].arr[8:10] = b"\x01\x00"
    fox.search_initial(base_pattern+item2_pattern[0])[0].arr[8:10] = b"\x17\x0E"
    fox.search_initial(base_pattern+item2_pattern[1])[0].arr[8:10] = b"\x01\x00"
    return

def item_rand_helper(item_type, item_num, offset):
    item_id = item_type.value(offset)
    item_amount = item_num.value(offset)
    rand_id = random.choice(gmon_item_lst)[0]
    rand_amount = random.randint(1,3)
    item_type.arr[offset*4:offset*4+2] = rand_id.to_bytes(2,byteorder="little")
    item_num.arr[offset*4:offset*4+2] = rand_amount.to_bytes(2,byteorder="little")
    return [item_id, item_amount, rand_id, rand_amount]

# def item_fixed_helper(item, offset, fixed_id):
#     item_id = item.value(offset)    
#     item.arr[offset*4:offset*4+2] = fixed_id.to_bytes(2,byteorder="little")
#     return [item_id, fixed_id]

def randomize_item_gmon(gmon):
    #  01 10 20 7F BE 00 00 00 26 02 00 00  // 獲得經驗 550
    #  01 10 20 7F C9 00 00 00 00 00 00 00  //  data        
    #  01 10 20 7F CA 00 00 00 00 00 00 00  //  data    
    #  01 10 20 7F CB 00 00 00 E8 03 00 00  // 偷竊金錢 1000
    #  01 10 20 7F CC 00 00 00 00 00 00 00  //  data
    #  01 10 20 7F CD 00 00 00 01 00 00 00  // 物品1數量 1    
    #  01 10 20 7F CE 00 00 00 46 0E 00 00  // 偷竊物品1 3654
    #  01 10 20 7F CF 00 00 00 00 00 00 00  //  data    
    #  01 10 20 7F D0 00 00 00 01 00 00 00  // 物品2數量 1
    #  01 10 20 7F D1 00 00 00 14 0E 00 00  // 偷竊物品2 3604
    #  01 10 20 7F D2 00 00 00 00 00 00 00  //  data
    #  01 10 20 7F D3 00 00 00 01 00 00 00  // 不能偷竊物品數量 1
    #  01 10 20 7F D4 00 00 00 4F 0E 00 00  // 不能偷竊物品 3663    
    # [money: C9,CA,CB] [item1: CC,CD,CE] [item2: CF,D0,D1] [item13 D2,D3,D4]

    type_pattern = b"\x00\x10\x10\x7F"
    res_lst = []    
    base_pattern = b"\x01\x10\x20\x7F"
    mone0_pattern = b"\xCB\x00", b"\xCA\x00", b"\xC9\x00"
    item1_pattern = b"\xCE\x00", b"\xCD\x00", b"\xCC\x00"
    item2_pattern = b"\xD1\x00", b"\xD0\x00", b"\xCF\x00"
    item3_pattern = b"\xD4\x00", b"\xD3\x00", b"\xD2\x00"

    def item_helper(pattern):
        type_item, num_item, dummy_item = None, None, None
        lst_item = item.search_initial(base_pattern+pattern[0])
        if lst_item:
            type_item = lst_item[0] # amount of money if used for steal_money
            num_item = item.search_initial(base_pattern+pattern[1])[0]
            dummy_item =  item.search_initial(base_pattern+pattern[2])[0]
        return type_item, num_item, dummy_item
    
    def itemlst_rand_helper(itemlst, pattern):
        itemlst[0].arr[4:6] = pattern[0]
        itemlst[1].arr[4:6] = pattern[1]
        itemlst[2].arr[4:6] = pattern[2]
        [item_id, item_amount, rand_id, rand_amount] = item_rand_helper(itemlst[0], itemlst[1], 2)
        return (item_id, item_amount, rand_id, rand_amount)

    res_lst = []
    for item in gmon.items:
        gmon_item_id = item[0].value(1)        
        gmon_item_name = item.str()

        money  = item_helper(mone0_pattern)
        steal1 = item_helper(item1_pattern)
        steal2 = item_helper(item2_pattern)
        drop   = item_helper(item3_pattern)

        mon_item_lst = []
        if money[0] != None:
            if steal1[0] == None:
                mon_item_lst.append(itemlst_rand_helper(money, item1_pattern))
            elif steal2[0] == None:
                mon_item_lst.append(itemlst_rand_helper(money, item2_pattern))
        if steal1[0] != None:
            mon_item_lst.append(itemlst_rand_helper(steal1, item1_pattern))
        if steal2[0] != None:
            mon_item_lst.append(itemlst_rand_helper(steal2, item2_pattern))
        if drop[0] != None:
            mon_item_lst.append(itemlst_rand_helper(drop, item3_pattern))
        res_lst.append((gmon_item_id, gmon_item_name, mon_item_lst))
    return res_lst

def print_item_lst(res_item_lst):
    for gmon_item_id, gmon_item_name, mon_item_lst in res_item_lst:
        for tup in mon_item_lst:
            item_id, item_amount, rand_id, rand_amount = tup
            if item_amount == 0:
                item_name, item_amount = "金錢", item_id
            else:
                item_name = item_dict[item_id]
            rand_name = item_dict[rand_id]
            tup_print = (gmon_item_id, gmon_item_name, item_name, item_amount, rand_name, rand_amount)
            print("0x%06X, %s, %s, %d -> %s, %d"%tup_print)
    return 
        
def randomize_item(gmon):
    res_item_lst = []      
    fix_fox(gmon)
    res_item_lst.extend(randomize_item_gmon(gmon))
    return res_item_lst

if __name__ == "__main__":    
    gmon = gFile("dat/gmon.dat")
    fix_fox(gmon)
    res_item_lst = randomize_item(gmon)
    print_item_lst(res_item_lst)
    gmon.export(gmon.filename+".randomized")    