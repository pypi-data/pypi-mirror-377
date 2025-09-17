import time,sys
import numpy as np

class TDC7200:
    DDS_MAX_FREQ = 0xFFFFFFF-1    #24 bit resolution
    #control bytes
    clockScaler = 4 # 8MHz
    # --- TDC7200 Register Definitions (from datasheet) ---
    INT_STATUS_REG = 0x00
    INT_MASK_REG = 0x01
    CONFIG1_REG = 0x02
    CONFIG2_REG = 0x03
    CLOCK_RATE_REG = 0x04
    TDC_MEAS_ACK_TIMEOUT_REG = 0x05
    # Time and Calibration Registers (24-bit values, read sequentially)
    TIME1_MSB_REG = 0x10
    TIME1_MID_REG = 0x11
    TIME1_LSB_REG = 0x12
    CALIBRATION1_MSB_REG = 0x1D
    CALIBRATION1_MID_REG = 0x1E
    CALIBRATION1_LSB_REG = 0x1F
    CALIBRATION2_MSB_REG = 0x20
    CALIBRATION2_MID_REG = 0x21
    CALIBRATION2_LSB_REG = 0x22

    def __init__(self,dev=None):
        self.CS='CS1'
        self.CS4 = 'CS4'
        self.device = dev
        self.device.SPI.set_parameters(2,2,1,1,0)
        self.device.SPI.stop('CS2') #Enable pin HIGH.
        self.device.SPI.map_reference_clock(self.clockScaler,'WAVEGEN')
        print ('clock set to ',self.device.SPI.DDS_CLOCK )
        print(self.device.SPI.xfer(self.CS,[]))

    def tdc7200_write_reg(self,reg_addr, data_byte):
        """Writes a single byte to a TDC7200 register."""
        # MSB 0 for write operation
        cmd_byte = reg_addr & 0x7F
        self.device.SPI.xfer(self.CS,[cmd_byte, data_byte])  # Use cs parameter if CS1 is not default

    def tdc7200_read_reg(self,reg_addr):
        """Reads a single byte from a TDC7200 register."""
        # MSB 1 for read operation
        cmd_byte = 0x80 | (reg_addr & 0x7F)
        # Send command byte + dummy byte to clock out the data
        read_response = self.device.SPI.xfer(self.CS,[cmd_byte,0x00])
        return read_response[1]

    def tdc7200_read_24bit_reg(self,base_reg_addr):
        """Reads a 24-bit value from a sequential 3-byte register set."""
        msb = self.tdc7200_read_reg(base_reg_addr)
        mid = self.tdc7200_read_reg(base_reg_addr + 1)
        lsb = self.tdc7200_read_reg(base_reg_addr + 2)
        return (msb << 16) | (mid << 8) | lsb

    def measure1(self):

        # --- Main TDC7200 Acquisition Sequence ---
        try:
            print("\n--- Initializing TDC7200 ---")

            # 1. Soft Reset the TDC7200 (if not already done by EN pin toggle)
            # Write 0 to RST_N (bit 0 of CONFIG1) to reset, then 1 to clear reset.
            self.tdc7200_write_reg(self.CONFIG1_REG, 0x00)  # Reset
            time.sleep(0.01)  # Small delay for reset to take effect
            self.tdc7200_write_reg(self.CONFIG1_REG, 0x01)  # Clear reset (set RST_N to 1 for normal operation)
            print("TDC7200 soft reset complete.")

            # 2. Configure TDC7200 Registers for Mode 1
            # CONFIG1:
            # - MEAS_MODE = 0 (Mode 1)
            # - START_CAL = 1 (Enable self-calibration)
            # - NUM_AVG = 0 (No averaging for now, just 1 START/STOP pair)
            # - RST_N = 1 (Already set above, ensuring it's not in reset)
            config1_value = 0b00000001  # RST_N=1, NUM_AVG=000, START_CAL=1, MEAS_MODE=0
            self.tdc7200_write_reg(self.CONFIG1_REG, config1_value)
            print(f"  CONFIG1 set to: {config1_value:08b} (Mode 1, Self-Cal Enabled)")

            # CONFIG2:
            # - CAL2_PERIOD = 000 (2 CLK_IN cycles for CAL2) - default
            # - NUM_STOP = 000 (Expects 1 STOP pulse)
            config2_value = 0b00000000  # CAL2_PERIOD=000, NUM_STOP=000
            self.tdc7200_write_reg(self.CONFIG2_REG, config2_value)
            print(f"  CONFIG2 set to: {config2_value:08b} (1 STOP pulse, CAL2_PERIOD=2)")

            # CLOCK_RATE (for internal calculation and timeout)
            # For 8MHz CLK_IN, set CLOCK_RATE_MHZ = 8.
            self.tdc7200_write_reg(self.CLOCK_RATE_REG, 0x08)
            print("  CLOCK_RATE set to 8MHz.")

            # TDC_MEAS_ACK_TIMEOUT (set this higher than your max expected ToF)
            # Default is 0xFF, which is usually fine for short ToF. Let's set it to 1000 clock cycles (125 us)
            # Value depends on CLOCK_RATE and desired timeout. 0x05 for 1000 CLK_IN cycles (1000 * 125ns = 125 us).
            self.tdc7200_write_reg(self.TDC_MEAS_ACK_TIMEOUT_REG, 0x05)
            print("  TDC_MEAS_ACK_TIMEOUT set (e.g., 125 us).")

            # INT_MASK: Enable NEW_MEAS_COMPLETED_MASK to drive INTB low
            # bit 1 of INT_MASK register
            self.tdc7200_write_reg(self.INT_MASK_REG, 0b00000010)  # Set bit 1
            print("  INT_MASK: NEW_MEAS_COMPLETED_MASK enabled.")

            # Clear any pending interrupt status by reading it
            initial_status = self.tdc7200_read_reg(self.INT_STATUS_REG)
            print(f"  Initial INT_STATUS: {initial_status:02X} (should be 0 or cleared after read)")

            print("\n--- Starting Measurement ---")


            print("\n--- Querying Measurement Status ---")

            # Wait for measurement to complete by polling INT_STATUS register
            max_wait_time = 1  # second
            start_time = time.time()
            measurement_completed = False

            while (time.time() - start_time) < max_wait_time:
                status_byte = self.tdc7200_read_reg(self.INT_STATUS_REG)
                # Check NEW_MEAS_COMPLETED bit (bit 1 of INT_STATUS)
                print(f"  Measuring..: {status_byte}")
                if (status_byte >> 1) & 0x01:
                    print(f"  Measurement completed! INT_STATUS: {status_byte:02X}")
                    measurement_completed = True
                    break
                time.sleep(0.001)  # Poll every 1ms

            if not measurement_completed:
                print("  Error: Measurement did not complete within timeout. Check pulses/wiring.")
            else:
                print("\n--- Retrieving Data ---")
                # Read the 24-bit TIME1 and CALIBRATION1 registers
                time1_raw = self.tdc7200_read_24bit_reg(self.TIME1_MSB_REG)
                calibration1_raw = self.tdc7200_read_24bit_reg(self.CALIBRATION1_MSB_REG)  # Note: CALIBRATION1 is 0x1D, 0x1E, 0x1F

                print(f"  Raw TIME1: {time1_raw}")
                print(f"  Raw CALIBRATION1: {calibration1_raw}")

                calibration2_raw = self.tdc7200_read_24bit_reg(self.CALIBRATION2_MSB_REG)
                print(f"  Raw CALIBRATION2: {calibration2_raw}")

                T_CLK_HZ = 8_000_000  # 8 MHz
                T_CLK_PS = 1_000_000_000_000 / T_CLK_HZ  # T_CLK in picoseconds (125000 ps = 125 ns)
                CAL2_PERIOD = 2  # From CONFIG2, 000b = 2 clock cycles

                # Ensure CALIBRATION1 is not zero to prevent division by zero
                if calibration1_raw == 0:
                    print("  Error: CALIBRATION1 is 0. Cannot calculate ToF. Check setup.")
                elif calibration1_raw == calibration2_raw:  # Check if CALIBRATION1 and CALIBRATION2 are the same (common in very short ToF for mode 1)
                    print(
                        "  Warning: CALIBRATION1 and CALIBRATION2 are identical, might indicate very short or no valid stop. Check datasheet formula again.")
                    print(f"  CALIBRATION1 - CALIBRATION2 = {calibration1_raw - calibration2_raw}")
                else:
                    # Formula for Mode 1 and Mode 2 from datasheet Section 8.3
                    # LSB = (CAL2_PERIOD * T_CLK_PS) / (CALIBRATION1_raw - CALIBRATION2_raw)
                    # TOF = TIME1_raw * LSB
                    denominator = (calibration1_raw - calibration2_raw)
                    if denominator == 0:
                        print("  Error: Denominator (CALIBRATION1 - CALIBRATION2) is zero. Cannot calculate ToF.")
                    else:
                        lsb_ps = (CAL2_PERIOD * T_CLK_PS) / denominator
                        time_of_flight_ps = time1_raw * lsb_ps
                        time_of_flight_ns = time_of_flight_ps / 1000.0

                        print(f"\n  Calculated LSB: {lsb_ps:.3f} ps/LSB")
                        print(f"  Calculated Time-of-Flight: {time_of_flight_ps:.3f} ps")
                        print(f"  Calculated Time-of-Flight: {time_of_flight_ns:.3f} ns")


        except Exception as e:
            print(f"\nAn error occurred: {e}")
        finally:
            print("\n--- Cleaning Up ---")
