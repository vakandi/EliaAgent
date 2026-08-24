# Diagnostic Proxy Setup — Copie-colle ça dans ton terminal

## Étape 1 : Run cette commande

```bash
echo "=== 1. macOS VERSION ===" && sw_vers && echo "" && \
echo "=== 2. wget installé ? ===" && (which wget 2>/dev/null && wget --version | head -1 || echo "❌ wget PAS INSTALLÉ") && echo "" && \
echo "=== 3. curl installé ? ===" && (which curl 2>/dev/null && curl --version | head -1 || echo "❌ curl PAS INSTALLÉ") && echo "" && \
echo "=== 4. ~/.proxychains.conf ===" && (cat ~/.proxychains.conf 2>/dev/null || echo "FICHIER INTROUVABLE") && echo "" && \
echo "=== 5. ~/.proxychains.current ===" && (cat ~/.proxychains.current 2>/dev/null || echo "FICHIER INTROUVABLE") && echo "" && \
echo "=== 6. PROXIES.TXT ===" && (cat ~/EliaAI/setup/proxies.txt 2>/dev/null && echo "(trouvé dans ~/EliaAI)" || (find ~ -name "proxies.txt" -maxdepth 5 2>/dev/null | head -3 && echo "---" && cat $(find ~ -name "proxies.txt" -maxdepth 5 2>/dev/null | head -1) 2>/dev/null || echo "INTROUVABLE")) && echo "" && \
echo "=== 7. ALIAS sp configuré ? ===" && (alias sp 2>/dev/null && alias sp | head -3 || echo "Pas d'alias sp trouvé") && echo "" && \
echo "=== 8. Chemin du repo EliaAI ===" && (ls ~/EliaAI/setup/switch-proxy.sh 2>/dev/null && echo "~/EliaAI OK" || find ~ -name "switch-proxy.sh" -maxdepth 5 2>/dev/null | head -3) && echo "" && \
echo "=== 9. Test sp (proxy auto) ===" && (bash ~/EliaAI/setup/switch-proxy.sh 2>&1 || bash $(find ~ -name "switch-proxy.sh" -maxdepth 5 2>/dev/null | head -1) 2>&1 || echo "switch-proxy.sh introuvable") && echo "" && \
echo "=== 10. .proxy_enabled ===" && (cat ~/EliaAI/.proxy_enabled 2>/dev/null || echo "INTROUVABLE")
```

## Étape 2 : Copie tout l'output et envoie-le au développeur

C'est tout. 10 lignes de diagnostic, ça me dit exactement ce qui cloche sur ton setup.

---

**Exemple de ce que ça affichera :**
```
=== 1. macOS VERSION ===
ProductName:		macOS
ProductVersion:		15.3.1
BuildVersion:		24D70

=== 2. wget installé ? ===
❌ wget PAS INSTALLÉ

=== 3. curl installé ? ===
curl 8.7.1 (x86_64-apple-darwin24.0) ...

=== 4. ~/.proxychains.conf ===
FICHIER INTROUVABLE
...
```
