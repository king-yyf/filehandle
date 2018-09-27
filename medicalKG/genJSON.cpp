#include <cstdio>
#include <cstring>
#include <string>
#include <map>
using namespace std;

int main()
{
    FILE * f1 = fopen("/Users/yangyf/Desktop/all_name.txt", "r");
    FILE * f2 = fopen("/Users/yangyf/Desktop/all_class.txt", "r");

    FILE * f3 = fopen("/Users/yangyf/Desktop/mesh.json", "w");

    map<string, int> idMap;

    char key[300],super[300], code[100],label[200];
    string tmp;

    int count = 1,has_child,id,pId;
    idMap.emplace("A-解剖学",count++);
    idMap.emplace("B-有机体",count++);
    idMap.emplace("C-疾病",count++);
    idMap.emplace("D-药物",count++);
    idMap.emplace("E-诊疗技术及设备",count++);
    idMap.emplace("F-心理学和精神病学",count++);
    idMap.emplace("G-生物科学",count++);
    idMap.emplace("H-自然科学",count++);
    idMap.emplace("I-社会科学",count++);
    idMap.emplace("J-工艺学、工业及农业",count++);
    idMap.emplace("K-人文科学",count++);
    idMap.emplace("L-信息科学",count++);
    idMap.emplace("N-医疗保健",count++);
    idMap.emplace("Z-地理名称",count++);
    map<string, int>::iterator it;
    for(it = idMap.begin(); it != idMap.end(); it++)
    {
        tmp = it->first;
        id = it->second;
        pId = 0;
        fprintf(f3, "{ id:%d, pId:%d, name:\"%s\", open:false, icon:\"images/class.gif\"},\n", id,pId,tmp.data());
    }
    while (fscanf(f1, "%s",key) == 1)
    {
        if(idMap.count(key) > 0) continue;
        idMap.emplace(key,count++);
    }
    fclose(f1);
    while (fscanf(f2, "%s %s %d", key, super,&has_child) == 3) {
        id = idMap.at(key);
        pId = idMap.at(super);
        if(has_child)
        {
            fprintf(f3, "{ id:%d, pId:%d, name:\"%s\", open:false, icon:\"images/class.gif\"},\n", id,pId,key);
        }
        else
        {
            fprintf(f3, "{ id:%d, pId:%d, name:\"%s\", icon:\"images/datarange.png\"},\n", id,pId,key);
        }
    }
    fclose(f2);
    printf("count = %d\n",count);
    return 0;
}

