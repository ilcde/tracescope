public class Main {
    static int sum(int[] numbers) {
        int total = 0;
        for (int value : numbers) {
            total += value;
        }
        return total;
    }
    public static void main(String[] args) {
        int[] numbers = {4, 8, 2, 6, 1};
        int result = sum(numbers);
        System.out.println(result);
    }
}
