import json
import random

def generate_question_answer_pairs(data):
    question_templates = [
        ("این رویداد در چه سالی آغاز شد؟", lambda item: item.get("period", {}).get("start_year")),
        ("این رویداد در چه سالی به پایان رسید؟", lambda item: item.get("period", {}).get("end_year")),
        ("علت‌های اصلی این رویداد چه بودند؟", lambda item: item.get("causes")),
        ("نتیجه این رویداد چه بود؟", lambda item: item.get("result")),
        ("این رویداد در کدام کشور اتفاق افتاد؟", lambda item: item.get("location", {}).get("country")),
        ("این رویداد در کدام منطقه رخ داد؟", lambda item: item.get("location", {}).get("primary_region")),
        ("رهبر اصلی این رویداد چه کسی بود؟", lambda item: item.get("leaders", [{}])[0].get("name")),
        ("وابستگی رهبر چه بود؟", lambda item: item.get("leaders", [{}])[0].get("affiliation")),
        ("چه تأثیرات سیاسی بر جای گذاشت؟", lambda item: item.get("impact", {}).get("political")),
        ("چه تأثیرات فرهنگی داشت؟", lambda item: item.get("impact", {}).get("cultural")),
        ("چه تأثیرات اجتماعی ثبت شده است؟", lambda item: item.get("impact", {}).get("social")),
        ("چه تأثیرات حقوقی بر کشور داشت؟", lambda item: item.get("impact", {}).get("legal")),
        ("یکی از رویدادهای کلیدی این انقلاب چه بود؟", lambda item: item.get("key_events", [{}])[0].get("event")),
        ("چه گروه‌هایی در این رویداد نقش داشتند؟", lambda item: [g["name"] for g in item.get("groups_involved", []) if g.get("name")]),
        ("هدف گروه‌های مخالف چه بود؟", lambda item: [g["motive"] for g in item.get("groups_involved", []) if g.get("motive")]),
        ("این رویداد مربوط به چه دوره تاریخی است؟", lambda item: item.get("period", {}).get("era")),
        ("در چه تاریخی قیام مهمی رخ داد؟", lambda item: item.get("key_events", [{}])[0].get("date")),
    ]

    results = []
    id_counter = 1

    for item in data:
        # Ensure we don't pick the same question twice
        selected_templates = random.sample(question_templates, 5)

        # Use your existing context builder
        title = item.get("title", "")
        context_parts = []

        # Description
        if "description" in item:
            context_parts.append(f"{item['description']}")

        # Period
        period = item.get("period", {})
        if "start_year" in period:
            context_parts.append(f"این رویداد در سال {period['start_year']} آغاز شد.")
        if "end_year" in period:
            context_parts.append(f"و در سال {period['end_year']} پایان یافت.")
        if "era" in period:
            context_parts.append(f"این رویداد مربوط به دوران {period['era']} است.")

        # Causes
        if "causes" in item:
            causes = "، ".join(item["causes"])
            context_parts.append(f"علل این رویداد عبارتند از: {causes}.")

        # Result
        if "result" in item:
            context_parts.append(f"نتیجه آن {item['result']}")

        # Impact
        impact = item.get("impact", {})
        for domain, impacts in impact.items():
            impact_list = "، ".join(impacts)
            context_parts.append(f"تأثیرات {domain} شامل: {impact_list}.")

        # Aftermath
        if "aftermath" in item:
            context_parts.append(f"پیامدهای بعد از رویداد: {item['aftermath']}")

        # Location
        location = item.get("location", {})
        if "country" in location:
            context_parts.append(f"کشور: {location['country']}")
        if "primary_region" in location:
            context_parts.append(f"منطقه اصلی: {location['primary_region']}")

        # Leaders
        for leader in item.get("leaders", []):
            context_parts.append(
                f"رهبر: {leader.get('name', '')} - نقش: {leader.get('role', '')} - وابستگی: {leader.get('affiliation', '')}"
            )

        # Key Events (timeline)
        for event in item.get("key_events", []):
            context_parts.append(
                f"در تاریخ {event['date']}، '{event['event']}' رخ داد: {event['description']}"
            )

        # Groups involved
        for group in item.get("groups_involved", []):
            context_parts.append(
                f"گروه: {group.get('name', '')} {group.get('type', '()')} با انگیزه: {group.get('motive', '')}"
            )

        # Join all parts into a single context string
        context = " ".join(context_parts)


        # Filter valid questions (skip any where data is null/empty)
        valid_templates = []
        for question_text, answer_func in question_templates:
            try:
                answer = answer_func(item)
                if isinstance(answer, list):
                    answer = [a for a in answer if a]
                    if not answer:
                        continue
                    answer = "، ".join(answer)
                elif not answer or str(answer).strip() == "":
                    continue
                valid_templates.append((question_text, lambda i, a=answer: a))
            except Exception:
                continue

        if len(valid_templates) < 5:
            continue  # Skip this item if not enough valid questions

        selected_templates = random.sample(valid_templates, 5)

        for question_text, answer_func in selected_templates:
            answer_text = str(answer_func(item)).strip()
            if not answer_text:
                continue
            answer_start = context.find(answer_text)
            if answer_start == -1:
                answer_start = 0

            results.append({
                "answers": {
                    "answer_start": [answer_start],
                    "text": [answer_text]
                },
                "context": context,
                "id": id_counter,
                "question": question_text,
                "title": title
            })
            id_counter += 1

    return results

# Load data from the input JSON file
with open("../raw_data/filtered_extracted_contents.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Generate the question format for each item
questions = generate_question_answer_pairs(data)

# Save the generated questions to an output JSON file
with open("../processed_data/filtered_extracted_contents_V2.json", "w", encoding="utf-8") as outfile:
    json.dump(questions, outfile, ensure_ascii=False, indent=2)

print("Output questions saved to output_questions.json")
