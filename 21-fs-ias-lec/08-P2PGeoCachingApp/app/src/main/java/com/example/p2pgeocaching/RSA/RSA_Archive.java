package com.example.p2pgeocaching.RSA;

import android.content.Context;
import android.content.res.AssetManager;
import android.util.Log;

import java.io.IOException;
import java.io.InputStream;
import java.math.BigInteger;
import java.util.Arrays;
import java.util.Random;
import java.util.Scanner;

/**
 * This class is used to access the adjusted RSA implementation.
 * There is a normal RSA implementation and a RSA-CRT implementation. Through this
 * class we can encode and decode messages, generate private and public keys,
 * split private key in n parts and recreate private key through the n parts (only supported
 * by normal RSA, not by RSA-CRT). In the normal RSA, we use only small n. As consequence
 * this implementation is not secure and can be broken in very few time. RSA-CRT is more
 * secure. Here we can work with keys with length of 128, 256, 512 or more bits.
 * The RSA implementation only serves for our project. It is absolutely not recommended, to use this
 * implementation in a surrounding, where security is essential!
 * Important is that we don't encode an entire message with RSA. Instead the message is
 * splitted in blocks of two letters. To avoid patterns, RSA is also combined with
 * cipher block chaining. To access the normal RSA, the methods generateKeys() and encode()
 * can be used. To access RSA-CRT, the methods generateKey128() and encode128() can be accessed.
 * For decoding, the method decode can be used. Here it doesn't matter whether RSA or RSA-CRT is used.
 */
public class RSA_Archive {
    /*
    public static void main (String [] args) {
        String key = generateKeys();
        System.out.println("Generated Keys.");
        String privateKey = getPrivateKey(key);
        System.out.println("Private Key (d_n): "+privateKey);
        String publicKey = getPublicKey(key);
        System.out.println("Public Key (e_n): "+publicKey);
        String encodedMessage = encode("M", privateKey);
        System.out.println("Encoded Message: "+encodedMessage);
        String decodedMessage = decode(encodedMessage, publicKey);
        System.out.println("Decoded Message: "+decodedMessage);
    }
    */
    private final static String TAG = "RSA_Archive";
    private final static String FILE_PATH = "raw/primeNumbers.txt";

    /**
     * This method is used to get a random prime value between 2 and 4093
     * Therefore, the method chooses randomly one line of the given file
     * "raw/primeNumbers.txt" which contains prime values.
     *
     * @param c Context with which we can access the file
     * @return random prime as int
     */
    private static int getRandomPrime(Context c) {
        Random random = new Random();
        AssetManager assetManager = c.getAssets();
        InputStream inputStream = null;
        while (inputStream == null) {
            try {
                inputStream = assetManager.open(FILE_PATH);
            } catch (IOException e) {
                Log.d(TAG, "IOException when generating primes, could not open primesFile.");
                try {
                    Log.d(TAG, "List of assets: " + Arrays.toString(assetManager.list("")));
                } catch (IOException i) {
                }
            }
        }
        Scanner scanner = new Scanner(inputStream);
        int randomRow = random.nextInt(numOfLines(scanner));
        String line = "";
        try {
            scanner = new Scanner(assetManager.open(FILE_PATH));
        } catch (IOException e) {
        }
        for (int i = 0; i < randomRow; i++) {
            scanner.nextLine();
        }
        line = scanner.nextLine();

        return Integer.parseInt(line);
    }

    /**
     * This method is used to get the total amount of lines of the file
     * "raw/primeNumbers.txt".
     *
     * @param sc Scanner which is used to scan over the lines of file "raw/primeNumbers.txt"
     * @return total amount of lines as int
     */
    private static int numOfLines(Scanner sc) {
        int lines = 0;
        // go through all lines of the file and count the amount of lines
        while (sc.hasNextLine()) {
            sc.nextLine();
            lines++;
        }
        sc.close();
        return lines;
    }

