#!/usr/bin/env python3
"""Google-Drive-Zugriff für die Content-Pipeline (nur Standardbibliothek).

Zugang: Ein Google-Apps-Script (apps-script/token.gs) im Konto von Joni gibt
ein kurzlebiges Drive-Token aus. Die Umgebung braucht dafür:
  JONIS_DRIVE_TOKEN_URL  Web-App-URL des Skripts
  JONIS_DRIVE_KEY        geheimer Schlüssel, der im Skript hinterlegt ist

Ohne diese Variablen funktioniert nur Lesen, und nur für per Link
freigegebene Ordner (Fallback über die öffentliche Ordneransicht).

Aufruf:
  drive.py whoami
  drive.py ls <ordner-id>                 JSON-Liste der Dateien
  drive.py get <datei-id> <pfad>
  drive.py put <pfad> <ordner-id> [name]  gibt neue Datei-ID aus
  drive.py update <datei-id> <pfad>       Inhalt einer Datei ersetzen
  drive.py mv <datei-id> <ziel-ordner> <alt-ordner>
  drive.py mkdir <name> <ordner-id>       vorhandenen Ordner wiederverwenden
"""
import json
import mimetypes
import os
import re
import shutil
import sys
import urllib.parse
import urllib.request

API = "https://www.googleapis.com/drive/v3"
UPLOAD = "https://www.googleapis.com/upload/drive/v3"
_token = None


def has_auth():
    return bool(os.environ.get("JONIS_DRIVE_TOKEN_URL") and os.environ.get("JONIS_DRIVE_KEY"))


def token():
    global _token
    if _token:
        return _token
    if not has_auth():
        sys.exit("Kein Drive-Schreibzugang: JONIS_DRIVE_TOKEN_URL und JONIS_DRIVE_KEY fehlen (siehe README).")
    url = os.environ["JONIS_DRIVE_TOKEN_URL"] + "?key=" + urllib.parse.quote(os.environ["JONIS_DRIVE_KEY"])
    with urllib.request.urlopen(url, timeout=60) as r:
        data = json.load(r)
    if "token" not in data:
        sys.exit(f"Token-Skript antwortet ohne Token: {data}")
    _token = data["token"]
    return _token


def _req(method, url, body=None, headers=None, raw=False):
    h = {"Authorization": "Bearer " + token()}
    h.update(headers or {})
    req = urllib.request.Request(url, data=body, method=method, headers=h)
    r = urllib.request.urlopen(req, timeout=600)
    return r if raw else json.load(r)


def ls(folder):
    if not has_auth():
        return _ls_public(folder)
    files, page = [], None
    while True:
        q = {
            "q": f"'{folder}' in parents and trashed = false",
            "fields": "nextPageToken, files(id,name,mimeType,size,createdTime)",
            "pageSize": 1000,
        }
        if page:
            q["pageToken"] = page
        res = _req("GET", f"{API}/files?" + urllib.parse.urlencode(q))
        files += res.get("files", [])
        page = res.get("nextPageToken")
        if not page:
            return files


def _ls_public(folder):
    url = f"https://drive.google.com/embeddedfolderview?id={folder}"
    html = urllib.request.urlopen(url, timeout=60).read().decode("utf-8")
    out = []
    for m in re.finditer(r'id="entry-([\w-]+)".*?flip-entry-title">([^<]+)<', html, re.S):
        name = m.group(2)
        kind = "application/vnd.google-apps.folder" if "." not in name else mimetypes.guess_type(name)[0] or ""
        out.append({"id": m.group(1), "name": name, "mimeType": kind})
    return out


def get(file_id, path):
    if has_auth():
        r = _req("GET", f"{API}/files/{file_id}?alt=media", raw=True)
    else:
        url = f"https://drive.usercontent.google.com/download?id={file_id}&export=download&confirm=t"
        r = urllib.request.urlopen(url, timeout=600)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "wb") as f:
        shutil.copyfileobj(r, f, 1 << 20)
    return path


def _resumable(method, url, path, meta):
    mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
    size = os.path.getsize(path)
    start = _req(method, url + ("&" if "?" in url else "?") + "uploadType=resumable",
                 body=json.dumps(meta).encode(),
                 headers={"Content-Type": "application/json; charset=UTF-8",
                          "X-Upload-Content-Type": mime, "X-Upload-Content-Length": str(size)},
                 raw=True)
    session = start.headers["Location"]
    with open(path, "rb") as f:
        req = urllib.request.Request(session, data=f, method="PUT",
                                     headers={"Content-Type": mime, "Content-Length": str(size)})
        return json.load(urllib.request.urlopen(req, timeout=1800))


def put(path, parent, name=None):
    meta = {"name": name or os.path.basename(path), "parents": [parent]}
    return _resumable("POST", f"{UPLOAD}/files?fields=id,name", path, meta)["id"]


def update(file_id, path):
    return _resumable("PATCH", f"{UPLOAD}/files/{file_id}?fields=id,name", path, {})["id"]


def mv(file_id, to, frm):
    q = urllib.parse.urlencode({"addParents": to, "removeParents": frm, "fields": "id"})
    return _req("PATCH", f"{API}/files/{file_id}?{q}", body=b"{}",
                headers={"Content-Type": "application/json"})["id"]


def mkdir(name, parent):
    for f in ls(parent):
        if f["name"] == name and f["mimeType"] == "application/vnd.google-apps.folder":
            return f["id"]
    meta = {"name": name, "parents": [parent], "mimeType": "application/vnd.google-apps.folder"}
    return _req("POST", f"{API}/files?fields=id", body=json.dumps(meta).encode(),
                headers={"Content-Type": "application/json"})["id"]


def main(argv):
    if not argv:
        sys.exit(__doc__)
    cmd, args = argv[0], argv[1:]
    if cmd == "whoami":
        if not has_auth():
            print("kein Schreibzugang (nur öffentliche Links)")
            return
        info = _req("GET", f"{API}/about?fields=user(emailAddress)")
        print(info["user"]["emailAddress"])
    elif cmd == "ls":
        print(json.dumps(ls(args[0]), ensure_ascii=False, indent=1))
    elif cmd == "get":
        print(get(args[0], args[1]))
    elif cmd == "put":
        print(put(args[0], args[1], args[2] if len(args) > 2 else None))
    elif cmd == "update":
        print(update(args[0], args[1]))
    elif cmd == "mv":
        print(mv(args[0], args[1], args[2]))
    elif cmd == "mkdir":
        print(mkdir(args[0], args[1]))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
