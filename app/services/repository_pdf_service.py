from __future__ import annotations

from dataclasses import dataclass, field
from textwrap import wrap

from dataclasses import dataclass


PAGE_WIDTH = 612
PAGE_HEIGHT = 792
MARGIN = 50
LINE_HEIGHT = 15
CONTENT_WIDTH = 512


def _pdf_text(value: object) -> str:
    text = str(value).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    return text.encode("latin-1", errors="replace").decode("latin-1")


@dataclass
class RepositoryFinding:
    file: str
    line_number: int
    severity: str
    category: str
    comment: str


@dataclass
class RepositoryReport:
    files_scanned: int
    issues_found: int
    critical: int
    high: int
    medium: int
    low: int

    repository_health_score: int

    strengths: list[str]
    weaknesses: list[str]
    recommendations: list[str]

    findings: list[RepositoryFinding]




@dataclass
class PdfPage:
    commands: list[str] = field(default_factory=list)

class RepositoryPdfBuilder:
    def __init__(self, report: RepositoryReport):
        self.report = report
        self.pages: list[PdfPage] = []
        self.page = self._new_page()
        self.y = PAGE_HEIGHT - MARGIN

    def build(self) -> bytes:
        self._draw_header()
        self._add_section_title("Repository Overview")
        self._add_key_value(
            "Files Scanned",
            self.report.files_scanned,
        )
        self._add_key_value(
            "Issues Found",
            self.report.issues_found,
        )
        self._add_key_value(
            "Critical",
            self.report.critical,
        )
        self._add_key_value(
            "High",
            self.report.high,
        )
        self._add_key_value(
            "Medium",
            self.report.medium,
        )
        self._add_key_value(
            "Low",
            self.report.low,
        )
        self._add_key_value(
            "Health Score",
            f"{self.report.repository_health_score}/100",
        )
        self._space(12)
        self._add_section_title("Strengths")
        for item in self.report.strengths:
            self._add_paragraph(f"• {item}")

        self._space(12)
        self._add_section_title("Weaknesses")
        for item in self.report.weaknesses:
            self._add_paragraph(f"• {item}")

        self._space(12)
        self._add_section_title("Recommendations")
        for item in self.report.recommendations:
            self._add_paragraph(f"• {item}")

        self._space(12)
        self._add_section_title("Findings")

        for index, finding in enumerate(
            self.report.findings,
            start=1,
        ):
            self._add_comment_block(
                index,
                finding,
            )

        return self._render()



    def _new_page(self) -> PdfPage:
        page = PdfPage()
        self.pages.append(page)
        return page

    def _draw_header(self) -> None:
        self.page.commands.extend(
            [
                "0.07 0.10 0.18 rg",
                f"0 {PAGE_HEIGHT - 108} {PAGE_WIDTH} 108 re f",
                "0.15 0.39 0.92 rg",
                f"{MARGIN} {PAGE_HEIGHT - 95} 72 4 re f",
            ]
        )
        self._add_text("Repository Security Report", x=MARGIN, y=PAGE_HEIGHT - 54, size=22, font="F2", color="1 1 1")
        self._add_text(
            f"Repository Report | Health Score {self.report.repository_health_score}/100",
            x=MARGIN,
            y=PAGE_HEIGHT - 78,
            size=11,
            color="0.82 0.87 0.94",
        )
        self.y = PAGE_HEIGHT - 136

    def _ensure_space(self, height: int) -> None:
        if self.y - height >= MARGIN:
            return

        self.page = self._new_page()
        self.y = PAGE_HEIGHT - MARGIN
        self._add_text("Repository Security Report", size=12, font="F2", color="0.07 0.10 0.18")
        self._space(18)

    def _space(self, amount: int) -> None:
        self.y -= amount

    def _add_section_title(self, title: str) -> None:
        self._ensure_space(34)
        self._add_text(title, size=14, font="F2", color="0.07 0.10 0.18")
        self.y -= 6
        self.page.commands.extend(["0.15 0.39 0.92 rg", f"{MARGIN} {self.y} 86 2 re f"])
        self.y -= 18

    def _add_key_value(self, key: str, value: object) -> None:
        self._ensure_space(LINE_HEIGHT)
        self._add_text(f"{key}: ", size=10, font="F2", color="0.20 0.25 0.34")
        self._add_text(str(value), x=MARGIN + 150, y=self.y, size=10, color="0.07 0.10 0.18")
        self.y -= LINE_HEIGHT

    def _add_paragraph(self, text: str, size: int = 10, indent: int = 0) -> None:
        for line in self._wrap_text(text, size=size, indent=indent):
            self._ensure_space(LINE_HEIGHT)
            self._add_text(line, x=MARGIN + indent, size=size, color="0.20 0.25 0.34")
            self.y -= LINE_HEIGHT

    def _add_comment_block(self, index: int, comment: object) -> None:
        comment_lines = self._wrap_text(comment.comment, size=10)
        minimum_block_height = (6 * LINE_HEIGHT) + 18
        full_block_height = ((5 + len(comment_lines)) * LINE_HEIGHT) + 18
        self._ensure_space(min(full_block_height, minimum_block_height))

        self._add_text(f"Comment #{index}", size=11, font="F2", color="0.07 0.10 0.18")
        self.y -= LINE_HEIGHT
        self._add_text(f"File: {comment.file}",size=10,color="0.20 0.25 0.34")
        self.y -= LINE_HEIGHT
        self._add_text(f"Line: {comment.line_number}", size=10, color="0.20 0.25 0.34")
        self.y -= LINE_HEIGHT
        self._add_text(f"Severity: {comment.severity.upper()}", size=10, color="0.20 0.25 0.34")
        self.y -= LINE_HEIGHT
        self._add_text(f"Category: {comment.category}", size=10, color="0.20 0.25 0.34")
        self.y -= LINE_HEIGHT
        self._space(6)

        for line in comment_lines:
            self._ensure_space(LINE_HEIGHT + 28)
            self._add_text(line, size=10, color="0.20 0.25 0.34")
            self.y -= LINE_HEIGHT

        self._space(8)
        self._ensure_space(18)
        self.page.commands.extend(["0.82 0.86 0.92 rg", f"{MARGIN} {self.y} {CONTENT_WIDTH} 1 re f"])
        self._space(18)

    def _wrap_text(self, text: str, size: int = 10, indent: int = 0) -> list[str]:
        available_width = CONTENT_WIDTH - indent
        max_chars = max(36, int(available_width / (size * 0.48)))
        lines = []
        for paragraph in str(text).splitlines() or [""]:
            lines.extend(wrap(paragraph, width=max_chars) or [""])

        return lines

    def _add_text(
        self,
        text: str,
        x: int = MARGIN,
        y: int | None = None,
        size: int = 11,
        font: str = "F1",
        color: str = "0 0 0",
    ) -> None:
        text_y = self.y if y is None else y
        self.page.commands.extend(
            [
                f"{color} rg",
                "BT",
                f"/{font} {size} Tf",
                f"{x} {text_y} Td",
                f"({_pdf_text(text)}) Tj",
                "ET",
            ]
        )

    def _render(self) -> bytes:
        objects: list[str] = [
            "<< /Type /Catalog /Pages 2 0 R >>",
            "",
        ]

        page_object_ids: list[int] = []
        content_object_ids: list[int] = []
        next_id = 3

        for _ in self.pages:
            page_object_ids.append(next_id)
            content_object_ids.append(next_id + 1)
            next_id += 2

        kids = " ".join(f"{page_id} 0 R" for page_id in page_object_ids)
        objects[1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(self.pages)} >>"

        for page, page_id, content_id in zip(self.pages, page_object_ids, content_object_ids):
            objects.append(
                "<< /Type /Page "
                "/Parent 2 0 R "
                f"/MediaBox [0 0 {PAGE_WIDTH} {PAGE_HEIGHT}] "
                "/Resources << /Font << "
                "/F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> "
                "/F2 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >> "
                ">> >> "
                f"/Contents {content_id} 0 R >>"
            )
            stream = "\n".join(page.commands)
            objects.append(f"<< /Length {len(stream.encode('latin-1'))} >>\nstream\n{stream}\nendstream")

        return _write_pdf(objects)


def _write_pdf(objects: list[str]) -> bytes:
    output = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]

    for object_id, body in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{object_id} 0 obj\n{body}\nendobj\n".encode("latin-1"))

    xref_offset = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode("latin-1"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("latin-1"))

    output.extend(
        (
            "trailer\n"
            f"<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            "startxref\n"
            f"{xref_offset}\n"
            "%%EOF\n"
        ).encode("latin-1")
    )
    return bytes(output)

def generate_repository_pdf(
    report: RepositoryReport,
) -> bytes:
    return RepositoryPdfBuilder(
        report
    ).build()