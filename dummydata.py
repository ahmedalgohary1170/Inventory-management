import random
import sqlite3
from datetime import datetime, timedelta
from database import Database
import os

def create_dummy_data():
    """إنشاء بيانات تجريبية للعملاء والمنتجات والفواتير"""
    db = Database()
    
    # حذف البيانات الحالية

    # إناء قوائم الأسماء والعناوين والمنتجات
    first_names = ["أحمد", "محمد", "علي", "محمود", "خالد", "عمر", "يوسف", "إبراهيم", "مصطفى", "عبدالله"]
    last_names = ["علي", "حسن", "محمود", "عبدالرحمن", "سليمان", "ناصر", "فارس", "وسيم", "بدر", "رامي"]
    cities = ["الرياض", "جدة", "الدمام", "المدينة المنورة", "مكة المكرمة", "الطائف", "تبوك", "الأحساء", "جازان", "نجران"]
    streets = ["العليا", "التحلية", "الجامعة", "الملك فهد", "الملك عبدالله", "السلام", "النهضة", "الخليج", "الرياض", "الملك سلمان"]
    
    product_names = [
        "جوال سامسونج", "آيفون", "لابتوب ديل", "تابلت هواوي", "سماعة لاسلكية",
        "ساعة ذكية", "كاميرا كانون", "شاحن سريع", "حقيبة لابتوب", "ماوس لاسلكي"
    ]
    
    # إضافة عملاء عشوائيين
    customers = []
    for i in range(20):
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        phone = f"05{random.randint(10000000, 99999999)}"
        note = "" if random.random() > 0.3 else random.choice(["عميل ممتاز", "يتأخر في السداد", "يطلب خصم", "جديد"])
        cursor = db.conn.cursor()
        cursor.execute(
            "INSERT INTO customers (name, phone, note) VALUES (?, ?, ?)",
            (name, phone, note)
        )
        customers.append(cursor.lastrowid)
        db.conn.commit()
    
    # إضافة منتجات عشوائية
    products = []
    for i in range(10):
        name = f"{product_names[i]} {random.choice(['برو', 'ماكس', 'لايت', 'بلس', ''])}".strip()
        price = random.randint(100, 5000)
        stock = random.randint(1, 100)
        cursor = db.conn.cursor()
        cursor.execute(
            "INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
            (name, price, stock)
        )
        products.append({"id": cursor.lastrowid, "price": price})
        db.conn.commit()
    
    # إضافة فواتير عشوائية
    statuses = ["جارية", "متأخرة", "منتهية"]
    
    # إنشاء فواتير قديمة (متأخرة)
    for _ in range(15):  # 15 فاتورة قديمة
        customer_id = random.choice(customers)
        product = random.choice(products)
        quantity = random.randint(1, 5)
        total_amount = product["price"] * quantity
        upfront_paid = random.randint(0, int(total_amount * 0.3))  # دفعة أولى قليلة
        months = random.choice([3, 6, 12])
        created_at = (datetime.now() - timedelta(days=random.randint(180, 365))).strftime("%Y-%m-%d %H:%M:%S")
        
        cursor = db.conn.cursor()
        cursor.execute(
            """INSERT INTO invoices 
               (customer_id, product_id, quantity, total_amount, upfront_paid, installment_count, installment_amount, start_date, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (customer_id, product["id"], quantity, total_amount, upfront_paid, 
             months, (total_amount - upfront_paid) / months, created_at, created_at)
        )
        invoice_id = cursor.lastrowid
        db.conn.commit()
        
        # إضافة أقساط قديمة (متأخرة)
        monthly_payment = (total_amount - upfront_paid) / months
        for i in range(months):
            due_date = (datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S") + timedelta(days=30*i)).strftime("%Y-%m-%d")
            paid = monthly_payment if random.random() > 0.7 else 0  # 30% مدفوعة
            
            cursor = db.conn.cursor()
            cursor.execute(
                """INSERT INTO installments 
                   (invoice_id, amount, due_date, paid, customer_id, product_id)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (invoice_id, monthly_payment, due_date, paid, customer_id, product["id"])
            )
            db.conn.commit()
    
    # إنشاء فواتير حديثة (جارية)
    for _ in range(15):  # 15 فاتورة حديثة
        customer_id = random.choice(customers)
        product = random.choice(products)
        quantity = random.randint(1, 5)
        total_amount = product["price"] * quantity
        upfront_paid = random.randint(0, int(total_amount * 0.5))
        months = random.choice([3, 6, 12, 24])
        created_at = (datetime.now() - timedelta(days=random.randint(0, 180))).strftime("%Y-%m-%d %H:%M:%S")
        
        cursor = db.conn.cursor()
        cursor.execute(
            """INSERT INTO invoices 
               (customer_id, product_id, quantity, total_amount, upfront_paid, installment_count, installment_amount, start_date, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (customer_id, product["id"], quantity, total_amount, upfront_paid, 
             months, (total_amount - upfront_paid) / months, created_at, created_at)
        )
        invoice_id = cursor.lastrowid
        db.conn.commit()
        
        # إضافة أقساط للفاتورة مع تواريخ استحقاق واقعية
        monthly_payment = (total_amount - upfront_paid) / months
        
        # تحديد تاريخ البداية (من 6 أشهر مضت إلى الآن)
        start_date = datetime.now() - timedelta(days=random.randint(30, 180))
        
        for i in range(months):
            # حساب تاريخ الاستحقاق (كل 30 يوم بدءًا من تاريخ البدء)
            due_date = (start_date + timedelta(days=30*i)).strftime("%Y-%m-%d")
            
            # تحديد حالة القسط بناءً على تاريخ الاستحقاق
            due_datetime = datetime.strptime(due_date, "%Y-%m-%d")
            today = datetime.now()
            
            if due_datetime > today:
                # إذا كان تاريخ الاستحقاق في المستقبل
                status = random.choices(
                    ["مدفوع", "قيد الانتظار"],
                    weights=[0.3, 0.7],
                    k=1
                )[0]
            else:
                # إذا كان تاريخ الاستحقاق في الماضي
                status = random.choices(
                    ["مدفوع", "متأخر"],
                    weights=[0.7, 0.3],
                    k=1
                )[0]
            
            # حساب المبلغ المدفوع بناءً على الحالة
            if status == "مدفوع":
                paid_amount = monthly_payment
                # إذا كان القسط متأخراً وتم دفعه، فليكن قد دفع متأخراً
                if due_datetime < today:
                    paid_amount = monthly_payment * random.uniform(0.8, 1.0)  # دفع جزئي في بعض الأحيان
            else:
                paid_amount = 0.0  # صفر إذا لم يتم الدفع
            
            cursor = db.conn.cursor()
            cursor.execute(
                """INSERT INTO installments 
                   (invoice_id, amount, due_date, paid, customer_id, product_id)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (invoice_id, monthly_payment, due_date, paid_amount, customer_id, product["id"])
            )
            db.conn.commit()
            
            # إضافة سجل الدفع إذا تم الدفع
            if status == "مدفوع":
                due_datetime = datetime.strptime(due_date, "%Y-%m-%d")
                today = datetime.now()
                
                # إذا كان تاريخ الاستحقاق في الماضي، اجعل تاريخ الدفع بعد تاريخ الاستحقاق
                if due_datetime < today:
                    # دفع متأخر (بعد 1-30 يوم من تاريخ الاستحقاق)
                    days_late = random.randint(1, 30)
                    payment_date = (due_datetime + timedelta(days=days_late)).strftime("%Y-%m-%d %H:%M:%S")
                    notes = "دفعة شهرية (متأخرة)"
                else:
                    # دفع مبكر (قبل 0-10 أيام من تاريخ الاستحقاق)
                    days_early = random.randint(0, 10)
                    payment_date = (due_datetime - timedelta(days=days_early)).strftime("%Y-%m-%d %H:%M:%S")
                    notes = "دفعة شهرية"
                
                cursor = db.conn.cursor()
                cursor.execute(
                    """INSERT INTO payments 
                       (invoice_id, amount, payment_date, notes, created_at, updated_at)
                       VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))""",
                    (invoice_id, paid_amount, payment_date, notes)
                )
                db.conn.commit()
    
    db.conn.commit()
    print("تم إنشاء البيانات التجريبية بنجاح!")

if __name__ == "__main__":
    create_dummy_data()
