#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

int is_prime(int, bool*);

int sieve(int n){
    bool* primes = (bool*)calloc(n+1,sizeof(bool));
    if (primes == NULL) {
        perror("allocating primes[]");
        exit(-1);
    }

    primes[0] = primes[1] = false;
    primes[2] = true;

    int primes_count = 1;
    for(int i = 3; i <= n; i++){
        if (is_prime(i,primes)){
            primes[i]= true;
            primes_count++;
        }
    }

    free(primes);
    return primes_count;
}

int is_prime(int n, bool* primes){
    int maxF = (int)sqrt((double)n);
    for (int i = 0; i <= maxF; i++){
        if (primes[i] && n%i==0)
            return false;
    }
    return true;
}

int main(int argc, char* argv[]){
    int n = atoi(argv[1]);

    int count = sieve(n);
    printf("prime count is %i\n", count);

    exit(0);
}