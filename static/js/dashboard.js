/**
 * GULISTON 1-SON TEXNIKUM - DASHBOARD SCRIPTS
 */

document.addEventListener('DOMContentLoaded', function () {
    // Mobil sidebar tugmasi
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('admin-sidebar');

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function () {
            sidebar.classList.toggle('show');
        });
    }

    // Guruhlar davomati Donut chartlarini chizish
    document.querySelectorAll('.group-attendance-chart').forEach(canvas => {
        const rawData = canvas.getAttribute('data-chart-data');
        if (rawData) {
            try {
                const dataValues = JSON.parse(rawData); // [present, late, sick, absent]
                new Chart(canvas, {
                    type: 'doughnut',
                    data: {
                        labels: ['Darsda', 'Kechikkan', 'Kasallik', 'Boshqa sabab'],
                        datasets: [{
                            data: dataValues,
                            backgroundColor: [
                                '#10b981', // Yashil (Darsda)
                                '#f59e0b', // Sariq (Kechikkan)
                                '#0ea5e9', // Moviy (Kasallik)
                                '#ef4444'  // Qizil (Boshqa sabab)
                            ],
                            borderWidth: 2,
                            borderColor: '#ffffff',
                            hoverOffset: 4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        cutout: '72%',
                        plugins: {
                            legend: {
                                display: false
                            },
                            tooltip: {
                                callbacks: {
                                    label: function (context) {
                                        return ` ${context.label}: ${context.raw} nafar`;
                                    }
                                }
                            }
                        }
                    }
                });
            } catch (e) {
                console.error("Donut chartni chizishda xatolik:", e);
            }
        }
    });
});

// Davomat modalini ochish va o'quvchilarni yuklash (Kasal, Kechikkan, Sababsiz)
window.openAttendanceModal = function(event, groupId, statusCode) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }

    const modalEl = document.getElementById('attendanceStatusModal');
    if (!modalEl) return;

    const modal = new bootstrap.Modal(modalEl);
    modal.show();

    const titleEl = document.getElementById('modalStatusTitle');
    const subtitleEl = document.getElementById('modalStatusSubtitle');
    const bodyEl = document.getElementById('modalStatusBody');

    bodyEl.innerHTML = `
        <div class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Yuklanmoqda...</span>
            </div>
            <p class="text-muted small mt-2">Ma‘lumotlar yuklanmoqda...</p>
        </div>
    `;

    fetch(`/attendance/api/group-students-status/?group_id=${groupId || ''}&status=${statusCode}`)
        .then(res => res.json())
        .then(data => {
            titleEl.textContent = `${data.group_name}: ${data.status_label}`;
            subtitleEl.textContent = `Sana: ${data.date} | Jami: ${data.count} nafar talaba`;

            if (data.students && data.students.length > 0) {
                let rowsHtml = '';
                data.students.forEach((st, idx) => {
                    let badgeClass = 'bg-secondary';
                    if (st.status_code === 'PRESENT') badgeClass = 'bg-success';
                    else if (st.status_code === 'LATE') badgeClass = 'bg-warning text-dark';
                    else if (st.status_code === 'SICK') badgeClass = 'bg-info text-dark';
                    else if (st.status_code === 'ABSENT') badgeClass = 'bg-danger';

                    let spravkaHtml = '';
                    if (st.has_spravka && st.spravka_url) {
                        spravkaHtml = `
                            <a href="${st.spravka_url}" target="_blank" class="btn btn-sm btn-outline-primary fw-bold">
                                <i class="bi bi-file-earmark-medical-fill me-1"></i> Spravka (095/h)
                            </a>
                            <small class="d-block text-success mt-1"><i class="bi bi-check-circle-fill"></i> ${st.spravka_status} (${st.spravka_dates})</small>
                        `;
                    } else if (st.status_code === 'SICK') {
                        spravkaHtml = `<span class="badge bg-warning-subtle text-warning border border-warning-subtle"><i class="bi bi-clock-history"></i> Spravka kutilmoqda</span>`;
                    } else if (st.status_code === 'ABSENT') {
                        spravkaHtml = `<span class="badge bg-danger-subtle text-danger border border-danger-subtle"><i class="bi bi-x-circle-fill"></i> Spravka yo‘q (Sababsiz)</span>`;
                    } else {
                        spravkaHtml = `<span class="text-muted small">—</span>`;
                    }

                    rowsHtml += `
                        <tr>
                            <td class="text-center fw-bold text-muted">${idx + 1}</td>
                            <td>
                                <strong class="text-dark d-block">${st.name}</strong>
                                <small class="text-muted">ID: ${st.student_id_number} ${st.group_name ? ' | ' + st.group_name : ''}</small>
                            </td>
                            <td class="text-center">
                                <span class="badge ${badgeClass} px-2 py-1">${st.status}</span>
                            </td>
                            <td>
                                ${spravkaHtml}
                            </td>
                        </tr>
                    `;
                });

                bodyEl.innerHTML = `
                    <div class="table-responsive">
                        <table class="table table-hover align-middle mb-0">
                            <thead class="table-light small text-muted">
                                <tr>
                                    <th class="text-center" style="width: 8%;">№</th>
                                    <th>O‘quvchining F.I.Sh</th>
                                    <th class="text-center" style="width: 25%;">Davomat holati</th>
                                    <th style="width: 35%;">Tibbiy Spravka / Hujjat</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${rowsHtml}
                            </tbody>
                        </table>
                    </div>
                `;
            } else {
                bodyEl.innerHTML = `
                    <div class="text-center py-5 text-muted">
                        <i class="bi bi-person-check fs-1 text-success d-block mb-2"></i>
                        Ushbu toifa bo‘yicha hech qanday o‘quvchi topilmadi.
                    </div>
                `;
            }
        })
        .catch(err => {
            console.error(err);
            bodyEl.innerHTML = `
                <div class="alert alert-danger m-3">
                    Ma‘lumotlarni yuklashda xatolik yuz berdi.
                </div>
            `;
        });
};
