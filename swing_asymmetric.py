import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import List
import warnings
warnings.filterwarnings('ignore')

@dataclass
class Trade:
    direction: str
    entry_time: pd.Timestamp
    entry_price: float
    exit_time: pd.Timestamp
    exit_price: float
    pnl: float
    bars_held: int
    exit_reason: str

def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, sep=';', skiprows=1,
                     names=['TICKER','PER','DATE','TIME','OPEN','HIGH','LOW','CLOSE','VOL'])
    df['datetime'] = pd.to_datetime(df['DATE'].astype(str) + df['TIME'].astype(str).str.zfill(6), format='%Y%m%d%H%M%S')
    df = df.sort_values('datetime').reset_index(drop=True)
    return df

def find_pivots_lr(df: pd.DataFrame, left: int, right: int):
    """Asymmetric pivots: left bars before, right bars after"""
    n = len(df)
    ph = np.full(n, np.nan); pl = np.full(n, np.nan)
    high = df['HIGH'].values; low = df['LOW'].values
    for i in range(left, n - right):
        if high[i] == high[i - left:i + right + 1].max(): ph[i] = high[i]
        if low[i] == low[i - left:i + right + 1].min(): pl[i] = low[i]
    df['ph'] = ph; df['pl'] = pl
    return df

def build_swings(df):
    n = len(df)
    sh1 = np.full(n, np.nan); sh2 = np.full(n, np.nan); sh3 = np.full(n, np.nan)
    sl1 = np.full(n, np.nan); sl2 = np.full(n, np.nan); sl3 = np.full(n, np.nan)
    ph_list = []; pl_list = []
    for i in range(n):
        if not np.isnan(df['ph'].iloc[i]):
            ph_list.append((i, df['ph'].iloc[i])); 
            if len(ph_list) > 3: ph_list.pop(0)
        if not np.isnan(df['pl'].iloc[i]):
            pl_list.append((i, df['pl'].iloc[i]))
            if len(pl_list) > 3: pl_list.pop(0)
        if len(ph_list) >= 1: sh1[i] = ph_list[-1][1]
        if len(ph_list) >= 2: sh2[i] = ph_list[-2][1]
        if len(ph_list) >= 3: sh3[i] = ph_list[-3][1]
        if len(pl_list) >= 1: sl1[i] = pl_list[-1][1]
        if len(pl_list) >= 2: sl2[i] = pl_list[-2][1]
        if len(pl_list) >= 3: sl3[i] = pl_list[-3][1]
    df['sh1'] = sh1; df['sh2'] = sh2; df['sh3'] = sh3
    df['sl1'] = sl1; df['sl2'] = sl2; df['sl3'] = sl3
    return df

def atr(df: pd.DataFrame, period: int = 14) -> np.ndarray:
    high = df['HIGH'].values; low = df['LOW'].values; close = df['CLOSE'].values
    tr1 = high - low
    tr2 = np.abs(high - np.roll(close, 1))
    tr3 = np.abs(low - np.roll(close, 1))
    tr = np.maximum(np.maximum(tr1, tr2), tr3)
    tr[0] = high[0] - low[0]
    atr_vals = np.full_like(tr, np.nan)
    atr_vals[period] = tr[:period+1].mean()
    for i in range(period + 1, len(tr)):
        atr_vals[i] = (atr_vals[i-1] * (period - 1) + tr[i]) / period
    return atr_vals

