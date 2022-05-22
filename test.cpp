// Compile command: g++-7 -O0 -g -Wall -o test test.cpp

#include <iostream>

void func9()
{ // end
}
void func7_1()
{ // end
}
void func8()
{
  func9();
}
void func7()
{
  func7_1();
  func8();
}
void func5_1()
{ // end
}
void func6()
{
  func7();
}
void func5()
{
  func5_1();
  func6();
}
void func4()
{
  func5();
}
void func3_1()
{ // end
}
void func2_1()
{ // end
}
void func3()
{
  func4();
  func3_1();
}
void func2()
{
  func2_1();
  func3();
}
void func1()
{
  func2();
}

int main()
{
  func1();
  return 0;
}
