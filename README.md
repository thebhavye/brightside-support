# Brightside Bikes support

The support page of a (made-up) online bike shop: a chat box that answers customer questions
from the FAQ pages in `faq/`.

```bash
python -m venv .venv && .venv/Scripts/pip install -r requirements.txt   # bin/pip on macOS/Linux
cp .env.example .env        # then put your model key in it
.venv/Scripts/uvicorn app:app --port 8000
```

Open http://localhost:8000 and ask a question.
