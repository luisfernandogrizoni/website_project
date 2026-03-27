// ==========================================
// CONTROLADOR DE INTERFACE DO FORMULÁRIO
// ==========================================

/**
 * Classe responsável por gerenciar as regras de negócio visuais e reativas
 * do formulário (ex: exibir/ocultar campos condicionalmente).
 */
export class FormUIController {
    /**
     * @param {string} idSelectEstadoCivil - O ID do elemento <select> de Estado Civil no HTML.
     * @param {string} idContainerConjuge - O ID da <div> que engloba o campo do cônjuge.
     */
    constructor(idSelectEstadoCivil, idContainerConjuge) {
        // Armazena as referências do DOM no escopo da classe (this) para evitar
        // múltiplas buscas (document.getElementById) durante a execução.
        this.selectCivil = document.getElementById(idSelectEstadoCivil);
        this.boxConjuge = document.getElementById(idContainerConjuge);
    }

    /**
     * O Maestro: Registra os evnt listeners) no DOM e garante
     * que o estado inicial da tela esteja correto ao carregar a página.
     */
    inicializador() {
        if (this.selectCivil) {
            this.selectCivil.addEventListener('change', () => {
                this.#toggleConjugeField();
            });

            this.#toggleConjugeField();
        }
    }

    /**
     * Regra de Negócio (Privada): Exibe a caixa de Cônjuge e torna o input obrigatório
     * apenas se o estado civil implicar em uma parceria formal.
     */
    #toggleConjugeField(){
        if (!this.selectCivil || !this.boxConjuge) return;
        const valor = this.selectCivil.value.toLowerCase().trim()

        console.log('Estado Civil Selecionado (Debug):', valor);
        if (valor.includes('casado') || valor.includes('uniao') || valor.includes('união')) {
            this.boxConjuge.style.display = 'block';

            const inputConjuge = this.boxConjuge.querySelector('input');
            if(inputConjuge) inputConjuge.setAttribute('required', 'true');
        } else {
            // Para outros estados civis (solteiro, viúvo, etc), esconde a caixa
            this.boxConjuge.style.display = 'none';

            const inputConjuge = this.boxConjuge.querySelector('input');
            if(inputConjuge) {
                inputConjuge.value = ''
                inputConjuge.removeAttribute('required');
            }

        }
    }

}




