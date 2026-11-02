#!/usr/bin/env python3
"""Aduce în 00-brut/ tot ce primește: exporturi claude.ai și ChatGPT, ZIP-uri, foldere, fișiere.

Folosire:  python importa.py <folderul 00-brut> <sursa> [<sursa> ...]
Verificare: python importa.py --test

Originalele nu se ating: totul se copiază sau se dezarhivează în 00-brut/.
ZIP-urile găsite înăuntru se dezarhivează pe loc. Un export recunoscut devine fișiere .md
lizibile + index.md; un fișier conversations*.json nerecunoscut rămâne neatins. Word, Excel
și PowerPoint primesc alături o copie text. Ce s-a importat deja nu se dublează la o nouă rulare.
"""
import hashlib
import json
import re
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime, timezone
from pathlib import Path

MANIFEST = ".importate.json"
WINDOWS_RESERVED = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)),
                    *(f"LPT{i}" for i in range(1, 10))}
UNREADABLE = {".doc", ".xls", ".ppt", ".pages", ".numbers", ".key", ".rar", ".7z"}
MAX_SHEET_ROWS = 5000  # ponytail: foile mai mari rămân în fișierul original; crește dacă apar cereri reale


def slug(text, max_len=60):
    text = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", str(text or "")).strip()
    text = re.sub(r"\s+", "-", text)
    text = text[:max_len].rstrip("-.") or "fara-titlu"
    return f"_{text}" if text.split(".")[0].upper() in WINDOWS_RESERVED else text


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
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as err:
        print(f"ATENȚIE: nu pot citi {path.name} ({err}). L-am lăsat neatins.")
        return None


def export_kind(data):
    """Formatul exportului după conținut, nu după numele fișierului."""
    first = next((c for c in data if isinstance(c, dict)), None) if isinstance(data, list) else None
    if first is None:
        return None
    if "mapping" in first:
        return "chatgpt"
    return "claude" if "chat_messages" in first else None


def claude_message_text(msg):
    parts = []
    for block in msg.get("content") or []:
        if not isinstance(block, dict):
            continue
        if block.get("type") == "text" and block.get("text"):
            parts.append(block["text"])
        elif block.get("type") == "tool_use" and block.get("name") == "artifacts":
            art = block.get("input") or {}
            if art.get("content"):
                parts.append(f"**Artefact: {art.get('title') or 'fără titlu'}**\n\n{art['content']}")
    text = "\n\n".join(parts) or msg.get("text") or ""
    for att in msg.get("attachments") or []:
        name = att.get("file_name") or "atașament"
        if att.get("extracted_content"):
            text += f"\n\n**Atașament: {name}**\n\n{att['extracted_content']}"
        else:
            text += f"\n\n*(atașament: {name})*"
    for f in msg.get("files") or []:
        text += f"\n\n*(fișier: {f.get('file_name') or '?'})*"
    return text.strip()


def parse_claude(conv):
    msgs = [("Eu" if m.get("sender") == "human" else "Claude", claude_message_text(m))
            for m in conv.get("chat_messages") or []]
    return {"id": conv.get("uuid"), "updated": conv.get("updated_at"), "title": conv.get("name"),
            "date": (conv.get("created_at") or "")[:10], "msgs": msgs}


def chatgpt_part(part):
    if isinstance(part, str):
        return part
    if isinstance(part, dict):
        if part.get("text"):
            return part["text"]
        return "*(imagine sau fișier atașat)*" if part.get("asset_pointer") else ""
    return ""


