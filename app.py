from flask import Flask, render_template, jsonify
from venmo_tracker import get_venmo_data
import json
from datetime import datetime

app = Flask(__name__)

def format_transaction(transaction):
    """Format a transaction for display"""
    try:
        # Debug print the transaction structure
        print("\n[🔍] Processing transaction:")
        print(json.dumps(transaction, indent=2))
        
        # Extract relevant information
        note = transaction.get('note', {}).get('content', '')
        date = transaction.get('date', '')
        if date:
            date = datetime.fromisoformat(date.replace('Z', '+00:00'))
            date = date.strftime('%Y-%m-%d %H:%M:%S')
        
        # Determine if it's a payment or charge based on the action
        title = transaction.get('title', {})
        print(f"\n[🔍] Title structure: {json.dumps(title, indent=2)}")
        
        action = title.get('payload', {}).get('action', '')
        print(f"\n[🔍] Action value: {action}")
        
        is_payment = action == 'pay'
        
        # Get the other person's information
        sender = title.get('sender', {})
        receiver = title.get('receiver', {})
        
        print(f"\n[🔍] Sender: {json.dumps(sender, indent=2)}")
        print(f"\n[🔍] Receiver: {json.dumps(receiver, indent=2)}")
        
        # Determine if you are the sender or receiver
        if sender.get('displayName') == 'you':
            other_person = receiver.get('displayName', 'Unknown')
        else:
            other_person = sender.get('displayName', 'Unknown')
        
        return {
            'note': note,
            'date': date,
            'type': 'Payment' if is_payment else 'Charge',
            'color': 'text-red-500' if is_payment else 'text-green-500',
            'other_person': other_person,
            'direction': 'to' if is_payment else 'from'
        }
    except Exception as e:
        print(f"Error formatting transaction: {e}")
        print(f"Transaction data: {json.dumps(transaction, indent=2)}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/transactions')
def get_transactions():
    try:
        # Get the data from venmo_tracker
        data = get_venmo_data()
        
        # Extract stories from the response
        stories = data.get('stories', [])
        
        # Format each story
        formatted_transactions = []
        for story in stories:
            formatted = format_transaction(story)
            if formatted:
                formatted_transactions.append(formatted)
        
        return jsonify({
            'success': True,
            'transactions': formatted_transactions,
            'raw_data': data  # Include the raw data in the response
        })
    except Exception as e:
        print(f"Error processing transactions: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True) 