import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime

# Banco de dados
conn = sqlite3.connect('rodas.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS rodas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    aro INTEGER NOT NULL,
    preco REAL NOT NULL,
    quantidade INTEGER NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS movimentacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roda_id INTEGER,
    tipo TEXT,
    quantidade INTEGER,
    data TEXT,
    FOREIGN KEY (roda_id) REFERENCES rodas (id)
)
''')
conn.commit()

# Função de Login
def fazer_login():
    user = entrada_user.get()
    senha = entrada_senha.get()
    if user == "test" and senha == "1234":
        login.destroy()
        tela_principal()
    else:
        messagebox.showerror("Erro", "Usuário ou senha inválidos")

# Tela Principal
def tela_principal():
    app = tk.Tk()
    app.title("Design Rodas")
    app.state('zoomed')  # Mantém maximizado com minimizar e maximizar

    app.configure(bg="#f0f0f0")

    frame_menu = tk.Frame(app, bg="#ececec", height=150)
    frame_menu.pack(fill='x')

    frame_conteudo = tk.Frame(app, bg="#ffffff")
    frame_conteudo.pack(fill='both', expand=True)

    def limpar_frame():
        for widget in frame_conteudo.winfo_children():
            widget.destroy()

    def abrir_cadastro():
        limpar_frame()
        tk.Label(frame_conteudo, text="Cadastro de Rodas", font=("Arial", 16), bg="#ffffff").pack(pady=10)

        tk.Label(frame_conteudo, text="Nome:", bg="#ffffff").pack()
        nome_entry = tk.Entry(frame_conteudo, width=30)
        nome_entry.pack()

        tk.Label(frame_conteudo, text="Aro:", bg="#ffffff").pack()
        aro_entry = tk.Entry(frame_conteudo, width=10)
        aro_entry.pack()

        tk.Label(frame_conteudo, text="Preço:", bg="#ffffff").pack()
        preco_entry = tk.Entry(frame_conteudo, width=10)
        preco_entry.pack()

        tk.Label(frame_conteudo, text="Quantidade:", bg="#ffffff").pack()
        quantidade_entry = tk.Entry(frame_conteudo, width=10)
        quantidade_entry.pack()

        def cadastrar_roda():
            if not (nome_entry.get() and aro_entry.get() and preco_entry.get() and quantidade_entry.get()):
                messagebox.showwarning("Aviso", "Preencha todos os campos.")
                return
            cursor.execute('''
                INSERT INTO rodas (nome, aro, preco, quantidade) VALUES (?, ?, ?, ?)
            ''', (nome_entry.get(), int(aro_entry.get()), float(preco_entry.get()), int(quantidade_entry.get())))
            conn.commit()
            novo_id = cursor.lastrowid
            messagebox.showinfo("Sucesso", f"Roda cadastrada com sucesso!\nID da roda: {novo_id}")

        tk.Button(frame_conteudo, text="Cadastrar", bg="#4CAF50", fg="white", command=cadastrar_roda).pack(pady=10)

    def abrir_listagem():
        limpar_frame()
        tk.Label(frame_conteudo, text="Listagem de Rodas", font=("Arial", 16), bg="#ffffff").pack(pady=10)

        colunas = ("ID", "Nome", "Aro", "Preço", "Quantidade")
        tree = ttk.Treeview(frame_conteudo, columns=colunas, show="headings", height=15)
        for col in colunas:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        tree.pack()

        filtro_frame = tk.Frame(frame_conteudo, bg="#ffffff")
        filtro_frame.pack(pady=10)
        tk.Label(filtro_frame, text="Filtrar por Aro:", bg="#ffffff").pack(side='left')
        filtro_entry = tk.Entry(filtro_frame, width=10)
        filtro_entry.pack(side='left', padx=5)

        def filtrar():
            tree.delete(*tree.get_children())
            aro = filtro_entry.get()
            if aro.isdigit():
                cursor.execute('SELECT * FROM rodas WHERE aro=?', (int(aro),))
            else:
                cursor.execute('SELECT * FROM rodas')
            for row in cursor.fetchall():
                tree.insert('', 'end', values=row)

        tk.Button(filtro_frame, text="Filtrar", command=filtrar, bg="#2196F3", fg="white").pack(side='left')
        tk.Button(filtro_frame, text="Listar Tudo", command=lambda: [filtro_entry.delete(0, 'end'), filtrar()],
                  bg="#FFC107").pack(side='left', padx=5)

        filtrar()

    def abrir_movimentacao(tipo):
        limpar_frame()
        operacao = "Entrada" if tipo == "entrada" else "Saída"
        tk.Label(frame_conteudo, text=f"Registrar {operacao}", font=("Arial", 16), bg="#ffffff").pack(pady=10)

        colunas = ("ID", "Nome", "Aro", "Preço", "Quantidade")
        tree = ttk.Treeview(frame_conteudo, columns=colunas, show="headings", height=10)
        for col in colunas:
            tree.heading(col, text=col)
            tree.column(col, width=140)
        tree.pack()

        cursor.execute('SELECT * FROM rodas')
        for row in cursor.fetchall():
            tree.insert('', 'end', values=row)

        def movimentar():
            item = tree.focus()
            if not item:
                messagebox.showwarning("Aviso", "Selecione uma roda.")
                return
            quantidade = simpledialog.askinteger("Quantidade", f"Quantidade para {operacao.lower()}:")
            if not quantidade or quantidade <= 0:
                return
            roda = tree.item(item)['values']
            nova_quantidade = roda[4] + quantidade if tipo == "entrada" else roda[4] - quantidade
            if nova_quantidade < 0:
                messagebox.showerror("Erro", "Estoque insuficiente!")
                return
            cursor.execute('UPDATE rodas SET quantidade=? WHERE id=?', (nova_quantidade, roda[0]))
            cursor.execute('''
                INSERT INTO movimentacoes (roda_id, tipo, quantidade, data) 
                VALUES (?, ?, ?, ?)
            ''', (roda[0], tipo, quantidade, datetime.now().strftime("%d/%m/%Y")))
            conn.commit()
            messagebox.showinfo("Sucesso", f"{operacao} registrada!")
            abrir_movimentacao(tipo)

        tk.Button(frame_conteudo, text=f"Registrar {operacao}", command=movimentar,
                  bg="#4CAF50" if tipo == "entrada" else "#E53935", fg="white").pack(pady=10)

    def abrir_movimentacoes():
        limpar_frame()
        tk.Label(frame_conteudo, text="Histórico de Movimentações", font=("Arial", 16), bg="#ffffff").pack(pady=10)

        entrada_frame = tk.Frame(frame_conteudo, bg="#d0ffd0")
        saida_frame = tk.Frame(frame_conteudo, bg="#ffd0d0")
        entrada_frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)
        saida_frame.pack(side="right", fill="both", expand=True, padx=10, pady=5)

        tk.Label(entrada_frame, text="Entradas", bg="#d0ffd0", font=("Arial", 14)).pack(pady=5)
        entrada_text = tk.Text(entrada_frame, height=25)
        entrada_text.pack(fill="both", expand=True)

        tk.Label(saida_frame, text="Saídas", bg="#ffd0d0", font=("Arial", 14)).pack(pady=5)
        saida_text = tk.Text(saida_frame, height=25)
        saida_text.pack(fill="both", expand=True)

        cursor.execute('''
            SELECT r.nome, r.aro, m.tipo, m.quantidade, m.data 
            FROM movimentacoes m
            JOIN rodas r ON m.roda_id = r.id
            ORDER BY m.id ASC
        ''')
        for nome, aro, tipo, quantidade, data in cursor.fetchall():
            linha = f"{data} - {nome} ARO {aro} {'entrou' if tipo == 'entrada' else 'saiu'} {quantidade}\n"
            if tipo == "entrada":
                entrada_text.insert('end', linha)
            else:
                saida_text.insert('end', linha)

    # Botões de Menu
    tk.Button(frame_menu, text="Cadastrar Roda", width=20, height=5, bg="#4CAF50", fg="white", command=abrir_cadastro).pack(side="left", padx=10, pady=20)
    tk.Button(frame_menu, text="Listar/Filtrar Aro", width=20, height=5, bg="#2196F3", fg="white", command=abrir_listagem).pack(side="left", padx=10)
    tk.Button(frame_menu, text="Registrar Entrada", width=20, height=5, bg="#8BC34A", fg="white", command=lambda: abrir_movimentacao("entrada")).pack(side="left", padx=10)
    tk.Button(frame_menu, text="Registrar Saída", width=20, height=5, bg="#E53935", fg="white", command=lambda: abrir_movimentacao("saida")).pack(side="left", padx=10)
    tk.Button(frame_menu, text="Movimentações", width=20, height=5, bg="#FFC107", fg="black", command=abrir_movimentacoes).pack(side="left", padx=10)
    tk.Button(frame_menu, text="Sair", width=20, height=5, bg="#FF5722", fg="white", command=app.quit).pack(side="left", padx=10, pady=20)

    app.mainloop()

# Tela de Login
login = tk.Tk()
login.title("Login - Design Rodas")
login.state('zoomed')  # Mantém a tela maximizada com minimizar/maximizar

# Frame centralizado
frame_login = tk.Frame(login, bg="#ececec")
frame_login.place(relx=0.5, rely=0.5, anchor="center")

tk.Label(frame_login, text="Usuário:", font=("Arial", 14), bg="#ececec").pack(pady=10)
entrada_user = tk.Entry(frame_login, font=("Arial", 14))
entrada_user.pack()

tk.Label(frame_login, text="Senha:", font=("Arial", 14), bg="#ececec").pack(pady=10)
entrada_senha = tk.Entry(frame_login, show="*", font=("Arial", 14))
entrada_senha.pack()

btn_login = tk.Button(frame_login, text="Entrar", command=fazer_login, bg="#4CAF50", fg="white", font=("Arial", 14))
btn_login.pack(pady=20)

login.mainloop()
conn.close()
