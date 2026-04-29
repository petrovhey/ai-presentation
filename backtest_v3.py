import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import List, Optional
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
    stop_init: float
    target_init: float
    bars_held: int
    exit_reason: str
    max_profit_during: float
    min_profit_during: float

def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, sep=';', skiprows=1,
                     names=['TICKER','PER','DATE','TIME','OPEN','HIGH','LOW','CLOSE','VOL'])
    df['datetime'] = pd.to_datetime(df['DATE'].astype(str) + df['TIME'].astype(str).str.zfill(6), format='%Y%m%d%H%M%S')
    df = df.sort_values('datetime').reset_index(drop=True)
    return df

def find_pivots(df: pd.DataFrame, length: int = 8):
    n = len(df)
    ph = np.full(n, np.nan); pl = np.full(n, np.nan)
    high = df['HIGH'].values; low = df['LOW'].values
    for i in range(length, n - length):
        if high[i] == high[i - length:i + length + 1].max(): ph[i] = high[i]
        if low[i] == low[i - length:i + length + 1].min(): pl[i] = low[i]
    df['ph'] = ph; df['pl'] = pl
    return df

def build_swing_history(df: pd.DataFrame, length: int = 8):
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

def parabolic_sar(high, low, close, af_start=0.02, af_inc=0.02, af_max=0.2):
    n = len(high)
    sar = np.full(n, np.nan)
    trend = 1 if close[1] > close[0] else -1
    ep = high[1] if trend == 1 else low[1]
    sar[1] = low[0] if trend == 1 else high[0]
    af = af_start
    for i in range(2, n):
        sar[i] = sar[i-1] + af * (ep - sar[i-1])
        if trend == 1:
            sar[i] = min(sar[i], low[i-1], low[i-2] if i >= 2 else low[i-1])
            if low[i] < sar[i]:
                trend = -1; sar[i] = ep; ep = low[i]; af = af_start
            else:
                if high[i] > ep: ep = high[i]; af = min(af + af_inc, af_max)
        else:
            sar[i] = max(sar[i], high[i-1], high[i-2] if i >= 2 else high[i-1])
            if high[i] > sar[i]:
                trend = 1; sar[i] = ep; ep = high[i]; af = af_start
            else:
                if low[i] < ep: ep = low[i]; af = min(af + af_inc, af_max)
    return sar

