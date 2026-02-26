#include <stdio.h>

int add(int a, int b) { return a + b; }

void print_message(const char *message) { printf("Message: %s\n", message); }

int multiply(int a, int b) {
  int result = 0;
  result = a * b;
  return result;
}

int main() {
  int x = 10;
  int y = 20;
  int sum = add(x, y);
  print_message("Hello from C!");
  int product = multiply(sum, 2);
  printf("Sum: %d, Product: %d\n", sum, product);
  return 0;
}
