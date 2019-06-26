
################################################################
# This is a generated script based on design: system
#
# Though there are limitations about the generated script,
# the main purpose of this utility is to make learning
# IP Integrator Tcl commands easier.
################################################################

namespace eval _tcl {
proc get_script_folder {} {
   set script_path [file normalize [info script]]
   set script_folder [file dirname $script_path]
   return $script_folder
}
}
variable script_folder
set script_folder [_tcl::get_script_folder]

################################################################
# Check if script is running in correct Vivado version.
################################################################
set scripts_vivado_version 2017.4
set current_vivado_version [version -short]

if { [string first $scripts_vivado_version $current_vivado_version] == -1 } {
   puts ""
   catch {common::send_msg_id "BD_TCL-109" "ERROR" "This script was generated using Vivado <$scripts_vivado_version> and is being run in <$current_vivado_version> of Vivado. Please run the script in Vivado <$scripts_vivado_version> then open the design in Vivado <$current_vivado_version>. Upgrade the design by running \"Tools => Report => Report IP Status...\", then run write_bd_tcl to create an updated script."}

   return 1
}

################################################################
# START
################################################################

# To test this script, run the following commands from Vivado Tcl console:
# source system_script.tcl

# If there is no project opened, this script will create a
# project, but make sure you do not have an existing project
# <./myproj/project_1.xpr> in the current working folder.

set list_projs [get_projects -quiet]
if { $list_projs eq "" } {
   create_project project_1 myproj -part xc7z020clg400-1
}


# CHANGE DESIGN NAME HERE
variable design_name
set design_name system

# If you do not already have an existing IP Integrator design open,
# you can create a design using the following command:
#    create_bd_design $design_name

# Creating design if needed
set errMsg ""
set nRet 0

set cur_design [current_bd_design -quiet]
set list_cells [get_bd_cells -quiet]

if { ${design_name} eq "" } {
   # USE CASES:
   #    1) Design_name not set

   set errMsg "Please set the variable <design_name> to a non-empty value."
   set nRet 1

} elseif { ${cur_design} ne "" && ${list_cells} eq "" } {
   # USE CASES:
   #    2): Current design opened AND is empty AND names same.
   #    3): Current design opened AND is empty AND names diff; design_name NOT in project.
   #    4): Current design opened AND is empty AND names diff; design_name exists in project.

   if { $cur_design ne $design_name } {
      common::send_msg_id "BD_TCL-001" "INFO" "Changing value of <design_name> from <$design_name> to <$cur_design> since current design is empty."
      set design_name [get_property NAME $cur_design]
   }
   common::send_msg_id "BD_TCL-002" "INFO" "Constructing design in IPI design <$cur_design>..."

} elseif { ${cur_design} ne "" && $list_cells ne "" && $cur_design eq $design_name } {
   # USE CASES:
   #    5) Current design opened AND has components AND same names.

   set errMsg "Design <$design_name> already exists in your project, please set the variable <design_name> to another value."
   set nRet 1
} elseif { [get_files -quiet ${design_name}.bd] ne "" } {
   # USE CASES: 
   #    6) Current opened design, has components, but diff names, design_name exists in project.
   #    7) No opened design, design_name exists in project.

   set errMsg "Design <$design_name> already exists in your project, please set the variable <design_name> to another value."
   set nRet 2

} else {
   # USE CASES:
   #    8) No opened design, design_name not in project.
   #    9) Current opened design, has components, but diff names, design_name not in project.

   common::send_msg_id "BD_TCL-003" "INFO" "Currently there is no design <$design_name> in project, so creating one..."

   create_bd_design $design_name

   common::send_msg_id "BD_TCL-004" "INFO" "Making design <$design_name> as current_bd_design."
   current_bd_design $design_name

}

common::send_msg_id "BD_TCL-005" "INFO" "Currently the variable <design_name> is equal to \"$design_name\"."

if { $nRet != 0 } {
   catch {common::send_msg_id "BD_TCL-114" "ERROR" $errMsg}
   return $nRet
}

##################################################################
# DESIGN PROCs
##################################################################


# Hierarchical cell: microblaze_core
proc create_hier_cell_microblaze_core { parentCell nameHier } {

  variable script_folder

  if { $parentCell eq "" || $nameHier eq "" } {
     catch {common::send_msg_id "BD_TCL-102" "ERROR" "create_hier_cell_microblaze_core() - Empty argument(s)!"}
     return
  }

  # Get object for parentCell
  set parentObj [get_bd_cells $parentCell]
  if { $parentObj == "" } {
     catch {common::send_msg_id "BD_TCL-100" "ERROR" "Unable to find parent cell <$parentCell>!"}
     return
  }

  # Make sure parentObj is hier blk
  set parentType [get_property TYPE $parentObj]
  if { $parentType ne "hier" } {
     catch {common::send_msg_id "BD_TCL-101" "ERROR" "Parent <$parentObj> has TYPE = <$parentType>. Expected to be <hier>."}
     return
  }

  # Save current instance; Restore later
  set oldCurInst [current_bd_instance .]

  # Set parent object as current
  current_bd_instance $parentObj

  # Create cell and set as current instance
  set hier_obj [create_bd_cell -type hier $nameHier]
  current_bd_instance $hier_obj

  # Create interface pins
  create_bd_intf_pin -mode Master -vlnv xilinx.com:interface:lmb_rtl:1.0 DLMB
  create_bd_intf_pin -mode Master -vlnv xilinx.com:interface:lmb_rtl:1.0 ILMB
  create_bd_intf_pin -mode Master -vlnv xilinx.com:interface:aximm_rtl:1.0 M_AXI
  create_bd_intf_pin -mode Slave -vlnv xilinx.com:interface:aximm_rtl:1.0 S1_AXI
  create_bd_intf_pin -mode Slave -vlnv xilinx.com:interface:axis_rtl:1.0 S2_AXIS

  # Create pins
  create_bd_pin -dir I -type clk Clk
  create_bd_pin -dir O Interrupt_1
  create_bd_pin -dir I -from 0 -to 0 PCap
  create_bd_pin -dir I -from 0 -to 0 S1_AXI_ARESETN
  create_bd_pin -dir O aclk
  create_bd_pin -dir O -from 0 -to 0 aresetn
  create_bd_pin -dir O -from 0 -to 0 bus_struct_reset
  create_bd_pin -dir I -from 0 -to 0 ext_reset_in

  # Create instance: axi_intc_0, and set properties
  set axi_intc_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:axi_intc:4.1 axi_intc_0 ]
  set_property -dict [ list \
   CONFIG.C_IRQ_IS_LEVEL {0} \
 ] $axi_intc_0

  # Create instance: axi_interconnect_0, and set properties
  set axi_interconnect_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:axi_interconnect:2.1 axi_interconnect_0 ]
  set_property -dict [ list \
   CONFIG.NUM_MI {5} \
   CONFIG.SYNCHRONIZATION_STAGES {2} \
 ] $axi_interconnect_0

  # Create instance: axi_timer_0, and set properties
  set axi_timer_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:axi_timer:2.0 axi_timer_0 ]
  set_property -dict [ list \
   CONFIG.mode_64bit {1} \
 ] $axi_timer_0

  # Create instance: mailbox, and set properties
  set mailbox [ create_bd_cell -type ip -vlnv xilinx.com:ip:mailbox:2.1 mailbox ]
  set_property -dict [ list \
   CONFIG.C_IMPL_STYLE {1} \
   CONFIG.C_MAILBOX_DEPTH {512} \
 ] $mailbox

  # Create instance: mdm_1, and set properties
  set mdm_1 [ create_bd_cell -type ip -vlnv xilinx.com:ip:mdm:3.2 mdm_1 ]
  set_property -dict [ list \
   CONFIG.C_USE_UART {1} \
 ] $mdm_1

  # Create instance: microblaze_0, and set properties
  set microblaze_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:microblaze:10.0 microblaze_0 ]
  set_property -dict [ list \
   CONFIG.C_D_AXI {1} \
   CONFIG.C_FSL_LINKS {3} \
   CONFIG.C_ICACHE_BASEADDR {0x0000000000000000} \
   CONFIG.C_ICACHE_HIGHADDR {0x000000003FFFFFFF} \
   CONFIG.C_NUMBER_OF_RD_ADDR_BRK {1} \
   CONFIG.C_NUMBER_OF_WR_ADDR_BRK {1} \
   CONFIG.C_PVR {1} \
   CONFIG.C_PVR_USER1 {0x02} \
   CONFIG.C_USE_BARREL {1} \
   CONFIG.C_USE_EXTENDED_FSL_INSTR {1} \
   CONFIG.C_USE_FPU {2} \
   CONFIG.C_USE_HW_MUL {2} \
 ] $microblaze_0

  # Create instance: proc_mb_reset_0, and set properties
  set proc_mb_reset_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:proc_sys_reset:5.0 proc_mb_reset_0 ]

  # Create instance: xlconcat_0, and set properties
  set xlconcat_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlconcat:2.1 xlconcat_0 ]

  # Create instance: xlconstant_locked, and set properties
  set xlconstant_locked [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlconstant:1.1 xlconstant_locked ]
  set_property -dict [ list \
   CONFIG.CONST_VAL {1} \
 ] $xlconstant_locked

  # Create interface connections
  connect_bd_intf_net -intf_net Conn1 [get_bd_intf_pins S1_AXI] [get_bd_intf_pins mailbox/S1_AXI]
  connect_bd_intf_net -intf_net Conn2 [get_bd_intf_pins M_AXI] [get_bd_intf_pins axi_interconnect_0/M04_AXI]
  connect_bd_intf_net -intf_net Conn3 [get_bd_intf_pins S2_AXIS] [get_bd_intf_pins microblaze_0/S2_AXIS]
  connect_bd_intf_net -intf_net axi_intc_0_interrupt [get_bd_intf_pins axi_intc_0/interrupt] [get_bd_intf_pins microblaze_0/INTERRUPT]
  connect_bd_intf_net -intf_net axi_interconnect_0_M00_AXI [get_bd_intf_pins axi_intc_0/s_axi] [get_bd_intf_pins axi_interconnect_0/M00_AXI]
  connect_bd_intf_net -intf_net axi_interconnect_0_M01_AXI [get_bd_intf_pins axi_interconnect_0/M01_AXI] [get_bd_intf_pins mailbox/S0_AXI]
  connect_bd_intf_net -intf_net axi_interconnect_0_M02_AXI [get_bd_intf_pins axi_interconnect_0/M02_AXI] [get_bd_intf_pins axi_timer_0/S_AXI]
  connect_bd_intf_net -intf_net axi_interconnect_0_M03_AXI [get_bd_intf_pins axi_interconnect_0/M03_AXI] [get_bd_intf_pins mdm_1/S_AXI]
  connect_bd_intf_net -intf_net microblaze_0_DLMB [get_bd_intf_pins DLMB] [get_bd_intf_pins microblaze_0/DLMB]
  connect_bd_intf_net -intf_net microblaze_0_ILMB [get_bd_intf_pins ILMB] [get_bd_intf_pins microblaze_0/ILMB]
  connect_bd_intf_net -intf_net microblaze_0_M_AXI_DP [get_bd_intf_pins axi_interconnect_0/S00_AXI] [get_bd_intf_pins microblaze_0/M_AXI_DP]
  connect_bd_intf_net -intf_net microblaze_0_debug [get_bd_intf_pins mdm_1/MBDEBUG_0] [get_bd_intf_pins microblaze_0/DEBUG]

  # Create port connections
  connect_bd_net -net Clk_1 [get_bd_pins Clk] [get_bd_pins aclk] [get_bd_pins axi_intc_0/s_axi_aclk] [get_bd_pins axi_interconnect_0/ACLK] [get_bd_pins axi_interconnect_0/M00_ACLK] [get_bd_pins axi_interconnect_0/M01_ACLK] [get_bd_pins axi_interconnect_0/M02_ACLK] [get_bd_pins axi_interconnect_0/M03_ACLK] [get_bd_pins axi_interconnect_0/M04_ACLK] [get_bd_pins axi_interconnect_0/S00_ACLK] [get_bd_pins axi_timer_0/s_axi_aclk] [get_bd_pins mailbox/S0_AXI_ACLK] [get_bd_pins mailbox/S1_AXI_ACLK] [get_bd_pins mdm_1/S_AXI_ACLK] [get_bd_pins microblaze_0/Clk] [get_bd_pins proc_mb_reset_0/slowest_sync_clk]
  connect_bd_net -net PCap_1 [get_bd_pins PCap] [get_bd_pins axi_timer_0/capturetrig0] [get_bd_pins axi_timer_0/capturetrig1]
  connect_bd_net -net S1_AXI_ARESETN_1 [get_bd_pins S1_AXI_ARESETN] [get_bd_pins mailbox/S1_AXI_ARESETN]
  connect_bd_net -net axi_timer_0_generateout0 [get_bd_pins axi_timer_0/generateout0] [get_bd_pins microblaze_0/S0_AXIS_TVALID]
  set_property -dict [ list \
HDL_ATTRIBUTE.MARK_DEBUG {true} \
 ] [get_bd_nets axi_timer_0_generateout0]
  connect_bd_net -net axi_timer_0_generateout1 [get_bd_pins axi_timer_0/generateout1] [get_bd_pins microblaze_0/S1_AXIS_TVALID]
  connect_bd_net -net axi_timer_0_interrupt [get_bd_pins axi_timer_0/interrupt] [get_bd_pins xlconcat_0/In0]
  connect_bd_net -net ext_reset_in_1 [get_bd_pins ext_reset_in] [get_bd_pins proc_mb_reset_0/ext_reset_in]
  connect_bd_net -net mailbox_0_Interrupt_1 [get_bd_pins Interrupt_1] [get_bd_pins mailbox/Interrupt_1]
  connect_bd_net -net mailbox_Interrupt_0 [get_bd_pins mailbox/Interrupt_0] [get_bd_pins xlconcat_0/In1]
  connect_bd_net -net mdm_1_Debug_SYS_Rst [get_bd_pins mdm_1/Debug_SYS_Rst] [get_bd_pins proc_mb_reset_0/mb_debug_sys_rst]
  set_property -dict [ list \
HDL_ATTRIBUTE.MARK_DEBUG {true} \
 ] [get_bd_nets mdm_1_Debug_SYS_Rst]
  connect_bd_net -net proc_mb_reset_0_bus_struct_reset [get_bd_pins bus_struct_reset] [get_bd_pins proc_mb_reset_0/bus_struct_reset]
  connect_bd_net -net proc_sys_reset_0_mb_reset [get_bd_pins microblaze_0/Reset] [get_bd_pins proc_mb_reset_0/mb_reset]
  set_property -dict [ list \
HDL_ATTRIBUTE.MARK_DEBUG {true} \
 ] [get_bd_nets proc_sys_reset_0_mb_reset]
  connect_bd_net -net proc_sys_reset_0_peripheral_aresetn [get_bd_pins aresetn] [get_bd_pins proc_mb_reset_0/peripheral_aresetn]
  connect_bd_net -net rst_clk_wiz_1_100M_interconnect_aresetn [get_bd_pins axi_intc_0/s_axi_aresetn] [get_bd_pins axi_interconnect_0/ARESETN] [get_bd_pins axi_interconnect_0/M00_ARESETN] [get_bd_pins axi_interconnect_0/M01_ARESETN] [get_bd_pins axi_interconnect_0/M02_ARESETN] [get_bd_pins axi_interconnect_0/M03_ARESETN] [get_bd_pins axi_interconnect_0/M04_ARESETN] [get_bd_pins axi_interconnect_0/S00_ARESETN] [get_bd_pins axi_timer_0/s_axi_aresetn] [get_bd_pins mailbox/S0_AXI_ARESETN] [get_bd_pins mdm_1/S_AXI_ARESETN] [get_bd_pins proc_mb_reset_0/interconnect_aresetn]
  set_property -dict [ list \
HDL_ATTRIBUTE.MARK_DEBUG {true} \
 ] [get_bd_nets rst_clk_wiz_1_100M_interconnect_aresetn]
  connect_bd_net -net xlconcat_0_dout [get_bd_pins axi_intc_0/intr] [get_bd_pins xlconcat_0/dout]
  connect_bd_net -net xlconstant_locked_const [get_bd_pins proc_mb_reset_0/dcm_locked] [get_bd_pins xlconstant_locked/dout]

  # Restore current instance
  current_bd_instance $oldCurInst
}

# Hierarchical cell: microblaze_0_local_memory
proc create_hier_cell_microblaze_0_local_memory { parentCell nameHier } {

  variable script_folder

  if { $parentCell eq "" || $nameHier eq "" } {
     catch {common::send_msg_id "BD_TCL-102" "ERROR" "create_hier_cell_microblaze_0_local_memory() - Empty argument(s)!"}
     return
  }

  # Get object for parentCell
  set parentObj [get_bd_cells $parentCell]
  if { $parentObj == "" } {
     catch {common::send_msg_id "BD_TCL-100" "ERROR" "Unable to find parent cell <$parentCell>!"}
     return
  }

  # Make sure parentObj is hier blk
  set parentType [get_property TYPE $parentObj]
  if { $parentType ne "hier" } {
     catch {common::send_msg_id "BD_TCL-101" "ERROR" "Parent <$parentObj> has TYPE = <$parentType>. Expected to be <hier>."}
     return
  }

  # Save current instance; Restore later
  set oldCurInst [current_bd_instance .]

  # Set parent object as current
  current_bd_instance $parentObj

  # Create cell and set as current instance
  set hier_obj [create_bd_cell -type hier $nameHier]
  current_bd_instance $hier_obj

  # Create interface pins
  create_bd_intf_pin -mode MirroredMaster -vlnv xilinx.com:interface:lmb_rtl:1.0 DLMB
  create_bd_intf_pin -mode MirroredMaster -vlnv xilinx.com:interface:lmb_rtl:1.0 ILMB
  create_bd_intf_pin -mode Slave -vlnv xilinx.com:interface:aximm_rtl:1.0 S00_AXI

  # Create pins
  create_bd_pin -dir I ACLK
  create_bd_pin -dir I -from 0 -to 0 ARESETN
  create_bd_pin -dir I LMB_Clk
  create_bd_pin -dir I -from 0 -to 0 LMB_Rst

  # Create instance: axi_bram_ctrl_d, and set properties
  set axi_bram_ctrl_d [ create_bd_cell -type ip -vlnv xilinx.com:ip:axi_bram_ctrl:4.0 axi_bram_ctrl_d ]
  set_property -dict [ list \
   CONFIG.C_SELECT_XPM {0} \
   CONFIG.SINGLE_PORT_BRAM {1} \
 ] $axi_bram_ctrl_d

  # Create instance: axi_bram_ctrl_i, and set properties
  set axi_bram_ctrl_i [ create_bd_cell -type ip -vlnv xilinx.com:ip:axi_bram_ctrl:4.0 axi_bram_ctrl_i ]
  set_property -dict [ list \
   CONFIG.C_SELECT_XPM {0} \
   CONFIG.SINGLE_PORT_BRAM {1} \
 ] $axi_bram_ctrl_i

  # Create instance: axi_bram_ctrl_p, and set properties
  set axi_bram_ctrl_p [ create_bd_cell -type ip -vlnv xilinx.com:ip:axi_bram_ctrl:4.0 axi_bram_ctrl_p ]
  set_property -dict [ list \
   CONFIG.C_SELECT_XPM {0} \
   CONFIG.SINGLE_PORT_BRAM {1} \
 ] $axi_bram_ctrl_p

  # Create instance: axi_interconnect_0, and set properties
  set axi_interconnect_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:axi_interconnect:2.1 axi_interconnect_0 ]
  set_property -dict [ list \
   CONFIG.ENABLE_ADVANCED_OPTIONS {0} \
   CONFIG.NUM_MI {3} \
   CONFIG.SYNCHRONIZATION_STAGES {2} \
 ] $axi_interconnect_0

  # Create instance: bram_d, and set properties
  set bram_d [ create_bd_cell -type ip -vlnv xilinx.com:ip:blk_mem_gen:8.4 bram_d ]
  set_property -dict [ list \
   CONFIG.EN_SAFETY_CKT {false} \
   CONFIG.Enable_B {Use_ENB_Pin} \
   CONFIG.Memory_Type {True_Dual_Port_RAM} \
   CONFIG.Port_B_Clock {100} \
   CONFIG.Port_B_Enable_Rate {100} \
   CONFIG.Port_B_Write_Rate {50} \
   CONFIG.Use_RSTB_Pin {true} \
 ] $bram_d

  # Create instance: bram_i, and set properties
  set bram_i [ create_bd_cell -type ip -vlnv xilinx.com:ip:blk_mem_gen:8.4 bram_i ]
  set_property -dict [ list \
   CONFIG.EN_SAFETY_CKT {false} \
   CONFIG.Enable_B {Use_ENB_Pin} \
   CONFIG.Memory_Type {True_Dual_Port_RAM} \
   CONFIG.Port_B_Clock {100} \
   CONFIG.Port_B_Enable_Rate {100} \
   CONFIG.Port_B_Write_Rate {50} \
   CONFIG.Use_RSTB_Pin {true} \
 ] $bram_i

  # Create instance: bram_p, and set properties
  set bram_p [ create_bd_cell -type ip -vlnv xilinx.com:ip:blk_mem_gen:8.4 bram_p ]
  set_property -dict [ list \
   CONFIG.EN_SAFETY_CKT {false} \
   CONFIG.Enable_B {Use_ENB_Pin} \
   CONFIG.Memory_Type {True_Dual_Port_RAM} \
   CONFIG.Port_B_Clock {100} \
   CONFIG.Port_B_Enable_Rate {100} \
   CONFIG.Port_B_Write_Rate {50} \
   CONFIG.Use_RSTB_Pin {true} \
 ] $bram_p

  # Create instance: dlmb_bram_if_cntlr_d, and set properties
  set dlmb_bram_if_cntlr_d [ create_bd_cell -type ip -vlnv xilinx.com:ip:lmb_bram_if_cntlr:4.0 dlmb_bram_if_cntlr_d ]

  # Create instance: dlmb_bram_if_cntlr_p, and set properties
  set dlmb_bram_if_cntlr_p [ create_bd_cell -type ip -vlnv xilinx.com:ip:lmb_bram_if_cntlr:4.0 dlmb_bram_if_cntlr_p ]

  # Create instance: dlmb_v10, and set properties
  set dlmb_v10 [ create_bd_cell -type ip -vlnv xilinx.com:ip:lmb_v10:3.0 dlmb_v10 ]
  set_property -dict [ list \
   CONFIG.C_LMB_NUM_SLAVES {2} \
 ] $dlmb_v10

  # Create instance: ilmb_bram_if_ctrl_i, and set properties
  set ilmb_bram_if_ctrl_i [ create_bd_cell -type ip -vlnv xilinx.com:ip:lmb_bram_if_cntlr:4.0 ilmb_bram_if_ctrl_i ]

  # Create instance: ilmb_v10, and set properties
  set ilmb_v10 [ create_bd_cell -type ip -vlnv xilinx.com:ip:lmb_v10:3.0 ilmb_v10 ]

  # Create interface connections
  connect_bd_intf_net -intf_net Conn [get_bd_intf_pins dlmb_bram_if_cntlr_p/SLMB] [get_bd_intf_pins dlmb_v10/LMB_Sl_1]
  connect_bd_intf_net -intf_net Conn1 [get_bd_intf_pins S00_AXI] [get_bd_intf_pins axi_interconnect_0/S00_AXI]
  connect_bd_intf_net -intf_net axi_bram_ctrl_0_BRAM_PORTA [get_bd_intf_pins axi_bram_ctrl_i/BRAM_PORTA] [get_bd_intf_pins bram_i/BRAM_PORTB]
  connect_bd_intf_net -intf_net axi_bram_ctrl_d_BRAM_PORTA [get_bd_intf_pins axi_bram_ctrl_d/BRAM_PORTA] [get_bd_intf_pins bram_d/BRAM_PORTB]
  connect_bd_intf_net -intf_net axi_bram_ctrl_p_BRAM_PORTA [get_bd_intf_pins axi_bram_ctrl_p/BRAM_PORTA] [get_bd_intf_pins bram_p/BRAM_PORTB]
  connect_bd_intf_net -intf_net axi_interconnect_0_M00_AXI [get_bd_intf_pins axi_bram_ctrl_p/S_AXI] [get_bd_intf_pins axi_interconnect_0/M00_AXI]
  connect_bd_intf_net -intf_net axi_interconnect_0_M01_AXI [get_bd_intf_pins axi_bram_ctrl_d/S_AXI] [get_bd_intf_pins axi_interconnect_0/M01_AXI]
  connect_bd_intf_net -intf_net axi_interconnect_0_M02_AXI [get_bd_intf_pins axi_bram_ctrl_i/S_AXI] [get_bd_intf_pins axi_interconnect_0/M02_AXI]
  connect_bd_intf_net -intf_net dlmb_bram_if_cntlr_p_BRAM_PORT [get_bd_intf_pins bram_p/BRAM_PORTA] [get_bd_intf_pins dlmb_bram_if_cntlr_p/BRAM_PORT]
  connect_bd_intf_net -intf_net ilmb_bram_if_cntlr_BRAM_PORT [get_bd_intf_pins bram_i/BRAM_PORTA] [get_bd_intf_pins ilmb_bram_if_ctrl_i/BRAM_PORT]
  connect_bd_intf_net -intf_net microblaze_0_dlmb [get_bd_intf_pins DLMB] [get_bd_intf_pins dlmb_v10/LMB_M]
  connect_bd_intf_net -intf_net microblaze_0_dlmb_bus [get_bd_intf_pins dlmb_bram_if_cntlr_d/SLMB] [get_bd_intf_pins dlmb_v10/LMB_Sl_0]
  connect_bd_intf_net -intf_net microblaze_0_dlmb_cntlr [get_bd_intf_pins bram_d/BRAM_PORTA] [get_bd_intf_pins dlmb_bram_if_cntlr_d/BRAM_PORT]
  connect_bd_intf_net -intf_net microblaze_0_ilmb [get_bd_intf_pins ILMB] [get_bd_intf_pins ilmb_v10/LMB_M]
  connect_bd_intf_net -intf_net microblaze_0_ilmb_bus [get_bd_intf_pins ilmb_bram_if_ctrl_i/SLMB] [get_bd_intf_pins ilmb_v10/LMB_Sl_0]

  # Create port connections
  connect_bd_net -net ACLK_1 [get_bd_pins ACLK] [get_bd_pins axi_bram_ctrl_d/s_axi_aclk] [get_bd_pins axi_bram_ctrl_i/s_axi_aclk] [get_bd_pins axi_bram_ctrl_p/s_axi_aclk] [get_bd_pins axi_interconnect_0/ACLK] [get_bd_pins axi_interconnect_0/M00_ACLK] [get_bd_pins axi_interconnect_0/M01_ACLK] [get_bd_pins axi_interconnect_0/M02_ACLK] [get_bd_pins axi_interconnect_0/S00_ACLK]
  connect_bd_net -net ARESETN_1 [get_bd_pins ARESETN] [get_bd_pins axi_bram_ctrl_d/s_axi_aresetn] [get_bd_pins axi_bram_ctrl_i/s_axi_aresetn] [get_bd_pins axi_bram_ctrl_p/s_axi_aresetn] [get_bd_pins axi_interconnect_0/ARESETN] [get_bd_pins axi_interconnect_0/M00_ARESETN] [get_bd_pins axi_interconnect_0/M01_ARESETN] [get_bd_pins axi_interconnect_0/M02_ARESETN] [get_bd_pins axi_interconnect_0/S00_ARESETN]
  connect_bd_net -net LMB_Clk_1 [get_bd_pins LMB_Clk] [get_bd_pins dlmb_bram_if_cntlr_d/LMB_Clk] [get_bd_pins dlmb_bram_if_cntlr_p/LMB_Clk] [get_bd_pins dlmb_v10/LMB_Clk] [get_bd_pins ilmb_bram_if_ctrl_i/LMB_Clk] [get_bd_pins ilmb_v10/LMB_Clk]
  connect_bd_net -net LMB_Rst_1 [get_bd_pins LMB_Rst] [get_bd_pins dlmb_bram_if_cntlr_d/LMB_Rst] [get_bd_pins dlmb_bram_if_cntlr_p/LMB_Rst] [get_bd_pins dlmb_v10/SYS_Rst] [get_bd_pins ilmb_bram_if_ctrl_i/LMB_Rst] [get_bd_pins ilmb_v10/SYS_Rst]

  # Restore current instance
  current_bd_instance $oldCurInst
}

