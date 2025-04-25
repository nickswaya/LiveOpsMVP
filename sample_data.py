import random
from datetime import datetime, timedelta
from data_model import KnowledgeRepository, LiveOpsChange, MetricMeasurement

def generate_sample_data(num_changes: int = 50) -> KnowledgeRepository:
    """Generate sample live ops changes and metrics for testing."""
    repo = KnowledgeRepository()
    
    categories = ["Sale", "Event", "Feature Update", "UI Change", "Balance Adjustment"]
    metrics = ["revenue", "dau", "retention", "session_length", "conversion_rate"]
    
    # Generate random changes over the past 30 days
    start_date = datetime.now() - timedelta(days=30)
    
    for i in range(num_changes):
        # Create a change
        change_date = start_date + timedelta(days=random.randint(0, 29))
        category = random.choice(categories)
        
        # Generate description based on category
        if category == "Sale":
            description = f"{random.choice(['BOGO', '2x', '3x', '50% off'])} sale on {random.choice(['coins', 'gems', 'boosters', 'special items'])}"
        elif category == "Event":
            description = f"{random.choice(['Weekend', 'Special', 'Holiday', 'Seasonal'])} {random.choice(['tournament', 'challenge', 'collection', 'competition'])} event"
        elif category == "Feature Update":
            description = f"Updated {random.choice(['bonus wheel', 'daily rewards', 'friend system', 'achievements'])}"
        elif category == "UI Change":
            description = f"Changed {random.choice(['lobby layout', 'store display', 'game UI', 'notification system'])}"
        else:  # Balance Adjustment
            description = f"Adjusted {random.choice(['payout rates', 'difficulty curve', 'progression speed', 'reward distribution'])}"
        
        # Expected impact
        expected_impact = {}
        for metric in random.sample(metrics, k=random.randint(1, 3)):
            expected_impact[metric] = random.choice(["increase", "decrease", "neutral"])
            
        # Create the change object
        change_id = f"change_{i}"
        change = LiveOpsChange(
            change_id=change_id,
            timestamp=change_date,
            category=category,
            description=description,
            expected_impact=expected_impact,
            tags=[random.choice(["VIP", "New Users", "Retention", "Monetization", "Engagement"])]
        )
        repo.add_change(change)
        
        # Generate metrics for this change
        for metric_name in metrics:
            # Base values for different metrics
            base_values = {
                "revenue": random.uniform(10000, 50000),
                "dau": random.uniform(10000, 100000),
                "retention": random.uniform(20, 40),
                "session_length": random.uniform(10, 30),
                "conversion_rate": random.uniform(2, 8)
            }
            
            # Generate before value
            before_value = base_values[metric_name]
            
            # Generate after value based on expected impact
            impact_multiplier = 1.0
            if metric_name in expected_impact:
                if expected_impact[metric_name] == "increase":
                    impact_multiplier = random.uniform(1.05, 1.25)
                elif expected_impact[metric_name] == "decrease":
                    impact_multiplier = random.uniform(0.75, 0.95)
                else:  # neutral
                    impact_multiplier = random.uniform(0.98, 1.02)
            
            # Add some randomness to make it realistic
            impact_multiplier *= random.uniform(0.9, 1.1)
            
            after_value = before_value * impact_multiplier
            
            # Create metric measurement
            metric = MetricMeasurement(
                change_id=change_id,
                metric_name=metric_name,
                before_value=before_value,
                after_value=after_value
            )
            repo.add_metric(metric)
    
    return repo