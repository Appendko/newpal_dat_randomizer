import random
from collections import Counter
from common import magic_lst, user_lst, lvlup_lst
from gFile import gFile, cmp
magic_dict = dict(magic_lst)
user_dict = dict(user_lst)
lvlup_dict = dict(lvlup_lst)

bool_fix_steal = True
bool_hero_limit = True
bool_remove_consumption = True

hero_limit = {0x07D0:1,0x07D1:4,0x07D2:2,0x07D3:4,0x07D4:99,0x07D5:99,0x07D6:99,0x07D7:99,0x07D9:99,} # 其實只有靈兒需要
MaxLevel = 20
LevelUpRatio = 3

def create_magic_pool():
    magic_id_lst = [x[0] for x in magic_lst]
    global magic_pool        
    magic_pool = {
    0x07D0: magic_id_lst.copy(), 0x07D1: magic_id_lst.copy(), 0x07D2: magic_id_lst.copy(), # 逍遙 / 靈兒 / 月如
    0x07D3: magic_id_lst.copy(), 0x07D4: magic_id_lst.copy(), 0x07D9: magic_id_lst.copy(), # 阿奴 / 巫后 / 夢境逍遙    
    0x07D5: [], 0x07D6: [], 0x07D7: [], # 使徒蓋羅嬌# 苗女初號機# 苗女貳號機    
    }

    # 夢蛇
    for user in [0x07D0, 0x07D2, 0x07D3, 0x07D9]:        
        _ = magic_pool[user].remove(0x1B27)

    # 逍遙神劍 / 飛龍探雲手
    for user in [0x07D1, 0x07D2, 0x07D3, 0x07D4]:
        _ = magic_pool[user].remove(0x1905)        
        _ = magic_pool[user].remove(0x1906)
        _ = magic_pool[user].remove(0x186C)

    for user in magic_pool:
        random.shuffle(magic_pool[user])
    return

def magic_rand_helper(item, user, offset, length=0): # 0 for no restriction, 1 for same length
    magic_id = item.value(offset)
    global magic_pool    
    if length == 0:
        rand_id = magic_pool[user].pop()
    else: #length should be 
        if length == 1: #replace the same length
            length =  len(magic_dict[magic_id])
        item_lst_len = [item_id for item_id in magic_pool[user] if len(magic_dict[item_id]) == length]
        rand_id = random.choice(item_lst_len)
        magic_pool[user].remove(rand_id)

    item.arr[offset*4:offset*4+2] = rand_id.to_bytes(2,byteorder="little")
    return [magic_id, rand_id]

def magic_fixed_helper(item, user, offset, fixed_id):
    magic_id = item.value(offset)    
    global magic_pool
    magic_pool[user].remove(fixed_id)    
    item.arr[offset*4:offset*4+2] = fixed_id.to_bytes(2,byteorder="little")
    return [magic_id, fixed_id]

def magic_limit_helper(item, user):
    # magic_id = item.value(offset)
    # item.arr[offset*4:offset*4+2] = fixed_id.to_bytes(2,byteorder="little")
    # return [magic_id, fixed_id]
    global hero_last_eq
    item.arr[:] = hero_last_eq[user]
    return

# def randomize_magic_lvlup(glevel):
#     # address : 0x2B6F8 177912
#     #  01 10 20 7F DC 00 00 00 02 19 00 00  // 仙術 6402
#     # id_pattern = b"\x00\x10\x10\x7F"
#     res_lst = []    
#     type_pattern = b"\x01\x10\x20\x7F\xDC\x00\x00\x00"
#     for item in glevel.items:
#         gitem_id = item[0].value(1)        
#         item_learn_magic_lst = item.search_initial(type_pattern)
#         for item_learn_magic in item_learn_magic_lst:
#             user_id = lvlup_dict[gitem_id][0]            
#             magic_id, rand_id = magic_rand_helper(item_learn_magic, user_id, 2)  
#             username = user_dict[user_id]
#             # print("0x%06X, %s, 0x%04X, %s -> 0x%04X, %s"%(gitem_id, username, magic_id, magic_dict[magic_id], rand_id, magic_dict[rand_id]))
#             res_lst.append((gitem_id, username, magic_id, magic_dict[magic_id], rand_id, magic_dict[rand_id]))
#     return res_lst

