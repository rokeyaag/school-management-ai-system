from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from io import BytesIO
import urllib.request
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from .models import Student


def get_image_from_url(url, width=2*cm, height=2.5*cm):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        data = urllib.request.urlopen(req, timeout=5).read()
        img = Image(BytesIO(data), width=width, height=height)
        return img
    except:
        return Paragraph("No Photo", ParagraphStyle('np', fontSize=6, alignment=TA_CENTER))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_list_pdf(request):
    school = request.user.school
    if not school:
        from apps.tenants.models import School
        school = School.objects.filter(name="Dhaka Model School").first()
    class_id = request.query_params.get('class_id')
    students = Student.objects.filter(school=school, is_active=True).select_related('user', 'class_name')
    if class_id:
        students = students.filter(class_name_id=class_id)
    students = students.order_by('class_name__name', 'roll')

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=1.5*cm, leftMargin=1.5*cm,
        topMargin=2*cm, bottomMargin=1.5*cm
    )

    elements = []

    header_style = ParagraphStyle('header', fontSize=16, fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=4)
    sub_style = ParagraphStyle('sub', fontSize=10, fontName='Helvetica', alignment=TA_CENTER, spaceAfter=2)
    small_style = ParagraphStyle('small', fontSize=8, fontName='Helvetica', alignment=TA_CENTER, spaceAfter=12)
    class_header_style = ParagraphStyle('ch', fontSize=11, fontName='Helvetica-Bold', spaceAfter=6, spaceBefore=12, textColor=colors.HexColor('#1E3A5F'))
    header_cell = ParagraphStyle('hc', fontSize=8, fontName='Helvetica-Bold', leading=10, textColor=colors.white, alignment=TA_CENTER)
    cell_style = ParagraphStyle('cell', fontSize=8, fontName='Helvetica', leading=10, textColor=colors.HexColor('#1E293B'))

    elements.append(Paragraph(school.name.upper(), header_style))
    elements.append(Paragraph("Student List", sub_style))
    elements.append(Paragraph("Session: 2026 | Total Students: " + str(students.count()), small_style))
    elements.append(Spacer(1, 0.3*cm))

    students_list = list(students)
    class_groups = {}
    for s in students_list:
        class_name = s.class_name.name if s.class_name else 'No Class'
        if class_name not in class_groups:
            class_groups[class_name] = []
        class_groups[class_name].append(s)

    for class_name, class_students in class_groups.items():
        elements.append(Paragraph("Class: " + class_name, class_header_style))

        table_data = [[
            Paragraph('Photo', header_cell),
            Paragraph('Student ID', header_cell),
            Paragraph('Name', header_cell),
            Paragraph('Roll', header_cell),
            Paragraph('Gender', header_cell),
            Paragraph('Father Name', header_cell),
            Paragraph('Father Mobile', header_cell),
            Paragraph('Mother Name', header_cell),
        ]]

        for s in class_students:
            photo_cell = get_image_from_url(s.photo) if s.photo else Paragraph('No Photo', ParagraphStyle('np', fontSize=6, alignment=TA_CENTER))
            table_data.append([
                photo_cell,
                Paragraph(s.student_id or '-', cell_style),
                Paragraph(s.user.full_name or '-', cell_style),
                Paragraph(s.roll or '-', cell_style),
                Paragraph(s.gender.capitalize() if s.gender else '-', cell_style),
                Paragraph(s.father_name or '-', cell_style),
                Paragraph(s.father_mobile or '-', cell_style),
                Paragraph(s.mother_name or '-', cell_style),
            ])

        col_widths = [2.2*cm, 2.5*cm, 3.5*cm, 1.2*cm, 1.5*cm, 3.2*cm, 2.5*cm, 3.2*cm]
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563EB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#EFF6FF')]),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#1E293B')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BFDBFE')),
            ('ROWHEIGHT', (0, 1), (-1, -1), 2.8*cm),
            ('ROWHEIGHT', (0, 0), (-1, 0), 0.8*cm),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 0.5*cm))

    def add_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 7)
        canvas.setFillColor(colors.grey)
        canvas.drawString(1.5*cm, 1*cm, school.name + " | Generated by School Management System")
        canvas.drawRightString(A4[0] - 1.5*cm, 1*cm, "Page " + str(doc.page))
        canvas.restoreState()

    doc.build(elements, onFirstPage=add_footer, onLaterPages=add_footer)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="student_list.pdf"'
    return response