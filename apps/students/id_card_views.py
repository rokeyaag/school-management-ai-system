from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.graphics.shapes import Drawing, Rect, String
from io import BytesIO
import urllib.request
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from .models import Student


CARD_W = 8.56 * cm
CARD_H = 5.4 * cm


def get_photo(url, w=2.2*cm, h=2.6*cm):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        data = urllib.request.urlopen(req, timeout=5).read()
        return Image(BytesIO(data), width=w, height=h)
    except:
        return None


def make_id_card(canvas, school, student, x, y):
    c = canvas

    # Card background
    c.setFillColor(colors.HexColor('#1a1428'))
    c.roundRect(x, y, CARD_W, CARD_H, 6*mm, fill=1, stroke=0)

    # Top accent bar
    c.setFillColor(colors.HexColor('#7c3aed'))
    c.roundRect(x, y + CARD_H - 1.4*cm, CARD_W, 1.4*cm, 6*mm, fill=1, stroke=0)
    c.setFillColor(colors.HexColor('#7c3aed'))
    c.rect(x, y + CARD_H - 1.4*cm, CARD_W, 0.7*cm, fill=1, stroke=0)

    # Bottom accent
    c.setFillColor(colors.HexColor('#4f46e5'))
    c.rect(x, y, CARD_W, 0.35*cm, fill=1, stroke=0)
    c.setFillColor(colors.HexColor('#4f46e5'))
    c.roundRect(x, y, CARD_W, 0.35*cm, 2*mm, fill=1, stroke=0)

    # School name
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 8)
    school_name = school.name.upper() if school else 'SCHOOL NAME'
    c.drawCentredString(x + CARD_W/2, y + CARD_H - 0.85*cm, school_name)

    c.setFont('Helvetica', 6)
    c.setFillColor(colors.HexColor('#c4b5fd'))
    c.drawCentredString(x + CARD_W/2, y + CARD_H - 1.15*cm, 'STUDENT IDENTITY CARD')

    # Photo area
    photo_x = x + 0.4*cm
    photo_y = y + 1.0*cm
    photo_w = 2.2*cm
    photo_h = 2.6*cm

    # Photo border
    c.setFillColor(colors.HexColor('#2d1f4e'))
    c.setStrokeColor(colors.HexColor('#7c3aed'))
    c.setLineWidth(1.5)
    c.roundRect(photo_x - 0.1*cm, photo_y - 0.1*cm, photo_w + 0.2*cm, photo_h + 0.2*cm, 3*mm, fill=1, stroke=1)

    if student.photo:
        img = get_photo(student.photo, photo_w, photo_h)
        if img:
            img.drawOn(c, photo_x, photo_y)
        else:
            c.setFillColor(colors.HexColor('#3d2b6e'))
            c.roundRect(photo_x, photo_y, photo_w, photo_h, 2*mm, fill=1, stroke=0)
            c.setFillColor(colors.HexColor('#a78bfa'))
            c.setFont('Helvetica-Bold', 20)
            initial = (student.user.full_name or 'S')[0].upper()
            c.drawCentredString(photo_x + photo_w/2, photo_y + photo_h/2 - 7, initial)
    else:
        c.setFillColor(colors.HexColor('#3d2b6e'))
        c.roundRect(photo_x, photo_y, photo_w, photo_h, 2*mm, fill=1, stroke=0)
        c.setFillColor(colors.HexColor('#a78bfa'))
        c.setFont('Helvetica-Bold', 20)
        initial = (student.user.full_name or 'S')[0].upper()
        c.drawCentredString(photo_x + photo_w/2, photo_y + photo_h/2 - 7, initial)

    # Info area
    info_x = x + 3.0*cm
    info_y = y + CARD_H - 1.7*cm
    line_h = 0.42*cm

    # Student name
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 9)
    name = student.user.full_name or ''
    if len(name) > 22:
        name = name[:22] + '...'
    c.drawString(info_x, info_y, name)

    # Divider line
    c.setStrokeColor(colors.HexColor('#7c3aed'))
    c.setLineWidth(0.5)
    c.line(info_x, info_y - 0.12*cm, x + CARD_W - 0.4*cm, info_y - 0.12*cm)

    # Fields
    fields = [
        ('ID', student.student_id or '-'),
        ('Class', student.class_name.name if student.class_name else '-'),
        ('Roll', student.roll or '-'),
        ('Blood', student.blood_group or '-'),
        ('Father', (student.father_name or '-')[:18]),
        ('Mobile', student.father_mobile or '-'),
    ]

    for j, (label, value) in enumerate(fields):
        fy = info_y - (j + 1) * line_h - 0.1*cm
        if fy < y + 0.5*cm:
            break
        c.setFont('Helvetica', 6)
        c.setFillColor(colors.HexColor('#a78bfa'))
        c.drawString(info_x, fy, label + ':')
        c.setFont('Helvetica-Bold', 6.5)
        c.setFillColor(colors.HexColor('#e2e8f0'))
        c.drawString(info_x + 1.3*cm, fy, str(value))

    # Bottom bar text
    c.setFont('Helvetica', 5.5)
    c.setFillColor(colors.HexColor('#c4b5fd'))
    c.drawCentredString(x + CARD_W/2, y + 0.1*cm, 'If found, please return to school | Session: 2026')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_id_cards_pdf(request):
    school = request.user.school
    if not school:
        from apps.tenants.models import School
        school = School.objects.filter(name="Dhaka Model School").first()
    class_id = request.query_params.get('class_id')
    student_id = request.query_params.get('student_id')

    students = Student.objects.filter(school=school, is_active=True).select_related('user', 'class_name')
    if class_id:
        students = students.filter(class_name_id=class_id)
    if student_id:
        students = students.filter(id=student_id)
    students = students.order_by('class_name__name', 'roll')

    buffer = BytesIO()
    from reportlab.pdfgen import canvas as pdf_canvas
    c = pdf_canvas.Canvas(buffer, pagesize=A4)

    PAGE_W, PAGE_H = A4
    MARGIN = 1.2*cm
    GAP_X = 0.5*cm
    GAP_Y = 0.6*cm
    COLS = 2
    ROWS = 4

    cards_per_page = COLS * ROWS
    total = students.count()

    start_x = [MARGIN, MARGIN + CARD_W + GAP_X]
    start_y_base = PAGE_H - MARGIN - CARD_H

    for idx, student in enumerate(students):
        page_idx = idx % cards_per_page
        if page_idx == 0 and idx > 0:
            c.showPage()

        col = page_idx % COLS
        row = page_idx // COLS
        x = start_x[col]
        y = start_y_base - row * (CARD_H + GAP_Y)

        make_id_card(c, school, student, x, y)

    c.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="student_id_cards.pdf"'
    return response