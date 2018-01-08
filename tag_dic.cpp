#include <string>
#include "trie.hpp"
#include "encode.hpp"
#include <cctype>
using namespace std;
typedef pair<string, string> PAIR;

int main(int argc, const char * argv[]) {
    //trie<string> t;
    FILE * fp_in;
    FILE * fp_out;
    string in_file = "/Users/yangyf/Desktop/intern/corpus/19980";
    string suffix = ".txt";
    map<string, string> tagmap;
    char line[8094];
    string result, str, word, postag;
    for(int i = 1; i < 7; ++i)
    {
      //  bool in_kuohao = false;
        string r_file = in_file + to_string(i) + suffix;
        fp_in = fopen(r_file.c_str(), "r");
        cout << "i : " << i << endl;
        while (!feof(fp_in))
        {
            fgets(line, 8192, fp_in);
            Encode::sbc2dbc(line, result);
            strcpy(line, result.c_str());
            char * pch = NULL;
            pch = strtok(line, " ");
            while (pch != NULL) {
                str = pch;  // eg str: 迈向/v。 [中国/ns。  政府/n]nt。
                if(str == "\r\n" || str == "\n" || str == " ")
                {
                    //  is_blank = true;
                    pch = strtok(NULL, " ");
                    continue;
                }
                size_t id;
                if(str[0] == '/')
                    id = str.find('/', 1);
                else
                    id = str.find('/');
                postag = str.substr(id + 1);// v; n]nt
                str = str.substr(0, id);   // 迈向; [中国
              //  cout << str << " --- " << postag << endl;
                if(str[0] == '[')
                    str = str.substr(1);
                size_t pos = postag.find(']');
                if(pos != string::npos)
                {
                    postag = postag.substr(0, pos);
                }
                tagmap.emplace(str, postag);
//                if( i == 6)
//                    printf("%s\n", pch);
                pch = strtok(NULL, " ");
            }
        }
        fclose(fp_in);
    }
    cout << "ok i" << endl;

  
    fp_out = fopen("/Users/yangyf/Desktop/intern/tag_dic1.txt", "w");
    map<string, string>::iterator it;
    for(it = tagmap.begin(); it != tagmap.end(); ++it)
    {
        if(! it->first.empty())
            fprintf(fp_out, "%s %s\r", it->first.c_str(), it->second.c_str());
    }
    fclose(fp_out);
    cout<< "ok" <<endl;
    
    return 0;
}
