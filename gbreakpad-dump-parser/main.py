from flask import Flask, render_template, request, send_file
from waitress import serve
from pathlib import Path
from subprocess import Popen, PIPE
from tempfile import NamedTemporaryFile
from os import path, chdir, remove, getenv
from tarfile import TarFile
from threading import Thread

app = Flask(__name__)

SYMBOLS_DEFAULT_PATH = getenv("SYMBOLS_DEFAULT_PATH", default = "/opt/symbols")
MINIDUMP_STACKWALK_BINARY = "/usr/local/bin/minidump_stackwalk"
SERVER_PORT = getenv("SERVER_PORT", default="5000")


def extract_and_remove_symbols_archive(archive, extract_path):
    arch = TarFile.open(archive, "r:gz")
    arch.extractall(extract_path)
    remove(archive)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/dump_upload", methods=["POST"])
def do_parse():
    upload = request.files.get("upload")
    if upload and Path(upload.filename).suffix == ".dmp":
        enable_stderr = request.form.get("enable_stderr")
        temp_file = NamedTemporaryFile(suffix=upload.filename)
        temp_file.write(upload.read())
        minidump_process = Popen([MINIDUMP_STACKWALK_BINARY, temp_file.name, SYMBOLS_DEFAULT_PATH], stdout=PIPE, stderr=PIPE)
        out, err = minidump_process.communicate()
        with open('stackwalk-result.txt', 'w') as f:
            f.write(out.decode())
    else:
        return render_template("index.html",notify="error")
    return render_template("index.html",
                    out=out.decode(), err=err.decode() if enable_stderr is not None else "",
                    filename=upload.filename
                    )


@app.route("/symbols_upload", methods=["POST"])
def symbols_upload():
    result_get="success"
    upload = request.files.get("upload", None)
    if upload and Path(upload.filename).suffix == ".gz" :
        temp_file = NamedTemporaryFile(delete=False, suffix=".tar.gz")
        temp_file.write(upload.read())
        Thread(target=extract_and_remove_symbols_archive, args=(temp_file.name, SYMBOLS_DEFAULT_PATH)).start()
    else:
        result_get="error"
    return render_template("index.html", notify=result_get)


@app.route('/download')
def download():
    path = 'stackwalk-result.txt'
    return send_file(path, as_attachment=True)


if __name__ == "__main__":
    abspath = path.abspath(__file__)
    chdir(path.dirname(abspath))

    serve(app, host = "0.0.0.0", port = SERVER_PORT)
