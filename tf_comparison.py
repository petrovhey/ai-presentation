import pandas as pd
import numpy as np
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

def load_data(path):
    df = pd.read_csv(path, sep=';', skiprows=1,
                     names=['TICKER','PER','DATE','TIME','OPEN','HIGH','LOW','CLOSE','VOL'])
    df['datetime'] = pd.to_datetime(df['DATE'].astype(str) + df['TIME'].astype(str).str.zfill(6), format='%Y%m%d%H%M%S')
    return df.sort_values('datetime').reset_index(drop=True)

def resample_to_tf(df, minutes):
    """Resample 5-min data to higher timeframe"""
    if minutes == 5:
        return df.copy()
    df = df.set_index('datetime')
    ohlc = df.resample(f'{minutes}min').agg({
        'OPEN': 'first',
        'HIGH': 'max',
        'LOW': 'min',
        'CLOSE': 'last',
        'VOL': 'sum'
    }).dropna().reset_index()
    return ohlc

def find_pivots_lr(df, left, right):
    n = len(df)
    ph = np.full(n, np.nan); pl = np.full(n, np.nan)
    h = df['HIGH'].values; l = df['LOW'].values
    for i in range(left, n - right):
        if h[i] == h[i-left:i+right+1].max(): ph[i] = h[i]
        if l[i] == l[i-left:i+right+1].min(): pl[i] = l[i]
    df['ph'] = ph; df['pl'] = pl
    return df

def build_swings(df):
    n = len(df)
    sh1=np.full(n,np.nan); sh2=np.full(n,np.nan); sh3=np.full(n,np.nan)
    sl1=np.full(n,np.nan); sl2=np.full(n,np.nan); sl3=np.full(n,np.nan)
    ph_list=[]; pl_list=[]
    for i in range(n):
        if not np.isnan(df['ph'].iloc[i]):
            ph_list.append((i,df['ph'].iloc[i]))
            if len(ph_list)>3: ph_list.pop(0)
        if not np.isnan(df['pl'].iloc[i]):
            pl_list.append((i,df['pl'].iloc[i]))
            if len(pl_list)>3: pl_list.pop(0)
        if len(ph_list)>=1: sh1[i]=ph_list[-1][1]
        if len(ph_list)>=2: sh2[i]=ph_list[-2][1]
        if len(ph_list)>=3: sh3[i]=ph_list[-3][1]
        if len(pl_list)>=1: sl1[i]=pl_list[-1][1]
        if len(pl_list)>=2: sl2[i]=pl_list[-2][1]
        if len(pl_list)>=3: sl3[i]=pl_list[-3][1]
    df['sh1']=sh1;df['sh2']=sh2;df['sh3']=sh3;df['sl1']=sl1;df['sl2']=sl2;df['sl3']=sl3
    return df

def atr(df, p=14):
    h=df['HIGH'].values; l=df['LOW'].values; c=df['CLOSE'].values
    tr=np.maximum(np.maximum(h-l, np.abs(h-np.roll(c,1))), np.abs(l-np.roll(c,1)))
    tr[0]=h[0]-l[0]; a=np.full_like(tr,np.nan); a[p]=tr[:p+1].mean()
    for i in range(p+1,len(tr)): a[i]=(a[i-1]*(p-1)+tr[i])/p
    return a

