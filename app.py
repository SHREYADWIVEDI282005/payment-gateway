from flask import Flask, render_template, request, jsonify
import razorpay
import random
import string

app = Flask(__name__)

# Razorpay API credenAtials
RAZORPAY_KEY_ID = 'rzp_test_QU4Ldxvblwsg80'
RAZORPAY_KEY_SECRET = 'Wvr258jEGTySk2aKmB1vjdm7'

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# Step 1: Home Page
@app.route('/')
def home():
    # Renders the home page with a form for booking
    return render_template('index.html')

# Step 2: Create Razorpay Order
@app.route('/create_order', methods=['POST'])
def create_order():
    user_name = request.form['name']
    mobile_number = request.form['mobile']
    booking_time = request.form['time']

    amount = 100 * 1  # Amount in paise (e.g., 100 INR)
    order_currency = 'INR'
    order_receipt = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

    # Create Razorpay order
    order = client.order.create({
        'amount': amount,
        'currency': order_currency,
        'receipt': order_receipt,
        'payment_capture': '1'
    })

    # Send order details to frontend
    return jsonify({
        'order_id': order['id'],
        'key': RAZORPAY_KEY_ID,
        'amount': amount,
        'name': user_name,
        'mobile': mobile_number,
        'time': booking_time
    })

# Step 3: Verify Payment
@app.route('/verify_payment', methods=['POST'])
def verify_payment():
    payment_id = request.form['razorpay_payment_id']
    order_id = request.form['razorpay_order_id']
    signature = request.form['razorpay_signature']

    try:
        # Verify the signature
        client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        })

        # Generate a verification ID
        verification_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        return render_template('success.html', verification_id=verification_id)

    except razorpay.errors.SignatureVerificationError:
        return "Payment verification failed!", 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

