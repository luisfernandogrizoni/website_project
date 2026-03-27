
const App = {

    processarMensagens: () => {
        const triggers = document.querySelectorAll('.message-trigger');
        if (triggers.length > 0) {
            App.fecharAlerta();
            triggers.forEach(el => {
                const tipo = el.dataset.type;
                const texto = el.dataset.text;

                if (tipo === 'success') {
                    App.mostrarSucesso(texto);
                } else if (tipo === 'danger' || tipo === 'error') {
                    App.mostrarErro(texto);
                } else {
                    App.mostrarErro(texto)
                }
            });
        }
    },

    initLogin: () => {
        const formLogin = document.getElementById('formLogin');
        if (formLogin) {
            formLogin.addEventListener('submit', (e) => {
                if (formLogin.checkValidity()) {
                    App.mostrarLoading('Autenticando');
                }
            });
        }
    },

    Stepper: {
        currentStep: 1,
        init: function() {
            this.goTo(1, true);
            this.bindEvents();
        },
            goTo: function(stepNumber, skipValidation = false) {
                if (!skipValidation && stepNumber > this.currentStep) {
                    if (!this.validateCurrentStep(this.currentStep)) {
                        App.mostrarErro("Por favor, preencha os campos obrigatórios antes de avançar.");
                        return;
                    }
                }
                document.querySelectorAll('.form-step').forEach(el => {
                    el.style.display = 'none';
                    el.classList.remove('active-step-animation');
                });
                const targetStepEl = document.getElementById(`step-${stepNumber}`);

                if (targetStepEl) {
                    targetStepEl.style.display = 'block';
                    targetStepEl.classList.add('active-step-animation');
                    document.querySelector('.stepper-wrapper').scrollIntoView({ behavior: 'smooth' });
                }
                this.updateIndicators(stepNumber);
                this.currentStep = stepNumber;
            },
            next: function(targetStep) {
                this.goTo(targetStep);
            },

            prev: function(targetStep) {
                this.goTo(targetStep, true);
            },

            updateIndicators: function(activeStep) {
                document.querySelectorAll('.stepper-item').forEach(item => {
                    item.classList.remove('active');
                });
                const activeItem = document.getElementById(`step-indicator-${activeStep}`);
                if (activeItem) {
                    activeItem.classList.add('active');
                }
            },
            validateCurrentStep: function(step) {
                const stepEl = document.getElementById(`step-${step}`);
                const inputs = stepEl.querySelectorAll('input:required, select:required');
                let isValid = true;

                inputs.forEach(input => {
                    if (!input.value) {
                        isValid = false;
                        input.classList.add('is-invalid');
                    } else {
                        input.classList.remove('is-invalid');
                    }
                });

                return isValid;
            },
            bindEvents: function() {
            document.querySelectorAll('.stepper-link').forEach(item => {
                item.addEventListener('click', () => {
                    const targetStep = parseInt(item.dataset.target);

                    if (targetStep < this.currentStep) {
                        this.goTo(targetStep, true);
                    } else if (targetStep === this.currentStep + 1) {
                        this.goTo(targetStep);
                    } else {
                        App.mostrarErro("Conclua as etapas anteriores primeiro")
                    }
                })
            })
                document.querySelectorAll('[data-stepper-action]').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        e.preventDefault();
                        const action = btn.dataset.stepperAction;
                        const target = parseInt(btn.dataset.target);

                        if (action === 'next') this.next(target);
                        if (action === 'prev') this.prev(target);
                    });
                });
            }
        },
        darBaixa: async (id, nomePaciente) => {
        const csrfTag = document.querySelector('meta[name="csrf-token"]');
        const csrfToken = csrfTag ? csrfTag.getAttribute('content') : '';

        if (!csrfToken) {
            console.error("CRÍTICO: CSRF Token não encontrado na meta tag!");
            App.mostrarErro("Erro de segurança: Recarregue a página.");
            return;
        }

        const {value: formValues } = await Swal.fire({
            title: `Dar baixa em: ${nomePaciente}`,
            html:
            `<div style="text-align: left">
                <label style="font-size: 0.9rem; font-weight: bold;">Data de Saída</label>
                <input id="swal-data" type="date" class="swal2-input" style="margin: 5px 0 15px 0;">

                <label style="font-size: 0.9rem; font-weight: bold;">Motivo da Saída</label>
                <select id="swal-motivo" class="swal2-select" style="margin: 5px 0;">
                    <option value="" disabled selected>Selecione</option>
                    <option value="Conclusão">Conclusão</option>
                    <option value="Desistência">Desistência</option>
                    <option value="Exclusão">Exclusão</option>
                    <option value="Óbito">Óbito</option>
                </select>
                </div>
        `,
        focusConfirm: false,
        showCancelButton: true,
        confirmButtonText: 'Confirmar',
        cancelButtonText: 'Cancelar',
        confirmButtonColor: '#C92A2A',
        preConfirm: () => {
                const dataSaida = document.getElementById('swal-data').value;
                const motivo = document.getElementById('swal-motivo').value;

                if (!dataSaida || !motivo) {
                    Swal.showValidationMessage('Por favor, preencha a data e o motivo');
                }
                return { data_saida: dataSaida, motivo: motivo };
                }
        });

        if (formValues) {
            App.mostrarLoading('Processando. Aguarde');
            try {
                const response = await fetch(`/api/paciente/${id}/baixa`, {
                    method: 'PATCH',
                    headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrfToken},
                    body: JSON.stringify(formValues)
                });

                    if (!response.ok) {
                        throw new Error('Erro do Servidor');
                    }

                App.mostrarSucesso('Baixa realizada com sucesso!', true);

                } catch (error) {
                    console.error("[CRITICAL] Falha na comunicação com API de Baixa. Status:", error);
                    App.fecharAlerta();
                    App.mostrarErro('Erro ao processar a baixa.');
                }
                }
            },

    abrirEdicao: async (id) => {
        App.mostrarLoading('Buscando dados para edição...');
        try {
            const response = await fetch(`/api/paciente/${id}`);
            if (!response.ok) throw new Error('Falha na API');
            const data = await response.json()

            App.fecharAlerta();

            const form = document.getElementById('prontuarioForm')
            if (!form) return;

            Object.keys(data).forEach(key => {
                const input = form.querySelector(`[data-bind="${key}"]`);
                if (input) {
                    if (input.type === 'checkbox') {
                        input.checked = data[key];
                    } else {
                        input.value = data[key] || '';
                    }
                    input.dispatchEvent(new Event('input'));
                }
            })

            document.querySelectorAll('.form-step').forEach(s => s.style.display = 'none');
            document.getElementById('step-1').style.display = 'block';

            form.setAttribute('data-mode', 'edit');
            form.setAttribute('data-id', id);

            console.log(`[DEBUG JS] Dados carregados para ID: ${id}`);
            form.scrollIntoView({ behavior: 'smooth' });

        } catch (error) {
            console.error("[ERRO JS]",error);
            App.mostrarErro('Erro ao carregar dados.');
        }
    },

    initCep: () => {
        const campoCep = document.querySelector('.action-busca-cep');
        if (campoCep) {
            campoCep.addEventListener('blur', async (e) => {
                const cep = e.target.value.replace(/\D/g, '');
                if (cep.length === 8) {
                    App.mostrarLoading('Buscando CEP...');
                    try {
                        const res = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
                        const data = await res.json();
                        if (!data.erro) {
                            const setVal = (id, val) => {
                                const el = document.getElementById(id);
                                if (el) el.value = val;
                            };
                            setVal('rua', data.logradouro);
                            setVal('bairro', data.bairro);
                            setVal('cidade', data.localidade);
                            setVal('estado', data.uf);
                            App.fecharAlerta();
                        } else {
                            App.mostrarErro('CEP não encontrado.');
                        }
                    } catch (error) {
                        App.mostrarErro('Erro ao buscar CEP.');
                    }
                }
            });
        }
    },
};

    window.onclick = function(event) {
        const modal = document.getElementById('modalDashboard');
        if (event.target == modal) {
            window.fecharDashboard();
        }
    };


    document.addEventListener('DOMContentLoaded', () => {
        const btnEdit = document.getElementById('btnEdit');
        if (btnEdit) {
            btnEdit.addEventListener('click', function() {
                const pacienteId = this.getAttribute('data-id');

                if (!pacienteId) {
                    console.error("Tentativa de edição sem ID válido.");
                }

                this.classList.add('is-loading');
                this.innerHTML = '<class="fas fa-spinner spin-icon"></i>Redirecionando...';

                setTimeout(() => {
                    window.location.href = `/prontuario?edit_id=${pacienteId}`;
                    }, 300);
                });
        }

        const btnInactivate = document.getElementById('btnInactivate');
        if (btnInactivate) {
            btnInactivate.addEventListener('click', function (){
                const pacienteId = this.getAttribute('data-id');
                if (!pacienteId) {
                    console.error("Tentativa de edição sem ID válido.");
                    return;
                }

                const elementoNome = document.getElementById('d-nome');
                const pacienteNome = elementoNome ? elementoNome.innerText : 'Paciente';

                App.darBaixa(pacienteId, pacienteNome);

            });
        }

        App.initMasks();
        App.initCep();
        App.initValidators();
        App.initLogin();
        App.processarMensagens();

        const form = document.getElementById('prontuarioForm');
        if (form) {
            const urlParams = new URLSearchParams(window.location.search);
            const editId = urlParams.get('edit_id');
            if (editId) {
                console.log(`[Modo Edição] ID detectado na URL: ${editId}. Buscando dados.`);
                App.abrirEdicao(editId);
            } else {
            console.log("[Modo Cadastro] Nenhum ID na URL. Formulário em branco.")
            }
            if (document.querySelector('.stepper-wrapper')) {
                App.Stepper.init();
            }
        }



    });