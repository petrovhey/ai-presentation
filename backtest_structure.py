import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import List, Optional
import warnings
warnings.filterwarnings('ignore')

# ═══════════════════════════════════════════════════════════════
#  БЭКТЕСТЕР: Structure Signal (LL+LL+HL / HH+HH+LH)
#  Данные: Si 5-мин (Финам), 01.01.26 — 31.03.26
# ═══════════════════════════════════════════════════════════════

@dataclass
class Trade:
    direction: str          # 'long' | 'short'
    entry_time: pd.Timestamp
    entry_price: float
    exit_time: pd.Timestamp
    exit_price: float
    pnl: float              # в пунктах Си
    stop_price: float
    target_price: float
    bars_held: int
    exit_reason: str        # 'tp' | 'sl' | 'end'


def load_data(path: str) -> pd.DataFrame:
    """Загрузка CSV Финам (разделитель ;)"""
    df = pd.read_csv(path, sep=';', skiprows=1,
                     names=['TICKER','PER','DATE','TIME','OPEN','HIGH','LOW','CLOSE','VOL'])
    df['datetime'] = pd.to_datetime(df['DATE'].astype(str) + df['TIME'].astype(str).str.zfill(6), format='%Y%m%d%H%M%S')
    df = df.sort_values('datetime').reset_index(drop=True)
    return df


def find_pivots(df: pd.DataFrame, length: int = 8):
    """
    ta.pivothigh(high, len, len)  и  ta.pivotlow(low, len, len)
    High >= всех в окне [bar-len .. bar+len], low <= всех.
    """
    n = len(df)
    ph = np.full(n, np.nan)
    pl = np.full(n, np.nan)
    
    high = df['HIGH'].values
    low  = df['LOW'].values
    
    for i in range(length, n - length):
        # Pivot High
        window_high = high[i - length:i + length + 1]
        if high[i] == window_high.max():
            # Проверим что это строго максимум (как в ta.pivothigh)
            # ta.pivothigh возвращает high если он >= соседей
            ph[i] = high[i]
        
        # Pivot Low
        window_low = low[i - length:i + length + 1]
        if low[i] == window_low.min():
            pl[i] = low[i]
    
    df['ph'] = ph
    df['pl'] = pl
    return df


def build_swing_history(df: pd.DataFrame, length: int = 8):
    """
    Собираем историю из последних 3 свингов (как в Pine).
    sh1/sh2/sh3 — последние 3 pivot high
    sl1/sl2/sl3 — последние 3 pivot low
    """
    n = len(df)
    
    # Индексы свингов
    sh1 = np.full(n, np.nan)
    sh2 = np.full(n, np.nan)
    sh3 = np.full(n, np.nan)
    shi1 = np.full(n, np.nan, dtype=int)
    
    sl1 = np.full(n, np.nan)
    sl2 = np.full(n, np.nan)
    sl3 = np.full(n, np.nan)
    sli1 = np.full(n, np.nan, dtype=int)
    
    ph_vals = df['ph'].values
    pl_vals = df['pl'].values
    
    # Списки свингов накопительно
    ph_list = []  # (index, value)
    pl_list = []
    
    for i in range(n):
        if not np.isnan(ph_vals[i]):
            ph_list.append((i, ph_vals[i]))
            # Оставляем только последние 3
            if len(ph_list) > 3:
                ph_list.pop(0)
        
        if not np.isnan(pl_vals[i]):
            pl_list.append((i, pl_vals[i]))
            if len(pl_list) > 3:
                pl_list.pop(0)
        
        # Заполняем
        if len(ph_list) >= 1:
            shi1[i] = ph_list[-1][0]
            sh1[i] = ph_list[-1][1]
        if len(ph_list) >= 2:
            sh2[i] = ph_list[-2][1]
        if len(ph_list) >= 3:
            sh3[i] = ph_list[-3][1]
            
        if len(pl_list) >= 1:
            sli1[i] = pl_list[-1][0]
            sl1[i] = pl_list[-1][1]
        if len(pl_list) >= 2:
            sl2[i] = pl_list[-2][1]
        if len(pl_list) >= 3:
            sl3[i] = pl_list[-3][1]
    
    df['sh1'] = sh1
    df['sh2'] = sh2
    df['sh3'] = sh3
    df['shi1'] = shi1
    df['sl1'] = sl1
    df['sl2'] = sl2
    df['sl3'] = sl3
    df['sli1'] = sli1
    
    return df


