# coding:utf-8
from scapy.layers.inet import *
from random import randint
from functools import partial


def get_rand_src_port():
	rv = randint(49152, 65535)  # 动态端口与私有端口所在区间
	return rv


def new_tcp_pkt(src_ip, dst_ip, dst_port, flags, src_port=None, seq=None, ack=None):
	seq = seq or randint(0, 65535)  # sequence的取值范围
	ack = ack or 0
	src_port = src_port or get_rand_src_port()
	rv = IP(src=src_ip, dst=dst_ip)/TCP(sport=src_port, dport=dst_port, seq=seq, ack=ack, flags=flags)
	return rv


def new_udp_pkt(src_ip, dst_ip, dst_port, src_port=None):
	src_port = src_port or get_rand_src_port()
	rv = IP(src=src_ip, dst=dst_ip)/UDP(sport=src_port, dport=dst_port)
	return rv


def get_flags_of_tcp_pkt(pkt):
	rv = ''
	if pkt and pkt.haslayer('TCP'):
		rv = pkt.getlayer('TCP').flags
	return rv


def _tcp_scan_3(src_ip, dst_ip, dst_port, flags):
	pkt1 = new_tcp_pkt(src_ip, dst_ip, dst_port, 'S')
	pkt2 = sr1(pkt1, timeout=1, verbose=0)
	if get_flags_of_tcp_pkt(pkt2) == 'SA':
		pkt3 = new_tcp_pkt(src_ip, dst_ip, dst_port, flags, src_port=pkt1.sport, seq=pkt1.seq+1, ack=pkt2.seq+1)
		send(pkt3, verbose=0)


def _tcp_scan_2(src_ip, dst_ip, dst_port, flags):
	pkt = new_tcp_pkt(src_ip, dst_ip, dst_port, flags)
	send(pkt, verbose=0)


def _udp_scan(src_ip, dst_ip, dst_port):
	pkt = new_udp_pkt(src_ip, dst_ip, dst_port)
	send(pkt, verbose=0)


tcp_connect_scan = partial(_tcp_scan_3, flags='RA')
tcp_stealth_scan = partial(_tcp_scan_3, flags='R')
tcp_xmas_scan = partial(_tcp_scan_2, flags='FPU')
tcp_null_scan = partial(_tcp_scan_2, flags='')
tcp_fin_scan = partial(_tcp_scan_2, flags='F')
udp_scan = _udp_scan
