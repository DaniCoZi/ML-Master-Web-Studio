# app/controllers/main_controller.py
from flask import Blueprint, render_template, request, jsonify

main_controller = Blueprint('main', __name__)

@main_controller.route('/')
def index():
    return render_template('index.html')

@main_controller.route('/about')
def about():
    return render_template('about.html')

@main_controller.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        from app.services.email import send_contact_email
        data = request.get_json(silent=True) or {}
        name    = (data.get('name')    or request.form.get('name')    or '').strip()
        email   = (data.get('email')   or request.form.get('email')   or '').strip()
        subject = (data.get('subject') or request.form.get('subject') or '').strip()
        message = (data.get('message') or request.form.get('message') or '').strip()

        if not all([name, email, subject, message]):
            return jsonify({"ok": False, "error": "Todos los campos son obligatorios."}), 400

        success = send_contact_email(name, email, subject, message)
        if success:
            return jsonify({"ok": True, "message": "¡Mensaje enviado! Te responderemos pronto."}), 200
        else:
            return jsonify({"ok": False, "error": "Error al enviar el mensaje. Intenta de nuevo."}), 500

    return render_template('contact.html')

@main_controller.route('/services')
def services():
    return render_template('service.html')

@main_controller.route('/blog')
def blog():
    return render_template('blog.html')

@main_controller.route('/team')
def team():
    return render_template('team.html')

@main_controller.route('/testimonial')
def testimonial():
    return render_template('testimonial.html')

@main_controller.route('/faq')
def faq():
    return render_template('FAQ.html')

@main_controller.route('/feature')
def feature():
    return render_template('feature.html')

@main_controller.route('/404')
def error404():
    return render_template('404.html'), 404

@main_controller.route('/login2')
def login2():
    return render_template('login2.html')