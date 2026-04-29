import pandas as pd
import numpy as np
from backtest_exits_v2 import load_data, backtest, metrics

# Прогоним Parabolic и посмотрим распределение сделок
df = load_data('/root/.openclaw/workspace/downloads/19dac7f4-0022-89d6-8000-00006ad46102_Si_260101_260331.csv')
trades = backtest(df, swing_len=8, stop_mode='atr', exit_mode='parabolic', 
                  tp_ratio=1.5, atr_mult_sl=1.0, atr_mult_tp=1.5)

print(f"Всего сделок: {len(trades)}")
print(f"Лонгов: {sum(1 for t in trades if t.direction == 'long')}")
print(f"Шортов: {sum(1 for t in trades if t.direction == 'short')}")

pnls = [t.pnl for t in trades]
wins = [p for p in pnls if p > 0]
losses = [p for p in pnls if p <= 0]

print(f"\nСредняя прибыль: {np.mean(wins):.1f} (медиана: {np.median(wins):.1f})")
print(f"Средний убыток:  {np.mean(losses):.1f} (медиана: {np.median(losses):.1f})")
print(f"Макс прибыль: {max(pnls):.1f}, Макс убыток: {min(pnls):.1f}")

# Распределение прибыли
print(f"\nПрибыльные сделки:")
print(f"  0-50:   {sum(1 for p in wins if p <= 50)}")
print(f"  50-100: {sum(1 for p in wins if 50 < p <= 100)}")
print(f"  100-200:{sum(1 for p in wins if 100 < p <= 200)}")
print(f"  200+:   {sum(1 for p in wins if p > 200)}")

print(f"\nУбыточные сделки:")
print(f"  -50-0:  {sum(1 for p in losses if p > -50)}")
print(f"  -100--50:{sum(1 for p in losses if -100 < p <= -50)}")
print(f"  <-100:  {sum(1 for p in losses if p <= -100)}")

# Проверим макс прибыль ВНУТРИ сделки vs взятая прибыль
print(f"\nCapture ratio (взятая / максимальная прибыль):")
captures = []
for t in trades:
    if t.max_profit_during > 0:
        captures.append(t.pnl / t.max_profit_during * 100)
print(f"  Средний: {np.mean(captures):.1f}%")
print(f"  Медиана: {np.median(captures):.1f}%")

# Смотрим первые 5 сделок детально
print(f"\n{'='*60}")
print("ПЕРВЫЕ 5 СДЕЛОК:")
for i, t in enumerate(trades[:5]):
    print(f"\n{i+1}. {t.direction} | Entry: {t.entry_price:.0f} @ {t.entry_time}")
    print(f"   Exit:  {t.exit_price:.0f} @ {t.exit_time} | PnL: {t.pnl:+.1f}")
    print(f"   Stop init: {t.stop_init:.0f} | Target init: {t.target_init:.0f}")
    print(f"   Max profit during: {t.max_profit_during:.1f} | Min: {t.min_profit_during:.1f}")
    print(f"   Bars held: {t.bars_held} | Reason: {t.exit_reason}")
