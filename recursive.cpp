// Compile command: g++-7 -O0 -g -Wall -o recursive recursive.cpp

#include <iostream>

int fibonacci(int n)
{
  if (n <= 2)
    return 1;
  else
    return fibonacci(n-1) + fibonacci(n-2);
}

int main()
{
  fibonacci(4);
  return 0;
}
