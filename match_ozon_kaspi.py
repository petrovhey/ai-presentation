#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import pandas as pd
from difflib import SequenceMatcher

# ─── CONFIG ────────────────────────────────────────
OZON_FILE = '/root/.openclaw/workspace/downloads/19dd3dd7-d792-8438-8000-00002217ba35_озон_цены.xlsx'
KASPI_FILE = '/root/.openclaw/workspace/downloads/19dd3dd7-d2a2-8265-8000-0000e35ece69_kaspi_products.xls'
OUTPUT_FILE = '/root/.openclaw/workspace/kaspi_with_ozon_matches.xlsx'

# ─── LOAD ──────────────────────────────────────────
ozon = pd.read_excel(OZON_FILE, engine='openpyxl')
kaspi = pd.read_csv(KASPI_FILE, sep='\t', encoding='cp1251')

print(f"Ozon: {len(ozon)} товаров")
print(f"Kaspi: {len(kaspi)} товаров")

# ─── HELPERS ─────────────────────────────────────
def extract_qty(text):
    """Извлекает количество (число перед капсулы/таблеток/шт/порций/мл/г/упаковок)"""
    # Ищем число перед указанными единицами
    m = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:капсул|таблеток|шт|порций|мл|г|упаковок|жевательных|капс|таб)', text, re.I)
    if m:
        # Нормализуем: если после числа г/мл - это скорее дозировка, проверим
        val = float(m.group(1).replace(',', '.'))
        unit = text[m.end():m.end()+10].lower()
        # Для "г" и "мл" уточним — если число маленькое, это скорее дозировка (200 г = порошок)
        if any(x in unit for x in ['г', 'мл']):
            return val
        return val
    # Пробуем найти "X капсул" в другом формате
    m = re.search(r'(\d+)\s*капс', text, re.I)
    if m:
        return float(m.group(1))
    return None

def extract_dosage(text):
    """Извлекает дозировку активного вещества (например 250 мкг, 1000 мг, 500мг)"""
    # Ищем число + единица измерения перед названием или в начале
    m = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:мг|мкг|мл|г|ME|МЕ|мг/|IU)', text, re.I)
    if m:
        return float(m.group(1).replace(',', '.')), m.group(0)
    return None, None

def extract_active(text):
    """Извлекает "активное вещество" — ключевое имя до дозировки/количества"""
    # Убираем марку в начале
    text_clean = re.sub(r'^\s*(?:GLS Pharmaceuticals|БАД|Витамин|Витамины)\s*', '', text, flags=re.I)
    text_clean = re.sub(r'^\s*[,\s]+', '', text_clean)
    
    # Ищем дозировку — все до нее считаем активным веществом
    dosage_match = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:мг|мкг|мл|г|ME|МЕ)', text_clean, re.I)
    if dosage_match:
        active = text_clean[:dosage_match.start()].strip()
        # Очищаем хвост (запятые, предлоги)
        active = re.sub(r'[,\s]+(?:для|с|в|и|при|витамин|витамины).*$', '', active, flags=re.I)
        active = re.sub(r'[,\s]+$', '', active)
        return active.strip()
    
    # Если нет дозировки — берем первые 2-3 слова как активное вещество
    words = text_clean.split()[:4]
    active = ' '.join(words)
    # Очищаем от хвоста с запятой
    active = re.sub(r'[,\s]+(?:для|с|в|и|при).*$', '', active, flags=re.I)
    return active.strip()

def clean_for_match(text):
    """Очистка для сравнения"""
    text = text.lower()
    text = re.sub(r'gl\s*pharmaceuticals|бад|витамин|витамины|добавка|капсул|таблеток|шт|мг|мкг|мл|г|упаковок|порций|для|при|с|в|и', '', text)
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'[,\.\(\)\-]', ' ', text)
    text = ' '.join(text.split())
    return text.strip()

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

# ─── PREPARE OZON ─────────────────────────────────
ozon_records = []
for idx, row in ozon.iterrows():
    name = str(row['Название'])
    price = row['Цена (Удержание МРЦ)']
    active = extract_active(name)
    qty = extract_qty(name)
    dosage, dosage_str = extract_dosage(name)
    clean = clean_for_match(name)
    
    ozon_records.append({
        'name': name,
        'price': price,
        'active': active,
        'qty': qty,
        'dosage': dosage,
        'clean': clean,
        'idx': idx
    })

