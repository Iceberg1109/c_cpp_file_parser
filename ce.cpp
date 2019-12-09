#include <iostream>
#include <stdio.h>
using namespace std;
#define OK 12
int c=3;
class Box
{
   public:
      double length;  //你好
      double breadth; 
      double height;   // ���ӵĸ߶�
};

class Box
{
   public:
      static int objectCount;
      // ���캯������
      Box(double l=2.0, double b=2.0, double h=2.0)
      {
         cout <<"Constructor called." << endl;
         length = l;
         breadth = b;
         height = h;
         // ÿ�δ�������ʱ���� 1
         objectCount++;
      }
      double Volume()
      {
         return length * breadth * height;
      }
   private:
      double length;     // ����
      double breadth;    // ����
      double height;     // �߶�
};
 
// ��ʼ���� Box �ľ�̬��Ա
int Box::objectCount = 0;
 
// ����
class Shape 
{
   public:
      void setWidth(int w)
      {
         width = w;
      }
      void setHeight(int h)
      {
         height = h;
      }
   protected:
      int width;
      int height;
};
 
// ������
class Rectangle: public Shape
{
   public:
      int getArea()
      { 
         return (width * height); 
      }
};

class Box2
{
   public:
 
      double getVolume(void)
      {
         return length * breadth * height;
      }
      void setLength( double len )
      {
          length = len;
      }
 
      void setBreadth( double bre )
      {
          breadth = bre;
      }
 
      void setHeight( double hei )
      {
          height = hei;
      }
      // ���� + ����������ڰ����� Box �������
      Box2 operator+(const Box2& b)
      {
         Box box;
         box.length = this->length + b.length;
         box.breadth = this->breadth + b.breadth;
         box.height = this->height + b.height;
         return box;
      }
   private:
      double length;      // ����
      double breadth;     // ����
      double height;      // �߶�
};
class Shape1 {
   protected:
      int width, height, test;
   public:
      Shape1( int a=0, int b=0)
      {
         width = a;
         height = b;
      }
      int area()
      {
         cout << "Parent class area :" <<endl;
         return 0;
      }
};

class Rectangle: public Shape1{
   public:
      Rectangle( int a=0, int b=0):Shape1(a, b) { }
      int area ()
      { 
         cout << "Rectangle class area :" <<endl;
         return (width * height); 
      }
};
class Triangle: public Shape{
   public:
      Triangle( int a=0, int b=0):Shape(a, b) { }
      int area ()
      { 
         cout << "Triangle class area :" <<endl;
         return (width * height / 2); 
      }
};

class Adder{
   public:
      // ���캯��
      Adder(int i = 0)
      {
        total = i;
      }
      // ����Ľӿ�
      void addNum(int number)
      {
          total += number;
      }
      // ����Ľӿ�
      int getTotal()
      {
          return total;
      }
   private:
      // �������ص�����
      int total;
};

class Box4
{
private:
   double width;
public:
   friend void printWidth1( Box4 box );
   void setWidth( double wid );
};
 
// ��Ա��������
void Box4::setWidth( double wid )
{
    width = wid;
}
 
// ��ע�⣺printWidth() �����κ���ĳ�Ա����
void printWidth1( Box4 box )
{
   /* ��Ϊ printWidth() �� Box ����Ԫ��������ֱ�ӷ��ʸ�����κγ�Ա */
   cout << "Width of box : " << box.width <<endl;
}
int main(void)
{
   Box Box1(3.3, 1.2, 1.5);    // ���� box1
   Box Box2(8.5, 6.0, 2.0);    // ���� box2
 
   // ������������
   cout << "Total objects: " << Box::objectCount << endl;
 
   return 0;
}
