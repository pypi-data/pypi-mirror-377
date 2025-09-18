# Quick Start Guide

Get up and running with mcpcap in minutes!

## 1. Install mcpcap

```bash
pip install mcpcap
```

## 2. Start the MCP Server

Start mcpcap as a stateless MCP server:

```bash
# Start with all modules (default: dns,dhcp,icmp,capinfos)
mcpcap

# Start with specific modules only
mcpcap --modules dns

# With packet analysis limits for large files
mcpcap --max-packets 1000
```

The server will start and display connection information. Keep this terminal open.

## 3. Connect with an MCP Client

### Option A: MCP Inspector (Quick Testing)

Install and run MCP Inspector for interactive testing:

```bash
npm install -g @modelcontextprotocol/inspector
npx @modelcontextprotocol/inspector mcpcap
```

This opens a web interface where you can test the analysis tools interactively.

### Option B: Claude Desktop

Add mcpcap to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "mcpcap": {
      "command": "mcpcap",
      "args": []
    }
  }
}
```

Restart Claude Desktop and you'll have access to mcpcap analysis tools.

## 4. Analyze PCAP Files

### DNS Analysis

Use the `analyze_dns_packets` tool with any PCAP file by providing file paths or URLs (not file uploads):

**Local files:**
```javascript
analyze_dns_packets("/path/to/dns.pcap")
analyze_dns_packets("./examples/dns.pcap")
```

**Remote files:**
```javascript
analyze_dns_packets("https://wiki.wireshark.org/uploads/dns.cap")
```

**Example response:**
```json
{
  "file": "./examples/dns.pcap",
  "analysis_timestamp": "2024-01-01T12:00:00.000000",
  "total_packets_in_file": 50,
  "dns_packets_found": 25,
  "dns_packets_analyzed": 25,
  "statistics": {
    "queries": 12,
    "responses": 13,
    "unique_domains_queried": 8,
    "unique_domains": ["example.com", "google.com", "github.com"]
  },
  "packets": ["...detailed packet analysis..."]
}
```

### DHCP Analysis

Use the `analyze_dhcp_packets` tool with any PCAP file containing DHCP traffic (provide file path or URL):

```javascript
analyze_dhcp_packets("/path/to/dhcp.pcap")
analyze_dhcp_packets("https://example.com/network-capture.pcap")
```

**Example response:**
```json
{
  "file": "/path/to/dhcp.pcap",
  "total_packets": 20,
  "dhcp_packets_found": 4,
  "dhcp_packets_analyzed": 4,
  "statistics": {
    "unique_clients_count": 1,
    "unique_servers_count": 1,
    "message_type_counts": {
      "DISCOVER": 1,
      "OFFER": 1,
      "REQUEST": 1,
      "ACK": 1
    },
    "transaction_count": 1
  },
  "packets": ["...detailed DHCP transaction analysis..."]
}
```

### ICMP Analysis

Use the `analyze_icmp_packets` tool with any PCAP file containing ICMP traffic (provide file path or URL):

```javascript
analyze_icmp_packets("/path/to/network.pcap")
analyze_icmp_packets("https://example.com/ping-capture.pcap")
```

**Example response:**
```json
{
  "file": "/path/to/network.pcap", 
  "total_packets": 100,
  "icmp_packets_found": 12,
  "icmp_packets_analyzed": 12,
  "statistics": {
    "icmp_type_counts": {
      "Echo Request": 6,
      "Echo Reply": 6
    },
    "unique_sources_count": 2,
    "unique_destinations_count": 2,
    "echo_sessions": 1
  },
  "packets": ["...detailed ICMP analysis..."]
}
```

### CapInfos Analysis

Use the `analyze_capinfos` tool to get metadata and statistics from any PCAP file:

```javascript
analyze_capinfos("/path/to/capture.pcap")
analyze_capinfos("https://example.com/network.pcap")
```

**Example response:**
```json
{
  "file_size_bytes": 4338,
  "filename": "dns.pcap",
  "file_encapsulation": "Ethernet",
  "packet_count": 38,
  "data_size_bytes": 3706,
  "capture_duration_seconds": 278.879,
  "first_packet_time": 1112172466.496046,
  "last_packet_time": 1112172745.375359,
  "data_rate_bytes": 13.29,
  "data_rate_bits": 106.31,
  "average_packet_size_bytes": 97.53,
  "average_packet_rate": 0.136
}
```

## 5. Use Analysis Prompts

mcpcap includes specialized prompts to guide your analysis:

### DNS Analysis Prompts

- **`security_analysis`** - Focus on threat detection:
  - Suspicious domain patterns (DGA domains)
  - DNS tunneling detection
  - C2 communication patterns
  - Known malicious domains

- **`network_troubleshooting`** - Network performance focus:
  - DNS response times and latency
  - Failed queries and timeouts
  - DNS server issues
  - Configuration problems

- **`forensic_investigation`** - Legal/forensic analysis:
  - Timeline reconstruction
  - Evidence preservation
  - Attribution and tracking
  - Detailed documentation

### DHCP Analysis Prompts

- **`dhcp_network_analysis`** - Network administration:
  - IP address management
  - DHCP lease analysis
  - Network topology mapping
  - Configuration optimization

- **`dhcp_security_analysis`** - Security threats:
  - Rogue DHCP server detection
  - DHCP attack identification
  - Client behavior anomalies
  - Security policy violations

- **`dhcp_forensic_investigation`** - Forensic analysis:
  - Device tracking via MAC addresses
  - Network presence timeline
  - Evidence collection
  - Incident reconstruction

### ICMP Analysis Prompts

- **`icmp_network_diagnostics`** - Network troubleshooting:
  - Ping connectivity analysis
  - Network path tracing
  - RTT and latency analysis
  - Packet loss detection

- **`icmp_security_analysis`** - Security threats:
  - ICMP-based attacks (floods, tunneling)
  - Reconnaissance activity detection
  - Covert channel communication
  - Network scanning patterns

- **`icmp_forensic_investigation`** - Forensic analysis:
  - Network activity timeline
  - Host communication patterns
  - Evidence preservation
  - Attack vector analysis

## 6. Example Workflow

Here's a typical analysis workflow:

1. **Start the server**: `mcpcap`
2. **Analyze DNS traffic**: `analyze_dns_packets("/path/to/capture.pcap")`
3. **Review results**: Look for unusual domains or query patterns  
4. **Use specialized prompts**: Apply security_analysis for threat detection
5. **Analyze DHCP traffic**: `analyze_dhcp_packets("/path/to/capture.pcap")`
6. **Analyze ICMP traffic**: `analyze_icmp_packets("/path/to/capture.pcap")`
7. **Get file metadata**: `analyze_capinfos("/path/to/capture.pcap")`
8. **Cross-reference findings**: Correlate DNS, DHCP, ICMP data and metadata for complete network picture

## 7. Configuration Options

### Module Selection

```bash
# DNS analysis only
mcpcap --modules dns

