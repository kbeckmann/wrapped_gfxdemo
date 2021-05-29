/*
 * SPDX-FileCopyrightText: 2020 Efabless Corporation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * SPDX-License-Identifier: Apache-2.0
 */

#include "verilog/dv/caravel/defs.h"

/*
    IO Test:
        - Configures MPRJ lower 8-IO pins as outputs
        - Observes counter value through the MPRJ lower 8 IO pins (in the testbench)
*/

#define MPRJ_BASE 0x30000000
#define REG0 ((volatile uint32_t*) (MPRJ_BASE + 0x00))
#define REG1 ((volatile uint32_t*) (MPRJ_BASE + 0x04))
#define REG2 ((volatile uint32_t*) (MPRJ_BASE + 0x08))
#define REG3 ((volatile uint32_t*) (MPRJ_BASE + 0x0c))

#define MPRJ_FB 0x30000100
#define FB0 ((volatile uint32_t*) (MPRJ_FB + 0x00))
#define FB1 ((volatile uint32_t*) (MPRJ_FB + 0x04))
#define FB2 ((volatile uint32_t*) (MPRJ_FB + 0x08))
#define FB3 ((volatile uint32_t*) (MPRJ_FB + 0x0c))

#pragma GCC optimize ("Os")

void main()
{
    /* 
    IO Control Registers
    | DM     | VTRIP | SLOW  | AN_POL | AN_SEL | AN_EN | MOD_SEL | INP_DIS | HOLDH | OEB_N | MGMT_EN |
    | 3-bits | 1-bit | 1-bit | 1-bit  | 1-bit  | 1-bit | 1-bit   | 1-bit   | 1-bit | 1-bit | 1-bit   |

    Output: 0000_0110_0000_1110  (0x1808) = GPIO_MODE_USER_STD_OUTPUT
    | DM     | VTRIP | SLOW  | AN_POL | AN_SEL | AN_EN | MOD_SEL | INP_DIS | HOLDH | OEB_N | MGMT_EN |
    | 110    | 0     | 0     | 0      | 0      | 0     | 0       | 1       | 0     | 0     | 0       |
    
     
    Input: 0000_0001_0000_1111 (0x0402) = GPIO_MODE_USER_STD_INPUT_NOPULL
    | DM     | VTRIP | SLOW  | AN_POL | AN_SEL | AN_EN | MOD_SEL | INP_DIS | HOLDH | OEB_N | MGMT_EN |
    | 001    | 0     | 0     | 0      | 0      | 0     | 0       | 0       | 0     | 1     | 0       |

    */

    // 6 inputs for encoder
    reg_mprj_io_8 =   GPIO_MODE_USER_STD_INPUT_NOPULL;
    reg_mprj_io_9 =   GPIO_MODE_USER_STD_INPUT_NOPULL;
    reg_mprj_io_10 =  GPIO_MODE_USER_STD_INPUT_NOPULL;
    reg_mprj_io_11 =  GPIO_MODE_USER_STD_INPUT_NOPULL;
    reg_mprj_io_12 =  GPIO_MODE_USER_STD_INPUT_NOPULL;
    reg_mprj_io_13 =  GPIO_MODE_USER_STD_INPUT_NOPULL;

    // 3 outputs for PWM, starting at 8
    reg_mprj_io_14 =  GPIO_MODE_USER_STD_OUTPUT;
    reg_mprj_io_15 =  GPIO_MODE_USER_STD_OUTPUT;
    reg_mprj_io_16 =  GPIO_MODE_USER_STD_OUTPUT;

    /* Apply configuration */
    reg_mprj_xfer = 1;
    while (reg_mprj_xfer == 1);

    // activate the project by setting the 0th bit of 2nd bank of LA
    reg_la1_ena  = 0;
    reg_la1_data = 1;

    // reset design with 0bit of 1st bank of LA
    reg_la0_ena  = 0;
    reg_la0_data = 1;
    reg_la0_data = 0;


#if 0
    reg_spimaster_config = 0xa002;	// Enable, prescaler = 2,
                    // connect to housekeeping SPI

    // Apply stream read (0x40 + 0x03) and read back one byte 

    // 0x08 = 0x01
    reg_spimaster_config = 0xb002;	// Apply stream mode
    reg_spimaster_data = 0x80;		// Write 0x80 (write mode)
    reg_spimaster_data = 0x08;		// Write 0x08 (start address)
    reg_spimaster_data = 0x03;		// Write 0x01 to PLL enable, no DCO mode
    reg_spimaster_config = 0xa102;	// Release CSB (ends stream mode)

    // 0x11 = 0x0d
    reg_spimaster_config = 0xb002;	// Apply stream mode
    reg_spimaster_data = 0x80;		// Write 0x80 (write mode)
    reg_spimaster_data = 0x11;		// Write 0x11 (start address)
    reg_spimaster_data = 0x09;		// Write 0x0d to PLL output divider
    reg_spimaster_config = 0xa102;	// Release CSB (ends stream mode)

    // 0x12 = 0x0f
    reg_spimaster_config = 0xb002;	// Apply stream mode
    reg_spimaster_data = 0x80;		// Write 0x80 (write mode)
    reg_spimaster_data = 0x12;		// Write 0x12 (start address)
    reg_spimaster_data = 0x0f;		// Write 0x0f to PLL output divider
    reg_spimaster_config = 0xa102;	// Release CSB (ends stream mode)

    // 0x09 = 0x00
    reg_spimaster_config = 0xb002;	// Apply stream mode
    reg_spimaster_data = 0x80;		// Write 0x80 (write mode)
    reg_spimaster_data = 0x09;		// Write 0x09 (start address)
    reg_spimaster_data = 0x00;		// Write 0x00 to clock from PLL (no bypass)
    reg_spimaster_config = 0xa102;	// Release CSB (ends stream mode)

    reg_spimaster_config = 0x2102;	// Release housekeeping SPI
#endif

    *FB0 = 0x01010101;
    *FB1 = 0x02020202;
    *FB2 = 0x04040404;
    *FB3 = 0x08080808;

    *REG0 = *FB0;
    *REG1 = *FB1;
    *REG2 = *FB2;
    *REG3 = *FB3;

/*
    *REG0 = 0x01020304;
    *REG1 = 0x10203040;
    *REG2 = 0x11223344;
    *REG3 = 0xcafef00d;
    *REG0 = *REG1;
    *REG1 = *REG2;
    *REG2 = *REG3;
    *REG3 = *REG0;
*/

}

