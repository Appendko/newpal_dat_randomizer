#Python Script to read g*.dat
#Author: Append Huang (append@gmail.com)
#Reference: https://www.ptt.cc/bbs/pal/M.1461154467.A.F26.html
#Reference: https://goo.gl/VypRfq
import numpy as np
from common import item_lst, full_item_lst
from gFile import cmp, gItem
full_item_dict = dict(full_item_lst)
item_dict = dict(item_lst)

class tItem(gItem):
    def __init__(self, loc, arr, callback=None):
        self.loc, self.len, self.arr = loc, len(arr), arr
        self.items = None
        if callback:
            self.items = callback(loc,arr)

    def value(self, index, offset=4, signed=False):
        return int.from_bytes(self.arr[index:index+offset], byteorder="little", signed=signed)

    def str(self, slice_ind):
        return self.arr[slice_ind].tobytes().decode(encoding="big5",errors="strict")

    def check_str(self, ind_begin, ind_end):
        try:
            res_str = self.str(slice(ind_begin, ind_end))
        except UnicodeDecodeError:
            return False
        return res_str        

    def findall(self, seq):
        if type(seq) == str:
            seq = seq.encode(encoding="big5", errors="strict")
        res = []
        ind = bytes(self.arr).find(seq)
        while ind != -1:
            res.append(ind)
            ind = bytes(self.arr).find(seq, ind+1)
        return res
    
    def findstr_l(self, seq, ind):
        if type(seq) == str:
            seq = seq.encode(encoding="big5", errors="strict")
        ind_str = self.arr[:ind].tobytes().rfind(seq)
        return ind_str
    
    def findstr_r(self, seq, ind):
        if type(seq) == str:
            seq = seq.encode(encoding="big5", errors="strict")        
        ind_str = self.arr.tobytes().find(seq, ind+1)
        return ind_str    

class tFile():
    def __init__(self, filename):
        self.filename = filename
        self.items = []        
        self.read(self.filename)

    def __getitem__(self, key):
        return self.items[key]
    
    def read(self, filename):
        with open(filename,"rb") as f:
            self.file_content = bytearray(f.read()) 
        self.parse_block()

    def parse_block(self):
        header = memoryview(self.file_content)[:0x204]
        self.header = gItem(0, header, None) #
        # Indices: 0x0204 -> ?
        #begin from 0x200, read every 4 bytes:
        i_begin = 0x204
        # i_end = int.from_bytes(self.file_content[i_begin:i_begin+4], byteorder="little")+0x200
        i_end = self.file_content.find(b"\x02\x04",i_begin)

        indices_view = memoryview(self.file_content)[i_begin:i_end]
        indices_begin = list(np.frombuffer(indices_view, dtype=np.uint32)+0x200)
        indices_end = indices_begin[1:]+[len(self.file_content)]
        self.indices = gItem(i_begin, indices_view, None)
        self.indices.items = indices_begin

        for ind_i1, ind_i2 in zip(indices_begin, indices_end):
            view_i = memoryview(self.file_content)[ind_i1:ind_i2]
            self.items.append(tItem(ind_i1, view_i, None))
        return

    def find_offset(self, offset):
        res = []
        if len(self.file_content) < offset:
            return None
        for item in self.items:
            if item.loc <= offset and item.loc+item.len > offset:
                res.append(item)
        if res:
            return sorted(res, key=lambda x:x.loc)[-1]
        return None   

    def export(self, filename, file_content=None):
        if file_content == None:
            file_content = self.file_content
        with open(filename,"wb") as f:
            f.write(bytes(file_content))


def test_titem(tfile):
    res_lst = []
    for i, item in enumerate(tfile.items):
        lst_8000 = item.findall(b"\x80\x00")
        if lst_8000:
            #res_lst.append((item, lst_8000))
            for ind in lst_8000:
                item_id = int.from_bytes(item[ind+2:ind+4], byteorder="little")
                item_num = int.from_bytes(item[ind+4:ind+6], byteorder="little",signed=True)
                item_name = full_item_dict.get(item_id, "0x%04X"%item_id)
                res_lst.append((item_name, item_num))
    return res_lst

if __name__ == "__main__":
    talk1 = tFile("dat/talk1.dat")
    talk2 = tFile("dat/talk2.dat")
    talk3 = tFile("dat/talk3.dat")
    talk4 = tFile("dat/talk4.dat")
    talk5 = tFile("dat/talk5.dat")
    talk6 = tFile("dat/talk6.dat")
    talk7 = tFile("dat/talk7.dat")
    talk8 = tFile("dat/talk8.dat")
    
                
