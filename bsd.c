#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#define PI 3.1415
// size_t strlcat(char *dst, const char *src, size_t size);
void uninitvar_strlcat(char *Ct, const char *S, size_t N)
{
    char *ct;
    char *s;
    size_t n;
    // cppcheck-suppress uninitvar
    (void)strlcat(ct,s,n);
    // cppcheck-suppress uninitvar
    (void)strlcat(ct,S,N);
    // cppcheck-suppress uninitvar
    (void)strlcat(Ct,s,N);
    // cppcheck-suppress uninitvar
    (void)strlcat(Ct,S,n);

    // no warning is expected for
    (void)strlcat(Ct,S,N);
}

void bufferAccessOutOfBounds(void)
{
    uint16_t uint16Buf[4];
    // cppcheck-suppress bufferAccessOutOfBounds
    arc4random_buf(uint16Buf, 9);
    // valid
    arc4random_buf(uint16Buf, 8);
}

void ignoredReturnValue(void)
{
    // cppcheck-suppress ignoredReturnValue
    arc4random();
    // cppcheck-suppress ignoredReturnValue
    arc4random_uniform(10);
}

void uninitvar(void)
{
    uint32_t uint32Uninit;

    // cppcheck-suppress uninitvar
    (void) arc4random_uniform(uint32Uninit);/*
    int main */
}

int Add(int a,int b)
{
	int result;
	result=a+b;
	if( a < 20 )
	{
       	printf("a  20\n" );
   	}
   	else
   	{
       	printf("a  20\n" );
   	}
	return result;
}
char xstr[12] = "Hello";
int main(void)
{
   char str1[12] = "Hello";
   char str2[12] = "World";
   char str3[12];
   int  len;
   len=3;
   int b=4;
   int c;
   c=Add(len,b);
   printf("%d",c);
   return 0;
}
