# THIN Site Guardian
## Sistema Inteligente de Manutenção, Qualidade, Segurança e Desempenho Web

Este documento registra o diagnóstico, a arquitetura e as rotinas de manutenção preventiva para o site **THIN — Direção Visual** (Wellington Correa).

---

## 1. Diagnóstico Inicial do Projeto

### Stack Atual:
- **Core:** HTML5 Semântico com arquitetura de ilhas reativas (React 19 + TypeScript + Vite 8).
- **Estilos:** CSS moderno com variáveis nativas, glassmorphism, tipografia Archivo + Instrument Serif e paleta nobre (`#F4F1EA`, `#101013`, `#873C48`, `#E9B872`).
- **Performance:** Imagens em formato WebP moderno, carregamento assíncrono (`decoding="async"`, `loading="lazy"`), pré-carregamento de fontes críticas.
- **Hospedagem Pública:** Netlify Edge (`https://thincorrea0.netlify.app/`) com cabeçalhos de segurança pré-configurados (HSTS, CSP, X-Frame-Options, X-Content-Type-Options).

### Auditoria de Conexão e Git:
- O ambiente do AI Studio exporta o pacote completo para desenvolvimento local ou sincronização via repositório GitHub.
- Atualmente, o Netlify serve a versão de produção com latência média de ~150-700ms via CDN global.

---

## 2. Como Executar as Verificações

O THIN Site Guardian pode ser executado localmente ou em pipelines de CI/CD através dos comandos:

```bash
# Executa a auditoria completa (remota + local + build + segurança)
npm run guardian

# Executa bateria completa: checagem de tipos + build de produção + auditoria
npm run check
```

---

## 3. O que o Guardian Audita

1. **Disponibilidade Pública & Uptime:**
   - Requisição HTTP com cabeçalhos reais para `https://thincorrea0.netlify.app/`.
   - Medição de tempo de resposta em milissegundos.
   - Verificação de integridade do conteúdo (garante que a página não retornou uma tela branca ou erro silencioso).
   - Validação de cabeçalhos de segurança (CSP, HSTS, X-Frame-Options, X-Content-Type-Options).

2. **Integridade de Assets Locais & Contatos:**
   - Varredura de todas as tags `<img>` e referências de assets para assegurar que nenhum arquivo esteja faltando no disco.
   - Monitoramento do peso individual das imagens (alerta se alguma ultrapassar 450KB).
   - Validação do link do **WhatsApp Oficial** (`https://wa.me/5517981927742`).

3. **Qualidade do Código e Compilação:**
   - Execução estrita do TypeScript (`tsc --noEmit`).
   - Compilação do bundle de produção com Vite (`vite build`).
   - Cálculo e monitoramento do peso total do diretório `dist/`.

4. **Blindagem e Segurança:**
   - Varredura de código contra exposição acidental de chaves de API, credenciais ou tokens privados no frontend.

---

## 4. Integração Contínua (GitHub Actions)

O arquivo `.github/workflows/guardian.yml` automatiza:
- **A cada alteração (Push / PR):** Instalação reproduzível (`npm ci`), checagem de tipos, compilação de produção e auditoria com geração de artefatos.
- **Monitoramento Agendado (Cron a cada 6h):** Verifica a saúde do site público automaticamente e registra relatórios.

---

## 5. Fluxo Seguro de Publicação (Netlify)

Para manter a segurança e evitar que alterações quebrem o site em produção:

1. **Desenvolvimento / Ajuste:** Alterações são feitas localmente ou no AI Studio.
2. **Validação:** Rodar `npm run check`.
3. **Prévia:** Conferir o preview localmente (`npm run dev` ou `npm run preview`).
4. **Deploy:** Sincronizar via Git com o repositório conectado ao Netlify ou fazer upload do arquivo `THIN-site-producao-dist.zip`.
5. **Pós-deploy:** O Guardian verifica se o site responde 200 OK com o conteúdo atualizado.