def backtest(df: pd.DataFrame, left: int, right: int,
             exit_mode: str = 'fixed_tp', tp_ratio: float = 1.5,
             atr_mult_sl: float = 1.0, time_exit_bars: int = 48) -> List[Trade]:
    df = find_pivots_lr(df.copy(), left, right)
    df = build_swings(df)
    df['atr'] = atr(df, 14)
    n = len(df)
    high = df['HIGH'].values; low = df['LOW'].values; close = df['CLOSE'].values; open_p = df['OPEN'].values
    ph = df['ph'].values; pl = df['pl'].values; atr_vals = df['atr'].values
    sh1 = df['sh1'].values; sh2 = df['sh2'].values; sh3 = df['sh3'].values
    sl1 = df['sl1'].values; sl2 = df['sl2'].values; sl3 = df['sl3'].values
    
    long_fired = False; short_fired = False
    trades = []; active_trade = None
    
    for i in range(n - 1):
        # СВИНГИ становятся доступны только через right баров после экстремума
        # ta.pivothigh(left, right) на баре i подтверждается на баре i+right
        ph_available = ph[i - right] if i >= right else np.nan
        pl_available = pl[i - right] if i >= right else np.nan
        
        if not np.isnan(ph_available): short_fired = False
        if not np.isnan(pl_available): long_fired = False
        
        long_sig = False; short_sig = False
        if not np.isnan(pl_available) and not np.isnan(sl1[i]) and not np.isnan(sl2[i]) and not np.isnan(sl3[i]) and not long_fired:
            if sl3[i] > sl2[i] and sl1[i] > sl2[i]: long_sig = True; long_fired = True
        if not np.isnan(ph_available) and not np.isnan(sh1[i]) and not np.isnan(sh2[i]) and not np.isnan(sh3[i]) and not short_fired:
            if sh3[i] < sh2[i] and sh1[i] < sh2[i]: short_sig = True; short_fired = True
        
        # Exit helpers (honest)
        def exit_long(stop_price):
            if low[i] <= stop_price:
                return True, (open_p[i] if open_p[i] < stop_price else stop_price)
            return False, close[i]
        def exit_short(stop_price):
            if high[i] >= stop_price:
                return True, (open_p[i] if open_p[i] > stop_price else stop_price)
            return False, close[i]
        
        if active_trade is not None:
            trade = active_trade; exited = False; exit_price = close[i]; exit_reason = 'end'
            
            if exit_mode == 'fixed_tp':
                if trade['direction'] == 'long':
                    exited, exit_price = exit_long(trade['stop'])
                    if exited: exit_reason = 'sl'
                    elif high[i] >= trade['target']: exited, exit_price, exit_reason = True, trade['target'], 'tp'
                else:
                    exited, exit_price = exit_short(trade['stop'])
                    if exited: exit_reason = 'sl'
                    elif low[i] <= trade['target']: exited, exit_price, exit_reason = True, trade['target'], 'tp'
            
            elif exit_mode == 'time_exit':
                if trade['direction'] == 'long':
                    exited, exit_price = exit_long(trade['stop'])
                    if exited: exit_reason = 'sl'
                    elif high[i] >= trade['target']: exited, exit_price, exit_reason = True, trade['target'], 'tp'
                    elif i - trade['entry_idx'] >= time_exit_bars: exited, exit_price, exit_reason = True, close[i], 'time'
                else:
                    exited, exit_price = exit_short(trade['stop'])
                    if exited: exit_reason = 'sl'
                    elif low[i] <= trade['target']: exited, exit_price, exit_reason = True, trade['target'], 'tp'
                    elif i - trade['entry_idx'] >= time_exit_bars: exited, exit_price, exit_reason = True, close[i], 'time'
            
            if exited:
                pnl = (exit_price - trade['entry']) if trade['direction'] == 'long' else (trade['entry'] - exit_price)
                trades.append(Trade(direction=trade['direction'], entry_time=trade['entry_time'], entry_price=trade['entry'],
                                    exit_time=df['datetime'].iloc[i], exit_price=exit_price, pnl=pnl,
                                    bars_held=i - trade['entry_idx'], exit_reason=exit_reason))
                active_trade = None
                continue
        
        entry_idx = i + 1
        if entry_idx >= n: continue
        entry_price = open_p[entry_idx]
        
        if long_sig and active_trade is None:
            stop = entry_price - atr_vals[i] * atr_mult_sl if not np.isnan(atr_vals[i]) else entry_price - 50
            risk = entry_price - stop
            if risk <= 0: risk = atr_vals[i] * 0.5 if not np.isnan(atr_vals[i]) else 50
            target = entry_price + risk * tp_ratio
            active_trade = {'direction': 'long', 'entry': entry_price, 'entry_time': df['datetime'].iloc[entry_idx],
                            'entry_idx': entry_idx, 'stop': stop, 'target': target}
        elif short_sig and active_trade is None:
            stop = entry_price + atr_vals[i] * atr_mult_sl if not np.isnan(atr_vals[i]) else entry_price + 50
            risk = stop - entry_price
            if risk <= 0: risk = atr_vals[i] * 0.5 if not np.isnan(atr_vals[i]) else 50
            target = entry_price - risk * tp_ratio
            active_trade = {'direction': 'short', 'entry': entry_price, 'entry_time': df['datetime'].iloc[entry_idx],
                            'entry_idx': entry_idx, 'stop': stop, 'target': target}
    
    if active_trade is not None:
        trade = active_trade; exit_price = close[-1]
        pnl = (exit_price - trade['entry']) if trade['direction'] == 'long' else (trade['entry'] - exit_price)
        trades.append(Trade(direction=trade['direction'], entry_time=trade['entry_time'], entry_price=trade['entry'],
                            exit_time=df['datetime'].iloc[-1], exit_price=exit_price, pnl=pnl,
                            bars_held=len(df)-1-trade['entry_idx'], exit_reason='end'))
    return trades

