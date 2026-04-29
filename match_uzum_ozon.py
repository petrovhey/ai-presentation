#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import pandas as pd
from difflib import SequenceMatcher

# ─── CONFIG ────────────────────────────────────────
OZON_FILE = '/root/.openclaw/workspace/downloads/19dd3edd-e012-872f-8000-0000aa688a7b_озон_цены.xlsx'
UZUM_FILE = '/root/.openclaw/workspace/downloads/19dd3edd-de62-8263-8000-0000945416de_uzum_products_1_.xls'
OUTPUT_FILE = '/root/.openclaw/workspace/uzum_with_ozon_matches_scored.xlsx'

# ─── LOAD ──────────────────────────────────────────
ozon = pd.read_excel(OZON_FILE, engine='openpyxl')
uzum = pd.read_csv(UZUM_FILE, sep='\t', encoding='cp1251')

print(f"Ozon: {len(ozon)} товаров")
print(f"Uzum: {len(uzum)} товаров")

# ─── HELPERS ─────────────────────────────────────
def extract_qty(text):
    m = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:капсул|таблеток|шт|порций|мл|г|упаковок|жевательных|капс|таб)', text, re.I)
    if m:
        return float(m.group(1).replace(',', '.'))
    m = re.search(r'(\d+)\s*капс', text, re.I)
    if m:
        return float(m.group(1))
    return None

def extract_dosage(text):
    m = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:мг|мкг|мл|г|ME|МЕ|IU)', text, re.I)
    if m:
        return float(m.group(1).replace(',', '.')), m.group(0)
    return None, None

def extract_active(text):
    text_clean = re.sub(r'^\s*(?:GLS Pharmaceuticals|БАД|Витамин|Витамины)\s*', '', text, flags=re.I)
    text_clean = re.sub(r'^\s*[,\s]+', '', text_clean)
    dosage_match = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:мг|мкг|мл|г|ME|МЕ)', text_clean, re.I)
    if dosage_match:
        active = text_clean[:dosage_match.start()].strip()
        active = re.sub(r'[,\s]+(?:для|с|в|и|при|витамин|витамины).*$', '', active, flags=re.I)
        active = re.sub(r'[,\s]+$', '', active)
        return active.strip()
    words = text_clean.split()[:4]
    active = ' '.join(words)
    active = re.sub(r'[,\s]+(?:для|с|в|и|при).*$', '', active, flags=re.I)
    return active.strip()

def clean_for_match(text):
    text = text.lower()
    text = re.sub(r'gl\s*pharmaceuticals|бад|витамин|витамины|добавка|капсул|таблеток|шт|мг|мкг|мл|г|упаковок|порций|для|при|с|в|и', '', text)
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'[,\.\(\)\-]', ' ', text)
    text = ' '.join(text.split())
    return text.strip()

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def score_to_10(score):
    if score < 0.20: return 1
    elif score < 0.30: return 2
    elif score < 0.40: return 3
    elif score < 0.50: return 4
    elif score < 0.60: return 5
    elif score < 0.70: return 6
    elif score < 0.75: return 7
    elif score < 0.80: return 8
    elif score < 0.90: return 9
    else: return 10

# ─── PREPARE OZON ─────────────────────────────────
ozon_records = []
for idx, row in ozon.iterrows():
    name = str(row['Название'])
    price = row['Цена (Удержание МРЦ)']
    active = extract_active(name)
    qty = extract_qty(name)
    dosage, _ = extract_dosage(name)
    clean = clean_for_match(name)
    ozon_records.append({'name': name, 'price': price, 'active': active, 'qty': qty, 'dosage': dosage, 'clean': clean, 'idx': idx})

# ─── MATCHING ────────────────────────────────────
matched_ozon_names = []
matched_ozon_prices = []
matched_scores = []
matched_scores_10 = []

for k_idx, k_row in uzum.iterrows():
    k_name = str(k_row['Название'])
    k_active = extract_active(k_name)
    k_qty = extract_qty(k_name)
    k_dosage, _ = extract_dosage(k_name)
    k_clean = clean_for_match(k_name)
    
    best_match = None
    best_score = 0
    
    for o in ozon_records:
        active_sim = similarity(k_active.lower(), o['active'].lower()) if k_active and o['active'] else 0
        clean_sim = similarity(k_clean, o['clean']) if k_clean and o['clean'] else 0
        
        dosage_sim = 0
        if k_dosage and o['dosage'] and k_dosage > 0 and o['dosage'] > 0:
            ratio_d = min(k_dosage, o['dosage']) / max(k_dosage, o['dosage'])
            if ratio_d > 0.7:
                dosage_sim = ratio_d
        
        qty_sim = 0
        if k_qty and o['qty'] and k_qty > 0 and o['qty'] > 0:
            ratio_q = min(k_qty, o['qty']) / max(k_qty, o['qty'])
            if ratio_q > 0.8:
                qty_sim = ratio_q
        
        score = (active_sim * 0.45) + (clean_sim * 0.35) + (dosage_sim * 0.15) + (qty_sim * 0.05)
        
        if score > best_score:
            best_score = score
            best_match = o
    
    if best_score >= 0.20 and best_match:
        matched_ozon_names.append(best_match['name'])
        matched_ozon_prices.append(best_match['price'])
        matched_scores.append(round(best_score, 3))
        matched_scores_10.append(score_to_10(best_score))
    else:
        matched_ozon_names.append(None)
        matched_ozon_prices.append(None)
        matched_scores.append(None)
        matched_scores_10.append(1)

# ─── SAVE RESULT ──────────────────────────────────
uzum['Ozon_товар'] = matched_ozon_names
uzum['Ozon_цена_руб'] = matched_ozon_prices
uzum['Сходство_raw'] = matched_scores
uzum['Уверенность_1_10'] = matched_scores_10

cols = ['Название', 'Цена (сум)', 'В рублях', 'Ссылка', 'Ozon_товар', 'Ozon_цена_руб', 'Сходство_raw', 'Уверенность_1_10']
uzum = uzum[[c for c in cols if c in uzum.columns]]

uzum.to_excel(OUTPUT_FILE, index=False, engine='openpyxl')
print(f"\n✅ Результат сохранен: {OUTPUT_FILE}")

print(f"\n=== Статистика уверенности ===")
for s in range(1, 11):
    count = sum(1 for x in matched_scores_10 if x == s)
    pct = count / len(matched_scores_10) * 100
    bar = '█' * int(pct / 2)
    print(f"  {s:2d}/10: {count:2d} товаров ({pct:5.1f}%) {bar}")

print(f"\n=== Все товары ===")
for i in range(len(uzum)):
    score = uzum.loc[i, 'Уверенность_1_10']
    oz_name = uzum.loc[i, 'Ozon_товар']
    print(f"\n[{score}/10] UZUM: {uzum.loc[i, 'Название'][:70]}")
    if pd.notna(oz_name):
        print(f"       OZON: {oz_name[:70]}")
        print(f"       raw={uzum.loc[i, 'Сходство_raw']} | Uzum={uzum.loc[i, 'В рублях']}₽ | Ozon={uzum.loc[i, 'Ozon_цена_руб']}₽")
    else:
        print(f"       OZON: нет совпадения")
