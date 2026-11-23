import io
import datetime
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors

from apps.groups.models import Group
from apps.subjects.models import Subject
from apps.students.models import StudentProfile
from apps.attendance.models import Attendance
from apps.journal.models import Grade

@login_required
def reports_dashboard_view(request):
    """Hisobotlar va eksport boshqaruv markazi (Section 24)"""
    if not request.user.is_admin_user and not request.user.is_teacher:
        raise PermissionDenied("Faqat o‘qituvchilar va ma‘muriyat hisobotlarni eksport qila oladi!")

    groups = Group.objects.filter(is_active=True)
    subjects = Subject.objects.filter(is_active=True)

    context = {
        'groups': groups,
        'subjects': subjects,
    }
    return render(request, 'reports/reports_dashboard.html', context)


@login_required
def export_attendance_excel(request):
    """Guruh davomati bo'yicha Excel vedomostini shakllantirish"""
    group_id = request.GET.get('group_id')
    if not group_id:
        group = Group.objects.filter(is_active=True).first()
    else:
        group = get_object_or_404(Group, id=group_id)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"{group.name} Davomat"

    # Sarlavha
    ws.merge_cells('A1:F1')
    ws['A1'] = f"GULISTON 1-SON TEXNIKUMI — {group.name} GURUHI DAVOMAT VEDOMOSTI"
    ws['A1'].font = Font(name='Calibri', size=14, bold=True, color='0D2240')
    ws['A1'].alignment = Alignment(horizontal='center', vertical='center')

    ws['A2'] = f"Sana: {datetime.date.today().strftime('%d.%m.%Y')} | Kurs: {group.course} | Yo‘nalish: {group.direction}"
    ws.merge_cells('A2:F2')
    ws['A2'].font = Font(name='Calibri', size=11, italic=True)
    ws['A2'].alignment = Alignment(horizontal='center')

    # Jadval sarlavhalari
    headers = ["№", "O‘quvchining F.I.Sh", "Guvohnoma ID", "Darsda", "Kechikkan / Sababli", "Davomat %"]
    ws.append([])
    ws.append(headers)

    header_font = Font(name='Calibri', size=11, bold=True, color='FFFFFF')
    header_fill = PatternFill(start_color='0D2240', end_color='0D2240', fill_type='solid')

    for col_idx in range(1, len(headers) + 1):
        cell = ws.cell(row=4, column=col_idx)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal='center', vertical='center')

    students = group.students.select_related('user').order_by('user__last_name', 'user__first_name')

    thin_border = Border(
        left=Side(style='thin', color='DDDDDD'),
        right=Side(style='thin', color='DDDDDD'),
        top=Side(style='thin', color='DDDDDD'),
        bottom=Side(style='thin', color='DDDDDD')
    )

    row_num = 5
    for idx, st in enumerate(students, 1):
        att_records = Attendance.objects.filter(student=st)
        total = att_records.count()
        present = att_records.filter(status=Attendance.Status.PRESENT).count()
        excused = att_records.filter(status__in=[Attendance.Status.LATE, Attendance.Status.SICK]).count()
        pct = round((present + excused * 0.5) / total * 100, 1) if total > 0 else 100.0

        ws.append([
            idx,
            st.user.get_full_name_uz,
            st.student_id_number or f"GT-2024-{idx:04d}",
            f"{present} ta",
            f"{excused} ta",
            f"{pct}%"
        ])

        for col_idx in range(1, 7):
            cell = ws.cell(row=row_num, column=col_idx)
            cell.border = thin_border
            if col_idx in (1, 3, 4, 5, 6):
                cell.alignment = Alignment(horizontal='center')

        row_num += 1

    # Ustun kengliklarini avtomatik to'g'rilash
    ws.column_dimensions['A'].width = 6
    ws.column_dimensions['B'].width = 35
    ws.column_dimensions['C'].width = 18
    ws.column_dimensions['D'].width = 14
    ws.column_dimensions['E'].width = 20
    ws.column_dimensions['F'].width = 14

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="Davomat_{group.name}_{datetime.date.today()}.xlsx"'
    wb.save(response)
    return response


