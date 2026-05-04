from flask import Flask, render_template, request, send_file
import sqlite3
import os
from docxtpl import DocxTemplate
from io import BytesIO

app = Flask(__name__)

# mapping template (lebih aman pakai os.path.join)
TEMPLATES = {
    "Aktif Kuliah": os.path.join("templates_surat", "aktif_kuliah.docx"),
    "Lab Penelitian": os.path.join("templates_surat", "lab_penelitian.docx"),
    "Ethical Clearance": os.path.join("templates_surat", "ethical.docx"),
    "Identifikasi Tumbuhan": os.path.join("templates_surat", "tumbuhan.docx")
}

DB = "database.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS pengajuan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT,
            ttl TEXT,
            jk TEXT,
            npm TEXT,
            nim TEXT,
            sem TEXT,
            jurusan TEXT,
            prodi TEXT,
            fakultas TEXT,
            jp TEXT,
            alamatmaha TEXT,
            namaortu TEXT,
            pekerortu TEXT,
            alamatortu TEXT,
            judul TEXT,
            doping TEXT,
            namatumbuhan TEXT,
            asaltumbuhan TEXT,
            keperluan TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')


# ================= FORM ROUTES =================
@app.route('/form/aktif-kuliah')
def form_aktif_kuliah():
    return render_template('form_aktif_kuliah.html')

@app.route('/form/lab-penelitian')
def form_lab_penelitian():
    return render_template('form_lab_penelitian.html')

@app.route('/form/ethical-clearance')
def form_ethical_clearance():
    return render_template('form_ethical_clearance.html')

@app.route('/form/identifikasi-tumbuhan')
def form_identifikasi_tumbuhan():
    return render_template('form_identifikasi_tumbuhan.html')


# ================= SUBMIT =================
@app.route('/submit', methods=['POST'])
def submit():
    data = (
        request.form.get('nama'),
        request.form.get('ttl'),
        request.form.get('jk'),
        request.form.get('npm'),
        request.form.get('nim'),
        request.form.get('sem'),
        request.form.get('jurusan'),
        request.form.get('prodi'),
        request.form.get('fakultas'),   # ← sudah benar urutan
        request.form.get('jp'),
        request.form.get('alamatmaha'),
        request.form.get('namaortu'),
        request.form.get('pekerortu'),
        request.form.get('alamatortu'),
        request.form.get('judul'),
        request.form.get('doping'),
        request.form.get('namatumbuhan'),
        request.form.get('asaltumbuhan'),
        request.form.get('keperluan')
    )

    # validasi sederhana
    if not data[-1]:
        return "Keperluan tidak valid"

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    INSERT INTO pengajuan (
        nama, ttl, jk, npm, nim, sem, jurusan, prodi, fakultas, jp,
        alamatmaha, namaortu, pekerortu, alamatortu,
        judul, doping, namatumbuhan, asaltumbuhan, keperluan
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, data)

    conn.commit()
    conn.close()

    return "Pengajuan berhasil dikirim!"


# ================= ADMIN =================
@app.route('/admin')
def admin():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("SELECT * FROM pengajuan ORDER BY id DESC")
    data = c.fetchall()

    conn.close()
    return render_template('admin.html', data=data)


# ================= GENERATE =================
@app.route('/generate/<int:id>')
def generate(id):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("SELECT * FROM pengajuan WHERE id=?", (id,))
    row = c.fetchone()
    conn.close()

    if not row:
        return "Data tidak ditemukan"

    template_path = TEMPLATES.get(row["keperluan"])
    if not template_path:
        return "Template tidak ditemukan"

    data = dict(row)  # ← otomatis semua field masuk

    doc = DocxTemplate(template_path)
    doc.render(data)

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name=f"surat_{id}.docx")


# ================= RUN =================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)