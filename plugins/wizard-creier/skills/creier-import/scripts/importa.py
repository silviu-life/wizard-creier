#!/usr/bin/env python3
"""Aduce în 00-brut/ tot ce primește: exportul din claude.ai, ZIP-uri, foldere, fișiere.

Folosire:  python importa.py <folderul 00-brut> <sursa> [<sursa> ...]
Verificare: python importa.py --test

Originalele nu se ating: totul se copiază sau se dezarhivează în 00-brut/.
ZIP-urile găsite înăuntru se dezarhivează pe loc. Orice folder care conține
conversations.json (exportul claude.ai) devine fișiere .md lizibile + index.md.
"""
import json
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path


def slug(text, max_len=60):
    text = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", str(text or "")).strip()
    text = re.sub(r"\s+", "-", text)
    return text[:max_len].rstrip("-.") or "fara-titlu"


def unique(path):
    if not path.exists():
        return path
    i = 2
    while True:
        candidate = path.with_name(f"{path.stem}-{i}{path.suffix}")
        if not candidate.exists():
            return candidate
        i += 1


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as err:
        print(f"ATENȚIE: nu pot citi {path.name} ({err}). L-am lăsat neatins.")
        return None


def message_text(msg):
    parts = [b.get("text", "") for b in msg.get("content") or [] if b.get("type") == "text"]
    text = "\n\n".join(p for p in parts if p) or msg.get("text") or ""
    for att in msg.get("attachments") or []:
        name = att.get("file_name") or "atașament"
        if att.get("extracted_content"):
            text += f"\n\n**Atașament: {name}**\n\n{att['extracted_content']}"
        else:
            text += f"\n\n*(atașament: {name})*"
    for f in msg.get("files") or []:
        text += f"\n\n*(fișier: {f.get('file_name') or '?'})*"
    return text.strip()


def write_conversations(convs, out):
    folder = out / "conversatii"
    folder.mkdir(parents=True, exist_ok=True)
    rows = []
    for conv in convs:
        msgs = conv.get("chat_messages") or []
        if not msgs:
            continue
        title = conv.get("name") or "Fără titlu"
        date = (conv.get("created_at") or "")[:10]
        path = unique(folder / f"{date}-{slug(title)}.md")
        lines = [f"# {title}", "", f"Data: {date}", ""]
        for msg in msgs:
            who = "Eu" if msg.get("sender") == "human" else "Claude"
            lines += [f"## {who}", "", message_text(msg), ""]
        path.write_text("\n".join(lines), encoding="utf-8")
        rows.append((date, title, len(msgs), path.name))
    return rows


def write_projects(projects, out):
    names = []
    for proj in projects:
        name = proj.get("name") or "Proiect"
        folder = unique(out / "proiecte" / slug(name))
        folder.mkdir(parents=True)
        lines = [f"# {name}", ""]
        if proj.get("description"):
            lines += [proj["description"], ""]
        if proj.get("prompt_template"):
            lines += ["## Instrucțiunile proiectului", "", proj["prompt_template"], ""]
        (folder / "proiect.md").write_text("\n".join(lines), encoding="utf-8")
        for doc in proj.get("docs") or []:
            fname = slug(doc.get("filename") or "document", 80)
            if not Path(fname).suffix:
                fname += ".md"
            unique(folder / fname).write_text(doc.get("content") or "", encoding="utf-8")
        names.append(name)
    return names


def strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for value in obj.values():
            yield from strings(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from strings(value)


def convert_claude_export(folder):
    """Transformă un export claude.ai (deja copiat în 00-brut) în .md lizibile."""
    report = [f"Export claude.ai: {folder}"]
    convs = load_json(folder / "conversations.json")
    if convs is None:
        return report
    rows = write_conversations(convs, folder)
    (folder / "conversations.json").unlink()
    report.append(f"  conversații: {len(rows)}")

    projects_file = folder / "projects.json"
    if projects_file.exists():
        projects = load_json(projects_file)
        if projects is not None:
            names = write_projects(projects, folder)
            projects_file.unlink()
            report.append(f"  proiecte: {len(names)} ({', '.join(names)})")

    # Formatul memoriei nu e documentat public: păstrăm orice text mai lung de o etichetă.
    for mem_file in folder.glob("memor*.json"):
        data = load_json(mem_file)
        if data is None:
            continue
        texts = [s for s in strings(data) if len(s) > 40]
        if texts:
            body = "\n\n---\n\n".join(texts)
            (folder / "memorie.md").write_text(f"# Memoria Claude\n\n{body}\n", encoding="utf-8")
            mem_file.unlink()
            report.append(f"  memorie: {len(texts)} bucăți de text")

    users = folder / "users.json"  # doar datele contului, nu ajută creierul
    if users.exists():
        users.unlink()

    rows.sort(reverse=True)
    index = ["# Conversații importate", "", "| Data | Titlu | Mesaje | Fișier |", "|---|---|---|---|"]
    index += [f"| {d} | {t.replace('|', '/')} | {n} | conversatii/{f} |" for d, t, n, f in rows]
    (folder / "index.md").write_text("\n".join(index) + "\n", encoding="utf-8")
    report.append(f"  index: {folder / 'index.md'}")
    return report


def expand(target):
    """Dezarhivează ZIP-urile din copie, apoi convertește exporturile claude.ai."""
    report = []
    while True:
        zips = [p for p in target.rglob("*") if p.is_file() and p.suffix.lower() == ".zip"]
        if target.is_file() and target.suffix.lower() == ".zip":
            zips.append(target)
        if not zips:
            break
        for zpath in zips:
            out = unique(zpath.with_name(slug(zpath.stem, 80)))
            try:
                with zipfile.ZipFile(zpath) as z:
                    z.extractall(out)  # extractall elimină căile absolute și „..”
            except zipfile.BadZipFile:
                report.append(f"ATENȚIE: {zpath.name} nu e un ZIP valid. L-am lăsat așa.")
                zpath.rename(zpath.with_suffix(".zip-stricat"))
                continue
            zpath.unlink()  # e copia din 00-brut; originalul rămâne la utilizator
            if zpath == target:
                target = out
    if target.is_dir():
        for conv in sorted(target.rglob("conversations.json")):
            report += convert_claude_export(conv.parent)
    return report


def bring(src, dest):
    src = Path(src).expanduser().resolve()
    if not src.exists():
        return [f"LIPSEȘTE: {src}"]
    if dest.resolve().is_relative_to(src):
        return [f"REFUZAT: {src} conține chiar folderul 00-brut."]
    if src.is_dir():
        target = unique(dest / slug(src.name, 80))
        shutil.copytree(src, target)
    else:
        target = unique(dest / src.name)
        shutil.copy2(src, target)
    return [f"Copiat: {src} -> {target}"] + expand(target)


def main(args):
    if len(args) < 2:
        print(__doc__)
        return 1
    dest = Path(args[0]).expanduser()
    dest.mkdir(parents=True, exist_ok=True)
    for src in args[1:]:
        print("\n".join(bring(src, dest)))
    return 0


def _test():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        export = tmp / "export"
        export.mkdir()
        (export / "conversations.json").write_text(json.dumps([{
            "name": "Oferta: client nou", "created_at": "2026-05-01T10:00:00Z",
            "chat_messages": [
                {"sender": "human", "content": [{"type": "text", "text": "Cât costă pachetul?"}]},
                {"sender": "assistant", "text": "500 lei",
                 "attachments": [{"file_name": "preturi.txt", "extracted_content": "Pachet: 500"}]},
            ]}, {"name": "gol", "chat_messages": []}]), encoding="utf-8")
        (export / "projects.json").write_text(json.dumps([{
            "name": "Firma", "prompt_template": "Vorbește cu tu.",
            "docs": [{"filename": "servicii", "content": "Consultanță"}]}]), encoding="utf-8")
        (export / "users.json").write_text("[]", encoding="utf-8")
        mixed = tmp / "de-la-mine"
        mixed.mkdir()
        shutil.make_archive(str(mixed / "claude-export"), "zip", export)
        (mixed / "oferta.txt").write_text("ofertă veche", encoding="utf-8")

        brut = tmp / "creier" / "00-brut"
        assert main([str(brut), str(mixed), str(tmp / "nu-exista")]) == 0
        root = brut / "de-la-mine" / "claude-export"
        conv = (root / "conversatii" / "2026-05-01-Oferta-client-nou.md").read_text(encoding="utf-8")
        assert "## Eu" in conv and "500 lei" in conv and "Pachet: 500" in conv
        assert "Vorbește cu tu." in (root / "proiecte" / "Firma" / "proiect.md").read_text(encoding="utf-8")
        assert (root / "proiecte" / "Firma" / "servicii.md").exists()
        assert "Oferta: client nou" in (root / "index.md").read_text(encoding="utf-8")
        assert not list(brut.rglob("*.json")) and not list(brut.rglob("*.zip"))
        assert (brut / "de-la-mine" / "oferta.txt").exists()
        assert (mixed / "claude-export.zip").exists()  # originalul neatins
    print("OK")


if __name__ == "__main__":
    if sys.argv[1:] == ["--test"]:
        _test()
    else:
        sys.exit(main(sys.argv[1:]))
