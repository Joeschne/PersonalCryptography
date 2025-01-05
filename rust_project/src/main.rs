fn main() {
    let string1 = String::from("Hello");
    let string2 = String::from("Rust");

    print_two_strings(&string1, &string2);

    println!("Original strings: {}, {}", string1, string2);
}

fn print_two_strings(input1: &str, input2: &str) {
    println!("{} and {}", input1, input2);
}