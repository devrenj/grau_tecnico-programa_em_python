import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

def inicializar_banco():
    conexao = sqlite3.connect("sistema_provas.db")
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS turmas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alunos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            turma_id INTEGER,
            FOREIGN KEY(turma_id) REFERENCES turmas(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS disciplinas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            sigla TEXT NOT NULL UNIQUE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS provas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT NOT NULL UNIQUE,
            nome TEXT NOT NULL,
            disciplina TEXT NOT NULL,
            qtd_questoes INTEGER NOT NULL,
            data_prova TEXT NOT NULL,
            raio_respostas TEXT NOT NULL,
            gabarito TEXT NOT NULL,
            tipo_avaliacao TEXT DEFAULT 'PROVA',
            turma_nome TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resultados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno_id INTEGER,
            prova_id INTEGER,
            acertos INTEGER,
            erros INTEGER,
            porcentagem REAL,
            respostas_aluno TEXT,
            comentario TEXT,
            FOREIGN KEY(aluno_id) REFERENCES alunos(id),
            FOREIGN KEY(prova_id) REFERENCES provas(id)
        )
    """)

    conexao.commit()
    conexao.close()

class SistemaProvasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestão de Provas e Notas")
        
        largura = 1020
        altura = 720
        largura_tela = self.root.winfo_screenwidth()
        altura_tela = self.root.winfo_screenheight()
        pos_x = (largura_tela // 2) - (largura // 2)
        pos_y = (altura_tela // 2) - (altura // 2)
        self.root.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")
        
        inicializar_banco()
        try:
            self.root.iconbitmap("icone.ico")
        except Exception:
            pass

        self.criar_componentes()
        self.carregar_turmas()

    def criar_componentes(self):
        painel_topo = tk.LabelFrame(self.root, text="Painel de Gestão", font=("Arial", 10, "bold"))
        painel_topo.pack(fill="x", padx=10, pady=10)

        f_turma = tk.Frame(painel_topo)
        f_turma.pack(fill="x", padx=5, pady=4)
        
        tk.Label(f_turma, text="Turma:", width=8, anchor="w").pack(side="left")
        self.combo_turmas = ttk.Combobox(f_turma, state="readonly", width=20)
        self.combo_turmas.pack(side="left", padx=5)
        self.combo_turmas.bind("<<ComboboxSelected>>", self.ao_selecionar_turma)

        self.btn_nota_turma = tk.Button(f_turma, text="Visualizar Notas da Turma", command=self.abrir_notas_turma, state="disabled")
        self.btn_nota_turma.pack(side="left", padx=10)

        self.btn_media_turma = tk.Button(f_turma, text="Visualizar Média da Turma", command=self.abrir_media_turma, state="disabled")
        self.btn_media_turma.pack(side="left", padx=10)

        f_aluno = tk.Frame(painel_topo)
        f_aluno.pack(fill="x", padx=5, pady=4)

        tk.Label(f_aluno, text="Aluno:", width=8, anchor="w").pack(side="left")
        self.combo_alunos = ttk.Combobox(f_aluno, state="readonly", width=20)
        self.combo_alunos.pack(side="left", padx=5)
        self.combo_alunos.bind("<<ComboboxSelected>>", self.ao_selecionar_aluno)

        self.btn_editar_aluno = tk.Button(f_aluno, text="Editar Aluno", command=self.abrir_alterar_aluno, state="disabled")
        self.btn_editar_aluno.pack(side="left", padx=10)

        self.btn_visualizar_notas = tk.Button(f_aluno, text="Visualizar Notas", command=self.abrir_visualizar_notas, state="disabled")
        self.btn_visualizar_notas.pack(side="left", padx=10)

        f_ger = tk.Frame(painel_topo)
        f_ger.pack(fill="x", padx=5, pady=6)

        self.btn_gerenciar_provas = tk.Button(f_ger, text="Gerenciar Provas", command=self.abrir_gerenciar_provas)
        self.btn_gerenciar_provas.pack(side="left", padx=5)

        self.btn_gerenciar_trabalhos = tk.Button(f_ger, text="Gerenciar Trabalhos", command=self.abrir_gerenciar_trabalhos)
        self.btn_gerenciar_trabalhos.pack(side="left", padx=15)

        self.painel_correcao = tk.LabelFrame(self.root, text="Aplicação e Correção de Avaliação", font=("Arial", 10, "bold"))
        self.painel_correcao.pack(fill="both", expand=True, padx=10, pady=5)

        tk.Label(self.painel_correcao, text="Selecione a Prova ou Trabalho Aplicado:").pack(anchor="w", padx=10, pady=5)
        self.combo_provas = ttk.Combobox(self.painel_correcao, state="readonly", width=60)
        self.combo_provas.pack(anchor="w", padx=10, pady=5)
        self.combo_provas.bind("<<ComboboxSelected>>", self.carregar_interface_respostas)

        self.canvas_container = tk.Canvas(self.painel_correcao)
        self.scrollbar = ttk.Scrollbar(self.painel_correcao, orient="vertical", command=self.canvas_container.yview)
        self.frame_respostas = ttk.Frame(self.canvas_container)

        self.frame_respostas.bind(
            "<Configure>",
            lambda e: self.canvas_container.configure(scrollregion=self.canvas_container.bbox("all"))
        )
        self.canvas_container.create_window((0, 0), window=self.frame_respostas, anchor="nw")
        self.canvas_container.configure(yscrollcommand=self.scrollbar.set)

        self.canvas_container.pack(side="top", fill="both", expand=True, padx=10, pady=5)
        self.scrollbar.pack(side="right", fill="y", pady=5)

        self.btn_salvar_correcao = tk.Button(self.painel_correcao, text="Salvar e Corrigir", command=self.salvar_correcao_aluno, bg="#d4edda", font=("Arial", 10, "bold"), state="disabled")
        self.btn_salvar_correcao.pack(anchor="center", pady=15)

    def obter_nome_completo_disciplina(self, sigla):
        conexao = sqlite3.connect("sistema_provas.db")
        cursor = conexao.cursor()
        cursor.execute("SELECT nome FROM disciplinas WHERE sigla = ?", (sigla,))
        res = cursor.fetchone()
        conexao.close()
        return res[0] if res else sigla

    def carregar_turmas(self):
        conexao = sqlite3.connect("sistema_provas.db")
        cursor = conexao.cursor()
        cursor.execute("SELECT nome FROM turmas")
        turmas = [row[0] for row in cursor.fetchall()]
        conexao.close()

        if not turmas:
            lista_final = ["(CRIAR NOVO)"]
        else:
            lista_final = ["(SELECIONAR)", "(CRIAR NOVO)"] + turmas

        self.combo_turmas['values'] = lista_final
        if lista_final:
            self.combo_turmas.current(0)
            self.carregar_alunos_da_turma(lista_final[0])

    def ao_selecionar_turma(self, event):
        selecao = self.combo_turmas.get()
        if selecao == "(CRIAR NOVO)":
            self.pedir_nova_turma()
        elif selecao == "(SELECIONAR)":
            self.carregar_alunos_da_turma("(SELECIONAR)")
        else:
            self.carregar_alunos_da_turma(selecao)
            self.btn_nota_turma.config(state="normal")
            self.btn_media_turma.config(state="normal")
            self.carregar_provas_combobox()

    def pedir_nova_turma(self):
        janela_nova = tk.Toplevel(self.root)
        janela_nova.title("Nova Turma")
        
        largura = 300
        altura = 150
        pos_x = (self.root.winfo_screenwidth() // 2) - (largura // 2)
        pos_y = (self.root.winfo_screenheight() // 2) - (altura // 2)
        janela_nova.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")

        tk.Label(janela_nova, text="Nome da Turma (Ex: INF14):").pack(pady=10)
        entry_turma = tk.Entry(janela_nova, width=25)
        entry_turma.pack()
        entry_turma.focus_set()

        def salvar(event=None):
            nome = entry_turma.get().strip().upper()
            if not nome:
                messagebox.showerror("Erro", "O nome não pode estar vazio.")
                return
            
            conexao = sqlite3.connect("sistema_provas.db")
            cursor = conexao.cursor()
            try:
                cursor.execute("INSERT INTO turmas (nome) VALUES (?)", (nome,))
                conexao.commit()
                conexao.close()
                janela_nova.destroy()
                self.carregar_turmas()
                self.combo_turmas.set(nome)
                self.carregar_alunos_da_turma(nome)
            except sqlite3.IntegrityError:
                messagebox.showerror("Erro", "Essa turma já existe.")
                conexao.close()

        entry_turma.bind("<Return>", salvar)
        tk.Button(janela_nova, text="Salvar", command=salvar).pack(pady=15)

    def carregar_alunos_da_turma(self, nome_turma):
        self.limpar_painel_respostas_parcial()
        if nome_turma in ["(SELECIONAR)", "(CRIAR NOVO)"]:
            conexao = sqlite3.connect("sistema_provas.db")
            cursor = conexao.cursor()
            cursor.execute("SELECT nome FROM turmas")
            tem_turmas = cursor.fetchone()
            conexao.close()
            
            if not tem_turmas:
                self.combo_alunos['values'] = ["(CRIAR NOVO)"]
            else:
                self.combo_alunos['values'] = ["(SELECIONAR)", "(CRIAR NOVO)"]
            self.combo_alunos.current(0)
            self.verificar_botaonotas()
            self.btn_nota_turma.config(state="disabled")
            self.btn_media_turma.config(state="disabled")
            self.carregar_provas_combobox()
            return

        conexao = sqlite3.connect("sistema_provas.db")
        cursor = conexao.cursor()
        cursor.execute("SELECT id FROM turmas WHERE nome = ?", (nome_turma,))
        res = cursor.fetchone()
        
        if not res:
            conexao.close()
            self.combo_alunos['values'] = ["(CRIAR NOVO)"]
            self.combo_alunos.current(0)
            self.verificar_botaonotas()
            self.carregar_provas_combobox()
            return

        turma_id = res[0]
        cursor.execute("SELECT nome FROM alunos WHERE turma_id = ?", (turma_id,))
        alunos = [row[0] for row in cursor.fetchall()]
        conexao.close()

        if not alunos:
            lista_final = ["(CRIAR NOVO)"]
        else:
            lista_final = ["(SELECIONAR)", "(CRIAR NOVO)"] + alunos

        self.combo_alunos['values'] = lista_final
        self.combo_alunos.current(0)
        self.verificar_botaonotas()
        self.carregar_provas_combobox()

    def ao_selecionar_aluno(self, event):
        aluno_sel = self.combo_alunos.get()
        if aluno_sel == "(CRIAR NOVO)":
            self.pedir_novo_aluno()
        else:
            self.limpar_painel_respostas_parcial()
            self.verificar_botaonotas()
            self.carregar_provas_combobox()

    def limpar_painel_respostas_parcial(self):
        for widget in self.frame_respostas.winfo_children():
            widget.destroy()
        self.btn_salvar_correcao.config(state="disabled")

    def pedir_novo_aluno(self):
        turma_atual = self.combo_turmas.get()
        if turma_atual in ["(SELECIONAR)", "(CRIAR NOVO)"]:
            messagebox.showwarning("Aviso", "Selecione uma turma válida primeiro.")
            self.combo_alunos.current(0)
            return

        janela_aluno = tk.Toplevel(self.root)
        janela_aluno.title("Novo Aluno")
        
        largura = 300
        altura = 150
        pos_x = (self.root.winfo_screenwidth() // 2) - (largura // 2)
        pos_y = (self.root.winfo_screenheight() // 2) - (altura // 2)
        janela_aluno.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")

        tk.Label(janela_aluno, text=f"Nome do Aluno para {turma_atual}:").pack(pady=10)
        entry_aluno = tk.Entry(janela_aluno, width=25)
        entry_aluno.pack()
        entry_aluno.focus_set()

        def salvar(event=None):
            nome = entry_aluno.get().strip()
            if not nome:
                messagebox.showerror("Erro", "O nome do aluno não pode ser vazio.")
                return

            conexao = sqlite3.connect("sistema_provas.db")
            cursor = conexao.cursor()
            cursor.execute("SELECT id FROM turmas WHERE nome = ?", (turma_atual,))
            turma_id = cursor.fetchone()[0]

            cursor.execute("INSERT INTO alunos (nome, turma_id) VALUES (?, ?)", (nome, turma_id))
            conexao.commit()
            conexao.close()

            janela_aluno.destroy()
            self.carregar_alunos_da_turma(turma_atual)
            self.combo_alunos.set(nome)
            self.verificar_botaonotas()
            self.carregar_provas_combobox()

        entry_aluno.bind("<Return>", salvar)
        tk.Button(janela_aluno, text="Salvar", command=salvar).pack(pady=15)

    def abrir_alterar_aluno(self):
        turma_atual = self.combo_turmas.get()
        aluno_atual = self.combo_alunos.get()

        if turma_atual in ["(SELECIONAR)", "(CRIAR NOVO)"] or not aluno_atual or aluno_atual in ["(SELECIONAR)", "(CRIAR NOVO)"]:
            messagebox.showwarning("Aviso", "Selecione um aluno válido para editar.")
            return

        janela_alt = tk.Toplevel(self.root)
        janela_alt.title("Editar Aluno")
        
        largura = 300
        altura = 150
        pos_x = (self.root.winfo_screenwidth() // 2) - (largura // 2)
        pos_y = (self.root.winfo_screenheight() // 2) - (altura // 2)
        janela_alt.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")

        tk.Label(janela_alt, text=f"Novo nome para o aluno:").pack(pady=10)
        entry_nome = tk.Entry(janela_alt, width=25)
        entry_nome.insert(0, aluno_atual)
        entry_nome.pack()
        entry_nome.focus_set()

        def salvar_alteracao(event=None):
            novo_nome = entry_nome.get().strip()
            if not novo_nome:
                messagebox.showerror("Erro", "O nome não pode estar vazio.")
                return

            conexao = sqlite3.connect("sistema_provas.db")
            cursor = conexao.cursor()
            cursor.execute("SELECT id FROM turmas WHERE nome = ?", (turma_atual,))
            t_res = cursor.fetchone()
            if not t_res:
                conexao.close()
                return
            turma_id = t_res[0]

            try:
                cursor.execute("""
                    UPDATE alunos SET nome = ? WHERE nome = ? AND turma_id = ?
                """, (novo_nome, aluno_atual, turma_id))
                conexao.commit()
                conexao.close()
                janela_alt.destroy()
                self.carregar_alunos_da_turma(turma_atual)
                self.combo_alunos.set(novo_nome)
                messagebox.showinfo("Sucesso", "Nome do aluno alterado com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", str(e))
                conexao.close()

        entry_nome.bind("<Return>", salvar_alteracao)
        tk.Button(janela_alt, text="Salvar Alteração", command=salvar_alteracao).pack(pady=15)

    def abrir_notas_turma(self):
        turma = self.combo_turmas.get()
        if turma in ["(SELECIONAR)", "(CRIAR NOVO)"]:
            return

        janela_nt = tk.Toplevel(self.root)
        janela_nt.title(f"Notas da Turma: {turma}")
        
        largura = 740
        altura = 450
        pos_x = (self.root.winfo_screenwidth() // 2) - (largura // 2)
        pos_y = (self.root.winfo_screenheight() // 2) - (altura // 2)
        janela_nt.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")

        tk.Label(janela_nt, text=f"Relatório de Notas - Turma {turma}", font=("Arial", 11, "bold")).pack(pady=10)

        frame_t = tk.Frame(janela_nt)
        frame_t.pack(fill="both", expand=True, padx=10, pady=5)

        cols = ("aluno", "prova", "disciplina", "tipo", "acertos_nota", "porcentagem")
        tree = ttk.Treeview(frame_t, columns=cols, show="headings", height=12)
        tree.heading("aluno", text="Aluno")
        tree.heading("prova", text="Avaliação")
        tree.heading("disciplina", text="Disciplina")
        tree.heading("tipo", text="Tipo")
        tree.heading("acertos_nota", text="Acertos / Nota")
        tree.heading("porcentagem", text="Desempenho (%)")
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame_t, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        
        scrollbar_h = ttk.Scrollbar(janela_nt, orient="horizontal", command=tree.xview)
        scrollbar_h.pack(side="bottom", fill="x", padx=10, pady=5)
        tree.configure(yscrollcommand=scrollbar.set, xscrollcommand=scrollbar_h.set)

        conexao = sqlite3.connect("sistema_provas.db")
        cursor = conexao.cursor()
        cursor.execute("SELECT id FROM turmas WHERE nome = ?", (turma,))
        t_res = cursor.fetchone()
        if not t_res:
            conexao.close()
            return
        turma_id = t_res[0]

        cursor.execute("""
            SELECT a.nome, p.nome, p.disciplina, p.tipo_avaliacao, r.acertos, r.porcentagem, r.respostas_aluno
            FROM resultados r
            JOIN alunos a ON r.aluno_id = a.id
            JOIN provas p ON r.prova_id = p.id
            WHERE a.turma_id = ?
        """, (turma_id,))

        for row in cursor.fetchall():
            aluno_nome, prova_nome, disc_sigla, tipo_av, acertos, porc, resp = row
            disc_completa = self.obter_nome_completo_disciplina(disc_sigla)
            if tipo_av == "TRABALHO":
                acertos_txt = resp
                porc_txt = f"{porc:.1f}%"
            else:
                acertos_txt = str(acertos)
                porc_txt = f"{porc:.2f}%"
            
            tree.insert("", "end", values=(aluno_nome, prova_nome, disc_completa, tipo_av, acertos_txt, porc_txt))

        conexao.close()

    def abrir_media_turma(self):
        turma = self.combo_turmas.get()
        if turma in ["(SELECIONAR)", "(CRIAR NOVO)"]:
            return

        janela_mt = tk.Toplevel(self.root)
        janela_mt.title(f"Média da Turma: {turma}")
        
        largura = 500
        altura = 400
        pos_x = (self.root.winfo_screenwidth() // 2) - (largura // 2)
        pos_y = (self.root.winfo_screenheight() // 2) - (altura // 2)
        janela_mt.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")

        tk.Label(janela_mt, text=f"Média de Notas por Aluno - Turma {turma}", font=("Arial", 11, "bold")).pack(pady=10)

        frame_t = tk.Frame(janela_mt)
        frame_t.pack(fill="both", expand=True, padx=10, pady=5)

        cols = ("aluno", "media")
        tree = ttk.Treeview(frame_t, columns=cols, show="headings", height=12)
        tree.heading("aluno", text="Nome do Aluno")
        tree.heading("media", text="Média Geral (%)")
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame_t, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        conexao = sqlite3.connect("sistema_provas.db")
        cursor = conexao.cursor()
        cursor.execute("SELECT id FROM turmas WHERE nome = ?", (turma,))
        t_res = cursor.fetchone()
        if not t_res:
            conexao.close()
            return
        turma_id = t_res[0]

        cursor.execute("""
            SELECT a.nome, AVG(r.porcentagem)
            FROM alunos a
            LEFT JOIN resultados r ON a.id = r.aluno_id
            WHERE a.turma_id = ?
            GROUP BY a.id, a.nome
        """, (turma_id,))

        for row in cursor.fetchall():
            aluno_nome, media_val = row
            media_txt = f"{media_val:.2f}%" if media_val is not None else "Sem notas"
            tree.insert("", "end", values=(aluno_nome, media_txt))

        conexao.close()

    def abrir_gerenciar_provas(self):
        turma_atual = self.combo_turmas.get()
        if turma_atual in ["(SELECIONAR)", "(CRIAR NOVO)"]:
            messagebox.showwarning("Aviso", "Selecione uma turma válida no painel superior antes de gerenciar provas.")
            return

        janela_provas = tk.Toplevel(self.root)
        janela_provas.title("Gerenciamento de Provas")
        
        largura = 720
        altura = 600
        pos_x = (self.root.winfo_screenwidth() // 2) - (largura // 2)
        pos_y = (self.root.winfo_screenheight() // 2) - (altura // 2)
        janela_provas.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")

        tk.Label(janela_provas, text=f"Provas Cadastradas ({turma_atual})", font=("Arial", 11, "bold")).pack(pady=5)
        
        frame_lista = tk.Frame(janela_provas)
        frame_lista.pack(fill="both", expand=True, padx=10, pady=5)

        colunas = ("codigo", "nome", "disciplina", "data")
        tree = ttk.Treeview(frame_lista, columns=colunas, show="headings", height=6)
        tree.heading("codigo", text="Código")
        tree.heading("nome", text="Nome da Prova")
        tree.heading("disciplina", text="Disciplina")
        tree.heading("data", text="Data")
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        
        scrollbar_h = ttk.Scrollbar(janela_provas, orient="horizontal", command=tree.xview)
        scrollbar_h.pack(side="bottom", fill="x", padx=10, pady=5)
        tree.configure(yscrollcommand=scrollbar.set, xscrollcommand=scrollbar_h.set)

        def atualizar_lista_tree():
            for i in tree.get_children():
                tree.delete(i)
            conexao = sqlite3.connect("sistema_provas.db")
            cursor = conexao.cursor()
            cursor.execute("SELECT codigo, nome, disciplina, data_prova FROM provas WHERE turma_nome = ? AND tipo_avaliacao = 'PROVA'", (turma_atual,))
            rows = cursor.fetchall()
            conexao.close()
            
            for row in rows:
                tree.insert("", "end", values=row)

            self.carregar_provas_combobox()

        atualizar_lista_tree()

        frame_form = tk.LabelFrame(janela_provas, text="Cadastrar ou Editar Prova", font=("Arial", 9, "bold"))
        frame_form.pack(fill="x", padx=10, pady=10)

        tk.Label(frame_form, text="Disciplina:").grid(row=0, column=0, sticky="w", padx=5, pady=3)
        
        conexao = sqlite3.connect("sistema_provas.db")
        cursor = conexao.cursor()
        cursor.execute("SELECT sigla, nome FROM disciplinas")
        disc_rows = cursor.fetchall()
        conexao.close()

        if not disc_rows:
            lista_disciplinas = ["(CRIAR NOVO)"]
        else:
            lista_disciplinas = ["(SELECIONAR)", "(CRIAR NOVO)"] + [f"{r[0]} - {r[1]}" for r in disc_rows]

        combo_disc = ttk.Combobox(frame_form, values=lista_disciplinas, state="readonly", width=22)
        combo_disc.grid(row=0, column=1, padx=5, pady=3)
        if lista_disciplinas:
            combo_disc.current(0)

        def verificar_nova_disciplina(event):
            if combo_disc.get() == "(CRIAR NOVO)":
                abrir_cadastro_disciplina()

        combo_disc.bind("<<ComboboxSelected>>", verificar_nova_disciplina)

        def abrir_cadastro_disciplina():
            j_disc = tk.Toplevel(janela_provas)
            j_disc.title("Nova Disciplina")
            j_disc.geometry("320x180")
            
            tk.Label(j_disc, text="Nome da Disciplina (Ex: Banco de Dados):").pack(pady=5)
            e_n_disc = tk.Entry(j_disc, width=30)
            e_n_disc.pack()
            e_n_disc.focus_set()

            tk.Label(j_disc, text="Sigla (3 letras ex: BDD):").pack(pady=5)
            e_s_disc = tk.Entry(j_disc, width=15)
            e_s_disc.pack()

            def salvar_disc():
                n_val = e_n_disc.get().strip()
                s_val = e_s_disc.get().strip().upper()
                if not n_val or not s_val:
                    messagebox.showerror("Erro", "Preencha todos os campos da disciplina.")
                    return

                conexao = sqlite3.connect("sistema_provas.db")
                cursor = conexao.cursor()
                try:
                    cursor.execute("INSERT INTO disciplinas (nome, sigla) VALUES (?, ?)", (n_val, s_val))
                    conexao.commit()
                    conexao.close()
                    j_disc.destroy()
                    
                    conexao = sqlite3.connect("sistema_provas.db")
                    cursor = conexao.cursor()
                    cursor.execute("SELECT sigla, nome FROM disciplinas")
                    novas_d = cursor.fetchall()
                    conexao.close()
                    
                    nova_lista = ["(SELECIONAR)", "(CRIAR NOVO)"] + [f"{r[0]} - {r[1]}" for r in novas_d]
                    combo_disc['values'] = nova_lista
                    combo_disc.set(f"{s_val} - {n_val}")
                except sqlite3.IntegrityError:
                    messagebox.showerror("Erro", "Essa sigla de disciplina já existe.")
                    conexao.close()

            tk.Button(j_disc, text="Salvar Disciplina", command=salvar_disc).pack(pady=10)

        tk.Label(frame_form, text="Nome da Prova:").grid(row=1, column=0, sticky="w", padx=5, pady=3)
        e_nome_prova = tk.Entry(frame_form, width=25)
        e_nome_prova.grid(row=1, column=1, padx=5, pady=3)

        tk.Label(frame_form, text="Qtd Questões:").grid(row=0, column=2, sticky="w", padx=5, pady=3)
        e_qtd = tk.Entry(frame_form, width=12)
        e_qtd.grid(row=0, column=3, sticky="w", padx=5, pady=3)

        tk.Label(frame_form, text="Data (DD/MM/AAAA):").grid(row=1, column=2, sticky="w", padx=5, pady=3)
        e_data = tk.Entry(frame_form, width=15)
        e_data.grid(row=1, column=3, sticky="w", padx=5, pady=3)

        def formatar_data(event):
            val = "".join([c for c in e_data.get() if c.isdigit()])
            if len(val) > 8:
                val = val[:8]
            formatado = ""
            if len(val) >= 2:
                formatado += val[:2] + "/"
                if len(val) >= 4:
                    formatado += val[2:4] + "/" + val[4:]
                else:
                    formatado += val[2:]
            else:
                formatado = val
            e_data.delete(0, tk.END)
            e_data.insert(0, formatado)

        e_data.bind("<KeyRelease>", formatar_data)

        tk.Label(frame_form, text="Raio Respostas:").grid(row=2, column=0, sticky="w", padx=5, pady=3)
        e_raio = tk.Entry(frame_form, width=15)
        e_raio.grid(row=2, column=1, sticky="w", padx=5, pady=3)
        e_raio.insert(0, "A-E")

        self.prova_em_edicao_codigo = None

        def carregar_dados_selecionados(event):
            selected_item = tree.selection()
            if not selected_item:
                return
            item_vals = tree.item(selected_item[0], "values")
            codigo_sel = item_vals[0]

            conexao = sqlite3.connect("sistema_provas.db")
            cursor = conexao.cursor()
            cursor.execute("SELECT nome, disciplina, qtd_questoes, data_prova, raio_respostas, gabarito FROM provas WHERE codigo = ?", (codigo_sel,))
            p_res = cursor.fetchone()
            conexao.close()

            if p_res:
                nome_p, disc_p, qtd_p, data_p, raio_p, gab_p = p_res
                self.prova_em_edicao_codigo = codigo_sel
                
                e_nome_prova.delete(0, tk.END)
                e_nome_prova.insert(0, nome_p)

                e_qtd.delete(0, tk.END)
                e_qtd.insert(0, str(qtd_p))

                e_data.delete(0, tk.END)
                e_data.insert(0, data_p)

                e_raio.delete(0, tk.END)
                e_raio.insert(0, raio_p)

                for val in combo_disc['values']:
                    if val.startswith(disc_p + " -") or val == disc_p:
                        combo_disc.set(val)
                        break

        tree.bind("<<TreeviewSelect>>", carregar_dados_selecionados)

        def abrir_configuracao_gabarito():
            disc_selecionada = combo_disc.get()
            if disc_selecionada in ["(SELECIONAR)", "(CRIAR NOVO)"] or not disc_selecionada:
                messagebox.showerror("Erro", "Selecione uma disciplina válida.")
                return

            d_cod = disc_selecionada.split(" - ")[0].strip()
            nome = e_nome_prova.get().strip()
            data = e_data.get().strip()
            raio = e_raio.get().strip().upper()
            
            try:
                qtd = int(e_qtd.get().strip())
            except ValueError:
                messagebox.showerror("Erro", "Quantidade de questões inválida.")
                return

            if not nome or not data or len(data) != 10:
                messagebox.showerror("Erro", "Preencha o nome e informe a data completa (DD/MM/AAAA).")
                return

            data_limpa = "".join([c for c in data if c.isdigit()])
            codigo_gerado = f"{turma_atual}{d_cod}{data_limpa}"

            conexao = sqlite3.connect("sistema_provas.db")
            cursor = conexao.cursor()
            gabarito_existente_str = None
            if self.prova_em_edicao_codigo:
                cursor.execute("SELECT gabarito FROM provas WHERE codigo = ?", (self.prova_em_edicao_codigo,))
                g_res = cursor.fetchone()
                if g_res:
                    gabarito_existente_str = g_res[0]
            conexao.close()

            janela_gab = tk.Toplevel(janela_provas)
            janela_gab.title(f"Definir Gabarito - {codigo_gerado}")
            
            larg_g = 420
            alt_g = 480
            px_g = (self.root.winfo_screenwidth() // 2) - (larg_g // 2)
            py_g = (self.root.winfo_screenheight() // 2) - (alt_g // 2)
            janela_gab.geometry(f"{larg_g}x{alt_g}+{px_g}+{py_g}")

            tk.Label(janela_gab, text=f"Raio Permitido: {raio}\nMúltiplas: AB ou ACDE", fg="blue", font=("Arial", 9, "bold")).pack(pady=5)

            canvas_g = tk.Canvas(janela_gab)
            scroll_g = ttk.Scrollbar(janela_gab, orient="vertical", command=canvas_g.yview)
            frame_g_in = ttk.Frame(canvas_g)

            frame_g_in.bind("<Configure>", lambda e: canvas_g.configure(scrollregion=canvas_g.bbox("all")))
            canvas_g.create_window((0, 0), window=frame_g_in, anchor="nw")
            canvas_g.configure(yscrollcommand=scroll_g.set)

            canvas_g.pack(side="top", fill="both", expand=True, padx=5, pady=5)
            scroll_g.pack(side="right", fill="y", pady=5)

            entradas_gab = []
            gabarito_antigo_lista = gabarito_existente_str.split(";") if gabarito_existente_str else []

            def validar_raio_geral(valor_digitado, raio_str):
                if "-" in raio_str:
                    partes = raio_str.split("-")
                    if len(partes) == 2:
                        inicio = partes[0].strip().upper()
                        fim = partes[1].strip().upper()
                        for char in valor_digitado:
                            if not (inicio <= char <= fim):
                                return False
                    return True
                return True

            for i in range(qtd):
                f_q = ttk.Frame(frame_g_in)
                f_q.pack(fill="x", pady=2)
                
                ttk.Label(f_q, text=f"Q{i+1}:", width=5).pack(side="left")
                e_resp = tk.Entry(f_q, width=15)
                e_resp.pack(side="left", padx=5)
                
                if i < len(gabarito_antigo_lista):
                    e_resp.insert(0, gabarito_antigo_lista[i])

                entradas_gab.append(e_resp)

                def upper_gab(e_w):
                    def callback(ev):
                        p = e_w.index(tk.INSERT)
                        t = e_w.get().upper()
                        e_w.delete(0, tk.END)
                        e_w.insert(0, t)
                        e_w.icursor(p)
                    return callback

                e_resp.bind("<KeyRelease>", upper_gab(e_resp))

            def salvar_no_banco():
                gabaritos_lista = []
                for idx, eg in enumerate(entradas_gab):
                    val = eg.get().strip().upper()
                    if not val:
                        messagebox.showerror("Erro", f"Preencha a resposta da questão {idx+1}")
                        return
                    
                    resp_norm = "".join(sorted([c for c in val if c.isalpha()]))
                    if not validar_raio_geral(resp_norm, raio):
                        messagebox.showerror("Erro", f"Questão {idx+1}: A resposta '{val}' contém caracteres fora do raio permitido ({raio}).")
                        return

                    gabaritos_lista.append(resp_norm)

                gabarito_str = ";".join(gabaritos_lista)

                conexao = sqlite3.connect("sistema_provas.db")
                cursor = conexao.cursor()
                try:
                    if self.prova_em_edicao_codigo and self.prova_em_edicao_codigo != codigo_gerado:
                        cursor.execute("DELETE FROM provas WHERE codigo = ?", (self.prova_em_edicao_codigo,))

                    cursor.execute("""
                        INSERT OR REPLACE INTO provas (codigo, nome, disciplina, qtd_questoes, data_prova, raio_respostas, gabarito, tipo_avaliacao, turma_nome)
                        VALUES (?, ?, ?, ?, ?, ?, ?, 'PROVA', ?)
                    """, (codigo_gerado, nome, d_cod, qtd, data, raio, gabarito_str, turma_atual))
                    conexao.commit()
                    conexao.close()
                    messagebox.showinfo("Sucesso", "Prova salva com sucesso!")
                    self.prova_em_edicao_codigo = None
                    janela_gab.destroy()
                    janela_provas.destroy()
                    self.carregar_provas_combobox()
                except Exception as e:
                    messagebox.showerror("Erro ao salvar", str(e))
                    conexao.close()

            tk.Button(janela_gab, text="Confirmar e Salvar Prova", command=salvar_no_banco, bg="#d4edda", font=("Arial", 10, "bold")).pack(pady=10)

        tk.Button(frame_form, text="Salvar / Atualizar Prova (Gabarito)", command=abrir_configuracao_gabarito, bg="#cce5ff").grid(row=3, column=0, columnspan=4, pady=8, sticky="ew", padx=5)

        self.carregar_provas_combobox()

    def abrir_gerenciar_trabalhos(self):
        turma_atual = self.combo_turmas.get()
        if turma_atual in ["(SELECIONAR)", "(CRIAR NOVO)"]:
            messagebox.showwarning("Aviso", "Selecione uma turma válida no painel superior antes de gerenciar trabalhos.")
            return

        janela_trab = tk.Toplevel(self.root)
        janela_trab.title("Gerenciamento de Trabalhos")
        
        largura = 720
        altura = 560
        pos_x = (self.root.winfo_screenwidth() // 2) - (largura // 2)
        pos_y = (self.root.winfo_screenheight() // 2) - (altura // 2)
        janela_trab.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")

        tk.Label(janela_trab, text=f"Trabalhos Cadastrados ({turma_atual})", font=("Arial", 11, "bold")).pack(pady=5)
        
        frame_lista = tk.Frame(janela_trab)
        frame_lista.pack(fill="both", expand=True, padx=10, pady=5)

        colunas = ("codigo", "nome", "disciplina", "data")
        tree = ttk.Treeview(frame_lista, columns=colunas, show="headings", height=6)
        tree.heading("codigo", text="Código")
        tree.heading("nome", text="Nome do Trabalho")
        tree.heading("disciplina", text="Disciplina")
        tree.heading("data", text="Data")
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        
        scrollbar_h = ttk.Scrollbar(janela_trab, orient="horizontal", command=tree.xview)
        scrollbar_h.pack(side="bottom", fill="x", padx=10, pady=5)
        tree.configure(yscrollcommand=scrollbar.set, xscrollcommand=scrollbar_h.set)

        def atualizar_lista_tree():
            for i in tree.get_children():
                tree.delete(i)
            conexao = sqlite3.connect("sistema_provas.db")
            cursor = conexao.cursor()
            cursor.execute("SELECT codigo, nome, disciplina, data_prova FROM provas WHERE turma_nome = ? AND tipo_avaliacao = 'TRABALHO'", (turma_atual,))
            rows = cursor.fetchall()
            conexao.close()
            
            for row in rows:
                tree.insert("", "end", values=row)

            self.carregar_provas_combobox()

        atualizar_lista_tree()

        frame_form = tk.LabelFrame(janela_trab, text="Cadastrar ou Editar Trabalho", font=("Arial", 9, "bold"))
        frame_form.pack(fill="x", padx=10, pady=10)

        tk.Label(frame_form, text="Disciplina:").grid(row=0, column=0, sticky="w", padx=5, pady=3)
        
        conexao = sqlite3.connect("sistema_provas.db")
        cursor = conexao.cursor()
        cursor.execute("SELECT sigla, nome FROM disciplinas")
        disc_rows = cursor.fetchall()
        conexao.close()

        if not disc_rows:
            lista_disciplinas = ["(CRIAR NOVO)"]
        else:
            lista_disciplinas = ["(SELECIONAR)", "(CRIAR NOVO)"] + [f"{r[0]} - {r[1]}" for r in disc_rows]

        combo_disc = ttk.Combobox(frame_form, values=lista_disciplinas, state="readonly", width=22)
        combo_disc.grid(row=0, column=1, padx=5, pady=3)
        if lista_disciplinas:
            combo_disc.current(0)

        def verificar_nova_disciplina(event):
            if combo_disc.get() == "(CRIAR NOVO)":
                abrir_cadastro_disciplina()

        combo_disc.bind("<<ComboboxSelected>>", verificar_nova_disciplina)

        def abrir_cadastro_disciplina():
            j_disc = tk.Toplevel(janela_trab)
            j_disc.title("Nova Disciplina")
            j_disc.geometry("320x180")
            
            tk.Label(j_disc, text="Nome da Disciplina (Ex: Banco de Dados):").pack(pady=5)
            e_n_disc = tk.Entry(j_disc, width=30)
            e_n_disc.pack()
            e_n_disc.focus_set()

            tk.Label(j_disc, text="Sigla (3 letras ex: BDD):").pack(pady=5)
            e_s_disc = tk.Entry(j_disc, width=15)
            e_s_disc.pack()

            def salvar_disc():
                n_val = e_n_disc.get().strip()
                s_val = e_s_disc.get().strip().upper()
                if not n_val or not s_val:
                    messagebox.showerror("Erro", "Preencha todos os campos da disciplina.")
                    return

                conexao = sqlite3.connect("sistema_provas.db")
                cursor = conexao.cursor()
                try:
                    cursor.execute("INSERT INTO disciplinas (nome, sigla) VALUES (?, ?)", (n_val, s_val))
                    conexao.commit()
                    conexao.close()
                    j_disc.destroy()
                    
                    conexao = sqlite3.connect("sistema_provas.db")
                    cursor = conexao.cursor()
                    cursor.execute("SELECT sigla, nome FROM disciplinas")
                    novas_d = cursor.fetchall()
                    conexao.close()
                    
                    nova_lista = ["(SELECIONAR)", "(CRIAR NOVO)"] + [f"{r[0]} - {r[1]}" for r in novas_d]
                    combo_disc['values'] = nova_lista
                    combo_disc.set(f"{s_val} - {n_val}")
                except sqlite3.IntegrityError:
                    messagebox.showerror("Erro", "Essa sigla de disciplina já existe.")
                    conexao.close()

            tk.Button(j_disc, text="Salvar Disciplina", command=salvar_disc).pack(pady=10)

        tk.Label(frame_form, text="Nome do Trabalho:").grid(row=1, column=0, sticky="w", padx=5, pady=3)
        e_nome_trab = tk.Entry(frame_form, width=25)
        e_nome_trab.grid(row=1, column=1, padx=5, pady=3)

        tk.Label(frame_form, text="Data (DD/MM/AAAA):").grid(row=1, column=2, sticky="w", padx=5, pady=3)
        e_data = tk.Entry(frame_form, width=15)
        e_data.grid(row=1, column=3, sticky="w", padx=5, pady=3)

        def formatar_data(event):
            val = "".join([c for c in e_data.get() if c.isdigit()])
            if len(val) > 8:
                val = val[:8]
            formatado = ""
            if len(val) >= 2:
                formatado += val[:2] + "/"
                if len(val) >= 4:
                    formatado += val[2:4] + "/" + val[4:]
                else:
                    formatado += val[2:]
            else:
                formatado = val
            e_data.delete(0, tk.END)
            e_data.insert(0, formatado)

        e_data.bind("<KeyRelease>", formatar_data)

        self.trabalho_em_edicao_codigo = None

        def carregar_dados_trabalho(event):
            selected_item = tree.selection()
            if not selected_item:
                return
            item_vals = tree.item(selected_item[0], "values")
            codigo_sel = item_vals[0]

            conexao = sqlite3.connect("sistema_provas.db")
            cursor = conexao.cursor()
            cursor.execute("SELECT nome, disciplina, data_prova FROM provas WHERE codigo = ?", (codigo_sel,))
            t_res = cursor.fetchone()
            conexao.close()

            if t_res:
                nome_t, disc_t, data_t = t_res
                self.trabalho_em_edicao_codigo = codigo_sel

                e_nome_trab.delete(0, tk.END)
                e_nome_trab.insert(0, nome_t)

                e_data.delete(0, tk.END)
                e_data.insert(0, data_t)

                for val in combo_disc['values']:
                    if val.startswith(disc_t + " -") or val == disc_t:
                        combo_disc.set(val)
                        break

        tree.bind("<<TreeviewSelect>>", carregar_dados_trabalho)

        def salvar_trabalho():
            disc_selecionada = combo_disc.get()
            if disc_selecionada in ["(SELECIONAR)", "(CRIAR NOVO)"] or not disc_selecionada:
                messagebox.showerror("Erro", "Selecione uma disciplina válida.")
                return

            d_cod = disc_selecionada.split(" - ")[0].strip()
            nome = e_nome_trab.get().strip()
            data = e_data.get().strip()

            if not nome or not data or len(data) != 10:
                messagebox.showerror("Erro", "Preencha o nome do trabalho e informe a data completa (DD/MM/AAAA).")
                return

            data_limpa = "".join([c for c in data if c.isdigit()])
            codigo_gerado = f"{turma_atual}{d_cod}{data_limpa}"

            conexao = sqlite3.connect("sistema_provas.db")
            cursor = conexao.cursor()
            try:
                if self.trabalho_em_edicao_codigo and self.trabalho_em_edicao_codigo != codigo_gerado:
                    cursor.execute("DELETE FROM provas WHERE codigo = ?", (self.trabalho_em_edicao_codigo,))

                cursor.execute("""
                    INSERT OR REPLACE INTO provas (codigo, nome, disciplina, qtd_questoes, data_prova, raio_respostas, gabarito, tipo_avaliacao, turma_nome)
                    VALUES (?, ?, ?, 1, ?, 'NOTA', 'NOTA', 'TRABALHO', ?)
                """, (codigo_gerado, nome, d_cod, data, turma_atual))
                conexao.commit()
                conexao.close()
                messagebox.showinfo("Sucesso", "Trabalho salvo com sucesso!")
                self.trabalho_em_edicao_codigo = None
                janela_trab.destroy()
                self.carregar_provas_combobox()
            except Exception as e:
                messagebox.showerror("Erro ao salvar", str(e))
                conexao.close()

        tk.Button(frame_form, text="Salvar / Atualizar Trabalho", command=salvar_trabalho, bg="#fff3cd").grid(row=2, column=0, columnspan=4, pady=8, sticky="ew", padx=5)

        self.carregar_provas_combobox()

    def carregar_provas_combobox(self):
        turma_atual = self.combo_turmas.get()
        if turma_atual in ["(SELECIONAR)", "(CRIAR NOVO)"]:
            self.combo_provas['values'] = []
            self.combo_provas.set('')
            return

        conexao = sqlite3.connect("sistema_provas.db")
        cursor = conexao.cursor()
        cursor.execute("SELECT codigo, nome, tipo_avaliacao FROM provas WHERE turma_nome = ?", (turma_atual,))
        linhas = cursor.fetchall()
        conexao.close()

        if not linhas:
            self.combo_provas['values'] = ["(CRIAR NOVA PROVA)", "(CRIAR NOVO TRABALHO)"]
            self.combo_provas.current(0)
        else:
            provas = ["(SELECIONAR)"] + [f"{row[0]} - {row[1]} ({row[2]})" for row in linhas]
            self.combo_provas['values'] = provas
            self.combo_provas.current(0)

    def carregar_interface_respostas(self, event):
        selecao = self.combo_provas.get()
        if not selecao:
            for widget in self.frame_respostas.winfo_children():
                widget.destroy()
            self.btn_salvar_correcao.config(state="disabled")
            return

        if selecao == "(CRIAR NOVA PROVA)":
            self.combo_provas.set("(SELECIONAR)")
            for widget in self.frame_respostas.winfo_children():
                widget.destroy()
            self.btn_salvar_correcao.config(state="disabled")
            self.abrir_gerenciar_provas()
            return
        elif selecao == "(CRIAR NOVO TRABALHO)":
            self.combo_provas.set("(SELECIONAR)")
            for widget in self.frame_respostas.winfo_children():
                widget.destroy()
            self.btn_salvar_correcao.config(state="disabled")
            self.abrir_gerenciar_trabalhos()
            return
        elif selecao == "(SELECIONAR)":
            for widget in self.frame_respostas.winfo_children():
                widget.destroy()
            self.btn_salvar_correcao.config(state="disabled")
            return

        codigo_prova = selecao.split(" - ")[0]

        conexao = sqlite3.connect("sistema_provas.db")
        cursor = conexao.cursor()
        cursor.execute("SELECT qtd_questoes, tipo_avaliacao, raio_respostas, gabarito FROM provas WHERE codigo = ?", (codigo_prova,))
        res = cursor.fetchone()
        conexao.close()

        if not res:
            return

        qtd, tipo, raio, gabarito_str = res

        for widget in self.frame_respostas.winfo_children():
            widget.destroy()

        self.entradas_aluno = []
        self.txt_comentario = None

        if tipo == "TRABALHO":
            f = ttk.Frame(self.frame_respostas)
            f.pack(fill="x", pady=5)
            tk.Label(f, text="Nota Atribuída (0 a 10):", width=25, anchor="w").pack(side="left")
            e = tk.Entry(f, width=15)
            e.pack(side="left", padx=5)
            self.entradas_aluno.append(e)

            f_c = ttk.Frame(self.frame_respostas)
            f_c.pack(fill="both", expand=True, pady=5)
            tk.Label(f_c, text="Comentário (máx 600 caracteres):", anchor="w").pack(anchor="w")
            
            self.txt_comentario = tk.Text(f_c, height=6, width=60)
            self.txt_comentario.pack(fill="both", expand=True, pady=2)

            def limitar_comentario(event):
                conteudo = self.txt_comentario.get("1.0", tk.END)
                if len(conteudo) > 601:
                    self.txt_comentario.delete("1.0 + 600 chars", tk.END)

            self.txt_comentario.bind("<KeyRelease>", limitar_comentario)

        else:
            lbl_raio = tk.Label(self.frame_respostas, text=f"Raio de respostas: {raio}", font=("Arial", 9, "bold"), fg="#333333")
            lbl_raio.pack(anchor="w", pady=(2, 6))

            gabarito_lista = gabarito_str.split(";")

            for i in range(qtd):
                f = ttk.Frame(self.frame_respostas)
                f.pack(fill="x", pady=3)

                tk.Label(f, text=f"Questão {i+1}:", width=12, anchor="w").pack(side="left")
                
                e = tk.Entry(f, width=15)
                e.pack(side="left", padx=5)
                self.entradas_aluno.append(e)

                gab_q = gabarito_lista[i] if i < len(gabarito_lista) else "A"
                qtd_opcoes = len(self.normalizar_resposta(gab_q))
                if qtd_opcoes > 1:
                    tk.Label(f, text=f"({qtd_opcoes} opções)", fg="blue", font=("Arial", 8, "italic")).pack(side="left", padx=5)

                def upper_aluno(e_w, idx_atual, max_chars):
                    def callback(ev):
                        if ev.keysym in ("Return", "Tab"):
                            if idx_atual < len(self.entradas_aluno) - 1:
                                self.entradas_aluno[idx_atual + 1].focus()
                            return "break"

                        p = e_w.index(tk.INSERT)
                        t = e_w.get().upper()
                        e_w.delete(0, tk.END)
                        e_w.insert(0, t)
                        e_w.icursor(p)

                        if len(t) >= max_chars and idx_atual < len(self.entradas_aluno) - 1:
                            self.entradas_aluno[idx_atual + 1].focus()
                    return callback

                e.bind("<KeyRelease>", upper_aluno(e, i, qtd_opcoes))
                e.bind("<Return>", lambda e, idx=i: self.ir_para_proximo(idx))
                e.bind("<Tab>", lambda e, idx=i: self.ir_para_proximo(idx))

        self.btn_salvar_correcao.config(state="normal")

    def ir_para_proximo(self, idx):
        if idx < len(self.entradas_aluno) - 1:
            self.entradas_aluno[idx + 1].focus()
        return "break"

    def normalizar_resposta(self, texto):
        limpo = "".join(sorted([c.upper() for c in texto if c.isalpha()]))
        return limpo

    def validar_raio(self, valor_digitado, raio_str):
        if "-" in raio_str:
            partes = raio_str.split("-")
            if len(partes) == 2:
                inicio = partes[0].strip().upper()
                fim = partes[1].strip().upper()
                for char in valor_digitado:
                    if not (inicio <= char <= fim):
                        return False
            return True
        return True

    def salvar_correcao_aluno(self):
        turma = self.combo_turmas.get()
        aluno = self.combo_alunos.get()
        prova_sel = self.combo_provas.get()

        if turma in ["(SELECIONAR)", "(CRIAR NOVO)"] or aluno in ["(SELECIONAR)", "(CRIAR NOVO)"] or not prova_sel or prova_sel in ["(SELECIONAR)", "(CRIAR NOVA PROVA)", "(CRIAR NOVO TRABALHO)"]:
            messagebox.showerror("Erro", "Selecione uma turma válida, um aluno válido e uma avaliação.")
            return

        codigo_prova = prova_sel.split(" - ")[0]

        conexao = sqlite3.connect("sistema_provas.db")
        cursor = conexao.cursor()

        cursor.execute("SELECT id FROM turmas WHERE nome = ?", (turma,))
        turma_id = cursor.fetchone()[0]

        cursor.execute("SELECT id FROM alunos WHERE nome = ? AND turma_id = ?", (aluno, turma_id))
        aluno_id = cursor.fetchone()[0]

        cursor.execute("SELECT id, gabarito, qtd_questoes, tipo_avaliacao, raio_respostas FROM provas WHERE codigo = ?", (codigo_prova,))
        prova_res = cursor.fetchone()
        prova_id, gabarito_str, qtd, tipo_av, raio_respostas = prova_res[0], prova_res[1], prova_res[2], prova_res[3], prova_res[4]

        if tipo_av == "TRABALHO":
            val_nota = self.entradas_aluno[0].get().strip().replace(",", ".")

            if not val_nota:
                messagebox.showerror("Erro", "Insira a nota do trabalho.")
                conexao.close()
                return

            try:
                nota_val = float(val_nota)
            except ValueError:
                messagebox.showerror("Erro", "A nota deve ser um número válido.")
                conexao.close()
                return

            if not (0.0 <= nota_val <= 10.0):
                messagebox.showerror("Erro", "A nota do trabalho deve estar entre 0 e 10.")
                conexao.close()
                return

            comentario = self.txt_comentario.get("1.0", tk.END).strip()
            porcentagem_trab = (nota_val / 10.0) * 100.0

            cursor.execute("""
                INSERT INTO resultados (aluno_id, prova_id, acertos, erros, porcentagem, respostas_aluno, comentario)
                VALUES (?, ?, ?, 0, ?, ?, ?)
            """, (aluno_id, prova_id, int(nota_val), porcentagem_trab, str(nota_val), comentario))

            conexao.commit()
            conexao.close()

            messagebox.showinfo("Sucesso", f"Trabalho registrado com nota {nota_val}!")
            for widget in self.frame_respostas.winfo_children():
                widget.destroy()
            self.combo_provas.set("(SELECIONAR)")
            self.btn_salvar_correcao.config(state="disabled")
            self.verificar_botaonotas()

        else:
            gabarito_oficial = gabarito_str.split(";")
            respostas_aluno = []

            for idx, entry in enumerate(self.entradas_aluno):
                val = entry.get().strip()
                if not val:
                    messagebox.showerror("Erro", f"A resposta da questão {idx+1} está vazia.")
                    conexao.close()
                    return
                
                resp_norm = self.normalizar_resposta(val)
                if not self.validar_raio(resp_norm, raio_respostas):
                    messagebox.showerror("Erro", f"Questão {idx+1}: A resposta '{val}' está fora do raio permitido ({raio_respostas}).")
                    conexao.close()
                    return

                respostas_aluno.append(resp_norm)

            acertos = 0
            for g, r in zip(gabarito_oficial, respostas_aluno):
                g_norm = self.normalizar_resposta(g)
                if g_norm == r:
                    acertos += 1

            erros = qtd - acertos
            porcentagem = (acertos / qtd) * 100 if qtd > 0 else 0
            resp_aluno_str = ";".join(respostas_aluno)

            cursor.execute("""
                INSERT INTO resultados (aluno_id, prova_id, acertos, erros, porcentagem, respostas_aluno, comentario)
                VALUES (?, ?, ?, ?, ?, ?, NULL)
            """, (aluno_id, prova_id, acertos, erros, porcentagem, resp_aluno_str))

            conexao.commit()
            conexao.close()

            messagebox.showinfo("Resultado", f"Correção concluída!\nAcertos: {acertos}\nErros: {erros}\nPorcentagem: {porcentagem:.2f}%")
            for widget in self.frame_respostas.winfo_children():
                widget.destroy()
            self.combo_provas.set("(SELECIONAR)")
            self.btn_salvar_correcao.config(state="disabled")
            self.verificar_botaonotas()

    def verificar_botaonotas(self):
        aluno = self.combo_alunos.get()
        turma = self.combo_turmas.get()
        if not aluno or aluno in ["(SELECIONAR)", "(CRIAR NOVO)"] or turma in ["(SELECIONAR)", "(CRIAR NOVO)"]:
            self.btn_visualizar_notas.config(state="disabled")
            self.btn_editar_aluno.config(state="disabled")
            return

        conexao = sqlite3.connect("sistema_provas.db")
        cursor = conexao.cursor()
        cursor.execute("SELECT id FROM turmas WHERE nome = ?", (turma,))
        t_res = cursor.fetchone()
        if not t_res:
            conexao.close()
            self.btn_visualizar_notas.config(state="disabled")
            self.btn_editar_aluno.config(state="disabled")
            return

        cursor.execute("SELECT id FROM alunos WHERE nome = ? AND turma_id = ?", (aluno, t_res[0]))
        a_res = cursor.fetchone()
        if not a_res:
            conexao.close()
            self.btn_visualizar_notas.config(state="disabled")
            self.btn_editar_aluno.config(state="disabled")
            return

        self.btn_editar_aluno.config(state="normal")

        cursor.execute("SELECT COUNT(*) FROM resultados WHERE aluno_id = ?", (a_res[0],))
        total_notas = cursor.fetchone()[0]
        conexao.close()

        if total_notas > 0:
            self.btn_visualizar_notas.config(state="normal")
        else:
            self.btn_visualizar_notas.config(state="disabled")

    def abrir_visualizar_notas(self):
        aluno = self.combo_alunos.get()
        turma = self.combo_turmas.get()

        janela_notas = tk.Toplevel(self.root)
        janela_notas.title(f"Notas do Aluno: {aluno}")
        
        largura = 740
        altura = 420
        pos_x = (self.root.winfo_screenwidth() // 2) - (largura // 2)
        pos_y = (self.root.winfo_screenheight() // 2) - (altura // 2)
        janela_notas.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")

        tk.Label(janela_notas, text=f"Histórico de Avaliações de {aluno} ({turma})", font=("Arial", 11, "bold")).pack(pady=10)

        frame_t = tk.Frame(janela_notas)
        frame_t.pack(fill="both", expand=True, padx=10, pady=5)

        cols = ("prova", "disciplina", "tipo", "acertos", "porcentagem", "comentario")
        tree = ttk.Treeview(frame_t, columns=cols, show="headings", height=10)
        tree.heading("prova", text="Nome")
        tree.heading("disciplina", text="Disciplina")
        tree.heading("tipo", text="Tipo")
        tree.heading("acertos", text="Acertos / Nota")
        tree.heading("porcentagem", text="Desempenho (%)")
        tree.heading("comentario", text="Comentário")
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame_t, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        
        scrollbar_h = ttk.Scrollbar(janela_notas, orient="horizontal", command=tree.xview)
        scrollbar_h.pack(side="bottom", fill="x", padx=10, pady=5)
        tree.configure(yscrollcommand=scrollbar.set, xscrollcommand=scrollbar_h.set)

        conexao = sqlite3.connect("sistema_provas.db")
        cursor = conexao.cursor()
        cursor.execute("SELECT id FROM turmas WHERE nome = ?", (turma,))
        t_id = cursor.fetchone()[0]
        cursor.execute("SELECT id FROM alunos WHERE nome = ? AND turma_id = ?", (aluno, t_id))
        a_id = cursor.fetchone()[0]

        cursor.execute("""
            SELECT p.nome, p.disciplina, p.tipo_avaliacao, r.acertos, r.porcentagem, r.comentario, r.respostas_aluno
            FROM resultados r
            JOIN provas p ON r.prova_id = p.id
            WHERE r.aluno_id = ?
        """, (a_id,))

        for row in cursor.fetchall():
            nome_av, disc_sigla, tipo_av, acertos, porc, comentario, resp = row
            disc_completa = self.obter_nome_completo_disciplina(disc_sigla)
            if tipo_av == "TRABALHO":
                acertos_txt = resp
                porc_txt = f"{porc:.1f}%"
            else:
                acertos_txt = str(acertos)
                porc_txt = f"{porc:.2f}%"
            
            comentario_txt = comentario if comentario else "-"
            tree.insert("", "end", values=(nome_av, disc_completa, tipo_av, acertos_txt, porc_txt, comentario_txt))

        conexao.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = SistemaProvasApp(root)
    root.mainloop()