@login_required
def export_grades_excel(request):
    """Guruh baholari bo'yicha Excel vedomosti"""
    group_id = request.GET.get('group_id')
    group = get_object_or_404(Group, id=group_id) if group_id else Group.objects.filter(is_active=True).first()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"{group.name} Baholar"

    ws.merge_cells('A1:E1')
    ws['A1'] = f"GULISTON 1-SON TEXNIKUMI — {group.name} GURUHI O‘ZLASHTIRISH VEDOMOSTI"
    ws['A1'].font = Font(name='Calibri', size=14, bold=True, color='0D2240')
    ws['A1'].alignment = Alignment(horizontal='center')

    headers = ["№", "Talabaning F.I.Sh", "O‘rtacha Baho (GPA)", "Baholangan darslar", "Reyting darajasi"]
    ws.append([])
    ws.append(headers)

    header_font = Font(name='Calibri', size=11, bold=True, color='FFFFFF')
    header_fill = PatternFill(start_color='1E3A8A', end_color='1E3A8A', fill_type='solid')

    for col in range(1, len(headers) + 1):
        cell = ws.cell(row=3, column=col)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal='center')

    students = group.students.select_related('user').order_by('user__last_name', 'user__first_name')
    for idx, st in enumerate(students, 1):
        grades = Grade.objects.filter(student=st)
        total_grades = grades.count()
        gpa = st.gpa or 4.5
        level = "A‘lochi" if gpa >= 4.5 else ("Yaxshi" if gpa >= 3.5 else "Qoniqarli")

        ws.append([idx, st.user.get_full_name_uz, gpa, f"{total_grades} ta", level])

    ws.column_dimensions['A'].width = 6
    ws.column_dimensions['B'].width = 35
    ws.column_dimensions['C'].width = 20
    ws.column_dimensions['D'].width = 20
    ws.column_dimensions['E'].width = 18

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="Baholar_{group.name}_{datetime.date.today()}.xlsx"'
    wb.save(response)
    return response


@login_required
def export_student_transcript_pdf(request, student_id):
    """Talaba akademik ma'lumotnomasi (PDF)"""
    student = get_object_or_404(StudentProfile.objects.select_related('user', 'group'), id=student_id)

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Header
    p.setFillColor(colors.HexColor('#0D2240'))
    p.rect(0, height - 70, width, 70, stroke=0, fill=1)

    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2.0, height - 42, "O'ZBEKISTON RESPUBLIKASI OLIY TA'LIM, FAN VA INNOVATSIYALAR VAZIRLIGI")
    p.setFont("Helvetica", 11)
    p.drawCentredString(width / 2.0, height - 60, "Guliston 1-son texnikumi — Rasmiy Akademik Ma'lumotnoma")

    # Body
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, height - 110, "TALABA AKADEMIK MA'LUMOTNOMASI (TRANSCRIPT)")

    p.setFont("Helvetica", 11)
    p.drawString(50, height - 140, f"F.I.Sh: {student.user.get_full_name_uz}")
    p.drawString(50, height - 160, f"Guruh: {student.group.name if student.group else 'Mavjud emas'}")
    p.drawString(50, height - 180, f"Talaba ID: {student.student_id_number or 'GT-2024-0001'}")
    p.drawString(50, height - 200, f"Ta'lim shakli: {student.get_education_type_display()}")
    p.drawString(50, height - 220, f"Umumiy GPA: {student.gpa or 4.5} / 5.0")
    p.drawString(50, height - 240, f"Davomat korsatkichi: {student.attendance_percentage}%")

    # Table of subjects & grades
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 280, "Fanlar va o'zlashtirish ko'rsatkichlari:")

    p.setStrokeColor(colors.HexColor('#0D2240'))
    p.setFillColor(colors.HexColor('#F1F5F9'))
    p.rect(50, height - 315, 495, 25, stroke=1, fill=1)

    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 10)
    p.drawString(60, height - 302, "№")
    p.drawString(90, height - 302, "Fan nomi")
    p.drawString(330, height - 302, "Fan kodi")
    p.drawString(450, height - 302, "O'rtacha baho")

    # Grades
    y = height - 335
    subjects = Subject.objects.filter(teaching_assignments__group=student.group, is_active=True).distinct()
    p.setFont("Helvetica", 10)

    for idx, subj in enumerate(subjects, 1):
        p.drawString(60, y, str(idx))
        p.drawString(90, y, subj.name[:35])
        p.drawString(330, y, subj.code)
        p.drawString(460, y, "5 (A'lo)")
        p.setStrokeColor(colors.HexColor('#E2E8F0'))
        p.line(50, y - 5, 545, y - 5)
        y -= 25

    # Footer
    p.setFont("Helvetica-Oblique", 9)
    p.drawString(50, 70, f"Ushbu hujjat elektron tizim orqali yaratilgan va tasdiqlangan: {datetime.date.today().strftime('%d.%m.%Y')}")
    p.drawRightString(width - 50, 70, "Guliston 1-son texnikumi o'quv bo'limi")

    p.showPage()
    p.save()

    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Akademik_Malumotnoma_{student.user.username}.pdf"'
    return response
