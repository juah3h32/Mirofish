"""
Generador de PDF para Reportes MiroFish
Crea un PDF profesional estilo "slide ejecutivo" con la info más importante de la simulación.

Usa PyMuPDF (fitz) para generar un PDF con diseño atractivo:
- Página de portada con título, fecha, stats clave
- Páginas de resumen ejecutivo por capítulo
- Métricas y hallazgos clave
"""

import os
import textwrap
from datetime import datetime
from typing import Dict, Any, List, Optional
import fitz  # PyMuPDF

from ..config import Config
from ..utils.logger import get_logger

logger = get_logger('mirofish.pdf_generator')

# ═══════════════════════════════════════════════════════════
# Colores y estilos
# ═══════════════════════════════════════════════════════════

# Paleta profesional oscura
COLOR_PRIMARY = (0.0, 0.0, 0.0)        # Negro - texto principal
COLOR_ACCENT = (0.95, 0.38, 0.08)       # Naranja MiroFish (#F26014)
COLOR_ACCENT_DARK = (0.8, 0.25, 0.0)    # Naranja oscuro
COLOR_GRAY = (0.4, 0.4, 0.4)           # Gris medio
COLOR_LIGHT_GRAY = (0.6, 0.6, 0.6)     # Gris claro
COLOR_BG_LIGHT = (0.97, 0.97, 0.97)    # Fondo claro
COLOR_BG_ACCENT = (0.95, 0.38, 0.08)   # Fondo naranja
COLOR_WHITE = (1.0, 1.0, 1.0)          # Blanco
COLOR_BORDER = (0.88, 0.88, 0.88)      # Borde sutil

# Dimensiones
PAGE_WIDTH = 595.28   # A4 width in points
PAGE_HEIGHT = 841.89  # A4 height in points
MARGIN = 50
CONTENT_WIDTH = PAGE_WIDTH - 2 * MARGIN


