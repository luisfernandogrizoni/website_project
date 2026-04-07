// ------------------- MÓDULO DE FORMATAÇÃO E MÁSCARAS DE TEXTO ------------------- //

/**
 * Remove underlines e aplica "Title Case" (Iniciais Maiúsculas).
 * * @param {string} texto - A string original (ex: "maria_silva")
 * @returns {string} O texto formatado (ex: "Maria Silva")
 */
export const formatarTexto = (texto) => {
        if (!texto) return '-';
        return texto
            .replace(/_/g, ' ')
            .toLowerCase()
            .replace(/(?:^|\s)\S/g, function (a) {
                return a.toUpperCase();
            });
    };

/**
 * Remove hífens e converte o padrão ISO (YYYY-MM-DD) para o padrão Brasileiro (DD/MM/YYYY).
 * * @param {string} texto - A string original (ex: "2026-03-12")
 * @returns {string} O texto formatado (ex: "12/03/2026")
 */
export const maskData = (valor) => {
        if (!valor) return '-';
        if (valor.includes('-')) {
            const partes = valor.split('-');
            if (partes.length === 3) {
                return `${partes[2]}/${partes[1]}/${partes[0]}`;
            }
        }
    }

/**
 * Insere hífens e pontuação de acordo com a máscara de cada documento (CPF, RG, CartãoSUS)
 * * @param {string} texto - A string original (ex: "12345648910")
 * @returns {string} O texto formatado (ex: "123.456.789-10")
 */
export const maskCPF = (valor) => {
            if (!valor) return '-';
            return valor
                .replace(/\D/g, '')
                .replace(/(\d{3})(\d)/, '$1.$2')
                .replace(/(\d{3})(\d)/, '$1.$2')
                .replace(/(\d{3})(\d{1,2})/, '$1-$2')
                .replace(/(-\d{2})\d+?$/, '$1');
        };

export const maskRG = (valor) => {
            if (!valor) return '-';
            return valor.replace(/\D/g, '')
                        .replace(/(\d{2})(\d{3})(\d{3})(\d{1})$/, "$1.$2.$3-$4");
        };
export const maskSUS = (valor) => {
            if (!valor) return '-';
            return valor.replace(/\D/g, '')
                .replace(/(\d{3})(\d{4})(\d{4})(\d{4})/, '$1 $2 $3 $4');
        };
