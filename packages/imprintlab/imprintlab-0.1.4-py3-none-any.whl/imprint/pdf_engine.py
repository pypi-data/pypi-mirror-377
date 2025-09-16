import os

class PDFBuildResult:
    def __init__(self, pdf_bytes: bytes):
        self.pdf_bytes = pdf_bytes
        self._default_suffix = ".pdf"

    def save(self, path: str) -> None:
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(path, "wb") as f:
            f.write(self.pdf_bytes)

    def to_bytes(self) -> bytes:
        return self.pdf_bytes

    def show(self) -> None:
        # abre um arquivo temporário .pdf usando o viewer do sistema
        import tempfile, webbrowser
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        tmp.write(self.pdf_bytes)
        tmp.flush()
        tmp.close()
        webbrowser.open(f"file://{tmp.name}")
