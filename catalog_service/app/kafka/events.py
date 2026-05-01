from uuid import UUID

from app.config import settings
from app.kafka.producer import KafkaProductProducer
from app.schemas.product_event import ProductUpdatedEvent, ProductUpdatedData

producer = KafkaProductProducer(bootstrap_servers=settings.kafka_bootstrap_servers)

def send_product_updated_event(product_id: UUID, old_values: dict, new_values: dict):
    event = ProductUpdatedEvent(data=ProductUpdatedData(product_id=product_id, old_values=old_values,
                                                        new_values=new_values))
    return producer.send_product_updated(event, key=str(product_id))