def backtest(df: pd.DataFrame,
             swing_len=8, stop_mode='atr', exit_mode='fixed_tp',
             tp_ratio=2.0, atr_mult_sl=1.0, atr_mult_tp=1.5,
             trail_atr_mult=1.5, chandelier_period=22, chandelier_mult=3.0,
             time_exit_bars=48, combo_tp_ratio=2.0, combo_trail_mult=1.5):
    df = find_pivots(df.copy(), swing_len)
    df = build_swing_history(df, swing_len)
    df['atr'] = atr(df, 14)
    n = len(df)
    high = df['HIGH'].values; low = df['LOW'].values; close = df['CLOSE'].values; open_p = df['OPEN'].values
    ph = df['ph'].values; pl = df['pl'].values; atr_vals = df['atr'].values
    sh1 = df['sh1'].values; sh2 = df['sh2'].values; sh3 = df['sh3'].values
    sl1 = df['sl1'].values; sl2 = df['sl2'].values; sl3 = df['sl3'].values
    
    psar_vals = parabolic_sar(high, low, close, 0.02, 0.02, 0.2) if exit_mode in ('parabolic','combo') else None
    
    long_fired = False; short_fired = False
    trades = []
    active_trade = None
    
    for i in range(n - 1):
        if not np.isnan(ph[i]): short_fired = False
        if not np.isnan(pl[i]): long_fired = False
        
        long_sig = False; short_sig = False
        if not np.isnan(pl[i]) and not np.isnan(sl1[i]) and not np.isnan(sl2[i]) and not np.isnan(sl3[i]) and not long_fired:
            if sl3[i] > sl2[i] and sl1[i] > sl2[i]: long_sig = True; long_fired = True
        if not np.isnan(ph[i]) and not np.isnan(sh1[i]) and not np.isnan(sh2[i]) and not np.isnan(sh3[i]) and not short_fired:
            if sh3[i] < sh2[i] and sh1[i] < sh2[i]: short_sig = True; short_fired = True
        
        if active_trade is not None:
            trade = active_trade
            curr_high = high[i]; curr_low = low[i]
            if trade['direction'] == 'long': unreal = curr_high - trade['entry']
            else: unreal = trade['entry'] - curr_low
            trade['max_profit'] = max(trade['max_profit'], unreal)
            trade['min_profit'] = min(trade['min_profit'], unreal)
            
            exited = False; exit_price = close[i]; exit_reason = 'end'
            
            # ЧЕСТНЫЕ ВЫХОДЫ: проверяем open для гэпов
            def exit_long_by_stop(stop_price):
                if curr_low <= stop_price:
                    if open_p[i] < stop_price: return True, open_p[i], 'sl_gap'
                    else: return True, stop_price, 'sl'
                return False, close[i], 'end'
            
            def exit_short_by_stop(stop_price):
                if curr_high >= stop_price:
                    if open_p[i] > stop_price: return True, open_p[i], 'sl_gap'
                    else: return True, stop_price, 'sl'
                return False, close[i], 'end'
            
            if exit_mode == 'fixed_tp':
                if trade['direction'] == 'long':
                    exited, exit_price, exit_reason = exit_long_by_stop(trade['stop'])
                    if not exited and curr_high >= trade['target']:
                        exited, exit_price, exit_reason = True, trade['target'], 'tp'
                else:
                    exited, exit_price, exit_reason = exit_short_by_stop(trade['stop'])
                    if not exited and curr_low <= trade['target']:
                        exited, exit_price, exit_reason = True, trade['target'], 'tp'
            
            elif exit_mode == 'trailing_atr':
                if trade['direction'] == 'long':
                    new_stop = curr_high - atr_vals[i] * trail_atr_mult if not np.isnan(atr_vals[i]) else trade['stop']
                    trade['stop'] = max(trade['stop'], new_stop)
                    exited, exit_price, exit_reason = exit_long_by_stop(trade['stop'])
                else:
                    new_stop = curr_low + atr_vals[i] * trail_atr_mult if not np.isnan(atr_vals[i]) else trade['stop']
                    trade['stop'] = min(trade['stop'], new_stop)
                    exited, exit_price, exit_reason = exit_short_by_stop(trade['stop'])
            
            elif exit_mode == 'parabolic':
                if trade['direction'] == 'long':
                    ps = psar_vals[i-1] if i > 0 and not np.isnan(psar_vals[i-1]) else trade['stop']
                    trade['stop'] = max(trade['stop'], ps)
                    exited, exit_price, exit_reason = exit_long_by_stop(trade['stop'])
                else:
                    ps = psar_vals[i-1] if i > 0 and not np.isnan(psar_vals[i-1]) else trade['stop']
                    trade['stop'] = min(trade['stop'], ps)
                    exited, exit_price, exit_reason = exit_short_by_stop(trade['stop'])
            
            elif exit_mode == 'chandelier':
                if trade['direction'] == 'long':
                    if i >= chandelier_period:
                        hh = np.max(high[i-chandelier_period:i])
                        atr_prev = atr_vals[i-1] if i > 0 else np.nan
                        ch = hh - atr_prev * chandelier_mult if not np.isnan(atr_prev) else trade['stop']
                        trade['stop'] = max(trade['stop'], ch)
                    exited, exit_price, exit_reason = exit_long_by_stop(trade['stop'])
                else:
                    if i >= chandelier_period:
                        ll = np.min(low[i-chandelier_period:i])
                        atr_prev = atr_vals[i-1] if i > 0 else np.nan
                        ch = ll + atr_prev * chandelier_mult if not np.isnan(atr_prev) else trade['stop']
                        trade['stop'] = min(trade['stop'], ch)
                    exited, exit_price, exit_reason = exit_short_by_stop(trade['stop'])
            
            elif exit_mode == 'swing_trail':
                if trade['direction'] == 'long':
                    if not np.isnan(sl1[i]): trade['stop'] = max(trade['stop'], sl1[i])
                    exited, exit_price, exit_reason = exit_long_by_stop(trade['stop'])
                else:
                    if not np.isnan(sh1[i]): trade['stop'] = min(trade['stop'], sh1[i])
                    exited, exit_price, exit_reason = exit_short_by_stop(trade['stop'])
            
            elif exit_mode == 'time_exit':
                if trade['direction'] == 'long':
                    exited, exit_price, exit_reason = exit_long_by_stop(trade['stop'])
                    if not exited and curr_high >= trade['target']:
                        exited, exit_price, exit_reason = True, trade['target'], 'tp'
                    if not exited and i - trade['entry_idx'] >= time_exit_bars:
                        exited, exit_price, exit_reason = True, close[i], 'time'
                else:
                    exited, exit_price, exit_reason = exit_short_by_stop(trade['stop'])
                    if not exited and curr_low <= trade['target']:
                        exited, exit_price, exit_reason = True, trade['target'], 'tp'
                    if not exited and i - trade['entry_idx'] >= time_exit_bars:
                        exited, exit_price, exit_reason = True, close[i], 'time'
            
            elif exit_mode == 'combo':
                if not trade.get('trailing_active', False):
                    if trade['direction'] == 'long':
                        exited, exit_price, exit_reason = exit_long_by_stop(trade['stop'])
                        if not exited and curr_high >= trade['target']:
                            trade['trailing_active'] = True
                    else:
                        exited, exit_price, exit_reason = exit_short_by_stop(trade['stop'])
                        if not exited and curr_low <= trade['target']:
                            trade['trailing_active'] = True
                if trade.get('trailing_active', False) and not exited:
                    if trade['direction'] == 'long':
                        new_stop = curr_high - atr_vals[i] * combo_trail_mult if not np.isnan(atr_vals[i]) else trade['stop']
                        trade['stop'] = max(trade['stop'], new_stop)
                        exited, exit_price, exit_reason = exit_long_by_stop(trade['stop'])
                        if exited: exit_reason = 'trail_sl'
                    else:
                        new_stop = curr_low + atr_vals[i] * combo_trail_mult if not np.isnan(atr_vals[i]) else trade['stop']
                        trade['stop'] = min(trade['stop'], new_stop)
                        exited, exit_price, exit_reason = exit_short_by_stop(trade['stop'])
                        if exited: exit_reason = 'trail_sl'
            
            if exited:
                pnl = (exit_price - trade['entry']) if trade['direction'] == 'long' else (trade['entry'] - exit_price)
                trades.append(Trade(
                    direction=trade['direction'], entry_time=trade['entry_time'], entry_price=trade['entry'],
                    exit_time=df['datetime'].iloc[i], exit_price=exit_price, pnl=pnl,
                    stop_init=trade['stop_init'], target_init=trade['target_init'],
                    bars_held=i - trade['entry_idx'], exit_reason=exit_reason,
                    max_profit_during=trade['max_profit'], min_profit_during=trade['min_profit']
                ))
                active_trade = None
                continue
        
        entry_idx = i + 1
        if entry_idx >= n: continue
        entry_price = open_p[entry_idx]
        
        if long_sig and active_trade is None:
            if stop_mode == 'swing1': stop = sl1[i] if not np.isnan(sl1[i]) else entry_price - atr_vals[i] * 0.5
            elif stop_mode == 'swing2': stop = sl2[i] if not np.isnan(sl2[i]) else entry_price - atr_vals[i] * 0.5
            else: stop = entry_price - atr_vals[i] * atr_mult_sl if not np.isnan(atr_vals[i]) else entry_price - 50
            risk = entry_price - stop
            if risk <= 0: risk = atr_vals[i] * 0.5 if not np.isnan(atr_vals[i]) else 50
            target = entry_price + risk * tp_ratio
            active_trade = {'direction': 'long', 'entry': entry_price, 'entry_time': df['datetime'].iloc[entry_idx],
                            'entry_idx': entry_idx, 'stop': stop, 'stop_init': stop, 'target': target, 'target_init': target,
                            'risk': risk, 'max_profit': 0, 'min_profit': 0}
        elif short_sig and active_trade is None:
            if stop_mode == 'swing1': stop = sh1[i] if not np.isnan(sh1[i]) else entry_price + atr_vals[i] * 0.5
            elif stop_mode == 'swing2': stop = sh2[i] if not np.isnan(sh2[i]) else entry_price + atr_vals[i] * 0.5
            else: stop = entry_price + atr_vals[i] * atr_mult_sl if not np.isnan(atr_vals[i]) else entry_price + 50
            risk = stop - entry_price
            if risk <= 0: risk = atr_vals[i] * 0.5 if not np.isnan(atr_vals[i]) else 50
            target = entry_price - risk * tp_ratio
            active_trade = {'direction': 'short', 'entry': entry_price, 'entry_time': df['datetime'].iloc[entry_idx],
                            'entry_idx': entry_idx, 'stop': stop, 'stop_init': stop, 'target': target, 'target_init': target,
                            'risk': risk, 'max_profit': 0, 'min_profit': 0}
    
    if active_trade is not None:
        trade = active_trade; exit_price = close[-1]
        pnl = (exit_price - trade['entry']) if trade['direction'] == 'long' else (trade['entry'] - exit_price)
        trades.append(Trade(direction=trade['direction'], entry_time=trade['entry_time'], entry_price=trade['entry'],
                            exit_time=df['datetime'].iloc[-1], exit_price=exit_price, pnl=pnl,
                            stop_init=trade['stop_init'], target_init=trade['target_init'],
                            bars_held=len(df)-1-trade['entry_idx'], exit_reason='end',
                            max_profit_during=trade['max_profit'], min_profit_during=trade['min_profit']))
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
    capture = [t.pnl / t.max_profit_during * 100 for t in trades if t.max_profit_during > 0 and t.pnl > 0]
    return {
        'trades': len(trades), 'total_pnl': round(total, 2), 'winrate': round(winrate, 1),
        'profit_factor': round(profit_factor, 2), 'avg_win': round(avg_win, 2), 'avg_loss': round(avg_loss, 2),
        'max_dd': round(max_dd, 2), 'sharpe': round(sharpe, 2),
        'capture_pct': round(np.mean(capture), 1) if capture else 0,
        'tp_exits': len([t for t in trades if t.exit_reason == 'tp']),
        'sl_exits': len([t for t in trades if 'sl' in t.exit_reason]),
        'time_exits': len([t for t in trades if t.exit_reason == 'time']),
        'trail_exits': len([t for t in trades if 'trail' in t.exit_reason]),
        'end_exits': len([t for t in trades if t.exit_reason == 'end'])
    }

