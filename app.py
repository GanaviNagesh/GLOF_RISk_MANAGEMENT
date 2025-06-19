from flask import Flask, jsonify, render_template, request, redirect, url_for
from glof_detection import check_glof_status, send_alert

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        uname = request.form.get('username', '').strip()
        pwd = request.form.get('password', '').strip()
        print(f"Login attempt - Username: {uname}, Password: {pwd}")
        
        # Check GLOF status after login (default lake or specify)
        glof_status, water_pixels = check_glof_status('imja-tsho')

        # Redirect to dashboard with alert status
        return redirect(url_for('dashboard', login_alert=glof_status, pixels=water_pixels))
    
    return render_template('login.html')


@app.route('/alert', methods=['GET', 'POST'])
def manual_alert():
    alert_sent = False
    if request.method == 'POST':
        priority = request.form.get('priority')
        custom_message = request.form.get('message')
        full_message = f"{priority}\n{custom_message}"
        send_alert(full_message)
        alert_sent = True
    return render_template('alert.html', alert_sent=alert_sent)


@app.route('/dashboard')
def dashboard():
    # Get status from login redirect (if any)
    glof_status = request.args.get('login_alert')
    water_pixels = request.args.get('pixels')

    # If not redirected, do a fresh check for default lake
    if not glof_status:
        glof_status, water_pixels = check_glof_status('imja-tsho')
    
    return render_template('dashboard.html', status=glof_status, pixels=water_pixels)


@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/map')
def map():
    return render_template('map.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/support')
def support():
    return render_template('support.html')


@app.route('/check_glof')
def check_and_alert():
    glof_status, water_pixels = check_glof_status('imja-tsho')
    if glof_status == "GLOF Detected":
        send_alert("🚨 GLOF Detected at Imja Lake!")
    return redirect(url_for('dashboard'))


# NEW API endpoint to get GLOF status for a specific lake
@app.route('/api/glof-monitoring')
def api_glof_monitoring():
    lake = request.args.get('lake', 'imja-tsho').lower()
    status, pixels = check_glof_status(lake)
    return jsonify({
        "status": status,
        "pixels": pixels,
        "lake": lake
    })


if __name__ == '__main__':
    app.run(debug=True)