# Hierarchical cell: pulse_gen_1
proc create_hier_cell_pulse_gen_1 { parentCell nameHier } {

  variable script_folder

  if { $parentCell eq "" || $nameHier eq "" } {
     catch {common::send_msg_id "BD_TCL-102" "ERROR" "create_hier_cell_pulse_gen_1() - Empty argument(s)!"}
     return
  }

  # Get object for parentCell
  set parentObj [get_bd_cells $parentCell]
  if { $parentObj == "" } {
     catch {common::send_msg_id "BD_TCL-100" "ERROR" "Unable to find parent cell <$parentCell>!"}
     return
  }

  # Make sure parentObj is hier blk
  set parentType [get_property TYPE $parentObj]
  if { $parentType ne "hier" } {
     catch {common::send_msg_id "BD_TCL-101" "ERROR" "Parent <$parentObj> has TYPE = <$parentType>. Expected to be <hier>."}
     return
  }

  # Save current instance; Restore later
  set oldCurInst [current_bd_instance .]

  # Set parent object as current
  current_bd_instance $parentObj

  # Create cell and set as current instance
  set hier_obj [create_bd_cell -type hier $nameHier]
  current_bd_instance $hier_obj

  # Create interface pins

  # Create pins
  create_bd_pin -dir I -type clk CLK
  create_bd_pin -dir O -from 0 -to 0 Dout
  create_bd_pin -dir I -from 0 -to 0 Op1

  # Create instance: c_counter_binary_count1, and set properties
  set c_counter_binary_count1 [ create_bd_cell -type ip -vlnv xilinx.com:ip:c_counter_binary:12.0 c_counter_binary_count1 ]
  set_property -dict [ list \
   CONFIG.CE {true} \
   CONFIG.Output_Width {3} \
   CONFIG.SCLR {true} \
   CONFIG.Sync_Threshold_Output {false} \
 ] $c_counter_binary_count1

  # Create instance: util_vector_logic_not, and set properties
  set util_vector_logic_not [ create_bd_cell -type ip -vlnv xilinx.com:ip:util_vector_logic:2.0 util_vector_logic_not ]
  set_property -dict [ list \
   CONFIG.C_OPERATION {not} \
   CONFIG.C_SIZE {1} \
   CONFIG.LOGO_FILE {data/sym_notgate.png} \
 ] $util_vector_logic_not

  # Create instance: util_vector_logic_not2, and set properties
  set util_vector_logic_not2 [ create_bd_cell -type ip -vlnv xilinx.com:ip:util_vector_logic:2.0 util_vector_logic_not2 ]
  set_property -dict [ list \
   CONFIG.C_OPERATION {not} \
   CONFIG.C_SIZE {1} \
   CONFIG.LOGO_FILE {data/sym_notgate.png} \
 ] $util_vector_logic_not2

  # Create instance: xlslice_b1_ioupdate2, and set properties
  set xlslice_b1_ioupdate2 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 xlslice_b1_ioupdate2 ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {2} \
   CONFIG.DIN_TO {2} \
   CONFIG.DIN_WIDTH {3} \
 ] $xlslice_b1_ioupdate2

  # Create instance: xlslice_b3_ce, and set properties
  set xlslice_b3_ce [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 xlslice_b3_ce ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {2} \
   CONFIG.DIN_TO {2} \
   CONFIG.DIN_WIDTH {3} \
 ] $xlslice_b3_ce

  # Create port connections
  connect_bd_net -net Op1_1 [get_bd_pins Op1] [get_bd_pins util_vector_logic_not/Op1]
  connect_bd_net -net P_CLK_1 [get_bd_pins CLK] [get_bd_pins c_counter_binary_count1/CLK]
  connect_bd_net -net c_counter_binary_divby5_Q [get_bd_pins c_counter_binary_count1/Q] [get_bd_pins xlslice_b1_ioupdate2/Din] [get_bd_pins xlslice_b3_ce/Din]
  connect_bd_net -net util_vector_logic_not2_Res [get_bd_pins c_counter_binary_count1/CE] [get_bd_pins util_vector_logic_not2/Res]
  connect_bd_net -net util_vector_logic_not_Res [get_bd_pins c_counter_binary_count1/SCLR] [get_bd_pins util_vector_logic_not/Res]
  connect_bd_net -net xlslice_b1_ioupdate1_Dout [get_bd_pins util_vector_logic_not2/Op1] [get_bd_pins xlslice_b3_ce/Dout]
  connect_bd_net -net xlslice_b1_ioupdate2_Dout [get_bd_pins Dout] [get_bd_pins xlslice_b1_ioupdate2/Dout]

  # Restore current instance
  current_bd_instance $oldCurInst
}

# Hierarchical cell: pulse_gen_0
proc create_hier_cell_pulse_gen_0 { parentCell nameHier } {

  variable script_folder

  if { $parentCell eq "" || $nameHier eq "" } {
     catch {common::send_msg_id "BD_TCL-102" "ERROR" "create_hier_cell_pulse_gen_0() - Empty argument(s)!"}
     return
  }

  # Get object for parentCell
  set parentObj [get_bd_cells $parentCell]
  if { $parentObj == "" } {
     catch {common::send_msg_id "BD_TCL-100" "ERROR" "Unable to find parent cell <$parentCell>!"}
     return
  }

  # Make sure parentObj is hier blk
  set parentType [get_property TYPE $parentObj]
  if { $parentType ne "hier" } {
     catch {common::send_msg_id "BD_TCL-101" "ERROR" "Parent <$parentObj> has TYPE = <$parentType>. Expected to be <hier>."}
     return
  }

  # Save current instance; Restore later
  set oldCurInst [current_bd_instance .]

  # Set parent object as current
  current_bd_instance $parentObj

  # Create cell and set as current instance
  set hier_obj [create_bd_cell -type hier $nameHier]
  current_bd_instance $hier_obj

  # Create interface pins

  # Create pins
  create_bd_pin -dir I -type clk CLK
  create_bd_pin -dir O -from 0 -to 0 Dout
  create_bd_pin -dir I -from 0 -to 0 Op1

  # Create instance: c_counter_binary_count1, and set properties
  set c_counter_binary_count1 [ create_bd_cell -type ip -vlnv xilinx.com:ip:c_counter_binary:12.0 c_counter_binary_count1 ]
  set_property -dict [ list \
   CONFIG.CE {true} \
   CONFIG.Output_Width {3} \
   CONFIG.SCLR {true} \
   CONFIG.Sync_Threshold_Output {false} \
 ] $c_counter_binary_count1

  # Create instance: util_vector_logic_not, and set properties
  set util_vector_logic_not [ create_bd_cell -type ip -vlnv xilinx.com:ip:util_vector_logic:2.0 util_vector_logic_not ]
  set_property -dict [ list \
   CONFIG.C_OPERATION {not} \
   CONFIG.C_SIZE {1} \
   CONFIG.LOGO_FILE {data/sym_notgate.png} \
 ] $util_vector_logic_not

  # Create instance: util_vector_logic_not2, and set properties
  set util_vector_logic_not2 [ create_bd_cell -type ip -vlnv xilinx.com:ip:util_vector_logic:2.0 util_vector_logic_not2 ]
  set_property -dict [ list \
   CONFIG.C_OPERATION {not} \
   CONFIG.C_SIZE {1} \
   CONFIG.LOGO_FILE {data/sym_notgate.png} \
 ] $util_vector_logic_not2

  # Create instance: xlslice_b1_ioupdate2, and set properties
  set xlslice_b1_ioupdate2 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 xlslice_b1_ioupdate2 ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {2} \
   CONFIG.DIN_TO {2} \
   CONFIG.DIN_WIDTH {3} \
 ] $xlslice_b1_ioupdate2

  # Create instance: xlslice_b3_ce, and set properties
  set xlslice_b3_ce [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 xlslice_b3_ce ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {2} \
   CONFIG.DIN_TO {2} \
   CONFIG.DIN_WIDTH {3} \
 ] $xlslice_b3_ce

  # Create port connections
  connect_bd_net -net Op1_1 [get_bd_pins Op1] [get_bd_pins util_vector_logic_not/Op1]
  connect_bd_net -net P_CLK_1 [get_bd_pins CLK] [get_bd_pins c_counter_binary_count1/CLK]
  connect_bd_net -net c_counter_binary_divby5_Q [get_bd_pins c_counter_binary_count1/Q] [get_bd_pins xlslice_b1_ioupdate2/Din] [get_bd_pins xlslice_b3_ce/Din]
  connect_bd_net -net util_vector_logic_not2_Res [get_bd_pins c_counter_binary_count1/CE] [get_bd_pins util_vector_logic_not2/Res]
  connect_bd_net -net util_vector_logic_not_Res [get_bd_pins c_counter_binary_count1/SCLR] [get_bd_pins util_vector_logic_not/Res]
  connect_bd_net -net xlslice_b1_ioupdate1_Dout [get_bd_pins util_vector_logic_not2/Op1] [get_bd_pins xlslice_b3_ce/Dout]
  connect_bd_net -net xlslice_b1_ioupdate2_Dout [get_bd_pins Dout] [get_bd_pins xlslice_b1_ioupdate2/Dout]

  # Restore current instance
  current_bd_instance $oldCurInst
}

# Hierarchical cell: microblaze_ppu
proc create_hier_cell_microblaze_ppu { parentCell nameHier } {

  variable script_folder

  if { $parentCell eq "" || $nameHier eq "" } {
     catch {common::send_msg_id "BD_TCL-102" "ERROR" "create_hier_cell_microblaze_ppu() - Empty argument(s)!"}
     return
  }

  # Get object for parentCell
  set parentObj [get_bd_cells $parentCell]
  if { $parentObj == "" } {
     catch {common::send_msg_id "BD_TCL-100" "ERROR" "Unable to find parent cell <$parentCell>!"}
     return
  }

  # Make sure parentObj is hier blk
  set parentType [get_property TYPE $parentObj]
  if { $parentType ne "hier" } {
     catch {common::send_msg_id "BD_TCL-101" "ERROR" "Parent <$parentObj> has TYPE = <$parentType>. Expected to be <hier>."}
     return
  }

  # Save current instance; Restore later
  set oldCurInst [current_bd_instance .]

  # Set parent object as current
  current_bd_instance $parentObj

  # Create cell and set as current instance
  set hier_obj [create_bd_cell -type hier $nameHier]
  current_bd_instance $hier_obj

  # Create interface pins
  create_bd_intf_pin -mode Master -vlnv xilinx.com:interface:aximm_rtl:1.0 M_AXI_out
  create_bd_intf_pin -mode Slave -vlnv xilinx.com:interface:aximm_rtl:1.0 S00_AXI
  create_bd_intf_pin -mode Slave -vlnv xilinx.com:interface:axis_rtl:1.0 S2_AXIS

  # Create pins
  create_bd_pin -dir I -from 0 -to 0 ARESETN1
  create_bd_pin -dir O Interrupt_1
  create_bd_pin -dir I -from 0 -to 0 PCap
  create_bd_pin -dir O aclk_out
  create_bd_pin -dir O -from 0 -to 0 areset_out
  create_bd_pin -dir I clk_in1

  # Create instance: axi_interconnect_0, and set properties
  set axi_interconnect_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:axi_interconnect:2.1 axi_interconnect_0 ]
  set_property -dict [ list \
   CONFIG.NUM_MI {3} \
   CONFIG.SYNCHRONIZATION_STAGES {2} \
 ] $axi_interconnect_0

  # Create instance: microblaze_0_local_memory
  create_hier_cell_microblaze_0_local_memory $hier_obj microblaze_0_local_memory

  # Create instance: microblaze_core
  create_hier_cell_microblaze_core $hier_obj microblaze_core

  # Create instance: pp_reset, and set properties
  set pp_reset [ create_bd_cell -type ip -vlnv xilinx.com:ip:axi_gpio:2.0 pp_reset ]
  set_property -dict [ list \
   CONFIG.C_ALL_INPUTS {0} \
   CONFIG.C_ALL_INPUTS_2 {1} \
   CONFIG.C_ALL_OUTPUTS {1} \
   CONFIG.C_DOUT_DEFAULT {0x00000001} \
   CONFIG.C_GPIO2_WIDTH {1} \
   CONFIG.C_GPIO_WIDTH {1} \
   CONFIG.C_INTERRUPT_PRESENT {0} \
   CONFIG.C_IS_DUAL {1} \
 ] $pp_reset

  # Create interface connections
  connect_bd_intf_net -intf_net Conn1 [get_bd_intf_pins M_AXI_out] [get_bd_intf_pins microblaze_core/M_AXI]
  connect_bd_intf_net -intf_net Conn2 [get_bd_intf_pins S2_AXIS] [get_bd_intf_pins microblaze_core/S2_AXIS]
  connect_bd_intf_net -intf_net S00_AXI_1 [get_bd_intf_pins S00_AXI] [get_bd_intf_pins axi_interconnect_0/S00_AXI]
  connect_bd_intf_net -intf_net axi_interconnect_0_M00_AXI [get_bd_intf_pins axi_interconnect_0/M00_AXI] [get_bd_intf_pins pp_reset/S_AXI]
  connect_bd_intf_net -intf_net axi_interconnect_0_M01_AXI [get_bd_intf_pins axi_interconnect_0/M01_AXI] [get_bd_intf_pins microblaze_0_local_memory/S00_AXI]
  connect_bd_intf_net -intf_net axi_interconnect_0_M02_AXI [get_bd_intf_pins axi_interconnect_0/M02_AXI] [get_bd_intf_pins microblaze_core/S1_AXI]
  connect_bd_intf_net -intf_net microblaze_0_DLMB [get_bd_intf_pins microblaze_0_local_memory/DLMB] [get_bd_intf_pins microblaze_core/DLMB]
  connect_bd_intf_net -intf_net microblaze_0_ILMB [get_bd_intf_pins microblaze_0_local_memory/ILMB] [get_bd_intf_pins microblaze_core/ILMB]

  # Create port connections
  connect_bd_net -net ARESETN1_1 [get_bd_pins ARESETN1] [get_bd_pins axi_interconnect_0/ARESETN] [get_bd_pins axi_interconnect_0/M00_ARESETN] [get_bd_pins axi_interconnect_0/M01_ARESETN] [get_bd_pins axi_interconnect_0/M02_ARESETN] [get_bd_pins axi_interconnect_0/S00_ARESETN] [get_bd_pins microblaze_0_local_memory/ARESETN] [get_bd_pins microblaze_core/S1_AXI_ARESETN] [get_bd_pins pp_reset/s_axi_aresetn]
  connect_bd_net -net LMB_Rst_1 [get_bd_pins microblaze_0_local_memory/LMB_Rst] [get_bd_pins microblaze_core/bus_struct_reset] [get_bd_pins pp_reset/gpio2_io_i]
  set_property -dict [ list \
HDL_ATTRIBUTE.MARK_DEBUG {true} \
 ] [get_bd_nets LMB_Rst_1]
  connect_bd_net -net PCap_1 [get_bd_pins PCap] [get_bd_pins microblaze_core/PCap]
  connect_bd_net -net clk_wiz_1_clk_out1 [get_bd_pins clk_in1] [get_bd_pins axi_interconnect_0/ACLK] [get_bd_pins axi_interconnect_0/M00_ACLK] [get_bd_pins axi_interconnect_0/M01_ACLK] [get_bd_pins axi_interconnect_0/M02_ACLK] [get_bd_pins axi_interconnect_0/S00_ACLK] [get_bd_pins microblaze_0_local_memory/ACLK] [get_bd_pins microblaze_core/Clk] [get_bd_pins pp_reset/s_axi_aclk]
  connect_bd_net -net microblaze_core_Interrupt_1 [get_bd_pins Interrupt_1] [get_bd_pins microblaze_core/Interrupt_1]
  connect_bd_net -net microblaze_core_aclk [get_bd_pins aclk_out] [get_bd_pins microblaze_0_local_memory/LMB_Clk] [get_bd_pins microblaze_core/aclk]
  connect_bd_net -net microblaze_core_peripheral_aresetn [get_bd_pins areset_out] [get_bd_pins microblaze_core/aresetn]
  connect_bd_net -net pp_reset_gpio_io_o [get_bd_pins microblaze_core/ext_reset_in] [get_bd_pins pp_reset/gpio_io_o]

  # Restore current instance
  current_bd_instance $oldCurInst
}

# Hierarchical cell: microblaze_mcs_ppu
proc create_hier_cell_microblaze_mcs_ppu { parentCell nameHier } {

  variable script_folder

  if { $parentCell eq "" || $nameHier eq "" } {
     catch {common::send_msg_id "BD_TCL-102" "ERROR" "create_hier_cell_microblaze_mcs_ppu() - Empty argument(s)!"}
     return
  }

  # Get object for parentCell
  set parentObj [get_bd_cells $parentCell]
  if { $parentObj == "" } {
     catch {common::send_msg_id "BD_TCL-100" "ERROR" "Unable to find parent cell <$parentCell>!"}
     return
  }

  # Make sure parentObj is hier blk
  set parentType [get_property TYPE $parentObj]
  if { $parentType ne "hier" } {
     catch {common::send_msg_id "BD_TCL-101" "ERROR" "Parent <$parentObj> has TYPE = <$parentType>. Expected to be <hier>."}
     return
  }

  # Save current instance; Restore later
  set oldCurInst [current_bd_instance .]

  # Set parent object as current
  current_bd_instance $parentObj

  # Create cell and set as current instance
  set hier_obj [create_bd_cell -type hier $nameHier]
  current_bd_instance $hier_obj

  # Create interface pins

  # Create pins
  create_bd_pin -dir O -from 0 -to 0 PERIPHERAL_RESET
  create_bd_pin -dir I SPI_DIN
  create_bd_pin -dir O -from 2 -to 0 SPI_DOUT_CLK_CSN
  create_bd_pin -dir O -from 0 -to 0 SRSET
  create_bd_pin -dir I UART_rxd
  create_bd_pin -dir O UART_txd
  create_bd_pin -dir I clk
  create_bd_pin -dir I reset

  # Create instance: microblaze_mcs_0, and set properties
  set microblaze_mcs_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:microblaze_mcs:3.0 microblaze_mcs_0 ]
  set_property -dict [ list \
   CONFIG.FIT1_No_CLOCKS {100} \
   CONFIG.GPI3_SIZE {1} \
   CONFIG.GPO1_INIT {0x00000000} \
   CONFIG.GPO1_SIZE {1} \
   CONFIG.GPO2_SIZE {1} \
   CONFIG.GPO3_INIT {0x00000001} \
   CONFIG.GPO3_SIZE {4} \
   CONFIG.GPO4_SIZE {4} \
   CONFIG.MEMSIZE {131072} \
   CONFIG.PIT1_INTERRUPT {1} \
   CONFIG.PIT1_PRESCALER {1} \
   CONFIG.PIT1_READABLE {1} \
   CONFIG.UART_BAUDRATE {115200} \
   CONFIG.USE_FIT1 {1} \
   CONFIG.USE_GPI3 {1} \
   CONFIG.USE_GPO1 {1} \
   CONFIG.USE_GPO2 {0} \
   CONFIG.USE_GPO3 {1} \
   CONFIG.USE_GPO4 {0} \
   CONFIG.USE_IO_BUS {0} \
   CONFIG.USE_PIT1 {1} \
   CONFIG.USE_UART_RX {1} \
   CONFIG.USE_UART_TX {1} \
 ] $microblaze_mcs_0

  # Create instance: xlslice_2_0_SPI_2_0, and set properties
  set xlslice_2_0_SPI_2_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 xlslice_2_0_SPI_2_0 ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {2} \
   CONFIG.DIN_TO {0} \
   CONFIG.DIN_WIDTH {4} \
   CONFIG.DOUT_WIDTH {3} \
 ] $xlslice_2_0_SPI_2_0

  # Create instance: xlslice_3_SRSET_3, and set properties
  set xlslice_3_SRSET_3 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 xlslice_3_SRSET_3 ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {3} \
   CONFIG.DIN_TO {3} \
   CONFIG.DIN_WIDTH {4} \
   CONFIG.DOUT_WIDTH {1} \
 ] $xlslice_3_SRSET_3

  # Create port connections
  connect_bd_net -net SPI_DIN_1 [get_bd_pins SPI_DIN] [get_bd_pins microblaze_mcs_0/GPIO3_tri_i]
  connect_bd_net -net UART_rxd_1 [get_bd_pins UART_rxd] [get_bd_pins microblaze_mcs_0/UART_rxd]
  connect_bd_net -net clk_1 [get_bd_pins clk] [get_bd_pins microblaze_mcs_0/Clk]
  connect_bd_net -net microblaze_mcs_0_GPIO1_tri_o [get_bd_pins PERIPHERAL_RESET] [get_bd_pins microblaze_mcs_0/GPIO1_tri_o]
  connect_bd_net -net microblaze_mcs_0_GPIO3_tri_o [get_bd_pins microblaze_mcs_0/GPIO3_tri_o] [get_bd_pins xlslice_2_0_SPI_2_0/Din] [get_bd_pins xlslice_3_SRSET_3/Din]
  connect_bd_net -net microblaze_mcs_0_UART_txd [get_bd_pins UART_txd] [get_bd_pins microblaze_mcs_0/UART_txd]
  connect_bd_net -net reset_1 [get_bd_pins reset] [get_bd_pins microblaze_mcs_0/Reset]
  connect_bd_net -net xlslice_0_Dout [get_bd_pins SPI_DOUT_CLK_CSN] [get_bd_pins xlslice_2_0_SPI_2_0/Dout]
  connect_bd_net -net xlslice_3_SRSET_3_Dout [get_bd_pins SRSET] [get_bd_pins xlslice_3_SRSET_3/Dout]

  # Restore current instance
  current_bd_instance $oldCurInst
}

