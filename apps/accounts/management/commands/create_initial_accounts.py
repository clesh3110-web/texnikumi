import os

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.accounts.models import User
from apps.teachers.models import TeacherProfile
from apps.students.models import StudentProfile


class Command(BaseCommand):
    help = "Toza bazada har bir rol uchun bittadan boshlang'ich hisob yaratadi."

    def handle(self, *args, **options):
        if User.objects.exists():
            raise CommandError(
                "Bazadagi foydalanuvchilar mavjud. Xavfsizlik uchun buyruq hech kimning "
                "parolini o'zgartirmaydi va mavjud hisoblarni o'chirmaydi."
            )

        accounts = [
            {
                "username": "direktor",
                "first_name": "Doniyor",
                "last_name": "Atabayev",
                "role": User.Role.SUPERADMIN,
                "env": "INITIAL_SUPERADMIN_PASSWORD",
            },
            {
                "username": "admin",
                "first_name": "Zulfiya",
                "last_name": "Nazarova",
                "role": User.Role.ADMIN,
                "env": "INITIAL_ADMIN_PASSWORD",
            },
            {
                "username": "sevinch_axmedova",
                "first_name": "Sevinch",
                "last_name": "Axmedova",
                "role": User.Role.TEACHER,
                "env": "INITIAL_TEACHER_PASSWORD",
            },
            {
                "username": "talaba",
                "first_name": "Jasur",
                "last_name": "Toshmatov",
                "role": User.Role.STUDENT,
                "env": "INITIAL_STUDENT_PASSWORD",
            },
        ]

        missing = [item["env"] for item in accounts if not os.getenv(item["env"])]
        if missing:
            raise CommandError(
                "Quyidagi .env qiymatlari kiritilmagan: " + ", ".join(missing)
            )

        with transaction.atomic():
            for item in accounts:
                password = os.environ[item["env"]]
                if len(password) < 12:
                    raise CommandError(
                        f"{item['env']} kamida 12 belgidan iborat bo'lishi kerak."
                    )
                user = User(
                    username=item["username"],
                    first_name=item["first_name"],
                    last_name=item["last_name"],
                    role=item["role"],
                    is_active=True,
                    is_verified=True,
                )
                user.set_password(password)
                user.save()
                if item["role"] == User.Role.TEACHER:
                    TeacherProfile.objects.create(user=user)
                elif item["role"] == User.Role.STUDENT:
                    StudentProfile.objects.create(user=user)

        self.stdout.write(self.style.SUCCESS(
            "4 ta boshlang'ich hisob yaratildi: direktor, admin, sevinch_axmedova, talaba."
        ))
        self.stdout.write(
            "Parollarni .env dan olib tashlang va faylni xavfsiz saqlang."
        )
