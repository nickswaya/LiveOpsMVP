from typing import Dict, Any

class DomainKnowledgeManager:
    def __init__(self):
        self.domain_context = self._build_domain_context()
    
    def _build_domain_context(self) -> Dict[str, Any]:
        """Build domain context to improve LLM understanding."""
        return {
            "concepts": {
                "BOGO": "Buy One Get One Free offers typically drive higher conversion rates and immediate revenue but may decrease long-term ARPPU (Average Revenue Per Paying User). Can cause inflated bankrolls and higher SLIB (Spins Left in Bankroll).",
                "RTP": "Return To Player adjustments directly impact player win rates and session length. Increasing RTP typically improves retention at the cost of revenue per session. It also drives higher SLIB (Spins Left in Bankroll).",
                "Cooldown": "Cooldown periods affect engagement frequency. Shorter cooldowns typically increase DAU but may decrease long-term retention.",
                "Featured Placement": "Moving content to featured positions typically increases visibility and short-term engagement.",
                "Sneek Peek": "Preview content that drives curiosity and short-term engagement, often used to test new concepts.",
                "Limited Time Event": "Creates urgency and typically drives strong short-term engagement and revenue spikes.",
                "VIP": "Features targeted at high-value players with strong monetization potential.",
                "A/B Test": "Experimental changes to measure impact before full deployment.",
                "OOC": "Out of Coins - When the player's bankroll is depleted. This drives revenue because the player is forced to buy more coins.",
                "OOC versus Churn": "Product managers must balance the risk of OOC vs churn. OOC drives revenue but can lead to player frustration and churn if not managed carefully.",
                "Spins Left in Bankroll": "Spins left in bankroll (SLIB) is the number of spins the player has left in their bankroll. This is a critical metric for product managers to monitor. If the player is nearing the end of their bankroll, they are more likely to buy more coins to continue playing.",
                "Risk of Ruin": "Players often stop playing if their bankroll is too high. They enjoy the thrill of the gamble, and if they never lose, they lose interest."
            },
            "category_contexts": {
                "Add Slot": "Adding new slot machines typically drives short-term engagement and can increase revenue if the theme and mechanics are appealing.",
                "Remove Slot": "Removing underperforming content can improve overall metrics by directing players to better performing games.",
                "RTP Adjustments": "RTP (Return To Player) is the percentage of wagers that are returned to players over time. Higher RTP is player-friendly but reduces margin.",
                "BOGO": "BOGO (Buy One Get One Free) offers are powerful conversion drivers but may reduce the perceived value of regular-priced items.",
                "Pearly Rush Event": "Collection-based event that drives engagement through completionist mechanics.",
                "Dealers Edge Event": "Table game focused event that appeals to a specific player segment interested in skill-based games."
            },
            "metric_contexts": {
                "revenue": "Direct monetization through in-app purchases. Primary business metric.",
                "dau": "Daily Active Users - measure of overall engagement and reach.",
                "retention": "Percentage of users who return after their first session. Critical for long-term success.",
                "session_length": "Time spent in-app per session. Indicator of engagement depth.",
                "conversion_rate": "Percentage of users who make a purchase. Key monetization efficiency metric.",
                "SLIB": "Spins left in bankroll (SLIB) is the number of spins the player has left in their bankroll. This is a critical metric for product managers to monitor. If the player is nearing the end of their bankroll, they are more likely to buy more coins to continue playing.",
                "OOC": "Out of Coins - When the player's bankroll is depleted. This drives revenue because the player is forced to buy more coins."
            }
        }
    
    def get_relevant_concepts(self, query: str) -> Dict[str, str]:
        """Get concepts relevant to a specific query."""
        query_lower = query.lower()
        relevant_concepts = {}
        
        for concept, description in self.domain_context["concepts"].items():
            if concept.lower() in query_lower:
                relevant_concepts[concept] = description
        
        return relevant_concepts
    
    def get_relevant_category_context(self, category: str) -> str:
        """Get context for a specific category."""
        return self.domain_context["category_contexts"].get(category, "")
    
    def get_relevant_metric_context(self, metric: str) -> str:
        """Get context for a specific metric."""
        return self.domain_context["metric_contexts"].get(metric, "")
    
    def get_context_for_query(self, query: str, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Get all relevant domain context for a query."""
        relevant_domain_context = {}
        
        # Add relevant concepts
        relevant_concepts = self.get_relevant_concepts(query)
        if relevant_concepts:
            relevant_domain_context["concepts"] = relevant_concepts
        
        # Add relevant category context
        if intent["type"] == "category_analysis" and "category" in intent["params"]:
            category_context = self.get_relevant_category_context(intent["params"]["category"])
            if category_context:
                relevant_domain_context["category_context"] = category_context
        
        # Add relevant metric context
        if intent["type"] in ["metric_impact", "metric_trend"] and "metric" in intent["params"]:
            metric_context = self.get_relevant_metric_context(intent["params"]["metric"])
            if metric_context:
                relevant_domain_context["metric_context"] = metric_context
        
        return relevant_domain_context
