#include <stdio.h>
__attribute__((noinline)) int compute(int n) {
    int unused = n * 123;
    int answer = n + 1;
    __asm__ volatile ("" ::: "memory");
    printf("%d\n", answer);
    return answer;
}
int main(int argc, char **argv) {
    compute(argc);
    return 0;
}
