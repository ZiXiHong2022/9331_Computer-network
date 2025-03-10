set title "Throughput Over Time"
set xlabel "Time[s]"
set ylabel "Throughtput [Mbps]"


set key outside
set key bel

plot "tcp1 .tr" using ($1) : ($2) title  'TCP 1' w lp lc rgb "blue", title  'TCP 2' w lp lc rgb "blue",

pause -1

