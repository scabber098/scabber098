class Solution {
    public long findKthSmallest(int[] coins, int k) {
        long low = 1, high = (long) coins[0] * k;

        while (low < high) {
            long mid = low + (high - low) / 2;

            if (count(mid, coins) >= k)
                high = mid;
            else
                low = mid + 1;
        }

        return low;
    }

    private long count(long x, int[] coins) {
        long result = 0;
        int n = coins.length;

        for (int mask = 1; mask < (1 << n); mask++) {
            long lcm = 1;
            boolean valid = true;
            int bits = 0;

            for (int i = 0; i < n; i++) {
                if ((mask & (1 << i)) != 0) {
                    bits++;
                    long g = gcd(lcm, coins[i]);
                    lcm = lcm / g * coins[i];

                    if (lcm > x) {
                        valid = false;
                        break;
                    }
                }
            }

            if (valid) {
                long add = x / lcm;
                if (bits % 2 == 1)
                    result += add;
                else
                    result -= add;
            }
        }

        return result;
    }

    private long gcd(long a, long b) {
        while (b != 0) {
            long temp = a % b;
            a = b;
            b = temp;
        }
        return a;
    }
}