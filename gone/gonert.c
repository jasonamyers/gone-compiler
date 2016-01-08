/* This file contains runtime support for Gone.  
   Rather than write everything in low-level LLVM, it is often
   easier to implement certain functionality in C and link against it.
*/

#include <stdio.h>

void _print_int(int x) {
  printf("%i\n", x);
}

void _print_float(double x) {
  printf("%f\n", x);
}

void _print_bool(int x) {
  if (x == 1) {
    printf("true\n");
  } else {
    printf("false\n");
  }
}
/* 
   Bootstrapping code for creating a stand-alone executable.
   This code will be needed once you move to Project 8.  

   It provides a main() function suitable for use with the C
   compiler.  This function invokes the Gone __init() function
   to set up global variables.  It then triggers the gone main()
   function to start the program.
*/

#ifdef NEED_MAIN
extern void __init(void);
extern int _gone_main(void);

int main() {
  __init();
  return _gone_main();
}
#endif