def atr(df: pd.DataFrame, period: int = 14) -> np.ndarray:
    """Average True Range"""
    high = df['HIGH'].values
    low = df['LOW'].values
    close = df['CLOSE'].values
    
    tr1 = high - low
    tr2 = np.abs(high - np.roll(close, 1))
    tr3 = np.abs(low - np.roll(close, 1))
    tr = np.maximum(np.maximum(tr1, tr2), tr3)
    tr[0] = high[0] - low[0]  # первый бар
    
    atr_vals = np.full_like(tr, np.nan)
    atr_vals[period] = tr[:period+1].mean()
    for i in range(period + 1, len(tr)):
        atr_vals[i] = (atr_vals[i-1] * (period - 1) + tr[i]) / period
    return atr_vals


def backtest(df: pd.DataFrame,
             swing_len: int = 8,
             stop_mode: str = 'swing1',   # 'swing1' | 'swing2' | 'atr'
             tp_ratio: float = 2.0,       # соотношение тейк к риску
             atr_mult_sl: float = 0.5,
             atr_mult_tp: float = 1.5,
             one_way: bool = False) -> List[Trade]:
    """
    Бэктест стратегии.
    
    stop_mode:
      'swing1' — стоп за ближайший свинг (sl1/sh1)
      'swing2' — стоп за дальний свинг (sl2/sh2)
      'atr'    — стоп = entry ± ATR * atr_mult_sl
    
    one_way: если True — после входа в лонг ждём шорт для переворота
    """
    df = find_pivots(df.copy(), swing_len)
    df = build_swing_history(df, swing_len)
    df['atr'] = atr(df, 14)
    
    n = len(df)
    high = df['HIGH'].values
    low = df['LOW'].values
    close = df['CLOSE'].values
    open_p = df['OPEN'].values
    ph = df['ph'].values
    pl = df['pl'].values
    
    atr_vals = df['atr'].values
    
    sh1 = df['sh1'].values
    sh2 = df['sh2'].values
    sh3 = df['sh3'].values
    sl1 = df['sl1'].values
    sl2 = df['sl2'].values
    sl3 = df['sl3'].values
    
    long_fired = False
    short_fired = False
    
    trades: List[Trade] = []
    active_trade: Optional[dict] = None
    
    for i in range(n - 1):  # -1 т.к. вход на следующем баре
        # Сброс флагов при новых свингах (как в Pine)
        if not np.isnan(ph[i]):
            short_fired = False
        if not np.isnan(pl[i]):
            long_fired = False
        
        # ─── СИГНАЛЫ ──────────────────────────────────────────
        long_sig = False
        short_sig = False
        
        if not np.isnan(pl[i]) and not np.isnan(sl1[i]) and not np.isnan(sl2[i]) and not np.isnan(sl3[i]) and not long_fired:
            if sl3[i] > sl2[i] and sl1[i] > sl2[i]:
                long_sig = True
                long_fired = True
        
        if not np.isnan(ph[i]) and not np.isnan(sh1[i]) and not np.isnan(sh2[i]) and not np.isnan(sh3[i]) and not short_fired:
            if sh3[i] < sh2[i] and sh1[i] < sh2[i]:
                short_sig = True
                short_fired = True
        
        # ─── УПРАВЛЕНИЕ АКТИВНОЙ ПОЗИЦИЕЙ ─────────────────────
        if active_trade is not None:
            trade = active_trade
            
            # Проверяем стоп и тейк на текущем баре (i+1 — это бар входа или последующий)
            # В реальности стоп/тейк могут сработать внутри бара — для простоты проверяем по low/high
            curr_high = high[i]
            curr_low = low[i]
            
            exited = False
            exit_price = close[i]
            exit_reason = 'end'
            
            if trade['direction'] == 'long':
                # Стоп: цена дошла до стопа
                if curr_low <= trade['stop']:
                    exited = True
                    exit_price = trade['stop']  # проскальзывание минимальное
                    exit_reason = 'sl'
                # Тейк
                elif curr_high >= trade['target']:
                    exited = True
                    exit_price = trade['target']
                    exit_reason = 'tp'
            else:  # short
                if curr_high >= trade['stop']:
                    exited = True
                    exit_price = trade['stop']
                    exit_reason = 'sl'
                elif curr_low <= trade['target']:
                    exited = True
                    exit_price = trade['target']
                    exit_reason = 'tp'
            
            if exited:
                pnl = (exit_price - trade['entry']) if trade['direction'] == 'long' else (trade['entry'] - exit_price)
                trade_obj = Trade(
                    direction=trade['direction'],
                    entry_time=trade['entry_time'],
                    entry_price=trade['entry'],
                    exit_time=df['datetime'].iloc[i],
                    exit_price=exit_price,
                    pnl=pnl,
                    stop_price=trade['stop'],
                    target_price=trade['target'],
                    bars_held=i - trade['entry_idx'],
                    exit_reason=exit_reason
                )
                trades.append(trade_obj)
                active_trade = None
                
                # Если реверсный режим — на этом же баре можно войти противоположно?
                # Для простоты — нет, ждём следующий бар
                continue
        
        # ─── НОВЫЙ ВХОД ─────────────────────────────────────
        entry_idx = i + 1
        if entry_idx >= n:
            continue
            
        entry_price = open_p[entry_idx]
        
        if long_sig and active_trade is None:
            # Стоп
            if stop_mode == 'swing1':
                stop = sl1[i] if not np.isnan(sl1[i]) else entry_price - atr_vals[i] * 0.5
            elif stop_mode == 'swing2':
                stop = sl2[i] if not np.isnan(sl2[i]) else entry_price - atr_vals[i] * 0.5
            else:  # atr
                stop = entry_price - atr_vals[i] * atr_mult_sl
            
            risk = entry_price - stop
            if risk <= 0:
                risk = atr_vals[i] * 0.5 if not np.isnan(atr_vals[i]) else 50
            
            target = entry_price + risk * tp_ratio
            
            active_trade = {
                'direction': 'long',
                'entry': entry_price,
                'entry_time': df['datetime'].iloc[entry_idx],
                'entry_idx': entry_idx,
                'stop': stop,
                'target': target,
                'risk': risk
            }
            
        elif short_sig and active_trade is None:
            if stop_mode == 'swing1':
                stop = sh1[i] if not np.isnan(sh1[i]) else entry_price + atr_vals[i] * 0.5
            elif stop_mode == 'swing2':
                stop = sh2[i] if not np.isnan(sh2[i]) else entry_price + atr_vals[i] * 0.5
            else:
                stop = entry_price + atr_vals[i] * atr_mult_sl
            
            risk = stop - entry_price
            if risk <= 0:
                risk = atr_vals[i] * 0.5 if not np.isnan(atr_vals[i]) else 50
            
            target = entry_price - risk * tp_ratio
            
            active_trade = {
                'direction': 'short',
                'entry': entry_price,
                'entry_time': df['datetime'].iloc[entry_idx],
                'entry_idx': entry_idx,
                'stop': stop,
                'target': target,
                'risk': risk
            }
    
    # Закрываем открытую позицию по последнему close
    if active_trade is not None:
        trade = active_trade
        exit_price = close[-1]
        pnl = (exit_price - trade['entry']) if trade['direction'] == 'long' else (trade['entry'] - exit_price)
        trades.append(Trade(
            direction=trade['direction'],
            entry_time=trade['entry_time'],
            entry_price=trade['entry'],
            exit_time=df['datetime'].iloc[-1],
            exit_price=exit_price,
            pnl=pnl,
            stop_price=trade['stop'],
            target_price=trade['target'],
            bars_held=len(df) - 1 - trade['entry_idx'],
            exit_reason='end'
        ))
    
    return trades


