#include <stdio.h>
int sum(int *numbers, int n) {
    int total = 0;
    for (int i = 0; i < n; i++) {
        total += numbers[i];
    }
    return total;
}
int main(void) {
    int numbers[] = {4, 8, 2, 6, 1};
    int result = sum(numbers, 5);
    printf("%d\n", result);
    return 0;
}
