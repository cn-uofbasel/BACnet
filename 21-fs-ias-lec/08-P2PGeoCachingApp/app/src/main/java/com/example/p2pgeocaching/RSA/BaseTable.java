package com.example.p2pgeocaching.RSA;

/**
 * This class is used to translate the letters a to z, A to Z, the numbers 0...9
 * and the space into base64 encoding an vice versa
 */
public class BaseTable {
    // Array which holds all letters and their specific base64 encoding
    private static String[][] table = {
            {"A", "000000"},
            {"B", "000001"},
            {"C", "000010"},
            {"D", "000011"},
            {"E", "000100"},
            {"F", "000101"},
            {"G", "000110"},
            {"H", "000111"},
            {"I", "001000"},
            {"J", "001001"},
            {"K", "001010"},
            {"L", "001011"},
            {"M", "001100"},
            {"N", "001101"},
            {"O", "001110"},
            {"P", "001111"},
            {"Q", "010000"},
            {"R", "010001"},
            {"S", "010010"},
            {"T", "010011"},
            {"U", "010100"},
            {"V", "010101"},
            {"W", "010110"},
            {"X", "010111"},
            {"Y", "011000"},
            {"Z", "011001"},
            {"a", "011010"},
            {"b", "011011"},
            {"c", "011100"},
            {"d", "011101"},
            {"e", "011110"},
            {"f", "011111"},
            {"g", "100000"},
            {"h", "100001"},
            {"i", "100010"},
            {"j", "100011"},
            {"k", "100100"},
            {"l", "100101"},
            {"m", "100110"},
            {"n", "100111"},
            {"o", "101000"},
            {"p", "101001"},
            {"q", "101010"},
            {"r", "101011"},
            {"s", "101100"},
            {"t", "101101"},
            {"u", "101110"},
            {"v", "101111"},
            {"w", "110000"},
            {"x", "110001"},
            {"y", "110010"},
            {"z", "110011"},
            {"0", "110100"},
            {"1", "110101"},
            {"2", "110110"},
            {"3", "110111"},
            {"4", "111000"},
            {"5", "111001"},
            {"6", "111010"},
            {"7", "111011"},
            {"8", "111100"},
            {"9", "111101"},
            {" ", "111110"}};

    /**
     * This method is used to translate the given letter into
     * it's base64 enconding
     *
     * @param letter letter which should be translated to binary value
     * @return base64 encoding of letter as string, if letter isn't listed in the
     * array an empty string is returned
     */
    public static String getBinValue(String letter) {
        for (int i = 0; i < table.length; i++) {
            if (table[i][0].compareTo(letter) == 0) {
                // could find the given letter in the array
                return table[i][1];
            }
        }
        // letter couldn'tbe found in the array, so return an empty string
        return "";
    }

    /**
     * This method is used to translate given base64 encoding to
     * it's ASCII letter
     *
     * @param binValue base64 encoding which should be translated to a letter
     * @return letter as string, if binary value isn't listed in the array
     * an empty string is returned
     */
    public static String getLetter(String binValue) {
        for (int i = 0; i < table.length; i++) {
            if (table[i][1].compareTo(binValue) == 0) {
                // could find the given base64 encoding in the array
                return table[i][0];
            }
        }
        // base64 encoding couldn't be found int the array, so return an empty string
        return "";
    }
}
