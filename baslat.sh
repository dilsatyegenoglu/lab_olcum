#!/usr/bin/env bash
# Laboratuvar Malzemeleri ve Ölçüm Cihazları - Linux / WSL başlatıcı
# © 2026 Emine Dilşat Yeğenoğlu & Tevfik Hasan Can. Tüm hakları saklıdır.
set -e
cd "$(dirname "$0")"

if [ ! -x .venv/bin/streamlit ]; then
    rm -rf .venv
    echo ">> Sanal ortam oluşturuluyor (yalnızca ilk seferde)..."
    if ! python3 -m venv .venv; then
        echo
        echo "!! python3-venv paketi eksik. Şunu çalıştırıp tekrar deneyin:"
        echo "   sudo apt update && sudo apt install -y python3-venv python3-pip"
        rm -rf .venv
        exit 1
    fi
    echo ">> Gerekli paketler kuruluyor (birkaç dakika sürebilir)..."
    .venv/bin/pip install --upgrade pip -q
    .venv/bin/pip install -r requirements.txt
fi

echo
echo "=================================================================="
echo "  Uygulama başlıyor. Windows'ta tarayıcıyı açıp şu adrese gidin:"
echo "      http://localhost:8501"
echo "  Kapatmak için bu pencerede Ctrl+C"
echo "=================================================================="
echo
.venv/bin/streamlit run lab_streamlit.py --server.headless true --browser.gatherUsageStats false
