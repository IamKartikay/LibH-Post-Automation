# Ollama setup (local, no account)

This project talks to **Ollama on your PC**, not to ollama.com. You do **not** need to create or connect an Ollama account for Library Herald automation.

An Ollama account / `ollama signin` is only for **cloud** models (names ending in `:cloud`) and the hosted API at `https://ollama.com`. Those are optional and unused here.

## What this app expects

From [`.env.example`](.env.example):

```
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
```

Copy that into `.env` if you have not already. The Python client posts to `{OLLAMA_HOST}/api/chat`. The local server on port **11434** does not require a login or API key.

## 1. Confirm the app is running

You already downloaded Ollama. On Windows it usually sits in the system tray and serves `http://localhost:11434`.

1. Open **Start** and launch **Ollama** if the tray icon is missing.
2. Open PowerShell and run:

```powershell
ollama --version
```

If that fails, close and reopen the terminal (PATH is set at install), or reinstall from [https://ollama.com/download/windows](https://ollama.com/download/windows).

3. Check the local API:

```powershell
curl http://localhost:11434/api/tags
```

A JSON list of models (even `"models": []`) means the server is up. You still do not need an account.

If the tray app is not running, start it from the Start menu. You should not need `ollama serve` when the Windows app is installed.

## 2. Skip the account / sign-in prompt

If the Ollama app asks you to sign in:

- Close or skip it.
- Stay on **local models**. Do not run `ollama signin` for this project.
- Do not create an API key at ollama.com unless you later choose cloud models on purpose.

Local `ollama pull` and `ollama run` work while signed out.

## 3. Download the model this repo uses

The default model is **`llama3.1:8b`** (about 4–5 GB). You need disk space and a reasonable amount of RAM (8 GB+; 16 GB is more comfortable).

In PowerShell:

```powershell
ollama pull llama3.1:8b
```

Wait until the download finishes. Then:

```powershell
ollama list
```

You should see `llama3.1:8b`. Smoke-test it:

```powershell
ollama run llama3.1:8b "Reply with the JSON object {\"ok\": true} only."
```

Type `/bye` to leave the chat.

### If 8B is too heavy

Smaller JSON-capable options (then set `OLLAMA_MODEL` in `.env` to match):

```powershell
ollama pull llama3.2:3b
```

or

```powershell
ollama pull qwen2.5:7b
```

Keep the `.env` name **exactly** the same as `ollama list`.

## 4. Point this project at Ollama

In the project folder:

```powershell
copy .env.example .env
```

Leave `OLLAMA_HOST=http://localhost:11434`. Set `OLLAMA_MODEL` if you pulled a different tag.

Then run **without** `--skip-llm`:

```powershell
python -m libh_automation --docx "LH Dec 2025 Doc.docx"
```

Dry-run is still the default, so this only writes `out/` files. It will call Ollama once per article (several minutes on CPU).

If Ollama is down, that article is marked `needs_review` with `LLM error: …` in `out/review_log.json` and the rest of the file continues.

## 5. Quick troubleshooting

| Symptom | What to do |
| --- | --- |
| `ollama` is not recognized | Reopen PowerShell; confirm Ollama is installed; start the app from the Start menu |
| Connection refused on 11434 | Start the Ollama Windows app; wait a few seconds; retry `curl http://localhost:11434/api/tags` |
| `model 'llama3.1:8b' not found` | Run `ollama pull llama3.1:8b` or change `OLLAMA_MODEL` |
| Very slow replies | Normal on CPU. Close other apps, or use a smaller model |
| App insists on sign-in | Ignore it. This pipeline only uses localhost, not ollama.com |
| You signed in anyway | Harmless. Local models still work. Sign-in is not required to stay connected |

## Optional: cloud (not used by this repo)

Only if you later want hosted models:

```powershell
ollama signin
ollama run gemma4:cloud
```

That path needs an ollama.com account. This automation’s `OLLAMA_HOST` would still be localhost unless you change the code to call `https://ollama.com` with an API key. Leave it on localhost unless you intentionally switch.
