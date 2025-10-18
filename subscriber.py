# subscriber.py
# One subscriber that listens to +/WML (all reservoirs) and writes a daily report.
# Usage: python subscriber.py --broker localhost --out daily_report.csv
import argparse, json, time, queue, threading, signal, sys
import pandas as pd
import paho.mqtt.client as mqtt
from datetime import datetime

q = queue.Queue()

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--broker", default="localhost")
    p.add_argument("--port", type=int, default=1883)
    p.add_argument("--topic", default="+/WML")  # wildcard for any reservoir
    p.add_argument("--out", default="daily_reservoir_report.csv")
    p.add_argument("--window_sec", type=int, default=24*3600)  # aggregation window
    return p.parse_args()

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        q.put(payload)
    except Exception as e:
        print("Bad message:", e)

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("MQTT connected")
    else:
        print(f"MQTT connect failed rc={rc}")

def write_daily(buffer, out_path):
    if not buffer:
        return 0
    df = pd.DataFrame(buffer)
    df["date"] = pd.to_datetime(df["timestamp"]).dt.date
    daily = (
        df.groupby(["date", "reservoir_id"])
          .agg(samples=("value", "count"),
               wml_min_taf=("value", "min"),
               wml_avg_taf=("value", "mean"),
               wml_max_taf=("value", "max"))
          .reset_index()
          .sort_values(["date", "reservoir_id"])
    )
    daily.to_csv(out_path, index=False)
    print(f"Wrote {out_path} with {len(daily)} rows at {datetime.now()}")
    return len(daily)

def aggregator(args, stop_event):
    buffer = []
    start = time.time()
    while not stop_event.is_set():
        try:
            item = q.get(timeout=1)
            buffer.append(item)
        except queue.Empty:
            pass

        # roll every window_sec (daily)
        if time.time() - start >= args.window_sec:
            write_daily(buffer, args.out)
            buffer.clear()
            start = time.time()

    # flush on shutdown
    write_daily(buffer, args.out)

if __name__ == "__main__":
    args = parse_args()
    stop_event = threading.Event()

    def handle_sigint(sig, frame):
        stop_event.set()
    signal.signal(signal.SIGINT, handle_sigint)

    t = threading.Thread(target=aggregator, args=(args, stop_event), daemon=True)
    t.start()

    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        protocol=mqtt.MQTTv311,
    )
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(args.broker, args.port, keepalive=60)
    client.subscribe(args.topic, qos=1)
    client.loop_forever()
