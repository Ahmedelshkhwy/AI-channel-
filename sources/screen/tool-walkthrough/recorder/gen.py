import random
from openpyxl import Workbook
rng = random.Random(7)
items = [("Panadol Extra 24 Tab",38),("Brufen 400mg 30 Tab",41),("Cataflam 50mg 20 Tab",52),("Augmentin 1g 14 Tab",118),
("Zithromax 500mg 3 Tab",105),("Flagyl 500mg 20 Tab",24),("Ciprobay 500mg 10 Tab",76),("Concor 5mg 30 Tab",64),
("Norvasc 5mg 30 Tab",97),("Lipitor 20mg 30 Tab",185),("Crestor 10mg 28 Tab",210),("Aspocid 75mg 30 Tab",9),
("Plavix 75mg 28 Tab",245),("Glucophage 1000mg 30 Tab",46),("Amaryl 2mg 30 Tab",71),("Januvia 100mg 28 Tab",390),
("Galvus Met 50/1000",310),("Lantus SoloStar Pen",520),("Nexium 40mg 14 Tab",138),("Controloc 40mg 14 Tab",112),
("Antinal 200mg 24 Caps",31),("Motilium 10mg 30 Tab",39),("Gaviscon Liquid 200ml",72),("Claritine 10mg 10 Tab",44),
("Zyrtec 10mg 20 Tab",58),("Telfast 120mg 20 Tab",86),("Ventolin Inhaler",62),("Seretide 250 Diskus",420),
("Omega 3 Plus 30 Caps",150),("Centrum A-Z 30 Tab",230),("Vitamin C 1000 Eff",48),("Ferrograd C 30 Tab",55),
("Bepanthen Cream 30g",95),("Fucidin Cream 15g",68),("Betadine Solution 120ml",40),("Otrivin Nasal Spray",36),
("Strepsils 24 Loz",45),("Congestal 20 Tab",22),("Comtrex 20 Tab",27),("Daflon 500mg 30 Tab",175)]
branches = ["فرع المعادي","فرع مدينة نصر","فرع الشيخ زايد","فرع وسط البلد"]
days = 90
slug = dict(zip(branches, ["maadi","nasr_city","zayed","downtown"]))
data = {b: [] for b in branches}
for i,(name,cost) in enumerate(items):
    base = rng.uniform(0.15, 2.2) * (1.6 if cost < 60 else 1.0)
    pattern = i % 5
    for bi,b in enumerate(branches):
        daily = base * rng.uniform(0.6, 1.4)
        sales = max(0, round(daily * days))
        stock = round(daily * rng.uniform(20, 55))
        if pattern == 0 and bi == i % 4:          # dead here, others short
            sales, stock = rng.randint(0, 3), round(base * rng.uniform(70, 120)) + 15
        elif pattern == 0 and bi == (i + 1) % 4:  # out of stock here
            stock = 0
        elif pattern == 1 and bi == (i + 2) % 4:  # big surplus here
            stock = round(daily * rng.uniform(160, 220)) + 10
        elif pattern == 1 and bi == (i + 3) % 4:
            stock = round(daily * rng.uniform(2, 6))
        elif pattern == 3 and bi == (i + 1) % 4:
            stock = round(daily * rng.uniform(1, 4))
        data[b].append((f"10{i+1:03d}", name, stock, sales, round(sales * cost * (1.12 + (i % 7) * 0.025), 2), cost))
for b in branches:
    wb = Workbook(); ws = wb.active; ws.title = "الأصناف"; ws.sheet_view.rightToLeft = True
    ws.append(["كود الصنف","اسم الصنف","الرصيد","الكمية المباعة","قيمة المبيعات","سعر الشراء"])
    for r in data[b]: ws.append(list(r))
    ws.column_dimensions["B"].width = 28
    wb.save(f"data/{slug[b]}_items.xlsx")
print("ok")
