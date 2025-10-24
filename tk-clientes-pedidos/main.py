import tkinter as tk
from tkinter import ttk
from db import init_db
from views.clientes_view import ClientesView
from views.pedidos_view import PedidosView
from views.produtos_view import ProdutosFrame

def abrir_clientes():
    janela = tk.Toplevel(root)
    janela.title("Clientes")
    ClientesView(janela)

def abrir_pedidos():
    janela = tk.Toplevel(root)
    janela.title("Pedidos")
    PedidosView(janela)

def abrir_produtos():
    janela = tk.Toplevel(root)
    janela.title("Produtos")
    ProdutosFrame(janela)

root = tk.Tk()
root.title("Sistema Clientes, Pedidos e Produtos")
root.geometry("500x300")

init_db()

menu = tk.Menu(root)
root.config(menu=menu)
menu_cad = tk.Menu(menu, tearoff=0)
menu_cad.add_command(label="Clientes", command=abrir_clientes)
menu_cad.add_command(label="Pedidos", command=abrir_pedidos)
menu_cad.add_command(label="Produtos", command=abrir_produtos)
menu.add_cascade(label="Cadastros", menu=menu_cad)

ttk.Label(root, text="Bem-vindo ao Sistema de Clientes, Pedidos e Produtos",
          font=("Arial",12)).pack(pady=50)

root.mainloop()
