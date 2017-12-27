#!/usr/bin/python
#coding=utf8

# 进行模板匹配
# 单个模板匹配+特征添加
# 上下文模板匹配

import os
import re
import sys
import json
import codecs
import logging
import operator
#import numpy as np
#import random
import time
#import hashlib
from collections import defaultdict

#from DataAccessObj import DataAccessObject
#from Utils import Utils
reload(sys)
sys.setdefaultencoding('utf8')

class PatternEngine(object):
	def __init__(self):
		pass

	# 解析一种类型的key	不包含*
	def parse_single_type(self, pat_ind, seg_ind, value_type=None):
		typ, key, key_type = pat_ind['type'], pat_ind['key'], pat_ind['key_type']
		if typ == 'require':		# 处理单一的字符或者标志
			if key_type == 'tag':
				if not value_type:
					return seg_ind['value_ori'] if key in seg_ind['key'] else False
				else:
					return seg_ind['key_dic'][key] if key in seg_ind['key'] else False
			else:
				return seg_ind['value_ori'] if seg_ind['value_ori'] == key else False
		if typ == 'require_enum':		# 处理	担任|任	
			key_set = set(key.split(u'|'))
			if key_type == 'tag':
				return seg_ind['value_ori'] if set(seg_ind['key']) & key_set else False
			else:
				return seg_ind['value_ori'] if seg_ind['value_ori'] in key_set else False
		if typ == 'exclude_text':	# 处理不包含某种类型的情况
			#key_set = set(key.split(u'|'))
			for key in key.split(u'|'):
				if key in seg_ind['value_ori']:
					return False
			return True
			#return False if seg_ind['value_ori'] in key_set else seg_ind['value_ori']
		if typ == 'exclude_tag':	# 处理不包含某种类型的情况
			key_set = set(key.split(u'|'))
			return False if set(seg_ind['key']) & key_set else seg_ind['value_ori']
		if typ == 'include_tag': # 处理*必须包含某种类型的情况
			key_set = set(key.split(u'|'))
#			if pat_ind['key'] == '<jiedaikuan_tigong>':
#				print 'jiedaikuan_tigong'
#				print 'seg', json.dumps(seg_ind, ensure_ascii=False)
#				print 'pat', json.dumps(pat_ind, ensure_ascii=False)
#				print json.dumps(list(set(seg_ind['key']) & key_set), ensure_ascii=False)
			return False if not (set(seg_ind['key']) & key_set) else seg_ind['value_ori']
		if typ == 'include_text': # 处理*必须包含某些文字的情况
			key_set = set([ss.encode('utf8') for ss in key.split(u'|')])
			return False if not (seg_ind['value_ori'] in key_set) else seg_ind['value_ori']
		return False

	# 特征匹配   
	def __match_feature(self, pattern, dic):
		pat_feat, dic_feat = pattern.get('feature', None), dic.get('feature', {})
		feat_matched = True
		if pat_feat:
			for k in pat_feat.keys():
				if pat_feat[k] != dic_feat.get(k, None):
					feat_matched = False
					break
		return feat_matched

	def __is_context_matched(self, pat, content_dic_ls, cur_ind):
		context_matched = True
		for c_offset, c_dic in pat['context'].iteritems():
			if not context_matched:
				break
			content_dic = content_dic_ls[cur_ind + c_offset]
			context_dic = content_dic.get('context',[])
			# and
			if c_dic.get('and', None) and filter(lambda x: x not in context_feat, c_dic['and']):
				context_matched = False
			# or
			if c_dic.get('or', None) and not filter(lambda x:x in context_feat, c_dic['or']):
				context_matched = False
			# not
			if c_dic.get('not', None) and filter(lambda x:x in context_feat, c_dic['not']):
				context_matched = False
		return context_matched

	# 解析*类型
	# 添加不包含的处理
	def parse_star_type(self, ind_p, ind_s, value_type, pat_ls, seg_ls, res_dic):
		ind_p += 1
		star_num, star_value = 0, ''
		# *匹配到最后的内容
		if ind_p == len(pat_ls):
			star_value = ''.join([seg_ls[ii]['value_ori'] for ii in range(ind_s, len(seg_ls))])
			# 处理*中处理不包含某些内容
			if pat_ls[ind_p-1]['type'].startswith('exclude') or pat_ls[ind_p-1]['type'].startswith('include'):
				exc_res = False
				while ind_s < len(seg_ls):
					exc_res = self.parse_single_type(pat_ls[ind_p-1], seg_ls[ind_s], value_type)
					ind_s += 1
					if not exc_res:
						return ind_p, ind_s, res_dic, False
			res_dic[ind_p-1] = star_value
			return ind_p, ind_s, res_dic, True
		# *没有匹配任何内容
		tmp_res = self.parse_single_type(pat_ls[ind_p], seg_ls[ind_s], value_type)
		if tmp_res:
			res_dic[ind_p-1] = ''
			#print 'nonono', tmp_res, ind_p, ind_s
			return  ind_p, ind_s, res_dic, tmp_res

		# 检查*匹配部分内容
		tmp_res = False # 判断*后面的标记是否匹配
		exc_res = True  # 判断*的内容中是否不包含某些必要的内容
		# 内容匹配过程
		while ind_s < len(seg_ls) and star_num < 100:
			star_num += 1
			# 判断*中不包含某些内容的情况
			if pat_ls[ind_p-1]['type'].startswith('exclude') or pat_ls[ind_p-1]['type'].startswith('include'):
				exc_res = self.parse_single_type(pat_ls[ind_p-1], seg_ls[ind_s], value_type)
				if not exc_res:
					return ind_p, ind_s, res_dic, False
				else:
					if ind_s+1 >= len(seg_ls):
