#!/usr/bin/python
#coding=utf8

import sys
import json
import chardet
from bson import ObjectId, json_util
from collections import defaultdict


# qa_doc 和 task_id-ls ,config 是测试数据,
#qa_doc = {'hbase':'2001-10-15_509740'}
task_id_ls = ['gufenshangshi','gufenshangshi.other']
config = ['num','time','person']


#task_id_ls = ['gufenshangshi']
#从json格式嵌套字典中获取value
def dget(dictionary, cmd, default=None):
    cmd_list = cmd.split('.')
    tmp = dict(dictionary)


    
    for c in cmd_list:
        try:
            val = tmp.get(c, None)
        except AttributeError:
            return default
        if val!= None:
            tmp = val
        else:
            return default
    return tmp

#输入:config：属性配置列表，key：seg所具有的属性
def extractor(config, key):
    for str in config:
        for item in key:
            if item.find(str) != -1:
                return True
    return False

#判断是否为单位，例如‘股’,单位可以和前面数字等合并
def is_unit(key):
    for item in key:
        if item.find('danwei') != -1:
            return True
    return False

sys.path.append('/data/tfs1/zhenqixu/efunds3/src')
reload(sys)
sys.setdefaultencoding('utf-8')

from Utils import Utils

def shuxing_tishi():
    num, num0 = 0,0
    c_utils = Utils()
    for line in sys.stdin:
        try:
            dic = json.loads(line.strip(), object_hook=json_util.object_hook)
        except:
            continue
        c_utils.max_match_one_mark_res(dic)
        content_ls = dic['content']
        for content_dic in content_ls:
            content_dic.pop('qa_result', None)
        pystr = json.dumps(dic,ensure_ascii = False, default = json_util.default)
        qa_doc = json.loads(pystr, encoding = "UTF-8")
        # task_tag_dict dict
        task_tag_dic = {'doc_id': qa_doc.get('hbase_key')}
        dict_list = []
        task_tag_dict = {}
        for val in dget(qa_doc, 'content'):
            if val.has_key('__index'):
                para_pos = val['__index']
                txt_pos = val['__content_offset']
                # value = val['content'] + val['separator']
                if(val.has_key('seg_list')):
                    for tag in val.get('seg_list'):
                        txt_off = txt_pos
                        # value = 'test'
                        value = tag['value_ori']
                        cnt = 0
                        for ch in value.decode('utf-8'):  # 统计段内偏移
                            cnt += 1
                        txt_pos += cnt
                        tag_ls = tag.get('key')
                        if extractor(config, tag_ls):
                            task_tag_obj = {'para_postion': para_pos, 'txt_position': txt_off,
                                        'value_ori': value, 'tag_list': tag_ls}
                            dict_list.append(task_tag_obj)
                        elif is_unit(tag_ls):
                            unit = tag['value_ori']
                            if len(dict_list) > 0 and dict_list[-1].has_key('value_ori'): 
                                dict_list[-1]['value_ori'] += unit

        for task_id in task_id_ls:
            task_tag_dict[task_id] = dict_list

        task_tag_dic['task_tag_dict'] = task_tag_dict

        print json.dumps(task_tag_dic, ensure_ascii=False, default=json_util.default)


if __name__ == '__main__':
    shuxing_tishi()

#
