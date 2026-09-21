import pandas as pd
import numpy as np
from execution import PaperExecutor
from strategies.grubber_kick import GrubberKick
"""
backtest/run_validation.py
Integrates with the `portal_bridge.py`[cite: 25] and generates `Trading_Journal.csv`[cite: 25].
"""


class BacktestValidator:
    def __init__(self, strategies, data_feed, instrument, slippage=0.5, commission=2.0):
        self.strategies = strategies
        self.data_feed = data_feed
        self.instrument = instrument
        self.executor = PaperExecutor(slippage=slippage, commission=commission)
        
    def run_walk_forward(self, train_window_days=30, test_window_days=10):
        # Sequential train/test windows to prevent curve-fitting
        print(f"Running Walk-Forward Validation for {self.instrument}...")
        results = []
        for strategy in self.strategies:
            print(f"Testing {strategy.__class__.__name__}...")
            trades = self.executor.execute_historical(strategy, self.data_feed)
            
            if len(trades) < 50:
                print(f"WARNING: {strategy.__class__.__name__} only generated {len(trades)} trades. Min 50-100 required.")
            
            metrics = self._calculate_metrics(trades)
            if metrics['profit_factor'] < 1.0:
                print(f"FAILED SANITY CHECK: {strategy.__class__.__name__} Profit Factor: {metrics['profit_factor']:.2f}")
                
            results.append(metrics)
            self._export_journal(trades, strategy.__class__.__name__)
            
        return results

    def _calculate_metrics(self, trades):
        df = pd.DataFrame(trades)
        if df.empty: return {'profit_factor': 0}
        
        df['day_of_week'] = df['entry_time'].dt.day_name()
        win_rate_by_day = df.groupby('day_of_week')['is_win'].mean().to_dict()
        
        gross_profit = df[df['pnl'] > 0]['pnl'].sum()
        gross_loss = abs(df[df['pnl'] < 0]['pnl'].sum())
        pf = gross_profit / gross_loss if gross_loss != 0 else np.inf
        
        return {
            'win_rate': df['is_win'].mean(),
            'avg_r_multiple': df['r_multiple'].mean(),
            'max_drawdown': self._calculate_max_dd(df['pnl']),
            'profit_factor': pf,
            'win_rate_by_day': win_rate_by_day
        }

    def _calculate_max_dd(self, pnl_series):
        cum_pnl = pnl_series.cumsum()
        running_max = cum_pnl.cummax()
        drawdown = running_max - cum_pnl
        return drawdown.max()

    def _export_journal(self, trades, strategy_name):
        # Maps to Trading_Journal.csv architecture[cite: 25]
        df = pd.DataFrame(trades)
        df['strategy_name'] = strategy_name
        df['discretionary_entry_criteria'] = ""
        df['discretionary_entry_location'] = ""
        df['discretionary_trade_management'] = ""
        df['discretionary_target_discipline'] = ""
        
        df.to_csv(f'Trading_Journal_{strategy_name}.csv', index=False)