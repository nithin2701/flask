from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import json

app = Flask(__name__)
app.secret_key = 'rk-gold-company-super-secret-key-2025'  # Change this to a strong secret key

# Load site data from JSON file
SITE_DATA_FILE = 'site_data.json'
def load_site_data():
    try:
        with open(SITE_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {
            'gold_rate': 10500,
            'offers': [
                "Special festive discounts available."
            ],
            'company_info': "RK Gold Company is your trusted partner for pure gold and exclusive jewelry offers. Visit us for the best rates and quality assurance."
        }

def save_site_data(data):
    with open(SITE_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

site_data = load_site_data()

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'gold123'  # Change this to a strong password

# Initialize SQLite database for inquiries
def init_db():
    conn = sqlite3.connect('inquiries.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS inquiries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template('index.html',
        gold_rate=site_data['gold_rate'],
        offers=site_data['offers'],
        company_info=site_data['company_info'],
        company_name="RK Gold Company",
        tagline="India's Most Trusted Gold Buyers - Instant Cash for Gold & Silver",
        services=[
            "Sell Gold & Silver Jewelry with 100% Transparency",
            "Get Instant Cash Payment at Best Market Rates",
            "Free Gold Rate Enquiry & Evaluation",
            "Corporate & Bulk Gold Buying Solutions",
            "Secure, Hassle-Free, and Confidential Transactions"
        ],
        highlights=[
            "ISO Certified Business",
            "Multiple Branches Across India",
            "Award-Winning Customer Service",
            "Trusted by 10,000+ Customers"
        ]
    )

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    error = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        else:
            error = 'Invalid username or password.'
    return render_template('admin_login.html', error=error)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    error = ''
    message = ''
    if request.method == 'POST':
        gold_rate_input = request.form.get('gold_rate', '').replace(',', '').replace('₹', '').strip()
        offers_input = request.form.get('offers', '')
        company_info_input = request.form.get('company_info', '')
        try:
            gold_rate = int(gold_rate_input)
        except ValueError:
            error = 'Please enter a valid number for gold rate.'
        if not error:
            site_data['gold_rate'] = gold_rate
            site_data['offers'] = [o.strip() for o in offers_input.split('\n') if o.strip()]
            site_data['company_info'] = company_info_input
            save_site_data(site_data)
            message = 'Changes saved successfully!'
    offers_text = '\n'.join(site_data['offers'])
    # Fetch inquiries from DB
    conn = sqlite3.connect('inquiries.db')
    c = conn.cursor()
    c.execute('SELECT name, email, phone, message, created_at FROM inquiries ORDER BY created_at DESC')
    inquiries = c.fetchall()
    conn.close()
    return render_template('admin.html',
        gold_rate=site_data['gold_rate'],
        offers_text=offers_text,
        company_info=site_data['company_info'],
        message=message,
        error=error,
        inquiries=inquiries)

@app.route('/admin-logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/inquiry', methods=['POST'])
def inquiry():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    message = request.form.get('message')
    if name and email and phone and message:
        conn = sqlite3.connect('inquiries.db')
        c = conn.cursor()
        c.execute('INSERT INTO inquiries (name, email, phone, message) VALUES (?, ?, ?, ?)', (name, email, phone, message))
        conn.commit()
        conn.close()
        return 'success'
    return 'error', 400

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
