import random
from common import item_lst, shop_params, egg_lst
from gFile import gFile, cmp
item_dict = dict(item_lst)

bool_fix_worm = True #固定 苗疆蠱店 蠱 -> 傀儡蟲
bool_fix_wood = True #固定 十年前木匠店 木劍 -> 木劍
bool_fix_gold = True #固定 金蠶王

# def shop_item(ind):
def shop_item(gmagic_item):       
    shop_item_lst = []
    for item in gmagic_item:
        if cmp(item.dtype, 0x7F102042):
            # obj_id = int.from_bytes(item.arr[4:6], byteorder="little")
            obj_id = item.value(1, offset=2, signed=False) 
            obj_loc = item.loc
            shop_item_lst.append(obj_id)
    return shop_item_lst

def shop_analyzer(gmagic):
    global dict_shop
    dict_shop = {}
    for i, gmagic_item in enumerate(gmagic.items):
        shop_item_lst = shop_item(gmagic_item)
        if shop_item_lst:
            dict_shop[i] = shop_item_lst
    
    # Remove Singlets: They are not real shops....
    for x in list(dict_shop.keys()):
        if len(dict_shop[x]) == 1:
            dict_shop.pop(x)
    return dict_shop

def print_shop(i):
    global dict_shop
    print("%d"%i, "0x%04X"%gmagic[i].loc, [item_dict[item] for item in dict_shop[i]])        
    return

def print_all_shop():
    global avail_shop
    for i in avail_shop:
        print_shop(i)
    return

"""
576 餘杭藥鋪       ['雄黃', '止血草', '還神丹', '還魂香', '十里香', '驅魔香']
577 餘杭鐵匠鋪     ['短刀', '護肩', '披風', '鐵履', '護腕', '鐵護腕']
578 餘杭木匠鋪     ['木劍', '籐甲', '木鞋', '草鞋', '皮帽', '髮飾']
580 蘇州藥鋪       ['雄黃', '止血草', '行軍丹', '金創藥', '還神丹', '還魂香', '十里香', '驅魔香']
581 蘇州武器店     ['籐甲', '鐵鎖衣', '武士披風', '長劍', '大刀', '越女劍', '芙蓉刀', '鐵履', '鐵護腕']
582 蘇州小吃攤     ['燒肉', '酒', '茶葉蛋', '水果', '糯米糕']
583 蘇州首飾攤     ['銀釵', '髮飾', '翠玉金釵', '鏽花鞋', '銀針', '銅鏡', '玉鐲', '香袋']
585 白河村藥鋪     ['雄黃', '止血草', '行軍丹', '還神丹', '還魂香', '九節菖蒲', '蜂王蜜', '十里香', '驅魔香']
586 白河村藥鋪     ['護心鏡', '鐵鎖衣', '柳月刀', '紅纓刀', '梅花鏢', '武僧靴', '天師符', '觀音符', '金剛符']
588 白河村藥鋪     ['雄黃酒', '九節菖蒲', '還魂香', '靈山仙芝', '龍涎草', '金創藥', '紫菁玉蓉膏']
589 揚州城藥鋪     ['九截鞭', '玄鐵劍', '青銅甲', '鐵鱗甲', '護心鏡', '武僧靴', '鹿皮靴', '翠玉金釵']
590 揚州城藥鋪     ['酒', '雄黃酒', '水果', '燒肉', '醃肉', '糯米糕']
591 揚州城藥鋪     ['九節菖蒲', '驅魔香', '九陰散', '天香續命露', '贖魂燈', '紫菁玉蓉膏', '金創藥', '雪蓮子', '天仙玉露', '十里香', '驅魔香']
592 長安城藥鋪     ['銀針', '透骨釘', '袖裡劍', '雷火珠', '毒龍砂', '吸星鎖', '無影神針', '血玲瓏', '引路蜂', '酒']
593 長安城藥鋪     ['風靈符', '雷靈符', '水靈符', '火靈符', '土靈符', '天師符', '金剛符', '土遁符', '騰雲符', '觀音符', '淨衣符', '靈心符']
594 長安城藥鋪     ['金童劍', '玉女劍', '龍泉劍', '金蛇鞭', '精鐵戰甲', '金縷衣', '鹿皮靴', '疾風靴', '霓虹羽衣']
595 苗疆藥鋪       ['沖天冠', '鬼針胄', '蓮花靴', '龍鱗靴', '鳳紋披風', '乾坤鏡', '雷火珠', '綑仙繩']
596 苗疆藥鋪       ['蠱', '金蠶王', '食妖蟲', '碧血蠶', '蜂王蜜', '驅魔香', '十里香', '贖魂燈', '毒龍砂']
597 苗疆藥鋪       ['九節菖蒲', '金創藥', '紫菁玉蓉膏', '靈山仙芝', '雪蓮子', '蜂王蜜', '靈葫仙丹', '驅魔香', '十里香', '九陰散']
598 夢境餘杭鐵匠鋪 ['短刀', '護肩', '披風', '鐵履', '護腕', '鐵護腕']
599 夢境餘杭木匠鋪 ['木劍', '籐甲', '木鞋', '草鞋', '皮帽', '髮飾']
600 苗疆藥鋪       ['鬼頭杖', '苗刀', '鬼牙刀', '天蠶寶衣', '天蠶絲帶', '虎皮靴', '豹牙手環', '血玲瓏', '無影神針']
"""

