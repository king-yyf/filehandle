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
    FILE * f1 = fopen("/Users/yangyf/Desktop/file1.txt", "r");
    FILE * f2 = fopen("/Users/yangyf/Desktop/icd.txt", "r");
    FILE * f3 = fopen("/Users/yangyf/Desktop/icd10.txt", "w");
    char code[200], label[300], superCode[200];
    queue<string> que1;
    queue<string> que2;
    int count = 0;
    while (fscanf(f2, "%s %s", code, label) == 2) {
        count++;
        if(strlen(code) == 5){
            que1.push(code);
            que2.push(label);
        }
    }
    int iNum;
    string tmp,min_code,max_code,str,str1, sCode,sLabel;
    for(int i = 0; i < 22; ++i)
    {
        printf("i = : %d\n", i);
        fscanf(f1, "%s %d", superCode, &iNum);
        str = superCode;
        min_code = str.substr(0,3);
        max_code = str.substr(4,3);
        str1 = "C."+min_code+"-C."+max_code+"-" + str.substr(7);
        fprintf(f3, "%s\t%s\t%d\n", str1.data(), "C-疾病",1);
        for(int j = 0; j < iNum; ++j)
        {
            //             printf("j = : %d, iNum = %d\n", j, iNum);
            fscanf(f1, "%s %s",code, label);
            sCode = code;
            sLabel = label;
            //            sLabel = sCode + "-" + sLabel;
            tmp = code;
            min_code = tmp.substr(0,3);
            max_code = tmp.substr(4);
            sLabel = "C."+min_code + "-C." + max_code + "-" + sLabel;
            fprintf(f3, "%s\t%s\t%d\n",sLabel.data(),str1.data(),1);
            while (!que1.empty()) {
                tmp = que1.front().substr(2);
                if(tmp >= min_code && tmp <= max_code){
                    str = que1.front() + "-" + que2.front();
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
    printf("count = %d\n",count);
    return 0;
}
