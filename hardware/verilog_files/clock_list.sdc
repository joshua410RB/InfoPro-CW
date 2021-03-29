create_clock -name "test_clk" -period 20.000ns [get_ports {test_clk}]
create_clock -name "sys_clk" -period 20.000ns [get_ports {sys_clk}]
create_clock -name "MAX10_CLK1_50" -period 20.000ns [get_ports {MAX10_CLK1_50}]