from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/providers')
def providers():
    # Basic placeholder for provider search functionality
    query = request.args.get('q', '')
    # In real app, you'd search the DB here
    return render_template('providers.html', query=query)

@app.route('/appointment')
def appointment():
    return render_template('appointement.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

if __name__ == '__main__':
    app.run(debug=True)
