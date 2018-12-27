// Copyright 2018 Xanadu Quantum Technologies Inc.

// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at

//     http://www.apache.org/licenses/LICENSE-2.0

// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
#include <iostream>
#include <complex>
#include <hafnian.hpp>


int main() {
    int nmax = 10;

    for (int m = 1; m <= nmax; m++) {
        int n = 2*m;
        hafnian::vec_complex mat(n*n, 1.0);

        std::complex<double> hafval = hafnian::loop_hafnian(mat);
        std::cout << hafval << std::endl;
    }

    return 0;\
};