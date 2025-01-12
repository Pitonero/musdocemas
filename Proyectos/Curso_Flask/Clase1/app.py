from flask import Flask, render_template

app = Flask(__name__) 

@app.route("/")

def hola_mundo():
    return "Hola Mundo cruel!!"

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

@app.route("/primera")
def template_primera():
    return render_template("primera_pagina.html")

if __name__=="__main__":
    app.run()