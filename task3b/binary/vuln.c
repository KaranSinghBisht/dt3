#include <stdio.h>
#define BUFSIZE 4

void win()
{
    puts("It was totally invisible Hows that possible? They used the Earths magnetic field X");
}

void vuln()
{
    puts("Input a string and it will be printed back!");
    char buf[BUFSIZE];
    gets(buf);
    puts(buf);
    fflush(stdout);
}

int main(int argc, char **argv)
{
    vuln();
    return 0;
}
