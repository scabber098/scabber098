class Solution {
    public int maxNumberOfFamilies(int n, int[][] reservedSeats) {
        HashMap<Integer, HashSet<Integer>> map = new HashMap<>();

        for (int[] seat : reservedSeats) {
            map.putIfAbsent(seat[0], new HashSet<>());
            map.get(seat[0]).add(seat[1]);
        }

        int ans = (n - map.size()) * 2;

        for (int row : map.keySet()) {
            HashSet<Integer> seats = map.get(row);

            boolean left = true;
            boolean right = true;
            boolean middle = true;

            for (int i = 2; i <= 5; i++) {
                if (seats.contains(i)) left = false;
            }

            for (int i = 6; i <= 9; i++) {
                if (seats.contains(i)) right = false;
            }

            for (int i = 4; i <= 7; i++) {
                if (seats.contains(i)) middle = false;
            }

            if (left && right) {
                ans += 2;
            } else if (left || right || middle) {
                ans++;
            }
        }

        return ans;
    }
}