    /**
     * This method is used to calculate the greatest common divisor of two BigInteger values
     *
     * @param a first BigInteger value
     * @param b second BigInteger value
     * @return greatest common divisor of the two values a and b
     */
    public static BigInteger ggT(BigInteger a, BigInteger b) {
        BigInteger min = a;
        // get the smaller number to avoid longer for-loop
        if (a.compareTo(b) > 0) {
            min = b;
        }
        for (BigInteger i = min; i.compareTo(BigInteger.ONE) > 0; i = i.subtract(BigInteger.ONE)) {
            // try to get a common divisor
            if ((a.mod(i)).compareTo(BigInteger.ZERO) == 0 && (b.mod(i)).compareTo(BigInteger.ZERO) == 0) {
                // return greatest common divisor
                return i;
            }
        }
        // if no divisor was found, return 1
        return BigInteger.ONE;
    }

    /**
     * This method is called to get the multiplicative inverse of two values.
     * It calls the method extendedEuclid and checks what extendedEuclid returns
     * and makes dependent on the result a last calculation
     *
     * @param a first value
     * @param n second value
     * @return multiplicative inverse of a and n
     */
    public static BigInteger multiplicativeInverse(BigInteger a, BigInteger n) {
        BigInteger[] result = extendedEuclid(a, n);
        if (result[1].compareTo(BigInteger.ZERO) == 1) {
            return result[1];
        } else {
            return result[1].add(n);
        }
    }

    /**
     * This method implements the extended euclidian algorithm
     * which is used to calculate the multiplicative inverse of two
     * values efficiently
     *
     * @param a first value
     * @param b second value
     * @return euclidian of a and b as BigInteger array
     */
    private static BigInteger[] extendedEuclid(BigInteger a, BigInteger b) {
        BigInteger[] result = new BigInteger[3];
        BigInteger a1, b1;

        if (b.equals(BigInteger.ZERO)) {
            result[0] = a;
            result[1] = BigInteger.ONE;
            result[2] = BigInteger.ZERO;
            return result;
        }

        result = extendedEuclid(b, a.mod(b));
        a1 = result[1];
        b1 = result[2];
        result[1] = b1;
        BigInteger support = a.divide(b);
        support = b1.multiply(support);
        result[2] = a1.subtract(support);
        return result;
    }

    /**
     * This method is used to get a random BigInteger value with the condition
     * that it must be smaller than the given parameter phi
     *
     * @param phi represents the limit of the random value
     * @return random BigInteger value
     */
    static BigInteger getRandomBigInteger(BigInteger phi) {
        Random random = new Random();
        BigInteger e;
        // e must be strictly lower than phi
        do {
            e = new BigInteger(phi.bitLength(), random);
        } while (e.compareTo(phi) >= 0);
        return e;
    }

    /**
     * This method is used to generate private and public keys
     *
     * @param c Context which is used to reach file "raw/primeNumbers.txt"
     * @return String which contains private and public Key in the format:
     * d_n:e_n
     */
    public static String generateKeys(Context c) {
        int p = 0;
        int q = 0;
        BigInteger bigP = BigInteger.ZERO;
        BigInteger bigQ = BigInteger.ZERO;
        BigInteger n = BigInteger.ZERO;
        // search after two prime values p and q which are not equall to each other
        // and produce n with a bit length between 12 and 18 bits.
        // If the bit length exceeds this limit, the calculation would take much longer
        while (p == q || n.bitLength() < 12 || n.bitLength() > 18) {
            // get p and q through the method getRandomPrime
            p = getRandomPrime(c);
            q = getRandomPrime(c);
            // transform p and q to BigInteger values
            bigP = BigInteger.valueOf(p);
            bigQ = BigInteger.valueOf(q);
            // calculate n with n = p * q
            n = bigP.multiply(bigQ);
        }
        // calculate phi with phi = (p-1) * (q-1)
        BigInteger phi = (bigP.subtract(BigInteger.ONE)).multiply(bigQ.subtract(BigInteger.ONE));

        BigInteger e = BigInteger.ZERO;
        BigInteger ggt = BigInteger.ZERO;
        // Try to calculate a which is bigger than zero and smaller than phi with the condition, that e and phi
        // don't share any other greatest common divisor than 1
        while (e.compareTo(BigInteger.ONE) <= 0 || e.compareTo(phi) >= 0 || ggt.compareTo(BigInteger.ONE) != 0) {
            // get e with the method getRandomBigInteger
            e = getRandomBigInteger(phi);
            // calculate greates common divisor of e and phi with the method ggT
            ggt = ggT(e, phi);
        }
        // Calculate the multiplicative inverse d of e and phi so that e * d == 1 mod phi
        // d is calculated with the method multiplicativeInverse
        BigInteger d = multiplicativeInverse(e, phi);
        // check whether all conditions are correct: d, e and n must be bigger than 0 (safety check)
        if (d.compareTo(BigInteger.ZERO) <= 0 || e.compareTo(BigInteger.ZERO) <= 0 || n.compareTo(BigInteger.ZERO) <= 0) {
            return generateKeys(c);
        }
        // return keys in the format "d_n:e_n"
        return d.toString() + "_" + n.toString() + ":" + e.toString() + "_" + n.toString();
    }