#						print 'execute this is incridable', json.dumps(seg_ls[ind_s], ensure_ascii=False)
						tmp_res = False
					else:
						tmp_res = self.parse_single_type(pat_ls[ind_p], seg_ls[ind_s+1], value_type)
#					print '--'*60
#					print json.dumps([pat_ls[ind_p], seg_ls[ind_s+1]], ensure_ascii=False)
#					print 'tmp_res', tmp_res
#					print '--'*60
					if tmp_res:
						star_value += seg_ls[ind_s]['value_ori']
						res_dic[ind_p-1] = star_value
						return ind_p, ind_s+1, res_dic, tmp_res
					else:
						star_value += seg_ls[ind_s]['value_ori']
						ind_s += 1
			# 普通*的判断
			else:
				# 判断之后的内容中是否包含哪些内容
				tmp_res = self.parse_single_type(pat_ls[ind_p], seg_ls[ind_s], value_type)
				if tmp_res != False:
					if not pat_ls[ind_p]['type'].startswith('exclude') or not pat_ls[ind_p]['type'].startswith('include'):
						res_dic[ind_p-1] = star_value
					break
				else:
					star_value += seg_ls[ind_s]['value_ori']
					ind_s += 1
		#if not exc_res:
		#	tmp_res = False
		return ind_p, ind_s, res_dic, tmp_res
	
	# 解析单个pattern
	def parse_one_pattern(self, pattern, dic):
		# 特征匹配
		feat_matched = self.__match_feature(pattern, dic)
		if not feat_matched:
			return []
		pat_ls, seg_ls, value_type = pattern['pattern'], dic.get('seg_list',None), pattern.get('value_type', None)
		if not seg_ls:
			return []
		ind_p, ind_s = 0, 0
		res = {}
		# 处理以某些词开头的情形
		if pat_ls[0]['key_type'] == '^':
			beg_res = self.parse_single_type(pat_ls[1], seg_ls[0], value_type)
			if beg_res:
				res[1] = beg_res
				ind_p, ind_s = 2, 1
			else:
				ind_p = len(pat_ls)
#			print '--'*30, 'parse_one_pattern', '--'*30
#			print ind_p, ind_s 
#			print json.dumps([pat_ls[ind_p], seg_ls[ind_s]], ensure_ascii=False)
#			print json.dumps(res, ensure_ascii=False)
#			print beg_res
#			print '--'*70
		# 处理中间模板匹配的情形
		while(ind_p < len(pat_ls) and ind_s < len(seg_ls)):
			pat_ind, seg_ind = pat_ls[ind_p], seg_ls[ind_s]
			typ = pat_ind['key_type']
			if typ != '*':
				tmp_res = self.parse_single_type(pat_ind, seg_ind, value_type)
#				print 'not *', ind_p, ind_s, json.dumps(tmp_res, ensure_ascii=False)
			# 处理*的情况
			else:
				ind_p, ind_s, res, tmp_res = self.parse_star_type(ind_p, ind_s, value_type, pat_ls, seg_ls, res)
