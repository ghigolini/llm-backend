import boto3
import logging
import json
from flask import jsonify, request

class ChatService:        
    def __init__(self, sys_prompt = "L'utente non può riferirsi a messaggi precedenti a meno che non lo richieda esplicitamente, non possono esserci ambiguità. Tutte le tue risposte riguardano il testo dopo la scritta FINE RIASSUNTO"):
        self.system_message = ""
        self.model_id = ""
        self.messages = []
        self.responses = []
                
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)
        
        # Create a Bedrock client
        self.client = boto3.client('bedrock-runtime', region_name='eu-central-1')  # Change region if needed
        
        self.init_model(sys_prompt)

    # Function to call Converse API
    def call_converse_api(self, system_message, user_message, model_id, streaming=False, summarized=False):
        """
        Calls the AWS Bedrock Converse API.

        Parameters:
        - system_message: The initial system message
        - user_message: The user's input message
        - model_id: The name of the model to use
        - streaming: Boolean indicating if streaming mode is on/off

        Returns:
        - The response from the API
        """

        output = []

        # Inference parameters to use.
        temperature = 0.5
        maxTokens = 1000
        topP = 0.9
        top_k = 20

        # Base inference parameters to use.
        inference_config = {
            "temperature": temperature,
            "maxTokens": maxTokens,
            "topP": topP,
        }
        # Additional inference parameters to use.
        additional_model_fields = {
            "inferenceConfig": {
                "topK": top_k
            }
        }

        # Setup the system prompts and messages to send to the model.
        system_prompts = [{"text": system_message}]
        # prev = ""
        # if not summarized and self.messages != []:
        #     prev = self.summarize_prev_conv()
        prev = []
        for i in range(len(self.messages)):
            prev.append(["Domanda: " + str(self.messages[i]) + "\nRisposta: " + str(self.responses[i])])
        print(prev)
        message = {
            "role": "user",
            "content": [{"text": str(prev) + ". FINE RIASSUNTO " + user_message}]
        }
        self.messages.append(user_message)
        print(self.messages)
        if not streaming:
            # Call the Converse API
            response = self.client.converse(
                modelId=model_id,
                messages=[message],
                system=system_prompts,
                inferenceConfig=inference_config,
                additionalModelRequestFields=additional_model_fields
            )
            self.responses.append(response["output"]["message"]["content"][0]["text"])
            print(self.responses)
            self.logger.info(f"Response from Converse API:\n{json.dumps(response, indent=2)}")
            print('\n\n###########################################\n\n')
            self.logger.info(f'Response Content Text:\n{response["output"]["message"]["content"][0]["text"]}')

            # Log token usage.
            token_usage = response['usage']
            print('\n\n###########################################\n\n')
            self.logger.info("Input tokens: %s", token_usage['inputTokens'])
            self.logger.info("Output tokens: %s", token_usage['outputTokens'])
            self.logger.info("Total tokens: %s", token_usage['totalTokens'])
            self.logger.info("Stop reason: %s", response['stopReason'])
        return response["output"]["message"]["content"][0]["text"]
    
    def summarize_prev_conv(self):
        r = ""
        c = ChatService("Sei un riassumitore di conversazioni, inizi i riassunti con RIASSUNTO e li termini con FINE RIASSUNTO")
        r = c.call_converse_api(self.system_message, "Riassumi la seguente conversazione tenendo conto che il messaggio i-esimo corrisponde alla risposta i-esima: " + str(self.messages) + str(self.responses), self.model_id, summarized=True)
        print("r: " + str(r))
        return r

    def init_model(self, sys_prompt = "Sei un ottimo assistente"):
        self.system_message = sys_prompt
        self.model_id = "eu.amazon.nova-lite-v1:0"  # Replace with actual model name

    def get_answer(self):
        user_message = request.form.get('message')

        if user_message != '':
            print(user_message)
            
            r = self.call_converse_api(self.system_message, user_message, self.model_id, False)
            
            response = {'answer': r}
            return jsonify(response)
        return ''