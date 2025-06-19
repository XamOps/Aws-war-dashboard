import gzip
import csv
from collections import defaultdict

COST_PER_GB = {'internet': 0.09, 'inter_az': 0.01, 'intra_vpc': 0.00}

PUBLIC_PREFIXES = ['3.', '13.', '15.']
PRIVATE_PREFIXES = ['10.', '172.16.', '192.168.']

def analyze_vpc_transfer_cost(flowlog_path):
    summary = defaultdict(int)
    with gzip.open(flowlog_path, 'rt') as f:
        reader = csv.reader(f, delimiter=' ')
        for row in reader:
            try:
                dstaddr = row[4]
                bytes_sent = int(row[10])
                if any(dstaddr.startswith(p) for p in PUBLIC_PREFIXES):
                    summary['internet'] += bytes_sent
                elif any(dstaddr.startswith(p) for p in PRIVATE_PREFIXES):
                    summary['intra_vpc'] += bytes_sent
                else:
                    summary['inter_az'] += bytes_sent
            except:
                continue
    return {k: round(v / (1024 ** 3) * COST_PER_GB[k], 2) for k, v in summary.items()}
