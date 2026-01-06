"""
RND - Independent Network Diagnostics
Real-time ping and traceroute functionality with enhanced error handling
"""
import logging
import subprocess
import re
import platform
import ipaddress
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class NetworkDiagnostics:
    """Independent network diagnostics - ping and traceroute with input sanitization"""

    def __init__(self):
        self.system = platform.system()

    def _validate_ip_or_hostname(self, target: str) -> bool:
        """Validate IP address or hostname to prevent command injection"""
        target = target.strip()
        
        # Try to parse as IP address
        try:
            ipaddress.ip_address(target)
            return True
        except ValueError:
            pass
        
        # Validate hostname (alphanumeric, dots, hyphens)
        if re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9\-\.]{0,253}[a-zA-Z0-9])?$', target):
            return True
        
        return False

    def ping(self, ip_address: str, count: int = 5, timeout: int = 5) -> Dict:
        """
        Perform ICMP ping check with enhanced error handling

        Returns:
            {
                'ip': str,
                'packets_sent': int,
                'packets_received': int,
                'packet_loss_percent': int,
                'min_rtt_ms': float,
                'avg_rtt_ms': float,
                'max_rtt_ms': float,
                'is_reachable': bool,
                'timestamp': datetime
            }
        """
        if not self._validate_ip_or_hostname(ip_address):
            logger.error(f"Invalid IP address or hostname: {ip_address}")
            return self._ping_error_result(ip_address, count, "Invalid IP address or hostname")
        
        count = max(1, min(count, 20))  # Limit to 1-20 packets
        timeout = max(1, min(timeout, 30))  # Limit to 1-30 seconds
        
        try:
            # Platform-specific ping command
            if self.system == "Windows":
                cmd = ["ping", "-n", str(count), "-w", str(timeout * 1000), ip_address]
            else:  # Linux/Mac
                cmd = ["ping", "-c", str(count), "-W", str(timeout), ip_address]

            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=timeout + 10,
                check=False  # Don't raise exception on non-zero exit
            )

            output = result.stdout + result.stderr  # Capture both stdout and stderr

            # Parse results
            if self.system == "Windows":
                return self._parse_ping_windows(output, ip_address, count)
            else:
                return self._parse_ping_unix(output, ip_address, count)

        except subprocess.TimeoutExpired:
            logger.warning(f"Ping timeout for {ip_address}")
            return self._ping_timeout_result(ip_address, count)
        except FileNotFoundError:
            logger.error("Ping command not found on system")
            return self._ping_error_result(ip_address, count, "Ping command not available")
        except Exception as e:
            logger.error(f"Ping error for {ip_address}: {e}", exc_info=True)
            return self._ping_error_result(ip_address, count, str(e))

    def _parse_ping_unix(self, output: str, ip: str, count: int) -> Dict:
        """Parse Unix/Linux/Mac ping output with improved regex"""
        result = {
            "ip": ip,
            "packets_sent": count,
            "packets_received": 0,
            "packet_loss_percent": 100,
            "min_rtt_ms": None,
            "avg_rtt_ms": None,
            "max_rtt_ms": None,
            "is_reachable": False,
            "timestamp": datetime.utcnow(),
        }

        # Example: "5 packets transmitted, 5 received, 0% packet loss"
        packet_match = re.search(r"(\d+) packets transmitted,\s*(\d+)\s+(?:packets\s+)?received", output, re.IGNORECASE)
        if packet_match:
            result["packets_sent"] = int(packet_match.group(1))
            result["packets_received"] = int(packet_match.group(2))
            sent = result["packets_sent"]
            received = result["packets_received"]
            result["packet_loss_percent"] = int(((sent - received) / sent) * 100) if sent > 0 else 100
            result["is_reachable"] = received > 0

        # Example: "round-trip min/avg/max/stddev = 10.5/12.3/15.2/1.8 ms"
        # Example: "rtt min/avg/max/mdev = 10.5/12.3/15.2/1.8 ms"
        rtt_match = re.search(r"(?:rtt|round-trip)\s+min/avg/max(?:/(?:stddev|mdev))?\s*=\s*([\d.]+)/([\d.]+)/([\d.]+)", output, re.IGNORECASE)
        if rtt_match:
            result["min_rtt_ms"] = float(rtt_match.group(1))
            result["avg_rtt_ms"] = float(rtt_match.group(2))
            result["max_rtt_ms"] = float(rtt_match.group(3))

        return result

    def _parse_ping_windows(self, output: str, ip: str, count: int) -> Dict:
        """Parse Windows ping output"""
        result = {
            "ip": ip,
            "packets_sent": count,
            "packets_received": 0,
            "packet_loss_percent": 100,
            "min_rtt_ms": None,
            "avg_rtt_ms": None,
            "max_rtt_ms": None,
            "is_reachable": False,
            "timestamp": datetime.utcnow(),
        }

        # Parse packet statistics
        packet_match = re.search(r"Sent = (\d+), Received = (\d+), Lost = \d+ $$(\d+)% loss$$", output)
        if packet_match:
            result["packets_sent"] = int(packet_match.group(1))
            result["packets_received"] = int(packet_match.group(2))
            result["packet_loss_percent"] = int(packet_match.group(3))
            result["is_reachable"] = result["packets_received"] > 0

        # Parse RTT statistics
        rtt_match = re.search(r"Minimum = (\d+)ms, Maximum = (\d+)ms, Average = (\d+)ms", output)
        if rtt_match:
            result["min_rtt_ms"] = float(rtt_match.group(1))
            result["max_rtt_ms"] = float(rtt_match.group(2))
            result["avg_rtt_ms"] = float(rtt_match.group(3))

        return result

    def _ping_timeout_result(self, ip: str, count: int) -> Dict:
        """Return timeout result"""
        return {
            "ip": ip,
            "packets_sent": count,
            "packets_received": 0,
            "packet_loss_percent": 100,
            "min_rtt_ms": None,
            "avg_rtt_ms": None,
            "max_rtt_ms": None,
            "is_reachable": False,
            "timestamp": datetime.utcnow(),
            "error": "Timeout",
        }

    def _ping_error_result(self, ip: str, count: int, error_msg: str = "Ping failed") -> Dict:
        """Return error result with custom message"""
        return {
            "ip": ip,
            "packets_sent": count,
            "packets_received": 0,
            "packet_loss_percent": 100,
            "min_rtt_ms": None,
            "avg_rtt_ms": None,
            "max_rtt_ms": None,
            "is_reachable": False,
            "timestamp": datetime.utcnow(),
            "error": error_msg,  # Made error message customizable
        }

    def traceroute(self, ip_address: str, max_hops: int = 30, timeout: int = 30) -> Dict:
        """
        Perform traceroute to device with enhanced error handling

        Returns:
            {
                'target_ip': str,
                'hops': [
                    {
                        'hop_number': int,
                        'ip': str,
                        'hostname': str,
                        'latency_ms': float
                    }
                ],
                'total_hops': int,
                'timestamp': datetime
            }
        """
        if not self._validate_ip_or_hostname(ip_address):
            logger.error(f"Invalid IP address or hostname: {ip_address}")
            return {
                "target_ip": ip_address,
                "hops": [],
                "total_hops": 0,
                "reached_destination": False,
                "timestamp": datetime.utcnow(),
                "error": "Invalid IP address or hostname",
            }
        
        max_hops = max(1, min(max_hops, 64))  # Limit to 1-64 hops
        timeout = max(5, min(timeout, 120))  # Limit to 5-120 seconds
        
        try:
            # Platform-specific traceroute command
            if self.system == "Windows":
                cmd = ["tracert", "-h", str(max_hops), "-w", "2000", ip_address]
            else:  # Linux/Mac
                traceroute_cmd = None
                for cmd_name in ["traceroute", "tracepath", "/usr/sbin/traceroute"]:
                    try:
                        subprocess.run([cmd_name, "--version"], capture_output=True, timeout=2, check=False)
                        traceroute_cmd = cmd_name
                        break
                    except FileNotFoundError:
                        continue
                
                if not traceroute_cmd:
                    raise FileNotFoundError("No traceroute command available")
                
                cmd = [traceroute_cmd, "-m", str(max_hops), "-w", "2", "-n", ip_address]

            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=timeout,
                check=False
            )

            output = result.stdout + result.stderr

            # Parse results
            if self.system == "Windows":
                hops = self._parse_traceroute_windows(output)
            else:
                hops = self._parse_traceroute_unix(output)

            return {
                "target_ip": ip_address,
                "hops": hops,
                "total_hops": len(hops),
                "reached_destination": any(h.get("ip") == ip_address for h in hops),
                "timestamp": datetime.utcnow(),
            }

        except subprocess.TimeoutExpired:
            logger.warning(f"Traceroute timeout for {ip_address}")
            return {
                "target_ip": ip_address,
                "hops": [],
                "total_hops": 0,
                "reached_destination": False,
                "timestamp": datetime.utcnow(),
                "error": "Traceroute timeout",
            }
        except FileNotFoundError as e:
            logger.error(f"Traceroute command not found: {e}")
            return {
                "target_ip": ip_address,
                "hops": [],
                "total_hops": 0,
                "reached_destination": False,
                "timestamp": datetime.utcnow(),
                "error": "Traceroute command not available on system",
            }
        except Exception as e:
            logger.error(f"Traceroute error for {ip_address}: {e}", exc_info=True)
            return {
                "target_ip": ip_address,
                "hops": [],
                "total_hops": 0,
                "reached_destination": False,
                "timestamp": datetime.utcnow(),
                "error": str(e),
            }

    def _parse_traceroute_unix(self, output: str) -> List[Dict]:
        """Parse Unix/Linux/Mac traceroute output with improved regex"""
        hops = []

        # Pattern 1: " 1  192.168.1.1 (192.168.1.1)  1.234 ms  1.345 ms  1.456 ms"
        # Pattern 2: " 1  192.168.1.1  1.234 ms  1.345 ms  1.456 ms" (numeric mode)
        # Pattern 3: " 1  * * *" (timeout)
        
        for line in output.split("\n"):
            line = line.strip()
            if not line:
                continue
            
            # Extract hop number
            hop_match = re.match(r"^\s*(\d+)", line)
            if not hop_match:
                continue
            
            hop_num = int(hop_match.group(1))
            
            # Check for timeout
            if "*" in line and not re.search(r"\d+\.\d+\.\d+\.\d+", line):
                hops.append({
                    "hop_number": hop_num,
                    "ip": None,
                    "hostname": "*",
                    "latency_ms": None
                })
                continue
            
            # Parse IP and latency
            ip_match = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)
            latency_match = re.search(r"([\d.]+)\s*ms", line)
            
            if ip_match:
                ip = ip_match.group(1)
                latency = float(latency_match.group(1)) if latency_match else None
                
                # Extract hostname if present
                hostname_match = re.search(r"([\w\.\-]+)\s+$$" + re.escape(ip) + r"$$", line)
                hostname = hostname_match.group(1) if hostname_match else ip
                
                hops.append({
                    "hop_number": hop_num,
                    "ip": ip,
                    "hostname": hostname,
                    "latency_ms": latency
                })

        return hops

    def _parse_traceroute_windows(self, output: str) -> List[Dict]:
        """Parse Windows tracert output with improved regex"""
        hops = []

        # Example line: "  1     1 ms     1 ms     1 ms  192.168.1.1"
        # Example line: "  2     5 ms     5 ms     5 ms  gateway.example.com [10.0.0.1]"
        # Example line: "  3     *        *        *     Request timed out."
        
        for line in output.split("\n"):
            line = line.strip()
            if not line or line.startswith("Tracing"):
                continue
            
            # Extract hop number
            hop_match = re.match(r"^(\d+)", line)
            if not hop_match:
                continue
            
            hop_num = int(hop_match.group(1))
            
            # Check for timeout
            if "Request timed out" in line or "*" in line and not re.search(r"\d+\.\d+\.\d+\.\d+", line):
                hops.append({
                    "hop_number": hop_num,
                    "ip": None,
                    "hostname": "*",
                    "latency_ms": None
                })
                continue
            
            # Parse latency (take first non-* value)
            latency_match = re.search(r"(\d+)\s*ms", line)
            latency = float(latency_match.group(1)) if latency_match else None
            
            # Parse IP address
            ip_match = re.search(r"\[([\d\.]+)\]", line)  # IP in brackets
            if not ip_match:
                ip_match = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)  # Direct IP
            
            if ip_match:
                ip = ip_match.group(1)
                
                # Extract hostname
                hostname_match = re.search(r"ms\s+([\w\.\-]+)\s+\[", line)
                hostname = hostname_match.group(1) if hostname_match else ip
                
                hops.append({
                    "hop_number": hop_num,
                    "ip": ip,
                    "hostname": hostname,
                    "latency_ms": latency
                })

        return hops
