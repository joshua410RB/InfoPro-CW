#include <iostream>
#include <fstream>
using namespace std;

int main(){
    ofstream myfile;
    std::string x; 
    myfile.open ("example.txt" , ios_base::app);
    while (cin){
        cin >> x;
        myfile << x+"\n";
    }
    myfile.close();
    return 0;
} 