# DHCP analysis only
mcpcap --modules dhcp

# All modules (default)
mcpcap --modules dns,dhcp,icmp,capinfos

# Or specific combinations
mcpcap --modules dns,icmp,capinfos
```

### Performance Tuning

```bash
# Limit packet analysis for large files
mcpcap --max-packets 1000

# Combined configuration
mcpcap --modules dns,capinfos --max-packets 500
```

## 8. Testing with Examples

mcpcap includes example PCAP files for testing:

```javascript
// Test DNS analysis
analyze_dns_packets("./examples/dns.pcap")

// Test DHCP analysis  
analyze_dhcp_packets("./examples/dhcp.pcap")

// Test ICMP analysis
analyze_icmp_packets("./examples/icmp.pcap")

// Test CapInfos analysis
analyze_capinfos("./examples/dns.pcap")
```

## Next Steps

- Explore the [MCP Integration Guide](mcp-integration.md) for detailed client setup
- Read the [Analysis Guides](analysis-guides.md) for advanced techniques
- Check out the examples directory for real PCAP files to practice with

## Troubleshooting

### Server Won't Start

```bash
# Check Python version (3.10+ required)
python --version

# Verify installation
pip show mcpcap

# Check for port conflicts
lsof -i :stdio
```

### File Not Found Errors

```bash
# Use absolute paths
analyze_dns_packets("/full/path/to/file.pcap")

# Check file exists and has correct extension
ls -la /path/to/file.pcap
file /path/to/file.pcap  # Should show "tcpdump capture file"
```

### No Packets Found

```bash
# Verify PCAP contains expected protocol traffic
tcpdump -r your-file.pcap -c 10 port 53    # For DNS
tcpdump -r your-file.pcap -c 10 port 67    # For DHCP

# Check file integrity
wireshark your-file.pcap
```

### MCP Client Connection Issues

- Ensure mcpcap server is still running
- Check MCP client configuration syntax
- Verify no firewall blocking connections
- Restart MCP client after configuration changes