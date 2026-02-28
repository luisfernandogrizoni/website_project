document.addEventListener('DOMContentLoaded', function() {

    const initDT = (selector) => {
        if ($(selector).length && !$.fn.DataTable.isDataTable(selector)) {
            $(selector).DataTable({
                language: { url: 'https://cdn.datatables.net/plug-ins/1.13.6/i18n/pt-BR.json' },
                responsive: true,
                pageLength: 10,
                destroy: true
            });
        }
    };

    initDT('#tabelaAtivos');
    initDT('#tabelaInativos');
});

function switchTab(tab) {
    document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

    if(tab === 'ativos') {
        document.querySelector('.nav-tab:nth-child(1)').classList.add('active');
        document.getElementById('tab-ativos').classList.add('active');
    } else {
        document.querySelector('.nav-tab:nth-child(2)').classList.add('active');
        document.getElementById('tab-inativos').classList.add('active');
    }
}
