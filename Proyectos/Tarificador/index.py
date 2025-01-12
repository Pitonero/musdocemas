from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("tarificador_vida.html")
 
@app.route('/abaut') 
def abaut():
    return render_template("tarificador_vida.html")
    #return render_template("abaut.html")

@app.route("/elegante") 
def hola_mundo_elegante():
    return """
    <html>
        <body>
            <h1>saludos!!</h1>
            <p>Hola Mundo!!</p>
        </body>    
    </html>    
"""

if __name__ == '__main__':
    app.run(debug=True) 