if __name__ == '__main__':
    DATA_PATH = '/root/.openclaw/workspace/downloads/19dac7f4-0022-89d6-8000-00006ad46102_Si_260101_260331.csv'
    print("Загрузка...")
    df = load_data(DATA_PATH)
    print(f"Баров: {len(df)} | {df['datetime'].iloc[0]} → {df['datetime'].iloc[-1]}\n")
    
    BASE = {'swing_len': 8, 'stop_mode': 'atr', 'atr_mult_sl': 1.0, 'tp_ratio': 1.5}
    modes = [
        ('fixed_tp', BASE.copy()),
        ('trailing_atr', {**BASE, 'trail_atr_mult': 1.5}),
        ('trailing_atr', {**BASE, 'trail_atr_mult': 2.0}),
        ('parabolic', BASE.copy()),
        ('chandelier', {**BASE, 'chandelier_period': 22, 'chandelier_mult': 3.0}),
        ('swing_trail', BASE.copy()),
        ('time_exit', {**BASE, 'time_exit_bars': 48}),
        ('combo', {**BASE, 'combo_tp_ratio': 2.0, 'combo_trail_mult': 1.5}),
    ]
    
    results = []
    for mode, cfg in modes:
        try:
            trades = backtest(df, exit_mode=mode, **cfg)
            m = metrics(trades)
            if m: results.append({'exit_mode': mode, **cfg, **m})
        except Exception as e:
            print(f"Ошибка {mode}: {e}")
    
    results_df = pd.DataFrame(results).sort_values('sharpe', ascending=False)
    print("="*85)
    print("СРАВНЕНИЕ ВЫХОДОВ (честные стопы, без lookahead)")
    print("="*85)
    print(results_df[['exit_mode','trades','total_pnl','winrate','profit_factor','max_dd','sharpe','capture_pct','sl_exits','tp_exits']].to_string(index=False))