    /**
     * This method is used to generate public and private keys with
     * large lengths. It is called if RSA-CRT is used. The difference between
     * RSA and RSA-CRT is, that e is fix and that the private key contains also
     * p and q (prime factorization of n).
     */
    public static String generateKey128() {
        // e is fix
        BigInteger e = new BigInteger("3");
        BigInteger ggt = BigInteger.ZERO;
        BigInteger p = BigInteger.ZERO;
        BigInteger q = BigInteger.ZERO;
        BigInteger n = BigInteger.ZERO;
        BigInteger phi = BigInteger.ZERO;
        // calculate p, q, n and phi so that the greatest common divisor between
        // e and phi is 1
        while (ggt.compareTo(BigInteger.ONE) != 0) {
            p = BigInteger.probablePrime(128, new Random());
            q = BigInteger.probablePrime(128, new Random());
            n = p.multiply(q);
            phi = (p.subtract(BigInteger.ONE)).multiply(q.subtract(BigInteger.ONE));
            ggt = ggT(e, phi);
        }
        // Calculate the multiplicative inverse d of e and phi so that e * d == 1 mod phi
        // d is calculated with the method multiplicativeInverse
        BigInteger d = multiplicativeInverse(e, phi);
        // check whether all conditions are correct: d, e and n must be bigger than 0 (safety check)
        if (d.compareTo(BigInteger.ZERO) <= 0 || e.compareTo(BigInteger.ZERO) <= 0 || n.compareTo(BigInteger.ZERO) <= 0) {
            return generateKey128();
        }
        // return key in the string format "d-p-q_n:e_n"
        String keyAsString = d.toString() + "-" + p.toString() + "-" + q.toString() + "_" + n.toString() + ":" + e.toString() + "_" + n.toString();
        return keyAsString;
    }

    /**
     * This method implements the chinese remainder theory. It is used for encode128, to
     * make the encoding calculation faster by splitting the original calculation
     * m^d mod n into two calculations.
     *
     * @param m message as BigInteger which should be encoded
     * @param d private Key d
     * @param p first value of prime factorization of n
     * @param q second value of prime factorization of n
     * @return encoded value as BigInteger
     */
    public static BigInteger crt(BigInteger m, BigInteger d, BigInteger p, BigInteger q) {
        BigInteger dP, dQ, qInv, m1, m2, support, s;
        dP = d.mod(p.subtract(BigInteger.ONE));
        dQ = d.mod(q.subtract(BigInteger.ONE));
        qInv = multiplicativeInverse(q, p);
        m1 = m.modPow(dP, p);
        m2 = m.modPow(dQ, q);
        support = qInv.multiply(m1.subtract(m2)).mod(p);
        s = m2.add(support.multiply(q));
        return s;
    }

    /**
     * This method is used to calculate the pow between base and exponent
     * which are both BigInteger values
     *
     * @param base     base value as BigInteger
     * @param exponent exponent values as BigInteger
     * @return BigInteger value base^exponent
     */
    private static BigInteger pow(BigInteger base, BigInteger exponent) {
        BigInteger result = BigInteger.ONE;
        while (exponent.signum() > 0) {
            if (exponent.testBit(0)) {
                result = result.multiply(base);
            }
            base = base.multiply(base);
            exponent = exponent.shiftRight(1);
        }
        return result;
    }

