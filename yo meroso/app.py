from flask import Flask, request, redirect, session, render_template_string
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

app = Flask(__name__)
app.secret_key = "clave_secreta"

client = MongoClient("mongodb://localhost:27017/")
db = client["nutriapp"]
usuarios = db["usuarios"]
usuarios.create_index("email", unique=True)

index_html = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Inicio</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">

<div class="container mt-5 text-center">
    <h1 class="mb-3">Inicio de Sesion</h1>

    {% if usuario %}
        <p>Bienvenido <b>{{usuario}}</b></p>
        <a href="/tareas" class="btn btn-warning m-2">Ir a tareas</a>
        <a href="/logout" class="btn btn-danger m-2">Cerrar sesion</a>
    {% else %}
        <a href="/login" class="btn btn-primary m-2">Login</a>
        <a href="/registro" class="btn btn-success m-2">Registro</a>
    {% endif %}
</div>

</body>
</html>
"""

login_html = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Login</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light d-flex align-items-center" style="height:100vh;">

<div class="container">
    <div class="row justify-content-center">
        <div class="col-md-4">
            <div class="card shadow p-4">

                <h3 class="text-center mb-3">Iniciar Sesion</h3>

                <form method="POST">
                    <input name="email" type="email" class="form-control mb-3" placeholder="Email" required>
                    <input name="password" type="password" class="form-control mb-3" placeholder="Contraseña" required>
                    <button class="btn btn-primary w-100">Entrar</button>
                </form>

                <p class="text-danger text-center mt-2">{{error}}</p>

                <div class="text-center mt-3">
                    <a href="/registro">Crear cuenta</a><br>
                    <a href="/">Volver</a>
                </div>

            </div>
        </div>
    </div>
</div>

</body>
</html>
"""

registro_html = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Registro</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light d-flex align-items-center" style="height:100vh;">

<div class="container">
    <div class="row justify-content-center">
        <div class="col-md-4">
            <div class="card shadow p-4">

                <h3 class="text-center mb-3">Registro</h3>

                <form method="POST">
                    <input name="nombre" class="form-control mb-3" placeholder="Nombre" required>
                    <input name="email" type="email" class="form-control mb-3" placeholder="Email" required>
                    <input name="password" type="password" class="form-control mb-3" placeholder="Contraseña" required>
                    <button class="btn btn-success w-100">Registrarse</button>
                </form>

                <p class="text-danger text-center mt-2">{{error}}</p>

                <div class="text-center mt-3">
                    <a href="/login">Ya tengo cuenta</a><br>
                    <a href="/">Volver</a>
                </div>

            </div>
        </div>
    </div>
</div>

</body>
</html>
"""

tareas_html = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Tareas</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">

<div class="container mt-5">
    <div class="card p-4 shadow">

        <h3 class="text-center mb-3">Gestor de Tareas</h3>

        <form class="mb-3">
            <input type="text" class="form-control mb-2" placeholder="Nueva tarea">
            <button class="btn btn-primary w-100">Agregar</button>
        </form>

        <ul class="list-group">
            <li class="list-group-item">Hacer ejercicio</li>
            <li class="list-group-item">Estudiar</li>
            <li class="list-group-item">Beber agua</li>
        </ul>

        <div class="text-center mt-3">
            <a href="/" class="btn btn-secondary">Inicio</a>
            <a href="/logout" class="btn btn-danger">Cerrar sesion</a>
        </div>

    </div>
</div>

</body>
</html>
"""

@app.route("/")
def inicio():
    return render_template_string(index_html, usuario=session.get("usuario"))

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        try:
            usuarios.insert_one({
                "nombre": request.form["nombre"],
                "email": request.form["email"],
                "password": request.form["password"]
            })
            return redirect("/login")
        except DuplicateKeyError:
            return render_template_string(registro_html, error="El email ya existe")
    return render_template_string(registro_html, error="")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = usuarios.find_one({
            "email": request.form["email"],
            "password": request.form["password"]
        })
        if usuario:
            session["usuario"] = usuario["email"]
            return redirect("/tareas")
        else:
            return render_template_string(login_html, error="Datos incorrectos")
    return render_template_string(login_html, error="")

@app.route("/tareas")
def tareas():
    if "usuario" in session:
        return render_template_string(tareas_html)
    return redirect("/login")

@app.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)