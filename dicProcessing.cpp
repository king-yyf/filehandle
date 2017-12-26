#include <iostream>
#include <cstdio>
#include <map>
#include <fstream>
#include <sstream>
#include <cstring>
#include <string>
#include "trie.hpp"
using namespace std;
//using namespace detail;

int main(int argc, const char * argv[]) {
    //trie<string> t;
    FILE * fp_dic_small = fopen("/Users/yangyf/Desktop/intern/dict/dict.txt.small", "r");
    FILE * fp_dic_big = fopen("/Users/yangyf/Desktop/intern/dict/dict.txt.big", "r");
    FILE * fp_pos = fopen("/Users/yangyf/Desktop/intern/dict/pos.utf8", "r");
    FILE * fp_small = fopen("/Users/yangyf/Desktop/intern/dict/dict_small.txt", "w");
    FILE * fp_big = fopen("/Users/yangyf/Desktop/intern/dict/dict_big.txt", "w");
    FILE * fp_tag = fopen("/Users/yangyf/Desktop/intern/dict/tag_dic.txt", "w");
    FILE * fp_test = fopen("/Users/yangyf/Desktop/intern/dict/test.txt", "w");
    map<string,string> dict1;
    map<string,string> dict;
    map<string,string> dict2;
 //   map<string, string> test1;
    char word[100],pos[16]; int num;
    string str,tag;
    while (!feof(fp_dic_small)) {
        fscanf(fp_dic_small, "%s%d%s",word,&num,pos);
        str = word;
        tag = pos;
        dict1.emplace(str, tag);
        dict.emplace(str, tag);
    }
    fclose(fp_dic_small);
    while (!feof(fp_dic_big)) {
        fscanf(fp_dic_big, "%s%d%s",word,&num,pos);
        str = word;
        tag = pos;
        dict2.emplace(str, tag);
        dict.emplace(str, tag);
    }
    fclose(fp_dic_big);
   // char * pch;
    while (fscanf(fp_pos, "%s", word) != EOF) {
        str = word;
//        str = word;
//        tag = pos;
        size_t id = str.find(',');
        tag = str.substr(id + 1);
        str = str.substr(0,id);
        dict1.emplace(str, tag);
        dict2.emplace(str, tag);
        dict.emplace(str, tag);
    }
    fclose(fp_pos);
    map<string, string>::iterator it;
    for(it = dict.begin(); it != dict.end(); ++it)
    {
        fprintf(fp_tag, "%s %s\r", it->first.c_str(), it->second.c_str());
    }
    for(it = dict1.begin(); it != dict1.end(); ++it)
    {
        if(it->first.length() > 4 && it->first.length() < 27)
        fprintf(fp_small, "%s\r", it->first.c_str());
    }
    for(it = dict2.begin(); it != dict2.end(); ++it)
    {
        if(it->first.length() > 4)
        fprintf(fp_big, "%s\r", it->first.c_str());
    }
    fclose(fp_tag);
    fclose(fp_big);
    fclose(fp_small);
    cout<< "ok" <<endl;
    return 0;
}
