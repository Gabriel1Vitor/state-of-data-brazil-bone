from flask import Flask , render_template

app = Flask(__name__)

@app.route("/")
def hello_world():
    return render_template("index.html")

@app.route('/radar')
def radar():
    return render_template('radar.html')

@app.route('/salario-real')
def salario():
    return render_template('salario-real.html')

@app.route('/volta')
def volta():
    return render_template('volta-ao-escritorio.html')

if __name__=="__main__":
    app.run(debug=True)