def metrics(trades: List[Trade]) -> dict:
    if not trades:
        return {}
    
    pnls = [t.pnl for t in trades]
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p <= 0]
    
    total = sum(pnls)
    winrate = len(wins) / len(pnls) * 100 if pnls else 0
    avg_win = np.mean(wins) if wins else 0
    avg_loss = np.mean(losses) if losses else 0
    
    gross_profit = sum(wins)
    gross_loss = abs(sum(losses))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
    
    # Max drawdown по equity curve
    equity = np.cumsum(pnls)
    peak = np.maximum.accumulate(equity)
    drawdown = peak - equity
    max_dd = np.max(drawdown) if len(drawdown) > 0 else 0
    
    # Sharpe (упрощённый, без безрисковой)
    returns = np.array(pnls)
    sharpe = np.mean(returns) / np.std(returns) * np.sqrt(len(returns)) if np.std(returns) > 0 else 0
    
    return {
        'trades': len(trades),
        'total_pnl': round(total, 2),
        'winrate': round(winrate, 1),
        'profit_factor': round(profit_factor, 2),
        'avg_win': round(avg_win, 2),
        'avg_loss': round(avg_loss, 2),
        'max_dd': round(max_dd, 2),
        'sharpe': round(sharpe, 2),
        'longs': len([t for t in trades if t.direction == 'long']),
        'shorts': len([t for t in trades if t.direction == 'short']),
        'tp_exits': len([t for t in trades if t.exit_reason == 'tp']),
        'sl_exits': len([t for t in trades if t.exit_reason == 'sl']),
        'end_exits': len([t for t in trades if t.exit_reason == 'end'])
    }


