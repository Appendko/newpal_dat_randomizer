#Python Script to read g*.dat
#Author: Append Huang (append@gmail.com)
#Reference: https://www.ptt.cc/bbs/pal/M.1461154467.A.F26.html
#Reference: https://goo.gl/VypRfq

def cmp(obj1, obj2):
    if type(obj1) == int:
        num1 = obj1
    else: 
        num1 = int.from_bytes(obj1, byteorder="little")

    if type(obj2) == int:
        num2 = obj2
    else: 
        num2 = int.from_bytes(obj2, byteorder="little")
    return ( num1 == num2 )

#read binary file as bytearray to make modification
class Item():
    def __init__(self, loc, arr, callback=None):
        self.loc, self.len, self.arr = loc, len(arr), arr
        self.items = None
        if callback:
            self.items = callback(loc,arr)
    def __repr__(self):
        if self.items:
            return "<0x%08X, %d, %s>"%(self.loc, self.len, self.items)
        else:
            return "<0x%08X, %d, %s>"%(self.loc, self.len, "".join(["\\x%02X"%x for x in self.arr]))
    def __getitem__(self, key):
        if self.items:
            return self.items[key]
        else:
            return self.arr[key]

    def str(self):
        if type(self.items)==list:
            items_str = [x.str() for x in self.items if cmp(x.dtype, 0x7FF2F000)]
            if items_str:
                if len(items_str) == 1:
                    return items_str[0]
                else:
                    return items_str
        return None

    def name(self):
        name = self.str()
        if type(name) == str:
            return name.replace("%","")
        else:
            return None
        
    def search_dtype(self, dtype):
        res_lst = []
        for gitem in self.items:
            if cmp(gitem.dtype, dtype):
                res_lst.append(gitem)
        return res_lst

    def search_initial(self, initial):
        res_lst = []
        for gitem in self.items:
            if len(gitem.arr) >= len(initial):
                if cmp(gitem.arr[:len(initial)], initial):
                    res_lst.append(gitem)
        return res_lst


class gItem(Item):
    def __init__(self, loc, arr, callback=None):
        super().__init__(loc, arr, callback)
        self.dtype = self.recog_item()

    def value(self, index, offset=4, signed=False):
        return int.from_bytes(self.arr[index*4:index*4+offset], byteorder="little", signed=signed)

    def set_value(self, value, index, offset=4, signed=False):
        if type(value) == int:
            self.arr[index*4:index*4+offset] = value.to_bytes(offset, byteorder="little", signed=signed)
        elif type(value) == bytearray or type(value) == bytes:
            self.arr[index*4:index*4+offset] = value
        else: # not-recognized? 
            self.arr[index*4:index*4+offset] = value        
        return

    def str(self):
        if cmp(self.dtype, 0x7FF2F000):
            return bytes(self.arr[4:]).decode(encoding="big5", errors="ignore")
        elif type(self.items)==list:
            items_str = [x.str() for x in self.items() if cmp(self.dtype, 0x7FF2F000)]
            return items_str
        else:
            return None
    
    def recog_item(self):
        if self.arr[3] == 0x7f:
            return memoryview(self.arr)[:4]
        else:
            return None
        
    def __setitem__(self, key, value):
        if self.items:
            raise Exception("__setitem__ for gItem() should be used only if it has no child in self.items.")
        else:
            if type(value) == int:
                if value < 65536:
                    self.arr[key:key+2] = value.to_bytes(2,byteorder="little")
                else: 
                    self.arr[key:key+4] = value.to_bytes(4,byteorder="little")                    
            elif type(value) == str:
                bytes_value = value.encode(encoding="big5", errors="ignore")
                self.arr[key:key+len(bytes_value)] = bytes_value
            elif type(value) == bytearray or type(value) == bytes:
                self.arr[key:key+len(value)] = value
            else: # not-recognized? 
                self.arr[key:key+len(value)] = value
            return        
        
