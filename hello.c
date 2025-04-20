#include <cs50.h>
#include <stdio.h>

int main(void)
{

    int i = 3;
    while (i > 0)
    { printf ("i \n" );
    i --;
}
    int x = get_int("what is x?");
    int y = get_int("what is y?");

    if (x > y)
    {
        printf("x > y");
    }


    char c = get_char("Give input");
    if (c == 'n')
    {
        printf("less than");
    }
}
