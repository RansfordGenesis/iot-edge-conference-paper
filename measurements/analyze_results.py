"""
Results Analysis — pulls Config A & B JSON results and CloudWatch metrics,
produces the final comparison table and figures for the paper.

Usage:
    python3 analyze_results.py \
        --config-a /tmp/config_a_results.json \
        --config-b /tmp/config_b_results.json \
        --region us-east-1
"""

import argparse
import json
import os
import datetime
import boto3
import numpy as np

REGION = 'us-east-1'


def load(path):
    with open(path) as f:
        return json.load(f)


def fetch_cloudwatch_inference(region, minutes=60):
    """Pull average InferenceLatency from CloudWatch (published by inference component)."""
    cw    = boto3.client('cloudwatch', region_name=region)
    end   = datetime.datetime.utcnow()
    start = end - datetime.timedelta(minutes=minutes)
    resp  = cw.get_metric_statistics(
        Namespace='IIoT/EdgeMetrics',
        MetricName='InferenceLatency',
        StartTime=start, EndTime=end,
        Period=3600, Statistics=['Average', 'SampleCount'],
    )
    points = resp.get('Datapoints', [])
    if not points:
        return None, None
    avg    = np.mean([p['Average'] for p in points])
    count  = sum(p['SampleCount'] for p in points)
    return avg, count


def fetch_cloudwatch_bandwidth(region, minutes=120):
    """Pull total bytes published to IoT Core from CloudWatch."""
    cw    = boto3.client('cloudwatch', region_name=region)
    end   = datetime.datetime.utcnow()
    start = end - datetime.timedelta(minutes=minutes)

    results = {}
    for label, dims in [
        ('config_a', [{'Name': 'Protocol', 'Value': 'MQTT'}]),
        ('config_b', [{'Name': 'Protocol', 'Value': 'MQTT'}]),
    ]:
        resp = cw.get_metric_statistics(
            Namespace='AWS/IoT',
            MetricName='PublishIn.Success',
            Dimensions=dims,
            StartTime=start, EndTime=end,
            Period=7200, Statistics=['Sum'],
        )
        points = resp.get('Datapoints', [])
        results[label] = sum(p['Sum'] for p in points) if points else None
    return results


def print_comparison(a, b):
    cw_inf, cw_count = fetch_cloudwatch_inference(REGION)

    bw_save  = b['bandwidth_saving_pct']
    a_bytes  = a['bytes_sent_total']
    b_bytes  = b['bytes_to_cloud']

    print('\n' + '=' * 65)
    print('  IIoT HYBRID CLOUD-EDGE ARCHITECTURE — RESULTS SUMMARY')
    print('=' * 65)
    print(f'  {"Metric":<40} {"Config A":>10} {"Config B":>10}')
    print('-' * 65)
    print(f'  {"Latency mean (ms)":<40} {a["latency_mean_ms"]:>10.1f} {b["inf_latency_mean_ms"]:>10.2f}')
    print(f'  {"Latency P95 (ms)":<40} {a["latency_p95_ms"]:>10.1f} {b["inf_latency_p95_ms"]:>10.2f}')
    print(f'  {"Total bytes to cloud (KB)":<40} {a_bytes/1024:>10.1f} {b_bytes/1024:>10.1f}')
    print(f'  {"Bandwidth saving (%)":<40} {"baseline":>10} {bw_save:>9.1f}%')
    print(f'  {"Readings forwarded to cloud":<40} {a["n_readings"]:>10} {b["n_anomalies"]:>10}')
    print(f'  {"Cloud forwarding rate":<40} {"100%":>10} {b["n_anomalies"]/b["n_readings"]:.0%}:>10}')
    if cw_inf:
        print(f'  {"CloudWatch avg inference (ms)":<40} {"N/A":>10} {cw_inf:>10.2f}')
    print('=' * 65)

    print('\n  KEY FINDINGS FOR PAPER')
    print(f'  • Latency reduction: {a["latency_mean_ms"]:.0f} ms → {b["inf_latency_mean_ms"]:.1f} ms'
          f' ({(1 - b["inf_latency_mean_ms"]/a["latency_mean_ms"])*100:.0f}% faster)')
    print(f'  • Bandwidth reduction: {bw_save:.0f}% less data sent to cloud')
    print(f'  • Edge sub-100ms target: {"MET" if b["inf_latency_p95_ms"] < 100 else "MISSED"}'
          f' (P95 = {b["inf_latency_p95_ms"]:.1f} ms)')

    summary = {
        'config_a': a,
        'config_b': b,
        'comparison': {
            'latency_reduction_pct': round((1 - b['inf_latency_mean_ms'] / a['latency_mean_ms']) * 100, 1),
            'bandwidth_saving_pct':  bw_save,
            'sub_100ms_met':         b['inf_latency_p95_ms'] < 100,
        }
    }
    out = '/tmp/results_comparison.json'
    with open(out, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f'\n  Full comparison saved → {out}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config-a', default='/tmp/config_a_results.json')
    parser.add_argument('--config-b', default='/tmp/config_b_results.json')
    parser.add_argument('--region',   default='us-east-1')
    args = parser.parse_args()

    REGION = args.region
    a = load(args.config_a)
    b = load(args.config_b)
    print_comparison(a, b)
