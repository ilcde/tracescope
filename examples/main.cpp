#include <iostream>
#include <array>
int main() {
    std::array<int, 5> numbers = {4, 8, 2, 6, 1};
    int total = 0;
    for (int value : numbers) {
        total += value;
    }
    std::cout << total << '\n';
    return 0;
}