#				print 'is *', ind_p, ind_s, json.dumps(res, ensure_ascii=False), json.dumps(tmp_res, ensure_ascii=False)
#			print '--'*30, 'parse_one_pattern', '--'*30
#			print ind_p, ind_s 
#			print json.dumps([pat_ls[ind_p], seg_ls[ind_s]], ensure_ascii=False)
#			print json.dumps(res, ensure_ascii=False)
#			print tmp_res
#			print '--'*70

		# 没有完全匹配 直接退出
			if tmp_res == False:
				return []
			res[ind_p] = tmp_res
			ind_p += 1
			ind_s += 1
		fin_res = []
		if (ind_p >= len(pat_ls) or (ind_s>=len(seg_ls) and ind_p==len(pat_ls)-1 and (pat_ls[ind_p]['key_type']=='*' or pat_ls[ind_p]['key_type']=='$'))) and res:
			# 解决最后的*什么内容都没有匹配的情况
			end_ind = len(pat_ls) - 1
			if pat_ls[-1]['key_type'] == '*' and end_ind not in res:
				res[end_ind] = ''
			for rule in pattern['rule']:
				tmp_dic = {}
				for k, vv in rule.iteritems():
					vvk = ''
					for v in vv:
						try:
							vvk += res[v]
						except:
							sys.stderr.write(str(end_ind) + '\n')
							sys.stderr.write( 'res: ' + json.dumps(res, ensure_ascii=False) + '\n')
							sys.stderr.write( 'pattern: ' + json.dumps(pattern, ensure_ascii=False) + '\n')
							sys.stderr.write( 'dic: ' + json.dumps(dic, ensure_ascii=False) + '\n')
							sys.stderr.write( '=='*20 + '\n')
							#sys.exit(-1)
					tmp_dic[k] = vvk
				fin_res.append(tmp_dic)
		# 进行context特征的添加
		if fin_res:
			#print json.dumps(fin_res, ensure_ascii=False)
			for res_dic in fin_res:
				for k in res_dic.keys():
					if 'context' not in dic:
						dic['context'] = {}
					dic['context'][k] = True
		return fin_res
	
	def __is_context_matched(self, pat, content_dic_ls, cur_ind):
		feat_matched = True
		for c_offset, c_dic in pat['context'].iteritems():
			if not feat_matched:
				break
			content_dic = content_dic_ls[cur_ind + c_offset]
			feat_dic = content_dic.get('feature',[])
			# and
			if c_dic.get('and', None) and filter(lambda x: x not in feat_dic, c_dic['and']):
				feat_matched = False
			# or
			if c_dic.get('or', None) and not filter(lambda x:x in feat_dic, c_dic['or']):
				feat_matched = False
			# not
			if c_dic.get('not', None) and filter(lambda x:x in feat_dic, c_dic['not']):
				feat_matched = False
		return feat_matched
	
	# 进行单个context feature的匹配
	def parse_context_feature(self, pat, one_dic):
		if 'context' not in pat:
			return None
		content_ls = one_dic.get('content', [])
		ind0, ind1 = min(pat['context'].keys()), max(pat['context'].keys())
		beg_ind = -ind0 if ind0 < 0 else 0
		end_ind = len(one_dic['content'])-ind1 if ind1 > 0 else len(one_dic['content'])
		fin_res = []
		for ind, content_dic in enumerate(content_ls[beg_ind:end_ind], beg_ind):
			feat_matched = self.__is_context_matched(pat, content_ls, ind)
			if feat_matched:
				tmp_res = self.parse_one_pattern(pat, content_dic)
				if tmp_res:
					fin_res.append({ind:tmp_res})
		return fin_res
	
	# 进行单个context pattern的匹配
	def parse_context_pattern(self, no_c_pat_ls, c_pat_ls, one_dic):
		if not one_dic.get('content', None):
			return []
		for content_dic in one_dic['content']:
			# 进行context特征的添加
			for pat in no_c_pat_ls:
				tmp_res = self.parse_one_pattern(pat, content_dic)
				if tmp_res:
					for dic in tmp_res:
						for k in dic.keys():
							if 'feature' not in content_dic:
								content_dic['feature'] = {}
							content_dic['feature'][k] = True
		# 进行context特征的匹配
		fin_res = []
		for pat in c_pat_ls:
			tmp_res = self.parse_context_feature(pat, one_dic)
			if tmp_res:
				fin_res.extend(tmp_res)
				#print 'context feature: {}'.format(json.dumps(tmp_res, ensure_ascii=False))
		return tmp_res
	
	# 自动识别要抽取的key, 可以利用tfidf来确定
	# 但是针对这个的效果并不好
#	def extract_inv_key(self, pat_ls):
#		tfidf_ls = []
#		df_dic = defaultdict(int)
#		for ind, pat in enumerate(pat_ls):
#			tf_dic, tmp_num = defaultdict(int), 0.0
#			for pati in pat['pattern']:
#				key = pati['key'].split('|')
#				for k in filter(lambda x: x not in ['*', '$', '^'], key):
#					tf_dic[k] += 1
#					tmp_num += 1.0
#			for key in tf_dic.keys():
#				df_dic[key] += 1
#				tf_dic[key] /= tmp_num
#			tfidf_ls.append(tf_dic)
#		####
#		logging.info('inv_key:')
#		for ls in tfidf_ls:
#			logging.info(json.dumps(ls, ensure_ascii=False))
#		###
#		inv_key = defaultdict(set)
#		for ind, tf_dic in enumerate(tfidf_ls):
#			tu_ls = [(k, v*np.log(len(pat_ls)/1.0/df_dic[k])) for k, v in tf_dic.iteritems()]
#			tu_ls = sorted(tu_ls, key=lambda x: x[1], reverse=True)
#			for tu in tu_ls[:2]:
#				inv_key[tu[0]].add(ind)
#		return inv_key
	
	# pattern倒排
	def get_inv_pat_inter(self, inv_key, pat_ls): 
		# key: $		、		、|兼 <s_djg_chenghu><tm_company>		*
		# 还可以加上出现的次数
		inv_pat_dic = defaultdict(set) 
		for ind, pat in enumerate(pat_ls):
			pati = pat['pattern']
			key_set = set()
			for key in pati:
				key_set.update(key['key'].split('|'))
			for key in inv_key:
				if key in key_set:
					inv_pat_dic[key].add(ind)
		return inv_pat_dic
	
	def filter_pattern_inter(self, seg_ls, inv_pat_dic):
		candi_pat_ind = set()
		tag_dic, value_dic = defaultdict(int), defaultdict(int)
		for seg in seg_ls:
			key, value = seg['key'], seg['value_ori']
			candi_pat_ind |= inv_pat_dic.get(value, set())
			for k in key:
				candi_pat_ind |= inv_pat_dic.get(k, set())
		return list(candi_pat_ind)
	
	def get_inv_pat_union(self, pat_ls):
		inv_pat_dic = defaultdict(set)
		for ind, pat in enumerate(pat_ls):
			for pati in pat['pattern']:
				if pati['key'].find('|') != -1:
					ls = pati['key'].split('|')
					for k in ls:
						inv_pat_dic[k].add(ind)
				else:
					inv_pat_dic[pati['key']].add(ind)
		return inv_pat_dic
	
	def filter_pattern_union(self, seg_ls, inv_pat_dic):
		candi_pat_ind = set([i for i in xrange(10)])
		for seg in seg_ls:
			tag_ls, value = seg['key'], seg['value_ori']
			for tag in tag_ls:
				if tag in inv_pat_dic:
					candi_pat_ind = candi_pat_ind & inv_pat_dic[tag]
			if value in inv_pat_dic:
				candi_pat_ind = candi_pat_ind & inv_pat_dic[value]
		return list(candi_pat_ind)
	
	def title_extraction(self, dic_ls, pat_ls):
		res_ls = []
		num = 0
		for dic in dic_ls:
			num += 1
	#		if num % 1000 == 0:
	#			logging.info('stage title extraction, line num: {}'.format(num))
			# 获取分词打标结果
			one_res = title_extraction_single(dic, pat_ls)
			res_ls.append(one_res)
		return res_ls 
	
	def title_extraction_single(self, dic, pat_ls):
		# 获取分词打标结果
		one_res = []
		pkey, content = dic.get('key', ' '), dic.get('content', '')
		for ind, tmp_dic in enumerate(content):
			#tmp_dic['is_title'] = False
			if 'seg_list' not in tmp_dic:
				continue
			#if len(tmp_dic['content']) > 50*3 or re.search(u'。|《|"|:', tmp_dic['content']):
			if len(tmp_dic['content']) > 50*3 or re.search(u'。|"', tmp_dic['content']):
				continue
			parse_res, tmp_set = [], set()
			for pat in pat_ls:
				tmp_res = self.parse_one_pattern(pat, tmp_dic)
				if tmp_res:
					ss = json.dumps(tmp_res)
					if ss not in tmp_set:
						tmp_set.add(ss)
						parse_res.extend(tmp_res)
			if parse_res:
				one_res.append([ind, tmp_dic['content'], parse_res[0]['num']])
				#tmp_dic['is_title'] = True
		return [pkey, one_res]
	
	def pdf_type_match(self, dic, pat_ls):
		# 获取分词打标结果
		one_res = []
		content = dic.get('content', '')
		for ind, tmp_dic in enumerate(content):
			if 'seg_list' not in tmp_dic:
				continue
			parse_res, tmp_set = [], set()
			for pat in pat_ls:
				tmp_res = self.parse_one_pattern(pat, tmp_dic)
				if tmp_res:
					ss = json.dumps(tmp_res)
					if ss not in tmp_set:
						tmp_set.add(ss)
						parse_res.extend(tmp_res)
			if parse_res:
				one_res.append(parse_res)
		# one_res进行merge
		fin_res_dic = defaultdict(set)
		for parse_res in one_res:
			for dic in parse_res:
				for k, v in dic.iteritems():
					if isinstance(v, list):
						fin_res_dic[k].update(v)
					else:
						fin_res_dic[k].add(v)
		fin_res = {k:list(v) for k, v in fin_res_dic.iteritems()}
		return fin_res

