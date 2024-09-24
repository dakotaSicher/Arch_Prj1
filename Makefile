sieve:
	gcc sieve.c -lm -o sieve

static:
	gcc sieve.c -lm -o sieve_static -static

clean:
	rm sieve sieve_static