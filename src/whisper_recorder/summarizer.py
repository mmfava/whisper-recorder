"""Summarization via GPT-4o module."""

import os
from pathlib import Path
import openai

from .config import load_config

def summarize_transcription(mode: str, prompt: str) -> None:
    """
    Generate summary from transcription using GPT-4o via OpenAI API.
    mode: 'reunião', 'curso' ou 'custom'
    prompt: prompt customizado para modo 'custom'
    """
    # Carregar configuração
    try:
        config = load_config()
    except FileNotFoundError:
        print("Configuração não encontrada. Execute 'whisper-recorder setup' primeiro.")
        return
    # Carregar chave de ambiente para API OpenAI (default OPENAI_API_KEY)
    key_env = config.get("openai_api", {}).get("key_env", "OPENAI_API_KEY")
    api_key = os.getenv(key_env)
    if not api_key:
        print(f"Variável de ambiente '{key_env}' não está definida. Defina sua chave OpenAI.")
        return
    openai.api_key = api_key

    # Encontrar última sessão
    base_dir = Path("gravações")
    if not base_dir.exists():
        print("Não foram encontradas gravações. Execute 'whisper-recorder record' primeiro.")
        return
    sessions = [p for p in base_dir.iterdir() if p.is_dir()]
    if not sessions:
        print("Não foram encontradas gravações. Execute 'whisper-recorder record' primeiro.")
        return
    session_dir = sorted(sessions)[-1]

    # Ler transcrição
    txt_path = session_dir / "transcription.txt"
    if not txt_path.exists():
        print(f"Transcrição não encontrada em {session_dir}. Execute 'whisper-recorder transcribe' primeiro.")
        return
    transcription = txt_path.read_text(encoding="utf-8")

    # Preparar mensagem do sistema
    if mode == "reunião":
        system_message = (
            "Você é um assistente que resume reuniões. "
            "Liste os tópicos debatidos, decisões tomadas e próximas ações (quem, o quê, prazo)."
        )
    elif mode == "curso":
        system_message = (
            "Você é um assistente que resume aulas de forma técnica e didática. "
            "Forneça um texto fluido e técnico, com explicações adicionais, diagramas em Mermaid, "
            "blocos de código e referências."
        )
    elif mode == "custom":
        if not prompt:
            print("Modo 'custom' requer parâmetro --prompt.")
            return
        system_message = prompt
    else:
        print(f"Modo desconhecido '{mode}'. Use 'reunião', 'curso' ou 'custom'.")
        return

    # Construir mensagens
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": transcription},
    ]
    print("Gerando resumo usando GPT-4o...")
    # Compatibilidade com openai.py >=1.0 (novo) e <1.0 (antigo)
    try:
        # novo interface (openai>=1.0)
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.3,
        )
    except AttributeError:
        # interface antiga (openai<1.0)
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.3,
            )
        except Exception as e:
            print("Erro na API OpenAI ao usar interface antiga:", e)
            return
    except Exception as e:
        print("Erro na API OpenAI (novo interface):", e)
        return

    # Extrair conteúdo da resposta
    try:
        summary = response.choices[0].message.content
    except Exception:
        try:
            summary = response["choices"][0]["message"]["content"]
        except Exception:
            summary = str(response)

    # Salvar summary.md
    summary_path = session_dir / "summary.md"
    summary_path.write_text(summary, encoding="utf-8")
    print(f"Resumo salvo em {summary_path}")