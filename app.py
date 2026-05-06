from flask import Flask, render_template, request, send_file, session, redirect
import sqlite3
import os
from docxtpl import DocxTemplate
from io import BytesIO
from datetime import datetime


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fallback_key")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == "admin" and password == "balkisut":
            session['login'] = True
            return redirect('/admin')
        else:
            return "Login gagal"

    return render_template('login.html')

# mapping template (lebih aman pakai os.path.join)
TEMPLATES = {
    "Surat Aktif Kuliah": os.path.join("templates_surat", "aktif_kuliah.docx"),
    "Permohonan Penggunaan Ruangan dan Fasilitas Laboratorium Penelitian": os.path.join("templates_surat", "lab_penelitian.docx"),
    "Permohonan Surat Ethical Clearance Manusia": os.path.join("templates_surat", "ethical(manusia).docx"),
    "Permohonan Surat Ethical Clearance Hewan": os.path.join("templates_surat", "ethical(hewan).docx"),
    "Surat Identifikasi Tumbuhan": os.path.join("templates_surat", "tumbuhan.docx"),
    "Surat Penyerahan Skripsi": os.path.join("templates_surat", "penyerahan_skripsi.docx"),
    "seminar hasil": os.path.join("templates_surat", "seminar_hasil.docx"),
    "Surat Penyerahan Skripsi Luks": os.path.join("templates_surat", "penyerahan_skripsi_luks.docx")
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
            keperluan TEXT,
            rencanapenel TEXT,
            tglsidang TEXT,
            hari TEXT,
            tgl TEXT,
            jam TEXT,
            doji1 TEXT,
            doji2 TEXT,
            doji3 TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
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

@app.route('/form/seminar-hasil')
def form_seminar_hasil():
    return render_template('form_seminar_hasil.html')

@app.route('/form/lab-penelitian')
def form_lab_penelitian():
    return render_template('form_lab_penelitian.html')

@app.route('/form/ethical-clearance-manusia')
def form_ethical_clearance_manusia():
    return render_template('form_ethical_clearance(manusia).html')

@app.route('/form/ethical-clearance-hewan')
def form_ethical_clearance_hewan():
    return render_template('form_ethical_clearance(hewan).html')

@app.route('/form/identifikasi-tumbuhan')
def form_identifikasi_tumbuhan():
    return render_template('form_identifikasi_tumbuhan.html')

@app.route('/form/penyerahan-skripsi')
def form_penyerahan_skripsi():
    return render_template('form_penyerahan_skripsi.html')

@app.route('/form/penyerahan-skripsi-luks')
def form_penyerahan_skripsi_luks():
    return render_template('form_penyerahan_skripsi_luks.html')

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
        request.form.get('keperluan'),
        request.form.get('rencanapenel'),
        request.form.get('tglsidang'),
        request.form.get('hari'),
        request.form.get('tgl'),
        request.form.get('jam'),
        request.form.get('doji1'),
        request.form.get('doji2'),
        request.form.get('doji3')
    )

    # validasi sederhana
    # if not data[-1]:
    #     return "Keperluan tidak valid"

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    INSERT INTO pengajuan (
        nama, ttl, jk, npm, nim, sem, jurusan, prodi, fakultas, jp,
        alamatmaha, namaortu, pekerortu, alamatortu,
        judul, doping, namatumbuhan, asaltumbuhan, keperluan, rencanapenel, tglsidang, hari, tgl, jam, doji1, doji2, doji3
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, data)

    conn.commit()
    conn.close()

    return "Pengajuan berhasil dikirim!"


# ================= ADMIN =================
@app.route('/admin')
def admin():
    if not session.get('login'):
        return redirect('/login')

    search = request.args.get('search', '')
    limit = int(request.args.get('limit', 10))

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    if search:
        query = """
        SELECT * FROM pengajuan
        WHERE nama LIKE ? OR keperluan LIKE ?
        ORDER BY id DESC
        LIMIT ?
        """
        c.execute(query, (f"%{search}%", f"%{search}%", limit))
    else:
        c.execute("SELECT * FROM pengajuan ORDER BY id DESC LIMIT ?", (limit,))

    data = c.fetchall()
    conn.close()

    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    return render_template('admin.html', data=data, now=now)

@app.route('/delete/<int:id>')
def delete(id):
    if not session.get('login'):
        return redirect('/login')

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DELETE FROM pengajuan WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/admin')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/api/data')
def api_data():
    if not session.get('login'):
        return {"error": "unauthorized"}, 403

    search = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    
    sort = request.args.get('sort', 'id')
    order = request.args.get('order', 'desc')

    # biar aman (WAJIB) 
    allowed_sort = ["id", "nama", "keperluan", "created_at"]
    if sort not in allowed_sort:
        sort = "id"

    query_order = "ASC" if order == "asc" else "DESC"

    offset = (page - 1) * limit

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    if search:
        c.execute("""
        SELECT COUNT(*) FROM pengajuan
        WHERE nama LIKE ? OR keperluan LIKE ?
        """, (f"%{search}%", f"%{search}%"))
    else:
        c.execute("SELECT COUNT(*) FROM pengajuan")

    total = c.fetchone()[0]

    if search:
        c.execute(f"""
    SELECT * FROM pengajuan
    WHERE nama LIKE ? OR keperluan LIKE ?
    ORDER BY {sort} {query_order}
    LIMIT ? OFFSET ?
    """, (f"%{search}%", f"%{search}%", limit, offset))
    else:
        c.execute(f"""
    SELECT * FROM pengajuan
    ORDER BY {sort} {query_order}
    LIMIT ? OFFSET ?
    """, (limit, offset))

    data = [dict(row) for row in c.fetchall()]
    conn.close()

    return {
        "data": data,
        "total": total,
        "page": page,
        "limit": limit
    }

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