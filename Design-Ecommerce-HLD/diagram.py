from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import User
from diagrams.onprem.compute import Server
from diagrams.onprem.database import MongoDB, MySQL, Cassandra
from diagrams.onprem.inmemory import Redis
from diagrams.onprem.queue import Kafka
from diagrams.onprem.analytics import Spark
from diagrams.custom import Custom

with Diagram("System Architecture", show=False):

    with Cluster("User Interaction"):
        user_home = Server("User Home Page")
        user_search = Server("User Search Page")
        user_purchase = Server("User Purchase Flow")

        recommendation_service = Server("Recommendation Service")
        search_service = Server("Search Service")
        order_taking_service = Server("Order Taking Service")

        user_home >> Edge(label="LB") >> recommendation_service
        user_search >> Edge(label="LB") >> search_service
        user_purchase >> Edge(label="LB") >> order_taking_service

    with Cluster("Search Flow"):
        wishlist_service = Server("Wishlist Service")
        search_consumer = Server("Search Consumer")
        cart_service = Server("Cart Service")
        serviceability_tat_service = Server("Serviceability + TAT Service")

        cart_db = MySQL("Cart DB")
        wishlist_db = MySQL("Wishlist DB")
        cassandra_db = Cassandra("Cassandra")

        search_service >> wishlist_service
        search_service >> Edge(label="Elastic Search") >> search_consumer
        search_service >> cart_service
        cart_service >> Edge(label="MySQL") >> cart_db
        wishlist_service >> Edge(label="MySQL") >> wishlist_db
        cart_service >> serviceability_tat_service
        serviceability_tat_service >> Edge(label="Serviceability") >> recommendation_service
        recommendation_service >> Edge(label="Cassandra") >> cassandra_db

    with Cluster("Item Service"):
        item_service = Server("Item Service")
        item_db = MongoDB("Item DB")
        spark_streaming = Spark("Spark Streaming")
        spark_cluster = Spark("Spark Cluster")
        hadoop_cluster = Custom("Hadoop Cluster", "./icons/hadoop.png")

        item_service >> Edge(label="MongoDB") >> item_db
        item_service >> recommendation_service
        item_service >> Edge(label="Spark Streaming") >> spark_streaming
        spark_streaming >> Edge(label="Spark Cluster") >> spark_cluster
        spark_streaming >> Edge(label="Hadoop Cluster") >> hadoop_cluster

    with Cluster("Kafka Event"):
        kafka = Kafka("KAFKA")
        warehouse_service = Server("Warehouse Service")
        inbound_service = Server("Inbound Service")
        logistics_service = Server("Logistics Service")

        spark_streaming >> Edge(label="Kafka") >> kafka
        kafka >> warehouse_service
        kafka >> inbound_service
        kafka >> logistics_service
        kafka >> search_consumer

    with Cluster("Purchase Flow"):
        oms_db = MySQL("OMS DB")
        payment_service = Server("Payment Service")
        order_processing_service = Server("Order Processing Service")
        historical_order_service = Server("Historical Order Service")
        archival_service = Server("Archival Service")
        inventory_service = Server("Inventory Service")
        inventory_db = MySQL("Inventory DB")
        redis_db = Redis("Redis")

        order_taking_service >> Edge(label="MySQL") >> oms_db
        order_taking_service >> payment_service
        order_taking_service >> order_processing_service
        order_processing_service >> historical_order_service
        historical_order_service >> Edge(label="Cassandra") >> cassandra_db
        order_processing_service >> archival_service
        order_processing_service >> Edge(label="Kafka") >> kafka
        order_taking_service >> inventory_service
        inventory_service >> Edge(label="MySQL") >> inventory_db
        inventory_service >> recommendation_service
        order_processing_service >> Edge(label="Redis") >> redis_db

    with Cluster("Processing"):
        spark_jobs = Spark("Spark Jobs")

        inventory_service >> spark_jobs
        spark_jobs >> Edge(label="Hadoop Cluster") >> hadoop_cluster
        spark_jobs >> spark_streaming
        spark_jobs >> recommendation_service

    notification_service = Server("Notification Service")
    kafka >> Edge(label="Notification") >> notification_service
