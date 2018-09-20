#include <cstdio>
#include <cstring>
#include <string>
#include <map>
using namespace std;
int main(){
    FILE * f1 = fopen("/Users/yangyf/Desktop/mesh.txt", "r");
    FILE * f2 = fopen("/Users/yangyf/Desktop/mesh_new.txt", "r");
    FILE * f3 = fopen("/Users/yangyf/Desktop/mesh_class.properties", "w");
    FILE * f4 = fopen("/Users/yangyf/Desktop/mesh_ind.properties", "w");
    map<string,string> meshMap;
    char code[300],label[300];
    string key,value,tmp;
    int count = 0;
    while (fscanf(f2, "%s %s",code,label) == 2) {
        key =code;
        value = label;
        meshMap.emplace(key,value);
        count++;
    }
    fclose(f2);
    char superCode[300];
    int n = 0;
   
    while (fscanf(f1, "%s %s %d", code, superCode, &n) == 3) {
        
        key = code;
        value = superCode;
        key = key + "-" + meshMap[code];
        value = value + "-" + meshMap[superCode];
        fprintf(f3, "%s = %s\n",key.data(),value.data());
        if(n == 0)
            fprintf(f4, "%s = %s\n",key.data(),value.data());
    }
    printf("count = %d\n",count);
    return 0;
}
