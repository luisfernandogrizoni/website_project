
const App = {
    mostrarLoading: (titulo = 'Processando...') => {
        Swal.fire({
            title: titulo,
            html: 'Por favor, aguarde.',
            allowOutsideClick: false,
            didOpen: () => Swal.showLoading()
        });
    },

    mostrarSucesso: (mensagem, reload = false) => {
        Swal.fire({
            icon: 'success',
            title: 'Sucesso!',
            text: mensagem,
            confirmButtonColor: '#28a745'
        }).then(() => {
            if (reload) window.location.reload();
        });
    },

    mostrarErro: (mensagem) => {
        Swal.fire({
            icon: 'error',
            title: 'Parece que algo deu errado!',
            text: mensagem,
            confirmButtonColor: '#d33'
        });
    },

    fecharAlerta: () => Swal.close(),

    api: {
        getCsftToken: () => {
            const tag = document.querySelector('meta[name="csrf-token"]');
            return tag ? tag.getAttribute('content') : '';
        },

        request: async (url, method = 'GET', body = null, isFormData = false) => {
            const headers = {'X-CSRFToken': App.api.getCsrfToken()};

            if (!isFormData && body) {
                headers['Content-Type'] = 'application/json';
            }

            const options = {method, headers};
            if (body) {
                options.body = isFormData ? body : JSON.stringify(body);
            }

            const response = await fetch(url, options);

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(errorText || `Erro do Servidor: ${response.status}`);
            }

            const contentType = response.headers.get("content-type");
            if (contentType && contentType.includes("application/json")) {
                return await response.json();
            }
            return await response.text();
        }

    },

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

    initMasks: () => {
        const masks = {
            '.mask-cpf': '000.000.000-00',
            '.mask-rg': '00.000.000-0',
            '.mask-cep': '00000-000',
            '.mask-phone': '(00) 00000-0000',
            '.mask-sus': '000.0000.0000.0000'
        }

        for (const [selector, maskPattern] of Object.entries(masks)) {
            document.querySelectorAll(selector).forEach(input => {
                if (input.tagName === 'INPUT' && !input.dataset.masked) {
                    try {
                        IMask(input, { mask: maskPattern });
                        input.dataset.masked = "true";
                    } catch (e) {
                        console.warn(`Erro na máscara ${selector}:`, e);
                    }
                }
            });
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

        isCpfValid: (cpf) => {
                cpf = cpf.replace(/[^\d]+/g, '');
                if (cpf.length !== 11 || /^(\d)\1+$/.test(cpf)) return false;

                let soma = 0, resto;

                for (let i = 1; i <= 9; i++)
                    soma = soma + parseInt(cpf.substring(i-1, i)) * (11 - i);
                resto = (soma * 10) % 11;
                if ((resto === 10) || (resto === 11)) resto = 0;
                if (resto !== parseInt(cpf.substring(9, 10))) return false;

                soma = 0;
                for (let i = 1; i <= 10; i++)
                    soma = soma + parseInt(cpf.substring(i-1, i)) * (12 - i);
                resto = (soma * 10) % 11;
                if ((resto === 10) || (resto === 11)) resto = 0;
                if (resto !== parseInt(cpf.substring(10, 11))) return false;

                return true;
            },

            initValidators: () => {
                document.querySelectorAll('.validate-cpf').forEach(input => {
                    input.addEventListener('blur', (e) => {
                        const valor = e.target.value;
                        if (valor) {
                            if (!App.isCpfValid(valor)) {
                                App.mostrarErro('O CPF digitado é inválido. Verifique os números.');
                                e.target.value = '';
                                e.target.classList.add('input-error');
                            } else {
                                e.target.classList.remove('input-error');
                            }
                        }
                    });
                });
                console.log("App: Validadores inicializados.");
            }
        };

    const abrirDashboard = async function(id) {
        const modal = document.getElementById('modalDashboard');
        const nomeEl = document.getElementById('d-nome');

        if(modal) {
            modal.style.display = 'flex';
            setTimeout(() => modal.classList.add('show'), 10);
        }

        if(nomeEl) nomeEl.innerText = "Buscando dados...";

        document.getElementById('d-nome').innerText = "Buscando informações...";
        const camposParaLimpar = ['d-idade', 'd-internacao', 'd-cpf', 'd-rg', 'd-endereco']; // Adicione outros se quiser
        camposParaLimpar.forEach(id => {
            const el = document.getElementById(id);
            if(el) el.innerText = "...";
        });

        try {
            const response = await fetch(`/api/paciente/${id}`);
            if (!response.ok) throw new Error("Paciente não encontrado");

            const data = await response.json();

            const set = (id, val) => {
                const el = document.getElementById(id);
                if(el) el.innerText = val || '-';
            };
            
            set('d-nome', data.nome);
            set('d-convenio', data.convenio);
            set('d-idade', data.idade + ' anos');
            set('d-internacao', Utils.maskData(data.data_internacao));

            set('d-cpf', Utils.maskCPF(data.cpf));
            set('d-rg', Utils.maskRG(data.rg));
            set('d-nascimento', Utils.maskData(data.data_nascimento));
            set('d-sus', Utils.maskSUS(data.cartao_sus));
            set('d-mae', Utils.formatarTexto(data.mae));

            set('d-escolaridade', Utils.formatarTexto(data.escolaridade));
            set('d-profissao', Utils.formatarTexto(data.profissao));
            set('d-religiao', Utils.formatarTexto(data.religiao));
            set('d-civil', Utils.formatarTexto(data.estado_civil));
            set('d-conjuge', Utils.formatarTexto(data.conjuge));

            set('d-endereco', data.endereco_completo);
            set('d-bairro', data.bairro);
            set('d-cidade', data.cidade);
            set('d-estado', data.estado);
            set('d-contato', data.contato);
            set('d-contato2', data.contato_dois);

            set('d-resp-nome', Utils.formatarTexto(data.responsavel));
            set('d-resp-relacao', Utils.formatarTexto(data.relacao));
            set('d-contrib', 'R$' + data.contrib);
            set('d-resp-cpf', Utils.maskCPF(data.cpf_resp));
            set('d-resp-rg', Utils.maskRG(data.rg_resp));

            const elConvenioTexto = document.getElementById('d-convenio');
            const elBadge = document.getElementById('d-badge-status');
            const convenio = (data.convenio || '').toLowerCase();


            let classeBadge = 'badge-padrao';
            let textoBadge = data.convenio;

            if (convenio.includes('social')) {
                classeBadge = 'badge-social';
                textoBadge = 'Social';
            }
            else if (convenio.includes('particular')) {
                classeBadge = 'badge-particular';
                textoBadge = 'Particular';
            }
            else if (convenio.includes('capsad')) {
                classeBadge = 'badge-caps';
                textoBadge = 'Caps AD';
            }
            else if (convenio.includes('taruma')) {
                classeBadge = 'badge-taruma';
                textoBadge = 'Convênio Tarumã';
            }

            const boxAtivo = document.getElementById('box-stats-ativo');
            const boxInativo = document.getElementById('box-stats-inativo');
            const badge = document.getElementById('d-badge-status');

            if (elConvenioTexto) {
                elConvenioTexto.innerText = textoBadge;
                elConvenioTexto.className = `badge ${classeBadge}`;
            }

            if (data.ativo) {
                if(boxAtivo) boxAtivo.style.display = 'flex';
                if(boxInativo) boxInativo.style.display = 'none';
                set('d-previsao', Utils.maskData(data.previsao_alta));

                if(badge) {
                    badge.innerText = "Ativo";
                    badge.className = "badge badge-padrao";
                    badge.style.backgroundColor = "green";
                }

            } else {
                if(boxAtivo) boxAtivo.style.display = 'none';
                if(boxInativo) boxInativo.style.display = 'flex';

                set('d-saida', Utils.maskData(data.data_saida));
                set('d-motivo', Utils.formatarTexto(data.motivo_saida));
                set('d-permanencia', Utils.formatarTexto(data.tempo_permanencia));

                if(badge) {
                    badge.innerText = "Inativo";
                    badge.className = "badge";
                    badge.style.backgroundColor = "#666";
                }
            }

            const btnEdit = document.getElementById('btnEdit');
            if (btnEdit) {
                btnEdit.setAttribute('data-id', id);
                btnEdit.classList.remove('is-loading');
                btnEdit.innerHTML = '<i class="fas fa-edit"></i> Editar';
            }

            const btnInactivate = document.getElementById('btnInactivate');
            if (btnInactivate) {
                btnInactivate.setAttribute('data-id', id);
                btnInactivate.classList.remove('is-loading');
                btnInactivate.innerHTML = '<i class="fas fa-archive"></i> Dar Baixa';
            }

            App.fecharAlerta();

        } catch (error) {
            console.error("Erro no Dashboard:", error);
            App.mostrarErro("Erro ao carregar prontuário.");
            fecharDashboard();
        }
    };

    window.fecharDashboard = function() {
        const modal = document.getElementById('modalDashboard');
        if(modal) {
            modal.classList.remove('show');
            setTimeout(() => modal.style.display = 'none', 300);
        }
    };

    window.onclick = function(event) {
        const modal = document.getElementById('modalDashboard');
        if (event.target == modal) {
            window.fecharDashboard();
        }
    };

    const Utils = {
        formatarTexto: (texto) => {
            if (!texto) return '-';
            return texto
                .replace(/_/g, ' ')
                .toLowerCase()
                .replace(/(?:^|\s)\S/g, function (a) {
                    return a.toUpperCase();
                });
        },

        maskCPF: (valor) => {
                if (!valor) return '-';
                return valor
                    .replace(/\D/g, '')
                    .replace(/(\d{3})(\d)/, '$1.$2')
                    .replace(/(\d{3})(\d)/, '$1.$2')
                    .replace(/(\d{3})(\d{1,2})/, '$1-$2')
                    .replace(/(-\d{2})\d+?$/, '$1');
            },

        maskRG: (valor) => {
            if (!valor) return '-';
            return valor.replace(/\D/g, '')
                        .replace(/(\d{2})(\d{3})(\d{3})(\d{1})$/, "$1.$2.$3-$4");
        },

        maskSUS: (valor) => {
            if (!valor) return '-';
            return valor.replace(/\D/g, '')
                .replace(/(\d{3})(\d{4})(\d{4})(\d{4})/, '$1 $2 $3 $4');
        },

        maskData: (valor) => {
            if (!valor) return '-';
            if (valor.includes('-')) {
            const partes = valor.split('-');
            if (partes.length === 3) {
                return `${partes[0]}/${partes[1]}/${partes[2]}`;
            }
        }
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