def parse_chatgpt(conv):
    """Exportul ChatGPT e un arbore; ramura finală se citește de la current_node în sus."""
    mapping = conv.get("mapping") or {}
    node_id, chain, visited = conv.get("current_node"), [], set()
    while node_id in mapping and node_id not in visited:
        visited.add(node_id)
        chain.append(mapping[node_id])
        node_id = mapping[node_id].get("parent")
    chain.reverse()
    if not chain:  # export fără current_node: ordinea cronologică
        chain = sorted(mapping.values(), key=lambda n: (n.get("message") or {}).get("create_time") or 0)
    msgs = []
    for node in chain:
        msg = node.get("message") or {}
        role = (msg.get("author") or {}).get("role")
        if role not in ("user", "assistant") or (msg.get("metadata") or {}).get("is_visually_hidden_from_conversation"):
            continue
        content = msg.get("content") or {}
        text = "\n\n".join(p for p in map(chatgpt_part, content.get("parts") or []) if p)
        text = text or content.get("text") or ""
        if text.strip():
            msgs.append(("Eu" if role == "user" else "ChatGPT", text.strip()))
    created = conv.get("create_time")
    date = datetime.fromtimestamp(created, timezone.utc).strftime("%Y-%m-%d") if isinstance(created, (int, float)) else ""
    return {"id": conv.get("conversation_id") or conv.get("id"), "updated": conv.get("update_time"),
            "title": conv.get("title"), "date": date, "msgs": msgs}


PARSERS = {"claude": parse_claude, "chatgpt": parse_chatgpt}


def write_conversations(convs, out, dest, seen):
    """Scrie conversațiile noi sau schimbate. Întoarce (rânduri, deja importate, eșuate)."""
    folder = out / "conversatii"
    rows, same, failed = [], 0, 0
    for kind, raw in convs:
        try:
            conv = PARSERS[kind](raw)
        except (AttributeError, TypeError, KeyError, ValueError, OverflowError, OSError):
            failed += 1
            continue
        if not conv["msgs"]:
            continue
        key = f"conv:{kind}:{conv['id']}" if conv["id"] else None
        old = seen.get(key) if key else None
        if old and old.get("updated") == conv["updated"]:
            same += 1
            continue
        first = conv["msgs"][0][1].replace("\n", " ")[:60]
        title = conv["title"] or first or "Fără titlu"
        folder.mkdir(parents=True, exist_ok=True)
        path = unique(folder / f"{conv['date']}-{slug(title)}.md")
        lines = [f"# {title}", "", f"Data: {conv['date']}", f"Sursa: {'ChatGPT' if kind == 'chatgpt' else 'claude.ai'}", ""]
        for who, text in conv["msgs"]:
            lines += [f"## {who}", "", text, ""]
        path.write_text("\n".join(lines), encoding="utf-8")
        if old and old.get("path"):  # versiunea veche, generată de noi, e înlocuită de cea nouă
            (dest / old["path"]).unlink(missing_ok=True)
        if key:
            seen[key] = {"updated": conv["updated"], "path": path.relative_to(dest).as_posix()}
        rows.append((conv["date"], title, len(conv["msgs"]), path.name))
    return rows, same, failed


def write_projects(projects, out, seen):
    names = []
    for proj in projects:
        if proj.get("is_starter_project"):
            continue
        key = f"proj:{proj.get('uuid')}" if proj.get("uuid") else None
        if key and seen.get(key) == proj.get("updated_at"):
            continue
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
        if key:
            seen[key] = proj.get("updated_at")
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


