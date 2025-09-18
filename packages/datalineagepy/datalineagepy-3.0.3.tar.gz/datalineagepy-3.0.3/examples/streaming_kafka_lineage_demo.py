from datalineagepy.connectors.streaming.kafka_connector import KafkaStreamingConnector
from datalineagepy import LineageTracker, LineageDataFrame
import pandas as pd
import time

# Setup tracker
tracker = LineageTracker(name="kafka_streaming_pipeline")

# Setup Kafka connector (assumes local Kafka broker)
kafka = KafkaStreamingConnector(
    topic="datalineagepy-demo", bootstrap_servers="localhost:9092")

# Simulate producing data
data = {"id": 1, "value": 42, "timestamp": time.time()}
kafka.send(data)
print("Produced message to Kafka:", data)

# Simulate consuming data
msg = kafka.receive(timeout_ms=2000)
if msg:
    print("Consumed message from Kafka:", msg)
    # Track lineage of received data
    df = pd.DataFrame([msg])
    ldf = LineageDataFrame(df, name="streamed_data", tracker=tracker)
    print("Lineage nodes:", list(tracker.nodes.keys()))
else:
    print("No message received from Kafka.")
