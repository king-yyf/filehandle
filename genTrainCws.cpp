//
//  main.cpp
//  dict
//
//  Created by Yang Yunfei on 2018/2/2.
//  Copyright © 2018年 Yang Yunfei. All rights reserved.
//

#include <iostream>
#include <stdio.h>
#include <vector>
#include <string>
#include <cstring>
//#include "trie.hpp"
//#include "trie_map.hpp"
#include <map>

using namespace std;

int getPos(char * str)
{
    int pos;
    if(strlen(str) == 1)
        pos = str[0] * 256;
    else
        pos = str[0] * 256 + str[1];
    return pos;
}

void str2vec(string sentence, vector<string> & words)
{
    size_t i = 0, size = sentence.length();
    while (i < size) {
        int cnt = 1;
        if(sentence[i] & 0x80){
            char ch = sentence[i];
            ch <<= 1;
            do{
                ch <<= 1;
                ++cnt;
            }while (ch & 0x80);
            words.emplace_back(sentence.substr(i, cnt));
            i += cnt;
        }else{
            char ch = sentence[i];
            size_t pos;
            if(isdigit(ch)){
                std::stod(sentence.substr(i), &pos);
                words.emplace_back(sentence.substr(i,pos));
                i += pos;
            }else if(isalpha(ch)){
                size_t cnt = 1;
                while(i + cnt < size && isalpha(sentence[i + cnt])){
                    cnt++;
                }
                words.emplace_back(sentence.substr(i, cnt));
                i += cnt;
            }else{
                words.emplace_back(sentence.substr(i,1));
                i++;
            }
        }
    }
}

int main(int argc, const char * argv[]) {
    
    
    FILE * fp_in = fopen("/Users/yangyf/Desktop/intern/corpus/train.txt", "r");
    FILE * fp_out = fopen("/Users/yangyf/Desktop/intern/corpus/segpos.utf8", "w");
    char word[100], tag[8], ch[10], begin[8];// in[3] = "I";

    while (!feof(fp_in))
    {
        fscanf(fp_in, "%s%s%s",word, tag, ch);
        if(strcmp(tag, "w") == 0){
            fprintf(fp_out, "\n");
            continue;
        }
        string str = word;
        vector<string> words;
        str2vec(str, words);
        if(words.size() == 0) continue;
        else{
            for(size_t i = 0; i < words.size(); ++i)
            {
                if(i == 0){
                    strcpy(begin, "B-");
                    strcat(begin, tag);
                    fprintf(fp_out, "%s\t%s\n", words[i].c_str(), begin);
                }else{
                    strcpy(ch, "I-");
                    strcat(ch, tag);
                    fprintf(fp_out, "%s\t%s\n", words[i].c_str(), ch);
                }
                
            }
        }
    }
    fclose(fp_in);
    fclose(fp_out);
 
    cout<<"ok!" << endl;
    return 0;
}


//    map<string, int> tag2int =
//    {
//        {"Ag", 16743}, {"Bg", 16999}, {"Dg", 17511}, {"Mg", 19815}, {"Ng", 20071},
//        {"Rg", 21095}, {"Tg", 21607}, {"Vg", 22119}, {"Yg", 22887}, {"a", 24832},
//        {"ad", 24932}, {"an", 24942}, {"b", 25088}, {"c", 25344}, {"d", 25600},
//        {"e", 25856}, {"f", 26112}, {"h", 26624}, {"i", 26880}, {"j", 27136},
//        {"k", 27392}, {"l", 27648}, {"m", 27904}, {"n", 28160}, {"nr", 28274},
//        {"ns", 28275}, {"nt", 28276}, {"nx", 28280}, {"nz", 28282}, {"o", 28416},
//        {"p", 28672}, {"q", 28928}, {"r", 29184}, {"s", 29440}, {"t", 29696},
//        {"u", 29952}, {"v", 30208}, {"vd", 30308}, {"vn", 30318}, {"w", 30464},
//        {"y", 30976}, {"z", 31232}
//    };
//    test case
//    int i = 17511, j = 29440;
//    char s1[3], s2[3];
//    s1[0] = (i >> 8) & 0xFF, s1[1] = i & 0xFF;
//    s2[0] = (j >> 8) & 0xFF, s2[1] = j & 0xFF;
//    printf("%s, %s\n", s1, s2);
