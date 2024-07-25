extern crate num_bigint;
extern crate num_primes;
extern crate rand;
extern crate ff;

use num_bigint::BigUint;
use num_primes::Generator;
use rand::Rng;

// Represents an element of a finite field
struct FiniteFieldElement {
    value: BigUint,
    modulus: BigUint,
}

// Implements the methods of the FiniteFieldElement struct
    impl FiniteFieldElement {
    fn new(value: BigUint, modulus: BigUint) -> Self {
        let value = value % &modulus;
        Self { value, modulus };
    }

    fn add(&self, other: &Self) -> Self {
        Self::new((&self.value + &other.value) % &self.modulus, self.modulus.clone())
    }

    fn sub(&self, other: &Self) -> Self {
        Self::new((&self.value + &self.modulus - &other.value) % &self.modulus, self.modulus.clone())
    }

    fn mul(&self, other: &Self) -> Self {
        Self::new((&self.value * &other.value) % &self.modulus, self.modulus.clone())
    }

    fn inv(&self) -> Self {
        Self::new(self.value.modpow(&(&self.modulus -2u32), &self.modulus), self.modulus.clone())
    }
}

#[derive(Debug, Clone)]
struct FiniteField {
    modulus: BigUint,
}

impl FiniteField {
    fn new(modulus: BigUint) -> Self {
        Self { modulus }
    }

    fn element(&self, value: BigUint) -> FiniteFieldElement {
        FiniteFieldElement::new(value, self.modulus.clone())
    }
}

// Represents an elliptic curve of the form y^2 = x^3 + Ax over a prime field
struct EllipticCurve {
    field: FiniteField,
    a: FiniteFieldElement
}

// Implements the methods of the EllipticCurve struct
impl EllipticCurve {
    fn new(field: FiniteField, a: BigUint) -> Self {
        let a_element = field.element(a);
        Self { field, a: a_element }
    }

    fn point(&self, x: BigUint, y: BigUint) -> EllipticCurvePoint {
        EllipticCurvePoint::new(self.field.element(x), self.field.element(y), self.a.clone())
    }
}

// Represents a point on an elliptic curve
struct EllipticCurvePoint {
    x: FiniteFieldElement,
    y: FiniteFieldElement,
    a: FiniteFieldElement,
}

// Implements the methods of the EllipticCurvePoint struct
impl EllipticCurvePoint {
    fn new(x: FiniteFieldElement, y: FiniteFieldElement, a: FiniteFieldElement) -> Self {
        Self { x, y, a }
    }

    fn add(&self, other: &Self) -> Self {
        if self.x.value == other.x.value && self.y.value == other.y.value {
            return self.double();
        }

        let lambda = (other.y.sub(&self.y)).mul(&other.x.sub(&self.x).inv());
        let x3 = lambda.mul(&lambda).sub(&self.x).sub(&other.x);
        let y3 = lambda.mul(&self.x.sub(&x3)).sub(&self.y);

        Self::new(x3, y3, self.a.clone())
    }

    fn double(&self) -> Self {
        let two = FiniteFieldElement::new(BigUint::from(2u32), self.x.modulus.clone());
        let three = FiniteFieldElement::new(BigUint::from(3u32), self.x.modulus.clone());
        let lambda = self.x.mul(&self.x).mul(&three).add(&self.a).mul(&two.mul(&self.y).inv());
        let x3 = lambda.mul(&lambda).sub(&self.x).sub(&self.x);
        let y3 = lambda.mul(&self.x.sub(&x3)).sub(&self.y);

        Self::new(x3, y3, self.a.clone())
    }
}


// Generate parameters for the CSIDH protocol
fn gen_params(n: usize, a: BigUint) -> (BigUint, Vec<BigUint>, FiniteField, EllipticCurve) {
    // Get the list of n primes
    let mut l_primes: Vec<BigUint> = Generator::new_prime_iterator().take(n + 1).skip(1).collect();
    
    // Generate the parameter p from the list of primes
    let mut p = BigUint::from(4u64);
    for prime in &l_primes {
        p *= prime;
    }
    p -= 1;

    // Ensure that p is prime
    while !num_primes::Verification::is_prime(&p) {
        let x = Generator::new_prime(&l_primes[l_primes.len() - 1] + 1);
        l_primes.push(x.clone());
        p = (&p + 1u64) * &x - 1u64;
    }

    let F = FiniteField::new(p.clone());
    let E0 = EllipticCurve::new(F.clone(), a);

    (p, l_primes, F, E0)
}

fn gen_key(n: usize, m: i64) -> Vec<i64> {
    let mut rng = rand::thread_rng();
    (0..n).map(|_| rng.gen_range(-m..=m)).collect()
}

fn main() {
    println!("Main method executed");
}
