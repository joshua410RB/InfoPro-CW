	component nios2_cpu is
		port (
			accel_interrupt_export : in  std_logic                     := 'X';             -- export
			accel_xdata_export     : in  std_logic_vector(15 downto 0) := (others => 'X'); -- export
			accel_ydata_export     : in  std_logic_vector(15 downto 0) := (others => 'X'); -- export
			accel_zdata_export     : in  std_logic_vector(15 downto 0) := (others => 'X'); -- export
			clk_clk                : in  std_logic                     := 'X';             -- clk
			disp0_export           : out std_logic_vector(7 downto 0);                     -- export
			disp1_export           : out std_logic_vector(7 downto 0);                     -- export
			led_export             : out std_logic_vector(9 downto 0);                     -- export
			reset_reset_n          : in  std_logic                     := 'X';             -- reset_n
			switch_export          : in  std_logic_vector(10 downto 0) := (others => 'X'); -- export
			update_control_export  : out std_logic_vector(8 downto 0);                     -- export
			update_value_export    : out std_logic_vector(15 downto 0);                    -- export
			x_coeff_bank_export    : out std_logic_vector(1 downto 0);                     -- export
			y_coeff_bank_export    : out std_logic_vector(1 downto 0);                     -- export
			z_coeff_bank_export    : out std_logic_vector(1 downto 0)                      -- export
		);
	end component nios2_cpu;

	u0 : component nios2_cpu
		port map (
			accel_interrupt_export => CONNECTED_TO_accel_interrupt_export, -- accel_interrupt.export
			accel_xdata_export     => CONNECTED_TO_accel_xdata_export,     --     accel_xdata.export
			accel_ydata_export     => CONNECTED_TO_accel_ydata_export,     --     accel_ydata.export
			accel_zdata_export     => CONNECTED_TO_accel_zdata_export,     --     accel_zdata.export
			clk_clk                => CONNECTED_TO_clk_clk,                --             clk.clk
			disp0_export           => CONNECTED_TO_disp0_export,           --           disp0.export
			disp1_export           => CONNECTED_TO_disp1_export,           --           disp1.export
			led_export             => CONNECTED_TO_led_export,             --             led.export
			reset_reset_n          => CONNECTED_TO_reset_reset_n,          --           reset.reset_n
			switch_export          => CONNECTED_TO_switch_export,          --          switch.export
			update_control_export  => CONNECTED_TO_update_control_export,  --  update_control.export
			update_value_export    => CONNECTED_TO_update_value_export,    --    update_value.export
			x_coeff_bank_export    => CONNECTED_TO_x_coeff_bank_export,    --    x_coeff_bank.export
			y_coeff_bank_export    => CONNECTED_TO_y_coeff_bank_export,    --    y_coeff_bank.export
			z_coeff_bank_export    => CONNECTED_TO_z_coeff_bank_export     --    z_coeff_bank.export
		);