def convert_export(folder, dest, seen):
    """Transformă un export recunoscut (deja copiat în 00-brut) în .md lizibile."""
    report, convs, used, kinds = [], [], [], set()
    for path in sorted(folder.glob("conversations*.json")):
        data = load_json(path)
        kind = export_kind(data) if data is not None else None
        if kind is None:
            if data is not None:
                report.append(f"ATENȚIE: nu recunosc formatul lui {path}. L-am lăsat neatins.")
            continue
        convs += [(kind, c) for c in data if isinstance(c, dict)]
        used.append(path)
        kinds.add(kind)
    if not used:
        return report

    rows, same, failed = write_conversations(convs, folder, dest, seen)
    label = " + ".join("ChatGPT" if k == "chatgpt" else "claude.ai" for k in sorted(kinds))
    report.append(f"Export {label}: {folder}")
    report.append(f"  conversații noi: {len(rows)}; deja importate: {same}")
    if failed:
        report.append(f"ATENȚIE: {failed} conversații n-au putut fi citite. Fișierul original a rămas în {folder}.")
    elif not rows and not same:
        report.append(f"ATENȚIE: n-am găsit nicio conversație cu mesaje. Fișierul original a rămas în {folder}.")
    else:
        for path in used:
            path.unlink()

    if "claude" in kinds:
        projects_file = folder / "projects.json"
        if projects_file.exists():
            projects = load_json(projects_file)
            if isinstance(projects, list):
                names = write_projects(projects, folder, seen)
                projects_file.unlink()
                report.append(f"  proiecte noi: {len(names)} ({', '.join(names)})")
        # Formatul memoriei nu e documentat public: scriem textele și păstrăm fișierul original lângă.
        texts = []
        for mem_file in sorted(folder.glob("memor*.json")):
            data = load_json(mem_file)
            if data is not None:
                texts += [s for s in strings(data) if len(s) > 15]
        if texts:
            body = "\n\n---\n\n".join(texts)
            (folder / "memorie.md").write_text(f"# Memoria Claude\n\n{body}\n", encoding="utf-8")
            report.append(f"  memorie: {len(texts)} bucăți de text")
        (folder / "users.json").unlink(missing_ok=True)  # doar datele contului, nu ajută creierul
    if "chatgpt" in kinds:
        for junk in ("chat.html", "user.json"):  # dublură a conversațiilor și datele contului
            (folder / junk).unlink(missing_ok=True)

    rows.sort(reverse=True)
    index = ["# Conversații importate", "", "| Data | Titlu | Mesaje | Fișier |", "|---|---|---|---|"]
    index += [f"| {d} | {t.replace('|', '/')} | {n} | conversatii/{f} |" for d, t, n, f in rows]
    (folder / "index.md").write_text("\n".join(index) + "\n", encoding="utf-8")
    report.append(f"  index: {folder / 'index.md'}")
    return report


def local(el):
    return el.tag.rsplit("}", 1)[-1]


def xml_paragraphs(data, para_tag, text_tag):
    out = []
    for para in ET.fromstring(data).iter():
        if local(para) == para_tag:
            text = "".join(t.text or "" for t in para.iter() if local(t) == text_tag)
            if text.strip():
                out.append(text)
    return out


def column_index(ref):
    n = 0
    for ch in re.match(r"[A-Z]*", ref or "").group():
        n = n * 26 + ord(ch) - 64
    return max(n - 1, 0)


def xlsx_text(z):
    names = z.namelist()
    shared = []
    if "xl/sharedStrings.xml" in names:
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")):
            shared.append("".join(t.text or "" for t in si.iter() if local(t) == "t"))
    sheets = [n for n in names if re.fullmatch(r"xl/worksheets/sheet\d+\.xml", n)]
    sheets.sort(key=lambda n: int(re.search(r"(\d+)\.xml", n).group(1)))
    out = []
    for number, name in enumerate(sheets, 1):
        rows = [el for el in ET.fromstring(z.read(name)).iter() if local(el) == "row"]
        out += [f"## Foaia {number}", ""]
        for row in rows[:MAX_SHEET_ROWS]:
            cells = {}
            for cell in row:
                if local(cell) != "c":
                    continue
                value = next((v.text for v in cell if local(v) == "v"), None)
                if cell.get("t") == "s" and value is not None:
                    value = shared[int(value)]
                elif cell.get("t") == "inlineStr":
                    value = "".join(t.text or "" for t in cell.iter() if local(t) == "t")
                if value not in (None, ""):
                    cells[column_index(cell.get("r"))] = str(value).replace("|", "/").replace("\n", " ")
            if cells:
                out.append(" | ".join(cells.get(i, "") for i in range(max(cells) + 1)))
        if len(rows) > MAX_SHEET_ROWS:
            out.append(f"*(doar primele {MAX_SHEET_ROWS} rânduri din {len(rows)}; restul e în fișierul original)*")
        out.append("")
    return out


def office_text(path):
    with zipfile.ZipFile(path) as z:
        suffix = path.suffix.lower()
        if suffix == ".docx":
            return xml_paragraphs(z.read("word/document.xml"), "p", "t")
        if suffix == ".xlsx":
            return xlsx_text(z)
        slides = [n for n in z.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)]
        slides.sort(key=lambda n: int(re.search(r"(\d+)\.xml", n).group(1)))
        return [line for n in slides for line in xml_paragraphs(z.read(n), "p", "t")]


