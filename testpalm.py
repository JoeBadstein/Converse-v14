"""
At the command line, only need to run once to install the package via pip:
$ pip install google-generativeai
"""
import os
import google.generativeai as palm

palm.configure(api_key=os.environ['genai'])

defaults = {
  'model': 'models/text-bison-001',
  'temperature': 0.25,
  'candidate_count': 1,
  'top_k': 40,
  'top_p': 0.95,
  'max_output_tokens': 1024,
  'stop_sequences': [],
}
prompt = f"""Who are you?"""

response = palm.generate_text(
  **defaults,
  prompt=prompt
)
print(response.result)