#!/bin/bash

if [[ $# -eq 1 ]] ; then
    RUNS=$1
else
    RUNS=200000
fi

SAVEDIR=~/Arch_Prj1/ini_and_configs/RISCV
BINARY=~/Arch_Prj1/sieve_riscv

echo "##################################################"

#tutorial run w/o cache
gem5/build/RISCV/gem5.opt gem5/configs/tutorial/part1/simple-riscv.py --riscv=1
cp m5out/config.ini $SAVEDIR/config_without_cache.ini
cp m5out/stats.txt $SAVEDIR/stats_without_cache.txt

echo "##################################################"

#tutorial run w/cache
gem5/build/RISCV/gem5.opt gem5/configs/tutorial/part1/two_level.py --riscv=1 --caches
cp m5out/config.ini $SAVEDIR/config_with_cache.ini
cp m5out/stats.txt $SAVEDIR/stats_with_cache.txt

echo "##################################################"

#sieve run SimpleCPU
gem5/build/RISCV/gem5.opt gem5/configs/tutorial/part1/two_level.py  --cmd=$BINARY -o "$RUNS" --riscv=1
cp m5out/config.ini $SAVEDIR/config_TimingSimpleCPU_sieve.ini
cp m5out/stats.txt $SAVEDIR/stats_TimingSimpleCPU_sieve.txt

echo "##################################################"

#sieve run MinorCPU
gem5/build/RISCV/gem5.opt gem5/configs/tutorial/part1/two_level.py  --cmd=$BINARY -o "$RUNS" --cpu=minor --riscv=1 --caches
cp m5out/config.ini $SAVEDIR/config_MinorCPU_sieve.ini
cp m5out/stats.txt $SAVEDIR/stats_MinorCPU_sieve.txt


for CLOCK in "1GHz" "1.5GHz" "2GHz" "2.5GHz" "3GHz";
do
echo "##################################################"

#direct l1I=32k, direct l1D=64k, unified L2=4m 
#sieve run SimpleCPU
gem5/build/RISCV/gem5.opt gem5/configs/tutorial/part1/two_level.py  -cmd=$BINARY -o "$RUNS" --caches --l1i_size='32kB' --l1i_assoc=1 --l1d_size='64kB' --l1d_assoc=1 --l2_size='4MB' --riscv=1
cp m5out/config.ini $SAVEDIR/config_TimingSimpleCPU_DirectCache_sieve_$CLOCK.ini
cp m5out/stats.txt $SAVEDIR/stats_TimingSimpleCPU_DirectCache_sieve_$CLOCK.txt

echo "##################################################"

#sieve run MinorCPU
gem5/build/RISCV/gem5.opt gem5/configs/tutorial/part1/two_level.py  --cmd=$BINARY -o "$RUNS" --cpu=minor --caches --l1i_size='32kB' --l1i_assoc=1 --l1d_size='64kB' --l1d_assoc=1 --l2_size='4MB' --clock=$CLOCK --riscv=1
cp m5out/config.ini $SAVEDIR/config_MinorCPU_DirectCache_sieve_$CLOCK.ini
cp m5out/stats.txt $SAVEDIR/stats_MinorCPU_DirectCache_sieve_$CLOCK.txt

done