def run_optimization(df: pd.DataFrame):
    """Перебор параметров и вывод топ-результатов."""
    results = []
    
    configs = []
    for swing_len in [6, 8, 10, 12]:
        for stop_mode in ['swing1', 'swing2', 'atr']:
            for tp_ratio in [1.5, 2.0, 2.5, 3.0]:
                if stop_mode == 'atr':
                    for atr_sl in [0.3, 0.5, 0.8, 1.0]:
                        configs.append({
                            'swing_len': swing_len,
                            'stop_mode': stop_mode,
                            'tp_ratio': tp_ratio,
                            'atr_mult_sl': atr_sl,
                            'atr_mult_tp': atr_sl * tp_ratio
                        })
                else:
                    configs.append({
                        'swing_len': swing_len,
                        'stop_mode': stop_mode,
                        'tp_ratio': tp_ratio,
                        'atr_mult_sl': 0.5,
                        'atr_mult_tp': 1.5
                    })
    
    print(f"Тестирую {len(configs)} комбинаций...")
    
    for cfg in configs:
        try:
            trades = backtest(df, **cfg)
            m = metrics(trades)
            if m:
                results.append({**cfg, **m})
        except Exception as e:
            pass
    
    if not results:
        print("Нет результатов")
        return
    
    results_df = pd.DataFrame(results)
    
    # Сортируем по Sharpe, затем по total_pnl
    results_df = results_df.sort_values(['sharpe', 'total_pnl'], ascending=[False, False])
    
    print("\n" + "="*80)
    print("ТОП-10 ПО SHARPE:")
    print("="*80)
    print(results_df.head(10).to_string(index=False))
    
    # Топ по PnL
    top_pnl = results_df.sort_values('total_pnl', ascending=False).head(5)
    print("\n" + "="*80)
    print("ТОП-5 ПО TOTAL PnL:")
    print("="*80)
    print(top_pnl.to_string(index=False))
    
    return results_df


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════
if __name__ == '__main__':
    DATA_PATH = '/root/.openclaw/workspace/downloads/19dac7f4-0022-89d6-8000-00006ad46102_Si_260101_260331.csv'
    
    print("Загрузка данных...")
    df = load_data(DATA_PATH)
    print(f"Баров: {len(df)} | Период: {df['datetime'].iloc[0]} → {df['datetime'].iloc[-1]}")
    
    # Базовый прогон (как в индикаторе)
    print("\n" + "="*80)
    print("БАЗОВЫЙ ПРОГОН (swing_len=8, stop=swing1, TP=1:2)")
    print("="*80)
    base_trades = backtest(df, swing_len=8, stop_mode='swing1', tp_ratio=2.0)
    base_m = metrics(base_trades)
    for k, v in base_m.items():
        print(f"  {k}: {v}")
    
    # Оптимизация
    print("\n")
    results = run_optimization(df)