def load_pattern(pat_fn, array_pattern_table = []):
	pat_ls = []
	for line in codecs.open(pat_fn, 'r', 'utf8'):
		line = line.strip()
		if line.startswith("#"):
			continue
		try:
			json_obj = json.loads(line)
			if 'pattern_type' in json_obj and json_obj['pattern_type'] == "table":
				array_pattern_table.append(json_obj)
			else:
				pat_ls.append(json_obj)
		except Exception as ex:
			pass
	return pat_ls

class PatternEngine2(PatternEngine):
	def __init__(self):
		PatternEngine.__init__(self)
		pass

	def find_pat_ind(self, pat_ls, seg_ls):
		res_dic = defaultdict(list)  # key为pattern的下标 value为seg_ls中出现的下标
		if not pat_ls or not seg_ls:
			return res_dic
		# 归一化pattern
		if pat_ls[0]['key_type'] != '^':
			pat_ls.insert(0, {'key_type':'^', 'type':'^', 'key':'^'})
		if pat_ls[-1]['key_type'] != '$':
			pat_ls.append({'key_type':'$', 'type':'$', 'key':'$'})
#		print json.dumps(pat_ls, ensure_ascii=False)
		# 进行连接关系的确定
		cur_ind = 0
		for indp, pat_dic in enumerate(pat_ls):
			key_typ = pat_dic['key_type']
			typ = pat_dic['type']
			key = pat_dic['key']
			key_set = set(pat_dic['key'].split('|'))
			if key_typ == '^' or key_typ == '$' or key_typ == '*':
				res_dic[indp] = []
				continue
			for ind, seg_dic in enumerate(seg_ls[cur_ind:], cur_ind):
				seg_key_set = set(seg_dic['key'])
				value_set = set([seg_dic['value_ori']])
				if key_typ == 'text':
					if (typ == 'require' or typ == 'require_enum') and (value_set & key_set):
						res_dic[indp].append(ind)
					else:
						continue
				elif key_typ == 'tag':
					if (typ == 'require' or typ == 'require_enum') and (seg_key_set & key_set):
						res_dic[indp].append(ind)
					else:
						continue
			if not res_dic[indp]:
				return res_dic
			else:
				cur_ind = res_dic[indp][0] + 1
		return res_dic

	def parse_new_matched(self, pat_ls, seg_ls, pat_ind_seg_dic):
		res_ls = []
		for ind, pat_dic in enumerate(pat_ls):
			key_typ = pat_dic['key_type']
			if key_typ != '*' or key_typ == '^' or key_typ == '$':
				break
		if ind == len(pat_ls) - 1:
			return res_ls
		first_ind = ind
		first_ind_ls = pat_ind_seg_dic[ind]
		tmp_ls = [-1]
		for ind in range(1, first_ind):
			pat_dic = pat_ls[ind]
			tmp_ls.append(tmp_ls[-1] + 1)
		pat_ind = first_ind
		while first_ind_ls:
			seg_ind = first_ind_ls.pop()
			tmp_ls.append(seg_ind)
			# 判断pat_ind的key_type
			while len(tmp_ls) < len(pat_ls):
				continue
		pass

