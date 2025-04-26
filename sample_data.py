import random
from datetime import datetime, timedelta
from data_model import LiveOpsChange, MetricMeasurement, KnowledgeRepository

def generate_sample_data(num_changes: int = 500) -> KnowledgeRepository:
    """Generate sample live ops changes and metrics for testing."""
    repo = KnowledgeRepository()
    
    # Define categories with specific descriptions and expected impacts
    category_templates = {
        "Add Slot": {
            "descriptions": [
                "Added new '{theme}' slot to {position}",
                "Released '{theme}' slot in {position} position",
                "Launched new '{theme}' slot machine in {position}"
            ],
            "themes": [
                "Egyptian Gold", "Lucky Dragons", "Wild West", "Mystic Fortune", 
                "Galactic Gems", "Treasure Island", "Phoenix Rise", "Diamond Deluxe",
                "Pirate's Bounty", "Golden Buddha", "Mermaid's Secret", "Aztec Empire"
            ],
            "positions": [
                "front page", "VIP room", "featured section", "new games section",
                "top row", "popular games", "recommended games"
            ],
            "impacts": {
                "revenue": ["increase", "increase", "neutral"],
                "dau": ["increase", "increase", "neutral"],
                "retention": ["increase", "neutral"],
                "session_length": ["increase", "increase", "neutral"],
                "conversion_rate": ["increase", "neutral"]
            },
            "tags": ["New Content", "Revenue Driver", "Engagement", "Content"]
        },
        "Remove Slot": {
            "descriptions": [
                "Removed '{theme}' slot from {position} due to {reason}",
                "Discontinued '{theme}' slot because of {reason}",
                "Pulled '{theme}' slot from {position} - {reason}"
            ],
            "themes": [
                "Fruit Fiesta", "Space Odyssey", "Neon Nights", "Fantasy Kingdom", 
                "Vegas Deluxe", "Thunder Cash", "Fairy Magic", "Prehistoric Giants",
                "Cash Tornado", "Lucky Clover", "Ninja Stars", "Samurai Fortune"
            ],
            "positions": [
                "front page", "VIP room", "featured section", "bottom row",
                "popular games section", "recommended games"
            ],
            "reasons": [
                "poor performance", "technical issues", "low engagement", 
                "seasonal rotation", "licensing expiration", "content refresh",
                "underperforming metrics", "outdated graphics"
            ],
            "impacts": {
                "revenue": ["neutral", "decrease", "increase"],
                "dau": ["neutral", "decrease"],
                "retention": ["neutral", "decrease", "increase"],
                "session_length": ["decrease", "neutral"],
                "conversion_rate": ["neutral", "decrease", "increase"]
            },
            "tags": ["Content Removal", "Performance Optimization", "Rotation"]
        },
        "Add Sneak Peek Slot": {
            "descriptions": [
                "Added sneak peek of upcoming '{theme}' slot for {duration}",
                "Launched {duration} preview of new '{theme}' slot in {position}",
                "Released sneak peek version of '{theme}' slot for {duration}"
            ],
            "themes": [
                "Treasure Hunters", "Cosmic Clash", "Dynasty Fortune", "Magical Forest", 
                "Ocean Riches", "Monster Bash", "Royal Gems", "Wild Safari",
                "Mythical Creatures", "Ancient Wonders", "Space Adventure", "Golden Empire"
            ],
            "durations": [
                "48 hours", "weekend", "3 days", "VIP weekend", "limited time",
                "24 hours", "week-long", "exclusive preview"
            ],
            "positions": [
                "featured section", "new games spotlight", "coming soon section",
                "VIP room", "exclusive preview area", "special events tab"
            ],
            "impacts": {
                "revenue": ["increase", "neutral"],
                "dau": ["increase", "increase", "neutral"],
                "retention": ["increase", "neutral"],
                "session_length": ["increase", "neutral"],
                "conversion_rate": ["neutral", "increase"]
            },
            "tags": ["Preview", "Limited Time", "Engagement", "Promotion", "Upcoming Content"]
        },
        "Extend Scratcher": {
            "descriptions": [
                "Extended '{theme}' scratcher campaign by {duration}",
                "Prolonged '{theme}' scratcher availability for additional {duration}",
                "Added {duration} extension to '{theme}' scratcher promotion"
            ],
            "themes": [
                "Golden Ticket", "Lucky 7s", "Cash Explosion", "Mega Millions", 
                "Jackpot Jubilee", "Diamond Dust", "Fortune Favors", "Treasure Chest",
                "Ruby Rush", "Sapphire Surprise", "Emerald Extravaganza", "Platinum Play"
            ],
            "durations": [
                "3 days", "weekend", "1 week", "5 days", "48 hours",
                "4 days", "limited time", "24 hours"
            ],
            "impacts": {
                "revenue": ["increase", "neutral"],
                "dau": ["increase", "neutral"],
                "retention": ["increase", "neutral"],
                "session_length": ["increase", "neutral"],
                "conversion_rate": ["neutral", "increase", "decrease"]
            },
            "tags": ["Extension", "Promotion", "Engagement", "Revenue Driver"]
        },
        "Slot Track Positioning adjustment": {
            "descriptions": [
                "Moved '{theme}' slot from {old_position} to {new_position}",
                "Adjusted position of '{theme}' slot from {old_position} to {new_position}",
                "Repositioned '{theme}' slot to {new_position} from {old_position}"
            ],
            "themes": [
                "Lucky Lions", "Golden Phoenix", "Crystal Cave", "Desert Treasure", 
                "Arctic Fortune", "Tropical Paradise", "Mystic Moon", "Dragon's Lair",
                "Panda Fortunes", "Viking Victory", "Pharaoh's Gold", "Aztec Adventure"
            ],
            "old_positions": [
                "bottom row", "page 2", "middle section", "secondary lobby",
                "side banner", "seasonal section", "new games", "bottom of lobby"
            ],
            "new_positions": [
                "top row", "front page", "featured section", "prime placement",
                "center position", "VIP section", "prominent position", "main lobby"
            ],
            "impacts": {
                "revenue": ["increase", "neutral", "decrease"],
                "dau": ["increase", "neutral"],
                "retention": ["neutral"],
                "session_length": ["increase", "neutral"],
                "conversion_rate": ["increase", "neutral", "decrease"]
            },
            "tags": ["UI Adjustment", "Visibility Change", "Optimization"]
        },
        "Cooldown adjustments": {
            "descriptions": [
                "Reduced cooldown on {feature} from {old} to {new}",
                "Increased cooldown period for {feature} from {old} to {new}",
                "Adjusted {feature} cooldown timer to {new} from {old}"
            ],
            "features": [
                "daily bonuses", "hourly rewards", "free spins", "gift requests", 
                "friend bonuses", "mystery boxes", "challenge rewards", "VIP perks",
                "wheel spins", "collector's bonus", "streak rewards", "mini-games"
            ],
            "old_timers": [
                "24 hours", "4 hours", "12 hours", "30 minutes", 
                "6 hours", "8 hours", "2 hours", "48 hours"
            ],
            "new_timers": [
                "12 hours", "2 hours", "6 hours", "15 minutes", 
                "4 hours", "24 hours", "1 hour", "3 hours"
            ],
            "impacts": {
                "revenue": ["increase", "decrease", "neutral"],
                "dau": ["increase", "neutral"],
                "retention": ["increase", "neutral"],
                "session_length": ["increase", "decrease", "neutral"],
                "conversion_rate": ["neutral", "decrease", "increase"]
            },
            "tags": ["Game Balance", "Engagement", "Retention", "Session Frequency"]
        },
        "Purchase Quests": {
            "descriptions": [
                "Added new '{theme}' purchase quest with {reward} reward",
                "Launched '{theme}' spending quest offering {reward}",
                "Implemented new purchase milestone quest: '{theme}' with {reward}"
            ],
            "themes": [
                "Summer Splash", "Treasure Hunter", "VIP Elite", "Whale's Journey", 
                "High Roller", "Jackpot Chase", "Big Spender", "Fortune Seeker",
                "Diamond Club", "Royal Flush", "Platinum Path", "Golden Opportunity"
            ],
            "rewards": [
                "exclusive avatar", "rare collection item", "VIP status boost", 
                "bonus multiplier", "unique profile frame", "special badge",
                "limited edition item", "bonus spins package", "premium currency"
            ],
            "impacts": {
                "revenue": ["increase", "increase", "neutral"],
                "dau": ["neutral", "increase"],
                "retention": ["increase", "neutral"],
                "session_length": ["increase", "neutral"],
                "conversion_rate": ["increase", "neutral"]
            },
            "tags": ["Monetization", "Engagement", "Reward System", "VIP", "Progression"]
        },
        "Test Configurations": {
            "descriptions": [
                "Tested variant {variant} of {feature} for {segment}",
                "A/B testing {feature} configuration {variant} with {segment}",
                "Experimental {feature} settings (variant {variant}) for {segment}"
            ],
            "features": [
                "first purchase offer", "tutorial flow", "bonus structure", "UI layout", 
                "reward distribution", "progression curve", "pricing model", "payout frequency",
                "win celebration", "loyalty rewards", "daily challenges", "store layout"
            ],
            "variants": ["A", "B", "C", "D", "2.1", "3.5", "X", "beta"],
            "segments": [
                "new users", "7-day retention cohort", "non-spenders", "lapsed players", 
                "high rollers", "casual players", "weekend players", "returning users",
                "Android users", "iOS users", "mid-tier spenders", "social players"
            ],
            "impacts": {
                "revenue": ["neutral", "increase", "decrease"],
                "dau": ["neutral", "increase", "decrease"],
                "retention": ["neutral", "increase", "decrease"],
                "session_length": ["neutral", "increase", "decrease"],
                "conversion_rate": ["neutral", "increase", "decrease"]
            },
            "tags": ["Test", "Experiment", "Optimization", "A/B Test", "Data-Driven"]
        },
        "Sale Themes": {
            "descriptions": [
                "Launched {holiday} themed sale with {discount} off",
                "Released special {holiday} sale offering {discount} discount",
                "Implemented {holiday} themed store promotion with {discount}"
            ],
            "holidays": [
                "Valentine's Day", "Halloween", "Christmas", "New Year", 
                "Thanksgiving", "Summer", "Spring", "Anniversary",
                "Black Friday", "Cyber Monday", "Easter", "Independence Day"
            ],
            "discounts": [
                "50%", "buy one get one free", "2x value", "30%", 
                "70%", "3x bonus", "40%", "special bundle",
                "progressive discount", "tiered rewards", "25%", "60%"
            ],
            "impacts": {
                "revenue": ["increase", "increase", "neutral"],
                "dau": ["increase", "neutral"],
                "retention": ["increase", "neutral"],
                "session_length": ["increase", "neutral"],
                "conversion_rate": ["increase", "increase", "neutral"]
            },
            "tags": ["Sale", "Promotion", "Seasonal", "Limited Time", "Monetization"]
        },
        "RYD Multiplier": {
            "descriptions": [
                "Increased Roll Your Dice multiplier to {multiplier}x for {duration}",
                "Special {multiplier}x multiplier for Roll Your Dice event lasting {duration}",
                "Roll Your Dice bonus multiplier: {multiplier}x for {duration}"
            ],
            "multipliers": ["2", "3", "4", "5", "2.5", "1.5", "3.5", "10"],
            "durations": [
                "weekend", "24 hours", "48 hours", "3 days", 
                "limited time", "special event", "day-long", "holiday period"
            ],
            "impacts": {
                "revenue": ["increase", "neutral"],
                "dau": ["increase", "neutral"],
                "retention": ["increase", "neutral"],
                "session_length": ["increase", "neutral"],
                "conversion_rate": ["increase", "neutral"]
            },
            "tags": ["Event", "Promotion", "Engagement", "Limited Time", "Special Feature"]
        },
        "Run Trident Trials": {
            "descriptions": [
                "Launched Trident Trials event with {theme} theme for {duration}",
                "Started {theme} Trident Trials tournament running for {duration}",
                "Released special {theme} edition of Trident Trials for {duration}"
            ],
            "themes": [
                "Deep Sea", "Neptune's Wrath", "Ocean's Bounty", "Atlantis", 
                "Pirates' Revenge", "Kraken's Lair", "Mermaid's Grotto", "Poseidon's Realm",
                "Coral Kingdom", "Sunken Treasure", "Mythical Waters", "Sea Monster"
            ],
            "durations": [
                "weekend", "7 days", "5 days", "3 days", 
                "limited time", "2 weeks", "special period", "extended weekend"
            ],
            "impacts": {
                "revenue": ["increase", "neutral"],
                "dau": ["increase", "increase", "neutral"],
                "retention": ["increase", "neutral"],
                "session_length": ["increase", "increase", "neutral"],
                "conversion_rate": ["neutral", "increase"]
            },
            "tags": ["Tournament", "Event", "Engagement", "Competition", "Limited Time"]
        },
        "BOGO": {
            "descriptions": [
                "Added Buy One Get One Free offer on {package} package",
                "Launched BOGO promotion for {package} purchase",
                "Special BOGO deal on {package} for {duration}"
            ],
            "packages": [
                "coin", "gem", "VIP points", "special bundle", 
                "premium currency", "booster", "power-up", "collector's item",
                "mega pack", "starter bundle", "deluxe pack", "royal chest"
            ],
            "durations": [
                "24 hours", "weekend", "limited time", "48 hours", 
                "flash sale", "special event", "3 days", "holiday period"
            ],
            "impacts": {
                "revenue": ["increase", "increase", "neutral"],
                "dau": ["increase", "neutral"],
                "retention": ["increase", "neutral"],
                "session_length": ["neutral", "increase"],
                "conversion_rate": ["increase", "increase", "neutral"]
            },
            "tags": ["Sale", "Promotion", "Value", "Limited Time", "Monetization"]
        },
        "RTP Adjustments": {
            "descriptions": [
                "Adjusted {direction} RTP for {slot_type} slots by {percent}%",
                "Modified RTP {direction} by {percent}% for {slot_type} machines",
                "Tuned {slot_type} slots with {percent}% {direction} RTP adjustment"
            ],
            "directions": ["up", "down"],
            "slot_types": [
                "high volatility", "low stakes", "progressive jackpot", "classic", 
                "video", "themed", "bonus heavy", "free spin focused",
                "new", "underperforming", "popular", "seasonal"
            ],
            "percents": ["2", "5", "3", "1.5", "4", "2.5", "3.5", "1"],
            "impacts": {
                "revenue": ["increase", "decrease", "neutral"],
                "dau": ["neutral", "increase", "decrease"],
                "retention": ["increase", "decrease", "neutral"],
                "session_length": ["increase", "decrease", "neutral"],
                "conversion_rate": ["neutral", "increase", "decrease"]
            },
            "tags": ["Game Balance", "Economy", "Tuning", "Technical"]
        },
        "Pearly Rush Event": {
            "descriptions": [
                "Launched Pearly Rush event with {theme} theme for {duration}",
                "Started {theme} Pearly Rush promotion running for {duration}",
                "Released special {theme} edition of Pearly Rush for {duration}"
            ],
            "themes": [
                "Ocean Depths", "Mermaid's Treasure", "Underwater Kingdom", "Oyster Bay", 
                "Shell Collector", "Pearl Hunter", "Jewel of the Sea", "Reef Adventure",
                "Tidal Wave", "Ocean's Gift", "Nautical Wonders", "Marine Mysteries"
            ],
            "durations": [
                "weekend", "3 days", "5 days", "week-long", 
                "limited time", "extended weekend", "special period", "holiday event"
            ],
            "impacts": {
                "revenue": ["increase", "neutral"],
                "dau": ["increase", "neutral"],
                "retention": ["increase", "neutral"],
                "session_length": ["increase", "neutral"],
                "conversion_rate": ["increase", "neutral"]
            },
            "tags": ["Event", "Promotion", "Engagement", "Collection", "Limited Time"]
        },
        "Dealers Edge Event": {
            "descriptions": [
                "Launched Dealers Edge event with {multiplier}x multiplier for {duration}",
                "Started Dealers Edge promotion with {multiplier}x bonus for {duration}",
                "Released special Dealers Edge event: {multiplier}x rewards for {duration}"
            ],
            "multipliers": ["2", "3", "1.5", "2.5", "4", "5", "3.5", "double"],
            "durations": [
                "weekend", "24 hours", "48 hours", "3 days", 
                "limited time", "special event", "day-long", "holiday period"
            ],
            "impacts": {
                "revenue": ["increase", "neutral"],
                "dau": ["increase", "neutral"],
                "retention": ["increase", "neutral"],
                "session_length": ["increase", "neutral"],
                "conversion_rate": ["increase", "neutral"]
            },
            "tags": ["Event", "Promotion", "Engagement", "Table Games", "Limited Time"]
        }
    }
    
    # List of all categories
    categories = list(category_templates.keys())
    
    # Common metrics across all changes
    metrics = ["revenue", "dau", "retention", "session_length", "conversion_rate"]
    
    # Generate random changes over the past 30 days
    start_date = datetime.now() - timedelta(days=30)
    
    for i in range(num_changes):
        # Select a random category for this change
        category = random.choice(categories)
        template = category_templates[category]
        
        # Create change date
        change_date = start_date + timedelta(days=random.randint(0, 29), 
                                            hours=random.randint(0, 23),
                                            minutes=random.randint(0, 59))
        
        # Generate description based on template
        description_template = random.choice(template["descriptions"])
        
        # Fill in the template with random values
        if category == "Add Slot":
            description = description_template.format(
                theme=random.choice(template["themes"]),
                position=random.choice(template["positions"])
            )
        elif category == "Remove Slot":
            description = description_template.format(
                theme=random.choice(template["themes"]),
                position=random.choice(template["positions"]),
                reason=random.choice(template["reasons"])
            )
        elif category == "Add Sneak Peek Slot":
            description = description_template.format(
                theme=random.choice(template["themes"]),
                duration=random.choice(template["durations"]),
                position=random.choice(template["positions"])
            )
        elif category == "Extend Scratcher":
            description = description_template.format(
                theme=random.choice(template["themes"]),
                duration=random.choice(template["durations"])
            )
        elif category == "Slot Track Positioning adjustment":
            description = description_template.format(
                theme=random.choice(template["themes"]),
                old_position=random.choice(template["old_positions"]),
                new_position=random.choice(template["new_positions"])
            )
        elif category == "Cooldown adjustments":
            old_timer = random.choice(template["old_timers"])
            # Make sure new timer is different from old timer
            new_timer = old_timer
            while new_timer == old_timer:
                new_timer = random.choice(template["new_timers"])
                
            description = description_template.format(
                feature=random.choice(template["features"]),
                old=old_timer,
                new=new_timer
            )
        elif category == "Purchase Quests":
            description = description_template.format(
                theme=random.choice(template["themes"]),
                reward=random.choice(template["rewards"])
            )
        elif category == "Test Configurations":
            description = description_template.format(
                variant=random.choice(template["variants"]),
                feature=random.choice(template["features"]),
                segment=random.choice(template["segments"])
            )
        elif category == "Sale Themes":
            description = description_template.format(
                holiday=random.choice(template["holidays"]),
                discount=random.choice(template["discounts"])
            )
        elif category == "RYD Multiplier":
            description = description_template.format(
                multiplier=random.choice(template["multipliers"]),
                duration=random.choice(template["durations"])
            )
        elif category == "Run Trident Trials":
            description = description_template.format(
                theme=random.choice(template["themes"]),
                duration=random.choice(template["durations"])
            )
        elif category == "BOGO":
            description = description_template.format(
                package=random.choice(template["packages"]),
                duration=random.choice(template.get("durations", ["limited time"]))
            )
        elif category == "RTP Adjustments":
            description = description_template.format(
                direction=random.choice(template["directions"]),
                slot_type=random.choice(template["slot_types"]),
                percent=random.choice(template["percents"])
            )
        elif category == "Pearly Rush Event":
            description = description_template.format(
                theme=random.choice(template["themes"]),
                duration=random.choice(template["durations"])
            )
        elif category == "Dealers Edge Event":
            description = description_template.format(
                multiplier=random.choice(template["multipliers"]),
                duration=random.choice(template["durations"])
            )
        else:
            description = f"Generic {category} change"
        
        # Expected impact
        expected_impact = {}
        for metric in random.sample(metrics, k=random.randint(2, 5)):  # At least 2 metrics, up to all 5
            if metric in template["impacts"]:
                expected_impact[metric] = random.choice(template["impacts"][metric])
            else:
                expected_impact[metric] = random.choice(["increase", "decrease", "neutral"])
            
        # Create the change object
        change_id = f"change_{i}"
        change = LiveOpsChange(
            change_id=change_id,
            timestamp=change_date,
            category=category,
            description=description,
            expected_impact=expected_impact,
            tags=[random.choice(template["tags"])]
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
                    impact_multiplier = random.uniform(1.05, 1.35)
                elif expected_impact[metric_name] == "decrease":
                    impact_multiplier = random.uniform(0.65, 0.95)
                else:  # neutral
                    impact_multiplier = random.uniform(0.97, 1.03)
            
            # Add some randomness to make it realistic
            impact_multiplier *= random.uniform(0.95, 1.05)
            
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