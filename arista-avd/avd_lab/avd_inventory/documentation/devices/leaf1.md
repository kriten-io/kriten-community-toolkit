# leaf1

## Table of Contents

- [Management](#management)
  - [Management Interfaces](#management-interfaces)
  - [DNS Domain](#dns-domain)
  - [IP Name Servers](#ip-name-servers)
  - [NTP](#ntp)
  - [Management API HTTP](#management-api-http)
- [Authentication](#authentication)
  - [Local Users](#local-users)
- [Management Security](#management-security)
  - [Management Security Summary](#management-security-summary)
  - [Management Security Device Configuration](#management-security-device-configuration)
- [Monitoring](#monitoring)
  - [TerminAttr Daemon](#terminattr-daemon)
- [Spanning Tree](#spanning-tree)
  - [Spanning Tree Summary](#spanning-tree-summary)
  - [Spanning Tree Device Configuration](#spanning-tree-device-configuration)
- [Internal VLAN Allocation Policy](#internal-vlan-allocation-policy)
  - [Internal VLAN Allocation Policy Summary](#internal-vlan-allocation-policy-summary)
  - [Internal VLAN Allocation Policy Device Configuration](#internal-vlan-allocation-policy-device-configuration)
- [VLANs](#vlans)
  - [VLANs Summary](#vlans-summary)
  - [VLANs Device Configuration](#vlans-device-configuration)
- [Interfaces](#interfaces)
  - [Ethernet Interfaces](#ethernet-interfaces)
  - [Port-Channel Interfaces](#port-channel-interfaces)
  - [Loopback Interfaces](#loopback-interfaces)
  - [VLAN Interfaces](#vlan-interfaces)
  - [VXLAN Interface](#vxlan-interface)
- [Routing](#routing)
  - [Service Routing Protocols Model](#service-routing-protocols-model)
  - [Virtual Router MAC Address](#virtual-router-mac-address)
  - [IP Routing](#ip-routing)
  - [IPv6 Routing](#ipv6-routing)
  - [Static Routes](#static-routes)
  - [Router BGP](#router-bgp)
- [BFD](#bfd)
  - [Router BFD](#router-bfd)
- [Multicast](#multicast)
  - [IP IGMP Snooping](#ip-igmp-snooping)
- [Filters](#filters)
  - [Prefix-lists](#prefix-lists)
  - [Route-maps](#route-maps)
- [VRF Instances](#vrf-instances)
  - [VRF Instances Summary](#vrf-instances-summary)
  - [VRF Instances Device Configuration](#vrf-instances-device-configuration)
- [Virtual Source NAT](#virtual-source-nat)
  - [Virtual Source NAT Summary](#virtual-source-nat-summary)
  - [Virtual Source NAT Configuration](#virtual-source-nat-configuration)

## Management

### Management Interfaces

#### Management Interfaces Summary

##### IPv4

| Management Interface | Description | Type | VRF | IP Address | Gateway |
| -------------------- | ----------- | ---- | --- | ---------- | ------- |
| Management0 | oob_management | oob | MGMT | 192.168.123.21/24 | 192.168.123.1 |

##### IPv6

| Management Interface | Description | Type | VRF | IPv6 Address | IPv6 Gateway |
| -------------------- | ----------- | ---- | --- | ------------ | ------------ |
| Management0 | oob_management | oob | MGMT | - | - |

#### Management Interfaces Device Configuration

```eos
!
interface Management0
   description oob_management
   no shutdown
   vrf MGMT
   ip address 192.168.123.21/24
```

### DNS Domain

DNS domain: lab.net

#### DNS Domain Device Configuration

```eos
dns domain lab.net
!
```

### IP Name Servers

#### IP Name Servers Summary

| Name Server | VRF | Priority |
| ----------- | --- | -------- |
| 8.8.8.8 | MGMT | - |

#### IP Name Servers Device Configuration

```eos
ip name-server vrf MGMT 8.8.8.8
```

### NTP

#### NTP Summary

##### NTP Local Interface

| Interface | VRF |
| --------- | --- |
| Management0 | MGMT |

##### NTP Servers

| Server | VRF | Preferred | Burst | iBurst | Version | Min Poll | Max Poll | Local-interface | Key |
| ------ | --- | --------- | ----- | ------ | ------- | -------- | -------- | --------------- | --- |
| time1.google.com | MGMT | - | - | - | - | - | - | - | - |
| time2.google.com | MGMT | - | - | - | - | - | - | - | - |
| time3.google.com | MGMT | - | - | - | - | - | - | - | - |

#### NTP Device Configuration

```eos
!
ntp local-interface vrf MGMT Management0
ntp server vrf MGMT time1.google.com
ntp server vrf MGMT time2.google.com
ntp server vrf MGMT time3.google.com
```

### Management API HTTP

#### Management API HTTP Summary

| HTTP | HTTPS | Default Services |
| ---- | ----- | ---------------- |
| False | True | - |

#### Management API VRF Access

| VRF Name | IPv4 ACL | IPv6 ACL |
| -------- | -------- | -------- |
| MGMT | - | - |

#### Management API HTTP Device Configuration

```eos
!
management api http-commands
   protocol https
   no shutdown
   !
   vrf MGMT
      no shutdown
```

## Authentication

### Local Users

#### Local Users Summary

| User | Privilege | Role | Disabled | Shell |
| ---- | --------- | ---- | -------- | ----- |
| cvpadmin | 15 | network-admin | False | - |

#### Local Users Device Configuration

```eos
!
username cvpadmin privilege 15 role network-admin secret sha512 <removed>
```

## Management Security

### Management Security Summary

| Settings | Value |
| -------- | ----- |
| Common password encryption key | True |

### Management Security Device Configuration

```eos
!
management security
   password encryption-key common
```

## Monitoring

### TerminAttr Daemon

#### TerminAttr Daemon Summary

| CV Compression | CloudVision Servers | VRF | Authentication | Smash Excludes | Ingest Exclude | Bypass AAA |
| -------------- | ------------------- | --- | -------------- | -------------- | -------------- | ---------- |
| gzip | 192.168.122.241:9910 | MGMT | key,qwerty | ale,flexCounter,hardware,kni,pulse,strata | /Sysdb/cell/1/agent,/Sysdb/cell/2/agent | False |

#### TerminAttr Daemon Device Configuration

```eos
!
daemon TerminAttr
   exec /usr/bin/TerminAttr -cvaddr=192.168.122.241:9910 -cvauth=key,<removed> -cvvrf=MGMT -smashexcludes=ale,flexCounter,hardware,kni,pulse,strata -ingestexclude=/Sysdb/cell/1/agent,/Sysdb/cell/2/agent -taillogs
   no shutdown
```

## Spanning Tree

### Spanning Tree Summary

STP mode: **mstp**

#### MSTP Instance and Priority

| Instance(s) | Priority |
| -------- | -------- |
| 0 | 4096 |

### Spanning Tree Device Configuration

```eos
!
spanning-tree mode mstp
spanning-tree mst 0 priority 4096
```

## Internal VLAN Allocation Policy

### Internal VLAN Allocation Policy Summary

| Policy Allocation | Range Beginning | Range Ending |
| ------------------| --------------- | ------------ |
| ascending | 1006 | 1199 |

### Internal VLAN Allocation Policy Device Configuration

```eos
!
vlan internal order ascending range 1006 1199
```

## VLANs

### VLANs Summary

| VLAN ID | Name | Trunk Groups |
| ------- | ---- | ------------ |
| 100 | TENANT_A_BGP_TO_COMPUTE | - |
| 200 | TENANT_A_TEST_L2_ONLY_VLAN | - |

### VLANs Device Configuration

```eos
!
vlan 100
   name TENANT_A_BGP_TO_COMPUTE
!
vlan 200
   name TENANT_A_TEST_L2_ONLY_VLAN
```

## Interfaces

### Ethernet Interfaces

#### Ethernet Interfaces Summary

##### L2

| Interface | Description | Mode | VLANs | Native VLAN | Trunk Group | Channel-Group |
| --------- | ----------- | ---- | ----- | ----------- | ----------- | ------------- |
| Ethernet1/1 | host11_leaf1_Ethernet1/1 | *access | *200 | *- | *- | 11 |
| Ethernet1/2 | host12_leaf1_Ethernet1/2 | *trunk | *100-150,200 | *- | *- | 12 |

*Inherited from Port-Channel Interface

##### IPv4

| Interface | Description | Type | Channel Group | IP Address | VRF |  MTU | Shutdown | ACL In | ACL Out |
| --------- | ----------- | -----| ------------- | ---------- | ----| ---- | -------- | ------ | ------- |
| Ethernet49/1 | P2P_LINK_TO_SPINE1_Ethernet1/1 | routed | - | 172.31.255.1/31 | default | 1500 | False | - | - |
| Ethernet50/1 | P2P_LINK_TO_SPINE2_Ethernet1/1 | routed | - | 172.31.255.3/31 | default | 1500 | False | - | - |

#### Ethernet Interfaces Device Configuration

```eos
!
interface Ethernet1/1
   description host11_leaf1_Ethernet1/1
   no shutdown
   channel-group 11 mode active
!
interface Ethernet1/2
   description host12_leaf1_Ethernet1/2
   no shutdown
   channel-group 12 mode active
!
interface Ethernet49/1
   description P2P_LINK_TO_SPINE1_Ethernet1/1
   no shutdown
   mtu 1500
   no switchport
   ip address 172.31.255.1/31
!
interface Ethernet50/1
   description P2P_LINK_TO_SPINE2_Ethernet1/1
   no shutdown
   mtu 1500
   no switchport
   ip address 172.31.255.3/31
```

### Port-Channel Interfaces

#### Port-Channel Interfaces Summary

##### L2

| Interface | Description | Type | Mode | VLANs | Native VLAN | Trunk Group | LACP Fallback Timeout | LACP Fallback Mode | MLAG ID | EVPN ESI |
| --------- | ----------- | ---- | ---- | ----- | ----------- | ------------| --------------------- | ------------------ | ------- | -------- |
| Port-Channel11 | host11_leaf1_to_host11 | switched | access | 200 | - | - | - | - | - | 0000:0000:d804:eca6:ffc4 |
| Port-Channel12 | host12_leaf3_to_host12 | switched | trunk | 100-150,200 | - | - | - | - | - | 0000:0000:1509:401c:dd4a |

##### EVPN Multihoming

####### EVPN Multihoming Summary

| Interface | Ethernet Segment Identifier | Multihoming Redundancy Mode | Route Target |
| --------- | --------------------------- | --------------------------- | ------------ |
| Port-Channel11 | 0000:0000:d804:eca6:ffc4 | all-active | d8:04:ec:a6:ff:c4 |
| Port-Channel12 | 0000:0000:1509:401c:dd4a | all-active | 15:09:40:1c:dd:4a |

#### Port-Channel Interfaces Device Configuration

```eos
!
interface Port-Channel11
   description host11_leaf1_to_host11
   no shutdown
   switchport
   switchport access vlan 200
   evpn ethernet-segment
      identifier 0000:0000:d804:eca6:ffc4
      route-target import d8:04:ec:a6:ff:c4
   lacp system-id d804.eca6.ffc4
!
interface Port-Channel12
   description host12_leaf3_to_host12
   no shutdown
   switchport
   switchport trunk allowed vlan 100-150,200
   switchport mode trunk
   evpn ethernet-segment
      identifier 0000:0000:1509:401c:dd4a
      route-target import 15:09:40:1c:dd:4a
   lacp system-id 1509.401c.dd4a
```

### Loopback Interfaces

#### Loopback Interfaces Summary

##### IPv4

| Interface | Description | VRF | IP Address |
| --------- | ----------- | --- | ---------- |
| Loopback0 | EVPN_Overlay_Peering | default | 192.0.255.129/32 |
| Loopback1 | VTEP_VXLAN_Tunnel_Source | default | 192.0.254.1/32 |
| Loopback100 | TEST_VRF_VTEP_DIAGNOSTICS | TEST_VRF | 10.255.1.1/32 |

##### IPv6

| Interface | Description | VRF | IPv6 Address |
| --------- | ----------- | --- | ------------ |
| Loopback0 | EVPN_Overlay_Peering | default | - |
| Loopback1 | VTEP_VXLAN_Tunnel_Source | default | - |
| Loopback100 | TEST_VRF_VTEP_DIAGNOSTICS | TEST_VRF | - |

#### Loopback Interfaces Device Configuration

```eos
!
interface Loopback0
   description EVPN_Overlay_Peering
   no shutdown
   ip address 192.0.255.129/32
!
interface Loopback1
   description VTEP_VXLAN_Tunnel_Source
   no shutdown
   ip address 192.0.254.1/32
!
interface Loopback100
   description TEST_VRF_VTEP_DIAGNOSTICS
   no shutdown
   vrf TEST_VRF
   ip address 10.255.1.1/32
```

### VLAN Interfaces

#### VLAN Interfaces Summary

| Interface | Description | VRF |  MTU | Shutdown |
| --------- | ----------- | --- | ---- | -------- |
| Vlan100 | TENANT_A_BGP_TO_COMPUTE | TEST_VRF | - | False |

##### IPv4

| Interface | VRF | IP Address | IP Address Virtual | IP Router Virtual Address | VRRP | ACL In | ACL Out |
| --------- | --- | ---------- | ------------------ | ------------------------- | ---- | ------ | ------- |
| Vlan100 |  TEST_VRF  |  -  |  10.100.100.1/24  |  -  |  -  |  -  |  -  |

#### VLAN Interfaces Device Configuration

```eos
!
interface Vlan100
   description TENANT_A_BGP_TO_COMPUTE
   no shutdown
   vrf TEST_VRF
   ip address virtual 10.100.100.1/24
```

### VXLAN Interface

#### VXLAN Interface Summary

| Setting | Value |
| ------- | ----- |
| Source Interface | Loopback1 |
| UDP port | 4789 |

##### VLAN to VNI, Flood List and Multicast Group Mappings

| VLAN | VNI | Flood List | Multicast Group |
| ---- | --- | ---------- | --------------- |
| 100 | 10100 | - | - |
| 200 | 10200 | - | - |

##### VRF to VNI and Multicast Group Mappings

| VRF | VNI | Multicast Group |
| ---- | --- | --------------- |
| TEST_VRF | 10 | - |

#### VXLAN Interface Device Configuration

```eos
!
interface Vxlan1
   description leaf1_VTEP
   vxlan source-interface Loopback1
   vxlan udp-port 4789
   vxlan vlan 100 vni 10100
   vxlan vlan 200 vni 10200
   vxlan vrf TEST_VRF vni 10
```

## Routing

### Service Routing Protocols Model

Multi agent routing protocol model enabled

```eos
!
service routing protocols model multi-agent
```

### Virtual Router MAC Address

#### Virtual Router MAC Address Summary

Virtual Router MAC Address: 00:1c:73:00:dc:01

#### Virtual Router MAC Address Device Configuration

```eos
!
ip virtual-router mac-address 00:1c:73:00:dc:01
```

### IP Routing

#### IP Routing Summary

| VRF | Routing Enabled |
| --- | --------------- |
| default | True |
| MGMT | False |
| TEST_VRF | True |

#### IP Routing Device Configuration

```eos
!
ip routing
no ip routing vrf MGMT
ip routing vrf TEST_VRF
```

### IPv6 Routing

#### IPv6 Routing Summary

| VRF | Routing Enabled |
| --- | --------------- |
| default | False |
| MGMT | false |
| TEST_VRF | false |

### Static Routes

#### Static Routes Summary

| VRF | Destination Prefix | Next Hop IP | Exit interface | Administrative Distance | Tag | Route Name | Metric |
| --- | ------------------ | ----------- | -------------- | ----------------------- | --- | ---------- | ------ |
| MGMT | 0.0.0.0/0 | 192.168.123.1 | - | 1 | - | - | - |

#### Static Routes Device Configuration

```eos
!
ip route vrf MGMT 0.0.0.0/0 192.168.123.1
```

### Router BGP

ASN Notation: asplain

#### Router BGP Summary

| BGP AS | Router ID |
| ------ | --------- |
| 65101 | 192.0.255.129 |

| BGP Tuning |
| ---------- |
| no bgp default ipv4-unicast |
| maximum-paths 4 ecmp 4 |

#### Router BGP Peer Groups

##### EVPN-OVERLAY-PEERS

| Settings | Value |
| -------- | ----- |
| Address Family | evpn |
| Source | Loopback0 |
| BFD | True |
| Ebgp multihop | 3 |
| Send community | all |
| Maximum routes | 0 (no limit) |

##### IPv4-UNDERLAY-PEERS

| Settings | Value |
| -------- | ----- |
| Address Family | ipv4 |
| Send community | all |
| Maximum routes | 12000 |

#### BGP Neighbors

| Neighbor | Remote AS | VRF | Shutdown | Send-community | Maximum-routes | Allowas-in | BFD | RIB Pre-Policy Retain | Route-Reflector Client | Passive | TTL Max Hops |
| -------- | --------- | --- | -------- | -------------- | -------------- | ---------- | --- | --------------------- | ---------------------- | ------- | ------------ |
| 172.31.255.0 | 65001 | default | - | Inherited from peer group IPv4-UNDERLAY-PEERS | Inherited from peer group IPv4-UNDERLAY-PEERS | - | - | - | - | - | - |
| 172.31.255.2 | 65001 | default | - | Inherited from peer group IPv4-UNDERLAY-PEERS | Inherited from peer group IPv4-UNDERLAY-PEERS | - | - | - | - | - | - |
| 192.0.255.1 | 65001 | default | - | Inherited from peer group EVPN-OVERLAY-PEERS | Inherited from peer group EVPN-OVERLAY-PEERS | - | Inherited from peer group EVPN-OVERLAY-PEERS | - | - | - | - |
| 192.0.255.2 | 65001 | default | - | Inherited from peer group EVPN-OVERLAY-PEERS | Inherited from peer group EVPN-OVERLAY-PEERS | - | Inherited from peer group EVPN-OVERLAY-PEERS | - | - | - | - |

#### Router BGP EVPN Address Family

##### EVPN Peer Groups

| Peer Group | Activate | Encapsulation |
| ---------- | -------- | ------------- |
| EVPN-OVERLAY-PEERS | True | default |

#### Router BGP VLANs

| VLAN | Route-Distinguisher | Both Route-Target | Import Route Target | Export Route-Target | Redistribute |
| ---- | ------------------- | ----------------- | ------------------- | ------------------- | ------------ |
| 100 | 192.0.255.129:10100 | 10100:10100 | - | - | learned |
| 200 | 192.0.255.129:10200 | 10200:10200 | - | - | learned |

#### Router BGP VRFs

| VRF | Route-Distinguisher | Redistribute |
| --- | ------------------- | ------------ |
| TEST_VRF | 192.0.255.129:10 | connected |

#### Router BGP Device Configuration

```eos
!
router bgp 65101
   router-id 192.0.255.129
   maximum-paths 4 ecmp 4
   no bgp default ipv4-unicast
   neighbor EVPN-OVERLAY-PEERS peer group
   neighbor EVPN-OVERLAY-PEERS update-source Loopback0
   neighbor EVPN-OVERLAY-PEERS bfd
   neighbor EVPN-OVERLAY-PEERS ebgp-multihop 3
   neighbor EVPN-OVERLAY-PEERS password 7 <removed>
   neighbor EVPN-OVERLAY-PEERS send-community
   neighbor EVPN-OVERLAY-PEERS maximum-routes 0
   neighbor IPv4-UNDERLAY-PEERS peer group
   neighbor IPv4-UNDERLAY-PEERS password 7 <removed>
   neighbor IPv4-UNDERLAY-PEERS send-community
   neighbor IPv4-UNDERLAY-PEERS maximum-routes 12000
   neighbor 172.31.255.0 peer group IPv4-UNDERLAY-PEERS
   neighbor 172.31.255.0 remote-as 65001
   neighbor 172.31.255.0 description spine1_Ethernet1/1
   neighbor 172.31.255.2 peer group IPv4-UNDERLAY-PEERS
   neighbor 172.31.255.2 remote-as 65001
   neighbor 172.31.255.2 description spine2_Ethernet1/1
   neighbor 192.0.255.1 peer group EVPN-OVERLAY-PEERS
   neighbor 192.0.255.1 remote-as 65001
   neighbor 192.0.255.1 description spine1
   neighbor 192.0.255.2 peer group EVPN-OVERLAY-PEERS
   neighbor 192.0.255.2 remote-as 65001
   neighbor 192.0.255.2 description spine2
   redistribute connected route-map RM-CONN-2-BGP
   !
   vlan 100
      rd 192.0.255.129:10100
      route-target both 10100:10100
      redistribute learned
   !
   vlan 200
      rd 192.0.255.129:10200
      route-target both 10200:10200
      redistribute learned
   !
   address-family evpn
      neighbor EVPN-OVERLAY-PEERS activate
   !
   address-family ipv4
      no neighbor EVPN-OVERLAY-PEERS activate
      neighbor IPv4-UNDERLAY-PEERS activate
   !
   vrf TEST_VRF
      rd 192.0.255.129:10
      route-target import evpn 10:10
      route-target export evpn 10:10
      router-id 192.0.255.129
      redistribute connected
```

## BFD

### Router BFD

#### Router BFD Multihop Summary

| Interval | Minimum RX | Multiplier |
| -------- | ---------- | ---------- |
| 300 | 300 | 3 |

#### Router BFD Device Configuration

```eos
!
router bfd
   multihop interval 300 min-rx 300 multiplier 3
```

## Multicast

### IP IGMP Snooping

#### IP IGMP Snooping Summary

| IGMP Snooping | Fast Leave | Interface Restart Query | Proxy | Restart Query Interval | Robustness Variable |
| ------------- | ---------- | ----------------------- | ----- | ---------------------- | ------------------- |
| Enabled | - | - | - | - | - |

#### IP IGMP Snooping Device Configuration

```eos
```

## Filters

### Prefix-lists

#### Prefix-lists Summary

##### PL-LOOPBACKS-EVPN-OVERLAY

| Sequence | Action |
| -------- | ------ |
| 10 | permit 192.0.255.128/25 eq 32 |
| 20 | permit 192.0.254.0/24 eq 32 |

#### Prefix-lists Device Configuration

```eos
!
ip prefix-list PL-LOOPBACKS-EVPN-OVERLAY
   seq 10 permit 192.0.255.128/25 eq 32
   seq 20 permit 192.0.254.0/24 eq 32
```

### Route-maps

#### Route-maps Summary

##### RM-CONN-2-BGP

| Sequence | Type | Match | Set | Sub-Route-Map | Continue |
| -------- | ---- | ----- | --- | ------------- | -------- |
| 10 | permit | ip address prefix-list PL-LOOPBACKS-EVPN-OVERLAY | - | - | - |

#### Route-maps Device Configuration

```eos
!
route-map RM-CONN-2-BGP permit 10
   match ip address prefix-list PL-LOOPBACKS-EVPN-OVERLAY
```

## VRF Instances

### VRF Instances Summary

| VRF Name | IP Routing |
| -------- | ---------- |
| MGMT | disabled |
| TEST_VRF | enabled |

### VRF Instances Device Configuration

```eos
!
vrf instance MGMT
!
vrf instance TEST_VRF
```

## Virtual Source NAT

### Virtual Source NAT Summary

| Source NAT VRF | Source NAT IP Address |
| -------------- | --------------------- |
| TEST_VRF | 10.255.1.1 |

### Virtual Source NAT Configuration

```eos
!
ip address virtual source-nat vrf TEST_VRF address 10.255.1.1
```