def price_analyzer(gitem):
    import itertools
    item_pattern = 0x7F100000
    gitem_items = [item for item in gitem.items if cmp(item[0].dtype, item_pattern)]

    type_pattern = b'\x01\x00\x20\x7F\x08'
    keyfunc = lambda x: x.search_initial(type_pattern)[0].value(2)
    data = sorted(gitem_items, key=keyfunc)
    groups = []
    uniquekeys = []
    for key, values in itertools.groupby(data, keyfunc):
        if key > 3:
            pass # break
        if key % 2 == 1:
            pass # continue
        # print(key)
        for item in values:
            type_pattern = b'\x01\x00\x20\x7F\x09'
            price_gitem = item.search_initial(type_pattern)[0]
            price = price_gitem.value(2, offset=2, signed=False)
            print("(0x%04X, \"%s\", %d),"%(item[0].value(1), item.name(),price))
    return

"""
    type0 = [
            (0x0E20, "三屍蠱"), (0x0E21, "鶴頂紅"), (0x0E22, "孔雀膽"), (0x0E23, "血海棠"), (0x0E24, "斷腸草"),
            (0x0E25, "金蠶蠱"), (0x0E26, "無影毒"), (0x0E2A, "隱蠱"),   (0x0F3E, "傀儡蟲"), (0x0F41, "紫金葫蘆"),
            (0x0F42, "煉蠱皿"), (0x0F70, "八仙石"), (0x0F71, "銀杏子"), (0x0F72, "玉菩提"), (0x0F73, "試煉果"),
            (0x0F74, "舍利子"), (0x0F75, "女媧石"), (0x0F76, "雪蛤蟆"), (0x1070, "鬼枯籐"), (0x10D2, "靈蠱"),
            (0x1139, "赤血蠶"),
            ]
    
    type2 = [
            (0x0E12, "屍腐肉"), (0x0E13, "腹蛇涎"), (0x0E14, "纏魂絲"), (0x0E15, "冰蠶蠱"), (0x0E16, "火蠶蠱"),
            (0x0E17, "忘魂花"), (0x0E18, "紫罌粟"), (0x0E1B, "醍醐香"), (0x0E1C, "迷魂香"), (0x0E1D, "蜂巢"),
            (0x0E1E, "幻蠱"),   (0x0E1F, "爆烈蠱"),
            ]
"""

