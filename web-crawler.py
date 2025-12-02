# crawler_architecture.py
# pip install diagrams
# Make sure graphviz is installed in your OS (apt / brew / choco) and is on PATH.

from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.compute import Server
from diagrams.onprem.queue import Rabbitmq
from diagrams.onprem.database import Postgresql
from diagrams.aws.storage import S3
from diagrams.onprem.monitoring import Prometheus
from diagrams.onprem.network import Nginx
from diagrams.generic.blank import Blank

graph_attr = {
    "dpi": "100"
}

with Diagram("Web Crawler - Production Architecture", show=False, direction="LR", graph_attr=graph_attr):
    # Left: seeders & ingestion
    url_seeder = Server("URL Seeder\n(seed list / seeds API)")

    with Cluster("Pre-Processing"):
        normalizer = Server("URL Normalizer\nCanonicalizer")
        duplicate = Server("Duplicate Detection\n(Bloom + Persistent)")
        seen_url_db = Postgresql("Seen URL Store\n(persistent dedupe)")

    # Frontier shards / scheduler
    with Cluster("Frontier & Scheduler\n(sharded by host)"):
        frontier_shards = Postgresql("URL Frontier Shards\n(priority, next_crawl_time)")
        url_scheduler = Server("URL Supplier / Scheduler")

    # Politeness & robots
    robots_checker = Server("robots.txt Fetcher\n& Parser")
    politeness = Server("Politeness Manager\n(per-host token buckets)")

    # Fetcher + Renderer
    html_fetcher = Server("HTML Fetcher & Renderer\n(fetch + render JS)")

    # Storage and cache
    s3_raw = S3("Raw HTML Store (S3)\n+ object metadata")
    cache_db = Postgresql("Cache DB / Fast KV\n(redirects / latest)")

    # Async processing pipeline
    html_queue = Rabbitmq("HTML Processing Queue\n(Kafka/SQS/RabbitMQ)")
    parser = Server("HTML Parser / Processor\n(extract links, metadata)")
    url_extractor = Server("URL Extractor / Filter\n(normalize, filter, priority)")
    
    # Failure handling and DLQ
    failed_db = Postgresql("Failed URLs DB\n(error info, retries)")
    dlq = Rabbitmq("DLQ (Dead Letter Queue)")

    # Observability
    monitoring = Prometheus("Monitoring & Alerts\n(metrics, tracing, logs)")

    # High-level flow edges (with labels)
    url_seeder >> Edge(label="seed URLs") >> normalizer
    normalizer >> duplicate
    duplicate >> Edge(label="new / unseen URLs") >> frontier_shards
    duplicate >> Edge(label="seen -> update stats") >> seen_url_db

    frontier_shards >> Edge(label="assign URL") >> url_scheduler
    url_scheduler >> Edge(label="check robots.txt") >> robots_checker
    robots_checker >> Edge(label="rules") >> politeness
    url_scheduler >> Edge(label="per-host token\n& schedule") >> politeness
    politeness >> Edge(label="allow request") >> html_fetcher

    # Fetcher stores raw HTML and emits messages to processing queue
    html_fetcher >> Edge(label="store HTML\n(s3 key + metadata)") >> s3_raw
    html_fetcher >> Edge(label="cache latest") >> cache_db
    html_fetcher >> Edge(label="publish\nfetch message") >> html_queue

    # Parser consumes, extracts links and content, may push new URLs back to frontier
    html_queue >> parser
    parser >> Edge(label="extract & normalize\nlinks, content-hash") >> url_extractor
    url_extractor >> Edge(label="dedupe check\n(quick bloom + persistent)") >> duplicate
    parser >> Edge(label="index / parsed doc") >> cache_db

    # Failure handling
    html_fetcher >> Edge(label="transient failures -> retry\n(exponential backoff)") >> failed_db
    html_fetcher >> Edge(label="permanent failures -> DLQ") >> dlq
    parser >> Edge(label="parser failures -> DLQ") >> dlq

    # Observability connections
    html_fetcher >> Edge(label="metrics / traces") >> monitoring
    url_scheduler >> Edge(label="metrics / traces") >> monitoring
    parser >> Edge(label="metrics / traces") >> monitoring
    duplicate >> Edge(label="metrics") >> monitoring

    # small decorative loop showing frontier -> fetch cycle
    frontier_shards >> Edge(style="dashed", label="assigned to\nfetcher cluster") >> html_fetcher

    # annotate external systems / notes (optional)
    extern = Blank("External: DNS, Internet, Target Hosts")
    html_fetcher >> Edge(label="fetches from") >> extern
