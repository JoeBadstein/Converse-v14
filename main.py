from flask import Flask, render_template, send_file, request, session
import google.generativeai as palm
import os
import requests


app = Flask('app')
palm.configure(api_key=os.environ['genai'])

app.secret_key = "secret"

def google_search(query):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'q': query,
        'cx': os.environ['gsearchCx'],
        'key': os.environ['gsearch']
    }
    response = requests.get(url, params=params)
    return response.json()


generation_config = {
  "temperature": 0.7,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 2048,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_ONLY_HIGH"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_ONLY_HIGH"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_ONLY_HIGH"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_ONLY_HIGH"
  }
]

model = palm.GenerativeModel(model_name="gemini-pro", generation_config=generation_config, safety_settings=safety_settings)

@app.route('/')
def index():
  return render_template("index.html")


@app.route('/style.css')
def style():
  return send_file('templates/style.css')

@app.route('/clear_session', methods=['POST'])
def clear_session():
    session.clear()
    print("session cleared")
    return '', 204  # return no content

@app.route('/script.js')
def script():
  return send_file('templates/script.js')


@app.route('/start_listening', methods=['POST'])
def start_listening():
    print("called")
    text = request.form.get('transcribed-text')
    devilMode = request.form.get('devilMode')
    try:
      convotext = session.get('convotext', "")
    except:
      print("first rep")
      convotext = ""
    if str(text) == "":
        print(f"no text received {text}")
        session['convotext'] = convotext
        return
    else:
        print("\n\n\n\n",text,"\n\n\n\n")
    # if sr data not none, proceed to palm ai
    prompt = f"""Based on the following keywords from a conversation, come up with 1 bit of info that are relevant to someone in this conversation, that knowing could make them seem smarter. {"This could be something such as an argument, a cool fact, or some context or history to make it seem like the person is an expert in the field. Be as concise as possible--1 sentence max." if not devilMode else "You are acting as the devil's advocate for this conversation, so attempt to make an argument against whatever was said. You will either correct their facts, or make an argument as to why they're wrong. (or both)"}. Don't just answer a question, but provide a fact based on an interesting keyword. Return the word 'null' if you cannot understand, or if you don't have something good to say, or if the MOST RECENT TEXT is too short to provide good knowledge.
      You will base your fact off of this text (return null if not enough info):
      ------------------
      MOST RECENT TEXT: {text}            
      PREVIOUS CONVERSATION CONTEXT (no diarization, do your best to figure it out):{convotext}
      ------------------
      
      Below, write the piece of information that will be told to a user in the conversation. Make it not too long, and to the point as it will be played directly in their ear. Be AS CONCISE AS POSSIBLE--1 sentence max, should be a short short phrase. Always answer any math question. Answer here and be AS CONCISE AS POSSIBLE, to get your point across: \n"""
  
    #If, and ONLY IF it is a specific time/date sensitive fact, such as a statistic, write a question to be searched up in this format (QST--> your question goes here). 
  
    print(prompt)

  
    response = model.generate_content(prompt)
    
    response = response.text

    text += ". "
    convotext = convotext + text
    if len(convotext) > 1000:
        convotext = convotext[-300:]
    if not response or response.replace(" ","") == "null":
        print("null")
        session['convotext'] = convotext
        return ""
    elif "QST-->" in response:
        
        query = response[6:]
        print("searching google with query:", query)
        try:
            result = google_search(query)
            # print out the first three snippets        
            info = ""
            for item in result['items'][:3]:
                info += str(item['snippet']) + "\n"
                print(info)
        except Exception as e:
            print(f"An error occurred while performing the Google search: {e}")
            session['convotext'] = convotext
            return f"An error occurred while performing the Google search:"
        response = model.generate_content(f"INFO: {info}\n Answer the question based on the info (if the info does not have enough info, use your own knowledge to give a definite answer): {query}\nFINAL ANSWER (Maxmimum 1 sentance, and RESTATE THE QUESTION YOU ARE ANSWERING):")
        response = response.text
        print(response)
        
        session['convotext'] = convotext
        return "SEARCH." + response
    else:
        print(response)
        
        session['convotext'] = convotext
        return response


app.run(host='0.0.0.0')
