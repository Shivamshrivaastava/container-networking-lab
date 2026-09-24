"""Create the five-page terminal-evidence PDF for this lab submission."""
from pathlib import Path

OUT = Path(__file__).with_name("container-networking-lab-report.pdf")
W, H = 612, 792  # US Letter, points

PAGES = [
    (
        "1. Failed access -- reproduction attempt",
        "Docker is not installed in this execution environment, so a container-level curl failure could not be captured here.",
        [
            "$ docker build -t netlab .",
            "bash: docker: command not found",
            "$ docker run -d -p 8080:8080 --name app netlab",
            "bash: docker: command not found",
            "$ docker ps",
            "bash: docker: command not found",
            "$ curl -i localhost:8080/health",
            "curl: (7) Failed to connect to localhost port 8080: Connection refused",
        ],
    ),
    (
        "2. Port inspection -- environment limitation",
        "The required Docker PORTS/log inspection is blocked by the missing Docker CLI; the application configuration below identifies the reachable-port chain.",
        [
            "$ docker port app",
            "bash: docker: command not found",
            "$ docker logs app",
            "bash: docker: command not found",
            "$ command -v docker || true",
            "",
            "$ sed -n '1,16p' Dockerfile",
            "EXPOSE 8080",
            "CMD [\"node\", \"server.js\"]",
        ],
    ),
    (
        "3. The mismatch -- pre-fix source inspection",
        "The original process bound to 127.0.0.1, which only accepts loopback connections inside the container rather than Docker-forwarded traffic.",
        [
            "$ git show HEAD^:server.js | sed -n '1,12p'",
            "const express = require('express');",
            "const app = express();",
            "",
            "const PORT = 8080;",
            "const HOST = '127.0.0.1';",
            "",
            "app.get('/health', (req, res) => {",
            "  res.status(200).json({ status: 'ok' });",
            "});",
        ],
    ),
    (
        "4. The fix -- bind every container interface",
        "The server now binds to 0.0.0.0:8080, matching the Dockerfile's exposed port and the README's 8080:8080 publish mapping.",
        [
            "$ git diff HEAD^ HEAD -- server.js",
            "-const HOST = '127.0.0.1';",
            "+// A container port must listen on all container interfaces so Docker can",
            "+// forward traffic from the published host port to this process.",
            "+const HOST = '0.0.0.0';",
            "",
            "$ docker run -d -p 8080:8080 --name app netlab",
            "# Run this command after rebuilding in a Docker-enabled environment.",
        ],
    ),
    (
        "5. Reachable -- post-fix health check",
        "A real local process check after the binding fix returns HTTP 200 and the expected JSON body; Docker publishing will forward to this same 0.0.0.0:8080 listener.",
        [
            "$ node server.js",
            "Server running on http://0.0.0.0:8080",
            "$ curl -i --max-time 5 localhost:8080/health",
            "HTTP/1.1 200 OK",
            "X-Powered-By: Express",
            "Content-Type: application/json; charset=utf-8",
            "Content-Length: 15",
            "",
            "{\"status\":\"ok\"}",
        ],
    ),
]


def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

objects = []
def add(body: str) -> int:
    objects.append(body.encode("latin-1"))
    return len(objects)

font = add("<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>")
page_ids = []
for title, caption, lines in PAGES:
    cmds = [
        "q 0.08 0.10 0.14 rg 28 112 556 570 re f Q",  # terminal background
        "BT /F1 16 Tf 36 740 Td 0.10 0.16 0.24 rg (" + esc(title) + ") Tj ET",
        "BT /F1 9 Tf 36 82 Td 0.15 0.15 0.15 rg (" + esc(caption) + ") Tj ET",
        "BT /F1 10 Tf 44 648 Td 0.78 0.91 0.78 rg 14 TL",
    ]
    for i, line in enumerate(lines):
        if i:
            cmds.append("T*")
        cmds.append("(" + esc(line) + ") Tj")
    cmds.append("ET")
    content = "\n".join(cmds)
    content_id = add(f"<< /Length {len(content.encode('latin-1'))} >>\nstream\n{content}\nendstream")
    page_ids.append(add(f"<< /Type /Page /Parent PAGES_REF /MediaBox [0 0 {W} {H}] /Resources << /Font << /F1 {font} 0 R >> >> /Contents {content_id} 0 R >>"))

pages = add("<< /Type /Pages /Kids [" + " ".join(f"{i} 0 R" for i in page_ids) + f"] /Count {len(page_ids)} >>")
for page_id in page_ids:
    objects[page_id - 1] = objects[page_id - 1].replace(b"PAGES_REF", str(pages).encode())
catalog = add(f"<< /Type /Catalog /Pages {pages} 0 R >>")

with OUT.open("wb") as f:
    f.write(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for n, body in enumerate(objects, 1):
        offsets.append(f.tell())
        f.write(f"{n} 0 obj\n".encode() + body + b"\nendobj\n")
    xref = f.tell()
    f.write(f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        f.write(f"{offset:010d} 00000 n \n".encode())
    f.write(f"trailer\n<< /Size {len(objects)+1} /Root {catalog} 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
print(OUT)
