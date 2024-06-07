import os
from contextlib import redirect_stdout

from gFile import gFile
from tFile import tFile
from randomize_magic import randomize_magic, print_magic_lst
from randomize_shop import randomize_shop, print_price_lst
from randomize_item import randomize_item, print_item_lst
from gmon_0exp import gmon_0exp, print_exp_lst
from randomize_talk import randomize_talkitem, print_talkitem_lst, randomize_talk1_specific
from fix_luggage import fix_luggage
from randomize_synthesis import randomize_syn, print_syn_egg, print_syn_order

if __name__ == "__main__":    
    outpath = "./randomized_dat"
    os.makedirs(outpath, exist_ok=True)
    
    gfight1 = gFile("dat/GFight1.dat")
    # gfight2 = gFile("dat/GFight2.dat")
    # gfight3 = gFile("dat/GFight3.dat")
    # gfight4 = gFile("dat/GFight4.dat")
    # gmap = gFile("dat/gmap.dat")    
    ghero = gFile("dat/ghero.dat")
    gitem = gFile("dat/gitem.dat")
    glevel = gFile("dat/glevel.dat")
    gmagic = gFile("dat/gmagic.dat")    
    gmon = gFile("dat/gmon.dat")
    talk1 = tFile("dat/talk1.dat")
    talk2 = tFile("dat/talk2.dat")
    talk3 = tFile("dat/talk3.dat")
    talk4 = tFile("dat/talk4.dat")       
    talk8 = tFile("dat/talk8.dat")

    res_magic_lst = randomize_magic(glevel, gmagic, ghero, gfight1)
    with open(outpath + "/" + 'magic.txt', 'w') as f:
        with redirect_stdout(f):
            print_magic_lst(res_magic_lst)

    res_price_lst = randomize_shop(gmagic, gitem)
    with open(outpath + "/" + 'price.txt', 'w') as f:
        with redirect_stdout(f):
            print_price_lst(res_price_lst)

    res_item_lst = randomize_item(gmon)
    with open(outpath + "/" + 'item_gmon.txt', 'w') as f:
        with redirect_stdout(f):
            print_item_lst(res_item_lst)    

    res_exp_lst = gmon_0exp(gmon)

    res_talk_lst = []
    _ = [res_talk_lst.extend(randomize_talkitem(t, gmagic)) for t in [talk1, talk2, talk3, talk4, talk8]]

    with open(outpath + "/" + 'item_talk.txt', 'w') as f:
        with redirect_stdout(f):
            print_talkitem_lst(res_talk_lst)

    fix_luggage(gmagic, gitem, talk1)
    randomize_talk1_specific(talk1)

    syn_egg_lst, syn_order_lst = randomize_syn(gitem) 

    with open(outpath + "/" + 'item_syn.txt', 'w') as f:
        with redirect_stdout(f):    
            print_syn_egg(syn_egg_lst)
            print_syn_order(syn_order_lst)

    def name_helper(filename):        
        outname = outpath + "/" + os.path.split(filename)[1]
        return outname

    gfight1.export(name_helper(gfight1.filename))
    ghero.export(name_helper(ghero.filename))
    gmagic.export(name_helper(gmagic.filename))
    glevel.export(name_helper(glevel.filename))
    gitem.export(name_helper(gitem.filename))
    gmon.export(name_helper(gmon.filename))
    _ = [t.export(name_helper(t.filename)) for t in [talk1, talk2, talk3, talk4, talk8]]