#	def parse_one_pattern(self, pattern, dic):
#		# 特征匹配
#		feat_matched = self.__match_feature(pattern, dic)
#		if not feat_matched:
#			return []
#		pat_ls, seg_ls, value_type = pattern['pattern'], dic.get('seg_list',None), pattern.get('value_type', None)
#		if not seg_ls:
#			return []
#		# 归一化pattern
#		rule_dic_ls = pattern['rule']
#		if pat_ls[0]['key_type'] != '^':
#			pat_ls.insert(0, {'key_type':'^', 'type':'^', 'key':'^'})
#			for rule_dic in rule_dic_ls:
#				for k in rule_dic.keys():
#					v_ls = rule_dic[k]
#					rule_dic[k] = [v+1 for v in v_ls]
#		if pat_ls[-1]['key_type'] != '$':
#			pat_ls.append({'key_type':'$', 'type':'$', 'key':'$'})
#		print json.dumps(pat_ls, ensure_ascii=False)
#		# pat节点之间的连接关系确定
#		res_ls = []
#		pat_ind_seg_dic = self.find_pat_ind(pat_ls, seg_ls)
#		print json.dumps(pat_ind_seg_dic, ensure_ascii=False)
#		if not pat_ind_seg_dic:
#			return res_ls
#		# 进行
#		cur_ind_s = 0
#		res_dic = {}
#		for ind_p, pat in enumerate(pat_ls):
#			key_typ, typ, key = pat_dic['key_type'], pat_dic['type'], pat_dic['key']
#			if key_typ == '$':
#				if cur_ind_s == len(seg_list) and ind_p == len(pat_ls):
#					res_dic = True
#					res_ls.append(res_dic)
#				else:
#					break
#			pat_ind_seg_dic[indp]

class PriorityPatternEngine(PatternEngine):
	def __init__(self):
		PatternEngine.__init__(self)
		pass

	# 获取模板抽取的关系集合
	def get_rule_set(self, pat):
		rule_set = set()
		rule_dic_ls = pat.get('rule', [])
		for rule_dic in rule_dic_ls:
			rule_set.update(rule_dic.keys())
		return rule_set
	
	# 获取当前模板的各个关系优先级
	# 若pat中不存在优先级, 则优先级为10000
	def get_cur_rule_pri_dic(self, pat, rule_set):
		cur_pri_dic = pat.get('priority', {})
		for k in rule_set:
			if k not in cur_pri_dic:
				cur_pri_dic[k] = 10000
		return cur_pri_dic
	
	def get_pri_rule_dic(self, pri_pat_res_dic_ls):
		pri_rule_dic = {}
		key_priority = 'priority'
		for pri_pat_res_dic in pri_pat_res_dic_ls:
			if len(pri_pat_res_dic.keys())>1 and key_priority in pri_pat_res_dic:
				for key in filter(lambda x: x != key_priority, pri_pat_res_dic.keys()):
					pri_rule_dic[key] = pri_pat_res_dic[key_priority]
		return pri_rule_dic
	
	def merge_multi_priority_res(self, pat_res, cur_pri_dic, pri_rule_dic, pri_pat_res_dic_ls):
		if not pat_res:
			return
		key_priority = 'priority'
		# 当前模板存在优先级的情况
		for cur_rule, cur_pri in cur_pri_dic.iteritems():
			value_ls = [dic[cur_rule] for dic in pat_res if cur_rule in dic]
			if value_ls: 
				# 将结果新加入结果中
				if cur_rule not in pri_rule_dic:
					pri_pat_res_dic_ls.append({cur_rule:value_ls, key_priority:cur_pri})
				# 需要用当前结果替换原始结果
				elif cur_pri < pri_rule_dic[cur_rule]:
					for pri_pat_res_dic in pri_pat_res_dic_ls:
						if cur_rule in pri_pat_res_dic:
							pri_pat_res_dic[cur_rule] = value_ls
							pri_pat_res_dic[key_priority] = cur_pri
				# 需要将当前结果添加到已有结果的后面
				elif cur_pri == pri_rule_dic[cur_rule]:
					for pri_pat_res_dic in pri_pat_res_dic_ls:
						if cur_rule in pri_pat_res_dic:
							pri_pat_res_dic[cur_rule].extend(value_ls)

	def drop_priority_and_remove_dupilcate_res(self, res_ls):
		for res_dic in res_ls:
			res_dic.pop('priority', None)
			for k, v_ls in res_dic.iteritems():
				res_dic[k] = list(set(v_ls))
		
	def parse_one_pattern_with_priority(self, pat, content_dic, pri_pat_res_dic_ls):
		# 获取当前pat抽取的关系对
		rule_set, pri_rule_dic = self.get_rule_set(pat), self.get_pri_rule_dic(pri_pat_res_dic_ls)
		# 获取当前关系优先级字典 若没有指定优先级 则默认优先级为10000
		cur_pri_dic = self.get_cur_rule_pri_dic(pat, rule_set)
		pri_rule_set = set(pri_rule_dic.keys())
		# 当前所有的关系的优先级均小于现有优先级
		low_prio = True
		for cur_rule, cur_pri in cur_pri_dic.iteritems():
			if cur_rule not in pri_rule_dic or (cur_rule in pri_rule_dic and cur_pri <= pri_rule_dic[cur_rule]):
				low_prio = False
				break
		if not low_prio:
			pat_res = self.parse_one_pattern(pat, content_dic)
			if pat_res:
				print 'content', content_dic['content'].strip()
				print 'seg_list', json.dumps(content_dic['seg_list'], ensure_ascii=False)
				print 'pat', json.dumps(pat, ensure_ascii=False)
				print 'pat_res', json.dumps(pat_res, ensure_ascii=False)
				print ''
				self.merge_multi_priority_res(pat_res, cur_pri_dic, pri_rule_dic, pri_pat_res_dic_ls)

