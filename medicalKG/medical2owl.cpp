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
#include <map>

using namespace std;

string url = "http://www.semanticweb.org/yangyf/ontologies/Medical#";
string url_prefix = "    <!-- ";
string arrow = " -->\n";
string suffix = "\"/>\n";
string class_suffix = "    </owl:Class>\n\n";
string class_prefix = "    <owl:Class rdf:about=\"";
string subclass_prefix = "        <rdfs:subClassOf rdf:resource=\"";
string file_suffix = "</rdf:RDF>\n\n<!-- Generated by the OWL API (version 4.2.8.20170104-2310) https://github.com/owlcs/owlapi -->";
string superclass = "药物";

string get_fa(string key, map<string, string> actMap)
{
    int len = (int)key.length();
    string res;
    switch (len) {
        case 1:
            res = "药物";
            break;
        case 3:
            if(actMap.count(key.substr(0,1)) > 0)
                res = actMap[key.substr(0,1)];
            else
                res = "药物";
            break;
        case 4:
            if(actMap.count(key.substr(0,3)) > 0)
                res = actMap[key.substr(0,3)];
            else
                res = get_fa(key.substr(0,3), actMap);
            break;
        case 5:
            if(actMap.count(key.substr(0,4)) > 0)
                res = actMap[key.substr(0,4)];
            else
                res = get_fa(key.substr(0,4), actMap);
            break;
        case 7:
            if(actMap.count(key.substr(0,5)) > 0)
                res = actMap[key.substr(0,5)];
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
    FILE * f1 = fopen("/Users/yangyf/Desktop/yaozhi.txt", "r");
//    FILE * f2 = fopen("/Users/yangyf/Desktop/file2.txt", "r");
    FILE * f2 = fopen("/Users/yangyf/Desktop/yaowu.owl", "w");
    char code[10], chname[200];
    map<string, string> atcCode;
      set<string> nameSet;
    string name;
    while (fscanf(f1, "%s %s", code, chname) == 2)
    {
        name = chname;
        if(nameSet.count(name) > 0)
            continue;
        else
            nameSet.insert(name);
        atcCode.emplace(code, chname);
//        if(!isalpha(code[0]))
//            cout << "code : " << code << "name: " << chname << " error ! " << endl;
//        exit(-1);
//        if(strcmp(code, "N03AF01") == 0)
//            cout << chname << endl;
    }
    map<string, string>::iterator it;
    string tmp;
    string fa;
    for(it = atcCode.begin(); it != atcCode.end(); ++it)
    {
        fa = get_fa(it->first, atcCode);
        if (fa == "error") {
            cout << "error : " << it->first << endl;
        }
        tmp = url_prefix + url + it->second + arrow + class_prefix + url + it->second +\
        "\">\n" + subclass_prefix + url + fa + suffix + class_suffix;
        fprintf(f2, "%s", tmp.c_str());
    }
    fprintf(f2, "%s", file_suffix.c_str());
    printf("ok ! \n");
    return 0;
}