def add_text_copies(target):
    """Word, Excel și PowerPoint primesc alături o copie .md; formatele vechi se raportează."""
    report, files = [], [target] if target.is_file() else [p for p in target.rglob("*") if p.is_file()]
    for path in files:
        suffix = path.suffix.lower()
        if suffix in (".docx", ".xlsx", ".pptx"):
            try:
                body = "\n\n".join(office_text(path)) if suffix != ".xlsx" else "\n".join(office_text(path))
                path.with_name(path.name + ".md").write_text(f"# Text extras din {path.name}\n\n{body}\n", encoding="utf-8")
                report.append(f"  copie text: {path.name}.md")
            except (zipfile.BadZipFile, KeyError, ET.ParseError, ValueError, IndexError, RuntimeError, OSError):
                report.append(f"NECITIT: {path}")
        elif suffix in UNREADABLE:
            report.append(f"NECITIT: {path}")
    return report


def expand(target, dest, seen):
    """Dezarhivează ZIP-urile din copie, apoi convertește exporturile recunoscute."""
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
            except (zipfile.BadZipFile, RuntimeError, NotImplementedError, OSError) as err:
                report.append(f"ATENȚIE: nu pot deschide {zpath.name} (e stricat sau are parolă: {err}). L-am lăsat așa.")
                zpath.rename(zpath.with_suffix(".zip-necitit"))
                continue
            zpath.unlink()  # e copia din 00-brut; originalul rămâne la utilizator
            if zpath == target:
                target = out
    if target.is_dir():
        for folder in sorted({p.parent for p in target.rglob("conversations*.json")}):
            try:
                report += convert_export(folder, dest, seen)
            except (AttributeError, TypeError, KeyError, ValueError, OSError) as err:
                report.append(f"ATENȚIE: conversia din {folder} s-a oprit ({err}). Fișierele au rămas acolo.")
    return report + add_text_copies(target)


def signature(src):
    """Amprenta unei surse, ca aceeași sursă să nu fie adusă de două ori."""
    digest = hashlib.sha256()
    if src.is_file():
        with src.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1 << 20), b""):
                digest.update(chunk)
    else:  # ponytail: nume + mărime + dată, fără conținut; un folder uriaș nu se citește de două ori
        for path in sorted(p for p in src.rglob("*") if p.is_file()):
            stat = path.stat()
            digest.update(f"{path.relative_to(src)}|{stat.st_size}|{int(stat.st_mtime)}\n".encode("utf-8", "replace"))
    return f"src:{digest.hexdigest()}"


def bring(src, dest, seen):
    src = Path(src).expanduser().resolve()
    if not src.exists():
        return [f"LIPSEȘTE: {src}"]
    if dest.resolve().is_relative_to(src):
        return [f"REFUZAT: {src} conține chiar folderul 00-brut."]
    key = signature(src)
    if key in seen:
        return [f"Deja importat, sărit: {src}"]
    report = []
    if src.is_dir():
        target = unique(dest / slug(src.name, 80))
        try:
            shutil.copytree(src, target, ignore_dangling_symlinks=True)
        except shutil.Error as err:
            report.append(f"ATENȚIE: {len(err.args[0])} fișiere din {src} n-au putut fi copiate.")
    elif re.fullmatch(r"conversations.*\.json", src.name):
        target = unique(dest / "export")  # JSON-ul adus singur are nevoie de folderul lui
        target.mkdir()
        shutil.copy2(src, target / src.name)
    else:
        target = unique(dest / src.name)
        shutil.copy2(src, target)
    report = [f"Copiat: {src} -> {target}"] + report + expand(target, dest, seen)
    seen[key] = str(target.name)
    return report


