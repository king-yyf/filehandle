//
//  main.cpp
//  txt2owl
//
//  Created by Yang Yunfei on 2018/7/16.
//  Copyright © 2018年 Yang Yunfei. All rights reserved.
//

#include <iostream>
#include <set>
#include <cstring>
#include <string>
#include <queue>
#include <map>

using namespace std;

string get_fa(string key, map<string, string> actMap)
{
    int len = (int)key.length();
    string res;
    switch (len) {
        case 1:
            res = "D药物";
            break;
        case 3:
            if(actMap.count(key.substr(0,1)) > 0)
                res = key.substr(0,1) + "-" +actMap[key.substr(0,1)];
            else
                res = "D药物";
            break;
        case 4:
            if(actMap.count(key.substr(0,3)) > 0)
                res = key.substr(0,3) + "-" + actMap[key.substr(0,3)];
            else
                res = get_fa(key.substr(0,3), actMap);
            break;
        case 5:
            if(actMap.count(key.substr(0,4)) > 0)
                res = key.substr(0,4) + "-" + actMap[key.substr(0,4)];
            else
                res = get_fa(key.substr(0,4), actMap);
            break;
        case 7:
            if(actMap.count(key.substr(0,5)) > 0)
                res = key.substr(0,5) + "-" + actMap[key.substr(0,5)];
            else
                res = get_fa(key.substr(0,5), actMap);
            break;
        default:
            res = "error";
            break;
    }
    return res;
}
int main(int argc, const char * argv[]) {
    // insert code here...
//    FILE * f1 = fopen("/Users/yangyf/Desktop/file1.txt", "r");
    FILE * f2 = fopen("/Users/yangyf/Desktop/atc.txt", "r");
    FILE * f3 = fopen("/Users/yangyf/Desktop/atc_class.properties", "w");
    FILE * f4 = fopen("/Users/yangyf/Desktop/atc_ind.properties", "w");
    char code[100], chname[200];
    map<string, string> atcCode;
    set<string> nameSet;
    string name;
    string key,value;
    while (fscanf(f2, "%s %s", code, chname) == 2)
    {
//        name = chname;
//        if(nameSet.count(name) > 0)
//            continue;
//        else
//            nameSet.insert(name);
        key = code;
        atcCode.emplace(key.substr(2), chname);
    }
    map<string, string>::iterator it;
    string fa;
    for(it = atcCode.begin(); it != atcCode.end(); ++it)
    {
        fa = get_fa(it->first, atcCode);
        if (fa == "error") {
            cout << "error : " << it->first << endl;
        }
        key = "D." + it->first + "-" + it->second;
        fa = "D." + fa;
        
        if(it->first.length() == 7)
        {
            fprintf(f4, "%s = %s\n",key.data(), fa.data());
            //            fprintf(f3, "%s", tmp.c_str());
        }
        else
        {
            fprintf(f3, "%s = %s\n",key.data(), fa.data());
        }
    }
    printf("ok!\n");
    return 0;
}

