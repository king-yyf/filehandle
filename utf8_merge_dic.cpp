//
//  main.cpp
//  encode
//
//  Created by Yang Yunfei on 2017/11/21.
//  Copyright © 2017年 Yang Yunfei. All rights reserved.
//

#include <iostream>
#include <cstdio>
#include <map>
#include <fstream>
#include <sstream>
#include <cstring>
#include <string>
#include "trie.hpp"
#include "encode.hpp"
#include <cctype>
using namespace std;
typedef pair<string, string> PAIR;

const map<string, char>  sbcMap =
{
    {"０", '0'}, {"１", '1'}, {"２", '2'}, {"３", '3'}, {"４", '4'},
    {"５", '5'}, {"６", '6'}, {"７", '7'}, {"８", '8'}, {"９", '9'},
    {"Ａ", 'A'}, {"Ｂ", 'B'}, {"Ｃ", 'C'}, {"Ｄ", 'D'}, {"Ｅ", 'E'},
    {"Ｆ", 'F'}, {"Ｇ", 'G'}, {"Ｈ", 'H'}, {"Ｉ", 'I'}, {"Ｊ", 'J'},
    {"Ｋ", 'K'}, {"Ｌ", 'L'}, {"Ｍ", 'M'}, {"Ｎ", 'N'}, {"Ｏ", 'O'},
    {"Ｐ", 'P'}, {"Ｑ", 'Q'}, {"Ｒ", 'R'}, {"Ｓ", 'S'}, {"Ｔ", 'T'},
    {"Ｕ", 'U'}, {"Ｖ", 'V'}, {"Ｗ", 'W'}, {"Ｘ", 'X'}, {"Ｙ", 'Y'},
    {"Ｚ", 'Z'},
    {"ａ", 'a'}, {"ｂ", 'b'}, {"ｃ", 'c'}, {"ｄ", 'd'}, {"ｅ", 'e'},
    {"ｆ", 'f'}, {"ｇ", 'g'}, {"ｈ", 'h'}, {"ｉ", 'i'}, {"ｊ", 'j'},
    {"ｋ", 'k'}, {"ｌ", 'l'}, {"ｍ", 'm'}, {"ｎ", 'n'}, {"ｏ", 'o'},
    {"ｐ", 'p'}, {"ｑ", 'q'}, {"ｒ", 'r'}, {"ｓ", 's'}, {"ｔ", 't'},
    {"ｕ", 'u'}, {"ｖ", 'v'}, {"ｗ", 'w'}, {"ｘ", 'x'}, {"ｙ", 'y'},
    {"ｚ", 'z'}, {"　", ' '}, {"．", '.'}
};

static bool sbc2dbc(const string & sbcStr, char & dbcChar)
{
    if(sbcMap.count(sbcStr) > 0)
    {
        dbcChar = sbcMap.at(sbcStr);
        return true;
    }
    return false;
}

//全半角转换，只支持utf-8编码方式
static void sbc2dbc(const string & input, string & output)
{
    output.clear();
    size_t i = 0, len = input.length();
    size_t cnt = 1;
    string word = "";
    char dbcChar;
    while (i < len)
    {
        if(input[i] & 0x80)
        {
            char ch = input[i];
            ch <<= 1;
            do{
                ch <<= 1;
                ++cnt;
            }while (ch & 0x80);
            word = input.substr(i, cnt);
            bool ok = sbc2dbc(word, dbcChar);
            if(ok)
            {
                output.append(1, dbcChar);
            }
            else
            {
                output += word;
            }
            i += cnt;
            cnt = 1;
        }
        else{
            output.append(1, input[i]);
            i++;
        }
    }
}

int main(int argc, const char * argv[]) {
    //trie<string> t;
    FILE * fp_in;
    FILE * fp_out;
    map<string, string> tagmap;
    
    fp_in = fopen("/Users/yangyf/Desktop/intern/dict/tag_dic.txt", "r");
    char word[100], tag[16];
    while (!feof(fp_in))
    {
        fscanf(fp_in, "%s%s", word, tag);
        string input = word, output = word;
        sbc2dbc(input, output);
        tagmap.emplace(output, tag);
    }
    fclose(fp_in);
    fp_in = fopen("/Users/yangyf/Desktop/intern/tag_utf8.txt", "r");
    while (!feof(fp_in))
    {
        fscanf(fp_in, "%s%s", word, tag);
//        string input = word, output = word;
//        sbc2dbc(input, output);
        tagmap.emplace(word, tag);
    }
    fclose(fp_in);
    fp_out = fopen("/Users/yangyf/Desktop/intern/tag_dic.txt", "w");
    map<string, string>::iterator it;
    for(it = tagmap.begin(); it != tagmap.end(); ++it)
    {
       // if(! it->first.empty())
            fprintf(fp_out, "%s %s\r", it->first.c_str(), it->second.c_str());
    }
    fclose(fp_out);
    cout<< "ok" <<endl;
    
    return 0;
}
