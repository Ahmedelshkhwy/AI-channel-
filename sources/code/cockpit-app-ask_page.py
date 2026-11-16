@app.route("/ask")
@login_required
def ask_page() -> str:
    question = request.args.get("q", "").strip()
    lang = current_language()
    rows = visible_item_rows()
    answer = data_questions.ask(question, rows, lang, claude_client()) if question else None
    branch = sorted({row["branch"] for row in rows})[0] if rows else ""
    examples = [example.format(branch=branch) for example in (data_questions.EXAMPLES_AR if lang == "ar" else data_questions.EXAMPLES_EN)]
    return render_template("ask.html", question=question, answer=answer, examples=examples, ai_enabled=bool(ai_key_source()))
