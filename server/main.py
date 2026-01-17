from fastapi import FastAPI, HTTPException
import pandas as pd
import os

app = FastAPI(title="API de Clientes")

DB_PATH = os.path.join(os.path.dirname(__file__), "database.csv")


def carregar_dados():
    if not os.path.exists(DB_PATH):
        df = pd.DataFrame(
            columns=["id", "nome", "idade", "tempo_cadastro", "usuario", "senha"]
        )
        df.to_csv(DB_PATH, index=False)
    return pd.read_csv(DB_PATH)


def salvar_dados(df):
    df.to_csv(DB_PATH, index=False)


@app.get("/")
def status():
    return {"status": "Servidor ativo"}


@app.get("/clientes")
def listar_clientes():
    df = carregar_dados()
    return df.to_dict(orient="records")


@app.get("/clientes/{cliente_id}")
def cliente_por_id(cliente_id: int):
    df = carregar_dados()
    cliente = df[df["id"] == cliente_id]

    if cliente.empty:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    return cliente.to_dict(orient="records")[0]


@app.get("/clientes/mais-antigo")
def cliente_mais_antigo():
    df = carregar_dados()

    if df.empty:
        raise HTTPException(status_code=404, detail="Nenhum cliente cadastrado")

    cliente = df.loc[df["tempo_cadastro"].idxmax()]
    return cliente.to_dict()


@app.post("/clientes")
def inserir_cliente(cliente: dict):
    df = carregar_dados()

    if cliente["id"] in df["id"].values:
        raise HTTPException(status_code=400, detail="ID já existente")

    df = pd.concat([df, pd.DataFrame([cliente])])
    salvar_dados(df)

    return {"mensagem": "Cliente inserido com sucesso"}


@app.patch("/clientes/{cliente_id}")
def atualizar_cliente(cliente_id: int, campo: str, valor: str):
    df = carregar_dados()

    if cliente_id not in df["id"].values:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    if campo not in df.columns:
        raise HTTPException(status_code=400, detail="Campo inválido")

    df.loc[df["id"] == cliente_id, campo] = valor
    salvar_dados(df)

    return {"mensagem": "Cliente atualizado com sucesso"}


@app.delete("/clientes/{cliente_id}")
def remover_cliente(cliente_id: int):
    df = carregar_dados()

    if cliente_id not in df["id"].values:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    df = df[df["id"] != cliente_id]
    salvar_dados(df)

    return {"mensagem": "Cliente removido com sucesso"}
