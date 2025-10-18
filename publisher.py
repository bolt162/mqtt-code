# publisher.py
# Usage: python publisher.py --broker localhost --topic SHASTA/WML --csv Shasta_WML.csv
import argparse, json, time
import pandas as pd
import paho.mqtt.client as mqtt

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--broker", default="localhost")
    p.add_argument("--port", type=int, default=1883)
    p.add_argument("--topic", required=True)  # e.g., SHASTA/WML
    p.add_argument("--csv", required=True)
    p.add_argument("--rate_hz", type=float, default=5.0)  # messages per second
    return p.parse_args()

def normalize(df):
    cols = {c.lower(): c for c in df.columns}
    tcol = next((c for c in cols if any(k in c for k in ["time", "date", "timestamp"])), list(cols)[0])
    vcol = next((c for c in cols if any(k in c for k in ["wml", "taf", "level", "value", "storage"])), list(cols)[1])
    x = pd.DataFrame({
        "timestamp": pd.to_datetime(df[cols[tcol]], errors="coerce"),
        "wml_taf": pd.to_numeric(df[cols[vcol]], errors="coerce")
    }).dropna()
    return x

if __name__ == "__main__":
    args = parse_args()
    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        protocol=mqtt.MQTTv311,
    )
    client.connect(args.broker, args.port, keepalive=60)

    df = pd.read_csv(args.csv)
    df = normalize(df)

    for _, row in df.iterrows():
        payload = {
            "reservoir_id": args.topic.split("/")[0],
            "timestamp": row["timestamp"].isoformat(),
            "metric": "WML",
            "unit": "TAF",
            "value": float(row["wml_taf"]),
        }
        client.publish(args.topic, json.dumps(payload), qos=1, retain=False)
        time.sleep(1.0 / args.rate_hz)

    client.disconnect()
