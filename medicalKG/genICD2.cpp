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

set<string> diseaseSet;
int main(int argc, const char * argv[]) {
    // insert code here...
//    FILE * f1 = fopen("/Users/yangyf/Desktop/file1.txt", "r");
    FILE * f2 = fopen("/Users/yangyf/Desktop/icdatc.txt", "r");
    FILE * f3 = fopen("/Users/yangyf/Desktop/icd_ind.properties", "w");
    char code[200], label[300];
    string tmp,min_code,max_code,str, sCode,sLabel;
    while (fscanf(f2, "%s %s", code, label) == 2) {
        sCode = code;
        sLabel = label;
        if(strlen(code) == 5){
            str = sCode + "-" + sLabel;
        }
        else{
            sLabel = sCode + "-" + sLabel;
            fprintf(f3, "%s = %s\n", sLabel.data(),str.data());
        }
    }
    printf("ok !\n");
    return 0;
}


