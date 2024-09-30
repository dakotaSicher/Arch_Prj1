x86:
	gcc sieve.c -lm -o sieve_static -static

riscv:
	riscv64-linux-gnu-gcc sieve.c -o sieve_riscv -static -lm

clean:
	rm sieve_riscv sieve_static