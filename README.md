# THIN — Sites e Direção Visual

Site institucional e portfólio de alta conversão de Wellington Correa (THIN), focado em direção visual, criação de sites e organização da presença digital de pequenos negócios em São José do Rio Preto, SP e região.

Aplicação estática independente desenvolvida em HTML5 semântico, CSS moderno e ilhas interativas em TypeScript com Vite e React 19. Não possui dependências de servidor dinâmico, banco de dados ou APIs proprietárias para execução.

---

## 1. Estrutura do Projeto (`thin-site-export`)

```text
thin-site-export/
├── dist/                   # Build final pronto para publicação estática (gerado via npm run build)
├── public/                 # Ativos estáticos e arquivos de configuração
│   ├── _headers            # Cabeçalhos HTTP para Netlify e Cloudflare Pages (HSTS, CSP, Cache)
│   ├── robots.txt          # Diretivas para mecanismos de busca
│   ├── sitemap.xml         # Mapa do site indexável
│   └── assets/             # Fotografias em WebP, ícones e texturas
├── src/                    # Componentes interativos React 19 (MaskedHeading, Lightning, ColorBends)
│   ├── components/         # Ilhas interativas WebGL e Motion
│   ├── App.tsx             # Definição dos estudos e dados do Laboratório
│   ├── main.tsx            # Ponto de montagem das ilhas interativas
│   └── index.css           # Estilos base
├── scripts/                # Scripts utilitários
│   ├── site_guardian.py    # Auditoria de integridade, disponibilidade e segurança
│   └── export_project.py   # Gerador de pacotes para exportação e backup
├── .github/workflows/      # CI/CD automatizado para GitHub Actions (testes + monitoramento 6h)
├── index.html              # Documento principal da aplicação (single-page)
├── netlify.toml            # Configuração de build e headers para Netlify
├── vercel.json             # Configuração de build e headers para Vercel
├── package.json            # Scripts de execução e dependências
├── package-lock.json       # Lockfile oficial para npm
├── tsconfig.json           # Configuração de tipagem TypeScript
├── vite.config.ts          # Configuração do Vite
├── GUARDIAN.md             # Documentação do sistema de manutenção e qualidade
├── .env.example            # Exemplo de variáveis de ambiente opcionais
└── README.md               # Este guia
```

---

## 2. Execução Local

Requisitos: **Node.js 18+** (recomendado Node.js 20 LTS) e **npm**.

```bash
# 1. Instalar as dependências
npm install

# 2. Iniciar o servidor de desenvolvimento local
npm run dev

# 3. Testar o build de produção localmente
npm run build
npm run preview
```

O site abrirá em `http://localhost:3000` (ou na porta configurada pelo Vite).

---

## 3. Comandos Disponíveis (`package.json`)

- `npm run dev` — Inicia o servidor Vite local para desenvolvimento.
- `npm run build` — Compila a aplicação estática na pasta `dist/`.
- `npm run preview` — Serve a pasta `dist/` localmente para validação final pré-deploy.
- `npm run lint` — Executa a checagem estrita de tipos com TypeScript (`tsc --noEmit`).
- `npm run guardian` — Executa a auditoria do THIN Site Guardian (testa disponibilidade remota, integridade de assets, links de contato e segurança).
- `npm run check` — Bateria completa: lint + build + guardian.

---

## 4. Guia de Publicação por Plataforma

O site gera uma pasta `dist/` estática. Ele pode ser hospedado em qualquer serviço estático moderno:

### A. Netlify (Configuração Pronta)

#### Via Git (Recomendado):
1. Conecte seu repositório no Netlify.
2. Parâmetros de build:
   - **Build command:** `npm run build`
   - **Publish directory:** `dist`
3. O Netlify detectará automaticamente o arquivo `netlify.toml`, aplicando regras de HSTS, CSP, cabeçalhos de segurança e cache.

#### Via Netlify Drop (Arrastar e Soltar):
1. Execute `npm run build` (ou descompacte o arquivo `THIN-site-producao-dist.zip`).
2. No painel do Netlify, acesse a aba **Sites** e arraste a pasta `dist` para a área de drop. O deploy é instantâneo.

---

### B. Vercel

1. Importe o projeto no painel da Vercel.
2. Parâmetros de build:
   - **Framework Preset:** Vite
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
3. O arquivo `vercel.json` na raiz já configura as diretivas de CSP com suporte a WebGL e headers de segurança.

---

### C. Cloudflare Pages

1. Conecte o repositório no Cloudflare Pages.
2. Parâmetros de build:
   - **Build command:** `npm run build`
   - **Build output directory:** `dist`
3. O Cloudflare Pages lerá o arquivo `public/_headers` (copiado automaticamente para `dist/_headers`), aplicando os cabeçalhos de segurança.

---

### D. Servidor Próprio (Apache / Nginx / VPS)

Basta compilar o site (`npm run build`) e copiar o conteúdo interno da pasta `dist/` para a raiz do seu servidor web (ex: `/var/www/html/`).

Exemplo para Nginx:
```nginx
server {
    listen 80;
    server_name seudominio.com.br;
    root /var/www/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location ~* \.(?:webp|jpg|jpeg|png|svg|ico|css|js)$ {
        expires 7d;
        add_header Cache-Control "public, no-transform";
    }
}
```

---

## 5. Como Configurar um Domínio Personalizado

Quando for conectar um domínio próprio (ex: `https://thinvisual.com.br`), atualize os seguintes pontos:

1. **`index.html` (linha 10):**
   ```html
   <link rel="canonical" href="https://SEUDOMINIO.com.br/">
   <meta property="og:url" content="https://SEUDOMINIO.com.br/">
   <meta property="og:image" content="https://SEUDOMINIO.com.br/assets/og-thin.jpg">
   <meta name="twitter:image" content="https://SEUDOMINIO.com.br/assets/og-thin.jpg">
   ```
2. **`public/sitemap.xml`:**
   Substitua `https://thincorrea0.netlify.app/` pelo seu domínio.
3. **`public/robots.txt`:**
   Substitua o link do sitemap.
4. Execute `npm run build` para regerar a pasta `dist/`.

---

## 6. Dependências Externas

O projeto foi construído para ter o mínimo de dependências externas:
- **Google Fonts:** Carrega as famílias tipográficas `Archivo` e `Instrument Serif` via `fonts.googleapis.com` (com fallback seguro para fontes do sistema).
- **Sem Backend Obrigatório:** Todos os contatos utilizam links diretos para o WhatsApp comercial oficial (`https://wa.me/5517981927742`) e Instagram (`https://www.instagram.com/thin_skx/`).
- **Sem Cookies de Rastreamento:** Dispensa banners intrusivos de cookies ou dependências pagas de terceiros.