def test_star_exclude():
	pat = {"pattern": [ {"key_type": "*", "type": "exclude_text", "key": "你好"}, \
											{"key_type": "text", "type": "require", "key": "治疗"}, \
											{"key_type": "*", "type": "exclude_tag", "key": "<dun>"}], \
											"priority": {"前": 10}, "rule": [{"治疗之前": [0], }, {"治疗之后": [2]}]}
#	c_dao, c_pat_eng = DataAccessObject(), PriorityPatternEngine()
#	for line in codecs.open('../tmp.1', 'r', 'utf8'):
#		one_dic = json.loads(line.strip())
#		content_dic_ls = one_dic.get('content', [])
#		pri_pat_res_dic_ls = []
#		for content_dic in content_dic_ls:
#			c_pat_eng.parse_one_pattern_with_priority(pat, content_dic, pri_pat_res_dic_ls)
#		print json.dumps(pri_pat_res_dic_ls, ensure_ascii=False)
#		#print '\n'.join([json.dumps(pri_pat_res_dic, ensure_ascii=False) for pri_pat_res_dic in pri_pat_res_dic_ls])

#def test_pat_priority():
#	c_dao = DataAccessObject()
#	c_utils = Utils()
#	c_pat_eng = PriorityPatternEngine()
#	class_type = 'touzibinggou'
#	key_class_type = 'class_type'
#	key_feature = 'feature'
#	dic_ls = c_dao.load_fields_from_mongo('elab_doc', {'tasks.id':class_type}, {'announcementTime':1})
#	#dic_ls = c_dao.load_fields_from_mongo('elab_doc', {'_id':'1203093878'}, {'announcementTime':1})
#	pat_ls = load_pattern('../conf/pat.txt_all')
#	for dic in dic_ls[:10]:
#		qid = dic['announcementTime'] + '_' + dic['_id']
#		print qid
#		qa_dic = c_dao.load_single_pdf_from_mysql(qid, 'gonggao_qa')
#		c_utils.paste_dic_content(qa_dic)
#		pri_pat_res_dic_ls = []
#		for content_dic in qa_dic['content']:
#			content_dic[key_feature] = {key_class_type:class_type}
#			for pat in pat_ls:
#				c_pat_eng.parse_one_pattern_with_priority(pat, content_dic, pri_pat_res_dic_ls)
#		print '\n'.join([json.dumps(pri_pat_res_dic, ensure_ascii=False) for pri_pat_res_dic in pri_pat_res_dic_ls])
#		print '=='*20
#
def test_new_pat_eng():
	c_pat_eng2 = PatternEngine2()
	pat_list = [{"key_type": "*", "type": "*", "key": "*"}, \
							{"key_type": "tag", "type": "require", "key": "<time>"}, \
							{"key_type": "*", "type": "*", "key": "*"}, \
							{"key_type": "tag", "type": "require", "key": "<bing>"}, \
							{"key_type": "*", "type": "*", "key": "*"}]
	seg_list = [{"key": ["<short_name>","<tm_company>","<crf_org>"],"key_dic": {"<short_name>": "恒瑞医药","<tm_company>": "恒瑞医药","<crf_org>": "恒瑞医药"},"begin_pos": 0,"len": 3,"value_ori": "恒瑞医药"},\
							{"key": ["<time>"],"key_dic": {"<time>": "2001-01-01-00-00-00-00_2001-12-31-23-59-00-00"},"begin_pos": 3,"len": 2,"value_ori": "2001年"},\
							{"key": ["<time>"],"key_dic": {},"begin_pos": 5,"len": 1,"value_ori": "中期"},\
							{"key": ["<bing>"],"key_dic": {},"begin_pos": 5,"len": 1,"value_ori": "中期"},\
							{"key": ["<bing>"],"key_dic": {},"begin_pos": 5,"len": 1,"value_ori": "中期"},\
							{"key": ["<basic>"],"key_dic": {},"begin_pos": 6,"len": 1,"value_ori": "报告"}]
	res_dic = c_pat_eng2.find_pat_ind(pat_list, seg_list)
	print json.dumps(res_dic, ensure_ascii=False)

