import instaloader

L = instaloader.Instaloader()

L.login("seu_user", "sua_senha")
L.save_session_to_file()

print("Login realizado e sessão salva!")