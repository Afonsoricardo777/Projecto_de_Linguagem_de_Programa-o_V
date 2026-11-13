from datetime import datetime
from flask import Flask, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = "chave_secreta_seguranca_loja"

# Base de dados simulada em memória para armazenar operadores e as suas senhas
# Exemplo inicial vazio ou pré-registo (vamos permitir registo na tela)
OPERADORES_DB = {"operador": "1234"}  # nome_usuario: senha

# Contador automático de vendas por operador
VENDAS_CONTADOR = {}


@app.route("/", methods=["GET", "POST"])
def login():
  if session.get("logado"):
    return redirect(url_for("fatura"))

  erro = None
  sucesso = None
  acao = request.form.get("acao")

  if request.method == "POST":
    usuario = request.form.get("usuario").strip().lower()
    senha = request.form.get("senha")
    nome_completo = request.form.get("nome_completo")

    if acao == "registar":
      # Registar novo operador
      if usuario in OPERADORES_DB:
        erro = "Este nome de utilizador já existe. Escolha outro."
      else:
        OPERADORES_DB[usuario] = senha
        # Guardar também o nome completo associado
        session["nome_completo_registo"] = nome_completo
        sucesso = (
            "Conta criada com sucesso! Faça login com os seus dados."
        )

    elif acao == "entrar":
      # Fazer Login
      if usuario in OPERADORES_DB and OPERADORES_DB[usuario] == senha:
        session["logado"] = True
        session["usuario_id"] = usuario
        # Se houver nome completo guardado, usa-o, senão usa o identificador
        session["operador_nome"] = (
            nome_completo
            if nome_completo
            else usuario.capitalize()
        )
        if session["usuario_id"] not in VENDAS_CONTADOR:
          VENDAS_CONTADOR[session["usuario_id"]] = 0
        return redirect(url_for("fatura"))
      else:
        erro = "Utilizador ou senha incorretos."

  return render_template("login.html", erro=erro, sucesso=sucesso)


@app.route("/fatura", methods=["GET", "POST"])
def fatura():
  if not session.get("logado"):
    return redirect(url_for("login"))

  operador_id = session.get("usuario_id")
  if operador_id not in VENDAS_CONTADOR:
    VENDAS_CONTADOR[operador_id] = 0

  resultado = None
  if request.method == "POST":
    nome = request.form.get("nome")
    genero = request.form.get("genero")
    tipo_produto = request.form.get("tipo_produto")
    prioridade = request.form.get("prioridade")
    data_compra = datetime.now().strftime("%d/%m/%Y %H:%M")

    try:
      valor_compras = float(request.form.get("valor_compras"))
    except (ValueError, TypeError):
      valor_compras = 0.0

    bonus = 0.0
    if valor_compras > 100000:
      bonus = valor_compras * 0.10

    valor_final = valor_compras - bonus

    # Incrementar automaticamente o número de vendas deste operador
    VENDAS_CONTADOR[operador_id] += 1
    numero_venda = VENDAS_CONTADOR[operador_id]

    resultado = {
        "nome": nome,
        "genero": genero,
        "tipo_produto": tipo_produto,
        "data_compra": data_compra,
        "prioridade": prioridade,
        "valor_compras": valor_compras,
        "bonus": bonus,
        "valor_final": valor_final,
        "tem_bonus": valor_compras > 100000,
        "numero_venda": numero_venda,
    }

  return render_template(
      "index.html",
      resultado=resultado,
      operador=session.get("operador_nome"),
      total_vendas=VENDAS_CONTADOR[operador_id],
  )
@app.route("/logout")
def logout():
  session.clear()
  return redirect(url_for("login"))

if __name__ == "__main__":
  app.run(debug=True)