def test_star_include():
	c_pat_eng = PatternEngine()
	seg_list = [{"len": 2, "key_dic": {"<kp_p_gongsi_zhuceziben>": "注册资金:"}, "begin_pos": 0, "key": ["<kp_p_gongsi_zhuceziben>"], "value_ori": "注册资金"}, \
							{"len": 3, "key_dic": {"<money>": "500万元"}, "begin_pos": 2, "key": ["<money>"], "value_ori": "500万元"}]
	pat_list = [{"key_type": "*", "type": "*", "key": "*"}, \
							{"key_type": "tag", "type": "require_enum", "key": "<kp_p_gongsi_zhucezijin>|<kp_p_gongsi_zhuceziben>"}, \
							{"key_type": "*", "type": "include_text", "key": "增资|至"}, \
							{"key_type": "tag", "type": "require_enum", "key": "<money>"}]
#	pat_list = [{"key_type": "tag", "type": "require", "key": "<crf_org>"}, \
#							{"key_type": "tag", "type": "require", "key": "<time>"}, \
#							{"key_type": "*", "type": "include_tag", "key": "<time>"}, \
#							{"key_type": "tag", "type": "require", "key": "<bing>"}, \
#							{"key_type": "*", "type": "include_tag", "key": "<time>|<basic>"}] \
##							{"key_type": "tag", "type": "require", "key": "<basic>"}, \
##							{"key_type": "$", "type": "require", "key": "$"}]
#	seg_list = [{"key": ["<short_name>","<tm_company>","<crf_org>"],"key_dic": {"<short_name>": "恒瑞医药","<tm_company>": "恒瑞医药","<crf_org>": "恒瑞医药"},"begin_pos": 0,"len": 3,"value_ori": "恒瑞医药"},\
#							{"key": ["<time>"],"key_dic": {"<time>": "2001-01-01-00-00-00-00_2001-12-31-23-59-00-00"},"begin_pos": 3,"len": 2,"value_ori": "2001年"},\
#							{"key": ["<time>"],"key_dic": {},"begin_pos": 5,"len": 1,"value_ori": "中期2"},\
#							{"key": ["<bing>"],"key_dic": {},"begin_pos": 6,"len": 1,"value_ori": "中期3"},\
#							{"key": ["<time>"],"key_dic": {},"begin_pos": 7,"len": 1,"value_ori": "中期4"},\
#							{"key": ["<basic>"],"key_dic": {},"begin_pos": 8,"len": 1,"value_ori": "报告"}]
#	seg_list = [{"len": 1, "key_dic": {"<bengongsi>": "公司", "<diyu_gongsi>": "公司"}, "begin_pos": 0, "key": ["<bengongsi>", "<diyu_gongsi>"], "value_ori": "公司"}, \
#			{"len": 9, "key_dic": {"<time_biaodi>": "拟在2012年12月30日前"}, "begin_pos": 1, "key": ["<time_biaodi>"], "value_ori": "拟在2012年12月30日前"}, \
#			{"len": 1, "key_dic": {"<touzi_jieci>": "向", "<muji_duishou_l_1>": "向", "<guquanjili_duixiang_l_1>": "向", "<guquanjili_jilirenshu_l_1>": "向", "<touzi_zhuti_r_3_1>": "向", "<touzi_duixiang_left_3>": "向", "<jiedaikuan_xiang>": "向"}, "begin_pos": 10, "key": ["<touzi_jieci>", "<muji_duishou_l_1>", "<guquanjili_duixiang_l_1>", "<guquanjili_jilirenshu_l_1>", "<touzi_zhuti_r_3_1>", "<touzi_duixiang_left_3>", "<jiedaikuan_xiang>"], "value_ori": "向"}, \
#			{"len": 15, "key_dic": {"<crf_org>": "关联方江苏省苏豪控股集团有限公司(以下简称\"苏豪控股\")"}, "begin_pos": 11, "key": ["<crf_org>"], "value_ori": "关联方江苏省苏豪控股集团有限公司(以下简称\"苏豪控股\")"}, \
#			{"len": 1, "key_dic": {"<jiedaikuan_jiedaikuan>": "借款"}, "begin_pos": 26, "key": ["<jiedaikuan_jiedaikuan>"], "value_ori": "借款"}, \
#			{"len": 5, "key_dic": {"<money>": "不超过1.5亿元"}, "begin_pos": 27, "key": ["<money>"], "value_ori": "不超过1.5亿元"}]
#	pat_list = [{"key_type": "^", "type": "require", "key": "^"}, \
#			{"key_type": "tag", "type": "require", "key": "<bengongsi>"}, \
#			{"key_type": "*", "type": "include_tag", "key": "<time_biaodi>"}, \
#			{"key_type": "tag", "type": "require", "key": "<jiedaikuan_xiang>"}, \
#			{"key_type": "tag", "type": "require_enum", "key": "<tm_company>|<crf_org>"}, \
#			{"key_type": "*", "type": "include_tag", "key": "<jiedaikuan_tigong>"}, \
#			{"key_type": "tag", "type": "require", "key": "<jiedaikuan_jiedaikuan>"}, \
#			{"key_type": "*", "type": "include_tag", "key": "<jiedaikuan_edu>"}, \
#			{"key_type": "tag", "type": "require", "key": "<money>"}, \
#			{"key_type": "*", "type": "*", "key": "*"}]
	pattern_dic = {'pattern':pat_list, 'rule':[{'test':[3]}]}
	content_dic = {'seg_list':seg_list}
	res_dic = c_pat_eng.parse_one_pattern(pattern_dic, content_dic)
	print json.dumps(res_dic, ensure_ascii=False)

