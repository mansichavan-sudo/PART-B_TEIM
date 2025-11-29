# recommender/engines/rule_based.py

def rule_based_recommendation(lead_type, service_type, pest_issue, past_purchases, customer_category):
    upsell = []
    cross_sell = []

    # UPSSELL LOGIC
    if lead_type in ["hot", "warm"]:
        upsell.append("Premium AMC Service")
    if pest_issue in ["termites", "bed bugs"]:
        upsell.append("Intensive Treatment Upgrade")

    if customer_category == "repeat":
        upsell.append("Annual Maintenance Plan")

    # CROSS SELL LOGIC
    if service_type == "service":
        cross_sell.append("Pest Control Addon Spray")
    if pest_issue == "cockroaches":
        cross_sell.append("Kitchen Deep Clean")

    if "AMC" in past_purchases:
        upsell.append("AMC Renewal Discount")

    # PRIORITY
    priority = "upsell_first" if lead_type == "hot" else "crosssell_first"

    return {
        "upsell": list(set(upsell)),
        "cross_sell": list(set(cross_sell)),
        "priority": priority
    }
