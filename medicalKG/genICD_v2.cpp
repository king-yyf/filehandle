#include <cstdio>
#include <cstring>
#include <string>
#include <queue>
#include <map>
using namespace std;

int main()
{
    FILE * f1 = fopen("/Users/yangyf/Desktop/icd-range.txt", "r");
    FILE * f2 = fopen("/Users/yangyf/Desktop/icd_name_v2.txt", "r");
    FILE * f3 = fopen("/Users/yangyf/Desktop/icd_rel.txt", "w");
    map<string,string> icdMap;
    map<string,string> icdMap2;
    queue<string> que1;
    queue<string> que2;
    char code [100], label[200],superCode[200];
    while (fscanf(f2, "%s %s", code, label) == 2)
    {
        if(strlen(code) == 3){
            icdMap.emplace(code,label);
            que1.push(code);
            que2.push(label);
        }
        else
            icdMap2.emplace(code,label);
    }
    string min_code, max_code, sCode,sLabel,str,str1,tmp;
    int iNum;
    for(int i = 0; i < 22; i++)
    {
        fscanf(f1, "%s %d",superCode,&iNum);
        str = superCode;
        min_code = str.substr(0,3);
        max_code = str.substr(4,3);
        str1 = "C."+min_code+"-C."+max_code+"-" + str.substr(7);
        fprintf(f3, "%s\t%s\t%d\n", str1.data(), "C-疾病",1);
        for(int j = 0; j < iNum; ++j){
            fscanf(f1, "%s %s",code, label);
            sCode = code;
            sLabel = label;
            tmp = code;
            min_code = tmp.substr(0,3);
            max_code = tmp.substr(4);
            sLabel = "C."+min_code + "-C." + max_code + "-" + sLabel;
            fprintf(f3, "%s\t%s\t%d\n",sLabel.data(),str1.data(),1);
            while (!que1.empty()) {
                tmp = que1.front();
                if(tmp >= min_code && tmp <= max_code){
                    str = "C." + que1.front() + "-" + que2.front();
                    fprintf(f3, "%s\t%s\t%d\n", str.data(), sLabel.data(),1);
                    que1.pop();
                    que2.pop();
                }
                else{
                    break;
                }
            }
        }
    }
    
    map<string,string>::iterator it;
    for(it = icdMap2.begin(); it != icdMap2.end(); it++)
    {
        sCode = it->first;
        sLabel = it->second;
        str = sCode.substr(0,3);
        tmp = "C." + sCode + "-" + sLabel;
        str1 = "C." + str + "-" + icdMap[str];
        fprintf(f3, "%s\t%s\t%d\n",tmp.data(),str1.data(),0);
    }
    printf("ok!\n");
    return 0;
}
