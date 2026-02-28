document.addEventListener('DOMContentLoaded', function() {
    const calendarEl = document.getElementById('calendar');

    const apiUrl = calendarEl.dataset.urlApi;
    const saveUrl = calendarEl.dataset.urlSalvar;

    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        locale: 'pt-br',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        events: apiUrl,
        editable: true,
        selectable: true,

        height: '100%',
        contentHeight: 'auto',

        dateClick: function (info) {
            abrirModalAgendamento(info.dateStr);
        },

        eventClick: function (info) {
            alert('Evento: ' + info.event.title);
        }
    });

    calendar.render();

    let resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(function (){
            calendar.updateSize();
            console.log('Calendário redimensionado!');
        }, 200);
    })


    const form = document.getElementById('formAgendamento');
    if (form) {
        form.addEventListener('submit', async function (e) {
            e.preventDefault();
            App.mostrarLoading('A guardar Agendamento...');

            try {
                const calendarDiv = document.getElementById('calendar'); // Bug corrigido aqui!
                const urlSalvar = calendarDiv.getAttribute('data-url-salvar');

                if (!urlSalvar) throw new Error('URL de salvamento não encontrada!');

                const formData = new FormData(form);

                await App.api.request(urlSalvar, 'POST', FormData, true);

                App.fecharAlerta();
                App.mostrarSucesso('Agendamento salvo com sucesso!');
                window.fecharModal();
                form.reset();

                calendar.refetchEvents();

            } catch (error) {
                console.error(error);
                App.fecharAlerta();
                App.mostrarErro(`Erro ao guardar: ${error.message}`);
            }
        });
    }

    function abrirModalAgendamento(data) {
        const modal = document.getElementById('modalAgendamento');
        const inputData = document.querySelector('input[name="data_inicio"]');

        if (inputData && data) {
            inputData.value = data;
        }

        modal.style.display = 'flex';
        setTimeout(() => modal.classList.add('show'), 10);
    }

    window.fecharModal = function () {
        const modal = document.getElementById('modalAgendamento');
        modal.classList.remove('show');
        setTimeout(() => modal.style.display = 'none', 300);
    }
})