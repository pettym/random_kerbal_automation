set datafile separator ","
set key autotitle columnhead

set grid
set term x11 persist
#unset border
#unset xtics
#set yrange[0:100]


#plot 'test.csv' using 1:2 with lines, '' using 1:3 with lines

#set yrange [-2:5]
#set ytics 20000
#set y2tics
#set y2range [-1:1]
#plot '1.csv' using 1:2 with lines, '' using 1:3 with lines axis x1y2


set ytics
set y2tics
set yrange [-0.1:0.1]
set y2range [-0.1:0.1]
set xtics 0,2

plot '1.csv' using 1:2 with lines, '' using 1:4 with lines axis x1y2