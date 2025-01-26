from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from werkzeug.utils import secure_filename
import pandas as pd
from deepseek_api import analyze_data
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'bat_analytics_secret_key')

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'csv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('upload'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == '1234' and password == '1234':
            session['logged_in'] = True
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('upload'))
        else:
            flash('Credenciais inválidas!', 'error')
    
    return render_template('login.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Nenhum arquivo selecionado', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('Nenhum arquivo selecionado', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                # Verificar se o arquivo pode ser lido como Excel ou CSV
                if filename.endswith('.xlsx'):
                    pd.read_excel(file, nrows=1)  # Tenta ler primeira linha
                elif filename.endswith('.csv'):
                    pd.read_csv(file, nrows=1)  # Tenta ler primeira linha
                
                # Se chegou aqui, o arquivo é válido
                file.seek(0)  # Volta ao início do arquivo
                file.save(filepath)
                flash(f'Arquivo {filename} enviado com sucesso!', 'success')
                
                try:
                    # Analyze the file using Deepseek API
                    diagnostic = analyze_data(filepath)
                    return render_template('results.html', diagnostic=diagnostic)
                except Exception as e:
                    flash(f'Arquivo enviado, mas houve um erro na análise: {str(e)}', 'error')
                    return redirect(request.url)
                
            except Exception as e:
                flash(f'Erro ao processar o arquivo. Verifique se o formato está correto: {str(e)}', 'error')
                return redirect(request.url)
            
        else:
            flash('Formato de arquivo não permitido. Use apenas .xlsx ou .csv', 'error')
            return redirect(request.url)

    return render_template('upload.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