# Hierarchical cell: ddc
proc create_hier_cell_ddc { parentCell nameHier } {

  variable script_folder

  if { $parentCell eq "" || $nameHier eq "" } {
     catch {common::send_msg_id "BD_TCL-102" "ERROR" "create_hier_cell_ddc() - Empty argument(s)!"}
     return
  }

  # Get object for parentCell
  set parentObj [get_bd_cells $parentCell]
  if { $parentObj == "" } {
     catch {common::send_msg_id "BD_TCL-100" "ERROR" "Unable to find parent cell <$parentCell>!"}
     return
  }

  # Make sure parentObj is hier blk
  set parentType [get_property TYPE $parentObj]
  if { $parentType ne "hier" } {
     catch {common::send_msg_id "BD_TCL-101" "ERROR" "Parent <$parentObj> has TYPE = <$parentType>. Expected to be <hier>."}
     return
  }

  # Save current instance; Restore later
  set oldCurInst [current_bd_instance .]

  # Set parent object as current
  current_bd_instance $parentObj

  # Create cell and set as current instance
  set hier_obj [create_bd_cell -type hier $nameHier]
  current_bd_instance $hier_obj

  # Create interface pins
  create_bd_intf_pin -mode Master -vlnv xilinx.com:interface:axis_rtl:1.0 M_AXIS
  create_bd_intf_pin -mode Master -vlnv xilinx.com:interface:aximm_rtl:1.0 M_AXI_S2MM
  create_bd_intf_pin -mode Slave -vlnv xilinx.com:interface:aximm_rtl:1.0 S_AXI
  create_bd_intf_pin -mode Slave -vlnv xilinx.com:interface:axis_rtl:1.0 S_AXIS_DATA

  # Create pins
  create_bd_pin -dir I -type clk CLK
  create_bd_pin -dir I -from 0 -to 0 -type rst aresetn

  # Create instance: axi_interconnect_0, and set properties
  set axi_interconnect_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:axi_interconnect:2.1 axi_interconnect_0 ]
  set_property -dict [ list \
   CONFIG.NUM_MI {4} \
   CONFIG.SYNCHRONIZATION_STAGES {2} \
 ] $axi_interconnect_0

  # Create instance: axis_data_fifo_0, and set properties
  set axis_data_fifo_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:axis_data_fifo:1.1 axis_data_fifo_0 ]
  set_property -dict [ list \
   CONFIG.HAS_TLAST {1} \
   CONFIG.TDATA_NUM_BYTES {4} \
 ] $axis_data_fifo_0

  # Create instance: axis_dwidth_converter_0, and set properties
  set axis_dwidth_converter_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:axis_dwidth_converter:1.1 axis_dwidth_converter_0 ]
  set_property -dict [ list \
   CONFIG.HAS_TLAST {1} \
   CONFIG.M_TDATA_NUM_BYTES {4} \
 ] $axis_dwidth_converter_0

  # Create instance: axis_dwidth_converter_1, and set properties
  set axis_dwidth_converter_1 [ create_bd_cell -type ip -vlnv xilinx.com:ip:axis_dwidth_converter:1.1 axis_dwidth_converter_1 ]
  set_property -dict [ list \
   CONFIG.HAS_TKEEP {1} \
   CONFIG.HAS_TLAST {1} \
   CONFIG.M_TDATA_NUM_BYTES {4} \
 ] $axis_dwidth_converter_1

  # Create instance: axis_register_slice_0, and set properties
  set axis_register_slice_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:axis_register_slice:1.1 axis_register_slice_0 ]
  set_property -dict [ list \
   CONFIG.HAS_TREADY {0} \
   CONFIG.TDATA_NUM_BYTES {2} \
 ] $axis_register_slice_0

  # Create instance: axis_register_slice_1, and set properties
  set axis_register_slice_1 [ create_bd_cell -type ip -vlnv xilinx.com:ip:axis_register_slice:1.1 axis_register_slice_1 ]
  set_property -dict [ list \
   CONFIG.HAS_TLAST {1} \
   CONFIG.HAS_TREADY {0} \
   CONFIG.TDATA_NUM_BYTES {8} \
 ] $axis_register_slice_1

  # Create instance: cic_compiler_x, and set properties
  set cic_compiler_x [ create_bd_cell -type ip -vlnv xilinx.com:ip:cic_compiler:4.0 cic_compiler_x ]
  set_property -dict [ list \
   CONFIG.Clock_Frequency {100.00} \
   CONFIG.Differential_Delay {2} \
   CONFIG.Filter_Type {Decimation} \
   CONFIG.Fixed_Or_Initial_Rate {10} \
   CONFIG.HAS_ARESETN {true} \
   CONFIG.HAS_DOUT_TREADY {false} \
   CONFIG.Input_Data_Width {16} \
   CONFIG.Input_Sample_Frequency {100.00} \
   CONFIG.Maximum_Rate {8192} \
   CONFIG.Minimum_Rate {10} \
   CONFIG.Number_Of_Channels {1} \
   CONFIG.Number_Of_Stages {4} \
   CONFIG.Output_Data_Width {72} \
   CONFIG.Quantization {Full_Precision} \
   CONFIG.RateSpecification {Frequency_Specification} \
   CONFIG.SamplePeriod {1} \
   CONFIG.Sample_Rate_Changes {Programmable} \
 ] $cic_compiler_x

  # Create instance: cic_compiler_y, and set properties
  set cic_compiler_y [ create_bd_cell -type ip -vlnv xilinx.com:ip:cic_compiler:4.0 cic_compiler_y ]
  set_property -dict [ list \
   CONFIG.Clock_Frequency {100.00} \
   CONFIG.Differential_Delay {2} \
   CONFIG.Filter_Type {Decimation} \
   CONFIG.Fixed_Or_Initial_Rate {10} \
   CONFIG.HAS_ARESETN {true} \
   CONFIG.HAS_DOUT_TREADY {false} \
   CONFIG.Input_Data_Width {16} \
   CONFIG.Input_Sample_Frequency {100.00} \
   CONFIG.Maximum_Rate {8192} \
   CONFIG.Minimum_Rate {10} \
   CONFIG.Number_Of_Channels {1} \
   CONFIG.Number_Of_Stages {4} \
   CONFIG.Output_Data_Width {72} \
   CONFIG.Quantization {Full_Precision} \
   CONFIG.RateSpecification {Frequency_Specification} \
   CONFIG.SamplePeriod {1} \
   CONFIG.Sample_Rate_Changes {Programmable} \
 ] $cic_compiler_y

  # Create instance: dds_compiler_0, and set properties
  set dds_compiler_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:dds_compiler:6.0 dds_compiler_0 ]
  set_property -dict [ list \
   CONFIG.Amplitude_Mode {Full_Range} \
   CONFIG.Has_ACLKEN {false} \
   CONFIG.Has_ARESETn {true} \
   CONFIG.Has_Phase_Out {false} \
   CONFIG.Has_TREADY {false} \
   CONFIG.Latency {9} \
   CONFIG.Latency_Configuration {Auto} \
   CONFIG.Negative_Sine {true} \
   CONFIG.Noise_Shaping {Taylor_Series_Corrected} \
   CONFIG.Output_Frequency1 {0} \
   CONFIG.Output_Width {16} \
   CONFIG.PINC1 {0} \
   CONFIG.Parameter_Entry {Hardware_Parameters} \
   CONFIG.Phase_Increment {Streaming} \
   CONFIG.Phase_Width {32} \
   CONFIG.Phase_offset {Streaming} \
   CONFIG.S_PHASE_Has_TUSER {Not_Required} \
 ] $dds_compiler_0

  # Create instance: dds_tvalid_0, and set properties
  set dds_tvalid_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 dds_tvalid_0 ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {0} \
   CONFIG.DIN_TO {0} \
 ] $dds_tvalid_0

  # Create instance: dec_15_0, and set properties
  set dec_15_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 dec_15_0 ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {15} \
   CONFIG.DOUT_WIDTH {16} \
 ] $dec_15_0

  # Create instance: dec_tvalid_4, and set properties
  set dec_tvalid_4 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 dec_tvalid_4 ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {4} \
   CONFIG.DIN_TO {4} \
 ] $dec_tvalid_4

  # Create instance: dma_con, and set properties
  set dma_con [ create_bd_cell -type ip -vlnv xilinx.com:ip:axi_dma:7.1 dma_con ]
  set_property -dict [ list \
   CONFIG.c_include_mm2s {0} \
   CONFIG.c_include_sg {0} \
   CONFIG.c_s2mm_burst_size {64} \
   CONFIG.c_sg_include_stscntrl_strm {0} \
   CONFIG.c_sg_length_width {23} \
 ] $dma_con

  # Create instance: gpio_DDC_control, and set properties
  set gpio_DDC_control [ create_bd_cell -type ip -vlnv xilinx.com:ip:axi_gpio:2.0 gpio_DDC_control ]
  set_property -dict [ list \
   CONFIG.C_ALL_OUTPUTS {0} \
   CONFIG.C_IS_DUAL {1} \
 ] $gpio_DDC_control

  # Create instance: gpio_DDC_fifo, and set properties
  set gpio_DDC_fifo [ create_bd_cell -type ip -vlnv xilinx.com:ip:axi_gpio:2.0 gpio_DDC_fifo ]
  set_property -dict [ list \
   CONFIG.C_ALL_OUTPUTS {0} \
   CONFIG.C_IS_DUAL {1} \
 ] $gpio_DDC_fifo

  # Create instance: gpio_DDS, and set properties
  set gpio_DDS [ create_bd_cell -type ip -vlnv xilinx.com:ip:axi_gpio:2.0 gpio_DDS ]
  set_property -dict [ list \
   CONFIG.C_ALL_OUTPUTS {0} \
   CONFIG.C_ALL_OUTPUTS_2 {0} \
   CONFIG.C_IS_DUAL {1} \
 ] $gpio_DDS

  # Create instance: mult_gen_x, and set properties
  set mult_gen_x [ create_bd_cell -type ip -vlnv xilinx.com:ip:mult_gen:12.0 mult_gen_x ]
  set_property -dict [ list \
   CONFIG.Multiplier_Construction {Use_Mults} \
   CONFIG.OptGoal {Speed} \
   CONFIG.OutputWidthHigh {31} \
   CONFIG.OutputWidthLow {16} \
   CONFIG.PipeStages {0} \
   CONFIG.PortAType {Signed} \
   CONFIG.PortAWidth {16} \
   CONFIG.PortBType {Signed} \
   CONFIG.PortBWidth {16} \
   CONFIG.RoundPoint {16} \
   CONFIG.UseRounding {true} \
   CONFIG.Use_Custom_Output_Width {true} \
 ] $mult_gen_x

  # Create instance: mult_gen_y, and set properties
  set mult_gen_y [ create_bd_cell -type ip -vlnv xilinx.com:ip:mult_gen:12.0 mult_gen_y ]
  set_property -dict [ list \
   CONFIG.Multiplier_Construction {Use_Mults} \
   CONFIG.OutputWidthHigh {31} \
   CONFIG.OutputWidthLow {16} \
   CONFIG.PipeStages {0} \
   CONFIG.PortAType {Signed} \
   CONFIG.PortAWidth {16} \
   CONFIG.PortBType {Signed} \
   CONFIG.PortBWidth {16} \
   CONFIG.RoundPoint {16} \
   CONFIG.UseRounding {true} \
   CONFIG.Use_Custom_Output_Width {true} \
 ] $mult_gen_y

  # Create instance: myip_shifter_x, and set properties
  set myip_shifter_x [ create_bd_cell -type ip -vlnv BSL.local:user:myip_shifter:1.12 myip_shifter_x ]

  set_property -dict [ list \
   CONFIG.TDATA_NUM_BYTES {4} \
 ] [get_bd_intf_pins /ddc/myip_shifter_x/m_axis_data]

  set_property -dict [ list \
   CONFIG.TDATA_NUM_BYTES {1} \
 ] [get_bd_intf_pins /ddc/myip_shifter_x/s_axis_config]

  set_property -dict [ list \
   CONFIG.TDATA_NUM_BYTES {9} \
 ] [get_bd_intf_pins /ddc/myip_shifter_x/s_axis_data]

  # Create instance: myip_shifter_y, and set properties
  set myip_shifter_y [ create_bd_cell -type ip -vlnv BSL.local:user:myip_shifter:1.12 myip_shifter_y ]

  set_property -dict [ list \
   CONFIG.TDATA_NUM_BYTES {4} \
 ] [get_bd_intf_pins /ddc/myip_shifter_y/m_axis_data]

  set_property -dict [ list \
   CONFIG.TDATA_NUM_BYTES {1} \
 ] [get_bd_intf_pins /ddc/myip_shifter_y/s_axis_config]

  set_property -dict [ list \
   CONFIG.TDATA_NUM_BYTES {9} \
 ] [get_bd_intf_pins /ddc/myip_shifter_y/s_axis_data]

  # Create instance: not_reset, and set properties
  set not_reset [ create_bd_cell -type ip -vlnv xilinx.com:ip:util_vector_logic:2.0 not_reset ]
  set_property -dict [ list \
   CONFIG.C_OPERATION {not} \
   CONFIG.C_SIZE {1} \
   CONFIG.LOGO_FILE {data/sym_notgate.png} \
 ] $not_reset

  # Create instance: not_reset1, and set properties
  set not_reset1 [ create_bd_cell -type ip -vlnv xilinx.com:ip:util_vector_logic:2.0 not_reset1 ]
  set_property -dict [ list \
   CONFIG.C_OPERATION {not} \
   CONFIG.C_SIZE {1} \
   CONFIG.LOGO_FILE {data/sym_notgate.png} \
 ] $not_reset1

  # Create instance: reset_cic_6, and set properties
  set reset_cic_6 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 reset_cic_6 ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {6} \
   CONFIG.DIN_TO {6} \
 ] $reset_cic_6

  # Create instance: reset_dds_1, and set properties
  set reset_dds_1 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 reset_dds_1 ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {1} \
   CONFIG.DIN_TO {1} \
 ] $reset_dds_1

  # Create instance: send_resetFIFO_1, and set properties
  set send_resetFIFO_1 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 send_resetFIFO_1 ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {0} \
   CONFIG.DIN_TO {0} \
 ] $send_resetFIFO_1

  # Create instance: send_tlast_8, and set properties
  set send_tlast_8 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 send_tlast_8 ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {8} \
   CONFIG.DIN_TO {8} \
 ] $send_tlast_8

  # Create instance: shift_23_16, and set properties
  set shift_23_16 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 shift_23_16 ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {23} \
   CONFIG.DIN_TO {16} \
   CONFIG.DOUT_WIDTH {8} \
 ] $shift_23_16

  # Create instance: shift_tvalid_5, and set properties
  set shift_tvalid_5 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 shift_tvalid_5 ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {5} \
   CONFIG.DIN_TO {5} \
 ] $shift_tvalid_5

  # Create instance: util_vector_and, and set properties
  set util_vector_and [ create_bd_cell -type ip -vlnv xilinx.com:ip:util_vector_logic:2.0 util_vector_and ]
  set_property -dict [ list \
   CONFIG.C_OPERATION {and} \
   CONFIG.C_SIZE {1} \
 ] $util_vector_and

  # Create instance: util_vector_not, and set properties
  set util_vector_not [ create_bd_cell -type ip -vlnv xilinx.com:ip:util_vector_logic:2.0 util_vector_not ]
  set_property -dict [ list \
   CONFIG.C_OPERATION {not} \
   CONFIG.C_SIZE {1} \
   CONFIG.LOGO_FILE {data/sym_notgate.png} \
 ] $util_vector_not

  # Create instance: xlconcat_0, and set properties
  set xlconcat_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlconcat:2.1 xlconcat_0 ]
  set_property -dict [ list \
   CONFIG.IN0_WIDTH {32} \
   CONFIG.IN1_WIDTH {32} \
 ] $xlconcat_0

  # Create instance: xlconcat_1, and set properties
  set xlconcat_1 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlconcat:2.1 xlconcat_1 ]
  set_property -dict [ list \
   CONFIG.IN0_WIDTH {32} \
   CONFIG.IN1_WIDTH {32} \
 ] $xlconcat_1

  # Create instance: xlconstant_0, and set properties
  set xlconstant_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlconstant:1.1 xlconstant_0 ]

  # Create instance: xlslice_cos_15_0, and set properties
  set xlslice_cos_15_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 xlslice_cos_15_0 ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {15} \
   CONFIG.DOUT_WIDTH {16} \
 ] $xlslice_cos_15_0

  # Create instance: xlslice_sin_32_16, and set properties
  set xlslice_sin_32_16 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 xlslice_sin_32_16 ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {31} \
   CONFIG.DIN_TO {16} \
   CONFIG.DOUT_WIDTH {16} \
 ] $xlslice_sin_32_16

  # Create interface connections
  connect_bd_intf_net -intf_net Conn1 [get_bd_intf_pins M_AXIS] [get_bd_intf_pins axis_data_fifo_0/M_AXIS]
  connect_bd_intf_net -intf_net S00_AXI_1 [get_bd_intf_pins S_AXI] [get_bd_intf_pins axi_interconnect_0/S00_AXI]
  connect_bd_intf_net -intf_net S_AXIS_1 [get_bd_intf_pins S_AXIS_DATA] [get_bd_intf_pins axis_register_slice_0/S_AXIS]
  connect_bd_intf_net -intf_net axi_dma_0_M_AXI_S2MM [get_bd_intf_pins M_AXI_S2MM] [get_bd_intf_pins dma_con/M_AXI_S2MM]
  connect_bd_intf_net -intf_net axi_interconnect_0_M00_AXI [get_bd_intf_pins axi_interconnect_0/M00_AXI] [get_bd_intf_pins gpio_DDS/S_AXI]
  connect_bd_intf_net -intf_net axi_interconnect_0_M01_AXI [get_bd_intf_pins axi_interconnect_0/M01_AXI] [get_bd_intf_pins gpio_DDC_control/S_AXI]
  connect_bd_intf_net -intf_net axi_interconnect_0_M02_AXI [get_bd_intf_pins axi_interconnect_0/M02_AXI] [get_bd_intf_pins dma_con/S_AXI_LITE]
  connect_bd_intf_net -intf_net axi_interconnect_0_M03_AXI [get_bd_intf_pins axi_interconnect_0/M03_AXI] [get_bd_intf_pins gpio_DDC_fifo/S_AXI]
  connect_bd_intf_net -intf_net axis_dwidth_converter_0_M_AXIS [get_bd_intf_pins axis_data_fifo_0/S_AXIS] [get_bd_intf_pins axis_dwidth_converter_0/M_AXIS]
  connect_bd_intf_net -intf_net axis_dwidth_converter_1_M_AXIS [get_bd_intf_pins axis_dwidth_converter_1/M_AXIS] [get_bd_intf_pins dma_con/S_AXIS_S2MM]
  connect_bd_intf_net -intf_net cic_compiler_x_M_AXIS_DATA [get_bd_intf_pins cic_compiler_x/M_AXIS_DATA] [get_bd_intf_pins myip_shifter_x/s_axis_data]
  set_property -dict [ list \
HDL_ATTRIBUTE.MARK_DEBUG {true} \
 ] [get_bd_intf_nets cic_compiler_x_M_AXIS_DATA]
  connect_bd_intf_net -intf_net cic_compiler_y_M_AXIS_DATA [get_bd_intf_pins cic_compiler_y/M_AXIS_DATA] [get_bd_intf_pins myip_shifter_y/s_axis_data]

  # Create port connections
  connect_bd_net -net CLK_1 [get_bd_pins CLK] [get_bd_pins axi_interconnect_0/ACLK] [get_bd_pins axi_interconnect_0/M00_ACLK] [get_bd_pins axi_interconnect_0/M01_ACLK] [get_bd_pins axi_interconnect_0/M02_ACLK] [get_bd_pins axi_interconnect_0/M03_ACLK] [get_bd_pins axi_interconnect_0/S00_ACLK] [get_bd_pins axis_data_fifo_0/s_axis_aclk] [get_bd_pins axis_dwidth_converter_0/aclk] [get_bd_pins axis_dwidth_converter_1/aclk] [get_bd_pins axis_register_slice_0/aclk] [get_bd_pins axis_register_slice_1/aclk] [get_bd_pins cic_compiler_x/aclk] [get_bd_pins cic_compiler_y/aclk] [get_bd_pins dds_compiler_0/aclk] [get_bd_pins dma_con/m_axi_s2mm_aclk] [get_bd_pins dma_con/s_axi_lite_aclk] [get_bd_pins gpio_DDC_control/s_axi_aclk] [get_bd_pins gpio_DDC_fifo/s_axi_aclk] [get_bd_pins gpio_DDS/s_axi_aclk] [get_bd_pins myip_shifter_x/aclk] [get_bd_pins myip_shifter_y/aclk]
  connect_bd_net -net aresetn_1 [get_bd_pins aresetn] [get_bd_pins axi_interconnect_0/ARESETN] [get_bd_pins axi_interconnect_0/M00_ARESETN] [get_bd_pins axi_interconnect_0/M01_ARESETN] [get_bd_pins axi_interconnect_0/M02_ARESETN] [get_bd_pins axi_interconnect_0/M03_ARESETN] [get_bd_pins axi_interconnect_0/S00_ARESETN] [get_bd_pins axis_dwidth_converter_0/aresetn] [get_bd_pins axis_dwidth_converter_1/aresetn] [get_bd_pins axis_register_slice_0/aresetn] [get_bd_pins axis_register_slice_1/aresetn] [get_bd_pins dma_con/axi_resetn] [get_bd_pins gpio_DDC_control/s_axi_aresetn] [get_bd_pins gpio_DDC_fifo/s_axi_aresetn] [get_bd_pins gpio_DDS/s_axi_aresetn] [get_bd_pins util_vector_and/Op1]
  connect_bd_net -net axis_data_fifo_0_axis_data_count [get_bd_pins axis_data_fifo_0/axis_data_count] [get_bd_pins gpio_DDC_fifo/gpio2_io_i]
  connect_bd_net -net axis_register_slice_0_m_axis_tdata [get_bd_pins axis_register_slice_0/m_axis_tdata] [get_bd_pins mult_gen_x/A] [get_bd_pins mult_gen_y/A]
  set_property -dict [ list \
HDL_ATTRIBUTE.MARK_DEBUG {true} \
 ] [get_bd_nets axis_register_slice_0_m_axis_tdata]
  connect_bd_net -net axis_register_slice_0_m_axis_tvalid [get_bd_pins axis_register_slice_0/m_axis_tvalid] [get_bd_pins cic_compiler_x/s_axis_data_tvalid] [get_bd_pins cic_compiler_y/s_axis_data_tvalid]
  set_property -dict [ list \
HDL_ATTRIBUTE.MARK_DEBUG {true} \
 ] [get_bd_nets axis_register_slice_0_m_axis_tvalid]
  connect_bd_net -net axis_register_slice_1_m_axis_tdata [get_bd_pins axis_dwidth_converter_0/s_axis_tdata] [get_bd_pins axis_dwidth_converter_1/s_axis_tdata] [get_bd_pins axis_register_slice_1/m_axis_tdata]
  connect_bd_net -net axis_register_slice_1_m_axis_tlast [get_bd_pins axis_dwidth_converter_0/s_axis_tlast] [get_bd_pins axis_dwidth_converter_1/s_axis_tlast] [get_bd_pins axis_register_slice_1/m_axis_tlast]
  connect_bd_net -net axis_register_slice_1_m_axis_tvalid [get_bd_pins axis_dwidth_converter_0/s_axis_tvalid] [get_bd_pins axis_dwidth_converter_1/s_axis_tvalid] [get_bd_pins axis_register_slice_1/m_axis_tvalid]
  connect_bd_net -net dds_compiler_0_m_axis_data_tdata [get_bd_pins dds_compiler_0/m_axis_data_tdata] [get_bd_pins xlslice_cos_15_0/Din] [get_bd_pins xlslice_sin_32_16/Din]
  connect_bd_net -net dds_tvalid_0_Dout [get_bd_pins dds_compiler_0/s_axis_phase_tvalid] [get_bd_pins dds_tvalid_0/Dout]
  connect_bd_net -net dec_15_0_Dout [get_bd_pins cic_compiler_x/s_axis_config_tdata] [get_bd_pins cic_compiler_y/s_axis_config_tdata] [get_bd_pins dec_15_0/Dout]
  connect_bd_net -net dec_tvalid_24_Dout [get_bd_pins cic_compiler_x/s_axis_config_tvalid] [get_bd_pins cic_compiler_y/s_axis_config_tvalid] [get_bd_pins dec_tvalid_4/Dout]
  connect_bd_net -net gpio_DDC_control_gpio2_io_o [get_bd_pins dds_tvalid_0/Din] [get_bd_pins dec_tvalid_4/Din] [get_bd_pins gpio_DDC_control/gpio2_io_i] [get_bd_pins gpio_DDC_control/gpio2_io_o] [get_bd_pins reset_cic_6/Din] [get_bd_pins reset_dds_1/Din] [get_bd_pins send_tlast_8/Din] [get_bd_pins shift_tvalid_5/Din]
  connect_bd_net -net gpio_DDC_control_gpio_io_o [get_bd_pins dec_15_0/Din] [get_bd_pins gpio_DDC_control/gpio_io_i] [get_bd_pins gpio_DDC_control/gpio_io_o] [get_bd_pins shift_23_16/Din]
  connect_bd_net -net gpio_DDC_fifo_gpio_io_o [get_bd_pins gpio_DDC_fifo/gpio_io_i] [get_bd_pins gpio_DDC_fifo/gpio_io_o] [get_bd_pins send_resetFIFO_1/Din]
  connect_bd_net -net gpio_DDS_gpio2_io_o [get_bd_pins gpio_DDS/gpio2_io_i] [get_bd_pins gpio_DDS/gpio2_io_o] [get_bd_pins xlconcat_0/In1]
  connect_bd_net -net gpio_DDS_gpio_io_o [get_bd_pins gpio_DDS/gpio_io_i] [get_bd_pins gpio_DDS/gpio_io_o] [get_bd_pins xlconcat_0/In0]
  connect_bd_net -net mult_gen_0_P [get_bd_pins cic_compiler_x/s_axis_data_tdata] [get_bd_pins mult_gen_x/P]
  set_property -dict [ list \
HDL_ATTRIBUTE.MARK_DEBUG {true} \
 ] [get_bd_nets mult_gen_0_P]
  connect_bd_net -net mult_gen_1_P [get_bd_pins cic_compiler_y/s_axis_data_tdata] [get_bd_pins mult_gen_y/P]
  connect_bd_net -net myip_shifter_x_m_axis_data_tdata [get_bd_pins myip_shifter_x/m_axis_data_tdata] [get_bd_pins xlconcat_1/In0]
  set_property -dict [ list \
HDL_ATTRIBUTE.MARK_DEBUG {true} \
 ] [get_bd_nets myip_shifter_x_m_axis_data_tdata]
  connect_bd_net -net myip_shifter_x_m_axis_data_tvalid [get_bd_pins axis_register_slice_1/s_axis_tvalid] [get_bd_pins myip_shifter_x/m_axis_data_tvalid]
  set_property -dict [ list \
HDL_ATTRIBUTE.MARK_DEBUG {true} \
 ] [get_bd_nets myip_shifter_x_m_axis_data_tvalid]
  connect_bd_net -net myip_shifter_y_m_axis_data_tdata [get_bd_pins myip_shifter_y/m_axis_data_tdata] [get_bd_pins xlconcat_1/In1]
  connect_bd_net -net not_reset_Res [get_bd_pins dds_compiler_0/aresetn] [get_bd_pins not_reset/Res]
  connect_bd_net -net reset_cic_26_Dout [get_bd_pins cic_compiler_x/aresetn] [get_bd_pins cic_compiler_y/aresetn] [get_bd_pins myip_shifter_x/aresetn] [get_bd_pins myip_shifter_y/aresetn] [get_bd_pins not_reset1/Res]
  connect_bd_net -net reset_cic_26_Dout1 [get_bd_pins not_reset1/Op1] [get_bd_pins reset_cic_6/Dout]
  connect_bd_net -net reset_dds_29_Dout [get_bd_pins not_reset/Op1] [get_bd_pins reset_dds_1/Dout]
  connect_bd_net -net send_resetFIFO_12_Dout [get_bd_pins send_resetFIFO_1/Dout] [get_bd_pins util_vector_not/Op1]
  connect_bd_net -net sendendofpacket_27_Dout [get_bd_pins axis_register_slice_1/s_axis_tlast] [get_bd_pins send_tlast_8/Dout]
  connect_bd_net -net shift_23_16_Dout [get_bd_pins myip_shifter_x/s_axis_config_tdata] [get_bd_pins myip_shifter_y/s_axis_config_tdata] [get_bd_pins shift_23_16/Dout]
  connect_bd_net -net shift_tvalid_25_Dout [get_bd_pins myip_shifter_x/s_axis_config_tvalid] [get_bd_pins myip_shifter_y/s_axis_config_tvalid] [get_bd_pins shift_tvalid_5/Dout]
  connect_bd_net -net util_vector_and_Res [get_bd_pins axis_data_fifo_0/s_axis_aresetn] [get_bd_pins util_vector_and/Res]
  connect_bd_net -net util_vector_not_Res [get_bd_pins util_vector_and/Op2] [get_bd_pins util_vector_not/Res]
  connect_bd_net -net xlconcat_0_dout [get_bd_pins dds_compiler_0/s_axis_phase_tdata] [get_bd_pins xlconcat_0/dout]
  connect_bd_net -net xlconcat_1_dout [get_bd_pins axis_register_slice_1/s_axis_tdata] [get_bd_pins xlconcat_1/dout]
  connect_bd_net -net xlconstant_0_const [get_bd_pins myip_shifter_x/m_axis_data_tready] [get_bd_pins myip_shifter_y/m_axis_data_tready] [get_bd_pins xlconstant_0/dout]
  connect_bd_net -net xlslice_15_0_Dout [get_bd_pins mult_gen_y/B] [get_bd_pins xlslice_sin_32_16/Dout]
  connect_bd_net -net xlslice_31_16_Dout [get_bd_pins mult_gen_x/B] [get_bd_pins xlslice_cos_15_0/Dout]
  set_property -dict [ list \
HDL_ATTRIBUTE.MARK_DEBUG {true} \
 ] [get_bd_nets xlslice_31_16_Dout]

  # Restore current instance
  current_bd_instance $oldCurInst
}

