import json

# Function to generate questions and context
def generate_questions(data):
    questions = []
    id_counter = 1  # Initialize the ID counter
    
    for item in data:
        title = item.get("title", "")
        context = []
        
        # Creating a detailed context based on available fields
        # Add year-based context if year exists
        if item.get("period", {}).get("start_year"):
            context.append(f"این رویداد در سال {item['period']['start_year']} شروع شده است.")
        if item.get("period", {}).get("end_year"):
            context.append(f"و در سال {item['period']['end_year']} به اتمام رسید.")
        
        # Add result to context
        result = item.get("result", "")
        if result:
            context.append(f"نتیجه این رویداد: {result}")
        
        # Add location-based context
        location = item.get("location", {}).get("city", "")
        if location:
            context.append(f"این رویداد در شهر {location} اتفاق افتاده است.")
        
        # Adding a timeline-based context
        for event in item.get("timeline", []):
            event_date = event.get("date", "")
            event_description = event.get("description", "")
            if event_date and event_description:
                context.append(f"در تاریخ {event_date}، {event_description}")
        
        # Convert the context list to a single string
        context = " ".join(context)
        
        # Adding 5 questions for each event
        # Question 1: Date or year related question
        question = {
            "answers": {
                "answer_start": [context.find(str(item['period'].get("start_year", "")))],
                "text": [str(item['period'].get("start_year", ""))]
            },
            "context": context,
            "id": str(id_counter),
            "question": "چه سالی این رویداد شروع شده است؟",
            "title": title
        }
        questions.append(question)
        
        # Question 2: Result related question
        question = {
            "answers": {
                "answer_start": [context.find(result)],
                "text": [result]
            },
            "context": context,
            "id": str(id_counter + 1),
            "question": "نتیجه این رویداد چه بود؟",            
            "title": title
        }
        questions.append(question)
        
        # Question 3: Location-related question
        if location:
            question = {
                "answers": {
                    "answer_start": [context.find(location)],
                    "text": [location]
                },
                "context": context,
                "id": str(id_counter + 2),
                "question": f"این رویداد در کدام شهر رخ داده است؟",                
                "title": title
            }
            questions.append(question)
        
        # Question 4: Event Description (Timeline)
        if len(item.get("timeline", [])) > 0:
            event = item["timeline"][0]  # Taking the first event for simplicity
            event_description = event.get("description", "")
            question = {
                "answers": {
                    "answer_start": [context.find(event_description)],
                    "text": [event_description]
                },
                "context": context,
                "id": str(id_counter + 3),
                "question": f"چه اتفاقی در {event.get('date', '')} رخ داده است؟",
                "title": title
            }
            questions.append(question)
        
        # Question 5: Key figures related question
        if item.get("key_figures", []):
            key_figure = item["key_figures"][0]  # Taking the first key figure for simplicity
            figure_name = key_figure.get("name", "")
            question = {
                "answers": {
                    "answer_start": [context.find(figure_name)],
                    "text": [figure_name]
                },
                "context": context,
                "id": str(id_counter + 4),
                "question": f"چه کسی در این رویداد نقش کلیدی داشت؟",                
                "title": title
            }
            questions.append(question)

        # Increment the id_counter by 5 for the next item
        id_counter += 5

    return questions

# Load data from the input JSON file
with open("raw_data/filtered_extracted_contents.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Generate the question format for each item
questions = generate_questions(data)

# Save the generated questions to an output JSON file
with open("processed_data/filtered_extracted_contents.json", "w", encoding="utf-8") as outfile:
    json.dump(questions, outfile, ensure_ascii=False, indent=2)

print("Output questions saved to output_questions.json")
