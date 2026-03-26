document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('prontuarioForm');

    if (form) {
        form.addEventListener('submit', async function (event) {
            event.preventDefault();
            App.mostrarLoading('Salvando Prontuário...');

            try {
                const formData = new FormData(form);
                const response = await fetch(window.location.href, {
                    method: 'POST',
                    body: formData
                });

                if (response.redirected) {
                    window.location.href = response.url;
                    return;
                }

                if (!response.ok) {
                    throw new Error('Erro HTTP: ${response.status}');
                }

                const html = await response.text();
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const erros = doc.querySelector('.error-message');

                if (erros) {
                    App.fecharAlerta()
                    const novoConteudo = doc.querySelector('main') || document.body;
                    const conteudoAtual = document.querySelector('main') || document.body;

                    conteudoAtual.innerHTML = novoConteudo.innerHTML;
                    App.mostrarErro('Verifique os campos obrigatórios destacados.');
                    if(App.initMasks) App.initMasks();

                } else {
                    const triggers = doc.querySelectorAll('.message-trigger');
                    if (triggers.length > 0) {
                        document.documentElement.innerHTML = html;
                    } else {
                        App.mostrarSucesso('Salvo com sucesso!', true);
                    }
                }
            } catch (error) {
                console.error('Erro Crítico no Envio: ', error);
                App.fecharAlerta();
                App.mostrarErro('Falha de comunicação. Tente novamente ou contate o suporte.');
            }
        });
    }

    const estadoCivilSelect = document.getElementById('estado_civil');
    const conjugeContainer = document.getElementById('conjuge_container');

    function toggleConjugeField() {
        if (!estadoCivilSelect || !conjugeContainer) return;

        const valor = estadoCivilSelect.value.toLowerCase().trim();
        console.log('Estado Civil Selecionado (Debug):', valor);
        if (valor.includes('casado') || valor.includes('uniao') || valor.includes('união')) {
            conjugeContainer.style.display = 'block';

            const inputConjuge = conjugeContainer.querySelector('input');
            if(inputConjuge) inputConjuge.setAttribute('required', 'true');
        } else {
            conjugeContainer.style.display = 'none';

            const inputConjuge = conjugeContainer.querySelector('input');
            if(inputConjuge) {
                inputConjuge.value = ''
                inputConjuge.removeAttribute('required');
            }

        }
    }

    if (estadoCivilSelect) {
        estadoCivilSelect.addEventListener('change', toggleConjugeField);
        toggleConjugeField();
    }
});

    function autoPreencher() {
    console.log("Iniciando preenchimento...");

    const dados = {
        'nome': 'Testando',
        'data_nascimento': '1990/01/01',
        'data_internacao': '2026/02/10',
        'cpf': '123.456.789-09',
        'rg': '12.345.678-9',
        'cartao_sus': '123.4567.8901.2345',
        'convenio': 'CapsAD',
        'cep': '01451-000',
        'rua': 'Avenida Brigadeiro Faria Lima',
        'num': '123',
        'bairro': 'Jardim Paulistano',
        'cidade': 'São Paulo',
        'estado': 'São Paulo',
        'mae': 'Maria Teste',
        'escolaridade': 'Não Alfabetizado',
        'profissao': 'Desenvolvedor',
        'religiao': 'Nenhuma',
        'estado_civil': 'Solteiro',
        'responsavel': 'Responsável Teste',
        'relacao': 'Pai',
        'contrib': '100.00',
        'contato': '(18) 99999-9999',
        'contato_dois': '(18) 98888-8888',
        'cpf_resp': '987.654.321-00',
        'rg_resp': '99.999.999-9'
    };

    for (const [key, value] of Object.entries(dados)) {
        let input = document.getElementById(key) || document.querySelector(`[name="${key}"]`);

        if (input) {
            input.value = value;
            input.dispatchEvent(new Event('input', { bubbles: true }));
            input.dispatchEvent(new Event('change', { bubbles: true }));
            input.dispatchEvent(new Event('blur', { bubbles: true }));
        } else {
            console.warn(`Campo não encontrado: ${key}`);
        }
    }


    App.mostrarSucesso('Dados preenchidos! Verifique se as máscaras aceitaram.');

}