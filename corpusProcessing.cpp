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
using namespace std;
typedef pair<string, string> PAIR;

class Encode{
public:
    static void sbc2dbc(const char * src, string& result)   //全角转半角
    {
        size_t len=strlen(src);
        char * buf=new char[len+1];
        int j=0;
        for(size_t i=0;i<len;i++)
        {
            if((unsigned char)src[i] > 163)
            {
                buf[j++]=src[i++];
                buf[j++]=src[i];
                continue;
            }
            else if((unsigned char)src[i]==163)
            {
                i++;
                buf[j++]=(unsigned char)src[i]-128;
                continue;
            }
            else if((unsigned char)src[i]==161&&(unsigned char)src[i+1]==161)
            {
                i++;
                buf[j++]=' ';
                continue;
            }
            else if((unsigned char)src[i]==161&&(unsigned char)src[i+1]!=161)
            {
                buf[j++]=src[i++];
                buf[j++]=src[i];
                continue;
            }
            else
            {
                buf[j++]=src[i];
            }
        }
        buf[j]=0;
        result=buf;
        delete[] buf;
    }
    
    static void dbc2sbc(const char * src, string& result)
    {
        size_t len=strlen(src);
        char * buf=new char[len*2+1];
        int j=0;
        for(size_t i=0;i<len;i++)
        {
            if((unsigned char)src[i] >= 163||(unsigned char)src[i]==161)
            {
                buf[j++]=src[i++];
                buf[j++]=src[i];
                continue;
            }
            else if((unsigned char)src[i]==32)
            {
                buf[j++]=(char)161;
                buf[j++]=(char)161;
                continue;
            }
            else if(((unsigned char)src[i]>='a'&&(unsigned char)src[i]<='z')||
                    ((unsigned char)src[i]>='A'&&(unsigned char)src[i]<='Z')||
                    (unsigned char)src[i]>=128)
            {
                buf[j++]=src[i];
                continue;
            }
            else
            {
                buf[j++]=(char)163;
                buf[j++]=src[i]+128;
                continue;
            }
        }
        buf[j]=0;
        result=buf;
        delete[] buf;
    }
    
    
};


bool isner(string tag)
{
    if(tag == "t" || tag == "nr" || tag == "m" || tag == "ns" || tag == "nt")
        return true;
    return false;
}

void gettag(string & str, string & pos_tag, string & ner_tag, string prepos)
{
    if(isner(pos_tag))
    {
        if(prepos == pos_tag)
        {
            ner_tag = "I-" + pos_tag;
        }
        else
        {
            ner_tag = "B-" + pos_tag;
        }
    }
    else
    {
        ner_tag = "O";
    }
}

int main(int argc, const char * argv[]) {
    //trie<string> t;
    FILE * fp_in;
    FILE * fp_out;
    string in_file = "/Users/yangyf/Desktop/intern/corpus/19980";
    string out = "_out";
    string suffix = ".txt";
    string result, str, postag, nertag, temp, prepos;
    char line[2048*4]; // word[500], pos_tag[10], ner_tag[10];
    
    //word :词
    //pos_tag :词性标注
    //ner_tag :实体识别标注
   //循环处理1月到6月的语料文件
    //{B I O} * {nr, ns, m, t, nt}
    vector<string> buff;
    bool in_kuohao = false;
    for(int i = 1; i < 7; ++i)
    {
      //  cout << i << endl;
        string r_file = in_file + to_string(i) + suffix;
        string w_file = in_file + to_string(i) + out + suffix;
        fp_in = fopen(r_file.c_str(), "r");
        fp_out = fopen(w_file.c_str(), "w");
        while (!feof(fp_in)) {
           // cout << "open file "<< r_file << " ok !" << endl;
            fgets(line, 8192, fp_in);
            //全角转半角 GBK编码
            Encode::sbc2dbc(line, result);
            strcpy(line, result.c_str());
            char * pch;
            pch = strtok(line, " ");
            while (pch != NULL) {
                str = pch; // eg str: 迈向/v
                if(str == "\r\n" || str == "\n" || str == " ")
                {
                     pch = strtok(NULL, " ");
                    continue;
                }
                   
                size_t id = str.find('/');
                prepos = postag;
                postag = str.substr(id + 1); //v; n]nt;
                str = str.substr(0, id); // 迈向; [中国 ;
                //cout << str << " --- " << postag << endl;
                if(in_kuohao)
                {
                    buff.emplace_back(str);
                    size_t idx = postag.find(']');
                    if(idx != string::npos){
                        nertag = postag.substr(idx + 1);
                        postag = postag.substr(0, idx);
                        for(size_t j = 0; j < buff.size(); ++j)
                        {
                            if(j == 0)
                            {
                                temp = "B-" + nertag;
                            }
                            else{
                                temp = "I-" + nertag;
                            }
                            fprintf(fp_out, "%s\t%s\t%s\n", buff[j].c_str(), postag.c_str(), temp.c_str());
                        }
                        in_kuohao = false;
                        buff.clear();
                    }
                }else if(str[0] == '[')
                {
                    in_kuohao = true;
                    buff.emplace_back(str.substr(1));
                }else
                {
                    gettag(str, postag, nertag, prepos);
                    fprintf(fp_out, "%s\t%s\t%s\n", str.c_str(), postag.c_str(), nertag.c_str());
                }
                pch = strtok(NULL, " ");
            }
            fprintf(fp_out, "\n");
        }
        fclose(fp_in);
        fclose(fp_out);
    }
    cout<< "ok" <<endl;
    return 0;
}
