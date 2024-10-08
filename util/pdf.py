# Since the issue is related to encoding, I will switch the PDF generation to use a Unicode-supported font.
from fpdf import FPDF

# Create a PDF document with UTF-8 support
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'News Report Summary', 0, 1, 'C')
        self.ln(10)

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.multi_cell(0, 10, f'标题: {title}')
        self.ln(5)

    def chapter_body(self, date, duration, content, link):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 10, f'日期: {date}\n时长: {duration}')
        self.multi_cell(0, 10, f'内容: {content}')
        self.multi_cell(0, 10, f'链接: {link}')
        self.ln()

    def add_news_item(self, title, date, duration, content, link):
        self.add_page()
        self.chapter_title(title)
        self.chapter_body(date, duration, content, link)

# Create a PDF and fill it with the content from the data
pdf = PDF()
pdf.set_left_margin(10)
pdf.set_right_margin(10)
pdf.set_auto_page_break(auto=True, margin=15)

# Add Unicode-compliant font for handling Chinese text
pdf.add_font('DejaVu', '', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', uni=True)
pdf.set_font('DejaVu', '', 12)

for _, row in data.iterrows():
    title = row['title']
    date = row['date']
    duration = row['duration']
    content = row['content']
    link = row['link']
    pdf.add_news_item(title, date, duration, content, link)

# Save the PDF
pdf_output_path = "/mnt/data/news_summary_utf8.pdf"
pdf.output(pdf_output_path)

pdf_output_path