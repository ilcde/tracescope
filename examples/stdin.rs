use std::io;
fn main(){
 let mut text=String::new();
 io::stdin().read_line(&mut text).unwrap();
 let n:i32=text.trim().parse().unwrap();
 let result=n*3;
 println!("{}",result);
}