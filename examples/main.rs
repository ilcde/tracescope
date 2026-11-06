fn main() {
    let numbers = [4, 8, 2, 6, 1];
    let mut total: i64 = 0;
    for value in numbers {
        total += value;
    }
    println!("{}", total);
}