    /**
     * This method is used to generate a random binary value with length of 12 bits
     *
     * @return String containing a binary value with length 12 bits
     */
    private static String getRandomBinValue() {
        StringBuilder randomBin = new StringBuilder();
        Random random = new Random();
        for (int i = 0; i < 12; i++) {
            // append either 0 or 1 to the string
            randomBin.append(random.nextInt(2));
        }
        return randomBin.toString();
    }

    /**
     * This method is used to encode a message with the given privateKey
     *
     * @param message    message which should be encoded with private Key in RSA
     * @param privateKey String which contains d an n in the format d_n
     * @return String containing the given message encoded in rsa
     */
    public static String encode(String message, String privateKey) {
        // split private key at "_". This is due to the fact that the privateKey
        // is in the format "d_n".
        String[] parts = privateKey.split("_");
        // transform the parts into BigInteger values
        BigInteger d = new BigInteger(parts[0]);
        BigInteger n = new BigInteger(parts[1]);
        String[] letters;
        BigInteger[] block;
        // if message length even then we don't have to pad
        if (message.length() % 2 == 0) {
            letters = new String[message.length()];
        } else {
            // padding necessary. Last array element is reserved for the binary
            // value 111111 (later). This serves as indicator for the decoding method,
            // that this element only served for padding
            letters = new String[message.length() + 1];
        }
        // get all characters in the message and save them in array letters
        for (int i = 0; i < message.length(); i++) {
            letters[i] = Character.toString(message.charAt(i));
            //System.out.println(letters[i]);
        }
        // If last array element is null then message is not even. This element
        // was reserved for the padding indicator
        if (letters[letters.length - 1] == null) {
            letters[letters.length - 1] = "";
        }
        // We transform all letters into base64 encoding and save them as 2-letter-blocks
        // That is the reasen, why block has only half of the length of array letters
        block = new BigInteger[letters.length / 2];
        for (int i = 0; i < block.length; i++) {
            // get base64 encoding of letter through class BaseTable
            String binaryBlock1 = BaseTable.getBinValue(letters[i * 2]);
            String binaryBlock2 = BaseTable.getBinValue(letters[i * 2 + 1]);
            // if second block is a empty string this means that this block is only
            // used for padding. Save there the binary value 111111
            if (binaryBlock2.equals("")) {
                binaryBlock2 = "111111";
            }
            // save 2-block-binary values in array
            block[i] = new BigInteger(binaryBlock1 + binaryBlock2, 2);
        }
        BigInteger[] encodedValues;
        // If we only have one block: use RSA directly
        if (block.length == 1) {
            encodedValues = new BigInteger[1];
            encodedValues[0] = block[0].modPow(d, n);
        } else {
            // If we have multiple block, than apply CBC. Generate an initalizing
            // vector with the length of 12 bits. Save the RSA encoding of it in the
            // first position of the array. Take this value and calculate XOR between it and
            // the first block. Apply RSA and save the value in array. Take that value and
            // calculate XOR with the second block etc.
            encodedValues = new BigInteger[block.length + 1];
            // calculate a random binary value of length of 12 bits and get the BigInteger value
            // of it. This servers as initializing vector
            BigInteger randomBigInt = new BigInteger(getRandomBinValue(), 2);
            // save RSA encoding of the initializing vector
            encodedValues[0] = randomBigInt.modPow(d, n);
            for (int i = 1; i < encodedValues.length; i++) {
                // get encoded block and calculate XOR with next block, get the RSA
                // encoding of XOR and save it in the array
                encodedValues[i] = (encodedValues[i - 1].xor(block[i - 1])).modPow(d, n);
                ;
            }
        }
        StringBuilder encodedMessage = new StringBuilder(encodedValues[0].toString());
        // append all RSA encodings in a string
        for (int i = 1; i < encodedValues.length; i++) {
            encodedMessage.append(" ").append(encodedValues[i].toString());
        }
        return encodedMessage.toString();
    }

