# coding=utf-8

import argparse
from tqdm import tqdm

def merge_comment_line(in_fname, out_fname):
    with open(in_fname, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        lines = [line.lower().strip() for line in lines]

    with open(out_fname,'w',encoding='utf-8') as f:
        flag = 0
        true_line = ""
        line_id = 0
        for line in tqdm(lines):
            line_id += 1
            if line_id == 1:
                f.write(line + '\n')
            else:
                if  len(line.strip()) == 0:
                    continue
                if line.endswith("双4g手机"):
                    if flag == 0:
                        f.write(line + '\n')
                    else:
                        true_line += line
                        f.write(true_line + '\n')
                        true_line = ""
                        flag = 0
                else:
                    flag = 1
                    true_line += line
    '''
    with open(out_fname, 'w', encoding='utf-8') as f:
        quote_start = False
        quote_line = ''
        for line in tqdm(lines):
            # 删除空行
            if not line.strip():
                continue

            if '"' not in line:
                if not quote_start:
                    # 1. 正常行则正常写入
                    f.write(line)
                else:
                    # 2. 错误中间行
                    quote_line += line.strip()
            else:
                if not quote_start:
                    # 3. 错误开始行
                    quote_start = True
                    quote_line += line.strip()
                else:
                    # 4. 错误结束行
                    quote_start = False
                    quote_line += line.strip()
                    f.write(quote_line+'\n')
                    quote_line = ''
    '''

def check_comment_file(in_fname):
    with open(in_fname, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            len_line = len(line.strip().split('\t'))
            if len_line != 14:
                print('{} : line {}, len {}'.format(in_fname, i, len_line))
                #print(line.strip().split('\t'))
                # return False
    return True


for dname in ['p30pro']:#['iqoo', 'nex', 'x27', 'z5x','iphone','mi','oppo','p30pro']:
    fname = 'data/{}/data_high.csv'.format(dname)
    newdata = 'data/{}/data_clean.csv'.format(dname)
    #merge_comment_line(fname, newdata)
    check_comment_file(newdata)