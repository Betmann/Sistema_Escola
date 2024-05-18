# importa o modulo http.server
import os
from http.server import SimpleHTTPRequestHandler
import socketserver
from urllib.parse import parse_qs , urlparse

class MyHandler(SimpleHTTPRequestHandler):
    def list_directory(self, path):
        try:
            # tenta abrir o arquivo
            f = open(os.path.join(path, "login.html"), "r")
            # se existir, envia o conteudo do arquivo
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(f.read().encode("utf-8"))
            f.close()
            return None
        except FileNotFoundError:
            pass
        return super().list_directory(path)

    def do_GET(self):
        if self.path == "/login":
            try:
                with open(os.path.join(os.getcwd(), "index.html"), "r") as login_file:
                    content = login_file.read()
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(content.encode("utf-8"))
            except FileNotFoundError:
                self.send_error(404, "File not found")

        elif self.path == '/login_failed':
            self.send_response(200) 
            self.send_header("Content-type", "text/html; charset=8")
            self.end_headers()
            # le o conteudo da pagina login.html
            with open(os.path.join(os.getcwd(), 'login.html'), 'r', encoding='utf-8') as login_file:
                content = login_file.read()
            mensagem = "Login e/ou senha incorreta... tenta novamente." 
            content = content.replace('<!-- Mensagem de erro sera inserida aqui -->',
                                       f'<div class="error-message">{mensagem}</div>')
            self.wfile.write(content.encode('utf-8')) 

        elif self.path.startswith('/cadastro'):

            query_params = parse_qs(urlparse(self.path).query)
            login = query_params.get('login', [''])[0]
            senha = query_params.get('senha', [''])[0]
            welcome_message = f"Hola {login}, seja bem vindo!! Percebemos que voce é novo por aqui.."

            self.send_response(200)
            self.send_header("Content-type", "text/html ; charset=utf-8")
            self.end_headers()

            with open(os.path.join(os.getcwd(), 'cadastro.html'), 'r' , encoding='utf') as cadastro_file:
               content = cadastro_file.read()

            content = content.replace('{login}', login)
            content = content.replace('{senha}', senha)
            content = content.replace('{welcome_message}', welcome_message)

            self.wfile.write(content.encode('utf-8'))

            return
        else:
             super().do_GET()

    def usuario_existente(self, login, senha):
        #verificar se o login já existe no arquivo
        with open('dados.txt', 'r', encoding='utf-8') as file:
            for line in file:
                if line.strip():
                   stored_login, stored_senha, stored_nome = line.strip().split(';')
                   if login == stored_login:
                      print("Cheguei aqui significando que localizei o login informando")
                      print("Senha:" + senha)
                      print("senha_armazenada:" + senha )
                      return senha == stored_senha
        return False  
    
    def remover_ultima_linha(self, arquivo): 
        print("Vou excluir ultima linha")
        with open(arquivo, 'r' , encoding='utf-8') as file:
            lines = file.readlines()
        with open(arquivo, 'w' , encoding='utf-8') as file:
            file.writelines(lines[:-1])
            
    
    def do_POST(self):
        if self.path == "/enviar_login":
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode('utf-8')

            # parseia os dados ao formulario
            form_data = parse_qs(body, keep_blank_values=True)

            # exibe os dados no terminal
            print("Dados do formulario:")
            print("Email:", form_data.get("email", [""])[0])
            print("Senha:", form_data.get("senha", [""])[0])

            #verificar se o usuario ja existe
            login = form_data.get('email', [''])[0]
            senha = form_data.get('senha', [''])[0]

            if self.usuario_existente(login, senha):
                #responde ao cliente indicando que o usuario ja consta nos registro
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                mensagem = f"Usuário {login} logado com sucesso!!!"
                self.wfile.write(mensagem.encode('utf-8'))

            else:
                
                if any(line.startswith(f"{login};") for line in 
                       open('dados.txt', 'r', encoding='utf-8')):
                    self.send_response(302)
                    self.send_header('Location' , '/login_falied')
                    self.end_headers()
                    return
                
                else:
                    with open('dados.txt', 'a', encoding='utf-8') as file:
                        file.write(f"{login};{senha};" + "none" + "\n")

                    self.send_response(302)
                    self.send_header('Location', f'/cadastro?login = {login}&senha={senha}')
                    self.end_headers()
                    return
                    
        elif self.path.startswith('/confirmar_cadastro'):
             content_length = int(self.headers['Content-Length'])
             body = self.rfile.read(content_length).decode('utf-8')
             form_data = parse_qs(body, keep_blank_values=True) 

             login = form_data.get('login', [''])[0]
             senha = form_data.get('senha' , [''])[0]
             nome = form_data.get('nome',[''])[0]
             print ("nome:" + nome)

             if self.usuario_existente(login, senha):
                 
                 with open('dados.txt', 'r', encoding='utf-8') as file:
                      lines = file.readlines()
                 with open('dados.txt', 'w', encoding='utf-8') as file: 
                        
                      for line in lines:
                          stored_login, stored_senha, stored_nome = line.strip().split(';') 
                          if login == stored_login and senha == stored_senha:
                              line = f"{login};{senha};{nome}\n"
                          file.write(line)   

                 self.send_response(302)
                 self.send_header("Content-type", "text/html; charset=utf-8")
                 self.end_headers() 
                 self.wfile.write("Registro Recebido com sucesso !!!!!" .encode("utf-8"))
                             
             else:
            
                 self.remover_ultima_linha('dados.txt')
                 self.send_response(302)
                 self.send_header("Content-type", "text/html; chartset-8")
                 self.end_headers()
                 self.wfile.write("A senha não confere. Retome o procedimentos" .encode('utf-8'))
        else:
            # se nao for a rota "/submit_login", continua como comportamento
            super(MyHandler, self).do_POST()

# define a porta a ser utilizada
enderoco_ip = "0.0.0.0"
porta = 8000


# cria um servidor na porta especificada
with socketserver.TCPServer((enderoco_ip, porta), MyHandler) as httpd:  # " "aceita qualquer requisicao de rede
    print(f"Servidor iniciado na porta {porta}")
    # mantem o servidor em execução
    httpd.serve_forever()