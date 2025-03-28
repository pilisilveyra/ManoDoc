from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html', active_page='home')

@app.route('/turnos')
def turnos():
    return render_template('turnos.html', active_page='turnos')

@app.route('/historial')
def historial():
    return render_template('historial.html', active_page='historial')

@app.route('/perfil')
def perfil():
    return render_template('perfil.html', active_page='perfil')

@app.route('/contact')
def contact():
    return render_template('contact.html', active_page='contact')



if __name__ == "__main__":
    app.run(debug=True, port=8080)  