    /**
     * This method is used to encode a message with the given privateKey of
     * the length of large amount of bits. In this encoding scheme, we use
     * RSA-CRT. This is a method where RSA is combined with the chinese remainder
     * theory. As consequence, the prime factorization p and q are also considered
     * in the encoding scheme
     *
     * @param message    message which should be encoded with private Key in RSA -CRT
     * @param privateKey String which contains d, p, w and n in the format
     *                   "d-p-q_n"
     * @return String containing the given message encoded in RSA-CRT
     */
    public static String encode128(String message, String privateKey) {
        // split private key at "_" to get d-p-q and n separated
        String[] parts = privateKey.split("_");
        // save n as BigInteger
        BigInteger n = new BigInteger(parts[1]);
        // split at "-" to get d, p and q
        String[] primeParts = parts[0].split("-");
        // save d, p and q
        BigInteger d = new BigInteger(primeParts[0]);
        BigInteger p = new BigInteger(primeParts[1]);
        BigInteger q = new BigInteger(primeParts[2]);
        String[] letters;
        BigInteger[] block;
        // if message length even then we don't have to pad
        if (message.length() % 2 == 0) {
            letters = new String[message.length()];
        } else {
            // padding necessary. Last array element is reserved for the binary
            // value 111111 (later). This serves as indicator for the decoding method,
            // that this element only served for padding
            letters = new String[message.length() + 1];
        }
        // get all characters in the message and save them in array letters
        for (int i = 0; i < message.length(); i++) {
            letters[i] = Character.toString(message.charAt(i));
        }
        // If last array element is null then message is not even. This element
        // was reserved for the padding indicator
        if (letters[letters.length - 1] == null) {
            letters[letters.length - 1] = "";
        }
        // We transform all letters into base64 encoding and save them as 2-letter-blocks
        // That is the reasen, why block has only half of the length of array letters
        block = new BigInteger[letters.length / 2];
        for (int i = 0; i < block.length; i++) {
            // get base64 encoding of letter through class BaseTable
            String binaryBlock1 = BaseTable.getBinValue(letters[i * 2]);
            String binaryBlock2 = BaseTable.getBinValue(letters[i * 2 + 1]);
            // if second block is a empty string this means that this block is only
            // used for padding. Save there the binary value 111111
            if (binaryBlock2 == "") {
                binaryBlock2 = "111111";
            }
            // save 2-block-binary values in array
            block[i] = new BigInteger(binaryBlock1 + binaryBlock2, 2);
        }
        BigInteger[] encodedValues;
        // If we only have one block: use RSA-CRT directly
        if (block.length == 1) {
            encodedValues = new BigInteger[1];
            encodedValues[0] = crt(block[0], d, p, q);
        } else {
            // If we have multiple block, than apply CBC. Generate an initalizing
            // vector with the length of 12 bits. Save the RSA-CRT encoding of it in the
            // first position of the array. Take this value and calculate XOR between it and
            // the first block. Apply RSA-CRT and save the value in array. Take that value and
            // calculate XOR with the second block etc.
            encodedValues = new BigInteger[block.length + 1];
            // calculate a random binary value of length of 12 bits and get the BigInteger value
            // of it. This servers as initializing vector
            BigInteger randomBigInt = new BigInteger(getRandomBinValue(), 2);
            // save RSA-CRT encoding of the initializing vector
            encodedValues[0] = crt(randomBigInt, d, p, q);
            for (int i = 1; i < encodedValues.length; i++) {
                // get encoded block and calculate XOR with next block, get the RSA
                // encoding of XOR and save it in the array
                encodedValues[i] = crt(encodedValues[i - 1].xor(block[i - 1]), d, p, q);
            }
        }
        String encodedMessage = encodedValues[0].toString();
        // append all RSA encodings in a string
        for (int i = 1; i < encodedValues.length; i++) {
            encodedMessage = encodedMessage + " " + encodedValues[i].toString();
        }
        return encodedMessage;
    }

