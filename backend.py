from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Connect to DB
def get_db():
    return sqlite3.connect('expenses.db')

# Add Expense
@app.route('/add_expense', methods=['POST'])
def add_expense():
    data = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT INTO expenses (title, category, amount, date) VALUES (?,?,?,?)',
              (data['title'], data['category'], data['amount'], data['date']))
    conn.commit()
    conn.close()
    return jsonify({'message':'Expense added'})

# Get Expenses
@app.route('/get_expenses', methods=['GET'])
def get_expenses():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM expenses')
    rows = c.fetchall()
    conn.close()
    return jsonify(rows)

# Delete Expense
@app.route('/delete_expense/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM expenses WHERE id=?', (expense_id,))
    conn.commit()
    conn.close()
    return jsonify({'message':'Expense deleted'})

if __name__ == "__main__":
    app.run(debug=True)