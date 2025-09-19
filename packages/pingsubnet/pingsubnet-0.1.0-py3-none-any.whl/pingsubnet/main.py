#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This program uses threading to ping every address on the current subnet.
Performance: because of threading, this program can typically ping 254 addresses in under 10 seconds.
Increasing timeout_ms or pings_per_host will increase the scan time.
To automatically install all required packages:
    pip install -r requirements.txt

An IPv4 blacklist has been added to allow the user to ignore specific interfaces.
Use the IP address blacklist to ignore local interfaces (e.g. "VirtualBox Host-Only Ethernet Adapter")
If a host does not appear in the list of online hosts, check the blacklist!
There is a chance that the wrong interface will be selected, and the results will not be valid.
If that happens, disable that interface, add its IPv4 address to the blacklist, or improve the logic in the 'for interface in interfaces' block.

2025-02 - Switched from print() to the logging module: https://docs.python.org/3/library/logging.html
2025-07 - Added the IPv4 class to handle the network and hosts.
"""
import argparse
import json
import logging
import platform
import queue
import socket
import sys
import threading
import time
from datetime import datetime
from typing import NoReturn

import psutil  # For OS interface detection.
from ping3 import ping

from IPv4 import IPv4

# OS detection, because Windows uses different ping and arp arguments.
operating_system = platform.system()


class CustomFormatter( logging.Formatter ):
  """
  Custom formatter for logging that formats INFO messages differently from other levels.
  """

  def format( self, record ):
    if record.levelno == logging.INFO:
      return record.getMessage()
    else:
      return super().format( record )  # Use the parent for warnings and errors.


def setup_logging() -> None:
  """
  Set up the logging configuration for the application.
  """
  # Create separate handlers for INFO and other levels, with different outputs.
  stdout_handler = logging.StreamHandler( sys.stdout )
  stderr_handler = logging.StreamHandler( sys.stderr )
  # Set log levels.
  stdout_handler.setLevel( logging.INFO )
  stderr_handler.setLevel( logging.WARNING )  # Includes WARNING, ERROR, CRITICAL.
  # Define different formats.
  info_format = "%(message)s"  # Simple format for info logs.
  detailed_format = "%(asctime)s - %(levelname)s - %(funcName)s - %(message)s"
  # Apply formatters.
  stdout_handler.setFormatter( CustomFormatter( info_format ) )
  stderr_handler.setFormatter( CustomFormatter( detailed_format ) )
  # Configure logger.
  logger = logging.getLogger()
  logger.setLevel( logging.DEBUG )  # Allow all levels now, but overridden by CLA.
  logger.addHandler( stdout_handler )
  logger.addHandler( stderr_handler )


def get_mac_from_ip( ip_address: str = "127.0.0.1" ) -> str:
  """
  This function will attempt to get the MAC address from the provided IP address using the arp table.

  :param ip_address: The IPv4 address to query for a MAC address.
  :return: The MAC address as a colon-delimited string, or None if not found.
  """
  import subprocess
  import re

  # This is a shortcut for local interfaces to avoid the need to call arp against the IP address.
  # if ip_address == selected_interface[1].address:
  #   return selected_interface_mac
  # The -n option sets the timeout.
  first_option = "-n"
  if operating_system == "Windows":
    # The -a option reads from the current arp table.
    first_option = "-a"

  std_out = subprocess.Popen( ["arp", first_option, ip_address], stdout = subprocess.PIPE ).communicate()[0]

  regex = r"(([a-f\d]{1,2}[:-]){5}[a-f\d]{1,2})".encode( "utf-8" )
  match = re.search( regex, std_out )

  if match:
    mac_binary = match.groups()[0]
    mac_with_colons = mac_binary.replace( b"-", b":" )
    return mac_with_colons.decode( "utf-8" ).upper()
  else:
    # Handle cases where no MAC address is found.
    return " (MAC not found) "


def get_hostname_from_ip( ip_address: str = "127.0.0.1" ) -> str:
  """
  This function will attempt to get the hostname from the provided IP address using the arp table.

  :param ip_address: The IPv4 address to query for a hostname.
  :return: The hostname as a string.
  """
  try:
    new_hostname, _, _ = socket.gethostbyaddr( ip_address )
    return new_hostname
  except socket.herror:
    return ""


def ping_host_and_get_info( dest_address: str, online_host_list, ping_count: int = 1, time_unit: str = "ms", src_address: str = "", timeout: int = 5000 ) -> None:
  """
  Ping the destination address with the source address.

  :param dest_address: The target IP address or hostname to ping.
  :param online_host_list: A Queue to store the results in.
  :param ping_count: How many times to ping.
  :param time_unit: The unit of time to ping.
  :param src_address: The IP address to ping from.
  :param timeout: How long to wait for a response.
  The output is a tuple containing the ip address, the hostname, the ping time, and the MAC address which is stored in online_host_list.
  """
  delay_sum = 0
  counter = 0
  for _ in range( ping_count ):
    delay = ping( dest_address, timeout, time_unit, src_address )  # Returns the delay in seconds or None if no response.
    if delay:
      counter += 1
      delay_sum += delay
  if counter > 0:
    address_mac_time_tuple = dest_address, get_mac_from_ip( dest_address ), delay_sum / counter
    online_host_list.put( address_mac_time_tuple + (get_hostname_from_ip( dest_address ),) )


def detect_network_interfaces( debug: bool ) -> list:
  """
  Get all interfaces.
  Exclude any which have a loopback or self-assigned IP.

  :param debug: A flag to enable debug mode.
  :return: A list of viable interfaces as tuples.
  """
  # Get all network interfaces.
  interfaces = psutil.net_if_addrs()
  if debug:
    logging.debug( f" Debug: {json.dumps( interfaces )}" )
  valid_interfaces = []
  for i_face_name, interface_addresses in interfaces.items():
    # Iterate over all address info for this interface.
    for address_info in interface_addresses:
      # Check if the address is IPv4.
      if address_info.family == socket.AF_INET:
        if not address_info.address.startswith( "127.0.0.1" ) and not address_info.address.startswith( "169.254" ):
          mac_address = None
          for addr_info in interface_addresses:
            if addr_info.family == psutil.AF_LINK:  # Or socket.AF_PACKET on Linux
              mac_address = addr_info.address
              break
          valid_interfaces.append( (i_face_name, address_info, mac_address) )
        break
  return valid_interfaces


def get_range( network ) -> tuple:
  """
  Use the network to determine the starting and ending IP addresses.

  :param network: An IPv4Network class instance.
  :return: The network address and broadcast address as a tuple.
  """
  # Calculate the network address (starting address).
  network_address = network.network_address

  # Calculate the broadcast address (ending address).
  broadcast_address = network.broadcast_address

  # Return the network range.
  return network_address, broadcast_address


def exiting( exit_code: int = 0, exit_text: str = "" ) -> NoReturn:
  """
  Exit the program with a message and timestamp.
  Post-conditions: The program will be terminated.

  :param exit_code: The return value to pass to the OS.
  :param exit_text: The text to print before exiting.
  :rtype: NoReturn
  :raises SystemExit: under all circumstances.
  """
  exit_timestamp = datetime.now().replace( microsecond = 0 ).isoformat( sep = " " )
  logging.info( "" )
  if exit_text != "":
    logging.info( f"{exit_text}" )
  logging.info( f"  Exiting with code {exit_code} at {exit_timestamp}" )
  raise SystemExit( exit_code )


def prompt_for_list_item( max_value: int ) -> int:
  """
  Prompt the user to select one element from selection_list.

  :param max_value: The number of elements to select from.
  :return: The selected list item.
  """
  temp_number = -1
  while temp_number < 0:
    temp_answer = input( "Enter the number to the left of your selection (or 'x' to exit): " ).strip()
    if temp_answer == "x":
      exiting( 1, "User aborted." )
    try:
      if max_value > int( temp_answer ) >= 0:
        temp_number = int( temp_answer )
      else:
        logging.info( "  That is not a valid selection!" )
    except ValueError:
      logging.warning( "That is not a valid number!" )
  return temp_number


def run():
  program_name = "PingSubnet"
  setup_logging()

  # Set up ArgumentParser.
  parser = argparse.ArgumentParser( description = f"{program_name}: A subnet pinging tool." )
  parser.add_argument( "--debug", action = "store_true", default = False, help = "Enable debug mode." )
  parser.add_argument( "--timeout_ms", type = int, default = 5000, help = "Ping timeout in milliseconds." )
  parser.add_argument( "--pings_per_host", type = int, default = 3, help = "Number of pings per host." )

  # Parse arguments.
  args = parser.parse_args()

  # Configure the logging level based on the debug flag.
  if args.debug:
    logging.getLogger().setLevel( logging.DEBUG )

  # Assign values from command-line arguments.
  debug = args.debug
  timeout_ms = args.timeout_ms
  pings_per_host = args.pings_per_host

  ping_unit = "ms"
  hostname = socket.gethostname()
  selected_index = 0
  start_time = time.perf_counter()
  current_time = datetime.now().replace( microsecond = 0 ).isoformat( sep = " " )

  logging.info( f"Starting {program_name} at {current_time}" )
  logging.debug( f"Hostname: {hostname}" )
  logging.info( f"Debug mode: {'ON' if debug else 'OFF'}" )
  logging.info( f"Timeout: {timeout_ms} ms" )
  logging.info( f"Pings per host: {pings_per_host}" )

  interface_list = detect_network_interfaces( debug )
  if not interface_list:
    exiting( 2, "No viable interfaces discovered!" )
  elif len( interface_list ) > 1:
    logging.info( "" )
    # Print the list of network interfaces.
    logging.info( "Network Interfaces Detected:" )
    # Print all valid interfaces.
    for index, (interface_name, interface_object, _) in enumerate( interface_list ):
      logging.info( f"  {index} - {interface_name} - {interface_object.address}" )
    # Prompt the user for the interface to use.
    selected_index = prompt_for_list_item( len( interface_list ) )
    if debug:
      logging.debug( f" Debug: Detailed network info: {interface_list[selected_index]}" )
  else:
    logging.info( f"Using the interface named '{interface_list[selected_index][0]}'" )

  # Get the selected IPv4 data and save to the global.
  selected_interface = interface_list[selected_index]
  selected_interface_mac = selected_interface[2].replace( "-", ":" )

  if debug:
    logging.debug( f" Debug: {selected_interface[1].address}/{selected_interface[1].netmask}" )
  # Use the IPv4 class to handle the network and hosts.
  ipv4 = IPv4( selected_interface[1].address, selected_interface[1].netmask )
  all_hosts = ipv4.hosts
  start_address = ipv4.network_address
  end_address = ipv4.broadcast_address
  logging.info( f"Pinging addresses from {start_address} to {end_address}" )

  logging.info( "" )
  logging.info( "Detected properties:" )
  logging.info( f"  {operating_system} operating system" )
  logging.info( f"  interface name: {selected_interface[0]}" )
  logging.info( f"  local hostname: {hostname}" )
  logging.info( f"  local IP address: {selected_interface[1].address}" )
  logging.info( f"  local network mask: {selected_interface[1].netmask}" )
  logging.info( f"  local MAC address: {selected_interface_mac}" )
  logging.info( "" )
  logging.info( f"Pinging addresses from {start_address} to {end_address}" )

  try:
    online_host_list = []
    online_host_queue = queue.Queue()
    thread_list = []
    subnet_size = len( all_hosts )
    if subnet_size > 4096:
      logging.info( f"\n\nThere were {subnet_size} possible hosts detected." )
      logging.info( "This is likely an incorrectly detected subnet mask or an unused network adapter." )
      logging.info( "Enter 1 to continue, or anything else to exit: " )
      answer = input( "" ).strip()
      if int( answer ) != 1:
        logging.info( "Exiting..." )
        sys.exit( -1 )

    suffix = "s"
    if pings_per_host == 1:
      suffix = ""
    logging.info( f"\nThreading {subnet_size} pings, pinging each host {pings_per_host} time{suffix}, and using a timeout of {timeout_ms} milliseconds..." )
    # For each IP address in the subnet, run the ping command with subprocess.popen interface.
    for i in range( subnet_size ):
      # thread_list.append( threading.Thread( target = ping_host_and_get_info, args = (str( all_hosts[i] ), pings_per_host, ping_unit, selected_interface[1].address, timeout_ms) ) )
      thread_list.append( threading.Thread( target = ping_host_and_get_info, args = (str( all_hosts[i] ), online_host_queue, pings_per_host, ping_unit, selected_interface[1].address, timeout_ms) ) )

    logging.info( "Starting all threads..." )
    # Start all threads.
    for thread in thread_list:
      thread.start()

    logging.info( "Waiting for all threads to finish..." )
    # Join all threads.
    for thread in thread_list:
      # Wait until all threads terminate using a timeout appropriate for the number of hosts.
      thread.join( timeout_ms / 1000 * pings_per_host )

    # After every thread has joined.
    online_host_list = []
    while not online_host_queue.empty():
      online_host_list.append( online_host_queue.get() )

    logging.info( "\nAll online host IP and MAC addresses:" )
    logging.info( "IP\tMAC\tHostname\tPing\tping unit" )
    sorted_ip_mac = sorted( online_host_list, key = lambda x: list( map( int, x[0].split( "." ) ) ) )
    for online_host in sorted_ip_mac:
      # Note that the results are displayed out of order.
      logging.info( f"{online_host[0]}\t{online_host[1]}\t{online_host[3]}\t{online_host[2]:.1f}\t{ping_unit}" )
    logging.info( "" )
    logging.info( f"{len( sorted_ip_mac )} out of {subnet_size} hosts responded to a ping within {timeout_ms / 1000} seconds." )
    logging.info( f"Scanning took {round( time.perf_counter() - start_time, 2 )} seconds.\n" )

  except KeyboardInterrupt:
    logging.warning( "Execution interrupted." )

  logging.info( f"Goodbye from {program_name}" )


if __name__ == "__main__":
  run()