def test_parse_one_pattern():
	c_pat_eng = PatternEngine()
	seg_list = [{"len": 1, "key_dic": {"<bengongsi>": "公司", "<diyu_gongsi>": "公司"}, "begin_pos": 0, "key": ["<bengongsi>", "<diyu_gongsi>"], "value_ori": "公司"}, {"len": 1, "key_dic": {}, "begin_pos": 1, "key": ["<basic>"], "value_ori": "预计"}, {"len": 2, "key_dic": {"<time>": "2014-01-01-00-00-00-00_2014-12-31-23-59-00-00"}, "begin_pos": 2, "key": ["<time>"], "value_ori": "2014年"}, {"len": 1, "key_dic": {"<numpure>": "1.000000", "<numreal>": "1.000000"}, "begin_pos": 4, "key": ["<numpure>", "<numreal>"], "value_ori": "1"}, {"len": 1, "key_dic": {}, "begin_pos": 5, "key": ["<basic>"], "value_ori": "-"}, {"len": 2, "key_dic": {"<time_month>": "2017-03-01-00-00-00-00_2017-03-31-23-59-00-00", "<time>": "2017-03-01-00-00-00-00_2017-03-31-23-59-00-00"}, "begin_pos": 6, "key": ["<time_month>", "<time>"], "value_ori": "3月"}, {"len": 1, "key_dic": {}, "begin_pos": 8, "key": ["<basic>"], "value_ori": "归"}, {"len": 1, "key_dic": {}, "begin_pos": 9, "key": ["<basic>"], "value_ori": "属于"}, {"len": 1, "key_dic": {}, "begin_pos": 10, "key": ["<basic>"], "value_ori": "母"}, {"len": 1, "key_dic": {"<bengongsi>": "公司", "<diyu_gongsi>": "公司"}, "begin_pos": 11, "key": ["<bengongsi>", "<diyu_gongsi>"], "value_ori": "公司"}, {"len": 1, "key_dic": {"<touzi_guquan>": "股东", "<gudong>": "股东", "<s_djg_chenghu>": "股东"}, "begin_pos": 12, "key": ["<touzi_guquan>", "<gudong>", "<s_djg_chenghu>"], "value_ori": "股东"}, {"len": 1, "key_dic": {"<muji_chengnuo_r_1_2>": "净利润"}, "begin_pos": 13, "key": ["<muji_chengnuo_r_1_2>"], "value_ori": "净利润"}, {"len": 1, "key_dic": {}, "begin_pos": 14, "key": ["<basic>"], "value_ori": "较"}, {"len": 1, "key_dic": {}, "begin_pos": 15, "key": ["<basic>"], "value_ori": "上年"}, {"len": 1, "key_dic": {}, "begin_pos": 16, "key": ["<basic>"], "value_ori": "增长"}, {"len": 2, "key_dic": {"<numpure>": "0.400000"}, "begin_pos": 17, "key": ["<numpure>"], "value_ori": "40%"}, {"len": 1, "key_dic": {}, "begin_pos": 19, "key": ["<basic>"], "value_ori": "-"}, {"len": 2, "key_dic": {"<numpure>": "0.650000"}, "begin_pos": 20, "key": ["<numpure>"], "value_ori": "65%"}]
	pat_list = [{"key_type": "*", "type": "*", "key": "*"}, {"key_type": "tag", "type": "require", "key": "<time>"}, {"key_type": "*", "type": "exclude_text", "key": "。|,|、"}, {"key_type": "tag", "type": "require", "key": "<numpure>"}, {"key_type": "*", "type": "exclude_text", "key": ","}, {"key_type": "text", "type": "require", "key": "pe"}, {"key_type": "*", "type": "*", "key": "*"}]
	pat_list = [{"key_type": "*", "type": "*", "key": "*"}, {"key_type": "tag", "type": "require_enum", "key": "<kp_p_daoqiri>"}, {"key_type": "*", "type": "include_text", "key": ":|为|约|是"}, {"key_type": "tag", "type": "require_enum", "key": "<time_day>|<time>"}]
	seg_list = [{"len": 2, "key_dic": {"<kp_p_daoqiri>": "到期日", "<kp_p_daikuan_qixian>": "到期日:"}, "begin_pos": 0, "key": ["<kp_p_daoqiri>", "<kp_p_daikuan_qixian>"], "value_ori": "到期日"}, {"len": 1, "key_dic": {"<jiedaikuan_xiang>": "为"}, "begin_pos": 2, "key": ["<jiedaikuan_xiang>"], "value_ori": "为"}, {"len": 6, "key_dic": {"<time_day>": "2016-09-05-00-00-00-00_2016-09-05-23-59-00-00", "<time>": "2016-09-05-00-00-00-00_2016-09-05-23-59-00-00"}, "begin_pos": 3, "key": ["<time_day>", "<time>"], "value_ori": "2016年9月5日"}]
	pattern_dic = {'pattern':pat_list, 'rule':[{'test':[1,2,3]}]}
	content_dic = {'seg_list':seg_list}
	res_dic = c_pat_eng.parse_one_pattern(pattern_dic, content_dic)
	print json.dumps(res_dic, ensure_ascii=False)

if __name__ == '__main__':
	sys.stdin = codecs.getreader('utf8')(sys.stdin)
	sys.stdout = codecs.getwriter('utf8')(sys.stdout)
	#logging.basicConfig(filename = '../log/PatternEngine.log', level='DEBUG', format='%(message)s')
	#test_new_pat_eng()
	#test_star_exclude()
	#test_star_include()
	test_parse_one_pattern()
	#test_pat_priority()