def main(args):
    if len(args) < 2:
        print(__doc__)
        return 1
    dest = Path(args[0]).expanduser()
    dest.mkdir(parents=True, exist_ok=True)
    manifest = dest / MANIFEST
    seen = (load_json(manifest) or {}) if manifest.exists() else {}
    for src in args[1:]:
        try:
            print("\n".join(bring(src, dest, seen)))
        except Exception as err:  # o sursă stricată nu le oprește pe celelalte
            print(f"ATENȚIE: {src} n-a putut fi adus ({type(err).__name__}: {err}). Merg mai departe.")
        manifest.write_text(json.dumps(seen, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


def _make_docx(path):
    xml = ('<w:document xmlns:w="w"><w:body><w:p><w:r><w:t>Contract </w:t></w:r><w:r><w:t>Popescu</w:t></w:r></w:p>'
           '</w:body></w:document>')
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("word/document.xml", xml)


def _make_xlsx(path):
    sheet = ('<worksheet xmlns="m"><sheetData><row r="1"><c r="A1" t="s"><v>0</v></c><c r="C1"><v>700</v></c></row>'
             '</sheetData></worksheet>')
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("xl/sharedStrings.xml", '<sst xmlns="m"><si><t>Standard</t></si></sst>')
        z.writestr("xl/worksheets/sheet1.xml", sheet)


def _chatgpt_conv(cid, text, updated=2.0):
    return {"id": cid, "conversation_id": cid, "title": "Oferta GPT", "create_time": 1777629600.5,
            "update_time": updated, "current_node": "c", "mapping": {
                "root": {"id": "root", "parent": None, "message": None},
                "a": {"id": "a", "parent": "root", "message": {"author": {"role": "system"},
                      "content": {"content_type": "text", "parts": ["ascuns"]}}},
                "b": {"id": "b", "parent": "a", "message": {"author": {"role": "user"},
                      "content": {"content_type": "multimodal_text", "parts": [{"asset_pointer": "file-1"}, text]}}},
                "alt": {"id": "alt", "parent": "b", "message": {"author": {"role": "assistant"},
                        "content": {"content_type": "text", "parts": ["ramura abandonată"]}}},
                "c": {"id": "c", "parent": "b", "message": {"author": {"role": "assistant"},
                      "content": {"content_type": "text", "parts": ["650 lei"]}}}}}


def _test():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        export = tmp / "export"
        export.mkdir()
        (export / "conversations.json").write_text(json.dumps([{
            "uuid": "c1", "updated_at": "1", "name": "Oferta: client nou", "created_at": "2026-05-01T10:00:00Z",
            "chat_messages": [
                {"sender": "human", "content": [{"type": "text", "text": "Cât costă pachetul?"}]},
                {"sender": "assistant", "text": "500 lei",
                 "attachments": [{"file_name": "preturi.txt", "extracted_content": "Pachet: 500"}]},
                {"sender": "assistant", "content": [{"type": "tool_use", "name": "artifacts",
                 "input": {"title": "Oferta", "content": "OFERTA ARTEFACT"}}]},
            ]}, {"name": "gol", "chat_messages": []},
            {"uuid": "c2", "updated_at": "1", "name": "", "created_at": "2026-05-02T10:00:00Z",
             "chat_messages": [{"sender": "human", "text": "Termen de livrare"}]}]), encoding="utf-8")
        (export / "projects.json").write_text(json.dumps([
            {"name": "Firma", "prompt_template": "Vorbește cu tu.",
             "docs": [{"filename": "servicii", "content": "Consultanță"}]},
            {"name": "Exemplu", "is_starter_project": True}]), encoding="utf-8")
        (export / "users.json").write_text("[]", encoding="utf-8")
        mixed = tmp / "de-la-mine"
        mixed.mkdir()
        shutil.make_archive(str(mixed / "claude-export"), "zip", export)
        (mixed / "oferta.txt").write_text("ofertă veche", encoding="utf-8")
        _make_docx(mixed / "contract.docx")
        _make_xlsx(mixed / "preturi.xlsx")
        (mixed / "vechi.xls").write_bytes(b"x")

        brut = tmp / "creier" / "00-brut"
        assert main([str(brut), str(mixed), str(tmp / "nu-exista")]) == 0
        root = brut / "de-la-mine" / "claude-export"
        conv = (root / "conversatii" / "2026-05-01-Oferta-client-nou.md").read_text(encoding="utf-8")
        assert "## Eu" in conv and "500 lei" in conv and "Pachet: 500" in conv and "OFERTA ARTEFACT" in conv
        assert "Vorbește cu tu." in (root / "proiecte" / "Firma" / "proiect.md").read_text(encoding="utf-8")
        assert (root / "proiecte" / "Firma" / "servicii.md").exists()
        assert not (root / "proiecte" / "Exemplu").exists()
        index = (root / "index.md").read_text(encoding="utf-8")
        assert "Oferta: client nou" in index and "Termen de livrare" in index
        assert not [p for p in brut.rglob("*.json") if p.name != MANIFEST] and not list(brut.rglob("*.zip"))
        assert (brut / "de-la-mine" / "oferta.txt").exists()
        assert (mixed / "claude-export.zip").exists()  # originalul neatins
        assert "Contract Popescu" in (brut / "de-la-mine" / "contract.docx.md").read_text(encoding="utf-8")
        assert "Standard |  | 700" in (brut / "de-la-mine" / "preturi.xlsx.md").read_text(encoding="utf-8")

        # aceeași sursă nu se dublează
        assert main([str(brut), str(mixed)]) == 0
        assert not (brut / "de-la-mine-2").exists()

        # ChatGPT, împărțit în mai multe fișiere; ramura abandonată și mesajele de sistem nu intră
        gpt = tmp / "gpt"
        gpt.mkdir()
        (gpt / "conversations-000.json").write_text(json.dumps([_chatgpt_conv("g1", "Cât costă?")]), encoding="utf-8")
        (gpt / "conversations-001.json").write_text(json.dumps([_chatgpt_conv("g2", "Și livrarea?")]), encoding="utf-8")
        (gpt / "chat.html").write_text("<html>", encoding="utf-8")
        assert main([str(brut), str(gpt)]) == 0
        files = sorted((brut / "gpt" / "conversatii").glob("*.md"))
        text = files[0].read_text(encoding="utf-8")
        assert len(files) == 2 and files[0].name.startswith("2026-05-01")
        assert "## ChatGPT" in text and "650 lei" in text and "imagine" in text
        assert "ramura abandonată" not in text and "ascuns" not in text
        assert not (brut / "gpt" / "chat.html").exists()

        # un export nou, cumulativ, aduce doar ce s-a schimbat și înlocuiește versiunea veche
        gpt2 = tmp / "gpt2"
        gpt2.mkdir()
        (gpt2 / "conversations.json").write_text(json.dumps(
            [_chatgpt_conv("g1", "Cât costă?"), _chatgpt_conv("g2", "Și livrarea azi?", 3.0)]), encoding="utf-8")
        assert main([str(brut), str(gpt2)]) == 0
        assert len(list((brut / "gpt2" / "conversatii").glob("*.md"))) == 1
        assert len(list((brut / "gpt" / "conversatii").glob("*.md"))) == 1

        # un fișier străin cu același nume nu se atinge
        foreign = tmp / "clienti"
        foreign.mkdir()
        (foreign / "conversations.json").write_text('[{"nume": "Ion"}]', encoding="utf-8")
        (foreign / "users.json").write_text('[{"nume": "Ion"}]', encoding="utf-8")
        assert main([str(brut), str(foreign)]) == 0
        assert (brut / "clienti" / "conversations.json").exists() and (brut / "clienti" / "users.json").exists()

        # ChatGPT adus ca fișier singur, formă neașteptată în interior: nimic nu se pierde, restul merge
        solo = tmp / "conversations.json"
        solo.write_text(json.dumps([{"title": "x", "mapping": "stricat", "id": "z"}]), encoding="utf-8")
        ok = tmp / "ok.txt"
        ok.write_text("ok", encoding="utf-8")
        assert main([str(brut), str(solo), str(ok)]) == 0
        assert (brut / "export" / "conversations.json").exists() and (brut / "ok.txt").exists()
        assert slug("con") == "_con"
    print("OK")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):  # consola Windows nu e UTF-8 și cade la „ț”
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if sys.argv[1:] == ["--test"]:
        _test()
    else:
        sys.exit(main(sys.argv[1:]))
