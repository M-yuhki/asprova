#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <cassert>
#include <iostream>
#include <sstream>
#include <fstream>
#include <string>
#include <vector>
#include <queue>
#include <set>
#include <map>
#include <utility>
#include <numeric>
#include <algorithm>
#include <bitset>
#include <complex>
class Order {
public:
    int r;	/** オーダ番号    : Order number */
    int i;  /** 品目番号      : Item number */
    int e;  /** 最早開始時刻  : Earliest start time */
    int d;  /** 納期          : Deadline */
    int q;  /** 製造数量      : Manufacturing quanity */
    Order(int _r, int _i, int _e, int _d, int _q) {
        r = _r;
        i = _i;
        e = _e;
        d = _d;
        q = _q;
    }
};
class Bom {
public:
    int i;  /** 品目番号             : Item number */
    int p;  /** 工程番号             : Process number */
    int m;  /** 設備番号             : Machine number */
    int t;  /** 1個当たりの製造時間  : Manufacturing time per piece */
    Bom(int _i, int _p, int _m, int _t) {
        i = _i;
        p = _p;
        m = _m;
        t = _t;
    }
};
class Operation {  /** 作業 **/
public:
    int m;  /** 設備番号           : Machine number */
    int r;  /** オーダ番号         : Order number */
    int p;  /** 工程番号           : Process number */
    int t1; /** 段取り開始時刻     : Setup start time */
    int t2; /** 製造開始           : Manufacturing start time */
    int t3; /** 製造終了           : Manufacturing end time */
    Operation(int _m, int _r, int _p, int _t1, int _t2, int _t3) {
        m = _m;
        r = _r;
        p = _p;
        t1 = _t1;
        t2 = _t2;
        t3 = _t3;
    }
};
int M;     /** 設備数                   : Number of machines */
int I;     /** 品目数                   : Number of items */
int P;     /** 最大工程数               : Max number of processes*/
int R;     /** 注文数                   : Number of Processes */
int BL;    /** BOM行数                  : Number of BOM lines */
double A1; /** 段取り時間ペナルティ係数 : Setup time penalty */
double A2; /** 納期遅れペナルティ係数   : Missed deadline penalty */
double A3; /** 着手遅延ポイント係数     : Assignment lateness bonus */
double B1; /** 段取り時間べき乗数       : Setup time exponent */
double B2; /** 納期遅れべき乗数         : Missed deadline exponent */
double B3; /** 着手遅延べき乗数         : Late assignment exponent */

std::vector<int> iToP; /** 各品目の工程数           : Number of processes by each item */
std::vector<int> C;    /** Cm 設備mの製造時間係数   : Machine manufacturing time multiplier */
std::vector<int> D;    /** Dm 設備mの段取り時間係数 : Machine setup time multiplier */