def metrics(trades):
    if not trades: return {}
    pnls = [t.pnl for t in trades]
    wins = [p for p in pnls if p > 0]; losses = [p for p in pnls if p <= 0]
    total = sum(pnls); winrate = len(wins) / len(pnls) * 100 if pnls else 0
    avg_win = np.mean(wins) if wins else 0; avg_loss = np.mean(losses) if losses else 0
    gross_profit = sum(wins); gross_loss = abs(sum(losses))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
    equity = np.cumsum(pnls); peak = np.maximum.accumulate(equity); drawdown = peak - equity
    max_dd = np.max(drawdown) if len(drawdown) > 0 else 0
    returns = np.array(pnls); sharpe = np.mean(returns) / np.std(returns) * np.sqrt(len(returns)) if np.std(returns) > 0 else 0
    return {'trades': len(trades), 'total_pnl': round(total, 2), 'winrate': round(winrate, 1),
            'profit_factor': round(profit_factor, 2), 'avg_win': round(avg_win, 2), 'avg_loss': round(avg_loss, 2),
            'max_dd': round(max_dd, 2), 'sharpe': round(sharpe, 2),
            'tp_pct': round(len([t for t in trades if t.exit_reason == 'tp'])/len(trades)*100, 1),
            'sl_pct': round(len([t for t in trades if 'sl' in t.exit_reason])/len(trades)*100, 1)}

if __name__ == '__main__':
    DATA_PATH = '/root/.openclaw/workspace/downloads/19dac7f4-0022-89d6-8000-00006ad46102_Si_260101_260331.csv'
    df = load_data(DATA_PATH)
    print(f"Баров: {len(df)} | {df['datetime'].iloc[0]} → {df['datetime'].iloc[-1]}\n")
    
    results = []
    for left in [2, 3, 4, 5, 6, 8, 10, 12]:
        for right in [1, 2, 3, 5, 6, 8, 10]:
            for mode in ['fixed_tp', 'time_exit']:
                try:
                    trades = backtest(df, left=left, right=right, exit_mode=mode)
                    m = metrics(trades)
                    if m: results.append({'left': left, 'right': right, 'mode': mode, **m})
                except: pass
    
    results_df = pd.DataFrame(results)
    
    # Топ по Sharpe
    print("="*90)
    print("ТОП-20 ПО SHARPE (все left/right, включая left<right)")
    print("="*90)
    top = results_df.sort_values('sharpe', ascending=False).head(20)
    print(top[['left','right','mode','trades','total_pnl','winrate','max_dd','sharpe','tp_pct','sl_pct']].to_string(index=False))
    
    # Топ по PnL
    print("\n" + "="*90)
    print("ТОП-10 ПО PnL")
    print("="*90)
    top_pnl = results_df.sort_values('total_pnl', ascending=False).head(10)
    print(top_pnl[['left','right','mode','trades','total_pnl','winrate','max_dd','sharpe']].to_string(index=False))
    
    # Интересные комбинации
    print("\n" + "="*90)
    print("ИНТЕРЕСНЫЕ КОМБИНАЦИИ (left≠right):")
    print("="*90)
    interesting = results_df[(results_df['left'] != results_df['right']) & (results_df['sharpe'] > 8)].sort_values('sharpe', ascending=False)
    print(interesting[['left','right','mode','trades','total_pnl','winrate','max_dd','sharpe']].head(10).to_string(index=False))
