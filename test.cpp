// Compile command: g++-7 -O0 -g -Wall -o test test.cpp

#include <iostream>
#include <vector>

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
void func4(const char *)
{
  func5();
}
template<typename T1, typename T2>
void func3_1(T1, T2)
{ // end
}
void func2_1(int, int)
{ // end
}
void func3()
{
  func4("");
  func3_1(float(0.0), double(0.0));
}
void func2()
{
  func2_1(std::rand(), std::rand());
  func3();
}
template<typename T>
std::vector<T> func1(T)
{
  func2();
  return {};
}

int main()
{
  func1(int(0.0));
  return 0;
}