class gFile():
    def __init__(self, filename):
        self.filename = filename
        self.items = []        
        self.read(self.filename)

    def __getitem__(self, key):
        return self.items[key]
    
    def search_id(self, item_id):
        for i, item in enumerate(self.items):
            if cmp(item[0].value(1), item_id): #All Item -> check First gItem-> 1st value (0th should be dtype)
                return i, self.items[i]
        return None    

    def read(self, filename):
        with open(filename,"rb") as f:
            self.file_content = bytearray(f.read()) 
        self.parse_block()

    def parse_block(self):
        header = memoryview(self.file_content)[:0x200]
        self.header = Item(0, header, None) #
        #begin from 0x200, read every 4 bytes:
        i_begin = 0x200
        i = i_begin
        while i <= len(self.file_content):        
            if self.file_content[i:i+4] == b'\xFF\xFF\x00\x7F': # End of block
                i += 4
                block = memoryview(self.file_content)[i_begin:i]                
                self.items.append(Item(i_begin, block, self.parse_blockitem))
                i_begin = i
            else:
                i += 1                
        i = len(self.file_content)
        if i > i_begin:
            block = memoryview(self.file_content)[i_begin:i]
            self.items.append(Item(i_begin, block, self.parse_blockitem))
    
    @staticmethod
    def parse_blockitem(offset, block):
        items = []
        begin_item = 0
        i = begin_item

        def block_item_helper(begin_item, i):
            block_item = memoryview(block)[begin_item:i]
            items.append(gItem(offset + begin_item, block_item, None))
            next_begin_item = i
            next_i = i + 4
            return next_begin_item, next_i

        while i < len(block) - 4:
            if block[i:i+3] == b'\x00\xF0\xF2\x7F': #string
                j = i
                while j < len(block):
                    if block[j:j+1] == b'\x25\x25': # strings end
                        i = j + 2
                        break
                    j += 1                        

            elif block[i+3] == 0x7F:
                # begin of an item
                if begin_item < i and (i-begin_item)%2==0:
                    begin_item, i = block_item_helper(begin_item, i)
                else: i += 1

            else:
                i += 1

        if begin_item < i:
            begin_item, i = block_item_helper(begin_item, i)
            i += 4
            begin_item, i = block_item_helper(begin_item, i)
        return items

    def export(self, filename, file_content=None):
        if file_content == None:
            file_content = self.file_content
        with open(filename,"wb") as f:
            f.write(bytes(file_content))

if __name__ == "__main__":
    from glob import glob
    import os
    items = [
        "dat/GFight1.dat", "dat/GFight2.dat", "dat/GFight3.dat", "dat/GFight4.dat",
        "dat/GeIndex.dat", "dat/ghero.dat", "dat/gitem.dat", "dat/glevel.dat", "dat/gmagic.dat",
        "dat/gmap.dat", "dat/gmon.dat",
        ]

    gfight1 = gFile("dat/GFight1.dat")
    gfight2 = gFile("dat/GFight2.dat")
    gfight3 = gFile("dat/GFight3.dat")
    gfight4 = gFile("dat/GFight4.dat")
    ghero = gFile("dat/ghero.dat")
    gitem = gFile("dat/gitem.dat")
    glevel = gFile("dat/glevel.dat")
    gmagic = gFile("dat/gmagic.dat")
    gmap = gFile("dat/gmap.dat")
    gmon = gFile("dat/gmon.dat")

    def gFileCheck(gfile):
        print(gfile.filename)
        next_loc1 = 0x200
        next_loc2 = 0x200
        for item1 in gfile.items:
            if item1.loc - next_loc1 != 0:
                print(item1.loc, next_loc1, item1.loc-next_loc1)
            next_loc1 += item1.len            
            for item2 in item1.items:
                if item2.loc - next_loc2 != 0:
                    print(item2.loc, next_loc2, item2.loc-next_loc2)
                next_loc2 += item2.len
        return

    for gfile in [gfight1, gfight2, gfight3, gfight4, ghero, gitem, glevel, gmagic, gmap, gmon]:
        gFileCheck(gfile)