# Hierarchical cell: TTL
proc create_hier_cell_TTL { parentCell nameHier } {

  variable script_folder

  if { $parentCell eq "" || $nameHier eq "" } {
     catch {common::send_msg_id "BD_TCL-102" "ERROR" "create_hier_cell_TTL() - Empty argument(s)!"}
     return
  }

  # Get object for parentCell
  set parentObj [get_bd_cells $parentCell]
  if { $parentObj == "" } {
     catch {common::send_msg_id "BD_TCL-100" "ERROR" "Unable to find parent cell <$parentCell>!"}
     return
  }

  # Make sure parentObj is hier blk
  set parentType [get_property TYPE $parentObj]
  if { $parentType ne "hier" } {
     catch {common::send_msg_id "BD_TCL-101" "ERROR" "Parent <$parentObj> has TYPE = <$parentType>. Expected to be <hier>."}
     return
  }

  # Save current instance; Restore later
  set oldCurInst [current_bd_instance .]

  # Set parent object as current
  current_bd_instance $parentObj

  # Create cell and set as current instance
  set hier_obj [create_bd_cell -type hier $nameHier]
  current_bd_instance $hier_obj

  # Create interface pins
  create_bd_intf_pin -mode Slave -vlnv xilinx.com:interface:aximm_rtl:1.0 S_AXI

  # Create pins
  create_bd_pin -dir O -from 3 -to 0 ADC
  create_bd_pin -dir O -from 3 -to 0 DDS
  create_bd_pin -dir O -from 7 -to 0 -type data IO
  create_bd_pin -dir O -from 3 -to 0 IO_15_12
  create_bd_pin -dir O -from 0 -to 0 LED_FRONT
  create_bd_pin -dir O -from 0 -to 0 P_0
  create_bd_pin -dir O -from 1 -to 0 P_4_3
  create_bd_pin -dir O -from 0 -to 0 TEMP_GATE
  create_bd_pin -dir I TRIGGER_IN
  create_bd_pin -dir O -from 3 -to 0 TTL
  create_bd_pin -dir I s_axi_aclk
  create_bd_pin -dir I -from 0 -to 0 s_axi_aresetn

  # Create instance: gpio_ttl, and set properties
  set gpio_ttl [ create_bd_cell -type ip -vlnv xilinx.com:ip:axi_gpio:2.0 gpio_ttl ]
  set_property -dict [ list \
   CONFIG.C_ALL_INPUTS_2 {0} \
   CONFIG.C_ALL_OUTPUTS {0} \
   CONFIG.C_ALL_OUTPUTS_2 {0} \
   CONFIG.C_IS_DUAL {0} \
   CONFIG.C_TRI_DEFAULT {0xFFFFFFFB} \
 ] $gpio_ttl

  # Create instance: xlconcat_0, and set properties
  set xlconcat_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlconcat:2.1 xlconcat_0 ]
  set_property -dict [ list \
   CONFIG.IN0_WIDTH {2} \
   CONFIG.IN2_WIDTH {29} \
   CONFIG.NUM_PORTS {3} \
 ] $xlconcat_0

  # Create instance: xlslice_0_P_0, and set properties
  set xlslice_0_P_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 xlslice_0_P_0 ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {0} \
   CONFIG.DOUT_WIDTH {1} \
 ] $xlslice_0_P_0

  # Create instance: xlslice_15_8_IO_7_0, and set properties
  set xlslice_15_8_IO_7_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 xlslice_15_8_IO_7_0 ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {15} \
   CONFIG.DIN_TO {8} \
   CONFIG.DOUT_WIDTH {8} \
 ] $xlslice_15_8_IO_7_0

  # Create instance: xlslice_19_16_generic_3_0, and set properties
  set xlslice_19_16_generic_3_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 xlslice_19_16_generic_3_0 ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {19} \
   CONFIG.DIN_TO {16} \
   CONFIG.DOUT_WIDTH {4} \
 ] $xlslice_19_16_generic_3_0

  # Create instance: xlslice_23_20_generic_3_0, and set properties
  set xlslice_23_20_generic_3_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 xlslice_23_20_generic_3_0 ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {23} \
   CONFIG.DIN_TO {20} \
   CONFIG.DOUT_WIDTH {4} \
 ] $xlslice_23_20_generic_3_0

  # Create instance: xlslice_27_24_generic_3_0, and set properties
  set xlslice_27_24_generic_3_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 xlslice_27_24_generic_3_0 ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {27} \
   CONFIG.DIN_TO {24} \
   CONFIG.DOUT_WIDTH {4} \
 ] $xlslice_27_24_generic_3_0

  # Create instance: xlslice_31_28_IO_15_12, and set properties
  set xlslice_31_28_IO_15_12 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 xlslice_31_28_IO_15_12 ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {31} \
   CONFIG.DIN_TO {28} \
   CONFIG.DOUT_WIDTH {4} \
 ] $xlslice_31_28_IO_15_12

  # Create instance: xlslice_4_3_P_4_3, and set properties
  set xlslice_4_3_P_4_3 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 xlslice_4_3_P_4_3 ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {4} \
   CONFIG.DIN_TO {3} \
   CONFIG.DOUT_WIDTH {2} \
 ] $xlslice_4_3_P_4_3

  # Create instance: xlslice_6_LED_FRONT, and set properties
  set xlslice_6_LED_FRONT [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 xlslice_6_LED_FRONT ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {6} \
   CONFIG.DIN_TO {6} \
   CONFIG.DOUT_WIDTH {1} \
 ] $xlslice_6_LED_FRONT

  # Create instance: xlslice_7_TEMP_GATE, and set properties
  set xlslice_7_TEMP_GATE [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 xlslice_7_TEMP_GATE ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {7} \
   CONFIG.DIN_TO {7} \
   CONFIG.DOUT_WIDTH {1} \
 ] $xlslice_7_TEMP_GATE

  # Create interface connections
  connect_bd_intf_net -intf_net Conn1 [get_bd_intf_pins S_AXI] [get_bd_intf_pins gpio_ttl/S_AXI]

  # Create port connections
  connect_bd_net -net TRIGGER_IN_1 [get_bd_pins TRIGGER_IN] [get_bd_pins xlconcat_0/In1]
  connect_bd_net -net gpio_ttl_gpio_io_o [get_bd_pins gpio_ttl/gpio_io_o] [get_bd_pins xlslice_0_P_0/Din] [get_bd_pins xlslice_15_8_IO_7_0/Din] [get_bd_pins xlslice_19_16_generic_3_0/Din] [get_bd_pins xlslice_23_20_generic_3_0/Din] [get_bd_pins xlslice_27_24_generic_3_0/Din] [get_bd_pins xlslice_31_28_IO_15_12/Din] [get_bd_pins xlslice_4_3_P_4_3/Din] [get_bd_pins xlslice_6_LED_FRONT/Din] [get_bd_pins xlslice_7_TEMP_GATE/Din]
  connect_bd_net -net s_axi_aclk_1 [get_bd_pins s_axi_aclk] [get_bd_pins gpio_ttl/s_axi_aclk]
  connect_bd_net -net s_axi_aresetn_1 [get_bd_pins s_axi_aresetn] [get_bd_pins gpio_ttl/s_axi_aresetn]
  connect_bd_net -net xlconcat_0_dout [get_bd_pins gpio_ttl/gpio_io_i] [get_bd_pins xlconcat_0/dout]
  connect_bd_net -net xlslice_0_P_0_Dout [get_bd_pins P_0] [get_bd_pins xlslice_0_P_0/Dout]
  connect_bd_net -net xlslice_15_8_IO_7_0_Dout [get_bd_pins IO] [get_bd_pins xlslice_15_8_IO_7_0/Dout]
  connect_bd_net -net xlslice_19_16_generic_4_0_Dout [get_bd_pins ADC] [get_bd_pins xlslice_19_16_generic_3_0/Dout]
  connect_bd_net -net xlslice_23_20_generic_4_0_Dout [get_bd_pins DDS] [get_bd_pins xlslice_23_20_generic_3_0/Dout]
  connect_bd_net -net xlslice_27_24_generic_3_0_Dout [get_bd_pins TTL] [get_bd_pins xlslice_27_24_generic_3_0/Dout]
  connect_bd_net -net xlslice_31_28_generic_3_1_Dout [get_bd_pins IO_15_12] [get_bd_pins xlslice_31_28_IO_15_12/Dout]
  connect_bd_net -net xlslice_4_3_P_4_3_Dout [get_bd_pins P_4_3] [get_bd_pins xlslice_4_3_P_4_3/Dout]
  connect_bd_net -net xlslice_6_LED_FRONT_Dout [get_bd_pins LED_FRONT] [get_bd_pins xlslice_6_LED_FRONT/Dout]
  connect_bd_net -net xlslice_7_TEMP_GATE_Dout [get_bd_pins TEMP_GATE] [get_bd_pins xlslice_7_TEMP_GATE/Dout]

  # Restore current instance
  current_bd_instance $oldCurInst
}

# Hierarchical cell: DDS_AD9951
proc create_hier_cell_DDS_AD9951 { parentCell nameHier } {

  variable script_folder

  if { $parentCell eq "" || $nameHier eq "" } {
     catch {common::send_msg_id "BD_TCL-102" "ERROR" "create_hier_cell_DDS_AD9951() - Empty argument(s)!"}
     return
  }

  # Get object for parentCell
  set parentObj [get_bd_cells $parentCell]
  if { $parentObj == "" } {
     catch {common::send_msg_id "BD_TCL-100" "ERROR" "Unable to find parent cell <$parentCell>!"}
     return
  }

  # Make sure parentObj is hier blk
  set parentType [get_property TYPE $parentObj]
  if { $parentType ne "hier" } {
     catch {common::send_msg_id "BD_TCL-101" "ERROR" "Parent <$parentObj> has TYPE = <$parentType>. Expected to be <hier>."}
     return
  }

  # Save current instance; Restore later
  set oldCurInst [current_bd_instance .]

  # Set parent object as current
  current_bd_instance $parentObj

  # Create cell and set as current instance
  set hier_obj [create_bd_cell -type hier $nameHier]
  current_bd_instance $hier_obj

  # Create interface pins
  create_bd_intf_pin -mode Slave -vlnv xilinx.com:interface:aximm_rtl:1.0 S00_AXI

  # Create pins
  create_bd_pin -dir I -type clk ACLK
  create_bd_pin -dir I -from 0 -to 0 -type rst ARESETN
  create_bd_pin -dir O -from 0 -to 0 DDS_CLKEN
  create_bd_pin -dir O -from 0 -to 0 DDS_IO_UPDATE
  create_bd_pin -dir O -from 0 -to 0 DDS_PWRD
  create_bd_pin -dir O -from 0 -to 0 DDS_RESET
  create_bd_pin -dir O DDS_SCLK
  create_bd_pin -dir O DDS_SDIO
  create_bd_pin -dir I DDS_SDO
  create_bd_pin -dir O -from 0 -to 0 DDS_SWT_EN
  create_bd_pin -dir O -from 0 -to 0 DDS_SYNC
  create_bd_pin -dir I -from 3 -to 0 DDS_TTL
  create_bd_pin -dir I -type clk P_CLK
  create_bd_pin -dir O -type intr ip2intc_irpt

  # Create instance: axi_interconnect_0, and set properties
  set axi_interconnect_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:axi_interconnect:2.1 axi_interconnect_0 ]
  set_property -dict [ list \
   CONFIG.ENABLE_ADVANCED_OPTIONS {0} \
   CONFIG.SYNCHRONIZATION_STAGES {2} \
 ] $axi_interconnect_0

  # Create instance: c_counter_binary_divby4, and set properties
  set c_counter_binary_divby4 [ create_bd_cell -type ip -vlnv xilinx.com:ip:c_counter_binary:12.0 c_counter_binary_divby4 ]
  set_property -dict [ list \
   CONFIG.CE {false} \
   CONFIG.Output_Width {2} \
   CONFIG.SCLR {true} \
 ] $c_counter_binary_divby4

  # Create instance: dds_outputs, and set properties
  set dds_outputs [ create_bd_cell -type ip -vlnv xilinx.com:ip:axi_gpio:2.0 dds_outputs ]
  set_property -dict [ list \
   CONFIG.C_ALL_OUTPUTS {1} \
   CONFIG.C_GPIO_WIDTH {5} \
   CONFIG.C_IS_DUAL {0} \
 ] $dds_outputs

  # Create instance: dds_spi, and set properties
  set dds_spi [ create_bd_cell -type ip -vlnv xilinx.com:ip:axi_quad_spi:3.2 dds_spi ]
  set_property -dict [ list \
   CONFIG.C_FAMILY {virtex7} \
   CONFIG.C_SCK_RATIO {4} \
   CONFIG.C_SUB_FAMILY {virtex7} \
   CONFIG.C_USE_STARTUP {0} \
   CONFIG.C_USE_STARTUP_INT {0} \
 ] $dds_spi

  # Create instance: proc_sys_reset_0, and set properties
  set proc_sys_reset_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:proc_sys_reset:5.0 proc_sys_reset_0 ]

  # Create instance: pulse_gen_0
  create_hier_cell_pulse_gen_0 $hier_obj pulse_gen_0

  # Create instance: pulse_gen_1
  create_hier_cell_pulse_gen_1 $hier_obj pulse_gen_1

  # Create instance: util_or_swt_en, and set properties
  set util_or_swt_en [ create_bd_cell -type ip -vlnv xilinx.com:ip:util_vector_logic:2.0 util_or_swt_en ]
  set_property -dict [ list \
   CONFIG.C_OPERATION {or} \
   CONFIG.C_SIZE {1} \
   CONFIG.LOGO_FILE {data/sym_orgate.png} \
 ] $util_or_swt_en

  # Create instance: util_vector_logic_or_ioupdate, and set properties
  set util_vector_logic_or_ioupdate [ create_bd_cell -type ip -vlnv xilinx.com:ip:util_vector_logic:2.0 util_vector_logic_or_ioupdate ]
  set_property -dict [ list \
   CONFIG.C_OPERATION {or} \
   CONFIG.C_SIZE {1} \
   CONFIG.LOGO_FILE {data/sym_orgate.png} \
 ] $util_vector_logic_or_ioupdate

  # Create instance: xlslice_b0_ioupdate, and set properties
  set xlslice_b0_ioupdate [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 xlslice_b0_ioupdate ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {1} \
   CONFIG.DIN_TO {1} \
   CONFIG.DIN_WIDTH {4} \
 ] $xlslice_b0_ioupdate

  # Create instance: xlslice_b0_swtEn, and set properties
  set xlslice_b0_swtEn [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 xlslice_b0_swtEn ]
  set_property -dict [ list \
   CONFIG.DIN_WIDTH {4} \
 ] $xlslice_b0_swtEn

  # Create instance: xlslice_b0_swt_en, and set properties
  set xlslice_b0_swt_en [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 xlslice_b0_swt_en ]
  set_property -dict [ list \
   CONFIG.DIN_WIDTH {5} \
 ] $xlslice_b0_swt_en

  # Create instance: xlslice_b1_ioupdate, and set properties
  set xlslice_b1_ioupdate [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 xlslice_b1_ioupdate ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {1} \
   CONFIG.DIN_TO {1} \
   CONFIG.DIN_WIDTH {5} \
 ] $xlslice_b1_ioupdate

  # Create instance: xlslice_b2_pwrd, and set properties
  set xlslice_b2_pwrd [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 xlslice_b2_pwrd ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {2} \
   CONFIG.DIN_TO {2} \
   CONFIG.DIN_WIDTH {5} \
 ] $xlslice_b2_pwrd

  # Create instance: xlslice_b3_reset, and set properties
  set xlslice_b3_reset [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 xlslice_b3_reset ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {3} \
   CONFIG.DIN_TO {3} \
   CONFIG.DIN_WIDTH {5} \
 ] $xlslice_b3_reset

  # Create instance: xlslice_b4_dds_sync_en, and set properties
  set xlslice_b4_dds_sync_en [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 xlslice_b4_dds_sync_en ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {4} \
   CONFIG.DIN_TO {4} \
   CONFIG.DIN_WIDTH {5} \
 ] $xlslice_b4_dds_sync_en

  # Create instance: xlslice_divby4, and set properties
  set xlslice_divby4 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 xlslice_divby4 ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {1} \
   CONFIG.DIN_TO {1} \
   CONFIG.DIN_WIDTH {2} \
 ] $xlslice_divby4

  # Create interface connections
  connect_bd_intf_net -intf_net S00_AXI_1 [get_bd_intf_pins S00_AXI] [get_bd_intf_pins axi_interconnect_0/S00_AXI]
  connect_bd_intf_net -intf_net axi_interconnect_0_M00_AXI [get_bd_intf_pins axi_interconnect_0/M00_AXI] [get_bd_intf_pins dds_spi/AXI_LITE]
  connect_bd_intf_net -intf_net axi_interconnect_0_M01_AXI [get_bd_intf_pins axi_interconnect_0/M01_AXI] [get_bd_intf_pins dds_outputs/S_AXI]

  # Create port connections
  connect_bd_net -net ACLK_1 [get_bd_pins ACLK] [get_bd_pins axi_interconnect_0/ACLK] [get_bd_pins axi_interconnect_0/S00_ACLK]
  connect_bd_net -net ARESETN_1 [get_bd_pins ARESETN] [get_bd_pins proc_sys_reset_0/ext_reset_in]
  connect_bd_net -net DDS_SDO_1 [get_bd_pins DDS_SDO] [get_bd_pins dds_spi/io1_i]
  connect_bd_net -net Din_1 [get_bd_pins DDS_TTL] [get_bd_pins xlslice_b0_ioupdate/Din] [get_bd_pins xlslice_b0_swtEn/Din]
  connect_bd_net -net Op1_1 [get_bd_pins pulse_gen_1/Op1] [get_bd_pins xlslice_b1_ioupdate/Dout]
  connect_bd_net -net P_CLK_1 [get_bd_pins P_CLK] [get_bd_pins axi_interconnect_0/M00_ACLK] [get_bd_pins axi_interconnect_0/M01_ACLK] [get_bd_pins c_counter_binary_divby4/CLK] [get_bd_pins dds_outputs/s_axi_aclk] [get_bd_pins dds_spi/ext_spi_clk] [get_bd_pins dds_spi/s_axi_aclk] [get_bd_pins proc_sys_reset_0/slowest_sync_clk] [get_bd_pins pulse_gen_0/CLK] [get_bd_pins pulse_gen_1/CLK]
  connect_bd_net -net axi_gpio_0_gpio_io_o [get_bd_pins dds_outputs/gpio_io_o] [get_bd_pins xlslice_b0_swt_en/Din] [get_bd_pins xlslice_b1_ioupdate/Din] [get_bd_pins xlslice_b2_pwrd/Din] [get_bd_pins xlslice_b3_reset/Din] [get_bd_pins xlslice_b4_dds_sync_en/Din]
  connect_bd_net -net axi_quad_spi_dds_ip2intc_irpt [get_bd_pins ip2intc_irpt] [get_bd_pins dds_spi/ip2intc_irpt]
  connect_bd_net -net c_counter_binary_0_Q [get_bd_pins c_counter_binary_divby4/Q] [get_bd_pins xlslice_divby4/Din]
  connect_bd_net -net dds_spi_io0_o [get_bd_pins DDS_SDIO] [get_bd_pins dds_spi/io0_o]
  connect_bd_net -net proc_sys_reset_0_interconnect_aresetn [get_bd_pins axi_interconnect_0/ARESETN] [get_bd_pins axi_interconnect_0/M00_ARESETN] [get_bd_pins axi_interconnect_0/M01_ARESETN] [get_bd_pins axi_interconnect_0/S00_ARESETN] [get_bd_pins dds_outputs/s_axi_aresetn] [get_bd_pins dds_spi/s_axi_aresetn] [get_bd_pins proc_sys_reset_0/interconnect_aresetn]
  connect_bd_net -net pulse_gen_0_Dout [get_bd_pins pulse_gen_0/Dout] [get_bd_pins util_vector_logic_or_ioupdate/Op2]
  connect_bd_net -net pulse_gen_1_Dout [get_bd_pins pulse_gen_1/Dout] [get_bd_pins util_vector_logic_or_ioupdate/Op1]
  connect_bd_net -net spi_dds_sck_o [get_bd_pins DDS_SCLK] [get_bd_pins dds_spi/sck_o]
  connect_bd_net -net spi_dds_ss_o [get_bd_pins DDS_CLKEN] [get_bd_pins dds_spi/ss_o]
  connect_bd_net -net util_or_sync_Res [get_bd_pins DDS_SWT_EN] [get_bd_pins util_or_swt_en/Res]
  connect_bd_net -net util_vector_logic_or_ioupdate_Res [get_bd_pins DDS_IO_UPDATE] [get_bd_pins util_vector_logic_or_ioupdate/Res]
  connect_bd_net -net xlslice_b0_ioupdate_Dout [get_bd_pins pulse_gen_0/Op1] [get_bd_pins xlslice_b0_ioupdate/Dout]
  connect_bd_net -net xlslice_b0_swtEn_Dout [get_bd_pins util_or_swt_en/Op2] [get_bd_pins xlslice_b0_swtEn/Dout]
  connect_bd_net -net xlslice_b0_swt_en_Dout [get_bd_pins util_or_swt_en/Op1] [get_bd_pins xlslice_b0_swt_en/Dout]
  connect_bd_net -net xlslice_b2_pwrd_Dout [get_bd_pins DDS_PWRD] [get_bd_pins xlslice_b2_pwrd/Dout]
  connect_bd_net -net xlslice_b3_reset_Dout [get_bd_pins DDS_RESET] [get_bd_pins xlslice_b3_reset/Dout]
  connect_bd_net -net xlslice_b4_dds_sync_en_Dout [get_bd_pins c_counter_binary_divby4/SCLR] [get_bd_pins xlslice_b4_dds_sync_en/Dout]
  connect_bd_net -net xlslice_divby4_Dout [get_bd_pins DDS_SYNC] [get_bd_pins xlslice_divby4/Dout]

  # Restore current instance
  current_bd_instance $oldCurInst
}