print(f"\nПример разбора Ozon:")
for r in ozon_records[:3]:
    print(f"  Актив: '{r['active']}' | Кол-во: {r['qty']} | Доза: {r['dosage']} | {r['name'][:60]}...")

# ─── MATCHING ────────────────────────────────────
matched_ozon_names = []
matched_ozon_prices = []

for k_idx, k_row in kaspi.iterrows():
    k_name = str(k_row['Название'])
    k_active = extract_active(k_name)
    k_qty = extract_qty(k_name)
    k_dosage, _ = extract_dosage(k_name)
    k_clean = clean_for_match(k_name)
    
    best_match = None
    best_score = 0
    
    for o in ozon_records:
        # 1. Сравниваем активное вещество (вес 0.5)
        active_sim = similarity(k_active.lower(), o['active'].lower()) if k_active and o['active'] else 0
        
        # 2. Сравниваем "чистое" название (вес 0.3)
        clean_sim = similarity(k_clean, o['clean']) if k_clean and o['clean'] else 0
        
        # 3. Проверяем дозировку (вес 0.15) — если есть у обоих и совпадает ≈
        dosage_sim = 0
        if k_dosage and o['dosage'] and k_dosage > 0 and o['dosage'] > 0:
            # Дозировки близки?
            ratio_d = min(k_dosage, o['dosage']) / max(k_dosage, o['dosage'])
            if ratio_d > 0.7:  # допуск 30%
                dosage_sim = ratio_d
        
        # 4. Проверяем количество капсул (вес 0.05) — если есть у обоих
        qty_sim = 0
        if k_qty and o['qty'] and k_qty > 0 and o['qty'] > 0:
            ratio_q = min(k_qty, o['qty']) / max(k_qty, o['qty'])
            if ratio_q > 0.8:  # допуск 20%
                qty_sim = ratio_q
        
        # Итоговый скор
        score = (active_sim * 0.45) + (clean_sim * 0.35) + (dosage_sim * 0.15) + (qty_sim * 0.05)
        
        if score > best_score:
            best_score = score
            best_match = o
    
    # Порог совпадения — минимум 0.25 для считания подходящим
    if best_score >= 0.25 and best_match:
        matched_ozon_names.append(best_match['name'])
        matched_ozon_prices.append(best_match['price'])
        if k_idx < 5:
            print(f"\nKASPI: {k_name[:70]}...")
            print(f"  → OZON: {best_match['name'][:70]}... | Сходство: {best_score:.2f}")
    else:
        matched_ozon_names.append(None)
        matched_ozon_prices.append(None)

# ─── SAVE RESULT ──────────────────────────────────
kaspi['Ozon_товар'] = matched_ozon_names
kaspi['Ozon_цена_руб'] = matched_ozon_prices

# Переставляем колонки: Название, Цена, В рублях, Ozon_товар, Ozon_цена_руб
cols = ['Название', 'Цена', 'В рублях', 'Ozon_товар', 'Ozon_цена_руб']
kaspi = kaspi[[c for c in cols if c in kaspi.columns]]

kaspi.to_excel(OUTPUT_FILE, index=False, engine='openpyxl')
print(f"\n✅ Результат сохранен: {OUTPUT_FILE}")
print(f"Найдено совпадений: {sum(1 for x in matched_ozon_names if x is not None)} / {len(kaspi)}")

# Покажем несколько примеров для проверки
print("\n=== Примеры совпадений ===")
count = 0
for i in range(len(kaspi)):
    if pd.notna(kaspi.loc[i, 'Ozon_товар']):
        print(f"\nKASPI:  {kaspi.loc[i, 'Название'][:70]}")
        print(f"Ozon:   {kaspi.loc[i, 'Ozon_товар'][:70]}")
        print(f"Цена Ozon: {kaspi.loc[i, 'Ozon_цена_руб']} руб | Kaspi: {kaspi.loc[i, 'В рублях']} руб")
        count += 1
        if count >= 10:
            break

print("\n=== Примеры БЕЗ совпадений ===")
count = 0
for i in range(len(kaspi)):
    if pd.isna(kaspi.loc[i, 'Ozon_товар']):
        print(f"KASPI:  {kaspi.loc[i, 'Название'][:80]}")
        count += 1
        if count >= 5:
            break
