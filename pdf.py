from fpdf import FPDF


class PDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 16)
        self.cell(0, 10, 'Reporte de Zonas Calientes en Imágenes Térmicas RGB', 0, 1, 'C')
        self.set_font('helvetica', 'I', 12)
        self.cell(0, 10, 'Análisis de temperatura y pérdidas de calor', 0, 1, 'C')
        self.line(10, 30, 200, 30)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')
