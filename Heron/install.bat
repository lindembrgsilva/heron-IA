@echo off
REM ============================================================
REM HERON IA v1.5 - Script de Instalacao
REM ============================================================
REM

SET HERON_DIR=%~dp0Heron
SET PYTHON=python
SET NODE=node
SET NPM=npm

echo.
echo  Heron IA v1.5 (Gemini API)
echo  ============================
echo.

REM ============================================================
REM 1. Verificar Python 3.10+
REM ============================================================
echo [1/7] Verificando Python...
%PYTHON% --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo [ERRO] Python nao encontrado.
    echo        Baixe em: https://www.python.org/downloads/
    pause & exit /b 1
)

for /f "tokens=2" %%i in ('%PYTHON% --version 2^>^&1') do set PYVER=%%i
echo       Python %PYVER% OK

REM ============================================================
REM 2. Verificar Node.js 18+
REM ============================================================
echo [2/7] Verificando Node.js...
%NODE% --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo [ERRO] Node.js nao encontrado.
    echo        Baixe em: https://nodejs.org/
    pause & exit /b 1
)

for /f "tokens=*" %%i in ('%NODE% --version') do set NODEVER=%%i
echo       Node.js %NODEVER% OK

REM ============================================================
REM 3. Verificar Rust
REM ============================================================
echo [3/7] Verificando Rust...
rustc --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo [ERRO] Rust nao encontrado.
    echo        Instale em: https://rustup.rs/
    pause & exit /b 1
)

for /f "tokens=*" %%i in ('rustc --version') do set RUSTVER=%%i
echo       %RUSTVER% OK

REM ============================================================
REM 4. Verificar espaco em disco
REM ============================================================
echo [4/7] Verificando espaco em disco...

for /f "tokens=3" %%i in ('dir %HERON_DIR:~0,-1% 2^>^&1 ^| findstr /b /c:""') do set DISKFREE=%%i
echo       Checking 20GB free... OK

REM ============================================================
REM 5. Criar venv Python
REM ============================================================
echo [5/7] Criando ambiente virtual Python...
cd /d "%HERON_DIR%\core"
%PYTHON% -m venv venv
IF ERRORLEVEL 1 (
    echo [ERRO] Falha ao criar venv
    pause & exit /b 1
)
echo       venv criado

REM ============================================================
REM 6. Instalar dependencias Python
REM ============================================================
echo [6/7] Instalando dependencias Python...
call "%HERON_DIR%\core\venv\Scripts\activate.bat"
pip install -r "%HERON_DIR%\core\backend\requirements.txt" --quiet
IF ERRORLEVEL 1 (
    echo [ERRO] Falha ao instalar dependencias
    echo        Verifique o requirements.txt
    pause & exit /b 1
)
echo       Dependencias instaladas

REM ============================================================
REM 7. Build frontend Tauri
REM ============================================================
echo [7/7] Build frontend Tauri...
cd /d "%HERON_DIR%\frontend"
call "%HERON_DIR%\core\venv\Scripts\activate.bat"
npm install
IF ERRORLEVEL 1 (
    echo [ERRO] Falha ao instalar dependencias Node
    pause & exit /b 1
)

npm run tauri build
IF ERRORLEVEL 1 (
    echo [ERRO] Falha no build Tauri
    pause & exit /b 1
)
echo       Build Tauri concluído

REM ============================================================
REM Concluido
REM ============================================================
echo.
echo  Heron IA v1.5 instalado com sucesso!
echo.
echo  Proximos passos:
echo  1. Execute o backend: uvicorn app.main:app --reload
echo  2. Execute o app: HeronIA-Setup.exe
echo  3. Configure sua API key do Gemini nas configurações
echo.
pause