std::vector<Order> orders;
std::vector<Operation> operations;
std::vector<std::vector<std::vector<int>>> times;
int time(int m, int i, int p) {
    return times[m][i][p];
}
bool canMake(int m, int i, int p) {
    return times[m][i][p] != -1;
}
int main(int argc, char* argv[]) {
    try {
        std::ifstream in(argv[1]);
        std::ifstream out(argv[2]);

        std::string s;
        in >> s >> M >> I >> P >> R >> BL;
        in >> s >> A1 >> A2 >> A3 >> B1 >> B2 >> B3;
        in >> s;
        C.resize(M);
        for (int m = 0; m < M; m++) {
            in >> C[m];
        }
        in >> s;
        D.resize(M);
        for (int m = 0; m < M; m++) {
            in >> D[m];
        }
        times.assign(M, std::vector<std::vector<int>>(I, std::vector<int>(P, -1)));
        iToP.assign(I, 0);
        for (int n = 0; n < BL; ++n) {
            int i, p, m, t;
            in >> s >> i >> p >> m >> t;
            times[m - 1][i - 1][p - 1] = t;
            iToP[i - 1] = std::max(iToP[i - 1], p);
        }
        for (int r = 0; r < R; ++r) {
            int r2, i, e, d, q;
            in >> s >> r2 >> i >> e >> d >> q;
            orders.push_back(Order(r2 - 1, i - 1, e, d, q));
        }
        P = 0;
        for (int i = 0; i < iToP.size(); i++) {
            P = std::max(P, iToP[i]);
        }
        int expectedOperations = 0;
        for (int r = 0; r < R; r++) {
            expectedOperations += iToP[orders[r].i];
        }
        int OL;
        out >> OL;
        if (OL != expectedOperations) {
            return 1;
        }
        for (int i = 0; i < OL; i++) {
            int m, r, p, t1, t2, t3;
            out >> m >> r >> p >> t1 >> t2 >> t3;
            if (out.eof()) {
                return 1;
            }
            m--;
            r--;
            p--;
            if (m < 0 && m >= M) {
                std::cerr << "m is out of range." << std::endl;
                return 1;
            }
            if (r < 0 && r >= R) {
                std::cerr << "r is out of range." << std::endl;
                return 1;
            }
            if (p < 0 && p >= iToP[orders[r].i]) {
                std::cerr << "p is out of range." << std::endl;
                return 1;
            }
            if (t1 < 0) {
                std::cerr << "t1 must be nonnegative." << std::endl;
                return 1;
            }
            if (t2 < 0) {
                std::cerr << "t2 must be nonnegative." << std::endl;
                return 1;
            }
            if (t3 < 0) {
                std::cerr << "t3 must be nonnegative." << std::endl;
                return 1;
            }
            operations.push_back(Operation(m, r, p, t1, t2, t3));
        }
        std::sort(operations.begin(), operations.end(), []( const Operation& o1, const Operation& o2 ) {return o1.t1 < o2.t1;});

        std::vector<int> mToPreviousT3(M, 0);							/* 各設備の前回の製造終了時刻 : Previous manufacturing end time of each machine */
        std::vector<int> mToPreviousI(M, -1);							/* 各設備の前回の品目 : Previous item of each machine */
        std::vector<std::vector<int>> t3rp(R, std::vector<int>(P, -1));	/* 各オーダの各工程の製造終了時刻 : Manufacturing end time of each process of each order */
        for (int i = 0; i < operations.size(); i++) {
            Operation& o = operations[i];
            if (o.t1 < 0) {
                std::cerr << "計画開始時刻違反 : Scheduling start time violation" << std::endl;
                return 1;
            }
            if (o.t2 < 0) {
                std::cerr << "計画開始時刻違反 : Scheduling start time violation" << std::endl;
                return 1;
            }
            if (o.t1 < orders[o.r].e) {
                std::cerr << "段取り開始時刻違反 : Setup start time violation" << std::endl;
                return 1;
            }
            if (o.p > 0) {
                if (t3rp[o.r][o.p - 1] == -1) {
                    std::cerr << "前の工程の作業が割付いていません。: Previous process operation is not assigned." << std::endl;
                    return 1;
                }
                if (o.t1 < t3rp[o.r][o.p - 1]) {
                    std::cerr << "段取り開始時刻違反 : Setup start time violation" << std::endl;
                    return 1;
                }
            }
            for (int i2 = 0; i2 < i; i2++) {
                Operation& o2 = operations[i2];
                if (o2.m != o.m) {
                    continue;
                }
                if (o.t1 < o2.t3) {
                    std::cerr << "設備キャパシティ違反 : Machine capacity violation" << std::endl;
                    return 1;
                }
            }
            if (mToPreviousI[o.m] == -1) {
                if (o.t2 - o.t1 != 0) {
                    std::cerr << "段取り時間間違い : Setup time error" << std::endl;
                    return 1;
                }
            } else {
                if (o.t2 - o.t1 != D[o.m] * (std::abs(mToPreviousI[o.m] - orders[o.r].i) % 3)) {
                    std::cerr << "段取り時間間違い : Setup time error" << std::endl;
                    return 1;
                }
            }
            if (o.t3 - o.t2 != C[o.m] * time(o.m, orders[o.r].i, o.p) * orders[o.r].q) {
                std::cerr << "製造時間間違い : Manufacturing time error" << std::endl;
                return 1;
            }
            if (!canMake(o.m, orders[o.r].i, o.p)) {
                std::cerr << "BOM違反 : BOM violation" << std::endl;
                return 1;
            }
            mToPreviousT3[o.m] = o.t3;
            mToPreviousI[o.m] = orders[o.r].i;
            if (t3rp[o.r][o.p] != -1) {
                std::cerr << "分割禁止 : Split operation detected" << std::endl;
                return 1;
            }
            t3rp[o.r][o.p] = o.t3;
        }
        for (int r = 0; r < R; r++) {
            for (int p = 0; p < iToP[orders[r].i]; p++) {
                if (t3rp[r][p] == -1) {
                    std::cerr << "未割り付け禁止 : Not assigend operation detected" << std::endl;
                    return 1;
                }
            }
        }
        double V1 = 0;
        double V2 = 0;
        double V3 = 0;
        for (int i = 0; i < operations.size(); i++) {
            Operation& o = operations[i];
            V1 += pow(o.t2 - o.t1, B1);
            if (o.p + 1 == iToP[orders[o.r].i]) {
                V2 += pow(std::max(o.t3 - orders[o.r].d, 0), B2);
            }
            if (o.p == 0) {
                V3 += pow(std::min(o.t1, orders[o.r].d) - orders[o.r].e, B3);
            }
        }
        long long V = static_cast<long long>(std::max(0.0, (1e6 - A1 * V1 - A2 * V2 + A3 * V3)));
        printf("IMOJUDGE<<<%lld>>>\n", V);
        return 0;
    } catch (char* str) {
        std::cerr << "error: " << str << std::endl;
        return 1;
    }
    return 1;
}