def randomize_shop(gmagic, gitem):
    dict_shop = shop_analyzer(gmagic)
    avail_shop = list(shop_params.keys())

    def item_lst_remove_egg():
        res_lst = item_lst.copy()
        [res_lst.remove(item) for item in egg_lst]
        return res_lst
    avail_item_lst = item_lst_remove_egg()

    def rand_helper():
        rand_item = random.choice(avail_item_lst)[0] 
        return rand_item

    def item_rand_helper(item):
        item_loc = item.loc + 4
        #item_id = int.from_bytes(item.arr[4:6], byteorder="little")
        item_id = item.value(1, offset=2, signed=False)
        rand_id = rand_helper()

        # Overwrite by Rules
        if bool_fix_worm and item_loc == 0x0000AA39:
            rand_id = 0x0F3E # 蠱 -> 傀儡蟲
        elif bool_fix_wood and item_loc == 0x0000AB25:
            rand_id = 0x0D7B # 木劍 -> 木劍
        elif bool_fix_gold: # 金蠶王
            # 0xA4E5 餘杭藥鋪 雄黃   # 0xA5AD 蘇州藥鋪 雄黃    # 0xA6E1 白河藥鋪 雄黃
            # 0xA79D 揚州藥鋪 雄黃酒 # 0xA869 長安藥鋪 九節菖蒲 # 0xAA89 苗疆藥鋪 九節菖蒲
            if item_loc in [0xA5B1, 0xA6E5, 0xA7A1, 0xA86D, 0xAA8D]:
                rand_id = 0x0F77
        # item.arr[4:6] = rand_id.to_bytes(2,byteorder="little")
        item.set_value(rand_id, 1, offset=2, signed=False)
        return [item_loc, item_id, rand_id]
    
    def price_randomizer(rand_id, Nmax, Nmin):
        rand_item = gitem.search_id(rand_id)[1]
        # price
        type_pattern = b'\x01\x00\x20\x7F\x09'
        rand_gitem = rand_item.search_initial(type_pattern)[0]
        rand_price = random.randint(Nmin, Nmax)
        #rand_gitem.arr[8:10] = rand_price.to_bytes(2,byteorder="little")
        rand_gitem.set_value(rand_price, 2, offset=2, signed=False)

        # sellable or not
        type_pattern = b'\x01\x00\x20\x7F\x08'
        rand_gitem = rand_item.search_initial(type_pattern)[0]
        int_sellable = rand_gitem.value(2)
        if int_sellable%2 == 0:           
            int_sellable += 1
            # rand_gitem.arr[8:10] = int_sellable.to_bytes(2,byteorder="little")
            rand_gitem.set_value(int_sellable, 2, offset=2, signed=False)
        return rand_price

    item_pool = item_dict.copy()
    if bool_fix_gold:
        def item_pool_remove_gold_silkworm(): #[0x0F77, '金蠶王']
            avail_item_lst.remove([0x0F77, '金蠶王'])
            item_pool.pop(0x0F77)
            price_randomizer(0x0F77, 65535, 65535)
            return 
        item_pool_remove_gold_silkworm()

    total_item_lst = []
    for shop_i in avail_shop:
        # [0xA4DD, "餘杭藥鋪"      ,  3000,   748,  1000,  200]
        _, shop_name, _, _, Nmax, Nmin = shop_params[shop_i]
        # item_id_loc_lst = dict_shop[shop_i]
        for item in gmagic[shop_i]:
            if cmp(item.dtype, 0x7F102042):
                [item_loc, item_id, rand_id] = item_rand_helper(item)
                if rand_id in item_pool:
                    rand_price = price_randomizer(rand_id, Nmax, Nmin)
                    rand_item_name = item_pool.pop(rand_id)
                    total_item_lst.append((shop_name, rand_id, rand_item_name, rand_price))

    # Those we can't buy it: price shouldn't be that high
    Nmax, Nmin = 1000, 200
    for item_id in list(item_pool.keys()):
        rand_price = price_randomizer(item_id, Nmax, Nmin)
        item_name = item_pool.pop(item_id)        
        total_item_lst.append(("N/A", item_id, item_name, rand_price))

    return total_item_lst   

def print_price_lst(total_price_lst):
    for tup in total_price_lst:
        print("%s, 0x%04X, %s, %d"%tup)
    return

if __name__ == "__main__":
    gitem = gFile("dat/gitem.dat")
    gmagic = gFile("dat/gmagic.dat")
    price_lst = randomize_shop(gmagic, gitem)
    print_price_lst(price_lst)
    gmagic.export(gmagic.filename+".randomized")
    gitem.export(gitem.filename+".randomized")

