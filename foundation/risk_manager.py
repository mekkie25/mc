class RiskManager:
    def __init__(self, default_breakeven_trigger=0.80):
        self.default_breakeven_trigger = default_breakeven_trigger

    def evaluate_trade_management(self, current_price, entry_price, initial_stop, targets):
        """Determines if a stop should be moved to breakeven or a target scaled out."""
        # Risk management logic engine 
        distance_to_target = abs(targets[0]['price'] - entry_price)
        current_distance = abs(current_price - entry_price)
        
        # 80% to target = move stop to breakeven
        if current_distance >= (distance_to_target * self.default_breakeven_trigger):
            return {'action': 'MOVE_STOP', 'new_stop': entry_price}
            
        return {'action': 'HOLD'}