    /**
     * This method is used to decode an encoded message with the given public key
     *
     * @param encodedMessageAsText encoded message that needs to be decoded
     * @param publicKey            public key in the format "e_n"
     * @return decoded message as String
     */
    public static String decode(String encodedMessageAsText, String publicKey) {
        // split public key at "_" to get e and n
        String[] parts = publicKey.split("_");
        // save e and n separately
        BigInteger e = new BigInteger(parts[0]);
        BigInteger n = new BigInteger(parts[1]);
        // split the encoded text at " " to get the individual parts. Remember, each block
        // represents the encoding of two letters in base64 format
        String[] partsOfText = encodedMessageAsText.split(" ");
        BigInteger[] encodedMessage = new BigInteger[partsOfText.length];
        for (int i = 0; i < encodedMessage.length; i++) {
            // transform string into BigInteger
            encodedMessage[i] = new BigInteger(partsOfText[i]);
        }
        StringBuilder message = new StringBuilder();
        BigInteger support;
        String binaryValue;
        String m, t, s;
        // If the message only contains one block
        if (encodedMessage.length == 1) {
            // Decode that block with RSA
            support = encodedMessage[0].modPow(e, n);
            // add zeroes to get 12 bit representation
            binaryValue = String.format("%12s", support.toString(2)).replace(' ', '0');
            // first 6 bits belongs to first letter in base64 format
            m = binaryValue.substring(0, 6);
            // last 6 bits belongs to second letter in base64 format
            t = binaryValue.substring(6, 12);
            // get the correct char letter from the class BaseTable
            m = BaseTable.getLetter(m);
            t = BaseTable.getLetter(t);
            message.append(m);
            // In the encoding scheme, we use padding. So check whether the last letter only
            // served for padding services or not. If yout get "", this means that the letter only
            // served as padding. If not, than append that letter to the message.
            if (t.compareTo("") != 0) {
                message.append(t);
            }
        } else {
            // we have multiple blocks
            BigInteger[] decodedInt = new BigInteger[encodedMessage.length - 1];
            // In the encoding scheme, we used CBC to avoid patterns. As consequence,
            // we decode last element and calculate the xor with the second last element.
            // Then we decode second last element and calculate the xor with the
            // third last element and so on. Through this way, we can get the original
            // message in base64 encoding.
            for (int i = encodedMessage.length - 1; i >= 1; i--) {
                support = encodedMessage[i].modPow(e, n);
                decodedInt[i - 1] = encodedMessage[i - 1].xor(support);
            }

            // go through array decodedInt
            for (BigInteger bigInteger : decodedInt) {
                // fill value with zeroes to get 12 bit format
                binaryValue = String.format("%12s", bigInteger.toString(2)).replace(' ', '0');
                // first base64 encoding
                m = binaryValue.substring(0, 6);
                // second base64 encoding
                t = binaryValue.substring(6, 12);
                // get the two letters
                m = BaseTable.getLetter(m);
                t = BaseTable.getLetter(t);
                message.append(m);
                // In the encoding scheme, we use padding. So check whether the last letter only
                // served for padding services or not. If yout get "", this means that the letter only
                // served as padding. If not, than append that letter to the message.
                if (t.compareTo("") != 0) {
                    message.append(t);
                }
            }
        }
        return message.toString();
    }

    /**
     * This method takes the keys and returns the private key
     *
     * @param key key in the format "d_n:e_n"
     * @return private key in the format "d_n"
     */
    public static String getPrivateKey(String key) {
        // split key at the position ":"
        String[] keys = key.split(":");
        // return first part "d_n"
        return keys[0];
    }

    /**
     * This method takes the keys and returns the public key
     *
     * @param key key in the format "d_n:e_n"
     * @return private key in the format "e_n"
     */
    public static String getPublicKey(String key) {
        // split key at the position ":"
        String[] keys = key.split(":");
        // return second part "e_n"
        return keys[1];
    }

    /**
     * This method is used to create private key String
     *
     * @param privateKey d value of private key
     * @param publicKey  format: "e_n"
     * @return privateKey as String in the format "d_n"
     */
    public static String createPrivateKey(String privateKey, String publicKey) {
        // split publicKey at the position "_" to get n
        String[] parts = publicKey.split("_");
        // return "d_n"
        return privateKey + "_" + parts[1];
    }

    /**
     * This method returns a random binary String with length n
     *
     * @param n length of string
     * @return the binary value as String
     */
    private static String getRandomBinWithLengthN(int n) {
        String binaryString = "";
        int j;
        Random random = new Random();
        for (int i = 0; i < n; i++) {
            // append n-times 0 or 1 to the string
            binaryString = binaryString + random.nextInt(2);
        }
        return binaryString;
    }