# Hierarchical cell: ADC_LTC2207
proc create_hier_cell_ADC_LTC2207 { parentCell nameHier } {

  variable script_folder

  if { $parentCell eq "" || $nameHier eq "" } {
     catch {common::send_msg_id "BD_TCL-102" "ERROR" "create_hier_cell_ADC_LTC2207() - Empty argument(s)!"}
     return
  }

  # Get object for parentCell
  set parentObj [get_bd_cells $parentCell]
  if { $parentObj == "" } {
     catch {common::send_msg_id "BD_TCL-100" "ERROR" "Unable to find parent cell <$parentCell>!"}
     return
  }

  # Make sure parentObj is hier blk
  set parentType [get_property TYPE $parentObj]
  if { $parentType ne "hier" } {
     catch {common::send_msg_id "BD_TCL-101" "ERROR" "Parent <$parentObj> has TYPE = <$parentType>. Expected to be <hier>."}
     return
  }

  # Save current instance; Restore later
  set oldCurInst [current_bd_instance .]

  # Set parent object as current
  current_bd_instance $parentObj

  # Create cell and set as current instance
  set hier_obj [create_bd_cell -type hier $nameHier]
  current_bd_instance $hier_obj

  # Create interface pins
  create_bd_intf_pin -mode Master -vlnv xilinx.com:interface:axis_rtl:1.0 M_AXIS
  create_bd_intf_pin -mode Slave -vlnv xilinx.com:interface:aximm_rtl:1.0 S_AXI

  # Create pins
  create_bd_pin -dir I ADC_CLKOUT_N
  create_bd_pin -dir I -from 15 -to 0 ADC_DATA
  create_bd_pin -dir O -from 0 -to 0 ADC_DITH
  create_bd_pin -dir I ADC_OF
  create_bd_pin -dir O -from 0 -to 0 ADC_PGA
  create_bd_pin -dir O -from 0 -to 0 ADC_RAND
  create_bd_pin -dir O -from 0 -to 0 ADC_SHDN
  create_bd_pin -dir I -from 3 -to 0 ADC_TTL
  create_bd_pin -dir I -type clk m_axis_aclk
  create_bd_pin -dir I -from 0 -to 0 -type rst m_axis_aresetn
  create_bd_pin -dir I -type clk s_axi_aclk
  create_bd_pin -dir I -from 0 -to 0 -type rst s_axi_aresetn

  # Create instance: axi_gpio_0, and set properties
  set axi_gpio_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:axi_gpio:2.0 axi_gpio_0 ]
  set_property -dict [ list \
   CONFIG.C_ALL_INPUTS {0} \
   CONFIG.C_ALL_INPUTS_2 {1} \
   CONFIG.C_ALL_OUTPUTS {0} \
   CONFIG.C_GPIO_WIDTH {8} \
   CONFIG.C_IS_DUAL {1} \
 ] $axi_gpio_0

  # Create instance: axis_clock_converter_0, and set properties
  set axis_clock_converter_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:axis_clock_converter:1.1 axis_clock_converter_0 ]
  set_property -dict [ list \
   CONFIG.TDATA_NUM_BYTES {2} \
 ] $axis_clock_converter_0

  # Create instance: axis_register_slice_0, and set properties
  set axis_register_slice_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:axis_register_slice:1.1 axis_register_slice_0 ]
  set_property -dict [ list \
   CONFIG.HAS_ACLKEN {0} \
   CONFIG.HAS_TREADY {0} \
   CONFIG.TDATA_NUM_BYTES {2} \
 ] $axis_register_slice_0

  # Create instance: c_counter_binary_0, and set properties
  set c_counter_binary_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:c_counter_binary:12.0 c_counter_binary_0 ]
  set_property -dict [ list \
   CONFIG.CE {true} \
   CONFIG.Load {false} \
   CONFIG.Output_Width {32} \
   CONFIG.SCLR {true} \
 ] $c_counter_binary_0

  # Create instance: selectio_wiz_0, and set properties
  set selectio_wiz_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:selectio_wiz:5.1 selectio_wiz_0 ]
  set_property -dict [ list \
   CONFIG.BUS_IO_STD {LVCMOS33} \
   CONFIG.BUS_SIG_TYPE {SINGLE} \
   CONFIG.CLK_DELAY {NONE} \
   CONFIG.CLK_EN {false} \
   CONFIG.CLK_FWD_IO_STD {LVCMOS33} \
   CONFIG.SELIO_BUS_IN_DELAY {NONE} \
   CONFIG.SELIO_CLK_BUF {BUFIO} \
   CONFIG.SELIO_CLK_IO_STD {LVCMOS33} \
   CONFIG.SYSTEM_DATA_WIDTH {16} \
   CONFIG.USE_SERIALIZATION {false} \
   CONFIG.USE_TEMPLATE {Custom} \
 ] $selectio_wiz_0

  # Create instance: util_vector_b0and, and set properties
  set util_vector_b0and [ create_bd_cell -type ip -vlnv xilinx.com:ip:util_vector_logic:2.0 util_vector_b0and ]
  set_property -dict [ list \
   CONFIG.C_OPERATION {and} \
   CONFIG.C_SIZE {1} \
 ] $util_vector_b0and

  # Create instance: util_vector_logic_0, and set properties
  set util_vector_logic_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:util_vector_logic:2.0 util_vector_logic_0 ]
  set_property -dict [ list \
   CONFIG.C_OPERATION {xor} \
   CONFIG.C_SIZE {15} \
   CONFIG.LOGO_FILE {data/sym_xorgate.png} \
 ] $util_vector_logic_0

  # Create instance: utl_or_run, and set properties
  set utl_or_run [ create_bd_cell -type ip -vlnv xilinx.com:ip:util_vector_logic:2.0 utl_or_run ]
  set_property -dict [ list \
   CONFIG.C_OPERATION {or} \
   CONFIG.C_SIZE {1} \
   CONFIG.LOGO_FILE {data/sym_orgate.png} \
 ] $utl_or_run

  # Create instance: xlconcat_0, and set properties
  set xlconcat_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlconcat:2.1 xlconcat_0 ]
  set_property -dict [ list \
   CONFIG.NUM_PORTS {15} \
 ] $xlconcat_0

  # Create instance: xlconcat_1, and set properties
  set xlconcat_1 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlconcat:2.1 xlconcat_1 ]
  set_property -dict [ list \
   CONFIG.IN0_WIDTH {1} \
   CONFIG.IN1_WIDTH {15} \
   CONFIG.NUM_PORTS {2} \
 ] $xlconcat_1

  # Create instance: xlconstant_tvalid, and set properties
  set xlconstant_tvalid [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlconstant:1.1 xlconstant_tvalid ]

  # Create instance: xlconstant_tvalid1, and set properties
  set xlconstant_tvalid1 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlconstant:1.1 xlconstant_tvalid1 ]

  # Create instance: xlslice_ADC_b0, and set properties
  set xlslice_ADC_b0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 xlslice_ADC_b0 ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {0} \
   CONFIG.DIN_TO {0} \
   CONFIG.DIN_WIDTH {16} \
 ] $xlslice_ADC_b0

  # Create instance: xlslice_adc_b1tob15, and set properties
  set xlslice_adc_b1tob15 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 xlslice_adc_b1tob15 ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {15} \
   CONFIG.DIN_TO {1} \
   CONFIG.DIN_WIDTH {16} \
   CONFIG.DOUT_WIDTH {15} \
 ] $xlslice_adc_b1tob15

  # Create instance: xlslice_b0_Run, and set properties
  set xlslice_b0_Run [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 xlslice_b0_Run ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {0} \
   CONFIG.DIN_TO {0} \
   CONFIG.DIN_WIDTH {8} \
 ] $xlslice_b0_Run

  # Create instance: xlslice_b0_TTL_Run, and set properties
  set xlslice_b0_TTL_Run [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 xlslice_b0_TTL_Run ]
  set_property -dict [ list \
   CONFIG.DIN_WIDTH {4} \
 ] $xlslice_b0_TTL_Run

  # Create instance: xlslice_b1_RAND, and set properties
  set xlslice_b1_RAND [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 xlslice_b1_RAND ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {1} \
   CONFIG.DIN_TO {1} \
   CONFIG.DIN_WIDTH {8} \
 ] $xlslice_b1_RAND

  # Create instance: xlslice_b2_PGA, and set properties
  set xlslice_b2_PGA [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 xlslice_b2_PGA ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {2} \
   CONFIG.DIN_TO {2} \
   CONFIG.DIN_WIDTH {8} \
 ] $xlslice_b2_PGA

  # Create instance: xlslice_b3_SHDN, and set properties
  set xlslice_b3_SHDN [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 xlslice_b3_SHDN ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {3} \
   CONFIG.DIN_TO {3} \
   CONFIG.DIN_WIDTH {8} \
 ] $xlslice_b3_SHDN

  # Create instance: xlslice_b4_DITH, and set properties
  set xlslice_b4_DITH [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 xlslice_b4_DITH ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {4} \
   CONFIG.DIN_TO {4} \
   CONFIG.DIN_WIDTH {8} \
 ] $xlslice_b4_DITH

  # Create instance: xlslice_b5_reset, and set properties
  set xlslice_b5_reset [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 xlslice_b5_reset ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {5} \
   CONFIG.DIN_TO {5} \
   CONFIG.DIN_WIDTH {8} \
 ] $xlslice_b5_reset

  # Create instance: xlslice_b7_reset, and set properties
  set xlslice_b7_reset [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 xlslice_b7_reset ]
  set_property -dict [ list \
   CONFIG.DIN_FROM {7} \
   CONFIG.DIN_TO {7} \
   CONFIG.DIN_WIDTH {8} \
 ] $xlslice_b7_reset

  # Create interface connections
  connect_bd_intf_net -intf_net S_AXI_1 [get_bd_intf_pins S_AXI] [get_bd_intf_pins axi_gpio_0/S_AXI]
  connect_bd_intf_net -intf_net axis_register_slice_0_M_AXIS [get_bd_intf_pins M_AXIS] [get_bd_intf_pins axis_register_slice_0/M_AXIS]

  # Create port connections
  connect_bd_net -net ADC_OF_1 [get_bd_pins ADC_OF] [get_bd_pins c_counter_binary_0/CE]
  connect_bd_net -net DDS_TTL_1 [get_bd_pins ADC_TTL] [get_bd_pins xlslice_b0_TTL_Run/Din]
  connect_bd_net -net axi_gpio_0_gpio_io_o [get_bd_pins axi_gpio_0/gpio_io_i] [get_bd_pins axi_gpio_0/gpio_io_o] [get_bd_pins xlslice_b0_Run/Din] [get_bd_pins xlslice_b1_RAND/Din] [get_bd_pins xlslice_b2_PGA/Din] [get_bd_pins xlslice_b3_SHDN/Din] [get_bd_pins xlslice_b4_DITH/Din] [get_bd_pins xlslice_b5_reset/Din] [get_bd_pins xlslice_b7_reset/Din]
  connect_bd_net -net axis_clock_converter_0_m_axis_tdata [get_bd_pins axis_clock_converter_0/m_axis_tdata] [get_bd_pins axis_register_slice_0/s_axis_tdata]
  set_property -dict [ list \
HDL_ATTRIBUTE.MARK_DEBUG {true} \
 ] [get_bd_nets axis_clock_converter_0_m_axis_tdata]
  connect_bd_net -net c_counter_binary_0_Q [get_bd_pins axi_gpio_0/gpio2_io_i] [get_bd_pins c_counter_binary_0/Q]
  connect_bd_net -net data_in_from_pins_1 [get_bd_pins ADC_DATA] [get_bd_pins selectio_wiz_0/data_in_from_pins]
  connect_bd_net -net m_axis_aclk_1 [get_bd_pins m_axis_aclk] [get_bd_pins axis_clock_converter_0/m_axis_aclk] [get_bd_pins axis_register_slice_0/aclk]
  connect_bd_net -net m_axis_aresetn_1 [get_bd_pins m_axis_aresetn] [get_bd_pins axis_clock_converter_0/m_axis_aresetn] [get_bd_pins axis_register_slice_0/aresetn]
  connect_bd_net -net s_axi_aclk_1 [get_bd_pins s_axi_aclk] [get_bd_pins axi_gpio_0/s_axi_aclk]
  connect_bd_net -net s_axi_aresetn_1 [get_bd_pins s_axi_aresetn] [get_bd_pins axi_gpio_0/s_axi_aresetn]
  connect_bd_net -net selectio_wiz_0_clk_out [get_bd_pins axis_clock_converter_0/s_axis_aclk] [get_bd_pins c_counter_binary_0/CLK] [get_bd_pins selectio_wiz_0/clk_out]
  connect_bd_net -net selectio_wiz_0_data_in_to_device [get_bd_pins selectio_wiz_0/data_in_to_device] [get_bd_pins xlslice_ADC_b0/Din] [get_bd_pins xlslice_adc_b1tob15/Din]
  set_property -dict [ list \
HDL_ATTRIBUTE.MARK_DEBUG {true} \
 ] [get_bd_nets selectio_wiz_0_data_in_to_device]
  connect_bd_net -net util_ds_buf_0_IBUF_OUT [get_bd_pins ADC_CLKOUT_N] [get_bd_pins selectio_wiz_0/clk_in]
  connect_bd_net -net util_vector_logic_0_Res [get_bd_pins util_vector_logic_0/Res] [get_bd_pins xlconcat_1/In1]
  connect_bd_net -net util_vector_logic_1_Res [get_bd_pins util_vector_b0and/Res] [get_bd_pins xlconcat_0/In0] [get_bd_pins xlconcat_0/In1] [get_bd_pins xlconcat_0/In2] [get_bd_pins xlconcat_0/In3] [get_bd_pins xlconcat_0/In4] [get_bd_pins xlconcat_0/In5] [get_bd_pins xlconcat_0/In6] [get_bd_pins xlconcat_0/In7] [get_bd_pins xlconcat_0/In8] [get_bd_pins xlconcat_0/In9] [get_bd_pins xlconcat_0/In10] [get_bd_pins xlconcat_0/In11] [get_bd_pins xlconcat_0/In12] [get_bd_pins xlconcat_0/In13] [get_bd_pins xlconcat_0/In14]
  connect_bd_net -net utl_or_run_Res [get_bd_pins axis_register_slice_0/s_axis_tvalid] [get_bd_pins utl_or_run/Res]
  connect_bd_net -net xlconcat_0_dout [get_bd_pins util_vector_logic_0/Op2] [get_bd_pins xlconcat_0/dout]
  connect_bd_net -net xlconcat_1_dout [get_bd_pins axis_clock_converter_0/s_axis_tdata] [get_bd_pins xlconcat_1/dout]
  set_property -dict [ list \
HDL_ATTRIBUTE.MARK_DEBUG {true} \
 ] [get_bd_nets xlconcat_1_dout]
  connect_bd_net -net xlconstant_0_const [get_bd_pins axis_clock_converter_0/s_axis_aresetn] [get_bd_pins axis_clock_converter_0/s_axis_tvalid] [get_bd_pins xlconstant_tvalid/dout]
  connect_bd_net -net xlconstant_tvalid1_dout [get_bd_pins axis_clock_converter_0/m_axis_tready] [get_bd_pins xlconstant_tvalid1/dout]
  connect_bd_net -net xlslice_ADC_b0_Dout [get_bd_pins util_vector_b0and/Op1] [get_bd_pins xlconcat_1/In0] [get_bd_pins xlslice_ADC_b0/Dout]
  connect_bd_net -net xlslice_adc_b1tob15_Dout [get_bd_pins util_vector_logic_0/Op1] [get_bd_pins xlslice_adc_b1tob15/Dout]
  connect_bd_net -net xlslice_b0_Run_Dout [get_bd_pins utl_or_run/Op1] [get_bd_pins xlslice_b0_Run/Dout]
  connect_bd_net -net xlslice_b0_TTL_Run_Dout [get_bd_pins utl_or_run/Op2] [get_bd_pins xlslice_b0_TTL_Run/Dout]
  connect_bd_net -net xlslice_b0_reset_Dout [get_bd_pins selectio_wiz_0/io_reset] [get_bd_pins xlslice_b5_reset/Dout]
  connect_bd_net -net xlslice_b1_RAND_Dout [get_bd_pins ADC_RAND] [get_bd_pins util_vector_b0and/Op2] [get_bd_pins xlslice_b1_RAND/Dout]
  connect_bd_net -net xlslice_b2_PGA_Dout [get_bd_pins ADC_PGA] [get_bd_pins xlslice_b2_PGA/Dout]
  connect_bd_net -net xlslice_b3_SHDN_Dout [get_bd_pins ADC_SHDN] [get_bd_pins xlslice_b3_SHDN/Dout]
  connect_bd_net -net xlslice_b4_DITH_Dout [get_bd_pins ADC_DITH] [get_bd_pins xlslice_b4_DITH/Dout]
  connect_bd_net -net xlslice_b7_reset_OFcount_Dout [get_bd_pins c_counter_binary_0/SCLR] [get_bd_pins xlslice_b7_reset/Dout]

  # Restore current instance
  current_bd_instance $oldCurInst
}