def randomize_magic_lvlup(glevel, ghero, gmagic):
    # address : 0x2B6F8 177912
    #  01 10 20 7F DC 00 00 00 02 19 00 00  // 仙術 6402
    lvup_pattern = b'\x01\x10\x20\x7F\x05\x00\x00\x00'
    hero_lst = [0x7D0,0x7D1,0x7D2,0x7D3,0x7D4]
    cur_lv_hero = [ghero.search_id(x)[1].search_initial(lvup_pattern)[0].value(2) for x in hero_lst]
    lvup_amount_hero = [99-x for x in cur_lv_hero]
    lvup_cumsum_hero = [0] + [sum(lvup_amount_hero[0:i+1]) for i in range(len(lvup_amount_hero))]
    slice_hero = [slice(i,j) for i,j in zip(lvup_cumsum_hero[:-1], lvup_cumsum_hero[1:])]
    lvlup_lst = [x for x in glevel.items if x.str()=="升級%%"] # total: 410, (98+94+96+71+51)
    lvlup_lst_hero = [lvlup_lst[slice_i] for slice_i in slice_hero]

    res_lst = []
    for lvup_lst_i, hero_id in zip(lvlup_lst_hero, hero_lst):
        username = user_dict[hero_id]   
        for i, lvup_item in enumerate(lvup_lst_i):
            for lvup_gitem in lvup_item.search_dtype(0x7F201001):
                # 04最高可能修行 05修行  0A升級所需經驗值  0B當前經驗值 
                # 10最大體力 11體力 16最大真氣 17真氣 DC學習仙術 
                # 1D武術 23靈力 29防禦 2F身法 35吉運 
                # if lvup_gitem.value(1) in [0x1D, 0x23, 0x29, 0x2F, 0x35, 0x10, 0x16]: 
                #     if i < MaxLevel:
                #         cur_val = lvup_gitem.value(2)
                #         lvup_gitem.set_value(cur_val*5, 2)
                #     else:
                #         lvup_gitem.set_value(0, 2)
                if lvup_gitem.value(1) == 0x05 and i >= MaxLevel*LevelUpRatio:
                    lvup_gitem.set_value(0, 2)
                #elif lvup_gitem.value(1) == 0x0A:
                #    lvup_gitem.set_value(0x7FFF, 2, offset=4, signed=False)
                if lvup_gitem.value(1) == 0xDC:
                    lvup_gitem.set_value(0x0B, 1, offset=4, signed=False)
                    lvup_gitem.set_value(0x00, 2, offset=4, signed=False)
                elif lvup_gitem.value(1) == 0x0B and i < MaxLevel*LevelUpRatio and i%LevelUpRatio == 0:
                    lvup_gitem.set_value(0xDC, 1, offset=4, signed=False) # LEARN MAGIC       
                    _, rand_id = magic_rand_helper(lvup_gitem, hero_id, 2)                      
                    res_lst.append((i, username, 0, "", rand_id, magic_dict[rand_id]))

    # 金蠶王要改成一次升 LevelUpRatio 等                    
    gold_silkworm_effect_id = 0xFC6               
    item_lvup_pattern = b"\x0B\x20\x30\x7F\x01\x10\xFF\x7E\x05\x00\x00\x00"
    gmagic_item = gmagic.search_id(gold_silkworm_effect_id)[1]
    gmagic_gitem = gmagic_item.search_initial(item_lvup_pattern)[0]
    gmagic_gitem.set_value(LevelUpRatio, 3, offset=4, signed=False)                    

    # 取消掉劇情自動升級
    for magic_item in gmagic.items:
        lvup_gitem_lst = magic_item.search_initial(b"\x0B\x20\x30\x7F\xD1\x07") 
        lvup_gitem_lst += magic_item.search_initial(b"\x0B\x20\x30\x7F\xD2\x07")
        if lvup_gitem_lst:
            for lvup_gitem in lvup_gitem_lst:
                lvup_gitem.set_value(0x00, 3, offset=4, signed=False)

    return res_lst


def randomize_magic_learn(gmagic):
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
            magic_id, rand_id = magic_rand_helper(item_learn_magic, user_id, 2, 0)  
            username = user_dict[user_id]
            # print("0x%06X, %s, 0x%04X, %s -> 0x%04X, %s"%(gitem_id, username, magic_id, magic_dict[magic_id], rand_id, magic_dict[rand_id]))
            res_lst.append((gitem_id, username, magic_id, magic_dict[magic_id], rand_id, magic_dict[rand_id]))
    return res_lst

