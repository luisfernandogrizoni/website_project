// ------------------- CONTROLADOR DA PÁGINA: PRONTUÁRIO ------------------- //

import { ApiService } from '../core/api.js';
import { NotificationService } from '../core/notification.js';
import { MaskController } from '../utils/masks.js';
import { FormUIController } from '../utils/form-controller.js';

const notificacao = new NotificationService();
const api = new ApiService();
const mascaras = new MaskController();

// ==========================================
// INICIALIZAÇÃO E OUVINTES DE EVENTOS (DOM)
// ==========================================

document.addEventListener('DOMContentLoaded', function() {
    // --------------------------------------
    // 1. Botão de Autopreencher (Dev/Testes)
    // --------------------------------------
    // TODO: Corrigir autopreencher: Botão não está retornando a função
    const btnPreencher = document.getElementById('btnAutoPreencher');
    if (btnPreencher) {
        btnPreencher.addEventListener('click', autoPreencher);
    }

    // --------------------------------------
    // 2. Submissão do Formulário Principal
    // --------------------------------------
    // Inicialização do controlador da caixa 'conjuge'
        const formUI = new FormUIController('estado_civil', 'conjuge_container');
        formUI.inicializador();

    // Inicialização das máscaras de documento
    mascaras.initMasks();
    const form = document.getElementById('prontuarioForm');
    if (form) {
        form.addEventListener('submit', async function (event) {
            event.preventDefault();
            notificacao.loading('Salvando Prontuário...');

            try {
                // Prepara os dados do formulário para envio, suportando arquivos
                const formData = new FormData(form);

                const html = await api.request(window.location.href, 'POST', formData, true);

                // Analisa o HTML retornado pelo Flask
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const erros = doc.querySelector('.error-message');

                if (erros) {
                    notificacao.fecharAlerta()

                    // Substitui o conteúdo principal da tela para exibir os erros do Flask
                    const novoConteudo = doc.querySelector('main') || document.body;
                    const conteudoAtual = document.querySelector('main') || document.body;

                    conteudoAtual.innerHTML = novoConteudo.innerHTML;
                    notificacao.erro('Verifique os campos obrigatórios destacados.');

                    mascaras.initMasks();

                } else {
                    const triggers = doc.querySelectorAll('.message-trigger');
                    if (triggers.length > 0) {
                        document.documentElement.innerHTML = html;
                    } else {
                        notificacao.sucesso('Salvo com sucesso!', true);
                    }
                }
            } catch (error) {
                console.error('Erro Crítico no Envio: ', error);
                notificacao.fecharAlerta();
                notificacao.erro('Falha de comunicação. Tente novamente ou contate o suporte.');
            }
        });
    }

    // ==========================================
    // FUNÇÕES AUXILIARES
    // ==========================================

    /**
     * Preenche o formulário automaticamente com dados fictícios.
     * Útil para agilizar testes de desenvolvimento e validação de máscaras.
     */
    function autoPreencher() {
        console.log("Iniciando preenchimento...");

        const dados = {
            'nome': 'Paciente de Teste da Silva',
            'data_nascimento': '1990-01-01',
            'data_internacao': '2026-02-10',
            'cpf': '12345678909',
            'rg': '123456789',
            'cartao_sus': '123456789012345',
            'convenio': 'capsad',
            'cep': '01451000',
            'rua': 'Avenida Brigadeiro Faria Lima',
            'num': '123',
            'bairro': 'Jardim Paulistano',
            'cidade': 'São Paulo',
            'estado': 'SP',
            'mae': 'Maria Teste da Silva',
            'escolaridade': 'fundamental',
            'profissao': 'Desenvolvedor',
            'religiao': 'nenhuma',
            'estado_civil': 'solteiro',
            'responsavel': 'Responsável Teste',
            'relacao': 'pai',
            'contrib': '100',
            'contato': '18999999999',
            'contato_dois': '18988888888',
            'cpf_resp': '98765432100',
            'rg_resp': '999999999'
        };

        for (const [key, value] of Object.entries(dados)) {
            let input = document.getElementById(key) || document.querySelector(`[name="${key}"]`);

            if (input) {
                // Lógica blindada para diferentes tipos de inputs HTML
                if (input.type === 'checkbox' || input.type === 'radio') {
                    input.checked = (value === true || value === 'true');
                } else {
                    input.value = value;
                }

                if (input) {
                    // Faz as máscaras de CPF/Telefone formatarem sozinhas
                    input.value = value;
                    input.dispatchEvent(new Event('input', {bubbles: true}));
                    input.dispatchEvent(new Event('change', {bubbles: true}));
                    input.dispatchEvent(new Event('blur', {bubbles: true}));
                } else {
                    console.warn(`Campo não encontrado: ${key}`);
                }
            }

            notificacao.sucesso('Dados preenchidos! Verifique se as máscaras aceitaram.');
        }
    }
})