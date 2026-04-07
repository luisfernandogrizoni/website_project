// ------------------- SERVIÇO DE COMUNICAÇÃO COM A API (FLASK) ------------------- //

/**
 * Classe responsável por centralizar todas as requisições HTTP do sistema.
 * Garante a injeção do token CSRF e padroniza o tratamento de respostas e erros.
 */
export class ApiService {

    /**
     * Busca o token de segurança CSRF na meta tag do HTML.
     * Método privado: acessível apenas pelo próprio objeto.
     * @returns {string} O token CSRF ou uma string vazia se não encontrado.
     */
     #getCsrfToken = () => {
        const tag = document.querySelector('meta[name="csrf-token"]');
        return tag ? tag.getAttribute('content') : '';
    };

     /**
     * Dispara uma requisição assíncrona para o servidor.
     * @param {string} url - O endpoint da API (ex: '/api/paciente/1').
     * @param {string} [method='GET'] - O verbo HTTP (GET, POST, PATCH, DELETE).
     * @param {Object|FormData} [body=null] - Os dados a serem enviados.
     * @param {boolean} [isFormData=false] - Define se o corpo é um FormData (para upload de arquivos/forms).
     * @returns {Promise<Object|string>} A resposta da API já convertida.
     * @throws {Error} Lança um erro detalhado caso o status HTTP represente uma falha.
     */
    async request(url, method = 'GET', body = null, isFormData = false){
            const headers = {'X-CSRFToken': this.#getCsrfToken()};

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
}