class PDFReportGenerator:
    """Generador de PDF profesional para reportes MiroFish"""

    def __init__(self, report_data: Dict[str, Any]):
        """
        Inicializa el generador de PDF.

        Args:
            report_data: Datos completos del reporte (de Report.to_dict())
        """
        self.report = report_data
        self.outline = report_data.get('outline', {})
        self.markdown = report_data.get('markdown_content', '')
        self.doc = None
        self.page = None
        self.y = 0  # Posición vertical actual
        self.page_num = 0

    def generate(self, output_path: str) -> str:
        """
        Genera el PDF y lo guarda en output_path.

        Returns:
            Ruta del PDF generado
        """
        self.doc = fitz.open()

        # Páginas del reporte
        self._add_cover_page()
        self._add_executive_summary()
        self._add_key_findings()
        self._add_metrics_page()

        # Guardar
        self.doc.save(output_path)
        self.doc.close()
        logger.info(f"PDF generado: {output_path}")
        return output_path

    def _new_page(self):
        """Crea una nueva página y resetea la posición Y"""
        self.page = self.doc.new_page(width=PAGE_WIDTH, height=PAGE_HEIGHT)
        self.y = MARGIN
        self.page_num += 1

    def _check_space(self, needed: float) -> bool:
        """Verifica si hay suficiente espacio, si no, crea nueva página"""
        if self.y + needed > PAGE_HEIGHT - MARGIN:
            self._new_page()
            return True
        return False

    # ═══════════════════════════════════════════════════════
    # Página 1: Portada
    # ═══════════════════════════════════════════════════════

    def _add_cover_page(self):
        """Portada profesional del reporte"""
        self._new_page()

        # Fondo superior con banda naranja
        rect = fitz.Rect(0, 0, PAGE_WIDTH, 280)
        self.page.draw_rect(rect, color=None, fill=COLOR_BG_ACCENT)

        # Logo / Nombre
        self.y = 60
        self._draw_text(
            "MIROFISH",
            x=MARGIN,
            y=self.y,
            fontsize=36,
            color=COLOR_WHITE,
            fontname="hebo",
            bold=True
        )

        self.y += 45
        self._draw_text(
            "Informe de Predicción · Simulación Social",
            x=MARGIN,
            y=self.y,
            fontsize=14,
            color=COLOR_WHITE,
            fontname="hebo"
        )

        # Línea separadora
        self.y += 30
        self.page.draw_line(
            fitz.Point(MARGIN, self.y),
            fitz.Point(MARGIN + 80, self.y),
            color=COLOR_WHITE,
            width=3
        )

        # Título del reporte
        self.y += 50
        title = self.outline.get('title', 'Informe de Simulación')
        self._draw_text_wrapped(
            title,
            x=MARGIN,
            y=self.y,
            width=CONTENT_WIDTH,
            fontsize=26,
            color=COLOR_PRIMARY,
            fontname="hebo",
            bold=True,
            line_height=1.3
        )

        # Resumen
        self.y += 80
        summary = self.outline.get('summary', '')
        if summary:
            self._draw_text(
                "RESUMEN EJECUTIVO",
                x=MARGIN,
                y=self.y,
                fontsize=10,
                color=COLOR_ACCENT,
                fontname="hebo",
                bold=True
            )
            self.y += 20
            self._draw_text_wrapped(
                summary,
                x=MARGIN,
                y=self.y,
                width=CONTENT_WIDTH,
                fontsize=12,
                color=COLOR_GRAY,
                fontname="helv",
                line_height=1.6
            )

        # Metadata en la parte inferior
        self.y = PAGE_HEIGHT - 120

        # Línea separadora
        self.page.draw_line(
            fitz.Point(MARGIN, self.y),
            fitz.Point(PAGE_WIDTH - MARGIN, self.y),
            color=COLOR_BORDER,
            width=1
        )

        self.y += 25

        # Fecha y ID
        created = self.report.get('created_at', '')
        if created:
            date_str = created[:10] if 'T' in created else created[:10]
        else:
            date_str = datetime.now().strftime('%Y-%m-%d')

        self._draw_text(
            f"Fecha: {date_str}",
            x=MARGIN,
            y=self.y,
            fontsize=9,
            color=COLOR_LIGHT_GRAY,
            fontname="helv"
        )
        self._draw_text(
            f"ID: {self.report.get('report_id', 'N/A')}",
            x=PAGE_WIDTH - MARGIN - 150,
            y=self.y,
            fontsize=9,
            color=COLOR_LIGHT_GRAY,
            fontname="helv",
            align="right"
        )

        self.y += 15
        scenario = self.report.get('simulation_requirement', '')
        if scenario:
            self._draw_text_wrapped(
                f"Escenario: {scenario}",
                x=MARGIN,
                y=self.y,
                width=CONTENT_WIDTH,
                fontsize=9,
                color=COLOR_LIGHT_GRAY,
                fontname="helv"
            )

    # ═══════════════════════════════════════════════════════
    # Página 2: Resumen Ejecutivo Extendido
    # ═══════════════════════════════════════════════════════

    def _add_executive_summary(self):
        """Resumen ejecutivo con los hallazgos principales de cada capítulo"""
        self._new_page()

        self._draw_section_header("Resumen de Hallazgos")

        sections = self.outline.get('sections', [])

        for i, section in enumerate(sections):
            title = section.get('title', f'Capítulo {i+1}')
            content = section.get('content', '')

            # Título del capítulo
            self.y += 10
            self._check_space(60)

            # Badge numerado
            badge_text = f"0{i+1}" if i < 9 else str(i+1)
            self._draw_badge(badge_text, x=MARGIN, y=self.y + 2)

            self._draw_text(
                title,
                x=MARGIN + 45,
                y=self.y,
                fontsize=14,
                color=COLOR_PRIMARY,
                fontname="hebo",
                bold=True
            )

            self.y += 22

            # Extraer primeras 3-4 frases clave del contenido
            if content:
                key_points = self._extract_key_sentences(content, max_sentences=3)
                for point in key_points:
                    clean_point = self._clean_markdown(point.strip())
                    if len(clean_point) > 15:
                        self._check_space(30)
                        self._draw_bullet_point(clean_point)
                        self.y += 4

            self.y += 10

    # ═══════════════════════════════════════════════════════
    # Página 3+: Hallazgos Clave por Capítulo
    # ═══════════════════════════════════════════════════════

    def _add_key_findings(self):
        """Hallazgos detallados de cada capítulo"""
        sections = self.outline.get('sections', [])

        for i, section in enumerate(sections):
            content = section.get('content', '')
            title = section.get('title', f'Capítulo {i+1}')

            if not content:
                continue

            self._new_page()
            self._draw_section_header(title)

            # Extraer hallazgos clave (párrafos relevantes)
            paragraphs = self._extract_key_paragraphs(content, max_paragraphs=6)

            for para in paragraphs:
                clean = self._clean_markdown(para.strip())
                if len(clean) > 20:
                    self.y += 8
                    self._check_space(80)

                    # Si empieza con **, es un sub-título
                    if clean.startswith('**') and '**' in clean[2:]:
                        sub_title = clean.split('**')[1]
                        self._draw_text(
                            sub_title,
                            x=MARGIN,
                            y=self.y,
                            fontsize=12,
                            color=COLOR_ACCENT,
                            fontname="hebo",
                            bold=True
                        )
                        self.y += 20
                    else:
                        self._draw_text_wrapped(
                            clean,
                            x=MARGIN + 10,
                            y=self.y,
                            width=CONTENT_WIDTH - 20,
                            fontsize=10,
                            color=COLOR_PRIMARY,
                            fontname="helv",
                            line_height=1.5
                        )
                        self.y += 8

            # Si todavía hay más contenido, añadir indicador
            remaining = len(paragraphs)
            if remaining > 0:
                self.y += 5
                self._check_space(20)
                self._draw_text(
                    f"→ {remaining} puntos adicionales en el informe completo",
                    x=MARGIN,
                    y=self.y,
                    fontsize=8,
                    color=COLOR_LIGHT_GRAY,
                    fontname="helv"
                )

    # ═══════════════════════════════════════════════════════
    # Página Final: Métricas y KPIs
    # ═══════════════════════════════════════════════════════

    def _add_metrics_page(self):
        """Página de métricas y KPIs de la simulación"""
        self._new_page()
        self._draw_section_header("Métricas de la Simulación")

        self.y += 15

        # Extraer métricas del contenido markdown
        metrics = self._extract_metrics()

        if not metrics:
            # Métricas por defecto
            metrics = [
                ("Agentes Simulados", "100+", "Individuos con perfiles únicos"),
                ("Plataformas", "2", "Twitter / Reddit en paralelo"),
                ("Rondas", "10", "Iteraciones temporales"),
                ("Motor IA", "Claude Sonnet 4.6", "Anthropic"),
                ("GraphRAG", "Zep", "Memoria temporal + comunidad"),
            ]

        # Mostrar métricas en grid 2x2
        positions = [
            (MARGIN, self.y),
            (MARGIN + CONTENT_WIDTH/2 + 15, self.y),
            (MARGIN, self.y + 130),
            (MARGIN + CONTENT_WIDTH/2 + 15, self.y + 130),
        ]

        for idx, (label, value, desc) in enumerate(metrics[:4]):
            if idx < len(positions):
                x, base_y = positions[idx]
                self._draw_metric_card(x, base_y, label, str(value), desc)

        self.y += 290

        # Nota al pie
        self._check_space(40)
        self.page.draw_line(
            fitz.Point(MARGIN, self.y),
            fitz.Point(PAGE_WIDTH - MARGIN, self.y),
            color=COLOR_BORDER,
            width=1
        )
        self.y += 20
        self._draw_text(
            "Generado por MiroFish · Motor de Predicción Social · v0.1",
            x=MARGIN,
            y=self.y,
            fontsize=8,
            color=COLOR_LIGHT_GRAY,
            fontname="helv"
        )
        self._draw_text(
            f"© {datetime.now().year} MiroFish",
            x=PAGE_WIDTH - MARGIN - 120,
            y=self.y,
            fontsize=8,
            color=COLOR_LIGHT_GRAY,
            fontname="helv",
            align="right"
        )

    # ═══════════════════════════════════════════════════════
    # Métodos de dibujo
    # ═══════════════════════════════════════════════════════

    def _draw_text(self, text: str, x: float, y: float, fontsize: float = 10,
                   color: tuple = COLOR_PRIMARY, fontname: str = "helv",
                   bold: bool = False, align: str = "left"):
        """Dibuja texto en la posición dada"""
        try:
            font = fitz.Font(fontname)
        except Exception:
            font = fitz.Font("helv")

        text_width = font.text_length(text, fontsize=fontsize)

        if align == "right":
            x = x - text_width
        elif align == "center":
            x = x - text_width / 2

        self.page.insert_text(
            fitz.Point(x, y + fontsize * 0.8),
            text,
            fontname=fontname,
            fontsize=fontsize,
            color=color
        )

        return text_width

    def _draw_text_wrapped(self, text: str, x: float, y: float, width: float,
                           fontsize: float = 10, color: tuple = COLOR_PRIMARY,
                           fontname: str = "helv", bold: bool = False,
                           line_height: float = 1.4):
        """Dibuja texto con ajuste de línea automático"""
        try:
            font = fitz.Font(fontname)
        except Exception:
            font = fitz.Font("helv")

        # Calcular caracteres por línea
        avg_char_width = font.text_length("a", fontsize=fontsize)
        chars_per_line = max(1, int(width / avg_char_width))

        lines = []
        words = text.split(' ')
        current_line = ''

        for word in words:
            test_line = current_line + (' ' if current_line else '') + word
            test_width = font.text_length(test_line, fontsize=fontsize)

            if test_width > width and current_line:
                lines.append(current_line)
                current_line = word
            else:
                current_line = test_line

        if current_line:
            lines.append(current_line)

        # Dibujar cada línea
        line_spacing = fontsize * line_height
        for i, line in enumerate(lines):
            if self.y + line_spacing > PAGE_HEIGHT - MARGIN:
                self._new_page()

            self._draw_text(line, x, self.y, fontsize, color, fontname)
            self.y += line_spacing

    def _draw_section_header(self, title: str):
        """Dibuja un encabezado de sección con línea decorativa"""
        # Línea naranja decorativa
        self.page.draw_line(
            fitz.Point(MARGIN, self.y),
            fitz.Point(MARGIN + 40, self.y),
            color=COLOR_ACCENT,
            width=4
        )

        self.y += 20
        self._draw_text(
            title,
            x=MARGIN,
            y=self.y,
            fontsize=20,
            color=COLOR_PRIMARY,
            fontname="hebo",
            bold=True
        )

        self.y += 35

    def _draw_badge(self, text: str, x: float, y: float):
        """Dibuja un badge numerado"""
        size = 28
        rect = fitz.Rect(x, y, x + size, y + size)
        self.page.draw_rect(rect, color=None, fill=COLOR_BG_ACCENT)
        self._draw_text(
            text,
            x=x + size/2,
            y=y + 2,
            fontsize=12,
            color=COLOR_WHITE,
            fontname="hebo",
            bold=True,
            align="center"
        )

    def _draw_bullet_point(self, text: str):
        """Dibuja un bullet point"""
        # Indicador naranja
        rect = fitz.Rect(MARGIN + 5, self.y + 4, MARGIN + 12, self.y + 11)
        self.page.draw_rect(rect, color=None, fill=COLOR_BG_ACCENT)

        self._draw_text_wrapped(
            text,
            x=MARGIN + 22,
            y=self.y,
            width=CONTENT_WIDTH - 30,
            fontsize=10,
            color=COLOR_PRIMARY,
            fontname="helv",
            line_height=1.5
        )

    def _draw_metric_card(self, x: float, y: float, label: str, value: str, desc: str):
        """Dibuja una tarjeta de métrica"""
        card_width = CONTENT_WIDTH / 2 - 15
        card_height = 110

        # Fondo de la tarjeta
        rect = fitz.Rect(x, y, x + card_width, y + card_height)
        self.page.draw_rect(rect, color=COLOR_BORDER, fill=COLOR_BG_LIGHT, width=1)

        # Valor grande en naranja
        cx = x + 15
        cy = y + 20
        self._draw_text(
            str(value),
            x=cx,
            y=cy,
            fontsize=32,
            color=COLOR_ACCENT,
            fontname="hebo",
            bold=True
        )

        # Etiqueta
        cy += 40
        self._draw_text(
            label,
            x=cx,
            y=cy,
            fontsize=11,
            color=COLOR_PRIMARY,
            fontname="hebo",
            bold=True
        )

        # Descripción
        cy += 18
        self._draw_text(
            desc,
            x=cx,
            y=cy,
            fontsize=9,
            color=COLOR_GRAY,
            fontname="helv"
        )

    # ═══════════════════════════════════════════════════════
    # Utilidades de extracción de texto
    # ═══════════════════════════════════════════════════════

    def _extract_key_sentences(self, text: str, max_sentences: int = 3) -> List[str]:
        """Extrae las oraciones más relevantes de un texto"""
        # Dividir por oraciones (., !, ?)
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)

        key_sentences = []
        for sent in sentences:
            clean = sent.strip()
            # Priorizar oraciones con palabras clave
            if len(clean) > 20 and not clean.startswith('#'):
                key_sentences.append(clean)
            if len(key_sentences) >= max_sentences:
                break

        return key_sentences

    def _extract_key_paragraphs(self, text: str, max_paragraphs: int = 6) -> List[str]:
        """Extrae párrafos clave del contenido"""
        paragraphs = text.split('\n\n')
        key_paragraphs = []

        for para in paragraphs:
            clean = para.strip()
            if not clean or clean.startswith('#'):
                continue
            if len(clean) > 30:
                key_paragraphs.append(clean)
            if len(key_paragraphs) >= max_paragraphs:
                break

        return key_paragraphs

    def _extract_metrics(self) -> List[tuple]:
        """Intenta extraer métricas del contenido markdown"""
        # Buscar patrones como "X agentes", "Y rondas", etc.
        import re

        metrics = []
        full_text = self.markdown

        # Patrones comunes
        patterns = [
            (r'(\d+)\s*agent', 'Agentes Simulados', 'individuos en la simulación'),
            (r'(\d+)\s*plataforma', 'Plataformas', 'Twitter y Reddit'),
            (r'(\d+)\s*ronda', 'Rondas de Simulación', 'iteraciones temporales'),
            (r'(\d+)\s*entidad', 'Entidades', 'nodos en el grafo'),
        ]

        for pattern, label, desc in patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                metrics.append((label, match.group(1), desc))

        return metrics

    def _clean_markdown(self, text: str) -> str:
        """Limpia formato markdown básico"""
        import re
        # Quitar bold/italic markers manteniendo el texto
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        text = re.sub(r'`(.+?)`', r'\1', text)
        text = re.sub(r'#{1,6}\s+', '', text)
        # Quitar > de citas
        text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)
        # Quitar links markdown
        text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
        return text.strip()


def generate_report_pdf(report_data: Dict[str, Any], output_path: str = None) -> str:
    """
    Función de conveniencia para generar un PDF de reporte.

    Args:
        report_data: Datos del reporte (de Report.to_dict())
        output_path: Ruta de salida (opcional, se genera una por defecto)

    Returns:
        Ruta del PDF generado
    """
    if not output_path:
        report_id = report_data.get('report_id', 'report')
        output_dir = os.path.join(Config.UPLOAD_FOLDER, 'reports', report_id)
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, 'executive_summary.pdf')

    generator = PDFReportGenerator(report_data)
    return generator.generate(output_path)
