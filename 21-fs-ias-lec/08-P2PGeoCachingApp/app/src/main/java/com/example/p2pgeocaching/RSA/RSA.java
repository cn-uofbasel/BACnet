package com.example.p2pgeocaching.RSA;


import java.math.BigInteger;
import java.util.Random;
import android.util.Log;

public class RSA {

    public static String generateKeys() {
        Log.d("RSA", "generate keys");
        BigInteger p;
        BigInteger q;
        BigInteger n;
        BigInteger phi;
        p = BigInteger.ZERO;
        q = BigInteger.ZERO;
        n = BigInteger.ZERO;
        Random random = new Random();
        int randomNum1 = 0, randomNum2 = 0;
        Log.d("RSA", "after init");
        while (p.compareTo(q) == 0 || n.bitLength() < 12 || n.bitLength() > 48) {
            while (randomNum1 < 2 || randomNum2 < 2) {
                randomNum1 = random.nextInt(24);
                randomNum2 = random.nextInt(24);
            }
            p = BigInteger.probablePrime(randomNum1, new Random());
            q = BigInteger.probablePrime(randomNum1, new Random());
            n = p.multiply(q);
            Log.d("RSA", "n = " +n);
        }
        Log.d("RSA", "after double while loop");
        phi = (p.subtract(BigInteger.ONE)).multiply(q.subtract(BigInteger.ONE));
        BigInteger e = BigInteger.ZERO;
        BigInteger ggt = BigInteger.ZERO;
        Log.d("RSA", "after double while loop");
        while (e.compareTo(BigInteger.ONE) <= 0 || e.compareTo(phi) >= 0 || ggt.compareTo(BigInteger.ONE) != 0) {
            e = RSA.getRandomBigInteger(phi);
            ggt = RSA.ggT(e, phi);
        }
        BigInteger d = RSA.multiplicativeInverse(e, phi);
        return d.toString() + "_" + n.toString() + ":" + e.toString() + "_" + n.toString();
    }

    public static String generateKeysCRT() {
        BigInteger p;
        BigInteger q;
        BigInteger n;
        BigInteger phi;
        p = BigInteger.ZERO;
        q = BigInteger.ZERO;
        n = BigInteger.ZERO;
        Random random = new Random();
        int randomNum1 = 0, randomNum2 = 0;
        while (p.compareTo(q) == 0 || n.bitLength() < 24 || n.bitLength() > 40) {
            while (randomNum1 == 0 || randomNum2 == 0) {
                randomNum1 = random.nextInt(24);
                randomNum2 = random.nextInt(24);
            }
            p = BigInteger.probablePrime(randomNum1, new Random());
            q = BigInteger.probablePrime(randomNum1, new Random());
            n = p.multiply(q);
        }
        phi = (p.subtract(BigInteger.ONE)).multiply(q.subtract(BigInteger.ONE));
        BigInteger e = BigInteger.ZERO;
        BigInteger ggt = BigInteger.ZERO;
        while (e.compareTo(BigInteger.ONE) <= 0 || e.compareTo(phi) >= 0 || ggt.compareTo(BigInteger.ONE) != 0) {
            e = RSA.getRandomBigInteger(phi);
            ggt = RSA.ggT(e, phi);
        }
        BigInteger d = RSA.multiplicativeInverse(e, phi);
        return d.toString() + "-" + p.toString() + "-" + q.toString() + "_" + n.toString() + ":" + e.toString() + "_" + n.toString();
    }

    public static String encode(String message, String privateKey) {
        String[] parts = privateKey.split("_");
        BigInteger d = new BigInteger(parts[0]);
        BigInteger n = new BigInteger(parts[1]);
        int k = RSA.getLengthOfBigIntegerAsBin(n) / 6;
        if (RSA.getLengthOfBigIntegerAsBin(n) % 6 == 0) {
            k--;
        }
        String[] letters = new String[message.length()];
        BigInteger[] block;
        if (message.length() % k == 0) {
            letters = new String[message.length()];
        } else {
            int t = message.length() / k;
            letters = new String[(t + 1) * k];
        }
        for (int i = 0; i < letters.length; i++) {
            letters[i] = "";
        }
        for (int i = 0; i < message.length(); i++) {
            letters[i] = Character.toString(message.charAt(i));
        }
        block = new BigInteger[letters.length / k];
        for (int i = 0; i < block.length; i++) {
            String string = "";
            for (int j = 0; j < k; j++) {
                String binaryBlock = BaseTable.getBinValue(letters[i * k + j]);
                if (binaryBlock == "") {
                    binaryBlock = "111111";
                }
                string = string + binaryBlock;
            }
            block[i] = new BigInteger(string, 2);
        }
        BigInteger[] encodedValues;
        encodedValues = new BigInteger[block.length + 1];
        BigInteger randomBigInt = new BigInteger(getRandomBinValue(k), 2);
        encodedValues[0] = randomBigInt;
        for (int i = 1; i < encodedValues.length; i++) {
            encodedValues[i] = (encodedValues[i - 1].xor(block[i - 1])).modPow(d, n);
        }
        String encodedMessage = encodedValues[0].toString();
        for (int i = 1; i < encodedValues.length; i++) {
            encodedMessage = encodedMessage + " " + encodedValues[i].toString();
        }
        return encodedMessage;
    }

