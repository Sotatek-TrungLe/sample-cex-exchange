from flask import Flask, render_template
import os

app = Flask(__name__)

# Route to render the main HTML page
@app.route('/')
def index():
    return render_template('order_book.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv("FLASK_RUN_PORT", 5000)))
