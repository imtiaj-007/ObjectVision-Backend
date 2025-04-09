from typing import Dict, List
from fastapi import WebSocket
from app.schemas.subscription_schema import SubscriptionDetails

# Active WebSocket connections
active_connections: Dict[str, WebSocket] = {}

# Subscription Plans
subscription_plans: List[SubscriptionDetails] = []