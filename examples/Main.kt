fun sum(numbers: IntArray): Int {
    var total = 0
    for (value in numbers) {
        total += value
    }
    return total
}
fun main() {
    val numbers = intArrayOf(4, 8, 2, 6, 1)
    val result = sum(numbers)
    println(result)
}