    public static String encodeCRT(String message, String privateKey) {
        String[] parts = privateKey.split("_");
        BigInteger n = new BigInteger(parts[1]);
        String[] primeParts = parts[0].split("-");
        BigInteger d = new BigInteger(primeParts[0]);
        BigInteger p = new BigInteger(primeParts[1]);
        BigInteger q = new BigInteger(primeParts[2]);
        int k = RSA.getLengthOfBigIntegerAsBin(n) / 6;
        if (RSA.getLengthOfBigIntegerAsBin(n) % 6 == 0) {
            k--;
        }
        String[] letters = new String[message.length()];
        BigInteger[] block;
        if (message.length() % k == 0) {
            letters = new String[message.length()];
        } else {
            int t = message.length() / k;
            letters = new String[(t + 1) * k];
        }
        for (int i = 0; i < letters.length; i++) {
            letters[i] = "";
        }
        for (int i = 0; i < message.length(); i++) {
            letters[i] = Character.toString(message.charAt(i));
        }
        block = new BigInteger[letters.length / k];
        for (int i = 0; i < block.length; i++) {
            String string = "";
            for (int j = 0; j < k; j++) {
                String binaryBlock = BaseTable.getBinValue(letters[i * k + j]);
                if (binaryBlock == "") {
                    binaryBlock = "111111";
                }
                string = string + binaryBlock;
            }
            block[i] = new BigInteger(string, 2);
        }
        BigInteger[] encodedValues;
        encodedValues = new BigInteger[block.length + 1];
        BigInteger randomBigInt = new BigInteger(getRandomBinValue(k), 2);
        encodedValues[0] = randomBigInt;
        for (int i = 1; i < encodedValues.length; i++) {
            encodedValues[i] = RSA.crt(encodedValues[i - 1].xor(block[i - 1]), d, p, q);
        }
        String encodedMessage = encodedValues[0].toString();
        for (int i = 1; i < encodedValues.length; i++) {
            encodedMessage = encodedMessage + " " + encodedValues[i].toString();
        }
        return encodedMessage;
    }

    public static String decode(String encodedMessageAsText, String publicKey) {
        String[] parts = publicKey.split("_");
        BigInteger e = new BigInteger(parts[0]);
        BigInteger n = new BigInteger(parts[1]);
        int k = RSA.getLengthOfBigIntegerAsBin(n) / 6;
        if (RSA.getLengthOfBigIntegerAsBin(n) % 6 == 0) {
            k--;
        }
        String[] partsOfText = encodedMessageAsText.split(" ");
        BigInteger[] encodedMessage = new BigInteger[partsOfText.length];
        for (int i = 0; i < encodedMessage.length; i++) {
            encodedMessage[i] = new BigInteger(partsOfText[i]);
        }
        String message = "";
        BigInteger support;
        String binaryValue;
        String m, t, s;
        BigInteger[] decodedInt = new BigInteger[encodedMessage.length - 1];
        for (int i = encodedMessage.length - 1; i >= 1; i--) {
            //support = pow(encodedMessage[i], e).mod(n);
            support = encodedMessage[i].modPow(e, n);
            //System.out.println("out"+i);
            decodedInt[i - 1] = encodedMessage[i - 1].xor(support);
        }

        for (int i = 0; i < decodedInt.length; i++) {
            binaryValue = String.format("%" + (k * 6) + "s", decodedInt[i].toString(2)).replace(' ', '0');
            for (int j = 0; j < k; j++) {
                m = binaryValue.substring(j * 6, j * 6 + 6);
                m = BaseTable.getLetter(m);
                message = message + m;
            }
        }
        return message;
    }

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

    public static BigInteger getRandomBigInteger(BigInteger phi) {
        Random random = new Random();
        BigInteger e;
        // e must be strictly lower than phi
        do {
            e = new BigInteger(phi.bitLength(), random);
        } while (e.compareTo(phi) >= 0);
        return e;
    }

    public static BigInteger ggT(BigInteger a, BigInteger b) {
        if (b.equals(BigInteger.ZERO)) {
            return a;
        }
        return ggT(b, a.mod(b));
    }

    public static BigInteger multiplicativeInverse(BigInteger a, BigInteger N) {
        BigInteger[] result = extendedEuclid(a, N);
        if (result[1].compareTo(BigInteger.ZERO) == 1) {
            return result[1];
        } else {
            return result[1].add(N);
        }
    }

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

    public static int getLengthOfBigIntegerAsBin(BigInteger keyValue) {
        int count = 0;
        BigInteger two = new BigInteger("2");
        while (keyValue.compareTo(BigInteger.ZERO) >= 1) {
            keyValue = keyValue.divide(two);
            count++;
        }
        return count;
    }

    public static String getRandomBinValue(int k) {
        String randomBin = "";
        Random random = new Random();
        for (int i = 0; i < k * 6; i++) {
            randomBin = randomBin + random.nextInt(2);
        }
        return randomBin;
    }

    public static String getPublicKey(String key) {
        // split key at the position ":"
        String[] keys = key.split(":");
        // return second part "e_n"
        return keys[1];
    }

    public static String getPrivateKey(String key) {
        // split key at the position ":"
        String[] keys = key.split(":");
        // return first part "d_n"
        return keys[0];
    }
}