    /**
     * This method is used to transform a binary String into BigInteger
     *
     * @param binaryString binary value as String which should be transformed into BigInteger
     * @return BigInteger value of binaryString
     */
    private static BigInteger binToBigInteger(String binaryString) {
        return new BigInteger(binaryString, 2);
    }

    /**
     * This method is used to get the length of the BigInteger value
     * in binary format
     *
     * @param keyValue BigInteger value
     * @return length of BigInteger value in binary format as int
     */
    static int getLengthOfBigIntegerAsBin(BigInteger keyValue) {
        int count = 0;
        BigInteger two = new BigInteger("2");
        while (keyValue.compareTo(BigInteger.ZERO) >= 1) {
            keyValue = keyValue.divide(two);
            count++;
        }
        return count;
    }

    /**
     * This method is used to split a private Key (d) into n parts
     * with XOR.
     *
     * @param n          amount of parts
     * @param privateKey private Key in format "d_n"
     * @return String containing the splitted keys
     */
    public static String keySplitting(int n, String privateKey) {
        BigInteger[] keyList = new BigInteger[n];
        String binaryString = "";
        BigInteger intValue, xorValue;
        // split private key at "_" to get d and n
        String[] parts = privateKey.split("_");
        BigInteger d = new BigInteger(parts[0]);
        // get length of d in binary format. This is done with the method
        // getLengthOfBigIntegerAsBin
        int binLength = getLengthOfBigIntegerAsBin(d);
        // if n is equal to 1, than a splitting is not performed
        // As consequence, d will be returned
        if (n == 1) {
            keyList[0] = d;
        } else {
            // n is not equal to 1
            // In this implementation, we calculate first a random BigInteger
            // value Q which has the same length like d in binary format.
            // Then we calculate the xor between Q and d. After that
            // we calculate again a new random BigInteger value T. We also
            // take the XOR between T and Q and so on. The value which was on the
            // left in one XOR calculation will be on the rigth in the next XOR
            // calculation
            for (int i = 0; i < n - 1; i++) {
                // calculate a random binary value with the length of
                // d in binary format
                binaryString = getRandomBinWithLengthN(binLength);
                // transform binary value to BigInteger.
                intValue = binToBigInteger(binaryString);
                // calculate XOR between random value and previously
                // calculated random value
                xorValue = intValue.xor(d);
                // save xor value
                keyList[i] = xorValue;
                // update d
                d = intValue;
            }
            // Add last element into array
            keyList[n - 1] = d;
            // check whether two splitted keys are equal to each other
            // If yes, start the method again
            for (int i = 0; i < keyList.length; i++) {
                for (int j = i; j < keyList.length; j++) {
                    if (keyList[j].compareTo(keyList[i]) == 0 && i != j) {
                        return keySplitting(n, privateKey);
                    }
                }
            }
        }
        // Append all splitted keys in an string of the formar:
        // "key1_key2_...._keyn"
        String splittedKeys = "";
        for (int i = 0; i < keyList.length; i++) {
            if (i != keyList.length - 1) {
                splittedKeys = splittedKeys + keyList[i].toString() + "_";
            } else {
                splittedKeys = splittedKeys + keyList[i].toString();
            }
        }
        return splittedKeys;
    }

    /**
     * This method recreates the private key
     *
     * @param keyList String which contains all splitted keys in
     *                the format "key1_key2_..._keyN"
     * @return String containing d
     */
    public static String keyRecreating(String keyList) {
        // get the individual keys
        String[] keyParts = keyList.split("_");
        // get the total amount of splitted keys
        int len = keyParts.length;
        // save last element in d
        BigInteger d = new BigInteger(keyParts[len - 1]);
        // If we only have one key in the array, this means
        // that it is directly d. If we look at the method
        // keySplitting, we see that a private key will not be
        // splitted if n is equal to one!
        if (keyParts.length == 1) {
            return d.toString();
        }
        // from the right side to the left, calculate the xors
        // in the beginning, d is equal to the last element.
        // calculate d XOR with second last element and save it
        // in d. Then calculate d XOR with third last element and
        // save it in d and so on. At the end we will get the original
        // private key d
        for (int i = len - 2; i >= 0; i--) {
            d = d.xor(new BigInteger(keyParts[i]));
        }
        // return d as string
        return d.toString();
    }
}