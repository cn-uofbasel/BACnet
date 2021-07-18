package com.example.p2pgeocaching.RSA;

import android.content.Context;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.List;

/**
 * This is a class which tests the security of the RSA implementation used in this
 * project. The test is written explicitely in a very naive way, to test how much
 * time a basic and inefficient program would take to break RSA
 */
public class SecurityTest {

    /**
     * This is a method which tries to break RSA implementation in a naive way
     * by going through all combinations between the numbers 2 to n.
     * So the complexity will be in O(n^2). Furthermore, it creates an own key
     * and prints out how much time it took to calculate the correct private key
     *
     * @param c Context used to access file which is necessary for the method getRandomPrime
     *          in class RSA
     */
    public static void breakRSA() {
        // generate the keys in the format "d_n:e_n"
        String keys = RSA.generateKeys();
        // get the individual parts "d_n" and "e_n"
        String privateKey = RSA.getPrivateKey(keys);
        String publicKey = RSA.getPublicKey(keys);
        // get the individual elements of these parts
        String[] parts = publicKey.split("_");
        String[] parts1 = privateKey.split("_");
        BigInteger dCorrect = new BigInteger(parts1[0]);
        BigInteger e = new BigInteger(parts[0]);
        BigInteger n = new BigInteger(parts[1]);
        List<BigInteger[]> relevantPrimes = new ArrayList<>();
        // note start time
        long start = System.currentTimeMillis();
        // go through all values between 2 and n and test all combinations
        for (BigInteger i = new BigInteger("2"); i.compareTo(n) <= 0; i = i.add(BigInteger.ONE)) {
            for (BigInteger j = new BigInteger("2"); j.compareTo(n) <= 0; j = j.add(BigInteger.ONE)) {
                // if i*j is bigger than n, than don't look at the other j's
                // because i*j will be always bigger than n
                if ((i.multiply(j)).compareTo(n) == 1) {
                    break;
                }
                // could find i*j = n
                if ((i.multiply(j)).compareTo(n) == 0) {
                    // check whether i and j are prime
                    if (!isPrime(i)) {
                        break;
                    }
                    if (!isPrime(j)) {
                        continue;
                    }
                    // save them in the list to manage the possibility,
                    // that multiple prime factor combinations can result in n
                    BigInteger[] array = new BigInteger[2];
                    array[0] = i;
                    array[1] = j;
                    relevantPrimes.add(array);
                }
            }
        }
        // if list is empty, than no prime factorization was found
        if (relevantPrimes.isEmpty()) {
            System.out.println("No factorization found");
            return;
        }
        // go through all combinations
        for (int i = 0; i < relevantPrimes.size(); i++) {
            BigInteger[] array = relevantPrimes.get(i);
            BigInteger p = array[0];
            BigInteger q = array[1];
            BigInteger phi = (p.subtract(BigInteger.ONE)).multiply(q.subtract(BigInteger.ONE));
            // test whether this condition between e and phi is correct
            // if not, leave it
            if ((RSA.ggT(e, phi)).compareTo(BigInteger.ONE) != 0) {
                continue;
            }
            // calculate d
            BigInteger d = RSA.multiplicativeInverse(e, phi);
            // we could find d
            if (d.compareTo(dCorrect) == 0) {
                //stop time and print it out
                long stop = System.currentTimeMillis();
                System.out.println("Could break RSA");
                long time = (stop - start);
                System.out.println("Time: " + time);
                break;
            }
        }
    }

    /**
     * This is a very naive method which tests for a given BigInteger
     * whether it is a prime or not
     *
     * @param a BigInteger value which should be tested
     * @return boolean whether a is a prime or not
     */
    private static boolean isPrime(BigInteger a) {
        for (BigInteger i = new BigInteger("2"); i.compareTo(a) < 0; i = i.add(BigInteger.ONE)) {
            try {
                // check whether i is a divisor of a
                if (a.mod(i) == BigInteger.ZERO) {
                    return false;
                }
            } catch (ArithmeticException e) {
            }
        }
        return true;
    }
}
