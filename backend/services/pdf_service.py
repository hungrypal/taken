"""Professional PDF report rendering for persisted predictions."""

from io import BytesIO


class PdfService:
    """Build an in-memory PDF so reports can be streamed without temp files."""

    def build_prediction_report(self, *, farmer_name: str, farm_location: str, prediction) -> bytes:
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
        except ImportError as exc:
            raise RuntimeError("PDF support is unavailable; install reportlab.") from exc

        stream = BytesIO()
        document = SimpleDocTemplate(stream, pagesize=A4, title="TerraScore Farm Report")
        styles = getSampleStyleSheet()
        climate = prediction.climate or {}
        rows = [
            ["Farmer", farmer_name], ["Farm location", farm_location],
            ["Prediction date", str(prediction.prediction_date)], ["NDVI", f"{prediction.ndvi:.3f}"],
            ["LST", f"{prediction.lst:.2f} °C"], ["Climate", f"Rainfall: {climate.get('rainfall', 'N/A')}; Temperature: {climate.get('temperature', 'N/A')}; Humidity: {climate.get('humidity', 'N/A')}"],
            ["Drought prediction", f"{prediction.drought_index:.2f}"], ["Credit score", f"{prediction.credit_score:.2f}/100"],
            ["Risk level", prediction.risk_classification],
        ]
        elements = [Paragraph("TerraScore Agricultural Credit Report", styles["Title"]), Spacer(1, 14)]
        table = Table(rows, colWidths=[145, 340])
        table.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E8F3E8")), ("GRID", (0, 0), (-1, -1), 0.4, colors.grey), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("PADDING", (0, 0), (-1, -1), 7)]))
        elements.extend([table, Spacer(1, 14), Paragraph("Recommendations", styles["Heading2"])])
        for item in prediction.recommendations or []:
            elements.append(Paragraph(f"<b>{item.get('category', 'Advice').title()}:</b> {item.get('message', '')}", styles["BodyText"]))
            elements.append(Spacer(1, 5))
        document.build(elements)
        return stream.getvalue()


pdf_service = PdfService()
