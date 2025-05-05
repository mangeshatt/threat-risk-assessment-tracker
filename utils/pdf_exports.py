# Recreate sample_tra_entries.csv to ensure it exists after reset
from fpdf import FPDF


# PDF class
class PDFSummary(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "CISO Risk Summary Report", ln=True, align="C")
        self.ln(10)

    def section_title(self, title):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, title, ln=True)
        self.ln(4)

    def add_risk_table(self, data):
        self.set_font("Arial", "", 10)
        for index, row in data.iterrows():
            self.cell(0, 8, f"{row['TRA_ID']}: {row['Asset_Name']} | Score: {row['Score']} | Status: {row['Status']}", ln=True)



