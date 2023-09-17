# -*- coding: utf-8 -*-
"""
Created on Wed May 13 18:04:52 2020

@author: Administrator
"""

from __future__ import absolute_import, division, print_function

import time

from builtins import *  # @UnusedWildImport

from mcculw import ul
from mcculw.enums import ScanOptions, FunctionType, Status
from examples.console import util
from mcculw.ul import ULError, a_input_mode
from mcculw.enums import InterfaceType
from mcculw.enums import ULRange
from mcculw.enums import AnalogInputMode
#import ctypes

import pandas as pd
import matplotlib.pyplot as plt

use_device_detection = True


def Scope_DAQ(rate,points_per_channel):
    board_num = 0
    board_index = 0
    find_device = "USB-1808X"
    if use_device_detection:
        board_num = -1
        ul.ignore_instacal()
        dev_list = ul.get_daq_device_inventory(InterfaceType.USB)
        if len(dev_list) > 0:
            for device in dev_list:
                if str(device) == find_device:
                    print(f"Found {find_device} board number = {board_index}")
                    print(f"Serial number: {device.unique_id}")
                    print(f"Product type: {hex(device.product_id)}")
                    board_num = board_index
                    ul.create_daq_device(board_num, device)
                board_index = board_index + 1
            if board_num == -1:
                print(f"Device {find_device} not found")
                return
        else:
            print("No devices detected")
            return
    # **********End of Discovery************

#    rate = 5000
#    points_per_channel = 50000
    low_chan = 0
    high_chan = 0
    num_chans = 1

    total_count = points_per_channel * num_chans
    half_count = int(total_count / 2)
    # If the hardware supports the SCALEDATA option, it is easiest to
    # use it.
    scan_options = ScanOptions.CONTINUOUS | ScanOptions.BACKGROUND | ScanOptions.SCALEDATA

    memhandle = ul.scaled_win_buf_alloc(total_count)

    # Convert the memhandle to a ctypes array.
    # Use the memhandle_as_ctypes_array_scaled method for scaled
    # buffers.
    ctypes_array = util.memhandle_as_ctypes_array_scaled(memhandle)

    # Note: the ctypes array will no longer be valid after win_buf_free is
    # called.
    # A copy of the buffer can be created using win_buf_to_array or
    # win_buf_to_array_32 before the memory is freed. The copy can be used
    # at any time.

    # Check if the buffer was successfully allocated
    if not memhandle:
        print("Failed to allocate memory.")
        return

    a_input_mode(board_num, AnalogInputMode.SINGLE_ENDED)

    try:
        # Start the scan
        ul.a_in_scan(
            board_num, low_chan, high_chan, total_count,
            rate, ULRange.BIP10VOLTS, memhandle, scan_options)

        # Create a format string that aligns the data in columns
        # plus two for curr_index and curr_count
        row_format = "{:8}" * (num_chans + 3)

        # Print the channel name headers
        labels = []
        for ch_num in range(low_chan, high_chan + 1):
            labels.append("CH" + str(ch_num) + "\t")

        labels.append("index\t")
        labels.append("count\t")
        labels.append("diff")
        print(row_format.format(*labels))

        # boolean flag used to toggle reading upper and lower buffer
        read_lower = True
        # Start updating the displayed values
        status, curr_count, curr_index = ul.get_status(
            board_num, FunctionType.AIFUNCTION)

        buf_data = util.memhandle_as_ctypes_array_scaled(memhandle)
        last = 0
        diff = 0
        hola = []

        while status != Status.IDLE and curr_count<total_count:
            # Make sure a data point is available for display.
            if curr_count > 0:
                # curr_index points to the start of the last completed
                # channel scan that was transferred between the board and
                # the data buffer. Display the latest value for each
                # channel.

                # display_data = []

                if (curr_index > half_count) and (read_lower == True):
                    diff = curr_count - last
                    ul.scaled_win_buf_to_array(memhandle, buf_data, 0, int(half_count))


                    hola = buf_data[0:half_count]
                    last = curr_count
                    read_lower = False
                    
                    hola = buf_data[0:half_count]
#                    print('Pausamos la cosa en curr_index = %s' % curr_index)
#                    time.sleep(2)
#                    plt.plot(hola,'ro')
#                    time.sleep(5)

                

            status, curr_count, curr_index = ul.get_status(
                board_num, FunctionType.AIFUNCTION)
            

        # Stop the background operation (this is required even if the
        # scan completes successfully)
        ul.stop_background(board_num, FunctionType.AIFUNCTION)

        print("Scan completed successfully.")
    except ULError as e:
        util.print_ul_error(e)
    finally:
       
        result = hola 


        
        ul.win_buf_free(memhandle)

        if use_device_detection:
            ul.release_daq_device(board_num)
            
    return result


#if __name__ == '__main__':
#    rate = 5000
#    points_per_channel = 25000
#    result = Scope_DAQ(rate,points_per_channel)
#    plt.plot(result)