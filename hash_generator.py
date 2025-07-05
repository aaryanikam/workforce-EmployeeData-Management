import streamlit_authenticator as stauth

passwords = ["12345"]  # 🔐 Replace this with your real password
hashed_passwords = stauth.Hasher(passwords).generate()
print(hashed_passwords)