# Procedure to create entire design; Provide argument to make
# procedure reusable. If parentCell is "", will use root.
proc create_root_design { parentCell } {

  variable script_folder
  variable design_name

  if { $parentCell eq "" } {
     set parentCell [get_bd_cells /]
  }

  # Get object for parentCell
  set parentObj [get_bd_cells $parentCell]
  if { $parentObj == "" } {
     catch {common::send_msg_id "BD_TCL-100" "ERROR" "Unable to find parent cell <$parentCell>!"}
     return
  }

  # Make sure parentObj is hier blk
  set parentType [get_property TYPE $parentObj]
  if { $parentType ne "hier" } {
     catch {common::send_msg_id "BD_TCL-101" "ERROR" "Parent <$parentObj> has TYPE = <$parentType>. Expected to be <hier>."}
     return
  }

  # Save current instance; Restore later
  set oldCurInst [current_bd_instance .]

  # Set parent object as current
  current_bd_instance $parentObj


  # Create interface ports
  set DDR [ create_bd_intf_port -mode Master -vlnv xilinx.com:interface:ddrx_rtl:1.0 DDR ]
  set FIXED_IO [ create_bd_intf_port -mode Master -vlnv xilinx.com:display_processing_system7:fixedio_rtl:1.0 FIXED_IO ]

  # Create ports
  set ADC_CLKOUT_N [ create_bd_port -dir I ADC_CLKOUT_N ]
  set ADC_DATA [ create_bd_port -dir I -from 15 -to 0 ADC_DATA ]
  set ADC_DITH [ create_bd_port -dir O -from 0 -to 0 ADC_DITH ]
  set ADC_OF [ create_bd_port -dir I ADC_OF ]
  set ADC_PGA [ create_bd_port -dir O -from 0 -to 0 ADC_PGA ]
  set ADC_RAND [ create_bd_port -dir O -from 0 -to 0 ADC_RAND ]
  set ADC_SHDN [ create_bd_port -dir O -from 0 -to 0 ADC_SHDN ]
  set DDS_CLKEN [ create_bd_port -dir O -from 0 -to 0 DDS_CLKEN ]
  set DDS_IO_UPDATE [ create_bd_port -dir O -from 0 -to 0 DDS_IO_UPDATE ]
  set DDS_PWRD [ create_bd_port -dir O -from 0 -to 0 DDS_PWRD ]
  set DDS_RESET [ create_bd_port -dir O -from 0 -to 0 DDS_RESET ]
  set DDS_SCLK [ create_bd_port -dir O DDS_SCLK ]
  set DDS_SDIO [ create_bd_port -dir O DDS_SDIO ]
  set DDS_SDO [ create_bd_port -dir I DDS_SDO ]
  set DDS_SWT_EN [ create_bd_port -dir O -from 0 -to 0 DDS_SWT_EN ]
  set DDS_SYNC [ create_bd_port -dir O -from 0 -to 0 DDS_SYNC ]
  set FPGA_CLK_N [ create_bd_port -dir I FPGA_CLK_N ]
  set FPGA_CLK_P [ create_bd_port -dir I FPGA_CLK_P ]
  set IO [ create_bd_port -dir O -from 7 -to 0 -type data IO ]
  set IO_15_12 [ create_bd_port -dir O -from 3 -to 0 IO_15_12 ]
  set LED_FRONT [ create_bd_port -dir O -from 0 -to 0 LED_FRONT ]
  set N_TEMP_GATE [ create_bd_port -dir O -from 0 -to 0 N_TEMP_GATE ]
  set PERIPHERAL_RESET [ create_bd_port -dir O -from 0 -to 0 PERIPHERAL_RESET ]
  set P_0 [ create_bd_port -dir O -from 0 -to 0 P_0 ]
  set P_4_3 [ create_bd_port -dir O -from 1 -to 0 P_4_3 ]
  set SRSET [ create_bd_port -dir O -from 0 -to 0 SRSET ]
  set TEMP_ADC_DIN_CLK_CSN [ create_bd_port -dir O -from 2 -to 0 TEMP_ADC_DIN_CLK_CSN ]
  set TEMP_ADC_DOUT [ create_bd_port -dir I TEMP_ADC_DOUT ]
  set TRIGGER_IN [ create_bd_port -dir I TRIGGER_IN ]

  # Create instance: ADC_LTC2207
  create_hier_cell_ADC_LTC2207 [current_bd_instance .] ADC_LTC2207

  # Create instance: DDS_AD9951
  create_hier_cell_DDS_AD9951 [current_bd_instance .] DDS_AD9951

  # Create instance: FPGA_CLKin, and set properties
  set FPGA_CLKin [ create_bd_cell -type ip -vlnv xilinx.com:ip:clk_wiz:5.4 FPGA_CLKin ]
  set_property -dict [ list \
   CONFIG.CLKOUT1_DRIVES {BUFGCE} \
   CONFIG.CLKOUT2_DRIVES {BUFGCE} \
   CONFIG.CLKOUT2_JITTER {130.958} \
   CONFIG.CLKOUT2_PHASE_ERROR {98.575} \
   CONFIG.CLKOUT2_USED {true} \
   CONFIG.CLKOUT3_DRIVES {BUFGCE} \
   CONFIG.CLKOUT4_DRIVES {BUFGCE} \
   CONFIG.CLKOUT5_DRIVES {BUFGCE} \
   CONFIG.CLKOUT6_DRIVES {BUFGCE} \
   CONFIG.CLKOUT7_DRIVES {BUFGCE} \
   CONFIG.MMCM_CLKIN1_PERIOD {10.000} \
   CONFIG.MMCM_CLKIN2_PERIOD {10.000} \
   CONFIG.MMCM_CLKOUT1_DIVIDE {10} \
   CONFIG.NUM_OUT_CLKS {2} \
   CONFIG.PRIM_SOURCE {Differential_clock_capable_pin} \
   CONFIG.USE_RESET {false} \
   CONFIG.USE_SAFE_CLOCK_STARTUP {true} \
 ] $FPGA_CLKin

  # Create instance: TTL
  create_hier_cell_TTL [current_bd_instance .] TTL

  # Create instance: axi_interconnect_0, and set properties
  set axi_interconnect_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:axi_interconnect:2.1 axi_interconnect_0 ]
  set_property -dict [ list \
   CONFIG.NUM_MI {4} \
   CONFIG.SYNCHRONIZATION_STAGES {2} \
 ] $axi_interconnect_0

  # Create instance: axi_interconnect_1, and set properties
  set axi_interconnect_1 [ create_bd_cell -type ip -vlnv xilinx.com:ip:axi_interconnect:2.1 axi_interconnect_1 ]

  # Create instance: axi_protocol_converter_0, and set properties
  set axi_protocol_converter_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:axi_protocol_converter:2.1 axi_protocol_converter_0 ]

  # Create instance: azynq_0, and set properties
  set azynq_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:processing_system7:5.5 azynq_0 ]
  set_property -dict [ list \
   CONFIG.PCW_ACT_APU_PERIPHERAL_FREQMHZ {666.666687} \
   CONFIG.PCW_ACT_CAN0_PERIPHERAL_FREQMHZ {23.8095} \
   CONFIG.PCW_ACT_CAN1_PERIPHERAL_FREQMHZ {23.8095} \
   CONFIG.PCW_ACT_CAN_PERIPHERAL_FREQMHZ {10.000000} \
   CONFIG.PCW_ACT_DCI_PERIPHERAL_FREQMHZ {10.158730} \
   CONFIG.PCW_ACT_ENET0_PERIPHERAL_FREQMHZ {125.000000} \
   CONFIG.PCW_ACT_ENET1_PERIPHERAL_FREQMHZ {10.000000} \
   CONFIG.PCW_ACT_FPGA0_PERIPHERAL_FREQMHZ {100.000000} \
   CONFIG.PCW_ACT_FPGA1_PERIPHERAL_FREQMHZ {10.000000} \
   CONFIG.PCW_ACT_FPGA2_PERIPHERAL_FREQMHZ {10.000000} \
   CONFIG.PCW_ACT_FPGA3_PERIPHERAL_FREQMHZ {10.000000} \
   CONFIG.PCW_ACT_I2C_PERIPHERAL_FREQMHZ {50} \
   CONFIG.PCW_ACT_PCAP_PERIPHERAL_FREQMHZ {200.000000} \
   CONFIG.PCW_ACT_QSPI_PERIPHERAL_FREQMHZ {200.000000} \
   CONFIG.PCW_ACT_SDIO_PERIPHERAL_FREQMHZ {50.000000} \
   CONFIG.PCW_ACT_SMC_PERIPHERAL_FREQMHZ {10.000000} \
   CONFIG.PCW_ACT_SPI_PERIPHERAL_FREQMHZ {10.000000} \
   CONFIG.PCW_ACT_TPIU_PERIPHERAL_FREQMHZ {200.000000} \
   CONFIG.PCW_ACT_TTC0_CLK0_PERIPHERAL_FREQMHZ {111.111115} \
   CONFIG.PCW_ACT_TTC0_CLK1_PERIPHERAL_FREQMHZ {111.111115} \
   CONFIG.PCW_ACT_TTC0_CLK2_PERIPHERAL_FREQMHZ {111.111115} \
   CONFIG.PCW_ACT_TTC1_CLK0_PERIPHERAL_FREQMHZ {111.111115} \
   CONFIG.PCW_ACT_TTC1_CLK1_PERIPHERAL_FREQMHZ {111.111115} \
   CONFIG.PCW_ACT_TTC1_CLK2_PERIPHERAL_FREQMHZ {111.111115} \
   CONFIG.PCW_ACT_TTC_PERIPHERAL_FREQMHZ {50} \
   CONFIG.PCW_ACT_UART_PERIPHERAL_FREQMHZ {50.000000} \
   CONFIG.PCW_ACT_USB0_PERIPHERAL_FREQMHZ {60} \
   CONFIG.PCW_ACT_USB1_PERIPHERAL_FREQMHZ {60} \
   CONFIG.PCW_ACT_WDT_PERIPHERAL_FREQMHZ {111.111115} \
   CONFIG.PCW_APU_CLK_RATIO_ENABLE {6:2:1} \
   CONFIG.PCW_APU_PERIPHERAL_FREQMHZ {666.666666} \
   CONFIG.PCW_ARMPLL_CTRL_FBDIV {40} \
   CONFIG.PCW_CAN0_BASEADDR {0xE0008000} \
   CONFIG.PCW_CAN0_GRP_CLK_ENABLE {0} \
   CONFIG.PCW_CAN0_HIGHADDR {0xE0008FFF} \
   CONFIG.PCW_CAN0_PERIPHERAL_CLKSRC {External} \
   CONFIG.PCW_CAN0_PERIPHERAL_ENABLE {0} \
   CONFIG.PCW_CAN0_PERIPHERAL_FREQMHZ {-1} \
   CONFIG.PCW_CAN1_BASEADDR {0xE0009000} \
   CONFIG.PCW_CAN1_GRP_CLK_ENABLE {0} \
   CONFIG.PCW_CAN1_HIGHADDR {0xE0009FFF} \
   CONFIG.PCW_CAN1_PERIPHERAL_CLKSRC {External} \
   CONFIG.PCW_CAN1_PERIPHERAL_ENABLE {0} \
   CONFIG.PCW_CAN1_PERIPHERAL_FREQMHZ {-1} \
   CONFIG.PCW_CAN_PERIPHERAL_CLKSRC {IO PLL} \
   CONFIG.PCW_CAN_PERIPHERAL_DIVISOR0 {1} \
   CONFIG.PCW_CAN_PERIPHERAL_DIVISOR1 {1} \
   CONFIG.PCW_CAN_PERIPHERAL_FREQMHZ {100} \
   CONFIG.PCW_CAN_PERIPHERAL_VALID {0} \
   CONFIG.PCW_CLK0_FREQ {100000000} \
   CONFIG.PCW_CLK1_FREQ {10000000} \
   CONFIG.PCW_CLK2_FREQ {10000000} \
   CONFIG.PCW_CLK3_FREQ {10000000} \
   CONFIG.PCW_CORE0_FIQ_INTR {0} \
   CONFIG.PCW_CORE0_IRQ_INTR {0} \
   CONFIG.PCW_CORE1_FIQ_INTR {0} \
   CONFIG.PCW_CORE1_IRQ_INTR {0} \
   CONFIG.PCW_CPU_CPU_6X4X_MAX_RANGE {667} \
   CONFIG.PCW_CPU_CPU_PLL_FREQMHZ {1333.333} \
   CONFIG.PCW_CPU_PERIPHERAL_CLKSRC {ARM PLL} \
   CONFIG.PCW_CPU_PERIPHERAL_DIVISOR0 {2} \
   CONFIG.PCW_CRYSTAL_PERIPHERAL_FREQMHZ {33.333333} \
   CONFIG.PCW_DCI_PERIPHERAL_CLKSRC {1} \
   CONFIG.PCW_DCI_PERIPHERAL_DIVISOR0 {15} \
   CONFIG.PCW_DCI_PERIPHERAL_DIVISOR1 {7} \
   CONFIG.PCW_DCI_PERIPHERAL_FREQMHZ {10.159} \
   CONFIG.PCW_DDRPLL_CTRL_FBDIV {32} \
   CONFIG.PCW_DDR_DDR_PLL_FREQMHZ {1066.667} \
   CONFIG.PCW_DDR_HPRLPR_QUEUE_PARTITION {HPR(0)/LPR(32)} \
   CONFIG.PCW_DDR_HPR_TO_CRITICAL_PRIORITY_LEVEL {15} \
   CONFIG.PCW_DDR_LPR_TO_CRITICAL_PRIORITY_LEVEL {2} \
   CONFIG.PCW_DDR_PERIPHERAL_CLKSRC {DDR PLL} \
   CONFIG.PCW_DDR_PERIPHERAL_DIVISOR0 {2} \
   CONFIG.PCW_DDR_PORT0_HPR_ENABLE {0} \
   CONFIG.PCW_DDR_PORT1_HPR_ENABLE {0} \
   CONFIG.PCW_DDR_PORT2_HPR_ENABLE {0} \
   CONFIG.PCW_DDR_PORT3_HPR_ENABLE {0} \
   CONFIG.PCW_DDR_RAM_BASEADDR {0x00100000} \
   CONFIG.PCW_DDR_RAM_HIGHADDR {0x3FFFFFFF} \
   CONFIG.PCW_DDR_WRITE_TO_CRITICAL_PRIORITY_LEVEL {2} \
   CONFIG.PCW_DM_WIDTH {4} \
   CONFIG.PCW_DQS_WIDTH {4} \
   CONFIG.PCW_DQ_WIDTH {32} \
   CONFIG.PCW_ENET0_BASEADDR {0xE000B000} \
   CONFIG.PCW_ENET0_ENET0_IO {MIO 16 .. 27} \
   CONFIG.PCW_ENET0_GRP_MDIO_ENABLE {1} \
   CONFIG.PCW_ENET0_GRP_MDIO_IO {MIO 52 .. 53} \
   CONFIG.PCW_ENET0_HIGHADDR {0xE000BFFF} \
   CONFIG.PCW_ENET0_PERIPHERAL_CLKSRC {IO PLL} \
   CONFIG.PCW_ENET0_PERIPHERAL_DIVISOR0 {8} \
   CONFIG.PCW_ENET0_PERIPHERAL_DIVISOR1 {1} \
   CONFIG.PCW_ENET0_PERIPHERAL_ENABLE {1} \
   CONFIG.PCW_ENET0_PERIPHERAL_FREQMHZ {1000 Mbps} \
   CONFIG.PCW_ENET0_RESET_ENABLE {0} \
   CONFIG.PCW_ENET1_BASEADDR {0xE000C000} \
   CONFIG.PCW_ENET1_GRP_MDIO_ENABLE {0} \
   CONFIG.PCW_ENET1_HIGHADDR {0xE000CFFF} \
   CONFIG.PCW_ENET1_PERIPHERAL_CLKSRC {IO PLL} \
   CONFIG.PCW_ENET1_PERIPHERAL_DIVISOR0 {1} \
   CONFIG.PCW_ENET1_PERIPHERAL_DIVISOR1 {1} \
   CONFIG.PCW_ENET1_PERIPHERAL_ENABLE {0} \
   CONFIG.PCW_ENET1_PERIPHERAL_FREQMHZ {1000 Mbps} \
   CONFIG.PCW_ENET1_RESET_ENABLE {0} \
   CONFIG.PCW_ENET_RESET_ENABLE {1} \
   CONFIG.PCW_ENET_RESET_POLARITY {Active Low} \
   CONFIG.PCW_ENET_RESET_SELECT {Share reset pin} \
   CONFIG.PCW_EN_4K_TIMER {0} \
   CONFIG.PCW_EN_CAN0 {0} \
   CONFIG.PCW_EN_CAN1 {0} \
   CONFIG.PCW_EN_CLK0_PORT {1} \
   CONFIG.PCW_EN_CLK1_PORT {0} \
   CONFIG.PCW_EN_CLK2_PORT {0} \
   CONFIG.PCW_EN_CLK3_PORT {0} \
   CONFIG.PCW_EN_CLKTRIG0_PORT {0} \
   CONFIG.PCW_EN_CLKTRIG1_PORT {0} \
   CONFIG.PCW_EN_CLKTRIG2_PORT {0} \
   CONFIG.PCW_EN_CLKTRIG3_PORT {0} \
   CONFIG.PCW_EN_DDR {1} \
   CONFIG.PCW_EN_EMIO_CAN0 {0} \
   CONFIG.PCW_EN_EMIO_CAN1 {0} \
   CONFIG.PCW_EN_EMIO_CD_SDIO0 {0} \
   CONFIG.PCW_EN_EMIO_CD_SDIO1 {1} \
   CONFIG.PCW_EN_EMIO_ENET0 {0} \
   CONFIG.PCW_EN_EMIO_ENET1 {0} \
   CONFIG.PCW_EN_EMIO_GPIO {0} \
   CONFIG.PCW_EN_EMIO_I2C0 {0} \
   CONFIG.PCW_EN_EMIO_I2C1 {0} \
   CONFIG.PCW_EN_EMIO_MODEM_UART0 {0} \
   CONFIG.PCW_EN_EMIO_MODEM_UART1 {0} \
   CONFIG.PCW_EN_EMIO_PJTAG {0} \
   CONFIG.PCW_EN_EMIO_SDIO0 {0} \
   CONFIG.PCW_EN_EMIO_SDIO1 {0} \
   CONFIG.PCW_EN_EMIO_SPI0 {0} \
   CONFIG.PCW_EN_EMIO_SPI1 {0} \
   CONFIG.PCW_EN_EMIO_SRAM_INT {0} \
   CONFIG.PCW_EN_EMIO_TRACE {0} \
   CONFIG.PCW_EN_EMIO_TTC0 {1} \
   CONFIG.PCW_EN_EMIO_TTC1 {0} \
   CONFIG.PCW_EN_EMIO_UART0 {1} \
   CONFIG.PCW_EN_EMIO_UART1 {0} \
   CONFIG.PCW_EN_EMIO_WDT {0} \
   CONFIG.PCW_EN_EMIO_WP_SDIO0 {0} \
   CONFIG.PCW_EN_EMIO_WP_SDIO1 {0} \
   CONFIG.PCW_EN_ENET0 {1} \
   CONFIG.PCW_EN_ENET1 {0} \
   CONFIG.PCW_EN_GPIO {1} \
   CONFIG.PCW_EN_I2C0 {0} \
   CONFIG.PCW_EN_I2C1 {0} \
   CONFIG.PCW_EN_MODEM_UART0 {0} \
   CONFIG.PCW_EN_MODEM_UART1 {0} \
   CONFIG.PCW_EN_PJTAG {0} \
   CONFIG.PCW_EN_PTP_ENET0 {1} \
   CONFIG.PCW_EN_PTP_ENET1 {0} \
   CONFIG.PCW_EN_QSPI {1} \
   CONFIG.PCW_EN_RST0_PORT {1} \
   CONFIG.PCW_EN_RST1_PORT {1} \
   CONFIG.PCW_EN_RST2_PORT {0} \
   CONFIG.PCW_EN_RST3_PORT {0} \
   CONFIG.PCW_EN_SDIO0 {1} \
   CONFIG.PCW_EN_SDIO1 {1} \
   CONFIG.PCW_EN_SMC {0} \
   CONFIG.PCW_EN_SPI0 {0} \
   CONFIG.PCW_EN_SPI1 {0} \
   CONFIG.PCW_EN_TRACE {0} \
   CONFIG.PCW_EN_TTC0 {1} \
   CONFIG.PCW_EN_TTC1 {0} \
   CONFIG.PCW_EN_UART0 {1} \
   CONFIG.PCW_EN_UART1 {1} \
   CONFIG.PCW_EN_USB0 {1} \
   CONFIG.PCW_EN_USB1 {0} \
   CONFIG.PCW_EN_WDT {0} \
   CONFIG.PCW_FCLK0_PERIPHERAL_CLKSRC {IO PLL} \
   CONFIG.PCW_FCLK0_PERIPHERAL_DIVISOR0 {5} \
   CONFIG.PCW_FCLK0_PERIPHERAL_DIVISOR1 {2} \
   CONFIG.PCW_FCLK1_PERIPHERAL_CLKSRC {IO PLL} \
   CONFIG.PCW_FCLK1_PERIPHERAL_DIVISOR0 {1} \
   CONFIG.PCW_FCLK1_PERIPHERAL_DIVISOR1 {1} \
   CONFIG.PCW_FCLK2_PERIPHERAL_CLKSRC {IO PLL} \
   CONFIG.PCW_FCLK2_PERIPHERAL_DIVISOR0 {1} \
   CONFIG.PCW_FCLK2_PERIPHERAL_DIVISOR1 {1} \
   CONFIG.PCW_FCLK3_PERIPHERAL_CLKSRC {IO PLL} \
   CONFIG.PCW_FCLK3_PERIPHERAL_DIVISOR0 {1} \
   CONFIG.PCW_FCLK3_PERIPHERAL_DIVISOR1 {1} \
   CONFIG.PCW_FCLK_CLK0_BUF {TRUE} \
   CONFIG.PCW_FCLK_CLK1_BUF {FALSE} \
   CONFIG.PCW_FCLK_CLK2_BUF {FALSE} \
   CONFIG.PCW_FCLK_CLK3_BUF {FALSE} \
   CONFIG.PCW_FPGA0_PERIPHERAL_FREQMHZ {100} \
   CONFIG.PCW_FPGA1_PERIPHERAL_FREQMHZ {100} \
   CONFIG.PCW_FPGA2_PERIPHERAL_FREQMHZ {33.333333} \
   CONFIG.PCW_FPGA3_PERIPHERAL_FREQMHZ {50} \
   CONFIG.PCW_FPGA_FCLK0_ENABLE {1} \
   CONFIG.PCW_FPGA_FCLK1_ENABLE {0} \
   CONFIG.PCW_FPGA_FCLK2_ENABLE {0} \
   CONFIG.PCW_FPGA_FCLK3_ENABLE {0} \
   CONFIG.PCW_FTM_CTI_IN0 {<Select>} \
   CONFIG.PCW_FTM_CTI_IN1 {<Select>} \
   CONFIG.PCW_FTM_CTI_IN2 {<Select>} \
   CONFIG.PCW_FTM_CTI_IN3 {<Select>} \
   CONFIG.PCW_FTM_CTI_OUT0 {<Select>} \
   CONFIG.PCW_FTM_CTI_OUT1 {<Select>} \
   CONFIG.PCW_FTM_CTI_OUT2 {<Select>} \
   CONFIG.PCW_FTM_CTI_OUT3 {<Select>} \
   CONFIG.PCW_GP0_EN_MODIFIABLE_TXN {0} \
   CONFIG.PCW_GP0_NUM_READ_THREADS {4} \
   CONFIG.PCW_GP0_NUM_WRITE_THREADS {4} \
   CONFIG.PCW_GP1_EN_MODIFIABLE_TXN {0} \
   CONFIG.PCW_GP1_NUM_READ_THREADS {4} \
   CONFIG.PCW_GP1_NUM_WRITE_THREADS {4} \
   CONFIG.PCW_GPIO_BASEADDR {0xE000A000} \
   CONFIG.PCW_GPIO_EMIO_GPIO_ENABLE {0} \
   CONFIG.PCW_GPIO_EMIO_GPIO_IO {<Select>} \
   CONFIG.PCW_GPIO_EMIO_GPIO_WIDTH {64} \
   CONFIG.PCW_GPIO_HIGHADDR {0xE000AFFF} \
   CONFIG.PCW_GPIO_MIO_GPIO_ENABLE {1} \
   CONFIG.PCW_GPIO_MIO_GPIO_IO {MIO} \
   CONFIG.PCW_GPIO_PERIPHERAL_ENABLE {1} \
   CONFIG.PCW_I2C0_BASEADDR {0xE0004000} \
   CONFIG.PCW_I2C0_GRP_INT_ENABLE {0} \
   CONFIG.PCW_I2C0_HIGHADDR {0xE0004FFF} \
   CONFIG.PCW_I2C0_PERIPHERAL_ENABLE {0} \
   CONFIG.PCW_I2C0_RESET_ENABLE {0} \
   CONFIG.PCW_I2C1_BASEADDR {0xE0005000} \
   CONFIG.PCW_I2C1_GRP_INT_ENABLE {0} \
   CONFIG.PCW_I2C1_HIGHADDR {0xE0005FFF} \
   CONFIG.PCW_I2C1_PERIPHERAL_ENABLE {0} \
   CONFIG.PCW_I2C1_RESET_ENABLE {0} \
   CONFIG.PCW_I2C_PERIPHERAL_FREQMHZ {25} \
   CONFIG.PCW_I2C_RESET_ENABLE {1} \
   CONFIG.PCW_I2C_RESET_POLARITY {Active Low} \
   CONFIG.PCW_IMPORT_BOARD_PRESET {None} \
   CONFIG.PCW_INCLUDE_ACP_TRANS_CHECK {0} \
   CONFIG.PCW_INCLUDE_TRACE_BUFFER {0} \
   CONFIG.PCW_IOPLL_CTRL_FBDIV {30} \
   CONFIG.PCW_IO_IO_PLL_FREQMHZ {1000.000} \
   CONFIG.PCW_IRQ_F2P_INTR {1} \
   CONFIG.PCW_IRQ_F2P_MODE {REVERSE} \
   CONFIG.PCW_MIO_0_DIRECTION {inout} \
   CONFIG.PCW_MIO_0_IOTYPE {LVCMOS 3.3V} \
   CONFIG.PCW_MIO_0_PULLUP {disabled} \
   CONFIG.PCW_MIO_0_SLEW {slow} \
   CONFIG.PCW_MIO_10_DIRECTION {inout} \
   CONFIG.PCW_MIO_10_IOTYPE {LVCMOS 3.3V} \
   CONFIG.PCW_MIO_10_PULLUP {disabled} \
   CONFIG.PCW_MIO_10_SLEW {slow} \
   CONFIG.PCW_MIO_11_DIRECTION {inout} \
   CONFIG.PCW_MIO_11_IOTYPE {LVCMOS 3.3V} \
   CONFIG.PCW_MIO_11_PULLUP {disabled} \
   CONFIG.PCW_MIO_11_SLEW {slow} \
   CONFIG.PCW_MIO_12_DIRECTION {inout} \
   CONFIG.PCW_MIO_12_IOTYPE {LVCMOS 3.3V} \
   CONFIG.PCW_MIO_12_PULLUP {disabled} \
   CONFIG.PCW_MIO_12_SLEW {slow} \
   CONFIG.PCW_MIO_13_DIRECTION {inout} \
   CONFIG.PCW_MIO_13_IOTYPE {LVCMOS 3.3V} \
   CONFIG.PCW_MIO_13_PULLUP {disabled} \
   CONFIG.PCW_MIO_13_SLEW {slow} \
   CONFIG.PCW_MIO_14_DIRECTION {inout} \
   CONFIG.PCW_MIO_14_IOTYPE {LVCMOS 3.3V} \
   CONFIG.PCW_MIO_14_PULLUP {disabled} \
   CONFIG.PCW_MIO_14_SLEW {slow} \
   CONFIG.PCW_MIO_15_DIRECTION {inout} \
   CONFIG.PCW_MIO_15_IOTYPE {LVCMOS 3.3V} \
   CONFIG.PCW_MIO_15_PULLUP {disabled} \
   CONFIG.PCW_MIO_15_SLEW {slow} \
   CONFIG.PCW_MIO_16_DIRECTION {out} \
   CONFIG.PCW_MIO_16_IOTYPE {LVCMOS 1.8V} \
   CONFIG.PCW_MIO_16_PULLUP {disabled} \
   CONFIG.PCW_MIO_16_SLEW {slow} \
   CONFIG.PCW_MIO_17_DIRECTION {out} \
   CONFIG.PCW_MIO_17_IOTYPE {LVCMOS 1.8V} \
   CONFIG.PCW_MIO_17_PULLUP {disabled} \
   CONFIG.PCW_MIO_17_SLEW {slow} \
   CONFIG.PCW_MIO_18_DIRECTION {out} \
   CONFIG.PCW_MIO_18_IOTYPE {LVCMOS 1.8V} \
   CONFIG.PCW_MIO_18_PULLUP {disabled} \
   CONFIG.PCW_MIO_18_SLEW {slow} \
   CONFIG.PCW_MIO_19_DIRECTION {out} \
   CONFIG.PCW_MIO_19_IOTYPE {LVCMOS 1.8V} \
   CONFIG.PCW_MIO_19_PULLUP {disabled} \
   CONFIG.PCW_MIO_19_SLEW {slow} \
   CONFIG.PCW_MIO_1_DIRECTION {out} \
   CONFIG.PCW_MIO_1_IOTYPE {LVCMOS 3.3V} \
   CONFIG.PCW_MIO_1_PULLUP {disabled} \
   CONFIG.PCW_MIO_1_SLEW {slow} \
   CONFIG.PCW_MIO_20_DIRECTION {out} \
   CONFIG.PCW_MIO_20_IOTYPE {LVCMOS 1.8V} \
   CONFIG.PCW_MIO_20_PULLUP {disabled} \
   CONFIG.PCW_MIO_20_SLEW {slow} \
   CONFIG.PCW_MIO_21_DIRECTION {out} \
   CONFIG.PCW_MIO_21_IOTYPE {LVCMOS 1.8V} \
   CONFIG.PCW_MIO_21_PULLUP {disabled} \
   CONFIG.PCW_MIO_21_SLEW {slow} \
   CONFIG.PCW_MIO_22_DIRECTION {in} \
   CONFIG.PCW_MIO_22_IOTYPE {LVCMOS 1.8V} \
   CONFIG.PCW_MIO_22_PULLUP {disabled} \
   CONFIG.PCW_MIO_22_SLEW {slow} \
   CONFIG.PCW_MIO_23_DIRECTION {in} \
   CONFIG.PCW_MIO_23_IOTYPE {LVCMOS 1.8V} \
   CONFIG.PCW_MIO_23_PULLUP {disabled} \
   CONFIG.PCW_MIO_23_SLEW {slow} \
   CONFIG.PCW_MIO_24_DIRECTION {in} \
   CONFIG.PCW_MIO_24_IOTYPE {LVCMOS 1.8V} \
   CONFIG.PCW_MIO_24_PULLUP {disabled} \
   CONFIG.PCW_MIO_24_SLEW {slow} \
   CONFIG.PCW_MIO_25_DIRECTION {in} \
   CONFIG.PCW_MIO_25_IOTYPE {LVCMOS 1.8V} \
   CONFIG.PCW_MIO_25_PULLUP {disabled} \
   CONFIG.PCW_MIO_25_SLEW {slow} \
   CONFIG.PCW_MIO_26_DIRECTION {in} \
   CONFIG.PCW_MIO_26_IOTYPE {LVCMOS 1.8V} \
   CONFIG.PCW_MIO_26_PULLUP {disabled} \
   CONFIG.PCW_MIO_26_SLEW {slow} \
   CONFIG.PCW_MIO_27_DIRECTION {in} \
   CONFIG.PCW_MIO_27_IOTYPE {LVCMOS 1.8V} \
   CONFIG.PCW_MIO_27_PULLUP {disabled} \
   CONFIG.PCW_MIO_27_SLEW {slow} \
   CONFIG.PCW_MIO_28_DIRECTION {inout} \
   CONFIG.PCW_MIO_28_IOTYPE {LVCMOS 1.8V} \
   CONFIG.PCW_MIO_28_PULLUP {disabled} \
   CONFIG.PCW_MIO_28_SLEW {slow} \
   CONFIG.PCW_MIO_29_DIRECTION {in} \
   CONFIG.PCW_MIO_29_IOTYPE {LVCMOS 1.8V} \
   CONFIG.PCW_MIO_29_PULLUP {disabled} \
   CONFIG.PCW_MIO_29_SLEW {slow} \
   CONFIG.PCW_MIO_2_DIRECTION {inout} \
   CONFIG.PCW_MIO_2_IOTYPE {LVCMOS 3.3V} \
   CONFIG.PCW_MIO_2_PULLUP {disabled} \
   CONFIG.PCW_MIO_2_SLEW {slow} \
   CONFIG.PCW_MIO_30_DIRECTION {out} \
   CONFIG.PCW_MIO_30_IOTYPE {LVCMOS 1.8V} \
   CONFIG.PCW_MIO_30_PULLUP {disabled} \
   CONFIG.PCW_MIO_30_SLEW {slow} \
   CONFIG.PCW_MIO_31_DIRECTION {in} \
   CONFIG.PCW_MIO_31_IOTYPE {LVCMOS 1.8V} \
   CONFIG.PCW_MIO_31_PULLUP {disabled} \
   CONFIG.PCW_MIO_31_SLEW {slow} \
   CONFIG.PCW_MIO_32_DIRECTION {inout} \
   CONFIG.PCW_MIO_32_IOTYPE {LVCMOS 1.8V} \
   CONFIG.PCW_MIO_32_PULLUP {disabled} \
   CONFIG.PCW_MIO_32_SLEW {slow} \
   CONFIG.PCW_MIO_33_DIRECTION {inout} \
   CONFIG.PCW_MIO_33_IOTYPE {LVCMOS 1.8V} \
   CONFIG.PCW_MIO_33_PULLUP {disabled} \
   CONFIG.PCW_MIO_33_SLEW {slow} \
   CONFIG.PCW_MIO_34_DIRECTION {inout} \
   CONFIG.PCW_MIO_34_IOTYPE {LVCMOS 1.8V} \
   CONFIG.PCW_MIO_34_PULLUP {disabled} \
   CONFIG.PCW_MIO_34_SLEW {slow} \
   CONFIG.PCW_MIO_35_DIRECTION {inout} \
   CONFIG.PCW_MIO_35_IOTYPE {LVCMOS 1.8V} \
   CONFIG.PCW_MIO_35_PULLUP {disabled} \
   CONFIG.PCW_MIO_35_SLEW {slow} \
   CONFIG.PCW_MIO_36_DIRECTION {in} \
   CONFIG.PCW_MIO_36_IOTYPE {LVCMOS 1.8V} \
   CONFIG.PCW_MIO_36_PULLUP {disabled} \
   CONFIG.PCW_MIO_36_SLEW {slow} \
   CONFIG.PCW_MIO_37_DIRECTION {inout} \
   CONFIG.PCW_MIO_37_IOTYPE {LVCMOS 1.8V} \
   CONFIG.PCW_MIO_37_PULLUP {disabled} \
   CONFIG.PCW_MIO_37_SLEW {slow} \
   CONFIG.PCW_MIO_38_DIRECTION {inout} \
   CONFIG.PCW_MIO_38_IOTYPE {LVCMOS 1.8V} \
   CONFIG.PCW_MIO_38_PULLUP {disabled} \
   CONFIG.PCW_MIO_38_SLEW {slow} \
   CONFIG.PCW_MIO_39_DIRECTION {inout} \
   CONFIG.PCW_MIO_39_IOTYPE {LVCMOS 1.8V} \
   CONFIG.PCW_MIO_39_PULLUP {disabled} \
   CONFIG.PCW_MIO_39_SLEW {slow} \
   CONFIG.PCW_MIO_3_DIRECTION {inout} \
   CONFIG.PCW_MIO_3_IOTYPE {LVCMOS 3.3V} \
   CONFIG.PCW_MIO_3_PULLUP {disabled} \
   CONFIG.PCW_MIO_3_SLEW {slow} \
   CONFIG.PCW_MIO_40_DIRECTION {inout} \
   CONFIG.PCW_MIO_40_IOTYPE {LVCMOS 1.8V} \
   CONFIG.PCW_MIO_40_PULLUP {disabled} \
   CONFIG.PCW_MIO_40_SLEW {slow} \
   CONFIG.PCW_MIO_41_DIRECTION {inout} \
   CONFIG.PCW_MIO_41_IOTYPE {LVCMOS 1.8V} \
   CONFIG.PCW_MIO_41_PULLUP {disabled} \
   CONFIG.PCW_MIO_41_SLEW {slow} \
   CONFIG.PCW_MIO_42_DIRECTION {inout} \
   CONFIG.PCW_MIO_42_IOTYPE {LVCMOS 1.8V} \
   CONFIG.PCW_MIO_42_PULLUP {disabled} \
   CONFIG.PCW_MIO_42_SLEW {slow} \
   CONFIG.PCW_MIO_43_DIRECTION {inout} \
   CONFIG.PCW_MIO_43_IOTYPE {LVCMOS 1.8V} \
   CONFIG.PCW_MIO_43_PULLUP {disabled} \
   CONFIG.PCW_MIO_43_SLEW {slow} \
   CONFIG.PCW_MIO_44_DIRECTION {inout} \
   CONFIG.PCW_MIO_44_IOTYPE {LVCMOS 1.8V} \
   CONFIG.PCW_MIO_44_PULLUP {disabled} \
   CONFIG.PCW_MIO_44_SLEW {slow} \
   CONFIG.PCW_MIO_45_DIRECTION {inout} \
   CONFIG.PCW_MIO_45_IOTYPE {LVCMOS 1.8V} \
   CONFIG.PCW_MIO_45_PULLUP {disabled} \
   CONFIG.PCW_MIO_45_SLEW {slow} \
   CONFIG.PCW_MIO_46_DIRECTION {in} \
   CONFIG.PCW_MIO_46_IOTYPE {LVCMOS 1.8V} \
   CONFIG.PCW_MIO_46_PULLUP {disabled} \
   CONFIG.PCW_MIO_46_SLEW {slow} \
   CONFIG.PCW_MIO_47_DIRECTION {inout} \
   CONFIG.PCW_MIO_47_IOTYPE {LVCMOS 1.8V} \
   CONFIG.PCW_MIO_47_PULLUP {disabled} \
   CONFIG.PCW_MIO_47_SLEW {slow} \
   CONFIG.PCW_MIO_48_DIRECTION {out} \
   CONFIG.PCW_MIO_48_IOTYPE {LVCMOS 1.8V} \
   CONFIG.PCW_MIO_48_PULLUP {disabled} \
   CONFIG.PCW_MIO_48_SLEW {slow} \
   CONFIG.PCW_MIO_49_DIRECTION {in} \
   CONFIG.PCW_MIO_49_IOTYPE {LVCMOS 1.8V} \
   CONFIG.PCW_MIO_49_PULLUP {disabled} \
   CONFIG.PCW_MIO_49_SLEW {slow} \
   CONFIG.PCW_MIO_4_DIRECTION {inout} \
   CONFIG.PCW_MIO_4_IOTYPE {LVCMOS 3.3V} \
   CONFIG.PCW_MIO_4_PULLUP {disabled} \
   CONFIG.PCW_MIO_4_SLEW {slow} \
   CONFIG.PCW_MIO_50_DIRECTION {in} \
   CONFIG.PCW_MIO_50_IOTYPE {LVCMOS 1.8V} \
   CONFIG.PCW_MIO_50_PULLUP {disabled} \
   CONFIG.PCW_MIO_50_SLEW {slow} \
   CONFIG.PCW_MIO_51_DIRECTION {inout} \
   CONFIG.PCW_MIO_51_IOTYPE {LVCMOS 1.8V} \
   CONFIG.PCW_MIO_51_PULLUP {disabled} \
   CONFIG.PCW_MIO_51_SLEW {slow} \
   CONFIG.PCW_MIO_52_DIRECTION {out} \
   CONFIG.PCW_MIO_52_IOTYPE {LVCMOS 1.8V} \
   CONFIG.PCW_MIO_52_PULLUP {disabled} \
   CONFIG.PCW_MIO_52_SLEW {slow} \
   CONFIG.PCW_MIO_53_DIRECTION {inout} \
   CONFIG.PCW_MIO_53_IOTYPE {LVCMOS 1.8V} \
   CONFIG.PCW_MIO_53_PULLUP {disabled} \
   CONFIG.PCW_MIO_53_SLEW {slow} \
   CONFIG.PCW_MIO_5_DIRECTION {inout} \
   CONFIG.PCW_MIO_5_IOTYPE {LVCMOS 3.3V} \
   CONFIG.PCW_MIO_5_PULLUP {disabled} \
   CONFIG.PCW_MIO_5_SLEW {slow} \
   CONFIG.PCW_MIO_6_DIRECTION {out} \
   CONFIG.PCW_MIO_6_IOTYPE {LVCMOS 3.3V} \
   CONFIG.PCW_MIO_6_PULLUP {disabled} \
   CONFIG.PCW_MIO_6_SLEW {slow} \
   CONFIG.PCW_MIO_7_DIRECTION {out} \
   CONFIG.PCW_MIO_7_IOTYPE {LVCMOS 3.3V} \
   CONFIG.PCW_MIO_7_PULLUP {disabled} \
   CONFIG.PCW_MIO_7_SLEW {slow} \
   CONFIG.PCW_MIO_8_DIRECTION {out} \
   CONFIG.PCW_MIO_8_IOTYPE {LVCMOS 3.3V} \
   CONFIG.PCW_MIO_8_PULLUP {disabled} \
   CONFIG.PCW_MIO_8_SLEW {slow} \
   CONFIG.PCW_MIO_9_DIRECTION {inout} \
   CONFIG.PCW_MIO_9_IOTYPE {LVCMOS 3.3V} \
   CONFIG.PCW_MIO_9_PULLUP {disabled} \
   CONFIG.PCW_MIO_9_SLEW {slow} \
   CONFIG.PCW_MIO_PRIMITIVE {54} \
   CONFIG.PCW_MIO_TREE_PERIPHERALS {GPIO#Quad SPI Flash#Quad SPI Flash#Quad SPI Flash#Quad SPI Flash#Quad SPI Flash#Quad SPI Flash#USB Reset#Quad SPI Flash#GPIO#SD 1#SD 1#SD 1#SD 1#SD 1#SD 1#Enet 0#Enet 0#Enet 0#Enet 0#Enet 0#Enet 0#Enet 0#Enet 0#Enet 0#Enet 0#Enet 0#Enet 0#USB 0#USB 0#USB 0#USB 0#USB 0#USB 0#USB 0#USB 0#USB 0#USB 0#USB 0#USB 0#SD 0#SD 0#SD 0#SD 0#SD 0#SD 0#SD 0#GPIO#UART 1#UART 1#SD 0#GPIO#Enet 0#Enet 0} \
   CONFIG.PCW_MIO_TREE_SIGNALS {gpio[0]#qspi0_ss_b#qspi0_io[0]#qspi0_io[1]#qspi0_io[2]#qspi0_io[3]/HOLD_B#qspi0_sclk#reset#qspi_fbclk#gpio[9]#data[0]#cmd#clk#data[1]#data[2]#data[3]#tx_clk#txd[0]#txd[1]#txd[2]#txd[3]#tx_ctl#rx_clk#rxd[0]#rxd[1]#rxd[2]#rxd[3]#rx_ctl#data[4]#dir#stp#nxt#data[0]#data[1]#data[2]#data[3]#clk#data[5]#data[6]#data[7]#clk#cmd#data[0]#data[1]#data[2]#data[3]#cd#gpio[47]#tx#rx#wp#gpio[51]#mdc#mdio} \
   CONFIG.PCW_M_AXI_GP0_ENABLE_STATIC_REMAP {0} \
   CONFIG.PCW_M_AXI_GP0_ID_WIDTH {12} \
   CONFIG.PCW_M_AXI_GP0_SUPPORT_NARROW_BURST {0} \
   CONFIG.PCW_M_AXI_GP0_THREAD_ID_WIDTH {12} \
   CONFIG.PCW_M_AXI_GP1_ENABLE_STATIC_REMAP {0} \
   CONFIG.PCW_M_AXI_GP1_ID_WIDTH {12} \
   CONFIG.PCW_M_AXI_GP1_SUPPORT_NARROW_BURST {0} \
   CONFIG.PCW_M_AXI_GP1_THREAD_ID_WIDTH {12} \
   CONFIG.PCW_NAND_CYCLES_T_AR {0} \
   CONFIG.PCW_NAND_CYCLES_T_CLR {0} \
   CONFIG.PCW_NAND_CYCLES_T_RC {2} \
   CONFIG.PCW_NAND_CYCLES_T_REA {1} \
   CONFIG.PCW_NAND_CYCLES_T_RR {0} \
   CONFIG.PCW_NAND_CYCLES_T_WC {2} \
   CONFIG.PCW_NAND_CYCLES_T_WP {1} \
   CONFIG.PCW_NAND_GRP_D8_ENABLE {0} \
   CONFIG.PCW_NAND_PERIPHERAL_ENABLE {0} \
   CONFIG.PCW_NOR_CS0_T_CEOE {1} \
   CONFIG.PCW_NOR_CS0_T_PC {1} \
   CONFIG.PCW_NOR_CS0_T_RC {2} \
   CONFIG.PCW_NOR_CS0_T_TR {1} \
   CONFIG.PCW_NOR_CS0_T_WC {2} \
   CONFIG.PCW_NOR_CS0_T_WP {1} \
   CONFIG.PCW_NOR_CS0_WE_TIME {2} \
   CONFIG.PCW_NOR_CS1_T_CEOE {1} \
   CONFIG.PCW_NOR_CS1_T_PC {1} \
   CONFIG.PCW_NOR_CS1_T_RC {2} \
   CONFIG.PCW_NOR_CS1_T_TR {1} \
   CONFIG.PCW_NOR_CS1_T_WC {2} \
   CONFIG.PCW_NOR_CS1_T_WP {1} \
   CONFIG.PCW_NOR_CS1_WE_TIME {2} \
   CONFIG.PCW_NOR_GRP_A25_ENABLE {0} \
   CONFIG.PCW_NOR_GRP_CS0_ENABLE {0} \
   CONFIG.PCW_NOR_GRP_CS1_ENABLE {0} \
   CONFIG.PCW_NOR_GRP_SRAM_CS0_ENABLE {0} \
   CONFIG.PCW_NOR_GRP_SRAM_CS1_ENABLE {0} \
   CONFIG.PCW_NOR_GRP_SRAM_INT_ENABLE {0} \
   CONFIG.PCW_NOR_PERIPHERAL_ENABLE {0} \
   CONFIG.PCW_NOR_SRAM_CS0_T_CEOE {1} \
   CONFIG.PCW_NOR_SRAM_CS0_T_PC {1} \
   CONFIG.PCW_NOR_SRAM_CS0_T_RC {2} \
   CONFIG.PCW_NOR_SRAM_CS0_T_TR {1} \
   CONFIG.PCW_NOR_SRAM_CS0_T_WC {2} \
   CONFIG.PCW_NOR_SRAM_CS0_T_WP {1} \
   CONFIG.PCW_NOR_SRAM_CS0_WE_TIME {2} \
   CONFIG.PCW_NOR_SRAM_CS1_T_CEOE {1} \
   CONFIG.PCW_NOR_SRAM_CS1_T_PC {1} \
   CONFIG.PCW_NOR_SRAM_CS1_T_RC {2} \
   CONFIG.PCW_NOR_SRAM_CS1_T_TR {1} \
   CONFIG.PCW_NOR_SRAM_CS1_T_WC {2} \
   CONFIG.PCW_NOR_SRAM_CS1_T_WP {1} \
   CONFIG.PCW_NOR_SRAM_CS1_WE_TIME {2} \
   CONFIG.PCW_OVERRIDE_BASIC_CLOCK {0} \
   CONFIG.PCW_P2F_CAN0_INTR {0} \
   CONFIG.PCW_P2F_CAN1_INTR {0} \
   CONFIG.PCW_P2F_CTI_INTR {0} \
   CONFIG.PCW_P2F_DMAC0_INTR {0} \
   CONFIG.PCW_P2F_DMAC1_INTR {0} \
   CONFIG.PCW_P2F_DMAC2_INTR {0} \
   CONFIG.PCW_P2F_DMAC3_INTR {0} \
   CONFIG.PCW_P2F_DMAC4_INTR {0} \
   CONFIG.PCW_P2F_DMAC5_INTR {0} \
   CONFIG.PCW_P2F_DMAC6_INTR {0} \
   CONFIG.PCW_P2F_DMAC7_INTR {0} \
   CONFIG.PCW_P2F_DMAC_ABORT_INTR {0} \
   CONFIG.PCW_P2F_ENET0_INTR {0} \
   CONFIG.PCW_P2F_ENET1_INTR {0} \
   CONFIG.PCW_P2F_GPIO_INTR {0} \
   CONFIG.PCW_P2F_I2C0_INTR {0} \
   CONFIG.PCW_P2F_I2C1_INTR {0} \
   CONFIG.PCW_P2F_QSPI_INTR {0} \
   CONFIG.PCW_P2F_SDIO0_INTR {0} \
   CONFIG.PCW_P2F_SDIO1_INTR {0} \
   CONFIG.PCW_P2F_SMC_INTR {0} \
   CONFIG.PCW_P2F_SPI0_INTR {0} \
   CONFIG.PCW_P2F_SPI1_INTR {0} \
   CONFIG.PCW_P2F_UART0_INTR {0} \
   CONFIG.PCW_P2F_UART1_INTR {0} \
   CONFIG.PCW_P2F_USB0_INTR {0} \
   CONFIG.PCW_P2F_USB1_INTR {0} \
   CONFIG.PCW_PACKAGE_DDR_BOARD_DELAY0 {0.361} \
   CONFIG.PCW_PACKAGE_DDR_BOARD_DELAY1 {0.351} \
   CONFIG.PCW_PACKAGE_DDR_BOARD_DELAY2 {0.386} \
   CONFIG.PCW_PACKAGE_DDR_BOARD_DELAY3 {0.391} \
   CONFIG.PCW_PACKAGE_DDR_DQS_TO_CLK_DELAY_0 {-0.112} \
   CONFIG.PCW_PACKAGE_DDR_DQS_TO_CLK_DELAY_1 {-0.093} \
   CONFIG.PCW_PACKAGE_DDR_DQS_TO_CLK_DELAY_2 {0.019} \
   CONFIG.PCW_PACKAGE_DDR_DQS_TO_CLK_DELAY_3 {0.009} \
   CONFIG.PCW_PACKAGE_NAME {clg400} \
   CONFIG.PCW_PCAP_PERIPHERAL_CLKSRC {1} \
   CONFIG.PCW_PCAP_PERIPHERAL_DIVISOR0 {5} \
   CONFIG.PCW_PCAP_PERIPHERAL_FREQMHZ {200} \
   CONFIG.PCW_PERIPHERAL_BOARD_PRESET {part0} \
   CONFIG.PCW_PJTAG_PERIPHERAL_ENABLE {0} \
   CONFIG.PCW_PLL_BYPASSMODE_ENABLE {0} \
   CONFIG.PCW_PRESET_BANK0_VOLTAGE {LVCMOS 3.3V} \
   CONFIG.PCW_PRESET_BANK1_VOLTAGE {LVCMOS 1.8V} \
   CONFIG.PCW_PS7_SI_REV {PRODUCTION} \
   CONFIG.PCW_QSPI_GRP_FBCLK_ENABLE {1} \
   CONFIG.PCW_QSPI_GRP_FBCLK_IO {MIO 8} \
   CONFIG.PCW_QSPI_GRP_IO1_ENABLE {0} \
   CONFIG.PCW_QSPI_GRP_SINGLE_SS_ENABLE {1} \
   CONFIG.PCW_QSPI_GRP_SINGLE_SS_IO {MIO 1 .. 6} \
   CONFIG.PCW_QSPI_GRP_SS1_ENABLE {0} \
   CONFIG.PCW_QSPI_INTERNAL_HIGHADDRESS {0xFCFFFFFF} \
   CONFIG.PCW_QSPI_PERIPHERAL_CLKSRC {IO PLL} \
   CONFIG.PCW_QSPI_PERIPHERAL_DIVISOR0 {5} \
   CONFIG.PCW_QSPI_PERIPHERAL_ENABLE {1} \
   CONFIG.PCW_QSPI_PERIPHERAL_FREQMHZ {200} \
   CONFIG.PCW_QSPI_QSPI_IO {MIO 1 .. 6} \
   CONFIG.PCW_SD0_GRP_CD_ENABLE {1} \
   CONFIG.PCW_SD0_GRP_CD_IO {MIO 46} \
   CONFIG.PCW_SD0_GRP_POW_ENABLE {0} \
   CONFIG.PCW_SD0_GRP_WP_ENABLE {1} \
   CONFIG.PCW_SD0_GRP_WP_IO {MIO 50} \
   CONFIG.PCW_SD0_PERIPHERAL_ENABLE {1} \
   CONFIG.PCW_SD0_SD0_IO {MIO 40 .. 45} \
   CONFIG.PCW_SD1_GRP_CD_ENABLE {1} \
   CONFIG.PCW_SD1_GRP_CD_IO {EMIO} \
   CONFIG.PCW_SD1_GRP_POW_ENABLE {0} \
   CONFIG.PCW_SD1_GRP_WP_ENABLE {0} \
   CONFIG.PCW_SD1_PERIPHERAL_ENABLE {1} \
   CONFIG.PCW_SD1_SD1_IO {MIO 10 .. 15} \
   CONFIG.PCW_SDIO0_BASEADDR {0xE0100000} \
   CONFIG.PCW_SDIO0_HIGHADDR {0xE0100FFF} \
   CONFIG.PCW_SDIO1_BASEADDR {0xE0101000} \
   CONFIG.PCW_SDIO1_HIGHADDR {0xE0101FFF} \
   CONFIG.PCW_SDIO_PERIPHERAL_CLKSRC {IO PLL} \
   CONFIG.PCW_SDIO_PERIPHERAL_DIVISOR0 {20} \
   CONFIG.PCW_SDIO_PERIPHERAL_FREQMHZ {50} \
   CONFIG.PCW_SDIO_PERIPHERAL_VALID {1} \
   CONFIG.PCW_SINGLE_QSPI_DATA_MODE {x4} \
   CONFIG.PCW_SMC_CYCLE_T0 {NA} \
   CONFIG.PCW_SMC_CYCLE_T1 {NA} \
   CONFIG.PCW_SMC_CYCLE_T2 {NA} \
   CONFIG.PCW_SMC_CYCLE_T3 {NA} \
   CONFIG.PCW_SMC_CYCLE_T4 {NA} \
   CONFIG.PCW_SMC_CYCLE_T5 {NA} \
   CONFIG.PCW_SMC_CYCLE_T6 {NA} \
   CONFIG.PCW_SMC_PERIPHERAL_CLKSRC {IO PLL} \
   CONFIG.PCW_SMC_PERIPHERAL_DIVISOR0 {1} \
   CONFIG.PCW_SMC_PERIPHERAL_FREQMHZ {100} \
   CONFIG.PCW_SMC_PERIPHERAL_VALID {0} \
   CONFIG.PCW_SPI0_BASEADDR {0xE0006000} \
   CONFIG.PCW_SPI0_GRP_SS0_ENABLE {0} \
   CONFIG.PCW_SPI0_GRP_SS1_ENABLE {0} \
   CONFIG.PCW_SPI0_GRP_SS2_ENABLE {0} \
   CONFIG.PCW_SPI0_HIGHADDR {0xE0006FFF} \
   CONFIG.PCW_SPI0_PERIPHERAL_ENABLE {0} \
   CONFIG.PCW_SPI1_BASEADDR {0xE0007000} \
   CONFIG.PCW_SPI1_GRP_SS0_ENABLE {0} \
   CONFIG.PCW_SPI1_GRP_SS1_ENABLE {0} \
   CONFIG.PCW_SPI1_GRP_SS2_ENABLE {0} \
   CONFIG.PCW_SPI1_HIGHADDR {0xE0007FFF} \
   CONFIG.PCW_SPI1_PERIPHERAL_ENABLE {0} \
   CONFIG.PCW_SPI_PERIPHERAL_CLKSRC {IO PLL} \
   CONFIG.PCW_SPI_PERIPHERAL_DIVISOR0 {1} \
   CONFIG.PCW_SPI_PERIPHERAL_FREQMHZ {166.666666} \
   CONFIG.PCW_SPI_PERIPHERAL_VALID {0} \
   CONFIG.PCW_S_AXI_ACP_ARUSER_VAL {31} \
   CONFIG.PCW_S_AXI_ACP_AWUSER_VAL {31} \
   CONFIG.PCW_S_AXI_ACP_ID_WIDTH {3} \
   CONFIG.PCW_S_AXI_GP0_ID_WIDTH {6} \
   CONFIG.PCW_S_AXI_GP1_ID_WIDTH {6} \
   CONFIG.PCW_S_AXI_HP0_DATA_WIDTH {32} \
   CONFIG.PCW_S_AXI_HP0_ID_WIDTH {6} \
   CONFIG.PCW_S_AXI_HP1_DATA_WIDTH {64} \
   CONFIG.PCW_S_AXI_HP1_ID_WIDTH {6} \
   CONFIG.PCW_S_AXI_HP2_DATA_WIDTH {64} \
   CONFIG.PCW_S_AXI_HP2_ID_WIDTH {6} \
   CONFIG.PCW_S_AXI_HP3_DATA_WIDTH {64} \
   CONFIG.PCW_S_AXI_HP3_ID_WIDTH {6} \
   CONFIG.PCW_TPIU_PERIPHERAL_CLKSRC {External} \
   CONFIG.PCW_TPIU_PERIPHERAL_DIVISOR0 {1} \
   CONFIG.PCW_TPIU_PERIPHERAL_FREQMHZ {200} \
   CONFIG.PCW_TRACE_BUFFER_CLOCK_DELAY {12} \
   CONFIG.PCW_TRACE_BUFFER_FIFO_SIZE {128} \
   CONFIG.PCW_TRACE_GRP_16BIT_ENABLE {0} \
   CONFIG.PCW_TRACE_GRP_2BIT_ENABLE {0} \
   CONFIG.PCW_TRACE_GRP_32BIT_ENABLE {0} \
   CONFIG.PCW_TRACE_GRP_4BIT_ENABLE {0} \
   CONFIG.PCW_TRACE_GRP_8BIT_ENABLE {0} \
   CONFIG.PCW_TRACE_INTERNAL_WIDTH {32} \
   CONFIG.PCW_TRACE_PERIPHERAL_ENABLE {0} \
   CONFIG.PCW_TRACE_PIPELINE_WIDTH {8} \
   CONFIG.PCW_TTC0_BASEADDR {0xE0104000} \
   CONFIG.PCW_TTC0_CLK0_PERIPHERAL_CLKSRC {CPU_1X} \
   CONFIG.PCW_TTC0_CLK0_PERIPHERAL_DIVISOR0 {1} \
   CONFIG.PCW_TTC0_CLK0_PERIPHERAL_FREQMHZ {133.333333} \
   CONFIG.PCW_TTC0_CLK1_PERIPHERAL_CLKSRC {CPU_1X} \
   CONFIG.PCW_TTC0_CLK1_PERIPHERAL_DIVISOR0 {1} \
   CONFIG.PCW_TTC0_CLK1_PERIPHERAL_FREQMHZ {133.333333} \
   CONFIG.PCW_TTC0_CLK2_PERIPHERAL_CLKSRC {CPU_1X} \
   CONFIG.PCW_TTC0_CLK2_PERIPHERAL_DIVISOR0 {1} \
   CONFIG.PCW_TTC0_CLK2_PERIPHERAL_FREQMHZ {133.333333} \
   CONFIG.PCW_TTC0_HIGHADDR {0xE0104fff} \
   CONFIG.PCW_TTC0_PERIPHERAL_ENABLE {1} \
   CONFIG.PCW_TTC0_TTC0_IO {EMIO} \
   CONFIG.PCW_TTC1_BASEADDR {0xE0105000} \
   CONFIG.PCW_TTC1_CLK0_PERIPHERAL_CLKSRC {CPU_1X} \
   CONFIG.PCW_TTC1_CLK0_PERIPHERAL_DIVISOR0 {1} \
   CONFIG.PCW_TTC1_CLK0_PERIPHERAL_FREQMHZ {133.333333} \
   CONFIG.PCW_TTC1_CLK1_PERIPHERAL_CLKSRC {CPU_1X} \
   CONFIG.PCW_TTC1_CLK1_PERIPHERAL_DIVISOR0 {1} \
   CONFIG.PCW_TTC1_CLK1_PERIPHERAL_FREQMHZ {133.333333} \
   CONFIG.PCW_TTC1_CLK2_PERIPHERAL_CLKSRC {CPU_1X} \
   CONFIG.PCW_TTC1_CLK2_PERIPHERAL_DIVISOR0 {1} \
   CONFIG.PCW_TTC1_CLK2_PERIPHERAL_FREQMHZ {133.333333} \
   CONFIG.PCW_TTC1_HIGHADDR {0xE0105fff} \
   CONFIG.PCW_TTC1_PERIPHERAL_ENABLE {0} \
   CONFIG.PCW_TTC_PERIPHERAL_FREQMHZ {50} \
   CONFIG.PCW_UART0_BASEADDR {0xE0000000} \
   CONFIG.PCW_UART0_BAUD_RATE {115200} \
   CONFIG.PCW_UART0_GRP_FULL_ENABLE {0} \
   CONFIG.PCW_UART0_HIGHADDR {0xE0000FFF} \
   CONFIG.PCW_UART0_PERIPHERAL_ENABLE {1} \
   CONFIG.PCW_UART0_UART0_IO {EMIO} \
   CONFIG.PCW_UART1_BASEADDR {0xE0001000} \
   CONFIG.PCW_UART1_BAUD_RATE {115200} \
   CONFIG.PCW_UART1_GRP_FULL_ENABLE {0} \
   CONFIG.PCW_UART1_HIGHADDR {0xE0001FFF} \
   CONFIG.PCW_UART1_PERIPHERAL_ENABLE {1} \
   CONFIG.PCW_UART1_UART1_IO {MIO 48 .. 49} \
   CONFIG.PCW_UART_PERIPHERAL_CLKSRC {IO PLL} \
   CONFIG.PCW_UART_PERIPHERAL_DIVISOR0 {20} \
   CONFIG.PCW_UART_PERIPHERAL_FREQMHZ {50} \
   CONFIG.PCW_UART_PERIPHERAL_VALID {1} \
   CONFIG.PCW_UIPARAM_ACT_DDR_FREQ_MHZ {533.333374} \
   CONFIG.PCW_UIPARAM_DDR_ADV_ENABLE {0} \
   CONFIG.PCW_UIPARAM_DDR_AL {0} \
   CONFIG.PCW_UIPARAM_DDR_BANK_ADDR_COUNT {3} \
   CONFIG.PCW_UIPARAM_DDR_BL {8} \
   CONFIG.PCW_UIPARAM_DDR_BOARD_DELAY0 {0.294} \
   CONFIG.PCW_UIPARAM_DDR_BOARD_DELAY1 {0.298} \
   CONFIG.PCW_UIPARAM_DDR_BOARD_DELAY2 {0.338} \
   CONFIG.PCW_UIPARAM_DDR_BOARD_DELAY3 {0.334} \
   CONFIG.PCW_UIPARAM_DDR_BUS_WIDTH {32 Bit} \
   CONFIG.PCW_UIPARAM_DDR_CL {7} \
   CONFIG.PCW_UIPARAM_DDR_CLOCK_0_LENGTH_MM {39.7} \
   CONFIG.PCW_UIPARAM_DDR_CLOCK_0_PACKAGE_LENGTH {54.563} \
   CONFIG.PCW_UIPARAM_DDR_CLOCK_0_PROPOGATION_DELAY {160} \
   CONFIG.PCW_UIPARAM_DDR_CLOCK_1_LENGTH_MM {39.7} \
   CONFIG.PCW_UIPARAM_DDR_CLOCK_1_PACKAGE_LENGTH {54.563} \
   CONFIG.PCW_UIPARAM_DDR_CLOCK_1_PROPOGATION_DELAY {160} \
   CONFIG.PCW_UIPARAM_DDR_CLOCK_2_LENGTH_MM {54.14} \
   CONFIG.PCW_UIPARAM_DDR_CLOCK_2_PACKAGE_LENGTH {54.563} \
   CONFIG.PCW_UIPARAM_DDR_CLOCK_2_PROPOGATION_DELAY {160} \
   CONFIG.PCW_UIPARAM_DDR_CLOCK_3_LENGTH_MM {54.14} \
   CONFIG.PCW_UIPARAM_DDR_CLOCK_3_PACKAGE_LENGTH {54.563} \
   CONFIG.PCW_UIPARAM_DDR_CLOCK_3_PROPOGATION_DELAY {160} \
   CONFIG.PCW_UIPARAM_DDR_CLOCK_STOP_EN {0} \
   CONFIG.PCW_UIPARAM_DDR_COL_ADDR_COUNT {10} \
   CONFIG.PCW_UIPARAM_DDR_CWL {6} \
   CONFIG.PCW_UIPARAM_DDR_DEVICE_CAPACITY {4096 MBits} \
   CONFIG.PCW_UIPARAM_DDR_DQS_0_LENGTH_MM {50.05} \
   CONFIG.PCW_UIPARAM_DDR_DQS_0_PACKAGE_LENGTH {101.239} \
   CONFIG.PCW_UIPARAM_DDR_DQS_0_PROPOGATION_DELAY {160} \
   CONFIG.PCW_UIPARAM_DDR_DQS_1_LENGTH_MM {50.43} \
   CONFIG.PCW_UIPARAM_DDR_DQS_1_PACKAGE_LENGTH {79.5025} \
   CONFIG.PCW_UIPARAM_DDR_DQS_1_PROPOGATION_DELAY {160} \
   CONFIG.PCW_UIPARAM_DDR_DQS_2_LENGTH_MM {50.10} \
   CONFIG.PCW_UIPARAM_DDR_DQS_2_PACKAGE_LENGTH {60.536} \
   CONFIG.PCW_UIPARAM_DDR_DQS_2_PROPOGATION_DELAY {160} \
   CONFIG.PCW_UIPARAM_DDR_DQS_3_LENGTH_MM {50.01} \
   CONFIG.PCW_UIPARAM_DDR_DQS_3_PACKAGE_LENGTH {71.7715} \
   CONFIG.PCW_UIPARAM_DDR_DQS_3_PROPOGATION_DELAY {160} \
   CONFIG.PCW_UIPARAM_DDR_DQS_TO_CLK_DELAY_0 {-0.073} \
   CONFIG.PCW_UIPARAM_DDR_DQS_TO_CLK_DELAY_1 {-0.072} \
   CONFIG.PCW_UIPARAM_DDR_DQS_TO_CLK_DELAY_2 {0.024} \
   CONFIG.PCW_UIPARAM_DDR_DQS_TO_CLK_DELAY_3 {0.023} \
   CONFIG.PCW_UIPARAM_DDR_DQ_0_LENGTH_MM {49.59} \
   CONFIG.PCW_UIPARAM_DDR_DQ_0_PACKAGE_LENGTH {104.5365} \
   CONFIG.PCW_UIPARAM_DDR_DQ_0_PROPOGATION_DELAY {160} \
   CONFIG.PCW_UIPARAM_DDR_DQ_1_LENGTH_MM {51.74} \
   CONFIG.PCW_UIPARAM_DDR_DQ_1_PACKAGE_LENGTH {70.676} \
   CONFIG.PCW_UIPARAM_DDR_DQ_1_PROPOGATION_DELAY {160} \
   CONFIG.PCW_UIPARAM_DDR_DQ_2_LENGTH_MM {50.32} \
   CONFIG.PCW_UIPARAM_DDR_DQ_2_PACKAGE_LENGTH {59.1615} \
   CONFIG.PCW_UIPARAM_DDR_DQ_2_PROPOGATION_DELAY {160} \
   CONFIG.PCW_UIPARAM_DDR_DQ_3_LENGTH_MM {48.55} \
   CONFIG.PCW_UIPARAM_DDR_DQ_3_PACKAGE_LENGTH {81.319} \
   CONFIG.PCW_UIPARAM_DDR_DQ_3_PROPOGATION_DELAY {160} \
   CONFIG.PCW_UIPARAM_DDR_DRAM_WIDTH {16 Bits} \
   CONFIG.PCW_UIPARAM_DDR_ECC {Disabled} \
   CONFIG.PCW_UIPARAM_DDR_ENABLE {1} \
   CONFIG.PCW_UIPARAM_DDR_FREQ_MHZ {533.333333} \
   CONFIG.PCW_UIPARAM_DDR_HIGH_TEMP {Normal (0-85)} \
   CONFIG.PCW_UIPARAM_DDR_MEMORY_TYPE {DDR 3} \
   CONFIG.PCW_UIPARAM_DDR_PARTNO {MT41K256M16 RE-125} \
   CONFIG.PCW_UIPARAM_DDR_ROW_ADDR_COUNT {15} \
   CONFIG.PCW_UIPARAM_DDR_SPEED_BIN {DDR3_1066F} \
   CONFIG.PCW_UIPARAM_DDR_TRAIN_DATA_EYE {1} \
   CONFIG.PCW_UIPARAM_DDR_TRAIN_READ_GATE {1} \
   CONFIG.PCW_UIPARAM_DDR_TRAIN_WRITE_LEVEL {1} \
   CONFIG.PCW_UIPARAM_DDR_T_FAW {40.0} \
   CONFIG.PCW_UIPARAM_DDR_T_RAS_MIN {35.0} \
   CONFIG.PCW_UIPARAM_DDR_T_RC {48.75} \
   CONFIG.PCW_UIPARAM_DDR_T_RCD {7} \
   CONFIG.PCW_UIPARAM_DDR_T_RP {7} \
   CONFIG.PCW_UIPARAM_DDR_USE_INTERNAL_VREF {1} \
   CONFIG.PCW_UIPARAM_GENERATE_SUMMARY {NA} \
   CONFIG.PCW_USB0_BASEADDR {0xE0102000} \
   CONFIG.PCW_USB0_HIGHADDR {0xE0102fff} \
   CONFIG.PCW_USB0_PERIPHERAL_ENABLE {1} \
   CONFIG.PCW_USB0_PERIPHERAL_FREQMHZ {60} \
   CONFIG.PCW_USB0_RESET_ENABLE {1} \
   CONFIG.PCW_USB0_RESET_IO {MIO 7} \
   CONFIG.PCW_USB0_USB0_IO {MIO 28 .. 39} \
   CONFIG.PCW_USB1_BASEADDR {0xE0103000} \
   CONFIG.PCW_USB1_HIGHADDR {0xE0103fff} \
   CONFIG.PCW_USB1_PERIPHERAL_ENABLE {0} \
   CONFIG.PCW_USB1_PERIPHERAL_FREQMHZ {60} \
   CONFIG.PCW_USB1_RESET_ENABLE {0} \
   CONFIG.PCW_USB_RESET_ENABLE {1} \
   CONFIG.PCW_USB_RESET_POLARITY {Active Low} \
   CONFIG.PCW_USB_RESET_SELECT {Share reset pin} \
   CONFIG.PCW_USE_AXI_FABRIC_IDLE {0} \
   CONFIG.PCW_USE_AXI_NONSECURE {0} \
   CONFIG.PCW_USE_CORESIGHT {0} \
   CONFIG.PCW_USE_CROSS_TRIGGER {0} \
   CONFIG.PCW_USE_CR_FABRIC {1} \
   CONFIG.PCW_USE_DDR_BYPASS {0} \
   CONFIG.PCW_USE_DEBUG {0} \
   CONFIG.PCW_USE_DEFAULT_ACP_USER_VAL {1} \
   CONFIG.PCW_USE_DMA0 {0} \
   CONFIG.PCW_USE_DMA1 {0} \
   CONFIG.PCW_USE_DMA2 {0} \
   CONFIG.PCW_USE_DMA3 {0} \
   CONFIG.PCW_USE_EXPANDED_IOP {0} \
   CONFIG.PCW_USE_EXPANDED_PS_SLCR_REGISTERS {0} \
   CONFIG.PCW_USE_FABRIC_INTERRUPT {1} \
   CONFIG.PCW_USE_HIGH_OCM {0} \
   CONFIG.PCW_USE_M_AXI_GP0 {1} \
   CONFIG.PCW_USE_M_AXI_GP1 {0} \
   CONFIG.PCW_USE_PROC_EVENT_BUS {0} \
   CONFIG.PCW_USE_PS_SLCR_REGISTERS {0} \
   CONFIG.PCW_USE_S_AXI_ACP {0} \
   CONFIG.PCW_USE_S_AXI_GP0 {0} \
   CONFIG.PCW_USE_S_AXI_GP1 {0} \
   CONFIG.PCW_USE_S_AXI_HP0 {1} \
   CONFIG.PCW_USE_S_AXI_HP1 {0} \
   CONFIG.PCW_USE_S_AXI_HP2 {0} \
   CONFIG.PCW_USE_S_AXI_HP3 {0} \
   CONFIG.PCW_USE_TRACE {0} \
   CONFIG.PCW_USE_TRACE_DATA_EDGE_DETECTOR {0} \
   CONFIG.PCW_VALUE_SILVERSION {3} \
   CONFIG.PCW_WDT_PERIPHERAL_CLKSRC {CPU_1X} \
   CONFIG.PCW_WDT_PERIPHERAL_DIVISOR0 {1} \
   CONFIG.PCW_WDT_PERIPHERAL_ENABLE {0} \
   CONFIG.PCW_WDT_PERIPHERAL_FREQMHZ {133.333333} \
 ] $azynq_0

  # Create instance: ddc
  create_hier_cell_ddc [current_bd_instance .] ddc

  # Create instance: microblaze_mcs_ppu
  create_hier_cell_microblaze_mcs_ppu [current_bd_instance .] microblaze_mcs_ppu

  # Create instance: microblaze_ppu
  create_hier_cell_microblaze_ppu [current_bd_instance .] microblaze_ppu

  # Create instance: proc_sys_reset_0, and set properties
  set proc_sys_reset_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:proc_sys_reset:5.0 proc_sys_reset_0 ]

  # Create instance: util_vector_logic_0, and set properties
  set util_vector_logic_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:util_vector_logic:2.0 util_vector_logic_0 ]
  set_property -dict [ list \
   CONFIG.C_OPERATION {not} \
   CONFIG.C_SIZE {1} \
   CONFIG.LOGO_FILE {data/sym_notgate.png} \
 ] $util_vector_logic_0

  # Create instance: xlconstant_0, and set properties
  set xlconstant_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlconstant:1.1 xlconstant_0 ]
  set_property -dict [ list \
   CONFIG.CONST_VAL {0} \
 ] $xlconstant_0

  # Create instance: xlconstant_1, and set properties
  set xlconstant_1 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlconstant:1.1 xlconstant_1 ]
  set_property -dict [ list \
   CONFIG.CONST_VAL {0} \
   CONFIG.CONST_WIDTH {1} \
 ] $xlconstant_1

  # Create instance: zynq_gpio, and set properties
  set zynq_gpio [ create_bd_cell -type ip -vlnv xilinx.com:ip:axi_gpio:2.0 zynq_gpio ]
  set_property -dict [ list \
   CONFIG.C_ALL_OUTPUTS {1} \
   CONFIG.C_GPIO_WIDTH {1} \
 ] $zynq_gpio

  # Create interface connections
  connect_bd_intf_net -intf_net ADC_LTC2207_M_AXIS [get_bd_intf_pins ADC_LTC2207/M_AXIS] [get_bd_intf_pins ddc/S_AXIS_DATA]
  connect_bd_intf_net -intf_net S00_AXI_1 [get_bd_intf_pins axi_interconnect_1/M00_AXI] [get_bd_intf_pins microblaze_ppu/S00_AXI]
  connect_bd_intf_net -intf_net axi_interconnect_0_M00_AXI [get_bd_intf_pins DDS_AD9951/S00_AXI] [get_bd_intf_pins axi_interconnect_0/M00_AXI]
  connect_bd_intf_net -intf_net axi_interconnect_0_M01_AXI [get_bd_intf_pins ADC_LTC2207/S_AXI] [get_bd_intf_pins axi_interconnect_0/M01_AXI]
  connect_bd_intf_net -intf_net axi_interconnect_0_M02_AXI [get_bd_intf_pins axi_interconnect_0/M02_AXI] [get_bd_intf_pins ddc/S_AXI]
  connect_bd_intf_net -intf_net axi_interconnect_0_M03_AXI [get_bd_intf_pins TTL/S_AXI] [get_bd_intf_pins axi_interconnect_0/M03_AXI]
  connect_bd_intf_net -intf_net axi_interconnect_1_M01_AXI [get_bd_intf_pins axi_interconnect_1/M01_AXI] [get_bd_intf_pins zynq_gpio/S_AXI]
  connect_bd_intf_net -intf_net axi_protocol_converter_0_M_AXI [get_bd_intf_pins axi_protocol_converter_0/M_AXI] [get_bd_intf_pins azynq_0/S_AXI_HP0]
  connect_bd_intf_net -intf_net azynq_0_M_AXI_GP0 [get_bd_intf_pins axi_interconnect_1/S00_AXI] [get_bd_intf_pins azynq_0/M_AXI_GP0]
  connect_bd_intf_net -intf_net ddc_M_AXIS [get_bd_intf_pins ddc/M_AXIS] [get_bd_intf_pins microblaze_ppu/S2_AXIS]
  connect_bd_intf_net -intf_net ddc_M_AXI_S2MM [get_bd_intf_pins axi_protocol_converter_0/S_AXI] [get_bd_intf_pins ddc/M_AXI_S2MM]
  connect_bd_intf_net -intf_net microblaze_ppu_M_AXI_out [get_bd_intf_pins axi_interconnect_0/S00_AXI] [get_bd_intf_pins microblaze_ppu/M_AXI_out]
  connect_bd_intf_net -intf_net processing_system7_0_DDR [get_bd_intf_ports DDR] [get_bd_intf_pins azynq_0/DDR]
  connect_bd_intf_net -intf_net processing_system7_0_FIXED_IO [get_bd_intf_ports FIXED_IO] [get_bd_intf_pins azynq_0/FIXED_IO]

  # Create port connections
  connect_bd_net -net ACLK_1 [get_bd_pins ADC_LTC2207/m_axis_aclk] [get_bd_pins ADC_LTC2207/s_axi_aclk] [get_bd_pins DDS_AD9951/ACLK] [get_bd_pins DDS_AD9951/P_CLK] [get_bd_pins TTL/s_axi_aclk] [get_bd_pins axi_interconnect_0/ACLK] [get_bd_pins axi_interconnect_0/M00_ACLK] [get_bd_pins axi_interconnect_0/M01_ACLK] [get_bd_pins axi_interconnect_0/M02_ACLK] [get_bd_pins axi_interconnect_0/M03_ACLK] [get_bd_pins axi_interconnect_0/S00_ACLK] [get_bd_pins axi_protocol_converter_0/aclk] [get_bd_pins ddc/CLK] [get_bd_pins microblaze_ppu/aclk_out]
  connect_bd_net -net ADC_CLKOUT_P_1 [get_bd_ports ADC_CLKOUT_N] [get_bd_pins ADC_LTC2207/ADC_CLKOUT_N]
  connect_bd_net -net ADC_DATA_1 [get_bd_ports ADC_DATA] [get_bd_pins ADC_LTC2207/ADC_DATA]
  connect_bd_net -net ADC_LTC2207_ADC_DITH [get_bd_ports ADC_DITH] [get_bd_pins ADC_LTC2207/ADC_DITH]
  set_property -dict [ list \
HDL_ATTRIBUTE.MARK_DEBUG {true} \
 ] [get_bd_nets ADC_LTC2207_ADC_DITH]
  connect_bd_net -net ADC_LTC2207_ADC_PGA [get_bd_ports ADC_PGA] [get_bd_pins ADC_LTC2207/ADC_PGA]
  set_property -dict [ list \
HDL_ATTRIBUTE.MARK_DEBUG {true} \
 ] [get_bd_nets ADC_LTC2207_ADC_PGA]
  connect_bd_net -net ADC_LTC2207_ADC_RAND [get_bd_ports ADC_RAND] [get_bd_pins ADC_LTC2207/ADC_RAND]
  set_property -dict [ list \
HDL_ATTRIBUTE.MARK_DEBUG {true} \
 ] [get_bd_nets ADC_LTC2207_ADC_RAND]
  connect_bd_net -net ADC_LTC2207_ADC_SHDN [get_bd_ports ADC_SHDN] [get_bd_pins ADC_LTC2207/ADC_SHDN]
  set_property -dict [ list \
HDL_ATTRIBUTE.MARK_DEBUG {true} \
 ] [get_bd_nets ADC_LTC2207_ADC_SHDN]
  connect_bd_net -net ADC_OF_1 [get_bd_ports ADC_OF] [get_bd_pins ADC_LTC2207/ADC_OF]
  connect_bd_net -net ADC_TTL_1 [get_bd_pins ADC_LTC2207/ADC_TTL] [get_bd_pins TTL/ADC]
  connect_bd_net -net ARESETN_1 [get_bd_pins ADC_LTC2207/m_axis_aresetn] [get_bd_pins ADC_LTC2207/s_axi_aresetn] [get_bd_pins DDS_AD9951/ARESETN] [get_bd_pins TTL/s_axi_aresetn] [get_bd_pins axi_interconnect_0/ARESETN] [get_bd_pins axi_interconnect_0/M00_ARESETN] [get_bd_pins axi_interconnect_0/M01_ARESETN] [get_bd_pins axi_interconnect_0/M02_ARESETN] [get_bd_pins axi_interconnect_0/M03_ARESETN] [get_bd_pins axi_interconnect_0/S00_ARESETN] [get_bd_pins axi_protocol_converter_0/aresetn] [get_bd_pins ddc/aresetn] [get_bd_pins microblaze_ppu/areset_out]
  connect_bd_net -net DDS_AD9951_DDS_CLKEN [get_bd_ports DDS_CLKEN] [get_bd_pins DDS_AD9951/DDS_CLKEN]
  set_property -dict [ list \
HDL_ATTRIBUTE.MARK_DEBUG {true} \
 ] [get_bd_nets DDS_AD9951_DDS_CLKEN]
  connect_bd_net -net DDS_AD9951_DDS_IO_UPDATE [get_bd_ports DDS_IO_UPDATE] [get_bd_pins DDS_AD9951/DDS_IO_UPDATE]
  set_property -dict [ list \
HDL_ATTRIBUTE.MARK_DEBUG {true} \
 ] [get_bd_nets DDS_AD9951_DDS_IO_UPDATE]
  connect_bd_net -net DDS_AD9951_DDS_PWRD [get_bd_ports DDS_PWRD] [get_bd_pins DDS_AD9951/DDS_PWRD]
  set_property -dict [ list \
HDL_ATTRIBUTE.MARK_DEBUG {true} \
 ] [get_bd_nets DDS_AD9951_DDS_PWRD]
  connect_bd_net -net DDS_AD9951_DDS_RESET [get_bd_ports DDS_RESET] [get_bd_pins DDS_AD9951/DDS_RESET]
  set_property -dict [ list \
HDL_ATTRIBUTE.MARK_DEBUG {true} \
 ] [get_bd_nets DDS_AD9951_DDS_RESET]
  connect_bd_net -net DDS_AD9951_DDS_SCLK [get_bd_ports DDS_SCLK] [get_bd_pins DDS_AD9951/DDS_SCLK]
  set_property -dict [ list \
HDL_ATTRIBUTE.MARK_DEBUG {true} \
 ] [get_bd_nets DDS_AD9951_DDS_SCLK]
  connect_bd_net -net DDS_AD9951_DDS_SDIO [get_bd_ports DDS_SDIO] [get_bd_pins DDS_AD9951/DDS_SDIO]
  set_property -dict [ list \
HDL_ATTRIBUTE.MARK_DEBUG {true} \
 ] [get_bd_nets DDS_AD9951_DDS_SDIO]
  connect_bd_net -net DDS_AD9951_DDS_SWT_EN [get_bd_ports DDS_SWT_EN] [get_bd_pins DDS_AD9951/DDS_SWT_EN]
  set_property -dict [ list \
HDL_ATTRIBUTE.MARK_DEBUG {true} \
 ] [get_bd_nets DDS_AD9951_DDS_SWT_EN]
  connect_bd_net -net DDS_AD9951_DDS_SYNC [get_bd_ports DDS_SYNC] [get_bd_pins DDS_AD9951/DDS_SYNC]
  set_property -dict [ list \
HDL_ATTRIBUTE.MARK_DEBUG {true} \
 ] [get_bd_nets DDS_AD9951_DDS_SYNC]
  connect_bd_net -net DDS_SDO_1 [get_bd_ports DDS_SDO] [get_bd_pins DDS_AD9951/DDS_SDO]
  set_property -dict [ list \
HDL_ATTRIBUTE.MARK_DEBUG {true} \
 ] [get_bd_nets DDS_SDO_1]
  connect_bd_net -net TEMP_ADC_DOUT_1 [get_bd_ports TEMP_ADC_DOUT] [get_bd_pins microblaze_mcs_ppu/SPI_DIN]
  connect_bd_net -net TRIGGER_IN_0_1 [get_bd_ports TRIGGER_IN] [get_bd_pins TTL/TRIGGER_IN]
  connect_bd_net -net TTL_DDS [get_bd_pins DDS_AD9951/DDS_TTL] [get_bd_pins TTL/DDS]
  connect_bd_net -net TTL_Dout_0 [get_bd_ports P_0] [get_bd_pins TTL/P_0]
  connect_bd_net -net TTL_Dout_1 [get_bd_ports LED_FRONT] [get_bd_pins TTL/LED_FRONT]
  connect_bd_net -net TTL_Dout_2 [get_bd_ports P_4_3] [get_bd_pins TTL/P_4_3]
  connect_bd_net -net TTL_IO [get_bd_ports IO] [get_bd_pins TTL/IO]
  set_property -dict [ list \
HDL_ATTRIBUTE.MARK_DEBUG {true} \
 ] [get_bd_nets TTL_IO]
  connect_bd_net -net TTL_LED [get_bd_ports IO_15_12] [get_bd_pins TTL/IO_15_12]
  connect_bd_net -net TTL_TEMP_GATE [get_bd_ports N_TEMP_GATE] [get_bd_pins TTL/TEMP_GATE]
  connect_bd_net -net UART_rxd_1 [get_bd_pins azynq_0/UART0_TX] [get_bd_pins microblaze_mcs_ppu/UART_rxd]
  connect_bd_net -net clk_in1_n_1 [get_bd_ports FPGA_CLK_N] [get_bd_pins FPGA_CLKin/clk_in1_n]
  connect_bd_net -net clk_in1_p_1 [get_bd_ports FPGA_CLK_P] [get_bd_pins FPGA_CLKin/clk_in1_p]
  connect_bd_net -net clk_wiz_0_clk_out1 [get_bd_pins FPGA_CLKin/clk_out1] [get_bd_pins axi_interconnect_1/ACLK] [get_bd_pins axi_interconnect_1/M00_ACLK] [get_bd_pins axi_interconnect_1/M01_ACLK] [get_bd_pins axi_interconnect_1/S00_ACLK] [get_bd_pins azynq_0/M_AXI_GP0_ACLK] [get_bd_pins azynq_0/S_AXI_HP0_ACLK] [get_bd_pins microblaze_mcs_ppu/clk] [get_bd_pins microblaze_ppu/clk_in1] [get_bd_pins proc_sys_reset_0/slowest_sync_clk] [get_bd_pins zynq_gpio/s_axi_aclk]
  connect_bd_net -net clk_wiz_0_clk_out2 [get_bd_pins FPGA_CLKin/clk_out2]
  connect_bd_net -net clk_wiz_0_locked [get_bd_pins FPGA_CLKin/locked] [get_bd_pins proc_sys_reset_0/dcm_locked]
  connect_bd_net -net microblaze_mcs_ppu_Dout_0 [get_bd_ports SRSET] [get_bd_pins microblaze_mcs_ppu/SRSET]
  connect_bd_net -net microblaze_mcs_ppu_PERIPHERAL_RESET [get_bd_pins microblaze_mcs_ppu/PERIPHERAL_RESET] [get_bd_pins util_vector_logic_0/Op1]
  connect_bd_net -net microblaze_mcs_ppu_SPI_DOUT_CLK_CSN [get_bd_ports TEMP_ADC_DIN_CLK_CSN] [get_bd_pins microblaze_mcs_ppu/SPI_DOUT_CLK_CSN]
  connect_bd_net -net microblaze_mcs_ppu_UART_txd [get_bd_pins azynq_0/UART0_RX] [get_bd_pins microblaze_mcs_ppu/UART_txd]
  connect_bd_net -net microblaze_ppu_Interrupt_1 [get_bd_pins azynq_0/IRQ_F2P] [get_bd_pins microblaze_ppu/Interrupt_1]
  connect_bd_net -net proc_sys_reset_0_peripheral_aresetn [get_bd_pins axi_interconnect_1/ARESETN] [get_bd_pins axi_interconnect_1/M00_ARESETN] [get_bd_pins axi_interconnect_1/M01_ARESETN] [get_bd_pins axi_interconnect_1/S00_ARESETN] [get_bd_pins microblaze_ppu/ARESETN1] [get_bd_pins proc_sys_reset_0/peripheral_aresetn] [get_bd_pins zynq_gpio/s_axi_aresetn]
  connect_bd_net -net processing_system7_0_FCLK_RESET0_N [get_bd_pins azynq_0/FCLK_RESET0_N] [get_bd_pins proc_sys_reset_0/ext_reset_in]
  set_property -dict [ list \
HDL_ATTRIBUTE.MARK_DEBUG {true} \
 ] [get_bd_nets processing_system7_0_FCLK_RESET0_N]
  connect_bd_net -net reset_1 [get_bd_pins microblaze_mcs_ppu/reset] [get_bd_pins proc_sys_reset_0/mb_reset]
  connect_bd_net -net util_vector_logic_0_Res [get_bd_ports PERIPHERAL_RESET] [get_bd_pins util_vector_logic_0/Res]
  connect_bd_net -net xlconstant_0_const [get_bd_pins microblaze_ppu/PCap] [get_bd_pins xlconstant_0/dout]
  connect_bd_net -net xlconstant_1_dout [get_bd_pins azynq_0/SDIO1_CDN] [get_bd_pins xlconstant_1/dout]

  # Create address segments
  create_bd_addr_seg -range 0x00008000 -offset 0x40020000 [get_bd_addr_spaces azynq_0/Data] [get_bd_addr_segs microblaze_ppu/microblaze_0_local_memory/axi_bram_ctrl_d/S_AXI/Mem0] SEG_axi_bram_ctrl_d_Mem0
  create_bd_addr_seg -range 0x00020000 -offset 0x40000000 [get_bd_addr_spaces azynq_0/Data] [get_bd_addr_segs microblaze_ppu/microblaze_0_local_memory/axi_bram_ctrl_i/S_AXI/Mem0] SEG_axi_bram_ctrl_i_Mem0
  create_bd_addr_seg -range 0x00020000 -offset 0x40040000 [get_bd_addr_spaces azynq_0/Data] [get_bd_addr_segs microblaze_ppu/microblaze_0_local_memory/axi_bram_ctrl_p/S_AXI/Mem0] SEG_axi_bram_ctrl_p_Mem0
  create_bd_addr_seg -range 0x00010000 -offset 0x41200000 [get_bd_addr_spaces azynq_0/Data] [get_bd_addr_segs zynq_gpio/S_AXI/Reg] SEG_axi_gpio_0_Reg
  create_bd_addr_seg -range 0x00010000 -offset 0x43800000 [get_bd_addr_spaces azynq_0/Data] [get_bd_addr_segs microblaze_ppu/microblaze_core/mailbox/S1_AXI/Reg] SEG_mailbox_Reg
  create_bd_addr_seg -range 0x00001000 -offset 0x41000000 [get_bd_addr_spaces azynq_0/Data] [get_bd_addr_segs microblaze_ppu/pp_reset/S_AXI/Reg] SEG_pp_reset_Reg
  create_bd_addr_seg -range 0x10000000 -offset 0x30000000 [get_bd_addr_spaces ddc/dma_con/Data_S2MM] [get_bd_addr_segs azynq_0/S_AXI_HP0/HP0_DDR_LOWOCM] SEG_processing_system7_0_HP0_DDR_LOWOCM
  create_bd_addr_seg -range 0x00001000 -offset 0x42100000 [get_bd_addr_spaces microblaze_ppu/microblaze_core/microblaze_0/Data] [get_bd_addr_segs ADC_LTC2207/axi_gpio_0/S_AXI/Reg] SEG_axi_gpio_0_Reg
  create_bd_addr_seg -range 0x00010000 -offset 0x41200000 [get_bd_addr_spaces microblaze_ppu/microblaze_core/microblaze_0/Data] [get_bd_addr_segs microblaze_ppu/microblaze_core/axi_intc_0/S_AXI/Reg] SEG_axi_intc_0_Reg
  create_bd_addr_seg -range 0x00010000 -offset 0x41C00000 [get_bd_addr_spaces microblaze_ppu/microblaze_core/microblaze_0/Data] [get_bd_addr_segs microblaze_ppu/microblaze_core/axi_timer_0/S_AXI/Reg] SEG_axi_timer_0_Reg
  create_bd_addr_seg -range 0x00001000 -offset 0x42001000 [get_bd_addr_spaces microblaze_ppu/microblaze_core/microblaze_0/Data] [get_bd_addr_segs DDS_AD9951/dds_outputs/S_AXI/Reg] SEG_dds_outputs_Reg
  create_bd_addr_seg -range 0x00001000 -offset 0x42000000 [get_bd_addr_spaces microblaze_ppu/microblaze_core/microblaze_0/Data] [get_bd_addr_segs DDS_AD9951/dds_spi/AXI_LITE/Reg] SEG_dds_spi_Reg
  create_bd_addr_seg -range 0x00008000 -offset 0x00020000 [get_bd_addr_spaces microblaze_ppu/microblaze_core/microblaze_0/Data] [get_bd_addr_segs microblaze_ppu/microblaze_0_local_memory/dlmb_bram_if_cntlr_d/SLMB/Mem] SEG_dlmb_bram_if_cntlr_d_Mem
  create_bd_addr_seg -range 0x00020000 -offset 0x00040000 [get_bd_addr_spaces microblaze_ppu/microblaze_core/microblaze_0/Data] [get_bd_addr_segs microblaze_ppu/microblaze_0_local_memory/dlmb_bram_if_cntlr_p/SLMB/Mem] SEG_dlmb_bram_if_cntlr_p_Mem
  create_bd_addr_seg -range 0x00010000 -offset 0x42400000 [get_bd_addr_spaces microblaze_ppu/microblaze_core/microblaze_0/Data] [get_bd_addr_segs ddc/dma_con/S_AXI_LITE/Reg] SEG_dma_con_Reg
  create_bd_addr_seg -range 0x00010000 -offset 0x42430000 [get_bd_addr_spaces microblaze_ppu/microblaze_core/microblaze_0/Data] [get_bd_addr_segs ddc/gpio_DDC_control/S_AXI/Reg] SEG_gpio_DDC_control_Reg
  create_bd_addr_seg -range 0x00010000 -offset 0x42420000 [get_bd_addr_spaces microblaze_ppu/microblaze_core/microblaze_0/Data] [get_bd_addr_segs ddc/gpio_DDC_fifo/S_AXI/Reg] SEG_gpio_DDC_fifo_Reg
  create_bd_addr_seg -range 0x00010000 -offset 0x42410000 [get_bd_addr_spaces microblaze_ppu/microblaze_core/microblaze_0/Data] [get_bd_addr_segs ddc/gpio_DDS/S_AXI/Reg] SEG_gpio_DDS_Reg
  create_bd_addr_seg -range 0x00001000 -offset 0x42300000 [get_bd_addr_spaces microblaze_ppu/microblaze_core/microblaze_0/Data] [get_bd_addr_segs TTL/gpio_ttl/S_AXI/Reg] SEG_gpio_ttl_Reg
  create_bd_addr_seg -range 0x00020000 -offset 0x00000000 [get_bd_addr_spaces microblaze_ppu/microblaze_core/microblaze_0/Instruction] [get_bd_addr_segs microblaze_ppu/microblaze_0_local_memory/ilmb_bram_if_ctrl_i/SLMB/Mem] SEG_ilmb_bram_if_cntlr_Mem
  create_bd_addr_seg -range 0x00010000 -offset 0x43600000 [get_bd_addr_spaces microblaze_ppu/microblaze_core/microblaze_0/Data] [get_bd_addr_segs microblaze_ppu/microblaze_core/mailbox/S0_AXI/Reg] SEG_mailbox_Reg
  create_bd_addr_seg -range 0x00001000 -offset 0x41400000 [get_bd_addr_spaces microblaze_ppu/microblaze_core/microblaze_0/Data] [get_bd_addr_segs microblaze_ppu/microblaze_core/mdm_1/S_AXI/Reg] SEG_mdm_1_Reg


  # Restore current instance
  current_bd_instance $oldCurInst

  save_bd_design
}
# End of create_root_design()


##################################################################
# MAIN FLOW
##################################################################

create_root_design ""


