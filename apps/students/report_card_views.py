from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
import urllib.request
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from .models import Student
from apps.exams.models import Exam, Marks


def get_photo(url, w=2.5*cm, h=3*cm):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        data = urllib.request.urlopen(req, timeout=5).read()
        return Image(BytesIO(data), width=w, height=h)
    except:
        return None


def get_grade_color(grade):
    if grade == 'A+': return colors.HexColor('#059669')
    if grade == 'A': return colors.HexColor('#0891b2')
    if grade == 'A-': return colors.HexColor('#0d9488')
    if grade == 'B': return colors.HexColor('#d97706')
    if grade == 'C': return colors.HexColor('#ea580c')
    if grade == 'D': return colors.HexColor('#dc2626')
    return colors.HexColor('#ef4444')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_report_card_pdf(request, student_pk):
    school = request.user.school
    exam_id = request.query_params.get('exam_id')

    try:
        student = Student.objects.get(pk=student_pk, school=school)
    except Student.DoesNotExist:
        from rest_framework.response import Response
        from rest_framework import status
        return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

    if exam_id:
        exams = Exam.objects.filter(id=exam_id, school=school)
    else:
        exams = Exam.objects.filter(school=school, class_name=student.class_name, is_published=True).order_by('-start_date')[:1]

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=1.5*cm, leftMargin=1.5*cm,
        topMargin=1.5*cm, bottomMargin=1.5*cm
    )

    elements = []

    title_style = ParagraphStyle('title', fontSize=18, fontName='Helvetica-Bold', alignment=TA_CENTER, textColor=colors.HexColor('#0a2540'), spaceAfter=2)
    sub_style = ParagraphStyle('sub', fontSize=10, fontName='Helvetica', alignment=TA_CENTER, textColor=colors.HexColor('#697386'), spaceAfter=2)
    small_style = ParagraphStyle('small', fontSize=8, fontName='Helvetica', alignment=TA_CENTER, textColor=colors.HexColor('#697386'), spaceAfter=12)
    label_style = ParagraphStyle('label', fontSize=8, fontName='Helvetica', textColor=colors.HexColor('#697386'))
    value_style = ParagraphStyle('value', fontSize=9, fontName='Helvetica-Bold', textColor=colors.HexColor('#0a2540'))
    section_style = ParagraphStyle('section', fontSize=11, fontName='Helvetica-Bold', textColor=colors.HexColor('#0a2540'), spaceBefore=12, spaceAfter=6)

    # Header
    elements.append(Paragraph(school.name.upper(), title_style))
    elements.append(Paragraph('Student Report Card', sub_style))
    elements.append(Paragraph('Session: 2026', small_style))
    elements.append(HRFlowable(width='100%', thickness=2, color=colors.HexColor('#635bff'), spaceAfter=12))

    # Student Info + Photo
    photo_cell = get_photo(student.photo) if student.photo else Paragraph('No\nPhoto', ParagraphStyle('np', fontSize=8, alignment=TA_CENTER, textColor=colors.HexColor('#697386')))

    info_data = [
        [Paragraph('Student Name', label_style), Paragraph(student.user.full_name or '-', value_style),
         Paragraph('Student ID', label_style), Paragraph(student.student_id or '-', value_style)],
        [Paragraph('Class', label_style), Paragraph(student.class_name.name if student.class_name else '-', value_style),
         Paragraph('Roll No', label_style), Paragraph(student.roll or '-', value_style)],
        [Paragraph('Father Name', label_style), Paragraph(student.father_name or '-', value_style),
         Paragraph('Mother Name', label_style), Paragraph(student.mother_name or '-', value_style)],
        [Paragraph('Gender', label_style), Paragraph(student.gender.capitalize() if student.gender else '-', value_style),
         Paragraph('Blood Group', label_style), Paragraph(student.blood_group or '-', value_style)],
        [Paragraph('Father Mobile', label_style), Paragraph(student.father_mobile or '-', value_style),
         Paragraph('Religion', label_style), Paragraph(student.religion or '-', value_style)],
    ]

    info_table = Table(info_data, colWidths=[3*cm, 5*cm, 3*cm, 5*cm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#0a2540')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e6ebf1')),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    # Student info + photo side by side
    top_table = Table([[info_table, photo_cell]], colWidths=[16*cm, 2.8*cm])
    top_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(top_table)
    elements.append(Spacer(1, 0.5*cm))

    # Marks per exam
    if not exams.exists():
        elements.append(Paragraph('No published exam results found.', ParagraphStyle('no', fontSize=10, alignment=TA_CENTER, textColor=colors.HexColor('#697386'))))
    else:
        for exam in exams:
            elements.append(Paragraph(f'Exam: {exam.name} ({exam.get_exam_type_display()})', section_style))
            elements.append(Paragraph(f'Date: {exam.start_date} to {exam.end_date}', ParagraphStyle('date', fontSize=8, textColor=colors.HexColor('#697386'), spaceAfter=8)))

            marks_qs = Marks.objects.filter(exam=exam, student=student).select_related('subject').order_by('subject__name')

            if not marks_qs.exists():
                elements.append(Paragraph('No marks recorded for this exam.', ParagraphStyle('no', fontSize=9, textColor=colors.HexColor('#697386'))))
                continue

            # Header
            bold_white = ParagraphStyle('bw', fontSize=9, fontName='Helvetica-Bold', textColor=colors.white, alignment=TA_CENTER)
            bold_white_left = ParagraphStyle('bwl', fontSize=9, fontName='Helvetica-Bold', textColor=colors.white)
            cell_center = ParagraphStyle('cc', fontSize=9, fontName='Helvetica', alignment=TA_CENTER, textColor=colors.HexColor('#0a2540'))
            cell_left = ParagraphStyle('cl', fontSize=9, fontName='Helvetica', textColor=colors.HexColor('#0a2540'))

            marks_data = [[
                Paragraph('Subject', bold_white_left),
                Paragraph('Total', bold_white),
                Paragraph('Obtained', bold_white),
                Paragraph('%', bold_white),
                Paragraph('Grade', bold_white),
                Paragraph('GP', bold_white),
                Paragraph('Status', bold_white),
            ]]

            total_obtained = 0
            total_full = 0

            for m in marks_qs:
                pct = round((float(m.marks_obtained) / float(m.total_marks)) * 100, 1) if not m.is_absent else 0
                grade_color = get_grade_color(m.grade)
                grade_para = ParagraphStyle('g', fontSize=9, fontName='Helvetica-Bold', alignment=TA_CENTER, textColor=grade_color)
                status = 'Absent' if m.is_absent else ('Pass' if pct >= 33 else 'Fail')
                status_color = colors.HexColor('#dc2626') if status in ['Fail', 'Absent'] else colors.HexColor('#059669')
                status_para = ParagraphStyle('s', fontSize=9, fontName='Helvetica-Bold', alignment=TA_CENTER, textColor=status_color)

                marks_data.append([
                    Paragraph(m.subject.name, cell_left),
                    Paragraph(str(int(m.total_marks)), cell_center),
                    Paragraph('Absent' if m.is_absent else str(float(m.marks_obtained)), cell_center),
                    Paragraph('-' if m.is_absent else str(pct) + '%', cell_center),
                    Paragraph(m.grade, grade_para),
                    Paragraph(str(m.grade_point), cell_center),
                    Paragraph(status, status_para),
                ])

                if not m.is_absent:
                    total_obtained += float(m.marks_obtained)
                    total_full += float(m.total_marks)

            # Total row
            total_pct = round((total_obtained / total_full) * 100, 1) if total_full > 0 else 0
            total_style = ParagraphStyle('ts', fontSize=9, fontName='Helvetica-Bold', alignment=TA_CENTER, textColor=colors.HexColor('#0a2540'))
            total_left = ParagraphStyle('tsl', fontSize=9, fontName='Helvetica-Bold', textColor=colors.HexColor('#0a2540'))
            marks_data.append([
                Paragraph('TOTAL', total_left),
                Paragraph(str(int(total_full)), total_style),
                Paragraph(str(round(total_obtained, 1)), total_style),
                Paragraph(str(total_pct) + '%', total_style),
                Paragraph('-', total_style),
                Paragraph('-', total_style),
                Paragraph('', total_style),
            ])

            col_widths = [5.5*cm, 2*cm, 2.5*cm, 2*cm, 2*cm, 1.5*cm, 2.8*cm]
            marks_table = Table(marks_data, colWidths=col_widths, repeatRows=1)
            marks_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#635bff')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f8fafc')]),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#eef2ff')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e6ebf1')),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(marks_table)

            # Summary box
            avg_gp = round(sum(float(m.grade_point) for m in marks_qs) / marks_qs.count(), 2) if marks_qs.count() > 0 else 0
            overall_grade = 'A+' if avg_gp >= 5 else 'A' if avg_gp >= 4 else 'A-' if avg_gp >= 3.5 else 'B' if avg_gp >= 3 else 'C' if avg_gp >= 2 else 'D' if avg_gp >= 1 else 'F'

            summary_data = [[
                Paragraph('Total Marks', label_style), Paragraph(str(int(total_full)), value_style),
                Paragraph('Obtained', label_style), Paragraph(str(round(total_obtained, 1)), value_style),
                Paragraph('Percentage', label_style), Paragraph(str(total_pct) + '%', value_style),
                Paragraph('GPA', label_style), Paragraph(str(avg_gp), value_style),
                Paragraph('Grade', label_style), Paragraph(overall_grade, ParagraphStyle('og', fontSize=12, fontName='Helvetica-Bold', textColor=get_grade_color(overall_grade))),
            ]]
            summary_table = Table(summary_data, colWidths=[2.2*cm, 2*cm, 2*cm, 2*cm, 2.5*cm, 2*cm, 1.5*cm, 1.5*cm, 1.8*cm, 1.3*cm])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#eef2ff')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e6ebf1')),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(Spacer(1, 0.3*cm))
            elements.append(summary_table)
            elements.append(Spacer(1, 0.5*cm))

    # Signature area
    elements.append(Spacer(1, 1*cm))
    elements.append(HRFlowable(width='100%', thickness=1, color=colors.HexColor('#e6ebf1'), spaceAfter=12))
    sig_data = [[
        Paragraph('___________________\nClass Teacher', ParagraphStyle('sig', fontSize=8, alignment=TA_CENTER, textColor=colors.HexColor('#697386'))),
        Paragraph('___________________\nHead Teacher', ParagraphStyle('sig', fontSize=8, alignment=TA_CENTER, textColor=colors.HexColor('#697386'))),
        Paragraph('___________________\nPrincipal', ParagraphStyle('sig', fontSize=8, alignment=TA_CENTER, textColor=colors.HexColor('#697386'))),
        Paragraph('___________________\nParent/Guardian', ParagraphStyle('sig', fontSize=8, alignment=TA_CENTER, textColor=colors.HexColor('#697386'))),
    ]]
    sig_table = Table(sig_data, colWidths=[4.7*cm, 4.7*cm, 4.7*cm, 4.7*cm])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(sig_table)

    # Footer
    def add_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 7)
        canvas.setFillColor(colors.HexColor('#697386'))
        canvas.drawString(1.5*cm, 0.8*cm, school.name + ' | Report Card 2026')
        canvas.drawRightString(A4[0] - 1.5*cm, 0.8*cm, 'Page ' + str(doc.page))
        canvas.restoreState()

    doc.build(elements, onFirstPage=add_footer, onLaterPages=add_footer)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report_card.pdf"'
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_report_cards_pdf(request):
    school = request.user.school
    exam_id = request.query_params.get('exam_id')
    class_id = request.query_params.get('class_id')

    students = Student.objects.filter(school=school, is_active=True).select_related('user', 'class_name')
    if class_id:
        students = students.filter(class_name_id=class_id)
    students = students.order_by('class_name__name', 'roll')

    if exam_id:
        exams_filter = Exam.objects.filter(id=exam_id, school=school)
    else:
        exams_filter = None

    buffer = BytesIO()
    from reportlab.pdfgen import canvas as pdf_canvas
    from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame

    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=1.5*cm, leftMargin=1.5*cm,
        topMargin=1.5*cm, bottomMargin=1.5*cm
    )

    all_elements = []
    title_style = ParagraphStyle('title', fontSize=16, fontName='Helvetica-Bold', alignment=TA_CENTER, textColor=colors.HexColor('#0a2540'), spaceAfter=4)
    sub_style = ParagraphStyle('sub', fontSize=9, fontName='Helvetica', alignment=TA_CENTER, textColor=colors.HexColor('#697386'), spaceAfter=16)

    for si, student in enumerate(students):
        if si > 0:
            from reportlab.platypus import PageBreak
            all_elements.append(PageBreak())

        all_elements.append(Paragraph(school.name.upper(), title_style))
        all_elements.append(Paragraph('Student Report Card — Session 2026', sub_style))
        all_elements.append(HRFlowable(width='100%', thickness=2, color=colors.HexColor('#635bff'), spaceAfter=12))

        label_style = ParagraphStyle('label', fontSize=8, fontName='Helvetica', textColor=colors.HexColor('#697386'))
        value_style = ParagraphStyle('value', fontSize=9, fontName='Helvetica-Bold', textColor=colors.HexColor('#0a2540'))

        info_data = [
            [Paragraph('Student Name', label_style), Paragraph(student.user.full_name or '-', value_style),
             Paragraph('Student ID', label_style), Paragraph(student.student_id or '-', value_style)],
            [Paragraph('Class', label_style), Paragraph(student.class_name.name if student.class_name else '-', value_style),
             Paragraph('Roll No', label_style), Paragraph(student.roll or '-', value_style)],
            [Paragraph('Father Name', label_style), Paragraph(student.father_name or '-', value_style),
             Paragraph('Mother Name', label_style), Paragraph(student.mother_name or '-', value_style)],
        ]
        info_table = Table(info_data, colWidths=[3*cm, 5*cm, 3*cm, 5*cm])
        info_table.setStyle(TableStyle([
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e6ebf1')),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        photo_cell = get_photo(student.photo) if student.photo else Paragraph('No\nPhoto', ParagraphStyle('np', fontSize=8, alignment=TA_CENTER, textColor=colors.HexColor('#697386')))
        top_table = Table([[info_table, photo_cell]], colWidths=[16*cm, 2.8*cm])
        top_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        all_elements.append(top_table)
        all_elements.append(Spacer(1, 0.4*cm))

        if exams_filter:
            exams = exams_filter
        else:
            exams = Exam.objects.filter(school=school, class_name=student.class_name, is_published=True).order_by('-start_date')[:1]

        section_style = ParagraphStyle('section', fontSize=10, fontName='Helvetica-Bold', textColor=colors.HexColor('#0a2540'), spaceBefore=8, spaceAfter=4)

        for exam in exams:
            all_elements.append(Paragraph(exam.name + ' (' + exam.get_exam_type_display() + ')', section_style))
            marks_qs = Marks.objects.filter(exam=exam, student=student).select_related('subject').order_by('subject__name')

            if not marks_qs.exists():
                all_elements.append(Paragraph('No marks recorded.', ParagraphStyle('no', fontSize=9, textColor=colors.HexColor('#697386'))))
                continue

            bold_white = ParagraphStyle('bw', fontSize=8, fontName='Helvetica-Bold', textColor=colors.white, alignment=TA_CENTER)
            bold_white_left = ParagraphStyle('bwl', fontSize=8, fontName='Helvetica-Bold', textColor=colors.white)
            cell_center = ParagraphStyle('cc', fontSize=8, alignment=TA_CENTER, textColor=colors.HexColor('#0a2540'))
            cell_left = ParagraphStyle('cl', fontSize=8, textColor=colors.HexColor('#0a2540'))

            marks_data = [[
                Paragraph('Subject', bold_white_left),
                Paragraph('Total', bold_white),
                Paragraph('Obtained', bold_white),
                Paragraph('%', bold_white),
                Paragraph('Grade', bold_white),
                Paragraph('GP', bold_white),
            ]]

            total_obtained = 0
            total_full = 0

            for m in marks_qs:
                pct = round((float(m.marks_obtained) / float(m.total_marks)) * 100, 1) if not m.is_absent else 0
                grade_color = get_grade_color(m.grade)
                grade_para = ParagraphStyle('g', fontSize=8, fontName='Helvetica-Bold', alignment=TA_CENTER, textColor=grade_color)
                marks_data.append([
                    Paragraph(m.subject.name, cell_left),
                    Paragraph(str(int(m.total_marks)), cell_center),
                    Paragraph('Absent' if m.is_absent else str(float(m.marks_obtained)), cell_center),
                    Paragraph('-' if m.is_absent else str(pct) + '%', cell_center),
                    Paragraph(m.grade, grade_para),
                    Paragraph(str(m.grade_point), cell_center),
                ])
                if not m.is_absent:
                    total_obtained += float(m.marks_obtained)
                    total_full += float(m.total_marks)

            total_pct = round((total_obtained / total_full) * 100, 1) if total_full > 0 else 0
            total_style = ParagraphStyle('ts', fontSize=8, fontName='Helvetica-Bold', alignment=TA_CENTER, textColor=colors.HexColor('#0a2540'))
            total_left = ParagraphStyle('tsl', fontSize=8, fontName='Helvetica-Bold', textColor=colors.HexColor('#0a2540'))
            marks_data.append([
                Paragraph('TOTAL', total_left),
                Paragraph(str(int(total_full)), total_style),
                Paragraph(str(round(total_obtained, 1)), total_style),
                Paragraph(str(total_pct) + '%', total_style),
                Paragraph('-', total_style),
                Paragraph('-', total_style),
            ])

            marks_table = Table(marks_data, colWidths=[6*cm, 2.5*cm, 3*cm, 2.5*cm, 2.5*cm, 2.3*cm], repeatRows=1)
            marks_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#635bff')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f8fafc')]),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#eef2ff')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e6ebf1')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            all_elements.append(marks_table)
            all_elements.append(Spacer(1, 0.3*cm))

        # Signature
        all_elements.append(Spacer(1, 0.8*cm))
        sig_data = [[
            Paragraph('___________________\nClass Teacher', ParagraphStyle('sig', fontSize=8, alignment=TA_CENTER, textColor=colors.HexColor('#697386'))),
            Paragraph('___________________\nHead Teacher', ParagraphStyle('sig', fontSize=8, alignment=TA_CENTER, textColor=colors.HexColor('#697386'))),
            Paragraph('___________________\nPrincipal', ParagraphStyle('sig', fontSize=8, alignment=TA_CENTER, textColor=colors.HexColor('#697386'))),
            Paragraph('___________________\nParent/Guardian', ParagraphStyle('sig', fontSize=8, alignment=TA_CENTER, textColor=colors.HexColor('#697386'))),
        ]]
        sig_table = Table(sig_data, colWidths=[4.7*cm, 4.7*cm, 4.7*cm, 4.7*cm])
        sig_table.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('TOPPADDING', (0, 0), (-1, -1), 4)]))
        all_elements.append(sig_table)

    def add_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 7)
        canvas.setFillColor(colors.HexColor('#697386'))
        canvas.drawString(1.5*cm, 0.8*cm, school.name + ' | Report Card 2026')
        canvas.drawRightString(A4[0] - 1.5*cm, 0.8*cm, 'Page ' + str(doc.page))
        canvas.restoreState()

    doc.build(all_elements, onFirstPage=add_footer, onLaterPages=add_footer)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="all_report_cards.pdf"'
    return response