def backtest(df, left=5, right=10, tp_ratio=1.5, atr_mult=1.0):
    df = find_pivots_lr(df.copy(), left, right)
    df = build_swings(df)
    df['atr'] = atr(df, 14)
    n=len(df); h=df['HIGH'].values; l=df['LOW'].values; c=df['CLOSE'].values; o=df['OPEN'].values
    ph=df['ph'].values; pl=df['pl'].values; a=df['atr'].values
    sh1=df['sh1'].values; sh2=df['sh2'].values; sh3=df['sh3'].values
    sl1=df['sl1'].values; sl2=df['sl2'].values; sl3=df['sl3'].values
    
    long_fired=False; short_fired=False; trades=[]; active=None
    
    for i in range(n-1):
        ph_av = ph[i-right] if i>=right else np.nan
        pl_av = pl[i-right] if i>=right else np.nan
        if not np.isnan(ph_av): short_fired=False
        if not np.isnan(pl_av): long_fired=False
        
        long_sig = not np.isnan(pl_av) and not np.isnan(sl1[i]) and not np.isnan(sl2[i]) and not np.isnan(sl3[i]) and not long_fired and sl3[i]>sl2[i] and sl1[i]>sl2[i]
        short_sig = not np.isnan(ph_av) and not np.isnan(sh1[i]) and not np.isnan(sh2[i]) and not np.isnan(sh3[i]) and not short_fired and sh3[i]<sh2[i] and sh1[i]<sh2[i]
        if long_sig: long_fired=True
        if short_sig: short_fired=True
        
        j=i+1
        if active is not None:
            trade=active; exited=False; ep=c[j]; reason='end'
            if trade['dir']=='long':
                if l[j]<=trade['stop']:
                    exited=True; ep=o[j] if o[j]<trade['stop'] else trade['stop']; reason='sl'
                elif h[j]>=trade['target']:
                    exited=True; ep=trade['target']; reason='tp'
            else:
                if h[j]>=trade['stop']:
                    exited=True; ep=o[j] if o[j]>trade['stop'] else trade['stop']; reason='sl'
                elif l[j]<=trade['target']:
                    exited=True; ep=trade['target']; reason='tp'
            if exited:
                pnl=(ep-trade['entry']) if trade['dir']=='long' else (trade['entry']-ep)
                trades.append({'pnl':pnl, 'reason':reason, 'entry':trade['entry'], 'exit':ep})
                active=None
        
        if long_sig and active is None:
            entry=o[j]
            risk=a[i]*atr_mult if not np.isnan(a[i]) else 50
            if risk<=0: risk=50
            active={'dir':'long','entry':entry,'stop':entry-risk,'target':entry+risk*tp_ratio}
        elif short_sig and active is None:
            entry=o[j]
            risk=a[i]*atr_mult if not np.isnan(a[i]) else 50
            if risk<=0: risk=50
            active={'dir':'short','entry':entry,'stop':entry+risk,'target':entry-risk*tp_ratio}
    
    if active is not None:
        pnl=(c[-1]-active['entry']) if active['dir']=='long' else (active['entry']-c[-1])
        trades.append({'pnl':pnl, 'reason':'end', 'entry':active['entry'], 'exit':c[-1]})
    
    pnls=[t['pnl'] for t in trades]
    total=sum(pnls); wins=[p for p in pnls if p>0]; losses=[p for p in pnls if p<=0]
    wr=len(wins)/len(pnls)*100 if pnls else 0
    dd=np.max(np.maximum.accumulate(np.cumsum(pnls))-np.cumsum(pnls)) if pnls else 0
    sharpe=np.mean(pnls)/np.std(pnls)*np.sqrt(len(pnls)) if np.std(pnls)>0 else 0
    avg_trade=total/len(trades) if trades else 0
    
    return {
        'trades': len(trades), 'pnl': total, 'winrate': wr, 'max_dd': dd,
        'sharpe': sharpe, 'avg_trade': avg_trade,
        'tp_exits': len([t for t in trades if t['reason']=='tp']),
        'sl_exits': len([t for t in trades if t['reason']=='sl'])
    }

def optimize_params(df, tf_name):
    """Подбор left/right под ТФ"""
    best_sharpe = -999; best = None
    for left in [3,5,8,10]:
        for right in [3,5,8,10,15]:
            if left + right > len(df) * 0.1: continue
            try:
                m = backtest(df, left=left, right=right)
                if m['sharpe'] > best_sharpe and m['trades'] >= 10:
                    best_sharpe = m['sharpe']
                    best = {**m, 'left': left, 'right': right, 'tf': tf_name}
            except: pass
    return best

if __name__ == '__main__':
    DATA_PATH = '/root/.openclaw/workspace/downloads/19dac7f4-0022-89d6-8000-00006ad46102_Si_260101_260331.csv'
    df_5min = load_data(DATA_PATH)
    
    results = []
    
    for tf_min in [5, 15, 30, 60]:
        df_tf = resample_to_tf(df_5min, tf_min)
        print(f"\n{'='*60}")
        print(f"ТАЙМФРЕЙМ: {tf_min} мин | Баров: {len(df_tf)}")
        print(f"{'='*60}")
        
        best = optimize_params(df_tf, f"{tf_min}min")
        if best:
            results.append(best)
            print(f"Лучшие: left={best['left']}, right={best['right']}")
            print(f"  Сделок: {best['trades']} | PnL: {best['pnl']:.1f} п | Winrate: {best['winrate']:.1f}%")
            print(f"  Max DD: {best['max_dd']:.1f} | Sharpe: {best['sharpe']:.2f} | Средняя сделка: {best['avg_trade']:.1f} п")
            print(f"  TP exits: {best['tp_exits']} | SL exits: {best['sl_exits']}")
    
    print(f"\n{'='*60}")
    print("СРАВНЕНИЕ ТФ (лучшие из каждого)")
    print(f"{'='*60}")
    print(f"{'ТФ':<8} {'L/R':<8} {'Сделок':<8} {'PnL':<10} {'Winrate':<10} {'Max DD':<10} {'Sharpe':<8}")
    print("-" * 70)
    for r in results:
        print(f"{r['tf']:<8} {r['left']}/{r['right']:<6} {r['trades']:<8} {r['pnl']:<10.1f} {r['winrate']:<10.1f} {r['max_dd']:<10.1f} {r['sharpe']:<8.2f}")
    
    # Топ по Sharpe
    print(f"\n{'='*60}")
    print("🏆 ЛУЧШИЙ ПО SHARPE:")
    best_overall = max(results, key=lambda x: x['sharpe'])
    print(f"  {best_overall['tf']}: left={best_overall['left']}, right={best_overall['right']}")
    print(f"  Sharpe: {best_overall['sharpe']:.2f} | PnL: {best_overall['pnl']:.1f} п | Winrate: {best_overall['winrate']:.1f}%")
    
    # Топ по PnL
    print(f"\n💰 ЛУЧШИЙ ПО PnL:")
    best_pnl = max(results, key=lambda x: x['pnl'])
    print(f"  {best_pnl['tf']}: left={best_pnl['left']}, right={best_pnl['right']}")
    print(f"  PnL: {best_pnl['pnl']:.1f} п | Sharpe: {best_pnl['sharpe']:.2f} | Сделок: {best_pnl['trades']}")
