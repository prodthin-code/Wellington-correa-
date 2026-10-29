#!/usr/bin/env python3
"""
THIN SITE GUARDIAN
Sistema de Manutenção, Qualidade, Segurança e Desempenho Web
Para THIN — Direção Visual (Wellington Correa)
"""

import sys
import os
import json
import time
import re
import urllib.request
import urllib.error
import subprocess
from datetime import datetime
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
PUBLIC_URL = "https://thincorrea0.netlify.app/"
REPORTS_DIR = WORKSPACE_ROOT / "reports"
DIST_DIR = WORKSPACE_ROOT / "dist"
PUBLIC_DIR = WORKSPACE_ROOT / "public"

class ThinSiteGuardian:
    def __init__(self, check_remote: bool = True):
        self.check_remote = check_remote
        self.report = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "target_url": PUBLIC_URL,
            "overall_status": "SAUDÁVEL",
            "checks": {},
            "metrics": {},
            "issues": [],
            "recommendations": []
        }

    def log(self, section: str, msg: str):
        print(f"[{section.upper()}] {msg}")

    def audit_remote_availability(self):
        """Monitora disponibilidade, tempo de resposta e headers do site publicado."""
        self.log("disponibilidade", f"Testando URL pública: {PUBLIC_URL}")
        start_time = time.time()
        try:
            req = urllib.request.Request(
                PUBLIC_URL,
                headers={"User-Agent": "THIN-Site-Guardian/1.0 (+https://thincorrea0.netlify.app)"}
            )
            with urllib.request.urlopen(req, timeout=12) as response:
                duration_ms = round((time.time() - start_time) * 1000)
                status_code = response.status
                headers = dict(response.headers)
                body = response.read().decode("utf-8", errors="ignore")

                # Validação de conteúdo essencial
                live_content_valid = all(
                    token in body for token in ["THIN", "Wellington", "Laboratório"]
                )
                has_latest_copy = "Modelos simples" in body

                # Validação de segurança em headers
                sec_headers = {
                    "Content-Security-Policy": headers.get("content-security-policy") is not None,
                    "Strict-Transport-Security": headers.get("strict-transport-security") is not None,
                    "X-Frame-Options": headers.get("x-frame-options") is not None,
                    "X-Content-Type-Options": headers.get("x-content-type-options") is not None,
                }

                self.report["checks"]["remote_availability"] = {
                    "status": "PASS" if status_code == 200 and live_content_valid else "FAIL",
                    "http_status": status_code,
                    "latency_ms": duration_ms,
                    "content_valid": live_content_valid,
                    "pending_deploy_sync": not has_latest_copy,
                    "server": headers.get("server", "Unknown"),
                    "security_headers": sec_headers
                }
                self.report["metrics"]["response_time_ms"] = duration_ms

                if not has_latest_copy:
                    self.report["recommendations"].append(
                        "O Netlify público ainda não recebeu o deploy das alterações recentes do Laboratório/Método. Sincronize o repositório ou faça o upload manual do zip quando desejar publicar."
                    )

                if duration_ms > 2000:
                    self.report["issues"].append({
                        "severity": "WARNING",
                        "title": "Latência elevada no Netlify Edge",
                        "detail": f"Tempo de resposta de {duration_ms}ms superou a meta de 2000ms."
                    })

                self.log("disponibilidade", f"HTTP {status_code} em {duration_ms}ms - Conteúdo íntegro: {live_content_valid} (Versão mais recente sincronizada: {has_latest_copy})")

        except Exception as e:
            self.report["checks"]["remote_availability"] = {
                "status": "FAIL",
                "error": str(e)
            }
            self.report["issues"].append({
                "severity": "CRITICAL",
                "title": "Falha na conexão com a URL pública",
                "detail": str(e)
            })
            self.report["overall_status"] = "FALHA CONFIRMADA"
            self.log("disponibilidade", f"ERRO: {e}")

    def audit_local_assets_and_links(self):
        """Verifica a integridade das imagens, caminhos e canais de contato."""
        self.log("assets", "Auditando referências de assets e links no index.html...")
        index_path = WORKSPACE_ROOT / "index.html"
        if not index_path.exists():
            self.report["issues"].append({"severity": "CRITICAL", "title": "index.html ausente"})
            return

        html = index_path.read_text(encoding="utf-8")

        # Verifica imagens em src/
        img_srcs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html)
        missing_images = []
        oversized_images = []

        for src in set(img_srcs):
            if src.startswith("http://") or src.startswith("https://") or src.startswith("data:"):
                continue
            clean_path = src.lstrip("/")
            file_on_disk = PUBLIC_DIR / clean_path
            if not file_on_disk.exists():
                # Tenta no workspace root
                file_on_disk = WORKSPACE_ROOT / clean_path

            if not file_on_disk.exists():
                missing_images.append(src)
            else:
                size_kb = file_on_disk.stat().st_size / 1024
                if size_kb > 450:
                    oversized_images.append({"path": src, "size_kb": round(size_kb, 1)})

        # Validação do WhatsApp Comercial
        whatsapp_official = "5517981927742"
        wa_links = re.findall(r'href=["\'](https://wa\.me/[^"\']+)["\']', html)
        wa_valid = all(whatsapp_official in link for link in wa_links)

        self.report["checks"]["assets"] = {
            "status": "PASS" if not missing_images else "FAIL",
            "total_images_referenced": len(img_srcs),
            "missing_images": missing_images,
            "oversized_images": oversized_images,
            "whatsapp_links_verified": wa_valid,
            "whatsapp_link_count": len(wa_links)
        }

        if missing_images:
            self.report["issues"].append({
                "severity": "CRITICAL",
                "title": "Imagens referenciadas ausentes no disco",
                "detail": f"Arquivos não encontrados: {missing_images}"
            })
            self.report["overall_status"] = "FALHA CONFIRMADA"

        if oversized_images:
            self.report["recommendations"].append(
                f"Otimizar as imagens com peso acima de 450KB para preservar o LCP móvel: {[img['path'] for img in oversized_images]}"
            )

        if not wa_valid:
            self.report["issues"].append({
                "severity": "WARNING",
                "title": "Link de WhatsApp desatualizado",
                "detail": f"Um ou mais links não utilizam o número comercial {whatsapp_official}."
            })

    def audit_security_and_secrets(self):
        """Verifica se há segredos, credenciais ou endpoints inseguros expostos."""
        self.log("segurança", "Escaneando código em busca de segredos e boas práticas...")
        suspicious_patterns = [
            re.compile(r'(AIza[0-9A-Za-z-_]{35})'),
            re.compile(r'sk_live_[0-9a-zA-Z]{24}'),
            re.compile(r'ghp_[0-9a-zA-Z]{36}'),
            re.compile(r'(SECRET|API_KEY|PRIVATE_KEY)\s*=\s*["\'][^"\']+["\']', re.IGNORECASE)
        ]

        exposed_secrets = []
        for root, _, files in os.walk(WORKSPACE_ROOT):
            if "node_modules" in root or ".git" in root or "dist" in root:
                continue
            for file in files:
                if file.endswith((".ts", ".tsx", ".js", ".html", ".json", ".md")):
                    fpath = Path(root) / file
                    try:
                        content = fpath.read_text(encoding="utf-8", errors="ignore")
                        for pat in suspicious_patterns:
                            matches = pat.findall(content)
                            if matches:
                                exposed_secrets.append(f"{fpath.name} ({len(matches)} ocorrência)")
                    except Exception:
                        pass

        self.report["checks"]["security"] = {
            "status": "PASS" if not exposed_secrets else "FAIL",
            "secrets_detected": exposed_secrets
        }

        if exposed_secrets:
            self.report["issues"].append({
                "severity": "CRITICAL",
                "title": "Possíveis segredos ou tokens expostos no frontend",
                "detail": f"Detectado em: {exposed_secrets}"
            })
            self.report["overall_status"] = "FALHA CONFIRMADA"

    def audit_build_and_types(self):
        """Verifica TypeScript e integridade do bundle Vite."""
        self.log("build", "Testando checagem de tipos (tsc --noEmit)...")
        try:
            lint_res = subprocess.run(
                ["npm", "run", "lint"],
                cwd=WORKSPACE_ROOT,
                capture_output=True,
                text=True,
                timeout=60
            )
            lint_pass = lint_res.returncode == 0
        except Exception as e:
            lint_pass = False
            self.log("build", f"Erro no lint: {e}")

        self.log("build", "Testando compilação de produção (vite build)...")
        try:
            build_res = subprocess.run(
                ["npm", "run", "build"],
                cwd=WORKSPACE_ROOT,
                capture_output=True,
                text=True,
                timeout=60
            )
            build_pass = build_res.returncode == 0
        except Exception as e:
            build_pass = False
            self.log("build", f"Erro no build: {e}")

        # Tamanho do bundle
        dist_size_kb = 0
        if DIST_DIR.exists():
            dist_size_kb = sum(f.stat().st_size for f in DIST_DIR.glob("**/*") if f.is_file()) / 1024

        self.report["checks"]["build"] = {
            "status": "PASS" if lint_pass and build_pass else "FAIL",
            "typescript_clean": lint_pass,
            "vite_build_clean": build_pass,
            "dist_total_kb": round(dist_size_kb, 1)
        }

        if not lint_pass or not build_pass:
            self.report["issues"].append({
                "severity": "CRITICAL",
                "title": "Falha na compilação ou checagem de tipos",
                "detail": "npm run lint ou npm run build falharam."
            })
            self.report["overall_status"] = "FALHA CONFIRMADA"

    def generate_reports(self):
        """Grava relatórios em JSON e Markdown legível."""
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)

        # Ajusta status geral se houver apenas avisos
        if self.report["overall_status"] != "FALHA CONFIRMADA":
            if any(i["severity"] == "WARNING" for i in self.report["issues"]):
                self.report["overall_status"] = "ATENÇÃO NECESSÁRIA"

        json_path = REPORTS_DIR / "health-report.json"
        json_path.write_text(json.dumps(self.report, indent=2, ensure_ascii=False), encoding="utf-8")

        md_path = REPORTS_DIR / "health-report.md"
        status_badge = {
            "SAUDÁVEL": "🟢 SAUDÁVEL",
            "ATENÇÃO NECESSÁRIA": "🟡 ATENÇÃO NECESSÁRIA",
            "FALHA CONFIRMADA": "🔴 FALHA CONFIRMADA"
        }.get(self.report["overall_status"], self.report["overall_status"])

        md_lines = [
            f"# THIN Site Guardian — Relatório de Saúde",
            f"**Data da Auditoria:** {self.report['timestamp']}",
            f"**Status Geral:** {status_badge}",
            f"**URL Pública:** [{PUBLIC_URL}]({PUBLIC_URL})\n",
            "## 1. Disponibilidade & Resposta",
        ]

        remote = self.report["checks"].get("remote_availability", {})
        if remote:
            md_lines.append(f"- **Status HTTP:** {remote.get('http_status', 'N/A')}")
            md_lines.append(f"- **Tempo de resposta:** {remote.get('latency_ms', 'N/A')}ms")
            md_lines.append(f"- **Validação de conteúdo:** {'Aprovada' if remote.get('content_valid') else 'Falhou'}")
            md_lines.append(f"- **Servidor / Borda:** {remote.get('server', 'Netlify')}")
        else:
            md_lines.append("- Verificação remota desativada.")

        md_lines.append("\n## 2. Qualidade do Código & Build")
        bld = self.report["checks"].get("build", {})
        md_lines.append(f"- **TypeScript:** {'Sem erros (Pass)' if bld.get('typescript_clean') else 'Erros encontrados'}")
        md_lines.append(f"- **Vite Production Build:** {'Compilado com sucesso' if bld.get('vite_build_clean') else 'Falha na compilação'}")
        md_lines.append(f"- **Tamanho total do diretório dist:** {bld.get('dist_total_kb', 0)} KB")

        md_lines.append("\n## 3. Integridade de Assets & Contatos")
        ast = self.report["checks"].get("assets", {})
        md_lines.append(f"- **Total de imagens auditadas:** {ast.get('total_images_referenced', 0)}")
        md_lines.append(f"- **Imagens ausentes:** {len(ast.get('missing_images', []))}")
        md_lines.append(f"- **Links oficiais do WhatsApp (17 98192-7742):** {'Todos corretos' if ast.get('whatsapp_links_verified') else 'Revisar'}")

        md_lines.append("\n## 4. Segurança & Segredos")
        sec = self.report["checks"].get("security", {})
        md_lines.append(f"- **Segredos expostos no código:** {'Nenhum detectado (Seguro)' if not sec.get('secrets_detected') else str(sec.get('secrets_detected'))}")

        if self.report["issues"]:
            md_lines.append("\n## 5. Problemas Identificados")
            for iss in self.report["issues"]:
                md_lines.append(f"- **[{iss['severity']}] {iss['title']}:** {iss['detail']}")

        if self.report["recommendations"]:
            md_lines.append("\n## 6. Recomendações")
            for rec in self.report["recommendations"]:
                md_lines.append(f"- {rec}")

        md_path.write_text("\n".join(md_lines), encoding="utf-8")
        self.log("relatório", f"Relatórios gerados em {REPORTS_DIR}/")

    def run_all(self):
        self.log("guardian", "Iniciando bateria de auditoria do THIN Site Guardian...")
        if self.check_remote:
            self.audit_remote_availability()
        self.audit_local_assets_and_links()
        self.audit_security_and_secrets()
        self.audit_build_and_types()
        self.generate_reports()
        self.log("guardian", f"Auditoria concluída. Status: {self.report['overall_status']}")
        return 0 if self.report["overall_status"] != "FALHA CONFIRMADA" else 1

if __name__ == "__main__":
    skip_remote = "--no-remote" in sys.argv
    guardian = ThinSiteGuardian(check_remote=not skip_remote)
    exit_code = guardian.run_all()
    sys.exit(exit_code)