def randomize_magic_initial(ghero):
    # address : 0xAA0 2720
    #  00 10 10 7F D2 07 00 00  //  代號 D2 07 00
    #  01 10 20 7F DC 00 00 00 F6 1A 00 00  // 仙術 6902
    #  01 10 20 7F DC 00 00 00 CF 18 00 00  // 仙術 6351   
    res_lst = [] 
    id_pattern = b"\x00\x10\x10\x7F"
    type_pattern = b"\x01\x10\x20\x7F\xDC\x00\x00\x00"
    equip_pattern = b"\x01\x10\x20\x7F\xDD\x00\x00\x00"

    # user's last equipment
    global hero_last_eq
    hero_last_eq = {}
    for user_id in [0x07D0,0x07D1,0x07D2,0x07D3,0x07D4,0x07D9]:
        last_eq = ghero.search_id(user_id)[1].search_initial(equip_pattern)[-1].arr.tobytes()
        hero_last_eq[user_id] = last_eq

    hero_skills = Counter()
    last_learn = dict()
    for item in ghero.items:
        user_id = item[0].value(1)
        item_learn_magic_lst = item.search_initial(type_pattern)
        for item_learn_magic in item_learn_magic_lst:
            if bool_fix_steal and user_id == 0x07D0 and item_learn_magic.value(2) == 0x1AF5: #0x1AF5 氣療術
                magic_id, rand_id = magic_fixed_helper(item_learn_magic, user_id, 2, 0x186C) #固定 0x186C 飛龍探雲手 
                hero_skills[user_id] += 1
            elif bool_hero_limit and hero_skills[user_id] >= hero_limit[user_id]:
                magic_limit_helper(item_learn_magic, user_id) # 用裝備覆蓋這行
                continue
            else:                
                magic_id, rand_id = magic_rand_helper(item_learn_magic, user_id, 2)  
                hero_skills[user_id] += 1
                last_learn[user_id] = rand_id
            username = user_dict[user_id]
            #print("0x%06X, %s, 0x%04X, %s -> 0x%04X, %s"%(user_id, username, magic_id, magic_dict[magic_id], rand_id, magic_dict[rand_id]))
            res_lst.append((user_id, username, magic_id, magic_dict[magic_id], rand_id, magic_dict[rand_id]))
    return res_lst

def print_magic_lst(res_magic_lst):
    for tup in res_magic_lst:
        print("0x%06X, %s, 0x%04X, %s -> 0x%04X, %s"%tup)
    return 

def remove_magic_consumption(gmagic, gfight1):
    item_consumption = b"\x01\x00\x20\x7F\x02"
    worm = b'\x11\x0E'
    for str_i in ["爆炸蠱%%", "三屍咒%%", "萬蠱蝕天%%"]:
        bomb_item = [x for x in gmagic if x.str()==str_i][0]
        bomb_script_id = bomb_item.search_initial(item_consumption)[0].value(2)
        consume_worm_gitem = [x for x in gfight1.search_id(bomb_script_id)[1].items if bytes(x.arr).find(worm)!=-1][0]
        # 41 20 20 7F 11 0E 00 00 FF FF FF FF
        # print(consume_worm_gitem)
        consume_worm_gitem.set_value(0, 2, 4)

    return

def randomize_magic(glevel, gmagic, ghero, gfight1):
    create_magic_pool()  
    if bool_remove_consumption:
        remove_magic_consumption(gmagic, gfight1)
    res_magic_lst = []      
    res_magic_lst.extend(randomize_magic_initial(ghero))
    res_magic_lst.extend(randomize_magic_lvlup(glevel, ghero, gmagic))
    res_magic_lst.extend(randomize_magic_learn(gmagic))
    return res_magic_lst



if __name__ == "__main__":    
    ghero = gFile("dat/ghero.dat")
    glevel = gFile("dat/glevel.dat")
    gmagic = gFile("dat/gmagic.dat")
    gfight1 = gFile("dat/GFight1.dat")    
    res_magic_lst = randomize_magic(glevel, gmagic, ghero, gfight1)
    print_magic_lst(res_magic_lst)

    gmagic.export(gmagic.filename+".randomized")
    glevel.export(glevel.filename+".randomized")    
    ghero.export(ghero.filename+".randomized")    