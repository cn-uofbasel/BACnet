package com.example.p2pgeocaching.RSA;

import java.math.BigInteger;
import java.util.*;
import java.util.Base64.*;
import java.io.*;

public class RuntimeTester
{
    public static void main (String[] args) {
        BigInteger p;
        BigInteger q;
        BigInteger n;
        BigInteger phi;
        boolean bool = false;
        for (int i = 128; i <= 1024; i = i * 2) {
            p = BigInteger.ZERO;
            q = BigInteger.ZERO;
            n = BigInteger.ZERO;
            if (bool) {
                break;
            }
            while (p.compareTo(q) == 0) {
                p = BigInteger.probablePrime(i, new Random());
                q = BigInteger.probablePrime(i, new Random());
                n = p.multiply(q);
            }
            phi = (p.subtract(BigInteger.ONE)).multiply(q.subtract(BigInteger.ONE));
            BigInteger e = BigInteger.ZERO;
            BigInteger ggt = BigInteger.ZERO;
            while (e.compareTo(BigInteger.ONE) <= 0 || e.compareTo(phi) >= 0 || ggt.compareTo(BigInteger.ONE) != 0){
                e = RSA.getRandomBigInteger(phi);
                ggt = RSA.ggT(e, phi);
            }
            BigInteger d = RSA.multiplicativeInverse(e, phi);
            String privateKey = d+"_"+n;
            String privateKeyCRT = d+"-"+p+"-"+q+"_"+n;
            String publicKey = e+"_"+n;
            for (int u = 2; u < (int) 2*i/6; u++) {
                System.out.println("Grösse von Prim: "+i+", Blockgrösse = "+u);
                System.out.println("Privat = "+privateKey+", Public = "+publicKey);
                long start = System.currentTimeMillis();
                String encodedMessage = encode("Lars Waldvogel", privateKey,u);
                String decodedMessage = decode(encodedMessage, publicKey, u);
                long stop = System.currentTimeMillis();
                long time = stop-start;
                System.out.println("Normal RSA: time = "+time+" ms, Name = "+decodedMessage);
                start = System.currentTimeMillis();
                encodedMessage = encodeCRT("Lars Waldvogel", privateKeyCRT,u);
                decodedMessage = decode(encodedMessage, publicKey, u);
                stop = System.currentTimeMillis();
                time = stop-start;
                System.out.println("RSA-CRT   : time = "+time+" ms, Name = "+decodedMessage);
                System.out.println("");
                if (decodedMessage.compareTo("Lars Waldvogel") != 0) {
                    System.out.println("Problem "+", i: "+i+", u = "+u+", decoded = "+decodedMessage);
                    bool = true;
                    break;
                }
            }
        }
    }

    public static String encode(String message, String privateKey, int k) {
        String[] parts = privateKey.split("_");
        BigInteger d = new BigInteger(parts[0]);
        BigInteger n = new BigInteger(parts[1]);
        String[] letters = new String[message.length()];
        BigInteger[] block;
        if (message.length() % k == 0) {
            letters = new String[message.length()];
        } else {
            int t = message.length() / k;
            letters = new String[(t+1) * k];
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
                String binaryBlock = BaseTable.getBinValue(letters[i*k + j]);
                if (binaryBlock == "") {
                    binaryBlock = "111111";
                }
                string = string + binaryBlock;
            }
            block[i] = new BigInteger(string, 2);
        }
        BigInteger[] encodedValues;
        encodedValues = new BigInteger[block.length + 1];
        BigInteger randomBigInt = new BigInteger(getRandomBinValue(k),2);
        encodedValues[0] = randomBigInt;
        for (int i = 1; i < encodedValues.length; i++) {
            encodedValues[i] = (encodedValues[i-1].xor(block[i-1])).modPow(d, n);
        }
        String encodedMessage = encodedValues[0].toString();
        for (int i = 1; i < encodedValues.length; i++) {
            encodedMessage = encodedMessage + " " + encodedValues[i].toString();
        }
        return encodedMessage;
    }

    public static String encodeCRT(String message, String privateKey, int k) {
        String[] parts = privateKey.split("_");
        BigInteger n = new BigInteger(parts[1]);
        String[] primeParts = parts[0].split("-");
        BigInteger d = new BigInteger(primeParts[0]);
        BigInteger p = new BigInteger(primeParts[1]);
        BigInteger q = new BigInteger(primeParts[2]);
        String[] letters = new String[message.length()];
        BigInteger[] block;
        if (message.length() % k == 0) {
            letters = new String[message.length()];
        } else {
            int t = message.length() / k;
            letters = new String[(t+1) * k];
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
                String binaryBlock = BaseTable.getBinValue(letters[i*k + j]);
                if (binaryBlock == "") {
                    binaryBlock = "111111";
                }
                string = string + binaryBlock;
            }
            block[i] = new BigInteger(string, 2);
        }
        BigInteger[] encodedValues;
        encodedValues = new BigInteger[block.length + 1];
        BigInteger randomBigInt = new BigInteger(getRandomBinValue(k),2);
        encodedValues[0] = randomBigInt;
        for (int i = 1; i < encodedValues.length; i++) {
            encodedValues[i] = RSA.crt(encodedValues[i-1].xor(block[i-1]), d, p, q);
        }
        String encodedMessage = encodedValues[0].toString();
        for (int i = 1; i < encodedValues.length; i++) {
            encodedMessage = encodedMessage + " " + encodedValues[i].toString();
        }
        return encodedMessage;
    }

    public static String decode(String encodedMessageAsText, String publicKey, int k){
        String[] parts = publicKey.split("_");
        BigInteger e = new BigInteger(parts[0]);
        BigInteger n = new BigInteger(parts[1]);
        String[] partsOfText = encodedMessageAsText.split(" ");
        BigInteger[] encodedMessage = new BigInteger[partsOfText.length];
        for (int i = 0; i < encodedMessage.length; i++) {
            encodedMessage[i] = new BigInteger(partsOfText[i]);
        }
        String message = "";
        BigInteger support;
        String binaryValue;
        String m, t, s;
        BigInteger[] decodedInt = new BigInteger[encodedMessage.length-1];
        for (int i = encodedMessage.length-1; i >= 1; i--) {
            //support = pow(encodedMessage[i], e).mod(n);
            support = encodedMessage[i].modPow(e, n);
            //System.out.println("out"+i);
            decodedInt[i-1] = encodedMessage[i-1].xor(support);
        }

        for (int i = 0; i < decodedInt.length; i++) {
            binaryValue = String.format("%"+(k*6)+"s", decodedInt[i].toString(2)).replace(' ', '0');
            for (int j = 0; j < k; j++) {
                m = binaryValue.substring(j*6, j*6+6);
                m = BaseTable.getLetter(m);
                message = message + m;
            }
        }
        return message;
    }

    public static String getRandomBinValue(int k) {
        String randomBin = "";
        Random random = new Random();
        for (int i = 0; i < k*6; i++) {
            randomBin = randomBin + random.nextInt(2);
        }
        return randomBin;
    }

}
